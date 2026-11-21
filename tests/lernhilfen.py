"""Use visible controls to seek help, revise and resume without committing a choice."""
import hashlib
import os

from playwright.sync_api import expect, sync_playwright

from acceptance import LOCAL, QA, ROOT, save


def help_path(browser, level, size, photos=False):
    page = browser.new_page(viewport=dict(zip(('width', 'height'), size)), has_touch=True)
    page.goto(LOCAL.as_uri())
    ui = page.locator
    button = lambda name: page.get_by_role('button', name=name, exact=True)
    ui('#level-'+level).click()
    ui('[data-person=Laura]').click()
    history = ui('#history')
    expect(history.locator('.person p').first).to_have_text(
        'Hi, ich bin Laura. Ich bin 19.' if level=='Foerder' else 'Hi, ich bin Laura, 19.')
    messages = history.text_content()
    chat_box = history.bounding_box()
    panel = ui('#support-panel')
    labels = ('Du kommst nicht weiter? – Hilfe anzeigen','Zweite Hilfe','Satzanfang zeigen',
              'Beispiel zeigen','Nächsten Schritt zeigen')

    def shot(name):
        if photos:
            page.screenshot(path=QA/(name+'.jpg'), type='jpeg', quality=78)

    def ready(control):
        # No locator click/scroll before measuring. Detect clipping and overlapping siblings.
        expect(control).to_be_in_viewport(ratio=.99)
        if ui('#room').is_visible():
            assert abs(ui('#help-dock').evaluate('e=>e.getBoundingClientRect().bottom-innerHeight'))<=1
        assert control.evaluate("""b=>{const r=b.getBoundingClientRect();
            return b.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2));}""")

    def open_to(depth):
        expect(panel).to_be_hidden()
        scroll = history.evaluate('e=>e.scrollTop')
        for n,label in enumerate(labels[:depth],1):
            ready(button(label))
            expect(ui('#help-action')).to_have_count(0)
            button(label).click()
            expect(panel.locator('.hint')).to_have_count(n)
            expect(ui('#hint-current')).to_be_focused()
            assert history.bounding_box() == chat_box and history.evaluate('e=>e.scrollTop') == scroll
        assert page.evaluate('scrollY') == 0

    ready(button(labels[0]))
    shot('Hilfe-vor-Auswahl')
    open_to(3)
    scaffold = ui('#hint-current p').inner_text()
    expect(panel.locator('.hint').first).to_contain_text('Karte „Kondom“, Abschnitt „Infektionsschutz“')
    expect(ui('.method[aria-pressed=true]')).to_have_count(0)
    expect(ui('#send')).to_have_count(0)
    assert history.text_content() == messages
    button('Karte „Kondom“ lesen').click()
    expect(ui('#card-K dt').get_by_text('Infektionsschutz', exact=True)).to_be_focused()
    ready(ui('#resources .return'))
    ui('#resources .return').click()
    expect(ui('#hint-current p')).to_have_text(scaffold)
    button('Vorherige Hilfe').click()
    expect(ui('#hint-current p')).to_contain_text('Risiko')
    button('Hilfe schließen').click()

    ui('#method-Cu').click()
    button(labels[0]).click()
    expect(ui('#hint-current p')).to_contain_text('Kupferspirale')
    ui('#method-P').click()
    expect(panel).to_be_hidden()
    ui('#work').evaluate('e=>e.scrollTop=e.scrollHeight')
    open_to(2)
    expect(panel.locator('.hint').first).to_contain_text('Kombinationspille')
    ready(ui('#send'))
    ui('#send').click()
    expect(ui('#task-title')).to_have_text('Laura antwortet')
    expect(ui('.decision-guide')).to_contain_text('Vorschlag ändern')
    expect(ui('.decision-guide')).to_contain_text('schützt nicht vor Infektionen')
    after_reply = history.text_content()
    ready(button(labels[0]))
    shot('Hilfe-nach-Rueckmeldung')
    open_to(5)
    expect(panel.locator('.hint').first).to_contain_text('Kondom')
    expect(ui('#hint-current p')).to_contain_text('Nachricht senden')
    expect(ui('#help-action')).to_have_text('Kondom als Entwurf öffnen')
    ready(ui('#help-action'))
    for label in ('Vorschlag beibehalten','Vorschlag ändern'):
        ready(button(label))
    shot('Auffanghilfe')
    ui('#pause-nav').click()
    ui('#pause .return').click()
    assert history.text_content() == after_reply
    ui('#home-nav').click()
    ui('[data-person=Tom]').click()
    expect(panel).to_be_hidden()
    ui('#home-nav').click()
    ui('[data-person=Laura]').click()
    assert history.text_content() == after_reply
    expect(panel.locator('.hint')).to_have_count(5)
    ui('#help-action').click()
    expect(panel).to_be_hidden()
    expect(ui('#method-K')).to_have_attribute('aria-pressed','true')
    assert history.text_content() == after_reply
    # Revision still allows a different draft and another visit to all levels of help.
    expect(ui('#additional,#combine')).to_have_count(0)
    ui('#method-H').click()
    expect(ui('#additional,#combine')).to_have_count(0)
    open_to(5)
    ui('#help-action').click()
    expect(ui('#additional,#combine')).to_have_count(0)
    expect(ui('#draft-preview p')).to_have_text('Wir schlagen dir ein Kondom vor.')
    # Even a leftover draft value from a later stage must not enter the chat.
    page.evaluate("""() => {
        current.additional='H';
        try { sendChoice(); } finally { current.additional=''; }
    }""")
    assert history.text_content() == after_reply
    ui('#send').click()
    expect(button('Vorschlag zurückziehen')).to_be_visible()
    button('Vorschlag beibehalten').click()
    expect(ui('#step')).to_have_text('Schritt 2 von 7')
    expect(panel).to_be_hidden()
    ui('#method-K').click()
    menu=ui('#additional')
    assert set(menu.locator('option').evaluate_all('options=>options.map(o=>o.value)'))=={'','P','Cu','H'}
    menu.select_option('P')
    menu.select_option('H')
    pair=ui('#draft-preview p').inner_text()
    expect(menu).to_have_value('H')
    ui('#method-H').click()
    expect(ui('#combine')).not_to_be_checked()
    ui('#combine').check()
    expect(ui('#draft-preview p')).to_have_text(pair)
    ui('#send').click()
    expect(history.locator('.team p').last).to_have_text(pair)
    page.close()
    return dict(niveau=level,frame=size,vor_auswahl=True,methodenwechsel=True,nach_rueckmeldung=True,
                kartenstelle=True,unterbrechung=True,kombination_ab_l1=True,satzanfang=scaffold,
                laura_age=19,hilfe_ohne_scroll=True,stufen=5,entwurf_ohne_senden=True)


