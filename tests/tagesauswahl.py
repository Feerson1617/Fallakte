"""Check the actual deliveries against the frozen build and navigate both in real browsers."""
import base64
from contextlib import contextmanager
import hashlib
import io
import json
import os
import re
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Thread
from functools import partial
from http.server import ThreadingHTTPServer
from zipfile import ZipFile

from lxml import etree, html
from playwright.sync_api import expect, sync_playwright

from acceptance import QuietHandler
from paths import complete_laura

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
QA = ROOT / 'build/tagesauswahl'
REFERENCE = 'ca77bf793ef1d2577d2f474895de15c503eb6df2'
TITLES = ['Mittwoch, 02.12.2026', 'Dienstag, 08.12.2026']
HOST = """<!doctype html><html lang="de"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{margin:0}iframe{display:block;border:0;width:100vw;height:100vh}</style>
<script>window.calls=[]; window.API=new Proxy({}, {get:(_,k)=>(...a)=>{calls.push([k,...a]);return 'true'}});</script>
<iframe name="sco" src="index.html"></iframe></html>"""


def digest(data):
    return hashlib.sha256(data).hexdigest()


def reference_build(folder):
    inputs = ('app', 'assets', 'data', 'index.html', 'scorm', 'scripts/build.py')
    archive = subprocess.check_output(['git', 'archive', '--format=zip', REFERENCE, *inputs], cwd=ROOT)
    with ZipFile(io.BytesIO(archive)) as files:
        files.extractall(folder)
        for name in files.namelist():
            if name.endswith('/') or name == 'scripts/build.py':
                continue
            current = ROOT / ('02-12.html' if name == 'index.html' else name)
            assert current.read_bytes() == files.read(name), name
    subprocess.run([sys.executable, 'scripts/build.py'], cwd=folder, check=True)
    return (folder / 'dist/Fallakte.html').read_bytes()


def check_release(version, frozen, site):
    folder = DIST / f'Version-{version}'
    standalone = (folder / 'Fallakte.html').read_bytes()
    with ZipFile(folder / 'Fallakte-SCORM12.zip') as package:
        assert package.testzip() is None
        assert set(package.namelist()) == {'index.html', 'imsmanifest.xml', *(p.name for p in (ROOT/'scorm').glob('*.xsd'))}
        package.extractall(site)
        assert package.read('index.html') == standalone
    schema = etree.XMLSchema(etree.parse(str(site / 'adlcp_rootv1p2.xsd')))
    manifest = etree.parse(str(site / 'imsmanifest.xml'))
    schema.assertValid(manifest)
    assert manifest.getroot().get('identifier') == f'FALLAKTE-{version}'
    resource = manifest.find('.//{*}resource')
    assert resource.get('href') == 'index.html'
    assert resource.get('{http://www.adlnet.org/xsd/adlcp_rootv1p2}scormtype') == 'sco'
    assert manifest.findtext('.//{*}schemaversion') == '1.2'
    assert manifest.find('.//{*}item').get('identifierref') == resource.get('identifier')
    doc = html.fromstring(standalone)
    blobs = {node.get('id'):base64.b64decode(node.text, validate=True)
             for node in doc.xpath('//script[@type="application/octet-stream"]')}
    assert list(blobs) == (['modul-02'] if version == 'A' else ['modul-02', 'modul-08'])
    assert blobs['modul-02'] == frozen
    if version == 'B':
        assert blobs['modul-08'] == (ROOT / 'module/08-12/index.html').read_bytes()
    else:
        assert b'modul-08' not in standalone and b'Dieser Unterrichtstag wird vorbereitet.' not in standalone
    image_paths = ['assets/laura.webp', 'tagesauswahl/assets/laura-umfeld.webp']
    assert [base64.b64decode(src.split(',')[1]) for src in doc.xpath('//img/@src')] == [
        (ROOT/path).read_bytes() for path in image_paths]
    (site / 'host.html').write_text(HOST)
    return {p.name:digest(p.read_bytes()) for p in folder.iterdir() if p.is_file()}


