"""Prüfschranke für die Blickführung, einschließlich einer tatsächlich getippten Erstbegründung."""
import json
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from pruefen import OUT, QA, room, LEVELS, sha
from lernspur_test import touch

def pruefen(engine):
    rows=[]
    with sync_playwright() as pw, getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as browser:
        for day in ('02','08'):
            path=OUT/f'Fallakte-{day}-12.html'
            for tier in LEVELS:
                p=browser.new_page(viewport={'width':1180,'height':820},has_touch=True)
                p.goto(path.as_uri()); f=room(p.main_frame,'erster' if day=='02' else 'zweiter')
                if day=='02':
                    touch(f,'#level-'+tier.replace('Förder','Foerder'));touch(f,'#neu')
                else:
                    f.locator('#level-0').select_option(tier);touch(f,'#start')
                root=f.locator('#lernspur')
                cue=root.locator('.aufgabenkasten')
                chat=root.locator('.gespraech')
                assert cue.inner_text().startswith('Aufgabe') and cue.bounding_box()['x']<chat.bounding_box()['x']
                assert not root.locator('textarea,select').count()
                expect(p.locator('[data-action=abschluss]')).to_be_disabled()
                if day=='08':
                    assert root.locator('.weitergeleitet').count()==2
                    assert 'Blutungen' not in chat.inner_text()
                touch(f,'#spur-lesen');assert not root.locator('textarea').count()
                root.locator('select').select_option(index=1)
                root.locator('textarea').fill('Mein erster Gedanke.')
                touch(f,'#spur-speichern')
                if day=='02':
                    expect(root).to_contain_text('Warte auf das Zeichen deiner Lehrkraft.')
                    touch(f,'#spur-chat')
                expect(p.locator('[data-action=abschluss]')).to_be_enabled()
                p.locator('[data-action=abschluss]').tap()
                if day=='08':expect(root.locator('.faktenpaar p')).to_have_count(2)
                root.locator('select').select_option(index=2)
                assert root.locator('textarea').input_value()==''
                root.locator('textarea').fill('Mein neuer Grund.');touch(f,'#spur-speichern')
                assert root.locator('.spur-zitat').all_text_contents()==['Mein erster Gedanke.','Mein neuer Grund.']
                rows.append(dict(tag=day,niveau=tier,browser=engine,html_sha256=sha(path.read_bytes())))
                p.close()
    folder=QA/'Freigabestufen';folder.mkdir(exist_ok=True,parents=True)
    (folder/f'Einstieg-{engine}.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    print(engine,len(rows),'Einstiege und Stundenabschlüsse')
if __name__=='__main__':pruefen(sys.argv[1])
