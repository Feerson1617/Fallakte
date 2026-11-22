"""Lesbarkeit der Infokarten und Tastatur-Rückkehr am gebauten Offline-Prototyp."""
import json
import os
import subprocess

from playwright.sync_api import expect, sync_playwright

from runde1_browser import HTML, QA, ROOT, choose, marked_card, sha, start

# Dieselben Druck-/Kartenabschnitte müssen digital ansteuerbar sein.
EXPECTED_SECTIONS = {
    'K': ['material', 'wirkung', 'sti', 'alltag', 'schmerzen'],
    'P': ['wirkung', 'sti', 'alltag', 'eignung', 'schmerzen'],
    'Cu': ['wirkung', 'sti', 'alltag', 'einlage', 'schmerzen'],
    'H': ['wirkung', 'sti', 'alltag', 'einlage', 'schmerzen'],
}
LAYOUTS = [(820, 1180, 100), (1180, 820, 150), (390, 450, 200)]


def set_layout(page, width, height, font):
    page.set_viewport_size({'width': width, 'height': height})
    page.locator('html').evaluate('(node, size) => node.style.fontSize = size + "%"', font)


def read_cards(page, bank, width, height, font):
    page.goto(HTML.as_uri())
    set_layout(page, width, height, font)
    navigation = page.locator('[data-nav=resources]')
    navigation.tap()
    dialog = page.locator('#material-dialog[open]')
    back = dialog.locator('#material-zurueck')
    expect(dialog.locator('.material-auswahl button')).to_have_count(len(EXPECTED_SECTIONS))
    for method, sections in EXPECTED_SECTIONS.items():
        choice = dialog.locator('#material-karte-' + method)
        choice.tap()
        expect(dialog.locator('h2')).to_have_text(bank[method]['title'])
        expect(dialog.locator('[data-section-id]')).to_have_count(len(sections))
        for key in sections:
            section = dialog.locator(f'[data-section-id="{key}"]')
            expect(section.locator('h3')).to_have_text(bank[method]['sections'][key]['title'])
            passage = section.locator('p')
            expect(passage).to_have_text(bank[method]['sections'][key]['text'])
            # A passage can be taller than the viewport. Its beginning and its end must both be reachable.
            for edge in ('start', 'end'):
                passage.evaluate('(p, edge) => p.scrollIntoView({block:edge})', edge)
                visible = passage.evaluate('''(p, edge) => {
                    const area = p.closest('.material-inhalt').getBoundingClientRect();
                    const pos = p.getBoundingClientRect()[edge === 'start' ? 'top' : 'bottom'];
                    return pos >= Math.max(0, area.top) - 1 && pos <= Math.min(innerHeight, area.bottom) + 1;
                }''', edge)
                assert visible, (method, key, edge, width, height, font)
        overflowing = dialog.evaluate('''el => [el, ...el.querySelectorAll('*')]
            .filter(node => node.scrollWidth > node.clientWidth + 1).map(node => node.tagName)''')
        assert not overflowing, (method, width, height, font, overflowing)
        expect(back).to_be_in_viewport(ratio=.99)
        back.tap()
        expect(choice).to_be_focused()
    back.tap()
    expect(navigation).to_be_focused()
    return dict(viewport=[width, height], schrift_prozent=font, karten=EXPECTED_SECTIONS,
                zeilenanfang_und_ende_erreichbar=True, horizontaler_ueberlauf=False,
                zurueck_sichtbar=True, rueckkehrfokus=True)


def working_state(page):
    return page.evaluate('''() => {
        const chat = document.querySelector('#beratung-verlauf');
        return {draft: document.querySelector('[data-strategy][aria-pressed="true"]').dataset.strategy,
                code: document.querySelector('#pruefcode').value, chat: chat.textContent,
                chatScroll: chat.scrollTop, scrollX, scrollY};
    }''')