@contextmanager
def host(directory):
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(directory)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}'
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def screenshot(page, name, photos):
    path = QA / (name + '.jpg')
    page.screenshot(path=path, type='jpeg', quality=78, animations='disabled')
    photos[path.name] = digest(path.read_bytes())


def exercise(browser, engine, version, kind, size, base, photos):
    scorm = kind == 'SCORM'
    context = browser.new_context(viewport=dict(zip(('width','height'), size)), has_touch=True,
                                  is_mobile=True, device_scale_factor=1)
    errors, blocked = [], []
    # WebKit's offline flag also blocks file URLs. Allow only the two LMS fixture URLs.
    urls = {base + '/host.html', base + '/index.html'} if scorm else set()
    def route(request):
        if request.request.url in urls:
            request.continue_()
        else:
            blocked.append(request.request.url)
            request.abort()
    context.route('http*/**', route)
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    entry = base + '/host.html' if scorm else (DIST/f'Version-{version}/Fallakte.html').as_uri()
    page.goto(entry)
    shell = page.frame(name='sco') if scorm else page.main_frame
    cards = shell.get_by_role('button')
    expect(cards).to_have_count(2)
    expect(shell.locator('#auswahl header')).to_have_text('Fallakte. Wähle deinen Unterrichtstag.')
    expect(cards).to_have_text(TITLES)
    expect(cards.first).to_be_enabled()
    for card in cards.all():
        expect(card).to_be_in_viewport(ratio=.99)
        assert card.locator('img').evaluate('e=>e.complete && e.naturalWidth>=480')
    if version == 'A':
        expect(cards.last).to_be_disabled()
        cards.last.evaluate('b=>b.click()')
        expect(shell.locator('iframe')).to_have_count(0)
    else:
        expect(cards.last).to_be_enabled()
    prefix = f'{engine}-{version}-{kind}-{size[0]}'
    shell.evaluate('document.fonts.ready')
    screenshot(page, 'Start-'+prefix, photos)
    back = shell.locator('#zurueck')
    if scorm:
        assert page.evaluate('calls') == [['LMSInitialize','']]

    def open_second():
        cards.last.tap()
        second = shell.frame_locator('iframe[title="Dienstag, 08.12.2026"]')
        expect(second.get_by_role('heading', name=TITLES[1])).to_be_visible()
        assert second.locator('body').evaluate("() => typeof FALLAKTE === 'undefined' && typeof LERNHILFEN === 'undefined'")
        assert second.locator('#history,#help').count() == 0
        return second

    if version == 'B':
        open_second()
        expect(shell.locator('iframe')).to_have_count(1)
        screenshot(page, 'Einstieg-08-'+prefix, photos)
        back.tap()
        expect(cards.last).to_be_focused()

    cards.first.tap()
    inner = shell.frame_locator('iframe[title="Mittwoch, 02.12.2026"]')
    expect(inner.locator('#home')).to_be_visible()
    expect(back).to_be_visible()
    assert shell.evaluate("typeof FALLAKTE === 'undefined' && typeof LERNHILFEN === 'undefined'")
    expect(inner.locator('#modul-08,#zweiter-tag')).to_have_count(0)
    inner.locator('#level-Foerder').tap()
    inner.locator('[data-person=Laura]').tap()
    expect(back).to_be_hidden()
    expect(inner.locator('#step')).to_have_text('Laura 1 von 5')
    assert inner.locator('body').evaluate('() => innerHeight') == shell.evaluate('innerHeight')
    inner.locator('#method-P').tap()
    inner.locator('#send').tap()
    for _ in range(5):
        inner.locator('#help').tap()
    snapshot = [inner.locator(s).inner_text() for s in ('#history','#support-panel','#work')]
    assert 'Infektionen' in snapshot[0]
    inner.locator('#cards-nav').tap()
    expect(back).to_be_hidden()
    inner.locator('#resources .return').tap()
    inner.locator('#home-nav').tap()
    back.tap()
    if version == 'B':
        open_second()
        back.tap()
    cards.first.tap()
    inner.locator('[data-person=Laura]').tap()
    assert [inner.locator(s).inner_text() for s in ('#history','#support-panel','#work')] == snapshot
    if version == 'A' and not scorm:
        screenshot(page, 'Hilfe-02-'+prefix, photos)

    # A reload clears the in-memory session. The paper-based recovery still reaches Laura 3.
    if scorm:
        assert page.evaluate('calls') == [['LMSInitialize','']]
    page.reload()
    shell = page.frame(name='sco') if scorm else page.main_frame
    shell.locator('#erster-tag').tap()
    launched = shell.locator('iframe[title="Mittwoch, 02.12.2026"]')
    expect(launched.content_frame.locator('#open-recovery')).to_be_visible()
    frame = launched.element_handle().content_frame()
    frame.locator('#open-recovery').tap()
    expect(shell.locator('#zurueck')).to_be_hidden()
    frame.locator('#recovery').get_by_role('button', name='ESA', exact=True).tap()
    frame.get_by_role('button', name='Laura 3 – Lauras Entscheidung').tap()
    expect(frame.locator('#step')).to_have_text('Laura 3 von 5')
    expect(frame.locator('.recap')).to_be_visible()
    expect(frame.locator('#history .team')).to_have_count(0)
    frame.locator('#home-nav').tap()
    results = [complete_laura(frame, tier, correct_first=True)['total'] for tier in ('Foerder','MSA','AHR')]
    assert results == [12,12,12]
    if scorm:
        page.locator('iframe').evaluate("e => e.src='about:blank'")
        page.wait_for_function('calls.length === 2')
        calls = page.evaluate('calls')
        assert calls == [['LMSInitialize',''],['LMSFinish','']]
    else:
        calls = []
    assert not errors and not blocked, (errors, blocked)
    context.close()
    return dict(browser=engine, browserversion=browser.version, version=version, format=kind,
                viewport=size, vollstaendige_korrekturwege=results, wiederaufnahme='Laura 3, ESA',
                hilfen_vor_und_nach_tageswechsel=5, scorm_sitzung=calls, fehler=errors, externe_zugriffe=blocked)


