"""Mixed decisions through the delivered HTML. Checks use the learners' visible controls."""
from playwright.sync_api import expect

LEVELS=('Foerder','ESA','MSA','AHR')
# Six recommendations per Laura interview; the friend's experience is a paper discussion.
METHOD_NAMES={'K':'Kondom','P':'Kombinationspille','Cu':'Kupferspirale','H':'Hormonspirale'}
ROUTES=(
    ('K','K+H','K','H','K+Cu','K'),
    ('K','Cu','K+Cu','Cu','K','K+Cu'),
    ('P','H','K+H','K+H','K','P'),
)


def mixed_paths(browser,local):
    records=[]
    for tier in LEVELS:
        for route_index,route in enumerate(ROUTES):
            page=browser.new_page(viewport={'width':820,'height':650},has_touch=True)
            page.goto(local.as_uri())
            button=lambda name: page.get_by_role('button',name=name,exact=True)
            ui=page.locator
            page.locator('#level-'+tier).click()

            def stop(known, open_list):
                ui('#pause-nav').click()
                expect(ui('#pause-facts li')).to_have_count(known)
                expect(ui('#class-stop')).to_have_count(0)
                if open_list:
                    ui('#pause-facts summary').click()
                    expect(ui('#pause-facts li').last).to_be_visible()
                    expect(ui('#stop-task')).to_contain_text({'Foerder':'Vergleiche','ESA':'Vergleiche','MSA':'Kriterium','AHR':'offene Frage'}[tier])
                ui('#pause .return').click()

            stop(0,False)
            ui('[data-person=Laura]').click()
            stop(1,route_index==0)
            for n,choice in enumerate(route):
                if n==2:
                    button('Weiter nach dem Gespräch').click()
                if n in (3,4):
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
                    history=ui('#history').text_content()
                    draft=ui('#draft-preview p').inner_text()
                    stop(4,True)
                    expect(ui('#draft-preview p')).to_have_text(draft)
                    # Visit another case, then a different level of Laura, before returning.
                    ui('#home-nav').click()
                    ui('[data-person=Tom]').click()
                    stop(4,True)
                    ui('#home-nav').click()
                    other=LEVELS[(LEVELS.index(tier)+1)%len(LEVELS)]
                    ui('#level-'+other).click()
                    stop(0,False)
                    ui('[data-person=Laura]').click()
                    expect(ui('#step')).to_have_text('Schritt 1 von 7')
                    stop(1,False)
                    ui('#home-nav').click()
                    ui('#level-'+tier).click()
                    ui('[data-person=Laura]').click()
                    expect(ui('#draft-preview p')).to_have_text(draft)
                    assert ui('#history').text_content()==history
                    expect(ui('#combine')).to_be_checked()
                if n==5:
                    stop(7,route_index==1)
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
                if n==5 and route_index==2:
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
            assert ui('#history .chat-step').count()==7
            stop(0,False)
            # Celina can consider a copper IUD while withholding consent about insertion.
            if route_index==1:
                button('Celina starten').click()
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
                                celina=route_index==1,final='zurückgezogen' if route_index==2 else 'vorläufig'))
            page.close()
    return records
