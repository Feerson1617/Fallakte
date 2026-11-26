"""Geschlossene Familienantworten nach jeder Hilfetiefe, ohne/mit Fehlversuchen und später Hilfe."""
import json
import os
from tempfile import TemporaryDirectory
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from pruefen import OUT,QA,HOST,host,room,sha,LEVELS
from zipfile import ZipFile
import argparse

def run(engine,tier):
    result=[]
    with TemporaryDirectory() as directory,sync_playwright() as pw:
        site=Path(directory)
        with ZipFile(OUT/'Fallakte-08-12-SCORM12.zip') as z:z.extractall(site)
        (site/'host.html').write_text(HOST)
        with host(site) as url,getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as b:
            p=b.new_page(viewport={'width':1180,'height':820},has_touch=True)
            p.set_default_timeout(5000);p.on('dialog',lambda d:d.accept())
            for depth in range(6):
                for mask in range(8):
                    p.goto(url+'/host.html');p.frame_locator('[name=sco]').locator('#zweiter-tag').wait_for();s=p.frame(name='sco');f=room(s,'zweiter')
                    for i,name in enumerate(('Mutter','Freundin','Großmutter','Vater')):
                        s.locator('[data-action=recovery]').click()
                        f.locator('#level-0').select_option(tier)
                        if i==2:f.locator('#papierstand').click()
                        f.locator('#person').select_option(name);f.locator('#open-entry').click()
                        observed=f.evaluate((Path(__file__).parent/'statuswege.js').read_text(),dict(name=name,depth=depth,mask=mask))
                        result.extend(observed)
        folder=QA/f'08-{tier}-{engine}';folder.mkdir(parents=True,exist_ok=True)
        (folder/'Statuswege.json').write_text(json.dumps(dict(html_sha256=sha((site/'index.html').read_bytes()),pruefungen=result),ensure_ascii=False))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('browser',choices=['chromium','webkit']);a.add_argument('niveau',choices=LEVELS);o=a.parse_args();run(o.browser,o.niveau)
