"""Ergänzende echte Bildschirmzustände für Wiedereinstieg, Papierausfall und Methodenwechsel."""
from playwright.sync_api import sync_playwright,expect
from auslieferung import OUT,QA,SRC,json_text
from pruefen import enter,button
from karten import LEVELS,METHODS
from sprachpruefung import bank,documents

def run():
    path=OUT/'Fallakte-Gesamt.html'
    first=bank(documents(path.read_bytes())['UB02'][0])
    rows=[]
    wortlaut=(SRC/'bildschirmwortlaut.js').read_text()
    with sync_playwright() as pw,pw.chromium.launch() as browser:
        for tier,label in LEVELS.items():
            p=browser.new_page();p.goto(path.as_uri());f=enter(p,'vor')
            def record(m,id,where):
                rows.append(dict(modul=m,niveau=tier,zustand=id,bildschirm=f.evaluate(wortlaut)))
            button(f,'level',tier);button(f,'references');record('PREP','Kartenwahl',f.locator('dialog'))
            for key in METHODS:
                button(f,'reference',key);record('PREP','Muster-'+key,f.locator('dialog'))
                f.locator('#close-sheet').click();button(f,'references')
            f.locator('#close-sheet').click();p.locator('#zurueck').click()
            f=enter(p,'02');f.locator('#level-'+tier).click();record('UB02','Einstieg',f.locator('#start'))
            for stage,step in first['stages'].items():
                p.locator('[data-action=recovery]').click();f.locator('#wieder-level-'+tier).click()
                record('UB02','Neustart',f.locator('#einstieg'))
                f.locator(f'[data-stage="{stage}"]').click()
                if tier in ('MSA','AHR'):
                    f.locator('[data-strategy="K"]').click()
                    f.locator('#papier-ersatz summary').click();record('UB02',stage+'-Ausfall',f.locator('#beratung'))
                    f.locator('#papier-ersatz summary').click();f.locator('#pruefcode').fill(step['code']);f.locator('#fachcheck-pruefen').click()
                    f.locator('#strategie-bearbeiten').click();f.locator('[data-strategy="P"]').click()
                    expect(f.locator('.fachcheck')).to_contain_text('Gib den Buchstaben erneut ein.')
                    record('UB02',stage+'-Wechsel',f.locator('#beratung'))
            p.close()
    (QA/'Weitere-Papieransichten.json').write_text(json_text(rows))

if __name__=='__main__':run()
