"""Mixed decisions through the delivered HTML. Checks use the learners' visible controls."""
from playwright.sync_api import expect

LEVELS=('Foerder','ESA','MSA','AHR')
METHOD_NAMES={'K':'Kondom','P':'Kombinationspille','Cu':'Kupferspirale','H':'Hormonspirale'}
ROUTES=(
    ('K','K+H','K','H','K'),
    ('K','Cu','K+Cu','Cu','K+Cu'),
    ('P','H','K+H','K+H','P'),
)


def idle_without_action(page, expected_step):
    work = page.locator('#work')
    history = page.locator('#history')
    step = page.locator('#step')
    expect(step).to_have_text(f'Laura {expected_step} von 5')
    before = (work.inner_text(), history.inner_text(), page.locator('#send').count())
    page.clock.fast_forward(25 * 60 * 1000)
    expect(work).to_be_visible()
    expect(step).to_have_text(f'Laura {expected_step} von 5')
    expect(page.locator('[role=alert],dialog[open]')).to_have_count(0)
    assert before == (work.inner_text(), history.inner_text(), page.locator('#send').count())


def mixed_paths(browser,local):
    records=[]
    for tier in LEVELS:
        for route_index,route in enumerate(ROUTES):
            page=browser.new_page(viewport={'width':820,'height':650},has_touch=True)
            if route_index==1:
                page.clock.install()
            page.goto(local.as_uri())
            button=lambda name: page.get_by_role('button',name=name,exact=True)
            ui=page.locator
            page.locator('#level-'+tier).click()

            ui('[data-person=Laura]').click()
            for n,choice in enumerate(route):
                if route_index==1:
                    idle_without_action(page,n+1)
                if n in (1,2,3):
                    expect(ui('#change-prior')).to_be_visible()
                    if route[n-1]==choice:
                        button('Vorschlag beibehalten').click()
                        expect(ui('#history .team').last).to_contain_text('Wir bleiben')
                        continue
                    ui('#change-prior').click()
                method=choice.split('+')[-1]
                if n==1:
                    ui('#help').click()
                    ui('#help').click()
                    expect(ui('.hint')).to_have_count(2)
                    ui('#method-K').click()
                    ui('#additional').select_option('P')
                ui('#method-'+method).click()
                if '+' in choice:
                    ui('#combine').check()
                if n==2 and route_index==1:
                    idle_without_action(page,n+1)
                    history=ui('#history').text_content()
                    draft=ui('#draft-preview p').inner_text()
                    ui('#cards-nav').click()
                    ui('#resources .return').click()
                    expect(ui('#draft-preview p')).to_have_text(draft)
                    # A different level starts separately. This draft is still here on return.
                    ui('#home-nav').click()
                    expect(ui('[data-person=Tom]')).to_be_enabled()
                    other=LEVELS[(LEVELS.index(tier)+1)%len(LEVELS)]
                    ui('#level-'+other).click()
                    ui('[data-person=Laura]').click()
                    expect(ui('#step')).to_have_text('Laura 1 von 5')
                    ui('#home-nav').click()
                    ui('#level-'+tier).click()
                    ui('[data-person=Laura]').click()
                    expect(ui('#draft-preview p')).to_have_text(draft)
                    assert ui('#history').text_content()==history
                    expect(ui('#combine')).to_be_checked()
                if n==4:
                    ui('#tentative').check()
                    expect(ui('#draft-preview p')).to_contain_text('Praxis')
                draft=ui('#draft-preview p').inner_text()
                displayed={code for code,name in METHOD_NAMES.items() if name in draft}
                assert displayed==set(choice.split('+')), (tier,n,choice,draft)
                ui('#send').click()
                expect(ui('#history .team').last.locator('p')).to_have_text(draft)
                before=ui('#history .chat-step').count()
                if n==0 and route_index==2:
                    # Unsuitable for the first goal. Ask Laura before revising the proposal.
                    ui('#ask').click()
                    ui('.question').first.click()
                    expect(ui('#work .preview')).to_contain_text('Krankheiten')
                    button('Vorschlag ändern').click()
                    ui('#method-K').click()
                    ui('#send').click()
                    assert ui('#history .chat-step').count()==before
                if n==4 and route_index==2:
                    expect(ui('.response')).to_contain_text('nicht')
                    button('Vorschlag ändern').click()
                    ui('#method-P').click()
                    ui('#combine').check()
                    ui('#tentative').check()
                    ui('#send').click()
                    expect(ui('.response')).to_contain_text('nicht')
                    button('Vorschlag zurückziehen').click()
                    expect(ui('#work')).to_contain_text('zurückgezogen')
                else:
                    button('Vorschlag beibehalten').click()
            expect(ui('#task-title')).to_have_text('Gespräch abgeschlossen')
            if route_index!=2:
                expect(ui('#work')).to_contain_text('Rat ist vorläufig')
            assert ui('#history .chat-step').count()==5
            # Celina can consider a copper IUD while withholding consent about insertion.
            if route_index==1:
                button('Zur Fallübersicht').click()
                ui('[data-person=Celina]').click()
                for ix,code in enumerate(('H','K','Cu','K','K+Cu')):
                    ui('#method-'+code.split('+')[-1]).click()
                    if '+' in code:
                        ui('#combine').check()
                    if ix==4:
                        ui('#tentative').check()
                    ui('#send').click()
                    if ix==0: expect(ui('.response')).to_contain_text('nicht')
                    if ix==2: expect(ui('.response')).to_contain_text('Beratung')
                    if ix==4: expect(ui('.response')).to_contain_text('zustimme')
                    button('Vorschlag beibehalten').click()
                expect(ui('#work')).to_contain_text('Celina entscheidet nach der Beratung selbst')
            records.append(dict(level=tier,choices=list(route),revision=route_index==2,
                                celina=route_index==1,unterbrochen=['L0','L1','L3','L4','L6'] if route_index==1 else [],
                                final='zurückgezogen' if route_index==2 else 'vorläufig'))
            page.close()
    return records
