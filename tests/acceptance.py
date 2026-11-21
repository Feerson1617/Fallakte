"""Run against the standalone and extracted SCO. Artifacts only from successful runs."""
import hashlib
import json
import os
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from zipfile import ZipFile

from playwright.sync_api import sync_playwright, expect
from lxml import etree
from feedback import run_scenarios

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
LOCAL = OUT / 'Fallakte.html'
QA = OUT / 'qa'
QA.mkdir(parents=True, exist_ok=True)
DATA = json.loads((ROOT / 'data/dialogdaten.js').read_text().split('=', 1)[1].strip()[:-1])
MATRIX = (ROOT / 'tests/dialogs.js').read_text()
FORMATS = {'Desktop': (1366, 900), 'iPad-hoch': (820, 1180),
           'iPad-quer': (1180, 820), 'Mobil': (360, 740)}


def save(name, data):
    result = {'html_sha256': hashlib.sha256(LOCAL.read_bytes()).hexdigest(), **data}
    (QA / (name + '.json')).write_text(json.dumps(result, indent=2, ensure_ascii=False))


def test_matrix(browser, engine):
    page = browser.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    records = []
    for level, size in zip(DATA['meta']['levels'], FORMATS.values()):
        page.set_viewport_size(dict(zip(('width','height'),size)))
        for person in DATA['cases']:
            for code in ('K', 'P', 'Cu', 'H', 'K+P', 'K+Cu', 'K+H'):
                page.goto(LOCAL.as_uri())
                records.append(page.evaluate(MATRIX, dict(person=person, tier=level, strategy=code, data=DATA)))
    assert not errors, errors
    page.close()
    return dict(engine=engine,version=browser.version,paths=records,errors=errors,scenarios=run_scenarios(browser,LOCAL,QA if engine=='chromium' else None))


def measure(page):
    issues = page.evaluate("""() => {
      const issues=[];
      if(document.documentElement.scrollWidth>innerWidth+1) issues.push('Seite zu breit');
      for(const e of document.querySelectorAll('button, summary, select, label.combine')){
        if(!e.getClientRects().length)continue;
        const r=e.getBoundingClientRect();
        if(r.width<43.9||r.height<43.9) issues.push('Touchfläche '+e.textContent);
        if(e.scrollWidth>e.clientWidth+2)issues.push('Überlauf '+e.textContent);
      }
      for(const e of document.querySelectorAll('.bubble, .article, #work, .hint')){
        if(e.clientWidth && e.scrollWidth>e.clientWidth+2)issues.push('Text zu breit '+e.className);
      }
      return issues;
    }""")
    assert not issues, issues


def pane(page, name):
    control=page.locator('#'+name)
    if control.is_visible() and control.get_attribute('aria-pressed')!='true':
        control.click()


def send(page, code):
    pane(page,'write-answer')
    page.locator('#method-' + code.split('+')[-1]).click()
    if '+' in code:
        page.locator('#combine').check()
    action = page.get_by_role('button', name='Nachricht senden', exact=True)
    expect(action).to_be_in_viewport(ratio=0.95)
    action.click()


