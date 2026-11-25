"""Reach alternate states through the public HTML controls, independently of the JS state."""
import itertools
import json
import os
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright, expect
from familienrat_qa import APP, BANK, LEVELS, QA, ROOT, set_team, start, sha

OUT = ROOT/'build/Familienrat-Zustaende'


def check_sources(page,engine):
    observations=[]
    ui=BANK['ui']
    def open_task(tier,entry):
        shell,f=start(page,APP.as_uri())
        set_team(f,[tier])
        if entry=='Wert':
            f.locator('#start').click();f.locator('#next').click()
        else:
            shell.locator('[data-action=recovery]').click()
            f.locator('#entry').select_option(entry);f.locator('#open-entry').click()
        return shell,f

    def observe(f,case,expected):
        tag=f.locator('section .tag').first
        expect(tag).to_have_text(ui[expected])
        observations.append(dict(weg=case,abschnitt=f.locator('h1').inner_text(),anzeige=tag.inner_text()))

    for wrong in (False,True):
        shell,f=open_task('AHR','Wert')
        f.get_by_text(ui['sourceInstead'],exact=True).click()
        if wrong:
            f.locator('#source-1').click()
            expect(f.locator('section')).to_contain_text(ui['sourceRetry'])
        f.locator('#source-0').click()
        expect(f.locator('section')).to_contain_text(ui['sourceYes'])
        expect(f.locator('#compare')).to_be_disabled()
        f.locator('textarea').fill('Der Mutter ist wichtig, wie es Laura körperlich geht.')
        f.locator('#compare').click();f.locator('#answer-0').click()
        expect(f.locator('section')).to_contain_text(ui['freeNote'])
        expected='corrected' if wrong else 'own'
        label='Originaltextstelle korrigiert' if wrong else 'Originaltextstelle selbstständig gewählt'
        observe(f,label,expected)
        if engine=='chromium' and not wrong:
            page.screenshot(path=OUT/'Quellenarbeit-Originalsatz.jpg',quality=65)
        # Reopen the task so that the tag is recomputed after the late solution.
        f.locator('#help').click();f.locator('#hint-last').click();f.locator('#dismiss').click()
        shell.locator('[data-action=home]').click();f.locator('#resume').click()
        observe(f,label+' · nachträgliche Hilfe 5',expected)

    for entry,hint,wrong,expected in [
        ('5',0,False,'own'),('5',1,False,'explain'),('5',5,False,'used'),
        ('transfer',0,False,'applied'),('transfer',0,True,'assisted'),
        ('transfer',1,False,'assisted'),('transfer',5,False,'appliedSolution'),
    ]:
        shell,f=open_task('ESA',entry)
        if entry=='transfer':
            shell.locator('[data-action=resources]').click()
            f.locator('#dialog-body > details').first.locator('summary').first.click()
        else:
            f.locator('#cards').click()
        expect(f.locator('#dialog-body details[open]').first).to_contain_text('Gebärmutter')
        f.locator('#dismiss').click()
        if wrong:f.locator('#answer-1').click()
        if hint:
            f.locator('#help').click()
            if hint==5:f.locator('#hint-last').click()
            f.locator('#dismiss').click()
        f.locator('#answer-0').click()
        task='Anwendung' if entry=='transfer' else 'Ergänzung'
        support=f'Hilfe {hint}' if hint else 'ohne gestufte Hilfe'
        attempt='nach Fehlversuch' if wrong else 'erster Versuch'
        observe(f,f'Fachkarte · {task} · {support} · {attempt}',expected)
        if entry=='5' and not hint:
            if engine=='chromium':page.screenshot(path=OUT/'Quellenarbeit-Fachkarte.jpg',quality=65)
            f.locator('#terms').click();f.locator('#dismiss').click()
            f.locator('#help').click();f.locator('#hint-last').click();f.locator('#dismiss').click()
            f.locator('#next').click()
            expect(f.locator('[data-application]')).to_have_count(0)
            observe(f,'Fachkarte · nachträgliches Glossar und Hilfe 5','own')
    return observations


