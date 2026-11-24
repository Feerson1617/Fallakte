"""Blackbox-Abnahme der Auslieferungen. Prüforakel ist das separat gelesene Planungs-ZIP."""
import functools
import json
import os
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from playwright.sync_api import sync_playwright

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vorbereitung'))
from bauen import OUT, QA, contracts, digest, json_text, revision

STEPS=Path(__file__).with_name('vorbereitung_wege.js').read_text()
SIZES={'iPad-hoch':(768,1024),'iPad-quer':(1024,768),'klein':(390,600)}
HOST="""<!doctype html><meta charset="utf-8"><title>SCORM-Testhost</title>
<style>*{box-sizing:border-box}html,body,iframe{margin:0;width:100%;height:100%;border:0;display:block}</style>
<script>window.calls=[];window.API=new Proxy({}, {get:(_,key)=>(...args)=>{calls.push([key,...args]);return 'true'}})</script>
<iframe title="Lernstationen" src="index.html"></iframe>"""


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):
        pass


def action(frame,action,value=None):
    locator=frame.locator('[data-do="'+action+'"]'+('' if value is None else '[data-value="'+str(value)+'"]'))
    locator.click(timeout=4500)


def navigation(page,frame,reopen,lesson,level,engine,layout,save):
    def click(command,value=None):
        action(frame,command,value)
    def take(name):
        if save:
            page.screenshot(path=QA/(engine+'-'+layout+'-'+name+'.png'))
    def visible(text):
        assert text in frame.locator('#view').inner_text()
    def fits():
        assert frame.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        assert frame.locator('button:visible').evaluate_all('(bs)=>bs.every(b=>b.getBoundingClientRect().height>=43.9)')
    click('level',level)
    fits();take('Start')
    click('picker')
    for chapter in lesson['chapters']:
        click('open',chapter['id']);visible(chapter['title']);fits()
        assert frame.locator('figure svg text').evaluate_all('(nodes)=>nodes.every(n=>{const b=n.getBBox();return b.x>=0 && b.x+b.width<=351})')
        if save and engine=='chromium':
            frame.locator('figure').screenshot(path=QA/('Grafik-'+chapter['id']+'.png'))
        click('home');click('picker')
    click('open','3A')
    take('Material');click('begin')
    q=lesson['chapters'][4]['questions'][0]
    wrong=next(i for i,o in enumerate(q['options']) if not o['correct'])
    right=next(i for i,o in enumerate(q['options']) if o['correct'])
    click('choice',wrong);click('check');visible(q['options'][wrong]['feedback']);click('hint')
    click('home');click('level','ESA')
    assert not frame.locator('[data-do=resume]').count()
    click('picker');click('open','4B');click('home');click('level',level);click('resume')
    visible(q['options'][wrong]['feedback']);visible(q['options'][wrong]['hints'][0]);take('Fehlversuch-Hilfe')
    click('material')
    assert lesson['chapters'][4]['supportingInfo'] in frame.locator('#sheet').inner_text()
    frame.locator('#close-sheet').click()
    click('choice',right);click('check');visible('Mit Hilfe 1 gelöst.')
    click('advance');q=lesson['chapters'][4]['questions'][1]
    wrong=next(i for i,o in enumerate(q['options']) if not o['correct'])
    click('choice',wrong);click('check');click('choice',next(i for i,o in enumerate(q['options']) if o['correct']))
    click('check');visible('Nach Korrektur gelöst.');click('advance');take('Papier');fits()
    click('home');click('new');frame.locator('#close-sheet').click();click('resume');visible('Infokarte ergänzen')
    code=frame.locator('#code')
    code.fill(' c ');click('code-check')
    assert frame.locator('[data-do=send]').is_enabled()
    code.fill('C!');assert frame.locator('[data-do=send]').is_disabled()
    click('code-check');visible('Gib einen der Buchstaben')
    code.fill(' c ');click('code-check');click('send');visible('Nachricht gesendet')
    if save and engine=='chromium':take('Code-gesendet')
    click('home');click('references')
    for i,card in enumerate(('K','P','Cu','H')):
        if i:click('references')
        click('reference',card)
        assert frame.locator('dialog .fields li').count()==4
        if i==1 and save and engine=='chromium':take('Ausfallkarte')
        frame.locator('#close-sheet').click()
    click('picker')
    assert 'In dieser Sitzung bearbeitet' not in frame.locator('#view').inner_text()
    click('open','1A');click('begin')
    reference_q=lesson['chapters'][0]['questions'][0]
    click('choice',next(i for i,o in enumerate(reference_q['options']) if o['correct']));click('check')
    visible('Nach Ansicht der Musterkarte gelöst.')
    click('home');click('new');click('reset')
    visible(lesson['intro']['title']);click('home');click('level','ESA');click('resume');visible('4B')
    frame=reopen()
    assert not frame.locator('[data-do=resume]').count()
    action(frame,'level',level);action(frame,'picker')
    assert frame.locator('.chapters small').count()==0
    action(frame,'open','3A')
    assert lesson['chapters'][4]['title'] in frame.locator('h1').inner_text()
    action(frame,'begin')
    assert frame.locator('[data-do=check]').is_disabled()
    return frame


