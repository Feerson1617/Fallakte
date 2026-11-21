"""Keep the reader's place in Tom's long article across real navigation."""
from playwright.sync_api import expect


def article_return(browser, standalone):
    page = browser.new_page(viewport={'width': 820, 'height': 650}, has_touch=True)
    page.goto(standalone.as_uri())
    ui = page.locator
    ui('#level-AHR').click()
    ui('[data-person=Tom]').click()
    ui('#method-K').click()
    ui('#send').click()
    page.get_by_role('button', name='Vorschlag beibehalten').click()
    history = ui('#history')
    glossary = ui('.article details')
    glossary.locator('summary').click()
    history.evaluate('h => h.scrollTop = h.scrollHeight')
    position = history.evaluate('h => h.scrollTop')
    messages = history.text_content()
    assert position > 0
    for via in ('Sicherung', 'Infokarten', 'Fallwechsel'):
        if via == 'Fallwechsel':
            ui('#home-nav').click()
            ui('[data-person=Celina]').click()
            ui('#home-nav').click()
            ui('[data-person=Tom]').click()
        else:
            if via == 'Infokarten':
                ui('#cards-nav').click()
            ui('#pause-nav').click()
            ui('#pause .return').click()
        expect(glossary).to_have_attribute('open', '')
        assert abs(history.evaluate('h => h.scrollTop') - position) <= 1, via
        assert history.text_content() == messages, via
        assert page.evaluate('scrollY') == 0
    history.evaluate('h => h.scrollTop = 0')
    ui('#latest').click()
    expect(ui('.article h3')).to_be_in_viewport()
    expect(ui('#latest')).to_be_hidden()
    glossary.locator('summary').click()
    ui('#cards-nav').click()
    ui('#resources .return').click()
    assert not glossary.evaluate('e => e.open')
    page.close()
    return dict(case='Tom', level='AHR', restored_via=['Sicherung', 'Infokarten → Sicherung', 'Fallwechsel'],
                glossary_state_preserved=True, scroll_position=position, jump_to_article=True)