def phone_entry(browser):
    page=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    page.goto(LOCAL.as_uri())
    page.locator('[data-person=Laura]').tap()
    page.locator('#chat-help').tap()
    expect(page.locator('#hint-current')).to_contain_text('Kondom')
    expect(page.locator('.method[aria-pressed=true]')).to_have_count(0)
    page.get_by_role('button',name='Hilfe schließen').tap()
    expect(page.locator('#help')).to_be_in_viewport(ratio=.99)
    page.close()


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
    for name in ('Du kommst nicht weiter? – Hilfe anzeigen','Zweite Hilfe','Satzanfang zeigen','Quelle öffnen'):
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
            phone_entry(browser)
            runs=[]
            for level in ('Foerder','ESA','MSA','AHR'):
                for size in ((820,650),(1024,600),(820,1180),(1180,820)):
                    photos=(engine,level,size)==('chromium','Foerder',(820,650))
                    runs.append(help_path(browser,level,size,photos))
            assert len({r['satzanfang'] for r in runs})==4
            results.append(dict(engine=engine,version=browser.version,wege=runs))
            browser.close()
    save('lernhilfen',dict(runs=results,lernerprobung=False,
         modulunabhaengig_geprueft=True, screenshots={name:hashlib.sha256((QA/name).read_bytes()).hexdigest() for name in
             ('Auffanghilfe.jpg','Hilfe-vor-Auswahl.jpg','Hilfe-nach-Rueckmeldung.jpg')}))
    print('32 Hilfewege über alle vier Niveaus in Chromium und WebKit bestanden.')
