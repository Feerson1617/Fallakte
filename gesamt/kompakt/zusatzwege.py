import gzip,json,os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import vertiefungen as t
from leseprotokoll import Aufzeichnung
from auslieferung import QA
from playwright.sync_api import sync_playwright

def run(team):
    engine,i,tier=team
    t.QA.mkdir(exist_ok=True,parents=True)
    target='Zusatz-'+engine+'-'+tier
    with Aufzeichnung(target),sync_playwright() as pw, getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as b:
        p=b.new_page(has_touch=True,viewport={'width':820 if i%2==0 else 1180,'height':1180 if i%2==0 else 820})
        issues=[]
        p.on('pageerror',lambda e:issues.append(str(e)))
        t.tom(p,tier,engine)
        choices=t.celina(p,tier,engine)
        assert not issues,issues
        p.close()
    print(engine,tier,flush=True)
    return {'browser':engine,'niveau':tier,'Tom':3,'Celina':choices},target

if __name__=='__main__':
    teams=[(engine,i,tier) for i,tier in enumerate(t.LEVELS) for engine in ('webkit','chromium')]
    with ProcessPoolExecutor(max_workers=4) as pool:results=list(pool.map(run,teams))
    with gzip.open(QA/'Zusatzdialoge.jsonl.gz','wt') as dst:
        for _,name in results:
            with gzip.open(QA/(name+'.jsonl.gz'),'rt') as f:
                for line in f:dst.write(line)
            (QA/(name+'.jsonl.gz')).rename(t.QA/(name+'.jsonl.gz'))
    (t.QA/'Vertiefungspruefung.json').write_text(json.dumps([row for row,_ in results]))
