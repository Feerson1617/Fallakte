import os,sys
from playwright.sync_api import sync_playwright,expect
from auslieferung import OUT,QA,ROOT,SRC,json_text
from leseprotokoll import Aufzeichnung
from pruefen import enter
def run(engine):
    rows=[]
    with Aufzeichnung('Dialogansichten-'+engine),sync_playwright() as pw, getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as b:
        p=b.new_page(viewport={'width':820,'height':1180},has_touch=True);p.goto((OUT/'Fallakte-02-12.html').as_uri())
        p.on('dialog',lambda d:d.accept())
        f=enter(p,'02')
        for t in ('Foerder','ESA','MSA','AHR'):
            for n in range(1,6):
                for k in ('K','P','Cu','H','K+P','K+Cu','K+H'):
                    p.locator('[data-action=recovery]').click()
                    f.locator('#wieder-level-'+t).click()
                    f.locator(f'#abschnitte [data-stage=L0{n}]').click()
                    rows.append(f.evaluate((SRC/'beratung_scan.js').read_text(),dict(key=k,tier=t)))
            print(t,'35 Empfehlungen geprüft',flush=True)
        p.close()
    assert len(rows)==140
    (QA/('Empfehlungen-'+engine+'.json')).write_text(json_text(rows))
if __name__=='__main__':
    for engine in ('chromium','webkit'):run(engine)