def main():
    QA.mkdir(parents=True, exist_ok=True)
    results, photos, bundles = [], {}, {}
    with TemporaryDirectory() as directory:
        root = Path(directory)
        frozen = reference_build(root / 'original')
        for version in 'AB':
            bundles[version] = check_release(version, frozen, root / version)
        # Both launches differ only in the allowed card and its optional document.
        common = (root/'B/index.html').read_bytes().replace(
            b'aria-labelledby="datum-08" data-entry="modul-08"', b'aria-labelledby="datum-08" disabled')
        common, count = re.subn(rb'<script id="modul-08" type="application/octet-stream">[A-Za-z0-9+/=]+</script>\n', b'', common)
        assert count == 1 and common == (root/'A/index.html').read_bytes()
        with host(root) as address, sync_playwright() as playwright:
            for engine in ('chromium','webkit'):
                exe = os.environ.get(engine.upper()+'_EXECUTABLE')
                browser = getattr(playwright,engine).launch(executable_path=exe)
                for version in 'AB':
                    for kind in ('HTML','SCORM'):
                        for size in ((820,1180),(1180,820)):
                            results.append(exercise(browser,engine,version,kind,size,address+'/'+version,photos))
                            print(engine,version,kind,size,'bestanden',flush=True)
                browser.close()
    report = dict(referenz=REFERENCE, modul_02_sha256=digest(frozen), pakete=bundles, durchlaeufe=results, bilder=photos)
    (QA/'Tagesauswahl.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')


if __name__ == '__main__':
    main()