def test_endings(page,frame,lesson,level,engine,delivery):
    """Echte Unterbrechungen vor dem Papierende, ein direkter Start und ein vollständiger Reload."""
    chapters={ch['id']:ch for ch in lesson['chapters']}
    evidence={}
    def click(command,value=None):
        action(frame,command,value)
    def solve(chapter_id,number):
        q=chapters[chapter_id]['questions'][number]
        assert q['prompt'] in frame.locator('#view h2').inner_text()
        click('choice',next(i for i,o in enumerate(q['options']) if o['correct']))
        click('check');click('advance')
    def open_chapter(key):
        click('picker');click('open',key);click('begin')
    def end_b(key,pause=False):
        open_chapter(key)
        solve(key,0);solve(key,1)
        assert frame.locator('[data-do="review"]').inner_text()=='Vollständige Karte vergleichen'
        click('review')
        if pause:
            click('home');click('resume')
        assert frame.locator('h1').inner_text()==chapters[key]['title']
        assert frame.locator('.reference .fields li').count()==4
        click('finish')
        title='Ende der ersten Vorbereitungsstunde' if key=='2B' else 'Abschluss der Vorbereitung'
        assert frame.locator('h1').inner_text()==title
    def status(stage,expected):
        actual=frame.locator('#checked-chapters').inner_text().split(', ')
        assert actual==expected,(engine,delivery,level,stage,actual)
        evidence[stage]=actual

    click('level',level)
    if (engine,delivery,level)==('chromium','Offline','Foerder'):
        # Die Zwischenansicht genau beim Übergang fotografieren, bevor 3A beginnt.
        click('picker');click('open','1A')
        for key in ('1A','1B','2A','2B'):
            click('begin');solve(key,0);solve(key,1)
            if key.endswith('B'):click('review')
            click('finish')
        assert frame.locator('[data-value="3A"]').is_visible()
        page.screenshot(path=QA/'Zwischenansicht-2B.png')
        click('home');click('new');click('reset');click('home')
    open_chapter('1A');solve('1A',0);click('home')
    end_b('2B',pause=True)
    status('2B nach unterbrochenem 1A',['2B'])
    assert 'Du hast Kondom und Kombinationspille bearbeitet.' not in frame.locator('#view').inner_text()
    click('home');click('resume');status('Zwischenansicht wiederaufgenommen',['2B'])
    click('open','3A');click('begin');solve('3A',0);solve('3A',1)
    # Förder/ESA haben jetzt beide Fachfragen gelöst, das Papierende fehlt.
    # MSA/AHR fehlt zusätzlich der noch nicht gesendete Code des Papierchecks.
    click('home');end_b('4B')
    completed=['2B','4B'] if chapters['3A']['paperCheck'] else ['2B','3A','4B']
    status('4B nach unterbrochenem 3A',completed)
    for method in ('K','P','Cu','H'):
        click('reference',method)
        assert frame.locator('dialog .fields li').count()==4
        frame.locator('#close-sheet').click()
    status('Nach Vergleich aller vier Musterkarten',completed)
    click('home');click('resume');status('Abschluss wiederaufgenommen',completed)
    page.reload()
    if delivery=='SCORM':
        page.frame_locator('iframe').locator('#view h1').wait_for()
        frame=page.frames[1]
    else:
        frame=page.main_frame
    click('level',level)
    assert frame.locator('[data-do=resume]').count()==0
    end_b('4B');status('Direkt in 4B nach Neuladen',['4B'])
    if engine=='webkit' and delivery=='Offline' and level=='AHR':
        page.screenshot(path=QA/'Abschluss-4B-nach-Neuladen.png')
    click('home');end_b('2B');status('Direkt in 2B ohne frühere Stunde',['2B'])
    if engine=='webkit' and delivery=='Offline' and level=='AHR':
        page.screenshot(path=QA/'Zwischenansicht-2B-Direkteinstieg.png')
    return dict(Browser=engine,Ausgabe=delivery,Niveau=level,Fachchecks=evidence)