def test_view(browser, engine, layout, size):
    ctx = browser.new_context(viewport=dict(zip(('width','height'), size)),
                              has_touch=layout!='Desktop', is_mobile=layout!='Desktop',
                              device_scale_factor=1, offline=engine=="chromium")
    # WebKit offline emulation also rejects file URLs. Block every HTTP(S) request instead.
    ctx.route(re.compile(r"^https?://"), lambda route: route.abort())
    ctx.add_init_script("""
      window.storageCalls = [];
      for (const [api, method] of [['Storage','setItem'],['IDBFactory','open'],['CacheStorage','open']]) {
        const prototype = window[api]?.prototype;
        if (!prototype) continue;
        const original = prototype[method];
        prototype[method] = function(...args) {
          window.storageCalls.push(api+'.'+method);
          return original.apply(this,args);
        };
      }
    """)
    page = ctx.new_page()
    errors, requests = [], []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('request', lambda r: requests.append(r.url) if r.url.startswith(('http:', 'https:')) else None)
    page.goto(LOCAL.as_uri())
    page.evaluate('document.fonts.ready')
    measure(page)
    if layout=='Desktop' and engine=='chromium':
        page.screenshot(path=QA/'Falluebersicht.jpg', type='jpeg',quality=78,full_page=True)
    tier={'Desktop':'AHR','iPad-hoch':'Foerder','iPad-quer':'MSA','Mobil':'ESA'}[layout]
    page.locator('#level-'+tier).click()
    page.locator('[data-person=Laura]').click()
    pane(page,'write-answer')
    page.locator('#help').click()
    expect(page.locator('.hint')).to_have_count(1)
    page.get_by_role('button',name='Zweite Hilfe').click()
    expect(page.locator('.hint')).to_have_count(2)
    page.get_by_role('button',name='Rückfrage stellen').click()
    page.locator('.question').first.click()
    send(page,'K')
    page.get_by_role('button',name='Vorschlag beibehalten').click()
    send(page,'K+H')
    page.get_by_role('button',name='Vorschlag beibehalten').click()
    pane(page,'write-answer')
    page.get_by_role('button',name='Weiter nach dem Gespräch').click()
    send(page,'P')
    expect(page.locator('.response')).to_contain_text('nicht')
    page.get_by_role('button',name='Vorschlag ändern').click()
    page.locator('#method-H').click()
    page.locator('#help').click()
    page.get_by_role('button',name='Karte „Hormonspirale“ lesen').click()
    expect(page.locator('#card-H')).to_have_attribute('open','')
    page.locator('#resources .return').click()
    expect(page.locator('#method-H')).to_have_attribute('aria-pressed','true')
    page.locator('#combine').check()
    measure(page)
    if engine=='chromium' and layout in ('iPad-hoch','iPad-quer','Mobil'):
        page.screenshot(path=QA/(layout+'.jpg'),type='jpeg',quality=76)
    # Park the reader at the first message, then submit a revision.
    history = page.locator('#history')
    pane(page,'read-chat')
    history.evaluate('(h)=>h.scrollTop=0')
    expect(page.locator('#latest')).to_be_visible()
    pane(page,'write-answer')
    page.locator('#send').click()
    pane(page,'read-chat')
    assert history.evaluate('(h)=>h.scrollTop')<3
    assert 'Kombinationspille' in history.inner_text()
    page.locator('#latest').click()
    assert history.evaluate('(h)=>h.scrollTop')>0
    before=history.inner_text()
    page.locator('#pause-nav').click()
    page.locator('#pause .return').click()
    assert history.inner_text()==before
    page.locator('#cards-nav').click()
    for card in page.locator('#method-cards summary').all():
        card.click()
        measure(page)
    page.locator('#resources .return').click()
    assert history.inner_text()==before
    pane(page,'write-answer')
    for code in ('Cu','P','K+H'):
        page.get_by_role('button',name='Vorschlag beibehalten').click()
        send(page,code)
        measure(page)
    page.get_by_role('button',name='Vorschlag beibehalten').click()
    completed=history.text_content()
    for name in ('Celina','Tom'):
        page.get_by_role('button',name=name+' starten').click()
        for stage in DATA['cases'][name]:
            if 'DONE' in stage['options']:
                if stage['type']=='article':
                    expect(history.locator('.article')).to_be_visible()
                    if tier=='AHR':
                        expect(history.locator('.article')).to_contain_text('266')
                        expect(history.locator('.article')).to_contain_text('YCT-529')
                pane(page,'write-answer')
                if stage['id']=='T2':
                    page.locator('#help').click()
                    page.get_by_role('button',name='Artikel nachlesen').click()
                    expect(history.locator('.article')).to_be_focused()
                    pane(page,'write-answer')
                measure(page)
                page.locator('#work .primary').click()
            else:
                send(page,'K' if name=='Tom' else 'K+Cu')
                measure(page)
                page.get_by_role('button',name='Vorschlag beibehalten').click()
        expect(page.locator('#task-title')).to_have_text('Gespräch abgeschlossen')
        page.locator('#pause-nav').click()
        page.locator('#review-laura').click()
        assert history.text_content()==completed
    storage=page.evaluate("""() => ({
      calls:storageCalls, local:localStorage.length, session:sessionStorage.length, cookies:document.cookie
    })""")
    assert storage == dict(calls=[],local=0,session=0,cookies=''), storage
    page.reload()
    page.locator('[data-person=Laura]').click()
    expect(history.locator('.team')).to_have_count(0)
    assert not errors and not requests, (errors,requests)
    ctx.close()
    return dict(layout=layout,width=size[0],height=size[1],tier=tier,engine=engine,
                version=browser.version,completed=['Laura','Celina','Tom'],external_requests=requests,errors=errors,storage=storage)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):
        pass


