"""Gleiche Familien- und persönlichen Entscheidungen im alten und neuen SCO."""
import argparse,gzip
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from playwright.sync_api import sync_playwright
from auslieferung import QA,OUT,SRC,json_text
from paarvergleich import start,pair
from sprachpruefung import BASE,rebuild
def run(ref):
    count=0
    with TemporaryDirectory() as tmp,sync_playwright() as pw,pw.chromium.launch() as b,gzip.open(QA/'Paarvergleich-UB08.ndjson.gz','wt') as out:
        paths=[]
        for i,z in enumerate([ref,OUT/'Fallakte-08-12-SCORM12.zip']):
            site=Path(tmp)/str(i)
            with ZipFile(z) as archive:archive.extractall(site)
            paths.append(site/'index.html')
        pages=[b.new_page(has_touch=True) for _ in paths]
        for route,team in enumerate([['Förder'],['ESA'],['MSA'],['AHR'],['Förder','AHR'],['ESA','MSA']]):
            frames=[start(p,path,'08') for p,path in zip(pages,paths)]
            for person in ['Mutter','Freundin','Großmutter','Vater','Lauras Frage']:
                for p,f in zip(pages,frames):
                    p.locator('[data-action=recovery]').click()
                    for i,t in enumerate(team):f.locator('#level-'+str(i)).select_option(t)
                    f.locator('#person').select_option(person);f.locator('#entry').select_option('0');f.locator('#open-entry').click()
                    f.evaluate((SRC/'familien_paar.js').read_text(),dict(kind='Laura' if person=='Lauras Frage' else 'Person',person=person,
                                                                            withHelp=True,number=route,joint=len(team)>1))
                count+=pair(out,'UB08',' / '.join(team),person,frames)
            print(team,count,flush=True)
    (QA/'Paarvergleich-UB08.json').write_text(json_text(dict(modul='UB08',zustaende=count)))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--referenz-zip',type=Path);a=p.parse_args()
    run(a.referenz_zip or rebuild(BASE,'gesamt/auslieferung.py','Gesamt')/'Fallakte-08-12-SCORM12.zip')
