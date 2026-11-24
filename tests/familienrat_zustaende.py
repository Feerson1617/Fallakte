"""Reach alternate states through the public HTML controls, independently of the JS state."""
import itertools
import json
import os
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright, expect
from familienrat_qa import APP, BANK, LEVELS, QA, ROOT, set_team, start, sha

OUT = ROOT/'build/Familienrat-Zustaende'


def check(engine):
    evidence = []
    with sync_playwright() as pw:
        browser = getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE'))
        page = browser.new_page(viewport={'width':1024,'height':768},has_touch=True)
        page.set_default_timeout(4500)
        shell, f = start(page,APP.as_uri())
        def click(id): f.locator('#'+id).click()
        def outer(action): shell.locator(f'[data-action={action}]').click()
        def entry(name,step,member=None):
            outer('recovery')
            f.locator('#person').select_option(name)
            f.locator('#entry').select_option(str(step))
            if member is not None:f.locator('#member').select_option(str(member))
            click('open-entry')
        def new(team):
            outer('home')
            f.locator('#level-1').select_option('')
            set_team(f,team)
            click('start')
            if f.locator('#confirm-start').is_visible():click('confirm-start')
        def help5():
            click('help');click('hint-last');click('dismiss')
        def free(id,words):
            field=f.locator('textarea')
            for value in [' ','x','.', 'xxx','test','123','xyz']:
                field.fill(value);expect(f.locator('#'+id)).to_be_disabled()
            for value in ['OP','gesunt',words]:
                field.fill(value);expect(f.locator('#'+id)).to_be_enabled()
            click(id)
        def compare(member,weight,concerns,edit=False):
            expect(f.locator('section h2')).to_contain_text('Person '+str(member+1))
            click('weight-'+str(weight))
            for part,concern in enumerate(concerns):
                source=part if weight==2 else weight
                click('concern-'+str(concern))
                for wrong in [2,1-concern,3]:
                    click('fact-'+str(wrong));expect(f.locator('section .retry')).to_be_visible()
                    expect(f.locator('#answer-0')).to_have_count(0)
                click('fact-'+str(concern))
                if source!=concern:
                    click('other')
                    free('check-reason','Spätere Kinder können auch eine Sorge um die Gesundheit sein.' if concern else 'Beschwerden könnten Lauras Ausbildungsalltag betreffen.')
                    if edit:
                        click('edit-reason');free('check-reason','Meine Gewichtung hängt von Lauras eigenen Fragen ab.')
                click('answer-1');expect(f.locator('#next')).to_have_count(0)
                click('answer-0');click('next')
        # The two ordered members have distinct assessments even if both use one level.
        for i,team in enumerate(itertools.product(LEVELS,repeat=2)):
            new(team);click('next');click('help')
            if team[0]!=team[1]:
                for tier in team:
                    f.locator('#help-tier').select_option(tier)
                    expect(f.locator('#dialog-body')).to_contain_text(BANK['cases']['Mutter']['tasks'][0]['helpByLevel'][tier][0])
            else:expect(f.locator('#help-tier')).to_have_count(0)
            click('dismiss')
            outer('home');click('start');click('dismiss');click('resume')
            expect(f.locator('h1')).to_have_attribute('data-section','MU-02')
            entry('Lauras Frage',3)
            expect(f.locator('[data-terminal]')).to_have_count(0)
            click('paper-ready');expect(f.locator('[data-terminal]')).to_be_visible()
            expect(f.locator('#open-Vater')).to_have_count(0)
            entry('Lauras Frage',2,1)
            # Eight possible weight / question patterns, repeated in reversed roles.
            patterns=[(0,[0]),(0,[1]),(1,[0]),(1,[1]),(2,[0,0]),(2,[0,1]),(2,[1,0]),(2,[1,1])]
            p2=patterns[i%8];p1=patterns[(i+3)%8]
            compare(1,*p2,edit=True)
            expect(f.locator('section h2')).to_contain_text('Person 1')
            if i%4==0:
                click('weight-0');click('concern-1');click('fact-1');click('other')
                free('check-reason','Die Zukunft kann Laura auch gesundheitlich beschäftigen.')
                click('answer-0');click('edit-weight')
                expect(f.locator('#answer-0')).to_have_count(0)
            compare(0,*p1,edit=True)
            expect(f.locator('#open-Vater')).to_be_visible()
            expect(f.locator('section')).to_contain_text(BANK['ui']['reasonOpen'])
            # Changing one member's completed judgement must revoke group completion.
            entry('Lauras Frage',2,1);click('edit-weight')
            entry('Lauras Frage',3);expect(f.locator('#open-Vater')).to_have_count(0)
            expect(f.locator('section')).to_contain_text(BANK['ui']['noPast'])
            evidence.append(dict(team=team,person1=p1,person2=p2,wege='Rückkehr, Hilfe, neue Gewichtung, individuelle Grenze und Freitext'))
        # Direct entry, cancellation and a genuinely fresh team.
        new(['ESA']);click('next');click('answer-0');help5()
        outer('home');click('resume');expect(f.locator('.tag')).to_have_text(BANK['ui']['own'])
        entry('Mutter',6);expect(f.locator('[data-application]')).to_have_count(0)
        new(['ESA']);click('next');expect(f.locator('#answer-0')).to_be_enabled()
        for person,c in BANK['cases'].items():
            for at,location in enumerate(c['recovery']):
                entry(person,at);expect(f.locator('h1')).to_have_attribute('data-section',location['id'])
                if at==len(c['recovery'])-1:expect(f.locator('section')).to_contain_text(BANK['ui']['noPast'])
                evidence.append(dict(einstieg=location['id'],person=person))
            # A non-addition solution cannot trigger a transfer; one viewed after
            # successful completion of the addition cannot create one either.
            entry(person,1);help5()
            entry(person,len(c['tasks'])+1);expect(f.locator('[data-application]')).to_have_count(0)
            entry(person,len(c['tasks']));click('answer-0');help5();click('next')
            expect(f.locator('[data-application]')).to_have_count(0)
            entry(person,'transfer');click('answer-2')
            expect(f.locator('#answer-0')).to_be_enabled();outer('home');click('resume')
            expect(f.locator('#response')).to_be_visible();click('jump')
            if person in ('Mutter','Freundin'):
                f.locator('aside > details > summary').click()
                expect(f.locator('aside')).to_contain_text(BANK['ui']['skipped'])
            entry(person,'transfer');click('answer-1');click('answer-0')
            expect(f.locator('section')).to_contain_text(BANK['ui']['assisted'])
            evidence.append(dict(anwendung=person,ausloesung='Getrennte Denkhandlungen, späte Hilfe, unterbrochen, zwei Fehlversuche, korrigiert'))
        for at,location in enumerate(BANK['evaluationRecovery']):
            entry('Lauras Frage',at)
            expect(f.locator('h1')).to_have_attribute('data-section',location['id'])
            evidence.append(dict(einstieg=location['id'],person='Laura'))
        page.reload();page.locator('#zweiter-tag').click()
        f=page.frame_locator('iframe[title^=Dienstag]')
        expect(f.locator('#start')).to_have_count(0)
        f.locator('#level-1').select_option('AHR');expect(f.locator('#start')).to_have_count(0)
        set_team(f,['ESA']);expect(f.locator('#resume')).to_have_count(0)
        assert page.evaluate('[localStorage.length,sessionStorage.length]')==[0,0]
        version=browser.version;browser.close()
    return dict(browser=engine,version=version,pruefungen=evidence)


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        result=list(pool.map(check,['chromium','webkit']))
    (OUT/'Zustaende.json').write_text(json.dumps(dict(commit=BANK['commit'],html_sha256=sha(APP.read_bytes()),browser=result),ensure_ascii=False,indent=2))
