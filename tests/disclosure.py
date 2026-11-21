"""Attempt to reveal later case information through the learner interface."""
from playwright.sync_api import expect


def first_message_only(browser, local, screenshot=None):
    page = browser.new_page(viewport={'width':820,'height':650},has_touch=True)
    page.goto(local.as_uri())
    page.get_by_role('button', name='Sicherung', exact=True).click()
    expect(page.locator('#pause li')).to_have_count(0)
    page.get_by_role('button', name='Zurück', exact=True).click()
    page.locator('[data-person=Laura]').click()
    history = page.locator('#history').inner_text()
    for entry in ('pause-nav','cards-nav'):
        page.locator('#'+entry).click()
        if entry=='cards-nav':
            page.locator('#pause-nav').click()
        # Try every disclosure action offered on the shared review page (including the old stop).
        actions = page.locator('#pause summary, #pause button:not(#review-laura):not(.return)')
        for control in actions.all():
            if control.is_visible():
                control.click()
        facts = page.locator('#pause li').all_inner_texts()
        assert facts==['Laura will sich vor Krankheiten schützen, die beim Sex übertragen werden.'], facts
        rendered=page.locator('#pause').inner_text().lower()
        for later in ('schwangerschaft','freundin','pille','spirale','schmerzen','kondom'):
            assert later not in rendered, (later,rendered)
        if screenshot and entry=='pause-nav':
            page.locator('.pause-note').screenshot(path=screenshot,type='jpeg',quality=82)
        page.get_by_role('button', name='Zurück', exact=True).click()
        assert page.locator('#history').inner_text()==history
        expect(page.locator('#step')).to_have_text('Schritt 1 von 7')
    page.close()
    return dict(stage=1,known_facts=1,attempts=['Sicherung','Infokarten → Sicherung'],later_facts_visible=False)