def test_scorm(browser):
    with TemporaryDirectory() as temp:
        root=Path(temp)
        with ZipFile(OUT/'Fallakte-SCORM12.zip') as z:
            assert z.testzip() is None
            z.extractall(root)
            members=z.namelist()
        schema=etree.XMLSchema(etree.parse(str(root/'adlcp_rootv1p2.xsd')))
        doc=etree.parse(str(root/'imsmanifest.xml'))
        schema.assertValid(doc)
        launch=doc.find('.//{*}resource').get('href')
        assert (root/launch).read_bytes()==LOCAL.read_bytes()
        # A launch frame with the documented SCORM 1.2 signatures records every API call.
        (root/'host.html').write_text(f'''<script>
          window.calls=[];
          window.API=new Proxy({{}},{{get:(_,key)=>(...args)=>{{calls.push([key,...args]);return 'true';}}}});
          </script><iframe width="820" height="650" src="{launch}"></iframe>''')
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=temp))
        Thread(target=server.serve_forever,daemon=True).start()
        try:
            page=browser.new_page()
            page.goto(f'http://127.0.0.1:{server.server_port}/host.html')
            frame=page.frame_locator('iframe')
            frame.locator('[data-person=Laura]').click()
            frame.locator('#method-Cu').click()
            frame.locator('#send').click()
            assert page.evaluate('calls')==[['LMSInitialize','']]
            page.evaluate("document.querySelector('iframe').src='about:blank'")
            page.wait_for_function('calls.length===2')
            calls=page.evaluate('calls')
            assert calls==[['LMSInitialize',''],['LMSFinish','']]
            page.close()
        finally:
            server.shutdown()
            server.server_close()
    save('scorm',dict(schema_valid=True,launch=launch,members=members,observed_calls=calls))


if __name__=='__main__':
    (QA/'bedienung.json').unlink(missing_ok=True)
    results=[]
    matrices=[]
    with sync_playwright() as p:
        for engine in ('chromium','webkit'):
            exe=os.environ.get(engine.upper()+'_EXECUTABLE')
            browser=getattr(p,engine).launch(**({'executable_path':exe} if exe else {}))
            matrices.append(test_matrix(browser,engine))
            print(engine,'84 Dialogwege und unabhängige Entscheidungsszenarien bestanden.',flush=True)
            if engine=='chromium':
                test_scorm(browser)
                print('SCORM-Schema und LMS-Lebenszyklus bestanden.',flush=True)
            for layout,size in FORMATS.items():
                results.append(test_view(browser,engine,layout,size))
                print(engine,layout,'bestanden',flush=True)
            browser.close()
    save('dialogwege',dict(runs=matrices))
    images={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in QA.glob('*.jpg')}
    save('bedienung',dict(runs=results,screenshots=images,real_ipad=False,itslearning=False,student_trial=False))
