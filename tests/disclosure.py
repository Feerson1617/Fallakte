"""Check that only the current case information is revealed during independent work."""
from playwright.sync_api import expect


def check_navigation(view):
    expect(view.locator('nav button')).to_have_text(['Fallakten', 'Infokarten'])
    expect(view.locator('#pause,#pause-nav,#stop-task,#review-laura')).to_have_count(0)
    assert view.locator('main > section').evaluate_all('nodes => nodes.map(n => n.id)') == ['home','room','resources']


def first_message_only(browser, local, screenshot=None):
    page = browser.new_page(viewport={'width':820, 'height':650}, has_touch=True)
    page.goto(local.as_uri())
    check_navigation(page)
    page.locator('[data-person=Laura]').click()
    history = page.locator('#history')
    initial = history.inner_text()
    expect(history.locator('.chat-step')).to_have_text(['Infektionsschutz'])
    for word in ('Schwangerschaft','Freundin','Regelschmerzen','Einsetzen'):
        assert word not in initial
    if screenshot:
        page.screenshot(path=screenshot, type='jpeg', quality=78)
    page.locator('#cards-nav').click()
    page.locator('#card-K summary').click()
    page.locator('#resources .return').click()
    page.locator('#home-nav').click()
    page.locator('[data-person=Laura]').click()
    assert history.inner_text() == initial
    expect(page.locator('#send')).to_have_count(0)
    expect(page.locator('#step')).to_have_text('Schritt 1 von 5')
    page.close()
    return dict(stage=1, navigation=['Fallakten','Infokarten'], later_facts_visible=False)
