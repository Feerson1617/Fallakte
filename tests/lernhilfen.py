"""Use visible controls to seek help, revise and resume without committing a choice."""
import hashlib
import os

from playwright.sync_api import expect, sync_playwright

from acceptance import LOCAL, QA, ROOT, save


def help_path(browser, level, size, screenshot=None):
    page = browser.new_page(viewport=dict(zip(('width', 'height'), size)), has_touch=True)
    page.goto(LOCAL.as_uri())
    ui = page.locator
    button = lambda name: page.get_by_role('button', name=name, exact=True)
    ui('#level-'+level).click()
    ui('[data-person=Laura]').click()
    history = ui('#history')
    chat_top = history.evaluate('e=>e.scrollTop')
    messages = history.text_content()
    panel = ui('#support-panel')

    def open_three():
        expect(panel).to_be_hidden()
        for n, label in enumerate(('Hilfe','Zweite Hilfe','Satzanfang zeigen'), start=1):
            if n < 3:
                expect(button('Satzanfang zeigen')).to_have_count(0)
            button(label).click()
            expect(panel.locator('.hint')).to_have_count(n)
            expect(ui('#hint-current')).to_be_focused()
            expect(history.locator('.person').last).to_be_in_viewport(ratio=.95)
        expect(button('Satzanfang zeigen')).to_have_count(0)
        expect(ui('#hint-current p')).to_contain_text('…')
        assert page.evaluate('scrollY') == 0
        return ui('#hint-current p').inner_text()

    scaffold = open_three()
    expect(ui('.method[aria-pressed=true]')).to_have_count(0)
    expect(ui('#send')).to_have_count(0)
    expect(ui('#method-P')).to_be_in_viewport(ratio=.99)
    assert history.text_content() == messages and history.evaluate('e=>e.scrollTop') == chat_top
    button('Karte „Kombinationspille“ lesen').click()
    expect(ui('#card-P dt').get_by_text('Infektionsschutz', exact=True)).to_be_focused()
    ui('#resources .return').click()
    expect(ui('#hint-current p')).to_have_text(scaffold)
    button('Hilfe schließen').click()

    ui('#method-Cu').click()
    button('Hilfe').click()
    expect(ui('#hint-current p')).to_contain_text('Kupferspirale')
    ui('#method-P').click()
    expect(panel).to_be_hidden()
    open_three()
    expect(panel.locator('.hint').first).to_contain_text('Kombinationspille')
    expect(panel.locator('.hint').nth(1)).to_contain_text('schützt nicht')
    expect(ui('#send')).to_be_in_viewport(ratio=.99)
    ui('#send').click()
    expect(ui('#task-title')).to_have_text('Laura antwortet')
    expect(ui('.decision-guide')).to_contain_text('Stimmt zuerst')
    expect(ui('.response')).to_contain_text('Infektionen')
    after_reply = history.text_content()
    open_three()
    for label in ('Vorschlag beibehalten','Vorschlag ändern'):
        expect(button(label)).to_be_in_viewport(ratio=.99)
    if screenshot:
        page.screenshot(path=screenshot, type='jpeg', quality=78)
    ui('#pause-nav').click()
    ui('#pause .return').click()
    expect(ui('#hint-current p')).to_have_text(scaffold)
    assert history.text_content() == after_reply
    ui('#home-nav').click()
    ui('[data-person=Tom]').click()
    expect(panel).to_be_hidden()
    ui('#home-nav').click()
    ui('[data-person=Laura]').click()
    assert history.text_content() == after_reply
    expect(panel.locator('.hint')).to_have_count(3)
    button('Vorschlag ändern').click()
    expect(panel).to_be_hidden()
    ui('#method-K').click()
    ui('#additional').select_option('H')
    ui('#send').click()
    button('Vorschlag beibehalten').click()
    expect(ui('#step')).to_have_text('Schritt 2 von 7')
    expect(panel).to_be_hidden()
    page.close()
    return dict(niveau=level, frame=size, vor_auswahl=True, methodenwechsel=True, nach_rueckmeldung=True,
                kartenstelle=True, unterbrechung=True, kombination=True, satzanfang=scaffold)


def independent_panel(browser):
    # The future module can load just these two scripts, without the contraceptive cases.
    page=browser.new_page()
    page.set_content('<main></main><section hidden id="panel"></section>')
    for source in ('ui.js','lernhilfen.js'):
        page.add_script_tag(path=str(ROOT/'app'/source))
    page.evaluate("""() => {
      const steps=['Fundstelle','Sachhinweis','Satzanfang'];
      const panel=document.querySelector('#panel');
      function draw(depth) {
        const entry=el('div');
        document.querySelector('main').replaceChildren(entry);
        panel.replaceChildren();
        panel.hidden=true;
        renderHelp(panel,entry,steps,depth,draw,{label:'Quelle öffnen',open:()=>panel.dataset.source='open'});
      }
      draw(0);
    }""")
    for name in ('Hilfe','Zweite Hilfe','Satzanfang zeigen','Quelle öffnen'):
        page.get_by_role('button',name=name,exact=True).click()
    expect(page.locator('#panel')).to_have_attribute('data-source','open')
    page.get_by_role('button',name='Hilfe schließen').click()
    expect(page.locator('#panel')).to_be_hidden()
    assert page.evaluate("typeof FALLAKTE === 'undefined'")
    page.close()


if __name__ == '__main__':
    results=[]
    with sync_playwright() as p:
        for engine in ('chromium','webkit'):
            exe=os.environ.get(engine.upper()+'_EXECUTABLE')
            browser=getattr(p,engine).launch(**({'executable_path':exe} if exe else {}))
            independent_panel(browser)
            runs=[]
            for level in ('Foerder','ESA','MSA','AHR'):
                shot=QA/'Auffanghilfe.jpg' if (engine,level)==('chromium','Foerder') else None
                runs.append(help_path(browser,level,(820,650) if level in ('Foerder','MSA') else (1024,600),shot))
            assert len({r['satzanfang'] for r in runs})==4
            results.append(dict(engine=engine,version=browser.version,wege=runs))
            browser.close()
    save('lernhilfen',dict(runs=results,lernerprobung=False,
         modulunabhaengig_geprueft=True, screenshot_sha256=hashlib.sha256((QA/'Auffanghilfe.jpg').read_bytes()).hexdigest()))
    print('Acht Hilfewege über alle vier Niveaus in Chromium und WebKit bestanden.')
