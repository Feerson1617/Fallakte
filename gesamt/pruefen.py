"""Black-box acceptance on the staged local HTML and the unzipped SCORM launch documents."""
import functools
import json
import os
import re
import sys
import threading
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from lxml import etree,html
from playwright.sync_api import sync_playwright,expect

from auslieferung import ROOT,SRC,OUT,QA,VERSIONS,sha,revision,json_text
from karten import LEVELS,METHODS,printed,compare
sys.path.insert(0,str(ROOT/'tests'))
from vorbereitung_browser import STEPS,HOST,Quiet
from bauen import contracts

CARD_TEST=(SRC/'karten_browser.js').read_text()
MENU={'vor':'vorbereitung','02':'erster-tag','08':'zweiter-tag'}
HOST_URL='http://127.0.0.1'
def button(frame,action,value=None):
    loc=frame.locator(f'[data-do="{action}"]'+('' if value is None else f'[data-value="{value}"]'))
    loc.click()

def enter(shell,key):
    shell.locator('#'+MENU[key]).click()
    iframe=shell.locator('#arbeitsplatz > iframe:visible')
    expect(iframe).to_have_count(1)
    frame=iframe.element_handle().content_frame()
    if key=='vor':expect(frame.locator('body > header')).to_be_hidden()
    return frame

def overview(shell):
    shell.locator('#modulaktionen [data-action=home]').click()

def photo(page,name):
    page.screenshot(path=QA/(name+'.jpg'),quality=68,animations='disabled')

def unpack(folder):
    import base64
    contents={}
    module_hashes=json.loads((QA/'Module.json').read_text())
    for version,allowed in VERSIONS.items():
        stem='Fallakte-'+version
        target=folder/version
        with ZipFile(OUT/(stem+'-SCORM12.zip')) as z:
            assert z.testzip() is None
            assert set(z.namelist())=={'imsmanifest.xml','index.html',*(p.name for p in (ROOT/'scorm').glob('*.xsd'))}
            z.extractall(target)
        raw=(target/'index.html').read_bytes()
        assert raw==(OUT/(stem+'.html')).read_bytes()
        manifest=etree.parse(str(target/'imsmanifest.xml'))
        etree.XMLSchema(etree.parse(str(target/'adlcp_rootv1p2.xsd'))).assertValid(manifest)
        assert manifest.xpath('string(//*[local-name()="schemaversion"])')=='1.2'
        assert manifest.xpath('//*[local-name()="resource"]/@href')==['index.html']
        doc=html.fromstring(raw)
        scripts=doc.xpath('//script[@type="application/octet-stream"]')
        ids=[s.get('id').removeprefix('modul-') for s in scripts]
        assert ids==list(allowed)
        hashes={k:sha(base64.b64decode(s.text,validate=True)) for k,s in zip(ids,scripts)}
        assert hashes=={k:module_hashes[k] for k in allowed}
        # Independent text/structure comparison against the frozen modules runs in sprachpruefung.py.
        prep=html.fromstring(base64.b64decode(scripts[ids.index('vor')].text))
        assert json.loads(prep.get_element_by_id('material').text)['cards']==json.loads((QA/'Referenzkarten.json').read_text())
        for key,id_ in MENU.items():
            card=doc.get_element_by_id(id_)
            assert (card.get('data-entry')=='modul-'+key)==(key in allowed)
            assert ('disabled' in card.attrib)==(key not in allowed)
        assert not doc.xpath('//script[@src] | //link[@href]')
        assert all(x.startswith('data:') for x in doc.xpath('//@src'))
        assert doc.xpath('string(//meta[@name="revision"]/@content)')==('562ea2566dd80e31c093f313b925adcb31e22c9a' if version=='Vorbereitung' else revision())
        (target/'host.html').write_text(HOST)
        contents[version]=hashes
    assert (folder/'Gesamt/index.html').read_bytes()==(folder/'08-12/index.html').read_bytes()
    return contents

def fit(frame):
    assert frame.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
    assert frame.locator('button:visible').evaluate_all('(bs)=>bs.every(b=>b.getBoundingClientRect().height>=43.9)')

def launch(page,base,version,delivery):
    if delivery=='Offline':
        page.goto((OUT/('Fallakte-'+version+'.html')).as_uri())
        return page.main_frame
    page.goto(base+'/'+version+'/host.html')
    page.frame_locator('iframe').locator('#auswahl').wait_for()
    return page.frames[1]

