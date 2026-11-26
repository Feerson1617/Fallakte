"""Durchlaufe dieselben Beratungsentscheidungen vor und nach der Statusnachricht des Elternrahmens."""
import argparse
from pathlib import Path
import gzip
import json
from playwright.sync_api import sync_playwright
from auslieferung import OUT,QA,SRC
from paarvergleich import RECORDER
from pruefen import enter

def run(reference=None):
    challenge=(SRC/'beratung_scan.js').read_text()
    location=QA/'Schnittstellenreferenz'/ 'Navigationsprobe.jsonl.gz' if reference else QA/'Navigationsprobe.jsonl.gz'
    location.parent.mkdir(parents=True,exist_ok=True)
    with gzip.open(location,'wt') as out,sync_playwright() as pw,pw.chromium.launch() as b:
        page=b.new_page(has_touch=True);page.goto((reference or OUT/'Fallakte-02-12.html').as_uri());f=enter(page,'02');f.evaluate(RECORDER)
        levels=['Foerder','ESA','MSA','AHR']
        for tier in levels:
            for n in range(1,6):
                for method in ('K','P','Cu','H','K+P','K+Cu','K+H'):
                    for wait in (False,True):
                        page.locator('[data-action=recovery]').evaluate('b=>b.click()')
                        f.locator('#wieder-level-'+tier).wait_for()
                        f.evaluate("tier=>document.getElementById('wieder-level-'+tier).click()",tier)
                        # Select and inspect before postMessage, or wait for its visible delivery.
                        f.evaluate("""async args=>{
                            document.querySelector('[data-stage="L0'+args.n+'"]').click();
                            if(args.wait) await new Promise(resolve=>setTimeout(resolve,80));
                            ("""+challenge+""")(args);
                        }""",dict(n=n,wait=wait,key=method,tier=tier))
                        for r in f.evaluate('window.pairs.splice(0)'):
                            out.write(json.dumps(dict(modul='UB02',text=r['gesamt'],niveau=tier,aktion=r['aktion']),ensure_ascii=False)+'\n')
            print(tier,flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--referenz',type=Path)
    run(parser.parse_args().referenz)
