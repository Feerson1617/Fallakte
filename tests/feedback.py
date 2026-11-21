"""Independent classroom scenarios. Expected decisions do not come from the dialog data."""
from playwright.sync_api import expect


def run_scenarios(browser, local, screenshots=None):
    page = browser.new_page()
    button = lambda text: page.get_by_role('button', name=text, exact=True)
    history = page.locator('#history')
    articles = history.locator('.article')

    def start(person):
        page.goto(local.as_uri())
        page.locator('[data-person=' + person + ']').click()

    def suggest(method, combine=False):
        page.locator('#method-' + method).click()
        if combine:
            page.locator('#combine').check()
        button('Nachricht senden').click()

    def keep():
        expect(button('Nächste Nachricht')).to_have_count(0)
        button('Vorschlag beibehalten').click()

    # A fixed boundary remains explicit after repeating the declined method in a combination.
    start('Laura')
    suggest('P')
    keep()
    suggest('H')
    keep()
    button('Weiter nach dem Gespräch').click()
    suggest('P')
    if screenshots:
        page.screenshot(path=screenshots/'Laura-Entscheidung.jpg',type='jpeg',quality=78)
    button('Vorschlag ändern').click()
    suggest('P', combine=True)
    expect(page.locator('.response')).to_contain_text('nicht')
    expect(button('Vorschlag ändern')).to_have_count(0)
    keep()
    expect(history).to_contain_text('Mein Nein gilt auch bei einer Kombination.')
    expect(history.locator('.chat-step').last).to_have_text('Regelschmerzen')
    suggest('H', combine=True)
    expect(page.locator('.response')).to_contain_text('ärztliche Beratung')
    keep()
    suggest('K')
    keep()
    suggest('H', combine=True)
    keep()
    expect(page.locator('#task-title')).to_have_text('Gespräch abgeschlossen')
    expect(page.locator('.paper-note')).to_contain_text('Mein letzter Rat')

    button('Zur gemeinsamen Sicherung').click()
    expect(page.locator('#pause-facts')).to_be_hidden()

    # A retained final pill proposal remains disputed through the class review and a return.
    start('Laura')
    for method in ('K', 'H'):
        suggest(method)
        keep()
    button('Weiter nach dem Gespräch').click()
    for method in ('H', 'K', 'K'):
        suggest(method)
        keep()
    suggest('P')
    button('Vorschlag ändern').click()
    suggest('P', combine=True)
    keep()
    expect(page.locator('#task-title')).to_have_text('Die Empfehlung bleibt offen')
    expect(page.locator('.unresolved')).to_contain_text('nicht zugestimmt')
    refusal=page.locator('#work .response').inner_text()
    expect(history.locator('.person p').last).to_have_text(refusal)
    button('Zur gemeinsamen Sicherung').click()
    expect(page.locator('#pause-facts')).to_be_hidden()
    expect(page.locator('#pause-conflict')).to_be_visible()
    expect(page.locator('#pause-conflict')).to_contain_text(refusal)
    button('Lauras Chat nachlesen').click()
    expect(page.locator('.unresolved')).to_be_visible()
    expect(page.locator('#work .response')).to_have_text(refusal)

    # A different level starts with its own unread facts, even after another team finished.
    page.locator('#home-nav').click()
    page.locator('#level-Foerder').click()
    button('Sicherung').click()
    facts = page.locator('#pause-facts')
    summary = facts.locator('summary')
    expect(page.locator('#review-laura')).to_be_hidden()
    expect(facts.locator('ul')).to_be_hidden()
    summary.click()
    expect(facts.locator('li')).to_have_count(7)
    expect(facts).to_contain_text('vor Krankheiten schützen')
    expect(page.locator('#pause-conflict')).to_be_hidden()
    page.locator('#pause .return').click()
    page.locator('[data-person=Laura]').click()
    suggest('K')
    keep()
    suggest('H')
    keep()
    button('Weiter nach dem Gespräch').click()
    page.locator('#method-P').click()
    page.locator('#combine').check()
    page.locator('#help').click()
    page.locator('#help').click()
    before = history.text_content()
    draft = page.locator('#draft-preview p').inner_text()
    hints = page.locator('.hint').all_text_contents()
    step = page.locator('#step').inner_text()
    button('Sicherung').click()
    expect(facts.locator('ul')).to_be_hidden()
    summary.focus()
    summary.press('Enter')
    expect(facts.locator('li')).to_have_count(4)
    expect(facts.locator('li').first).to_contain_text('will keine Pille')
    expect(facts).to_contain_text('Andere Mittel mit Hormonen')
    expect(facts).to_contain_text('Einsetzen')
    expect(facts).to_contain_text('Regel')
    expect(facts).to_contain_text('Kondom')
    expect(facts).to_contain_text('selbst entscheiden')
    expect(facts).not_to_contain_text('Freundin')
    if screenshots:
        page.locator('.pause-note').screenshot(path=screenshots/'Frueher-Stopp.jpg',type='jpeg',quality=82)
    page.locator('#pause .return').click()
    assert history.text_content()==before and page.locator('#step').inner_text()==step
    expect(page.locator('#draft-preview p')).to_have_text(draft)
    assert page.locator('.hint').all_text_contents()==hints
    expect(page.locator('#combine')).to_be_checked()
    expect(page.locator('#method-P')).to_have_attribute('aria-pressed','true')
    button('Nachricht senden').click()
    expect(page.locator('.response')).to_contain_text('nicht')
    expect(button('Vorschlag ändern')).to_be_visible()

    # Celina refuses hormones, yet can consider a copper IUD after counselling.
    start('Celina')
    suggest('H')
    button('Vorschlag ändern').click()
    suggest('H', combine=True)
    keep()
    expect(history).to_contain_text('möchte ich auch die Hormonspirale nicht')
    suggest('K')
    keep()
    suggest('Cu')
    expect(page.locator('.response')).to_contain_text('noch nicht ausgeschlossen')
    button('Vorschlag ändern').click()
    suggest('Cu', combine=True)
    button('Vorschlag zurückziehen').click()
    expect(history).to_contain_text('Wir ziehen unseren Vorschlag zurück.')
    expect(history.locator('.chat-step').last).to_have_text('Schutz in der Beziehung')

    # Twice unsuitable, including a return from another case. No early article.
    start('Tom')
    suggest('P')
    expect(page.locator('.response')).to_contain_text('Eisprung')
    button('Vorschlag ändern').click()
    suggest('Cu')
    expect(page.locator('.response')).to_contain_text('Gebärmutter')
    keep()
    expect(articles).to_have_count(0)
    if screenshots:
        page.screenshot(path=screenshots/'Tom-Eigener-Beitrag.jpg',type='jpeg',quality=78)
    snapshot = history.inner_text()
    page.locator('#home-nav').click()
    page.locator('[data-person=Celina]').click()
    page.locator('#home-nav').click()
    page.locator('[data-person=Tom]').click()
    assert history.inner_text() == snapshot
    expect(articles).to_have_count(0)
    expect(page.locator('#work .preview')).to_have_text('Für dich selbst schlagen wir ein Kondom vor.')
    button('Nachricht senden').click()
    expect(articles).to_have_count(1)
    expect(history.locator('.team').last).to_contain_text('Kondom')
    proposal = history.text_content().index('Für dich selbst schlagen wir ein Kondom vor.')
    assert proposal < history.text_content().index('noch mehr Möglichkeiten') < history.text_content().index('Geteilter Artikel')

    # A direct revision to a self-applicable option needs no guided fallback.
    start('Tom')
    suggest('H')
    button('Vorschlag ändern').click()
    suggest('K')
    expect(articles).to_have_count(0)
    keep()
    expect(articles).to_have_count(1)
    expect(history).not_to_contain_text('Für dich selbst schlagen wir ein Kondom vor.')
    page.close()
    return ['Laura: wiederholtes Nein, Sorge, Kombination bis zum Abschluss',
            'Laura: letzter Kombinationsvorschlag bleibt in Abschluss, Sicherung und Wiederaufnahme strittig',
            'Sicherung bei frühem Stopp: offene Stufen, Niveauwechsel, Entwurf und Hilfen erhalten',
            'Celina: Hormongrenze, offene Einlage und Rücknahme',
            'Tom: zweimal ungeeignet, Unterbrechung, dann eigener Kondomvorschlag',
            'Tom: Revision direkt zum Kondom']