def check(engine):
    evidence = []
    with sync_playwright() as pw:
        browser = getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE'))
        page = browser.new_page(viewport={'width':1024,'height':768},has_touch=True)
        page.set_default_timeout(15000)
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
            expect(f.locator('#level-1')).to_have_count(0)
            set_team(f,team)
            if f.locator('#confirm-level').is_visible():click('confirm-level')
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
        def compare(tier,weight,concerns,edit=False):
            expect(f.locator('section h2')).to_contain_text(tier)
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
                click('answer-1');expect(f.locator('#next')).to_have_count(0)
                click('answer-0')
                if source!=concern and edit:
                    click('edit-reason');free('check-reason','Meine Gewichtung hängt von Lauras eigenen Fragen ab.')
                    expect(f.locator('section')).to_contain_text(BANK['ui']['checkLimit'])
                    expect(f.locator('#answer-0')).to_be_disabled()
                click('next')
        patterns=[(0,[0]),(0,[1]),(1,[0]),(1,[1]),(2,[0,0]),(2,[0,1]),(2,[1,0]),(2,[1,1])]
        for i,(weight,concerns) in enumerate(patterns):
            tier=LEVELS[i%4]
            new([tier]);click('next');click('help')
            expect(f.locator('#help-tier')).to_have_count(0)
            expect(f.locator('#dialog-body')).to_contain_text(BANK['cases']['Mutter']['tasks'][0]['helpByLevel'][tier][0])
            click('dismiss');outer('home');click('start');click('dismiss');click('resume')
            expect(f.locator('h1')).to_have_attribute('data-section','MU-02')
            entry('Lauras Frage',3)
            expect(f.locator('[data-terminal],#paper-ready,#open-Vater')).to_have_count(0)
            click('open-review')
            compare(tier,weight,concerns,edit=True)
            expect(f.locator('#open-Vater')).to_be_visible()
            expect(f.locator('#open-review')).to_have_count(0)
            expect(f.locator('[data-terminal]')).to_be_visible()
            expect(f.locator('section')).to_contain_text(BANK['ui']['reasonOpen'])
            entry('Lauras Frage',2);click('edit-weight')
            entry('Lauras Frage',3);expect(f.locator('#open-Vater')).to_have_count(0)
            expect(f.locator('#open-review')).to_be_visible()
            evidence.append(dict(niveau=tier,wahl=weight,fragen=concerns,wege='Ein Niveau; Hilfe, Abbruch, Festhalten und erneute Auswahl'))
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
            f.locator('aside > details > summary').click()
            status_text=BANK['ui']['skipped']
            if person in ('Großmutter','Vater'):status_text=person+' · '+status_text
            expect(f.locator('aside')).to_contain_text(status_text)
            entry(person,'transfer');click('answer-1');click('answer-0')
            expect(f.locator('section')).to_contain_text(BANK['ui']['assisted'])
            evidence.append(dict(anwendung=person,ausloesung='Getrennte Denkhandlungen, späte Hilfe, unterbrochen, zwei Fehlversuche, korrigiert'))
        # A reply may disclose the target even when no help button was pressed.
        for person,task_id,wrong,transfer in [('Mutter','Ergänzung',2,True),('Freundin','Ergänzung',1,True),
                ('Großmutter','Ergänzung',2,True),('Freundin','Leerstelle',1,False),('Vater','Folgerung',0,False)]:
            new(['ESA'])
            tasks=BANK['cases'][person]['tasks']
            at=next(i+1 for i,t in enumerate(tasks) if t['id']==task_id)
            entry(person,at);click('answer-'+str(wrong))
            click('answer-'+('2' if person=='Vater' else '0'))
            expect(f.locator('.tag')).to_have_text(BANK['ui']['used'])
            entry(person,len(tasks)+1)
            expect(f.locator('[data-application]')).to_have_count(int(transfer))
            evidence.append(dict(person=person,aufgedeckt_durch_rueckmeldung=task_id,passende_anwendung=transfer))
        for at,location in enumerate(BANK['evaluationRecovery']):
            entry('Lauras Frage',at)
            expect(f.locator('h1')).to_have_attribute('data-section',location['id'])
            evidence.append(dict(einstieg=location['id'],person='Laura'))
        page.reload();page.locator('#zweiter-tag').click()
        f=page.frame_locator('iframe[title^=Dienstag]')
        expect(f.locator('#start')).to_have_count(0)
        expect(f.locator('#level-1,#member,#start')).to_have_count(0)
        set_team(f,['ESA']);expect(f.locator('#resume')).to_have_count(0)
        assert page.evaluate('[localStorage.length,sessionStorage.length]')==[0,0]
        sources=check_sources(page,engine)
        version=browser.version;browser.close()
    return dict(browser=engine,version=version,pruefungen=evidence,quellenarbeit=sources)


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        result=list(pool.map(check,['chromium','webkit']))
    (OUT/'Zustaende.json').write_text(json.dumps(dict(commit=BANK['commit'],html_sha256=sha(APP.read_bytes()),browser=result),ensure_ascii=False,indent=2))
