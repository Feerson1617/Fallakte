"""Vorher und nachher dieselben Rückfragen, Lesewege, Methoden und Codes bei Tom/Celina."""
import argparse,gzip
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from playwright.sync_api import sync_playwright,expect
from auslieferung import QA,OUT,json_text
from pruefen import enter
from paarvergleich import RECORDER,pair
from endvergleich import REFERENZ as BASE,rebuild

FLOW="""async ({index,key,tier})=>{
 const $=id=>document.getElementById(id),c=JSON.parse($('bank').textContent).stages[index];
 const click=b=>{
   if(typeof b==='string')b=$(b);
   const d=b?.closest('details:not([open])');if(d && d.querySelector('summary')!==b)d.querySelector('summary').click();
   if(!b||b.disabled||!b.getClientRects().length)throw Error('Zusatzfall: Bedienelement fehlt '+key);
   b.click();
 };
 const close=async()=>{click('back');await new Promise(r=>setTimeout(r,20));};
 if(key)click('method-'+key);
 const check=c.checks?.[key]||c;
 click('help');await close();
 for(const [i] of (check.questions||c.questions).entries()){click('ask');click('q'+i);}
 click('source');for(const d of document.querySelectorAll('#reading details'))if(!d.open)click(d.querySelector('summary'));
 await close();
 if(key && !c.allowed.includes(key))return;
 const labels=['MSA','AHR'].includes(tier)?['Z',...'ABC']:Array.from(document.querySelectorAll('[id^=answer-]')).map(b=>b.id.slice(-1));
 for(const v of [...labels.filter(x=>x!==check.code),check.code]){
   if($('code')){$('code').value=v;$('code').dispatchEvent(new Event('input',{bubbles:true}));click('check');}
   else click('answer-'+v);
 }
 click('send');
}"""
def run(ref):
    count=0
    with TemporaryDirectory() as tmp,sync_playwright() as pw,pw.chromium.launch() as browser,gzip.open(QA/'Paarvergleich-Zusatz.ndjson.gz','wt') as out:
        pages=[];parents=[]
        for i,path in enumerate([ref,OUT/'Fallakte-08-12-SCORM12.zip']):
            folder=Path(tmp)/str(i)
            with ZipFile(path) as z:z.extractall(folder)
            p=browser.new_page(viewport={'width':820,'height':1180});p.goto((folder/'index.html').as_uri())
            parents.append(enter(p,'02'));pages.append(p)
        for tier in ('Foerder','ESA','MSA','AHR'):
            for person in ('Tom','Celina'):
                for index in range(3 if person=='Tom' else 5):
                    for key in ([''] if person=='Tom' and index else ['K','P','Cu','H','K+P','K+Cu','K+H']):
                        frames=[]
                        for p,parent in zip(pages,parents):
                            p.locator('[data-action=recovery]').evaluate('b=>b.click()')
                            parent.locator('#wieder-level-'+tier).click()
                            parent.locator('#wiederfall').get_by_role('button',name=person,exact=True).click()
                            parent.locator('#abschnitte button').nth(index).click()
                            iframe=parent.locator('#rahmen-reserve-'+person)
                            f=iframe.element_handle().content_frame()
                            expect(f.locator('#step')).to_contain_text(person+' '+str(index+1)+' von')
                            # Eine neue Aufnahme je Weg; der iframe kann aus einer früheren Aufgabe stammen.
                            if not f.evaluate('Boolean(window.pairs)'):f.evaluate(RECORDER)
                            f.evaluate('window.pairs.length=0')
                            if key:f.locator('[id="method-'+key+'"]').wait_for(state='attached')
                            f.evaluate(FLOW,dict(index=index,key=key,tier=tier));frames.append(f)
                        count+=pair(out,person,tier,f'{person} {index+1} · {key}',frames)
            print(tier,count,flush=True)
    (QA/'Paarvergleich-Zusatz.json').write_text(json_text(dict(modul='Tom und Celina',zustaende=count)))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--referenz-zip',type=Path);a=p.parse_args()
    run(a.referenz_zip or rebuild(BASE,'gesamt/auslieferung.py','Gesamt')/'Fallakte-08-12-SCORM12.zip')
