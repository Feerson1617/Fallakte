"""Ergänzende echte Bildschirmzustände für Wiedereinstieg, Papierausfall und Methodenwechsel."""
from playwright.sync_api import sync_playwright,expect
from auslieferung import OUT,QA,SRC,json_text
from pruefen import enter,button
from karten import LEVELS,METHODS
from sprachpruefung import bank,documents

def run():
    path=OUT/'Fallakte-Gesamt.html'
    docs=documents(path.read_bytes())
    first=bank(docs['UB02'][0]);prep=bank(docs['PREP'][0])
    rows=[]
    wortlaut=(SRC/'bildschirmwortlaut.js').read_text()
    with sync_playwright() as pw,pw.chromium.launch() as browser:
        for tier,label in LEVELS.items():
            p=browser.new_page();p.goto(path.as_uri());f=enter(p,'vor')
            def record(m,id):
                rows.append(dict(modul=m,niveau=tier,zustand=id,bildschirm=f.evaluate(wortlaut)))
            button(f,'level',tier);record('PREP','Niveaustart')
            button(f,'references');record('PREP','Kartenwahl')
            for key in METHODS:
                button(f,'reference',key);record('PREP','Muster-'+key)
                f.locator('#close-sheet').click();button(f,'references')
            f.locator('#close-sheet').click()
            for c in prep['levels'][tier]['chapters']:
                if not c.get('paperCheck') and c['id'] not in ('2B','4B'):continue
                button(f,'picker');button(f,'open',c['id']);button(f,'begin')
                for q in c['questions']:
                    button(f,'choice',next(i for i,o in enumerate(q['options']) if o['correct']))
                    button(f,'check');button(f,'advance')
                if c.get('paperCheck'):
                    f.locator('summary').filter(has_text='Ausfallhilfe').click()
                    record('PREP',c['id']+'-Ersatz')
                else:
                    button(f,'review');button(f,'finish')
                    record('PREP',c['id']+'-Teileinstieg')
                p.locator('[data-action=home]').click()
            p.locator('#zurueck').click()
            f=enter(p,'02');f.locator('#level-'+tier).click();record('UB02','Einstieg')
            for stage,step in first['stages'].items():
                p.locator('[data-action=recovery]').click();f.locator('#wieder-level-'+tier).click()
                if stage=='L01':
                    for name in ('Tom','Celina','Laura'):
                        f.locator('#wiederfall').get_by_role('button',name=name,exact=True).click()
                        record('UB02','Neustart' if name=='Laura' else 'Neustart-'+name)
                f.locator(f'[data-stage="{stage}"]').click()
                if tier in ('MSA','AHR'):
                    f.locator('[data-strategy="K"]').click()
                    f.locator('#papier-ersatz summary').click();record('UB02',stage+'-Ausfall')
                    f.locator('#papier-ersatz summary').click();f.locator('#pruefcode').fill(step['code']);f.locator('#fachcheck-pruefen').click()
                    f.locator('#strategie-bearbeiten').click();f.locator('[data-strategy="P"]').click()
                    expect(f.locator('.fachcheck')).to_contain_text('Gib den Buchstaben erneut ein.')
                    record('UB02',stage+'-Wechsel')
            p.close()
    (QA/'Weitere-Papieransichten.json').write_text(json_text(rows))

if __name__=='__main__':run()