def test():
    s,c=contracts()
    results=[]; transcripts=[]; navigation_runs=[]; endings=[]
    QA.mkdir(exist_ok=True,parents=True)
    with TemporaryDirectory() as folder,sync_playwright() as pw:
        with ZipFile(OUT/'Vorbereitung-SCORM12.zip') as z:z.extractall(folder)
        (Path(folder)/'host.html').write_text(HOST)
        server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=folder))
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        try:
            for engine in ('chromium','webkit'):
                custom=os.getenv('WEBKIT_EXECUTABLE') if engine=='webkit' else None
                with getattr(pw,engine).launch(executable_path=custom) as browser:
                    for delivery in ('Offline','SCORM'):
                        for layout,(w,h) in SIZES.items():
                            context=browser.new_context(viewport=dict(width=w,height=h),has_touch=True)
                            page=context.new_page()
                            errors=[];requests=[]
                            page.on('pageerror',lambda e:errors.append(str(e)))
                            page.on('request',lambda r:requests.append(r.url))
                            def open_app():
                                if delivery=='Offline':
                                    page.goto((OUT/'Vorbereitung.html').as_uri())
                                    return page.main_frame
                                page.goto('http://127.0.0.1:'+str(server.server_port)+'/host.html')
                                iframe=page.frame_locator('iframe')
                                iframe.locator('#view h1').wait_for()
                                return page.frames[1]
                            frame=open_app()
                            frame=navigation(page,frame,open_app,s['levels']['MSA'],'MSA',engine,layout,
                                             delivery=='Offline' and ((engine=='chromium' and layout=='iPad-hoch') or (engine=='webkit' and layout in ('klein','iPad-quer'))))
                            navigation_runs.append([engine,delivery,layout])
                            if layout=='iPad-hoch':
                                for assisted in (False,True):
                                    frame=open_app()
                                    for level,lesson in s['levels'].items():
                                        record=frame.evaluate(STEPS,dict(lesson=lesson,cards=c['levels'][level],ui=s['ui'],level=level,assisted=assisted))
                                        snapshots=record.pop('Auftraege')
                                        if engine=='chromium' and delivery=='Offline' and not assisted:transcripts.extend(snapshots)
                                        results.append(dict(Browser=engine,Ausgabe=delivery,**record))
                                        if engine=='chromium' and delivery=='Offline' and level=='Foerder' and not assisted:
                                            action(frame,'picker');action(frame,'open','4B')
                                            page.screenshot(path=QA/'Abschluss-4B.png')
                                            action(frame,'home')
                            if layout=='iPad-quer':
                                for level,lesson in s['levels'].items():
                                    endings.append(test_endings(page,open_app(),lesson,level,engine,delivery))
                            if layout=='klein':
                                frame.locator('html').evaluate("n=>n.style.fontSize='150%'")
                                assert frame.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                            if delivery=='SCORM':
                                page.locator('iframe').evaluate("f=>{f.src='about:blank'}")
                                page.wait_for_function("calls.some(c=>c[0]==='LMSFinish')")
                                assert page.evaluate('calls')==[['LMSInitialize',''],['LMSFinish','']]
                            assert not errors,errors
                            assert all(u.startswith(('file:', 'http://127.0.0.1:', 'data:', 'about:')) for u in requests),requests
                            assert not context.cookies()
                            context.close()
                        print(engine,delivery,'bestanden',flush=True)
        finally:server.shutdown();server.server_close()
    (QA/'Browserpruefung.json').write_text(json_text(dict(commit=revision(),
        HTML_SHA256=digest((OUT/'Vorbereitung.html').read_bytes()),Navigation=navigation_runs,Abschlusswege=endings,Wege=results)))
    (QA/'Bildschirmwortlaut.json').write_text(json_text(transcripts))


if __name__=='__main__':test()
