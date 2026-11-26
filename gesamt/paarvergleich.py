"""Paarweiser Export von Zuständen nach identischen UI-Eingaben auf Referenz- und Kandidaten-SCO."""
import argparse,gzip,json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from playwright.sync_api import sync_playwright
from auslieferung import QA,OUT,SRC,ROOT,json_text
from pruefen import enter,STEPS
from endvergleich import REFERENZ as BASE,rebuild

# Die Beobachtung läuft nur im Test. Klick und Eingabe gehen über die öffentliche UI.
RECORDER="""() => {
  window.pairs=[];
  const screenText = (SCREEN_READER);
  const save=e=>{
    const root=document.querySelector('dialog[open]')||document.querySelector('#view,#beratung:not([hidden]),#app,#desk')||document.body;
    const c=e.target.closest('button,summary,select,input,textarea');
    if(!c)return;
    window.pairs.push({aktion:c.id||c.dataset.do||c.tagName,wert:c.dataset.value||c.dataset.option||'',
      ansicht:root.innerText,gesamt:screenText(),knopf:[...root.querySelectorAll('button')].filter(x=>x.getClientRects().length&&!x.disabled).map(x=>x.textContent)});
  };
  for(const type of ['click','change'])window.addEventListener(type,save);
}""".replace("SCREEN_READER",(SRC/"bildschirmwortlaut.js").read_text())
def start(p,path,kind):
    p.goto(path.as_uri());f=enter(p,kind);f.evaluate(RECORDER);return f
def pair(out,module,tier,route,frames):
    snapshots=[f.evaluate('window.pairs.splice(0)') for f in frames]
    assert len(snapshots[0])==len(snapshots[1]),(module,tier,route,list(map(len,snapshots)))
    for i,(a,b) in enumerate(zip(*snapshots)):
        assert (a['aktion'],a['wert'])==(b['aktion'],b['wert']),(module,route,i,a['aktion'],b['aktion'])
        row=dict(modul=module,niveau=tier,weg=route,schritt=i,aktion=b['aktion'],auswahl=b['wert'],
                 alttext=a['ansicht'],alter_bildschirm=a['gesamt'],neutext=b['ansicht'],ganzer_bildschirm=b['gesamt'],bedienung=b['knopf'],grund='Zustand nach derselben Bedienhandlung auf beiden SCOs')
        out.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n')
    return len(snapshots[0])
def run(ref,kind):
    count=0
    with TemporaryDirectory() as tmp,sync_playwright() as pw,pw.chromium.launch() as browser,gzip.open(QA/('Paarvergleich-'+kind+'.ndjson.gz'),'wt') as out:
        paths=[]
        for i,archive in enumerate([ref,OUT/'Fallakte-08-12-SCORM12.zip']):
            dest=Path(tmp)/str(i)
            with ZipFile(archive) as z:z.extractall(dest)
            paths.append(dest/'index.html')
        pages=[browser.new_page(viewport={'width':820,'height':1180}) for _ in paths]
        for tier in ('Foerder','ESA','MSA','AHR'):
            if kind=='PREP':
                for assisted in (False,True):
                    fs=[]
                    for p,path in zip(pages,paths):
                        f=start(p,path,'vor');fs.append(f)
                        value=f.evaluate("""t=>{const b=JSON.parse(document.querySelector('#material').textContent);return {lesson:b.levels[t],ui:b.ui,cards:b.cards[t]}}""",tier)
                        f.evaluate(STEPS,dict(**value,level=tier,assisted=assisted,embedded=True))
                    count+=pair(out,kind,tier,'mit Hilfen' if assisted else 'selbstständig',fs)
            else:
                fs=[start(p,path,'02') for p,path in zip(pages,paths)]
                for n in range(1,6):
                    for key in ('K','P','Cu','H','K+P','K+Cu','K+H'):
                        for p,f in zip(pages,fs):
                            p.locator('[data-action=recovery]').evaluate('b=>b.click()')
                            f.locator('#wieder-level-'+tier).click()
                            f.locator(f'#abschnitte [data-stage=L0{n}]').click()
                            f.evaluate((SRC/'beratung_scan.js').read_text(),dict(key=key,tier=tier))
                        count+=pair(out,kind,tier,f'L0{n} · {key}',fs)
            print(kind,tier,count,flush=True)
    (QA/('Paarvergleich-'+kind+'.json')).write_text(json_text(dict(modul=kind,zustaende=count)))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('modul',choices=['PREP','UB02']);p.add_argument('--referenz-zip',type=Path);a=p.parse_args()
    run(a.referenz_zip or rebuild(BASE,'gesamt/auslieferung.py','Gesamt')/'Fallakte-08-12-SCORM12.zip',a.modul)
