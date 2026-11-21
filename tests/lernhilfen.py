"""Use visible controls to seek help, revise and resume without committing a choice."""
import hashlib
import os
import re

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
    ui('#cards-nav').click()
    ui('#resources .return').click()
    assert history.text_content() == after_reply
    ui('#home-nav').click()
    expect(ui('[data-person=Tom]')).to_be_disabled()
    expect(ui('[data-person=Celina]')).to_be_disabled()
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
    expect(ui('#step')).to_have_text('Schritt 2 von 5')
    expect(panel).to_be_hidden()
    expect(ui('#work .preview')).to_contain_text('Kondom')
    ui('#change-prior').click()
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


def five_phase_actions(browser, level):
    """Open and execute the fifth help at each core decision without sending a reply."""
    page=browser.new_page(viewport={'width':820,'height':650},has_touch=True)
    page.goto(LOCAL.as_uri())
    ui=page.locator
    ui('#level-'+level).click()
    ui('[data-person=Laura]').click()
    results=[]
    for number,method in enumerate(('P','K','P','Cu','H'),1):
        expect(ui('#step')).to_have_text(f'Schritt {number} von 5')
        if number in (2,3,4):
            ui('#change-prior').click()
        ui('#method-'+method).click()
        if number in (3,4):
            ui('#combine').check()
        history=ui('#history').text_content()
        for depth in range(1,6):
            ui('#help').click()
            expect(ui('#card-cue')).to_be_in_viewport(ratio=.99)
            expect(ui('.hint')).to_have_count(depth)
            if depth==1:
                expect(ui('#hint-current')).to_contain_text('Abschnitt „')
            if depth==2:
                fact=ui('#hint-current p').inner_text()
                if number==3:
                    assert 'nicht sicher' in fact and 'lehnt die Pille ab' in fact
                if number==4:
                    assert 'schmerzen' in fact.lower() and 'Infektion' in fact
            if depth==4:
                expect(ui('#hint-current')).to_contain_text('Eine mögliche Begründung')
        ui('#help-action').click()
        expect(ui('#method-K')).to_have_attribute('aria-pressed','true')
        expect(ui('#send')).to_be_enabled()
        assert ui('#history').text_content()==history
        ui('#send').click()
        ui('#work .row button').first.click()
        results.append(dict(abschnitt=number,fachhinweis=fact,entwurf_ohne_senden=True))
    expect(ui('#task-title')).to_have_text('Gespräch abgeschlossen')
    page.close()
    return dict(niveau=level,abschnitte=results)


def carried_advice(browser, level, photos):
    page=browser.new_page(viewport={'width':820,'height':650},has_touch=True)
    ui=page.locator
    button=lambda text: page.get_by_role('button',name=text,exact=True)
    keep=button('Vorschlag beibehalten')
    change=button('Vorschlag ändern')
    def start():
        page.goto(LOCAL.as_uri())
        ui('#level-'+level).click()
        expect(ui('[data-person=Celina]')).to_be_disabled()
        expect(ui('[data-person=Tom]')).to_be_disabled()
        ui('[data-person=Laura]').click()
    def send(method):
        ui('#method-'+method).click()
        ui('#send').click()

    start()
    send('P')
    keep.click()
    history=ui('#history')
    for stage in ('L1','L3'):
        latest=history.locator('.person').last
        expect(latest).to_be_in_viewport()
        expect(latest).to_contain_text('Pille' if stage=='L3' else re.compile('schwanger', re.I))
        expect(ui('#work .preview')).to_contain_text('Kombinationspille')
        expect(ui('#work .response')).to_contain_text('möchte ich nicht' if stage=='L3' else 'regelmäßig')
        expect(ui('#send')).to_have_count(0)
        if stage=='L3' and photos:
            page.screenshot(path=QA/'Laura-Rat-pruefen.jpg',type='jpeg',quality=78)
        ui('#help').click()
        section = 'Anwendung' if stage=='L1' else 'Mögliche Nachteile'
        expect(ui('#hint-current p')).to_contain_text(f'Karte „Kombinationspille“, Abschnitt „{section}“')
        if stage=='L1':
            expect(ui('#hint-current p')).to_contain_text('Wie oft')
            keep.click()
    expect(ui('#hint-current p')).to_contain_text('Lauras Nein')
    before=history.inner_text()
    button('Karte „Kombinationspille“ lesen').click()
    ui('#resources .return').click()
    for depth in range(2,6):
        ui('#help').click()
        expect(ui('.hint')).to_have_count(depth)
    ui('#help-action').click()
    expect(ui('#method-K')).to_have_attribute('aria-pressed','true')
    assert history.inner_text()==before
    ui('#send').click()
    for _ in range(2): keep.click()  # L3 reply, then L4 review
    expect(ui('#task-title')).to_have_text('Euer vorläufiger Rat')
    expect(ui('#work')).not_to_contain_text('Laufzettel')
    expect(ui('#work')).to_contain_text('Nachteil')
    if photos:
        page.screenshot(path=QA/'Laura-Muendlicher-Rat.jpg',type='jpeg',quality=78)
    send('K')
    keep.click()
    expect(ui('#task-title')).to_have_text('Gespräch abgeschlossen')
    ui('#home-nav').click()
    expect(ui('[data-person=Celina]')).to_be_enabled()
    expect(ui('[data-person=Tom]')).to_be_enabled()
    ui('#level-AHR').click()
    expect(ui('[data-person=Tom]')).to_be_disabled()

    # Withdrawing leaves no advice to carry, even after the two new goals are introduced.
    start()
    for _ in ('L0','L1'):
        expect(ui('#change-prior')).to_have_count(0)
        send('P')
        change.click()
        send('P')
        button('Vorschlag zurückziehen').click()
    expect(ui('#change-prior')).to_have_count(0)
    expect(ui('.method')).to_have_count(4)
    expect(ui('.method[aria-pressed=true]')).to_have_count(0)
    send('H')
    expect(ui('#work .response')).to_be_visible()
    page.close()
    return dict(niveau=level,ohne_vorwahl=['L1','L3'],uebernommen=['L1','L3'],entwurf_ohne_senden=True)


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
            reviews=[carried_advice(browser,level,(engine,level)==('chromium','Foerder')) for level in ('Foerder','ESA')]
            results.append(dict(engine=engine,version=browser.version,wege=runs,weiterfuehrung=reviews,
                                fuenf_abschnitte=[five_phase_actions(browser,level) for level in ('Foerder','ESA','MSA','AHR')]))
            browser.close()
    save('lernhilfen',dict(runs=results,lernerprobung=False,
         modulunabhaengig_geprueft=True, screenshots={name:hashlib.sha256((QA/name).read_bytes()).hexdigest() for name in
             ('Auffanghilfe.jpg','Hilfe-vor-Auswahl.jpg','Hilfe-nach-Rueckmeldung.jpg','Laura-Rat-pruefen.jpg','Laura-Muendlicher-Rat.jpg')}))
    print('32 Hilfewege über alle vier Niveaus in Chromium und WebKit bestanden.')