def frames_test(page,shell,allowed,engine,version,delivery):
    assert shell.locator('#auswahl .tag:enabled').count()==len(allowed)
    assert shell.locator('#auswahl .tag').count()==3
    assert not shell.locator('#arbeitsplatz iframe').count()
    fit(shell)
    if engine=='chromium' and delivery=='Offline':photo(page,'Start-'+version)
    prep=enter(shell,'vor');button(prep,'level','ESA');button(prep,'picker');button(prep,'open','3A');button(prep,'begin')
    button(prep,'choice',0);button(prep,'hint')
    shell.locator('#zurueck').click()
    if '02' in allowed:
        day=enter(shell,'02')
        day.locator('#level-MSA').click();day.locator('#neu').click()
        day.locator('[data-strategy="K"]').click()
        if version=='02-12' and engine=='webkit' and delivery=='SCORM':photo(page,'Laura-02')
        shell.locator('#zurueck').click()
    if '08' in allowed:
        day=enter(shell,'08')
        day.locator('#level-0').select_option('AHR');day.locator('#start').click()
        if version=='08-12' and engine=='webkit' and delivery=='SCORM':photo(page,'Familienrat-08')
        shell.locator('#zurueck').click()
    prep=enter(shell,'vor')
    expect(prep.locator('[data-do=choice][data-value="0"]')).to_have_attribute('aria-pressed','true')
    expect(prep.locator('.help')).to_contain_text('Hilfe 1')
    expect(shell.locator('#gespraechsstand')).to_have_text('ESA')
    overview(shell);button(prep,'resume');expect(prep.locator('h1')).to_contain_text('3A')
    shell.locator('#zurueck').click()
    if '02' in allowed:
        day=enter(shell,'02')
        expect(day.locator('#beratung-stage')).to_have_attribute('data-stage','L01')
        expect(day.get_by_text('Dein Rat · Kondom',exact=True)).to_be_visible()
        shell.locator('#zurueck').click()
    if '08' in allowed:
        day=enter(shell,'08');expect(day.locator('aside')).to_be_visible()
        shell.locator('#zurueck').click()
    if delivery=='SCORM':assert page.evaluate('calls')==[['LMSInitialize','']]
    page.reload()
    if delivery=='SCORM':
        page.frame_locator('iframe').locator('#auswahl').wait_for()
        shell=page.frames[1]
    assert shell.locator('#arbeitsplatz iframe').count()==0
    prep=enter(shell,'vor');button(prep,'level','ESA')
    assert prep.locator('[data-do=resume]').count()==0
    button(prep,'picker')
    assert not prep.locator('.chapters small').count()
    if version=='Vorbereitung' and engine=='webkit' and delivery=='SCORM':photo(page,'Wiederaufnahme')
    button(prep,'open','3A');expect(prep.locator('#supporting')).to_be_visible()
    if '02' in allowed:
        shell.locator('#zurueck').click();day=enter(shell,'02')
        shell.locator('[data-action=recovery]').click();day.locator('#wieder-level-MSA').click()
        day.locator('#abschnitte button').nth(2).click()
        expect(day.locator('#beratung-stage')).to_have_attribute('data-stage','L03')
        assert day.locator('#beratung-verlauf [data-kind=send]').count()==0
    if '08' in allowed:
        shell.locator('#zurueck').click();day=enter(shell,'08')
        shell.locator('[data-action=recovery]').click()
        day.locator('#level-0').select_option('AHR')
        day.locator('#person').select_option('Freundin');day.locator('#entry').select_option('3')
        day.locator('#open-entry').click();expect(day.locator('h1')).to_have_attribute('data-section','FR-04')
    shell.locator('#zurueck').click()
    shell.locator('html').evaluate("e=>e.style.fontSize='150%'")
    fit(shell)

def read_modal(frame,method):
    button(frame,'reference',method)
    card=frame.locator('dialog[open] .reference').evaluate('el=>readPrintedCard(el)')
    frame.locator('#close-sheet').click()
    return card

def card_routes(page,open_shell,frame,shell,level,lesson,trace,save):
    # The regular black-box path just finished 4B and returned to the section picker.
    button(frame,'open','4B')
    expected=frame.locator('#checked-chapters').inner_text()
    expect(frame.locator('#view .paper')).to_contain_text('an der gestrichelten Linie')
    final={k:read_modal(frame,k) for k in METHODS}
    assert frame.locator('#checked-chapters').inner_text()==expected
    overview(shell)
    shell=open_shell();frame=enter(shell,'vor')
    button(frame,'level',level)
    assert frame.locator('[data-do=resume]').count()==0
    frame.evaluate(CARD_TEST)
    fallback={};resume={}
    for number,method in enumerate(METHODS,1):
        button(frame,'references');fallback[method]=read_modal(frame,method)
        button(frame,'picker');button(frame,'open',f'{number}B');button(frame,'begin')
        if save and number==1:photo(page,'Vorbereitung-'+level)
        chapter=lesson['chapters'][number*2-1]
        for q in chapter['questions']:
            button(frame,'choice',next(i for i,o in enumerate(q['options']) if o['correct']))
            button(frame,'check');button(frame,'advance')
        button(frame,'review');overview(shell);button(frame,'resume')
        resume[method]=frame.locator('#view .reference').evaluate('el=>readPrintedCard(el)')
        if save and method=='Cu':photo(page,'Musterkarte-'+level)
        overview(shell)
    rows=[]
    for n,k in enumerate(METHODS,1):
        entries=trace['entries'][f'{n}A']+trace['entries'][f'{n}B']
        ways={'B-Vergleich':trace['review'][f'{n}B'],'Weiterarbeiten':resume[k],'Ausfall/Zeitnot nach Neustart':fallback[k],'Abschluss 4B':final[k]}
        rows.append((k,entries,ways))
    return rows

