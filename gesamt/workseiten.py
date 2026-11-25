"""Papierübergänge, Direkteinstieg und abgeschlossene Prüfung im gebauten SCO."""
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from playwright.sync_api import expect,sync_playwright
from auslieferung import OUT,QA,SRC,json_text
from sprachpruefung import bank,documents
from pruefen import enter

def run():
    rows=[]
    wortlaut=(SRC/'bildschirmwortlaut.js').read_text()
    with TemporaryDirectory() as tmp, sync_playwright() as pw:
        with ZipFile(OUT/'Fallakte-08-12-SCORM12.zip') as z:z.extractall(tmp)
        path=Path(tmp)/'index.html'
        family=bank(documents(path.read_bytes())['UB08'][0])
        for engine in ('chromium','webkit'):
            with getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as browser:
                for tier in family['levels']:
                    page=browser.new_page(viewport={'width':820,'height':1180},has_touch=True)
                    page.goto(path.as_uri())
                    def snap(f,key,button,goal):
                        rows.append(dict(browser=engine,niveau=tier,zustand=key,bildschirm=f.evaluate(wortlaut),
                                         rueckkehr=button,ziel=goal))
                        if tier=='Förder' and engine=='chromium':
                            page.screenshot(path=QA/('Work-'+key+'.jpg'),quality=63)
                    def entry(person,step):
                        page.locator('[data-action=recovery]').click()
                        f.locator('#person').select_option(person);f.locator('#entry').select_option(str(step));f.locator('#open-entry').click()
                    def check_order(key):
                        step=family['media']['steps'][key];panel=f.locator('[data-handoff]')
                        expect(panel).to_have_attribute('data-handoff',key)
                        expect(panel.locator('[data-level]')).to_have_count(1)
                        assert panel.locator('.paper-order').inner_text()==step['orders'][tier]['screen']
                        if key.endswith('erst') and tier in ('Förder','ESA'):
                            opts=family['media']['fields'][step['field']]['foerder' if tier=='Förder' else 'options']
                            assert opts==f.locator('button[id^="answer-"]:visible').all_inner_texts()
                        back=step['buttonText'] or (family['ui']['compare'] if tier in ('MSA','AHR') else 'Aussage zur Frage wählen')
                        snap(f,key,back if step['nextId'] else 'Unterrichtsgespräch · kein Knopf',step['nextId'] or 'Besprechung auf Papier')
                    f=enter(page,'08');expect(f.locator('select')).to_have_count(1);expect(f.locator('#start')).to_have_count(0)
                    f.locator('#level-0').select_option(tier);f.locator('#start').click();f.locator('#next').click()
                    page.locator('[data-action=home]').click()
                    f.locator('#level-0').select_option(next(t for t in family['levels'] if t!=tier))
                    f.locator('#dismiss').click();assert f.locator('#level-0').input_value()==tier
                    f.locator('#resume').click();expect(f.locator('h1')).to_have_attribute('data-section','MU-02')
                    # Reload discards memory. A paper result cannot certify the digital check.
                    page.reload();f=enter(page,'08');page.locator('[data-action=recovery]').click()
                    f.locator('#level-0').select_option(tier);f.locator('#person').select_option('Lauras Frage')
                    f.locator('#entry').select_option('3');f.locator('#open-entry').click()
                    expect(f.locator('[data-handoff],#paper-ready,#member')).to_have_count(0)
                    snap(f,'LA-offen',f.locator('#open-review').inner_text(),'LA-03')
                    f.locator('#open-review').click();expect(f.locator('h1')).to_have_attribute('data-section','LA-03')
                    for name,case in family['cases'].items():
                        n=len(case['tasks']);prefix=case['recovery'][0]['id'].split('-')[0]
                        entry(name,n);check_order(prefix+'-erst')
                        entry(name,n+1);check_order(prefix+('-ergebnis' if prefix in ('MU','FR') else '-einstieg'))
                    entry('Lauras Frage',1);check_order('LA-eigen')
                    entry('Lauras Frage',0);f.evaluate((SRC/'familien_paar.js').read_text(),dict(kind='Laura',withHelp=False,number=2))
                    expect(f.locator('#open-review')).to_have_count(0);check_order('LA-abschluss')
                    for name in ('Großmutter','Vater'):
                        c=family['cases'][name];entry(name,len(c['tasks'])+1);check_order(c['recovery'][0]['id'].split('-')[0]+'-ergebnis')
                    page.locator('#zurueck').click();day=enter(page,'02')
                    level='Foerder' if tier=='Förder' else tier
                    day.locator('#level-'+level).click();day.locator('#neu').click();day.locator('#lehrkraft summary').click()
                    day.locator('#sicherung-oeffnen').click();dlg=day.locator('#material-dialog')
                    expect(dlg).to_contain_text('Mein Schlussrat');expect(dlg.locator('input')).to_have_count(0)
                    rows.append(dict(browser=engine,niveau=tier,zustand='UB02-Stopp',bildschirm=day.evaluate(wortlaut),rueckkehr='Besprechung auf Papier',ziel='Gemeinsame Sicherung'))
                    if engine=='webkit' and tier=='ESA':page.screenshot(path=QA/'Work-Schlussrat-Stopp.jpg',quality=63)
                    page.close()
    assert len(rows)==8*14,len(rows)
    (QA/'Work-Gegenprobe.json').write_text(json_text(rows))

if __name__=='__main__':run()
