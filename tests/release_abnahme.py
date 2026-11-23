"""Independent pupil-side release paths against the offline file and extracted SCO."""
import hashlib
import json
import os
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from lxml import etree
from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'build/Releasepruefung'
APP = ROOT / 'dist/Vorabkandidat'
PRACTICE = ROOT / 'dist/Uebungsakte'
# Matching on biological meaning avoids the bank's keys, marking and button order.
ROUTE = [
    ('K', 'B', r'ohne Latex hält Spermien zurück|fängt Sperma auf', r'Nur ein Kondom aus Latex'),
    ('K', 'C', r'aber nicht ganz|Ein Risiko bleibt', r'schützt alle Hautstellen'),
    ('K+P', 'A', r'regelmäßige Einnahme.*STI-Risiko', r'vergessene Pille nichts'),
    ('K+Cu', 'B', r'Kupfer kann Regelschmerzen verstärken.*Zustimmung', r'gleicht die mögliche Verstärkung'),
    ('K+H', 'C', r'Ob sie passt und Laura die Einlage möchte, ist offen', r'notwendigen? Kombination'),
]
LEVELS = ('Foerder', 'ESA', 'MSA', 'AHR')


def unpack(folder, name, target):
    with ZipFile(folder / (name + '-SCORM12.zip')) as archive:
        assert archive.testzip() is None
        archive.extractall(target)
    manifest = etree.parse(target / 'imsmanifest.xml')
    etree.XMLSchema(etree.parse(target / 'adlcp_rootv1p2.xsd')).assertValid(manifest)
    assert manifest.xpath('string(//*[local-name()="schemaversion"])') == '1.2'
    for href in manifest.xpath('//@href'):
        assert (target / href).is_file(), href
    identifier = manifest.xpath('string(//*[local-name()="item"]/@identifierref)')
    resources = manifest.xpath('//*[local-name()="resource" and @identifier=$id]', id=identifier)
    assert len(resources) == 1
    launch = target / resources[0].attrib['href']
    assert launch.read_bytes() == (folder / (name + '.html')).read_bytes()
    return launch


def choose(day, key):
    button = day.locator(f'[data-strategy="{key}"]')
    if not button.is_visible():
        day.locator('#weitere-strategien summary').tap()
    button.tap()


def route(page, engine, tier, file, size):
    page.set_viewport_size(dict(zip(('width', 'height'), size)))
    page.goto(file.as_uri())
    page.locator('#erster-tag').tap()
    day = page.frame_locator('iframe[title^=Mittwoch]')
    day.locator('#level-' + tier).tap()
    day.locator('#neu').tap()
    send = day.locator('#nachricht-senden')
    paper = tier in ('MSA', 'AHR')
    if size[0] == 390:
        day.locator('html').evaluate("e => e.style.fontSize='150%'")
    for i, (key, code, correct, wrong) in enumerate(ROUTE, 1):
        expect(day.locator('#beratung-stage')).to_have_attribute('data-stage', f'L0{i}')
        expect(send).to_be_hidden()
        if not paper:
            assert 1 <= day.locator('[data-strategy]:visible').count() <= 3
        choose(day, key)
        if i == 4:
            day.locator('#passende-karte').tap()
            expect(day.locator('#material-dialog[open]')).to_have_attribute('data-method', 'Cu')
            expect(day.locator('[data-section-id]:visible')).to_have_attribute('data-section-id', 'schmerzen')
            day.locator('#material-zurueck').tap()
            expect(day.locator('#passende-karte')).to_be_focused()
        if paper:
            field = day.locator('#pruefcode')
            submit = day.locator('#fachcheck-pruefen')
            for invalid in ('', 'Z'):
                field.fill(invalid)
                submit.tap()
                expect(send).to_be_hidden()
                expect(day.locator('#fachmeldung')).not_to_be_empty()
            if i == 1 and size[0] == 390:
                field.tap()
                expect(field).to_be_focused()
                page.set_viewport_size({'width':390, 'height':460})
            field.fill(' ' + code.lower() + ' ')
            submit.tap()
            if i == 1:
                page.screenshot(path=QA / f'{engine}-{tier}-Fachcheck.jpg', quality=70)
                page.set_viewport_size(dict(zip(('width', 'height'), size)))
        else:
            reasons = day.locator('#begruendungen button')
            reasons.filter(has_text=re.compile(wrong, re.I)).tap()
            expect(send).to_be_hidden()
            reasons.filter(has_text=re.compile(correct, re.I)).tap()
        expect(send).to_be_enabled()
        send.evaluate('b => {b.click(); b.click()}')
        expect(day.locator('.chat-entry[data-kind=send]')).to_have_count(i)
        if i < 5:
            day.locator('#beratung-weiter').tap()
    day.locator('#beratung-fertig').tap()
    expect(day.locator('[data-optional=Tom]')).to_be_enabled()
    expect(day.locator('[data-optional=Celina]')).to_be_disabled()


def main():
    QA.mkdir(parents=True, exist_ok=True)
    rows = []
    with TemporaryDirectory() as temp, sync_playwright() as pw:
        sco = unpack(APP, 'Fallakte', Path(temp) / 'gemeinsam')
        uebung = unpack(PRACTICE, 'Uebungsakte', Path(temp) / 'uebung')
        for engine in ('chromium', 'webkit'):
            browser = getattr(pw, engine).launch(executable_path=os.getenv(engine.upper() + '_EXECUTABLE'))
            for i, tier in enumerate(LEVELS):
                size = [(820,1180), (1180,820), (390,844), (390,844)][i]
                # WebKit's offline flag blocks file:// itself, even a blank local page.
                context = browser.new_context(has_touch=True, offline=engine == 'chromium', service_workers='block')
                context.route(re.compile(r'^https?://'), lambda request: request.abort())
                page = context.new_page()
                errors, external = [], []
                page.on('pageerror', lambda exc: errors.append(str(exc)))
                page.on('request', lambda req: external.append(req.url) if req.url.startswith(('http:', 'https:')) else None)
                file = sco if i % 2 else APP / 'Fallakte.html'
                route(page, engine, tier, file, size)
                page.goto(uebung.as_uri())
                page.locator('#tier-' + tier).tap()
                page.locator('#start').tap()
                page.locator('#source').tap()
                expect(page.locator('#cardTitle')).to_contain_text('Kondom')
                page.locator('#back').tap()
                expect(page.locator('#source')).to_be_focused()
                assert not errors and not external, (errors, external)
                rows.append(dict(browser=engine, version=browser.version, niveau=tier, viewport=size,
                                 einstieg=file.name, offline=True, abschnitte=5,
                                 fachcheck='Falsche und richtige Antwort, Doppeltippen',
                                 tastaturflaeche=[390,460] if i >= 2 else None))
                context.close()
            browser.close()
    digest = hashlib.sha256((APP / 'Fallakte.html').read_bytes()).hexdigest()
    (QA / 'Abnahme.json').write_text(json.dumps(dict(html_sha256=digest, wege=rows), indent=2))


if __name__ == '__main__':
    main()