def session_log(page):
    page.locator('iframe').evaluate("f=>{f.src='about:blank'}")
    page.wait_for_function("calls.some(c=>c[0]==='LMSFinish')")
    assert page.evaluate('calls')==[['LMSInitialize',''],['LMSFinish','']]

def run():
    from sprachfassung import redigieren
    paper=printed();lessons,cards=contracts();redigieren(lessons)
    evidence={};flows=[];sessions=[]
    with TemporaryDirectory() as tmp,sync_playwright() as pw:
        folder=Path(tmp);contents=unpack(folder)
        server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=tmp))
        threading.Thread(target=server.serve_forever,daemon=True).start()
        base=HOST_URL+':'+str(server.server_port)
        try:
            for engine in ('chromium','webkit'):
                with getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as browser:
                    for delivery in ('Offline','SCORM'):
                        for version,allowed in VERSIONS.items():
                            size=(820,1180) if delivery=='Offline' else (1180,820)
                            if version=='Vorbereitung' and delivery=='SCORM':size=(390,560)
                            ctx=browser.new_context(viewport=dict(zip(('width','height'),size)),has_touch=True)
                            page=ctx.new_page();errors=[];addresses=[];storage=[]
                            page.on('pageerror',lambda e:errors.append(str(e)))
                            page.on('request',lambda r:addresses.append(r.url))
                            ctx.expose_binding('reportStorage',lambda _,name:storage.append(name))
                            ctx.add_init_script("""for(const k of ['setItem','removeItem','clear']){
                              const orig=Storage.prototype[k];Storage.prototype[k]=function(...a){reportStorage(k);return orig.apply(this,a)}}
                              if(window.indexedDB){const orig=IDBFactory.prototype.open;IDBFactory.prototype.open=function(...a){reportStorage('indexedDB');return orig.apply(this,a)}}""")
                            def open_shell():return launch(page,base,version,delivery)
                            shell=open_shell()
                            frames_test(page,shell,allowed,engine,version,delivery)
                            if version=='Gesamt':
                                for level,lesson in lessons['levels'].items():
                                    for assisted in (False,True):
                                        shell=open_shell();frame=enter(shell,'vor');frame.evaluate(CARD_TEST)
                                        stats=frame.evaluate(STEPS,dict(lesson=lesson,cards=cards['levels'][level],ui=lessons['ui'],
                                            level=level,assisted=assisted,embedded=True))
                                        flows.append(dict(browser=engine,ausgabe=delivery,niveau=level,hilfen=assisted,fragen=stats['Fragen']))
                                        if assisted:
                                            overview(shell);expect(frame.locator('.levels')).to_be_visible()
                                            continue
                                        trace=frame.evaluate('window.cardTrace')
                                        for method,entries,ways in card_routes(page,open_shell,frame,shell,level,lesson,trace,engine=='chromium' and delivery=='Offline'):
                                            ref=paper[level,method];fingerprint=compare(ref,entries,ways)
                                            key=f'{level}/{method}'
                                            row=evidence.setdefault(key,dict(niveau=LEVELS[level],methode=ref['title'],seite=ref['page'],
                                                felder=entries,text_sha256=fingerprint,schueler_pdf_sha256=ref['student_sha256'],
                                                referenz_pdf_sha256=ref['reference_sha256'],wege=list(ways),laeufe=[]))
                                            assert row['text_sha256']==fingerprint and row['felder']==entries
                                            row['laeufe'].append(engine+'/'+delivery)
                            if delivery=='SCORM':session_log(page)
                            assert not errors and not storage and not ctx.cookies(),(errors,storage)
                            allowed_http={base+'/'+version+'/host.html',base+'/'+version+'/index.html'}
                            assert all(u.startswith(('file:','data:','about:')) or u in allowed_http for u in addresses),addresses
                            ctx.close();sessions.append([engine,delivery,version,size])
                            print(engine,delivery,version,'bestanden',flush=True)
        finally:server.shutdown();server.server_close()
    assert len(evidence)==16 and all(len(r['laeufe'])==4 for r in evidence.values())
    assert len(flows)==32 and len(sessions)==16
    (QA/'Browserpruefung.json').write_text(json_text(dict(commit=revision(),module=contents,sitzungen=sessions,wege=flows)))
    (QA/'Kartenpruefung.json').write_text(json_text(dict(commit=revision(),karten=list(evidence.values()))))

if __name__=='__main__':run()
