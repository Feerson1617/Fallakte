"""Alle endlichen Folgen sendbarer Empfehlungen im extrahierten Originalmodul spielen."""
import argparse
import base64
import itertools
import json
import os
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright
from lernspur_test import schluss
from pruefen import LEVELS, OUT, QA, sha

PLAY="""({tier,path})=>{
  const get=s=>{const n=document.querySelector(s);if(!n||n.disabled)throw Error(s);return n;};
  function click(s){
    const n=get(s),more=n.closest('details:not([open])');if(more)more.querySelector('summary').click();
    n.click();
  }
  click('[data-nav=home]');click('#level-'+tier);click('#neu');
  if(document.querySelector('#spur-wahl')){
    const choice=document.querySelector('#spur-wahl');choice.selectedIndex=1;
    const f=document.querySelector('#spur-grund');f.value='Ich denke an Lauras Wunsch.';f.dispatchEvent(new Event('input'));
    click('#spur-speichern');
  }
  path.forEach((method,i)=>{
    const stage='L0'+(i+1),s=LAURA.stages[stage];
    if(i>0 && !document.querySelector('.bisher')?.textContent.includes(LAURA.strategies[path[i-1]].label))
      throw Error('Bisheriger Rat '+path);
    click('[data-strategy="'+method+'"]');
    const txt=document.querySelector('#erklaerung');
    if(txt){txt.value='Die Methode muss zu Lauras aktuellem Anliegen passen.';txt.dispatchEvent(new Event('input'));click('#vergleichen');}
    const answer=s.levels[tier].strategies[method].options.find(o=>o.correct);
    click('[data-option="'+answer.id+'"]');click('#nachricht-senden');
    const chat=[...document.querySelectorAll('[data-kind=send]')];
    if(chat.length!==i+1||chat.some((n,j)=>n.dataset.aboutStrategy!==path[j]))throw Error('Verlauf '+path);
    if(i<path.length-1)click('#beratung-weiter');
  });
  return !!get('#beratung-fertig');
}"""

def run(engine,level,limit=None):
    with TemporaryDirectory() as d,sync_playwright() as pw:
        raw=(OUT/'Fallakte-02-12.html').read_bytes()
        m=re.search(rb'<script id="modul-02" type="application/octet-stream">([^<]+)',raw)
        source=Path(d)/'modul.html';source.write_bytes(base64.b64decode(m[1]))
        with getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as b:
            p=b.new_page(viewport={'width':1180,'height':820},has_touch=True);p.on('dialog',lambda dlg:dlg.accept());p.goto(source.as_uri())
            tier=level.replace('Förder','Foerder')
            methods=p.evaluate("""t=>Object.values(LAURA.stages).map(s=>Object.keys(s.levels[t].strategies).filter(k=>s.levels[t].strategies[k].status==='C'))""",tier)
            paths=[]
            for path in itertools.islice(itertools.product(*methods),limit):
                assert p.evaluate(PLAY,dict(tier=tier,path=path))
                paths.append(' / '.join(path))
            print(engine,level,len(paths),flush=True)
            p.locator('#beratung-fertig').click();schluss(p)
            extra={}
            for name in ('Tom','Celina'):
                extra[name]=[]
                button=p.locator('[data-optional="'+name+'"]')
                button.click()
                iframe=p.locator('#rahmen-reserve-'+name)
                f=iframe.element_handle().content_frame()
                f.locator('#step').wait_for()
                choices=f.evaluate("JSON.parse(document.querySelector('#bank').textContent).stages.map(s=>s.allowed||[''])")
                for idx,route in enumerate(itertools.islice(itertools.product(*choices),limit)):
                    if idx:
                        button.click()
                        f.wait_for_function("!!document.querySelector('[id^=method-]')")
                    f.evaluate((Path(__file__).parent/'zusatzfolge.js').read_text(),route)
                    button.wait_for(state='visible');extra[name].append(route)
            if limit:return
            folder=QA/f'02-{level}-{engine}';folder.mkdir(parents=True,exist_ok=True)
            (folder/'Ratfolgen.json').write_text(json.dumps(dict(html_sha256=sha(raw),folgen=paths,zusatz=extra),ensure_ascii=False))

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('browser',choices=['chromium','webkit']);a.add_argument('niveau',choices=LEVELS);a.add_argument('--limit',type=int);o=a.parse_args();run(o.browser,o.niveau,o.limit)
