"""Nachprüfung des unabhängigen Bestands am Offline-Dokument und am gepackten SCO."""
import gzip
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from playwright.sync_api import sync_playwright
from erstellen import HERE, OUT, sha

DIAGNOSEN = """rows=>{
 const d=JSON.parse(document.querySelector('#material').textContent);
 const tasks=new Map(Object.values(d.levels).flatMap(l=>l.fragen.filter(q=>q.modell).map(q=>[q.modell,[q,l]])));
 return rows.map(x=>{
   const [q,l]=tasks.get(x.model),m=d.modelle[x.model],diag=Lernfeedback.analyze(x.model,x.text);
   const r={text:x.text,last:diag,tries:1,attempts:[diag]};
   const fb=rueckmeldung(q,m,r),helps=[1,2,3,4,5].map(n=>fachhilfe(q,m,r,l.cards[l.fragen.indexOf(q)],n,l.cards));
   if(diag.state==='unsicher' && (!fb.includes('Vergleiche deine Erklärung') || /richtig sein|stimmt|passt/.test(fb)))throw Error(x.text+' / '+fb);
   if(diag.error){const correction=diag.quelle?Lernfeedback.gesundheit[diag.error].info:m.fehler[diag.error];
     if(!helps[4].includes(correction)||!vergleichstext(q,m,r,diag).includes(correction))throw Error(x.text);}
   return {...x,ist:diag.state,fehler:diag.error,rueckmeldung:fb,hilfen:helps};
 });
}"""
GEOMETRIE = """()=>{
 const p=document.querySelector('.paper'),rows=Array.from(p.querySelectorAll('li'));
 const within=r=>r.top>=0 && r.left>=0 && r.bottom<=innerHeight+1 && r.right<=innerWidth+1;
 const texts=[...p.querySelectorAll('li,h1,p')].map(e=>{const r=new Range();r.selectNodeContents(e);
   return [e.innerText,[...r.getClientRects()].every(within)];});
 const buttons=[...document.querySelectorAll('button')].map(e=>{const r=e.getBoundingClientRect();
   return [e.innerText,within(r)&&e.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2))&&r.height>=44&&r.width>=44];});
 return {texts,buttons,rows:rows.length};
}"""

def pruefen():
    rows=json.loads(gzip.decompress((HERE/'pruefdaten/Gegenpruefung-CLT.json.gz').read_bytes()))
    assert len(rows)==1058
    results=[]
    with TemporaryDirectory() as tmp,sync_playwright() as pw:
        path=Path(tmp)
        with ZipFile(OUT/'Vorbereitung-SCORM12.zip') as z:z.extractall(path)
        assert (path/'index.html').read_bytes()==(OUT/'Vorbereitung.html').read_bytes()
        for name in ('chromium','webkit'):
            with getattr(pw,name).launch(executable_path=os.getenv(name.upper()+'_EXECUTABLE')) as browser:
                page=browser.new_page(viewport={'width':740,'height':340},has_touch=True)
                for h in (OUT/'Vorbereitung.html',path/'index.html'):
                    page.goto(h.as_uri())
                    if name=='chromium' and h.parent==OUT:
                        diag=page.evaluate(DIAGNOSEN,rows)
                        assert all(r['expected'] in ('passend','vollständig richtig') for r in diag if r['ist']=='passend'),[r for r in diag if r['ist']=='passend' and r['expected'] not in ('passend','vollständig richtig')][:1]
                    for tier in ('Foerder','ESA','MSA','AHR'):
                        page.goto(h.as_uri())
                        page.evaluate("async()=>{document.documentElement.style.fontSize='150%';await document.fonts.ready}")
                        def pick(action,value=None):
                            selector=f'[data-action="{action}"]'+(f'[data-value="{value}"]' if value is not None else '')
                            page.locator(selector).tap(timeout=2500)
                        pick('level',tier);pick('lookup')
                        for i in range(4):
                            pick('fill',i)
                            record=page.evaluate(GEOMETRIE)
                            assert record['rows']==4 and all(v for _,v in record['texts']+record['buttons']),(tier,i,record)
                            results.append(dict(browser=name,datei=h.name,niveau=tier,kapitel=i+1,**record))
                            if tier=='AHR' and h.parent==OUT:
                                pic=OUT.parent.parent/'build/Kartenlernen/Sichtbilder'/f'Papier-{name}-{i+1}-740x340.jpg'
                                pic.parent.mkdir(parents=True,exist_ok=True);page.screenshot(path=str(pic))
                            pick('written')
    return dict(html_sha256=sha((OUT/'Vorbereitung.html').read_bytes()),papier=results,texte=diag)
if __name__=='__main__':
    print(len(pruefen()['papier']))