def return_to_draft(page):
    start(page, 'MSA')
    choose(page, 'Cu')
    code = page.locator('#pruefcode')
    code.fill(' a ')
    page.locator('#fachcheck-pruefen').tap()
    set_layout(page, 390, 450, 200)
    source = page.locator('#passende-karte')
    source.scroll_into_view_if_needed()
    source.focus()
    before = working_state(page)
    source.press('Enter')
    dialog = page.locator('#material-dialog[open]')
    assert marked_card(page) == ('K', 'material')
    expect(dialog.locator('[data-target=true] h3')).to_be_in_viewport()
    page.keyboard.press('Escape')
    expect(source).to_be_focused()
    assert working_state(page) == before

    help_button = page.locator('#hilfe')
    help_button.scroll_into_view_if_needed()
    help_button.focus()
    before = working_state(page)
    help_button.press('Enter')
    for depth in range(1, 5):
        expect(dialog.locator('#hilfe-text')).to_have_attribute('data-depth', str(depth))
        dialog.locator('#hilfe-weiter').press('Enter')
    link = dialog.locator('#hilfe-karte')
    link.scroll_into_view_if_needed()
    link.focus()
    help_scroll = dialog.locator('.material-inhalt').evaluate('el => el.scrollTop')
    link.press('Enter')
    assert marked_card(page) == ('Cu', 'wirkung')
    page.keyboard.press('Escape')
    expect(link).to_be_focused()
    expect(dialog.locator('#hilfe-text')).to_have_attribute('data-depth', '5')
    assert dialog.locator('.material-inhalt').evaluate('el => el.scrollTop') == help_scroll
    page.keyboard.press('Escape')
    expect(help_button).to_be_focused()
    assert working_state(page) == before

    code.fill(' b ')
    code.press('Enter')
    send = page.locator('#nachricht-senden')
    expect(send).to_be_enabled()
    send.scroll_into_view_if_needed()
    expect(send).to_be_in_viewport()
    send.tap()
    expect(page.locator('#beratung-weiter')).to_be_visible()
    return dict(niveau='MSA', abschnitt='L01', strategie='Cu', falscher_code=' a ',
                korrektur=' b ', fehlerquelle=['K', 'material'], hilfequelle=['Cu', 'wirkung'],
                hilfeebene_bei_rueckkehr=5, fokus_und_scroll_erhalten=True,
                entscheidung_code_und_verlauf_erhalten=True, versand_nach_korrektur=True)


def main():
    QA.mkdir(parents=True, exist_ok=True)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = dict(commit=commit, html_sha256=sha(HTML), browsers=[],
                  art='Touch-Emulation mit verkleinerter Höhe. Die echte iPad-Tastatur bleibt im Praxistest zu prüfen.')
    bank = json.loads((ROOT / 'data/laura-0212.json').read_text())['cards']
    with sync_playwright() as pw:
        for engine in ('chromium', 'webkit'):
            browser = getattr(pw, engine).launch(executable_path=os.getenv(engine.upper() + '_EXECUTABLE'))
            page = browser.new_page(is_mobile=True, has_touch=True)
            errors = []
            page.on('pageerror', lambda err: errors.append(str(err)))
            result = dict(engine=engine, version=browser.version, layouts=[])
            for layout in LAYOUTS:
                result['layouts'].append(read_cards(page, bank, *layout))
            result['tastatur'] = return_to_draft(page)
            assert json.loads(page.locator('#materialvertrag').text_content())['buildCommit'] == commit
            assert not errors, (engine, errors)
            result['skriptfehler'] = errors
            report['browsers'].append(result)
            browser.close()
    assert sha(HTML) == report['html_sha256'], 'Die gebaute HTML-Datei hat sich während des Tests geändert.'
    (QA / 'karten.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('Karten und Fokusrückkehr in Chromium und WebKit geprüft:', QA / 'karten.json')


if __name__ == '__main__':
    main()
