"""Run the existing pupil-side routes directly against the new integrated builds."""
import base64
import json
import os
import sys
from zipfile import ZipFile
from lxml import html
from playwright.sync_api import sync_playwright
from auslieferung import ROOT,OUT,QA,json_text,revision
from karten import LEVELS
sys.path.insert(0,str(ROOT/'tests'))
import release_abnahme
import familienrat_lernwege

def run():
    doc=html.parse(str(OUT/'Fallakte-02-12.html'))
    first=html.fromstring(base64.b64decode(doc.getroot().get_element_by_id('modul-02').text))
    ub=json.loads(first.get_element_by_id('materialvertrag').text)['cards']
    with ZipFile(ROOT/'vorbereitung/Stationsplanung.zip') as plan:
        contract=json.loads(plan.read('Kartenvertrag.json'))
    sources=[]
    for tier,methods in contract['levels'].items():
        for m in methods:
            for section in m['sections']:
                original=ub[m['method']]['sections'][section['id']]
                source='shortText' if tier in ('Foerder','ESA') else 'text'
                assert (original['title'],original[source])==(section['title'],section['sourceText'])
                sources.append(dict(niveau=tier,methode=m['title'],titel=section['title'],ub=original[source],vorbereitung=section['completedText']))
    assert len(sources)==80
    records=[]
    release_abnahme.QA=QA
    familienrat_lernwege.APP=OUT/'Fallakte-08-12.html'
    with sync_playwright() as pw:
        for ie,engine in enumerate(('chromium','webkit')):
            with getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as browser:
                for i,(tier,display) in enumerate(LEVELS.items()):
                    page=browser.new_page(has_touch=True)
                    size=[(820,1180),(1180,820),(390,844),(390,844)][i]
                    release_abnahme.route(page,engine,tier,OUT/'Fallakte-02-12.html',size)
                    page.close()
                    family=familienrat_lernwege.walk(browser,display,(i+ie)%2==1)
                    records.append(dict(browser=engine,niveau=tier,laura='L01 bis L05',familienrat=family))
            print(engine,'beide Unterrichtsbesuche auf vier Niveaus bestanden',flush=True)
    (QA/'Unterrichtspruefung.json').write_text(json_text(dict(commit=revision(),wege=records,karten=sources)))
if __name__=='__main__':run()
