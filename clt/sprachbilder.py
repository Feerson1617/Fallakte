"""Gezielte Wortlautprüfung im Schülerfenster, mit Screenshots aus beiden Startformaten."""
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from playwright.sync_api import sync_playwright
from pruefen import OUT, QA, HOST, host, room, sha, LEVELS
from lernspur_test import touch

def pruefen(engine):
    directory=QA/'Sprachbilder'/engine
    directory.mkdir(parents=True,exist_ok=True)
    rows=[]
    with TemporaryDirectory() as tmp,sync_playwright() as pw,getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as browser:
        for day in ('02','08'):
            html=OUT/f'Fallakte-{day}-12.html'
            with ZipFile(html.with_name(html.stem+'-SCORM12.zip')) as z:z.extractall(tmp)
            assert (Path(tmp)/'index.html').read_bytes()==html.read_bytes()
            (Path(tmp)/'host.html').write_text(HOST)
            with host(Path(tmp)) as url:
                for i,tier in enumerate(LEVELS):
                    embedded=i%2==1
                    width,height=((740,410) if i==1 else (1024,768))
                    page=browser.new_page(viewport={'width':width,'height':height},has_touch=True)
                    page.set_default_timeout(7000)
                    page.goto(url+'/host.html' if embedded else html.as_uri())
                    shell=page.frame(name='sco') if embedded else page.main_frame
                    def capture(name,frame):
                        text=frame.locator('body').inner_text()
                        if frame==shell:text=frame.locator('#auswahl').inner_text()
                        assert text.strip() and 'undefined' not in text
                        buttons=frame.locator('button:visible,summary:visible,select:visible,textarea:visible').evaluate_all("nodes=>nodes.map(n=>({id:n.id,wort:n.getAttribute('aria-label')||n.innerText||n.labels?.[0]?.innerText||'',gesperrt:!!n.disabled}))")
                        cues=frame.locator('.aufgabenkasten:visible p').all_inner_texts()
                        row=dict(buttons=buttons,cue=' '.join(cues),tag=day,niveau=tier,ansicht=name,format='SCORM' if embedded else 'HTML',
                                 sha256=sha(html.read_bytes()),browser=engine,breite=width,hoehe=height,text=text)
                        if tier in ('ESA','AHR'):
                            filename=f'{day}-{tier}-{name}.jpg'
                            page.screenshot(path=directory/filename,quality=70)
                            row['bild']=filename
                        rows.append(row)
                    shell.locator('#tageshilfe').click();capture('Tageshilfe',shell)
                    shell.locator('#auswahl-zurueck').click()
                    frame=room(shell,'erster' if day=='02' else 'zweiter')
                    capture('Falluebersicht',frame)
                    shell.locator('[data-action=recovery]').click()
                    if day=='02':
                        t=tier.replace('Förder','Foerder')
                        frame.locator('#wieder-level-'+t).click();capture('Wiedereinstieg',frame)
                        frame.locator('[data-stage=L02]').click()
                        touch(frame,'#strategie-P')
                        if i>=2:
                            assert 'Pille' in frame.locator('.aufgabenkasten:visible p').inner_text()
                            field=frame.locator('#erklaerung')
                            field.fill('Die Pille schützt vor HIV.');touch(frame,'#vergleichen')
                            assert 'nicht vor HIV' in frame.locator('#fachmeldung').inner_text()
                            capture('HIV-Korrektur',frame)
                            touch(frame,'#entwurf-bearbeiten');field.fill('Ich habe noch einen anderen Vorschlag.')
                            touch(frame,'#vergleichen');assert frame.locator('[data-diagnose=unsicher]').is_visible()
                            fact=frame.locator('[data-diagnose]').inner_text()
                            assert 'Pille' in fact and ('Ansteckung' in fact or 'HIV' in fact),fact
                            assert frame.locator('[data-option]').count() and frame.locator('.eigener-text p').text_content().endswith('anderen Vorschlag.')
                        capture('Pille-Infektionsschutz',frame)
                        touch(frame,'#hilfe');capture('Hilfe-zur-Pille',frame)
                    else:
                        frame.locator('#level-0').select_option(tier)
                        frame.locator('#person').select_option('Mutter');frame.locator('#entry').select_option('1')
                        capture('Wiedereinstieg',frame);touch(frame,'#open-entry')
                        cue=frame.locator('.aufgabenkasten p').inner_text()
                        assert 'Mama' in cue and frame.locator('.blatt-inhalt h2:visible').count()==0
                        capture('Mamas-Wert',frame)
                        if i>=2:
                            frame.locator('textarea').fill('Das sehe ich anders.')
                            touch(frame,'#compare')
                            assert frame.locator('[data-diagnose=unsicher]').is_visible()
                            assert 'Gesundheit' in frame.locator('[data-diagnose]').inner_text()
                            assert frame.locator('[id^=answer-]').count()
                            capture('Quellensatz',frame)
                        touch(frame,'#help');capture('Hilfe-Mutter',frame)
                    page.close()
    (directory/'Wortlaut.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    print(engine,len(rows),'beobachtete Schüleransichten')
if __name__=='__main__':pruefen(sys.argv[1])

