"""Alte und neue Förder-/ESA-Anzeigen am entpackten Startdokument gegenüberstellen."""
import argparse,base64,json,os,sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from playwright.sync_api import sync_playwright,expect
from auslieferung import OUT,QA,ROOT,json_text
from sprachpruefung import BASE,rebuild,documents,bank
from pruefen import enter
def run(ref):
    rows=[]
    with TemporaryDirectory() as tmp,sync_playwright() as pw, pw.chromium.launch() as browser:
        for version,release in [('vorher',ref),('nachher',OUT/'Fallakte-08-12-SCORM12.zip')]:
            directory=Path(tmp)/version
            with ZipFile(release) as z:z.extractall(directory)
            path=directory/'index.html'
            material=bank(documents(path.read_bytes())['UB08'][0])
            for tiers in [('Förder',),('ESA',),('Förder','AHR'),('MSA','ESA')]:
                p=browser.new_page(viewport={'width':820,'height':1180},has_touch=True)
                p.goto(path.as_uri());f=enter(p,'08')
                for member,t in enumerate(tiers):f.locator('#level-'+str(member)).select_option(t)
                f.locator('#start').click()
                f.locator('#jump').click()
                expect(f.locator('h1')).to_have_attribute('data-section','LA-01')
                for person,step,key in [('Mutter',5,'MU-erst'),('Mutter',6,'MU-ergebnis'),('Freundin',5,'FR-erst'),('Freundin',6,'FR-ergebnis'),('Lauras Frage',1,'LA-eigen'),('Lauras Frage',3,'LA-abschluss')]:
                    p.locator('[data-action=recovery]').click()
                    f.locator('#person').select_option(person);f.locator('#entry').select_option(str(step));f.locator('#open-entry').click()
                    if key=='LA-abschluss':
                        expect(f.locator('[data-handoff]')).to_have_count(0)
                        f.locator('#paper-ready').click()
                    panel=f.locator('[data-handoff]')
                    expect(panel).to_have_attribute('data-handoff',key)
                    for i,lvl in enumerate(tiers):
                        prompt=panel.locator('[data-member]').nth(i).inner_text()
                        assert prompt==material['media']['steps'][key]['orders'][lvl]['screen']
                        rows.append(dict(version=version,team=tiers,person=i+1,niveau=lvl,zustand=key,anzeige=prompt,
                                         rueckweg=f.locator('[data-return],[data-terminal]').inner_text()))
                    if tiers==('Förder',) and key in ('LA-eigen','LA-abschluss','MU-erst','MU-ergebnis'):
                        p.screenshot(path=QA/(version+'-'+key+'.jpg'),quality=67)
                p.close()
    (QA/'Work-Gegenprobe.json').write_text(json_text(rows))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--referenz-zip',type=Path);a=p.parse_args()
    run(a.referenz_zip or rebuild(BASE,'gesamt/auslieferung.py','Gesamt')/'Fallakte-08-12-SCORM12.zip')
