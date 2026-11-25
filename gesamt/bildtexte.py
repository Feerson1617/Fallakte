"""Liest die acht Stationsgrafiken mit ihren zugänglichen Beschreibungen im echten SCO."""
import csv,gzip,os
from tempfile import TemporaryDirectory
from pathlib import Path
from zipfile import ZipFile
from playwright.sync_api import sync_playwright
from auslieferung import OUT,QA,SRC,json_text
from pruefen import enter,button


def run():
    with gzip.open(SRC/'pruefgrundlagen/Ausgangsinventar.csv.gz','rt',encoding='utf-8-sig') as f:
        ref={r['stelle']:r['text'] for r in csv.DictReader(f) if r['typ']=='SVG'}
    values={}
    with TemporaryDirectory() as temp,sync_playwright() as pw:
        with ZipFile(OUT/'Fallakte-Vorbereitung-SCORM12.zip') as z:z.extractall(temp)
        for engine in ('chromium','webkit'):
            found={}
            with getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as browser:
                p=browser.new_page(viewport={'width':820,'height':1180},has_touch=True)
                p.goto((Path(temp)/'index.html').as_uri());f=enter(p,'vor');button(f,'level','Foerder');button(f,'picker')
                for code in ('1A','1B','2A','2B','3A','3B','4A','4B'):
                    button(f,'open',code)
                    svg=f.locator('figure svg')
                    readings=svg.evaluate("""e=>Array.from(e.querySelectorAll('title,text')).map((n,i)=>[n.localName+'/'+i,n.textContent,n.localName==='title'||(n.getBBox().width>0 && n.getBBox().height>0)])""")
                    prefix='graphics/'+code+'/'
                    for key,text,visible in readings:
                        assert visible,(code,key);found[prefix+key]=text
                    found[prefix+'aria-label']=svg.get_attribute('aria-label')
                    p.locator('[data-action=home]').click();button(f,'picker')
                assert found==ref,(engine,found.keys()^ref.keys())
            values[engine]=found
    (QA/'Bildtexte.json').write_text(json_text(values))
if __name__=='__main__':run()
