"""Drive the delivered two-day app. Test judgments against the case meanings."""
import base64
import hashlib
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic
from zipfile import ZipFile

from lxml.html import fromstring
from playwright.sync_api import expect, sync_playwright
from release_abnahme import unpack
from tagesauswahl import host, HOST
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from familienrat_build import OUT, REF, ROOT, DAY02, payload, sha, markdown, git

QA = ROOT/'build/Familienrat-QA'
APP = OUT/'Fallakte.html'
BANK = json.loads((OUT/'Work-Materialvertrag.json').read_text())
LEVELS = BANK['levels']
NAMES = list(BANK['cases'])
# From the four messages and the two different questions about biology.
KEYS = {'Mutter':[0,0,0,0,0],'Freundin':[0,0,1,0,0],
        'Großmutter':[0,0,1,0],'Vater':[0,2,2,0]}
TEAMS = [[l] for l in LEVELS]+[['Förder','ESA'],['ESA','MSA'],['MSA','AHR'],['Förder','AHR']]
def snap(page,name):
    page.screenshot(path=QA/(name+'.jpg'),quality=62,animations='disabled')
def tap(frame,id):
    control=frame.locator('#'+id)
    if id.startswith('answer-') and not control.is_visible() and frame.locator('#more-options').count():
        frame.locator('#more-options summary').tap()
    control.tap()
def start(page,url,lms=False):
    page.goto(url)
    shell=page.frame(name='sco') if lms else page
    shell.locator('#zweiter-tag').tap()
    return shell,shell.frame_locator('iframe[title^=Dienstag]')
def set_team(f,team):
    for i,t in enumerate(team):f.locator('#level-'+str(i)).select_option(t)
def can_continue(f):
    return f.locator('#next').is_visible()
def hints(f,task,team):
    tap(f,'help')
    for d in range(5):
        if d:tap(f,'hint-next')
        expect(f.locator('#dialog-title')).to_have_text(f'Hilfe {d+1} / 5')
        expect(f.locator('#dialog-body')).to_contain_text(task['helpByLevel'][team[0]][d])
    if len(team)>1:
        f.locator('#help-tier').select_option(team[1])
        expect(f.locator('#dialog-body')).to_contain_text(task['helpByLevel'][team[1]][4])
    tap(f,'dismiss')
    expect(f.locator('#help')).to_be_focused()

def paper(f,key,team,trace):
    step=BANK['media']['steps'][key]
    panel=f.locator('[data-handoff]')
    expect(panel).to_have_count(1)
    expect(panel).to_have_attribute('data-handoff',key)
    expect(f.locator('h1')).to_have_text(step['section'])
    expect(f.locator('h1')).to_have_attribute('data-section',step['sectionId'])
    orders=panel.locator('[data-member]')
    expect(orders).to_have_count(len(team))
    texts=[]
    for i,tier in enumerate(team):
        order=orders.nth(i)
        expect(order).to_have_attribute('data-level',tier)
        expect(order).to_be_visible()
        text=order.inner_text()
        assert text==step['orders'][tier]['screen'] and step['field'] in text
        texts.append(text)
    # A repeated generic writing instruction outside the handoff would give pupils
    # two paper assignments, even if the contract itself were internally consistent.
    stray=f.locator('main p:not([data-handoff] p)').all_inner_texts()
    assert not any('Halte Wert und Norm' in text or 'Schreibe deine Verbindung jetzt' in text for text in stray)
    back=f.locator('[data-return]')
    expect(back).to_have_count(1)
    expect(back).to_have_text(step['returnText'])
    expect(back).to_have_attribute('data-return',step['nextId'])
    if step['after']:expect(panel).to_contain_text(step['after'])
    trace.append(dict(schritt=key,abschnitt=f.locator('h1').inner_text(),feld=step['field'],
                      auftraege=texts,rueckweg=back.inner_text(),ziel=step['nextId']))
    return step

def arrived(f,step):
    expect(f.locator('h1')).to_have_attribute('data-section',step['nextId'])
    expect(f.locator('h1')).to_have_text(step['returnText'].removeprefix('Weiter im Chat: '))

def case(page,f,person,team,probe,trace,shots=False):
    application=None
    c=BANK['cases'][person]
    expect(f.locator('aside')).to_contain_text(c['original'].split('.')[0])
    tap(f,'next')
    for j,(task,key) in enumerate(zip(c['tasks'],KEYS[person],strict=True)):
        expect(f.locator('main h2').last).to_have_text(task['prompt'])
        assert not can_continue(f)
        if task['id']=='Ergänzung':
            step=paper(f,task['sectionId'].split('-')[0]+'-erst',team,trace)
            arrived(f,step)
            if shots:snap(page,person+'-Erstfeld')
        else:expect(f.locator('[data-handoff]')).to_have_count(0)
        if f.locator('#compare').is_visible():
            expect(f.locator('#compare')).to_be_disabled()
            expect(f.locator('#answer-0')).to_have_count(0)
            if probe:
                f.locator('textarea').fill('   ')
                expect(f.locator('#compare')).to_be_disabled()
                f.locator('textarea').fill('…')
                expect(f.locator('#compare')).to_be_disabled()
            if probe and team==['AHR'] and j==0 and person=='Mutter' and page.context.browser.browser_type.name=='chromium':
                snap(page,'Eigenleistung')
            if task.get('evidenceSentences') and (j==1 or not probe):
                f.get_by_text(BANK['ui']['sourceInstead'],exact=True).tap()
                indices=task['evidenceSentences']
                if probe:
                    tap(f,'source-'+str(next(i for i in range(3) if i not in indices)))
                    expect(f.locator('section')).to_contain_text(BANK['ui']['sourceRetry'])
                    expect(f.locator('#answer-0')).to_have_count(0)
                tap(f,'source-'+str(indices[0]))
                expect(f.locator('section')).to_contain_text(BANK['ui']['sourceYes'])
            else:
                thought=c['tasks'][j]['answers'][key]['text']
                if person=='Mutter' and j==0:thought='Ihr liegt Lauras Wohlergehen am Herzen.'
                f.locator('textarea').fill(thought);tap(f,'compare')
                expect(f.locator('section')).to_contain_text(thought)
                expect(f.locator('section')).to_contain_text(BANK['ui']['freeNote'])
        if shots and j==0:snap(page,person+'-Aufgabe')
        if probe:
            hints(f,task,team)
            tap(f,'cards')
            expect(f.locator('#dialog-body')).to_contain_text(c['card'])
            if person=='Mutter' and task['id']=='Ergänzung':
                card=f.locator('#dialog-body > details').first
                if card.get_attribute('open') is None:card.locator('summary').first.tap()
                if card.locator('details').count():card.locator('details summary').tap()
                expect(card.get_by_text('Schwangerschaftsgewebe',exact=False).last).to_be_visible()
                expect(card).to_contain_text('mit einer Blutung ausgestoßen')
            tap(f,'dismiss')
            for no,opt in enumerate(task['answers']):
                if no==key:continue
                tap(f,'answer-'+str(no));expect(f.locator('#response')).to_have_text(opt['feedback'])
                assert not can_continue(f)
                if shots and j==0 and person=='Mutter':snap(page,'Mutter-Rueckmeldung')
            if shots and j==0 and person=='Mutter':
                tap(f,'help');tap(f,'hint-next');snap(page,'Mutter-Hilfe');tap(f,'dismiss')
        tap(f,'answer-'+str(key));expect(f.locator('#response')).to_have_text(task['answers'][key]['feedback'])
        if probe:expect(f.locator('.tag').last).to_have_text(BANK['ui']['used'])
        elif team==['ESA']:expect(f.locator('.tag').last).to_have_text(BANK['ui']['own'])
        tap(f,'next')
    if probe:
        task=c['transfer']
        advanced=all(t in ('MSA','AHR') for t in team)
        prompt=task.get('advancedPrompt',task['prompt']) if advanced else task['prompt']
        expect(f.locator('section h2').first).to_have_text(prompt)
        expect(f.locator('aside')).not_to_contain_text(c['addition'])
        expect(f.locator('[data-handoff]')).to_have_count(0)
        assert not can_continue(f)
        expect(f.locator('#jump')).to_be_visible()
        visible_words=len(f.locator('section').inner_text().split())
        if shots and person=='Mutter':snap(page,'Anwendung')
        # Each result is final on this question. Use different teams for each distractor,
        # a correct first application and correct selection after consulting a solution.
        source=LEVELS.index(team[0])
        selected=0 if source in (0,3) else source
        if source==3:hints(f,task,team)
        if selected==0 and person in ('Mutter','Freundin'):
            # Select by the biological meaning independently of JSON order and ok flags.
            if person=='Mutter':
                meaning='Kontraktionen können auch ohne Operation schmerzen.' if advanced else 'Die Gebärmutter zieht sich zusammen.'
            else:
                meaning='Nach einem komplikationslosen Abbruch bleibt eine spätere Schwangerschaft möglich.' if advanced else 'Nein. Sie ist möglich, aber nicht sicher.'
            f.get_by_role('button',name=meaning,exact=not advanced).tap()
        else:tap(f,'answer-'+str(selected))
        answer=task['answers'][selected]
        expected=answer.get('advancedFeedback',answer['feedback']) if advanced else answer['feedback']
        expect(f.locator('#response')).to_have_text(expected)
        expect(f.locator('#answer-0')).to_be_disabled()
        expect(f.locator('section')).not_to_contain_text(BANK['ui']['helpBeforePaper'])
        expect(f.locator('section')).not_to_contain_text(BANK['ui']['mixedTransfer'])
        outcome=BANK['ui']['applied' if source==0 else 'assisted']
        expect(f.locator('section')).to_contain_text(outcome)
        application=dict(person=person,frage=prompt,option=selected,rueckmeldung=expected,status=outcome,
                         woerter_vor_antwort=visible_words,hilfe_bei_anwendung=source==3)
    else:
        expect(f.locator('section')).not_to_contain_text(BANK['ui']['helpBeforePaper'])
    expect(f.locator('aside')).to_contain_text('Unsere Ergänzung für Laura')
    expect(f.locator('aside')).to_contain_text(c['addition'])
    step=paper(f,c['recovery'][0]['id'].split('-')[0]+'-ergebnis',team,trace)
    if probe:expect(f.locator('[data-handoff]')).to_contain_text(step['support'])
    matrix=f.locator('details[data-digital=matrix]')
    expect(matrix.locator('summary')).to_have_text(BANK['ui']['readMatrix'])
    assert matrix.get_attribute('open') is None
    if shots:
        f.locator('#next').scroll_into_view_if_needed();snap(page,person+'-Ergebnisfeld')
        matrix.locator('summary').tap()
        for value in c['matrix'].values():expect(matrix).to_contain_text(value)
        matrix.locator('summary').tap()
    tap(f,'next');arrived(f,step)
    return application

def judgment(page,f,team,route,probe,trace,shots):
    expect(f.locator('aside')).to_contain_text('Entscheiden möchte ich selbst.')
    if shots:snap(page,'Lauras-zweite-Nachricht')
    tap(f,'next')
    step=paper(f,'LA-eigen',team,trace)
    for t in team:expect(f.locator('section')).to_contain_text(BANK['evaluation'][t])
    if shots:snap(page,'Persoenliche-Bewertung')
    assert not f.locator('#open-Vater').is_visible()
    if probe:
        tap(f,'help');tap(f,'hint-last');expect(f.locator('#dialog-body')).to_contain_text('Eine andere mögliche Antwort')
        tap(f,'dismiss')
    tap(f,'next');arrived(f,step)
    for index,t in enumerate(team):
        choice=(route+index)%3
        expect(f.locator('section h2')).to_contain_text(t)
        expect(f.locator('[data-fieldref]')).to_have_attribute('data-fieldref',step['field'])
        expect(f.locator('[data-handoff]')).to_have_count(0)
        if shots and index==0:snap(page,'Fachbezug-Pruefen')
        tap(f,'weight-'+str(choice))
        for n in ([0,1] if choice==2 else [choice]):
            tap(f,'concern-'+str(n))
            if probe:
                for wrong,row in [(1-n,4 if n==0 else 5),(2,6),(3,7)]:
                    tap(f,'fact-'+str(wrong));expect(f.locator('section')).to_contain_text(BANK['review'][row][1].split('“')[0])
            tap(f,'fact-'+str(n))
            if probe:
                tap(f,'answer-1');expect(f.locator('#response')).to_have_text(BANK['limits'][n]['answers'][1]['feedback'])
                tap(f,'help');tap(f,'hint-last');tap(f,'dismiss')
            tap(f,'answer-0');tap(f,'next')
    step=paper(f,'LA-abschluss',team,trace);arrived(f,step)
    if shots:
        f.locator('[data-handoff]').scroll_into_view_if_needed();snap(page,'Lernbogen-Sicherung')
    expect(f.locator('#open-Großmutter')).to_be_visible()
    for i in range(len(team)):expect(f.locator('section')).to_contain_text(team[i])

def check_freeze(browser,engine):
    shots=[]
    for path in (REF/'dist/Vorabkandidat/Fallakte.html',APP):
        p=browser.new_page(viewport={'width':820,'height':1180},has_touch=True)
        p.goto(path.as_uri());p.locator('#erster-tag').tap()
        f=p.frame_locator('iframe[title^=Mittwoch]')
        f.locator('#level-ESA').tap();f.locator('#neu').tap()
        f.locator('[data-strategy="K"]').tap()
        p.evaluate('document.fonts.ready')
        f.locator('body').evaluate('e=>e.ownerDocument.fonts.ready')
        expect(p.locator('#gespraechsstand')).to_contain_text('Laura 1')
        shots.append(p.screenshot(animations='disabled'))
        if path==APP:
            p.locator('#zurueck').tap();p.locator('#zweiter-tag').tap()
            g=p.frame_locator('iframe[title^=Dienstag]');set_team(g,['ESA']);tap(g,'start');tap(g,'next')
            p.locator('#zurueck').tap();p.locator('#erster-tag').tap()
            expect(f.locator('#aktueller-rat')).to_have_attribute('data-about-strategy','K')
            p.locator('#zurueck').tap();p.locator('#zweiter-tag').tap();expect(g.locator('main h2').last).to_have_text(BANK['cases']['Mutter']['tasks'][0]['prompt'])
        p.close()
    assert shots[0]==shots[1],engine+' – Pixelvergleich'
    return sha(shots[1])

def recover(page,f,shell,team,person,step):
    shell.locator('[data-action=recovery]').tap();set_team(f,team)
    f.locator('#person').select_option(person);f.locator('#entry').select_option(str(step))
    tap(f,'open-entry')

def engine_run(engine,url):
    results=[]
    with sync_playwright() as pw:
        b=getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE'))
        freeze=check_freeze(b,engine)
        for route,team in enumerate(TEAMS + [[t] for t in LEVELS]):
            portrait=route%2==0
            size=(390,844) if route==6 else (820,1180) if portrait else (1180,820)
            ctx=b.new_context(has_touch=True,viewport=dict(zip(('width','height'),size)),reduced_motion='reduce')
            page=ctx.new_page();page.set_default_timeout(7000)
            errors=[];requests=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('request',lambda r:requests.append(r.url) if r.url.startswith(('http:','https:')) and not r.url.startswith(url) else None)
            lms=route%2==1
            shell,f=start(page,url+'/host.html' if lms else APP.as_uri(),lms)
            set_team(f,team)
            shots=engine=='chromium' and route==4
            if shots:snap(page,'Erste-Nachricht-und-Team')
            if route==6:f.locator('html').evaluate("e=>e.style.fontSize='150%'")
            f.locator('body').evaluate("""e=>{window.taps=0;document.addEventListener('click',()=>window.taps++,true);
                window.inputs=new Set();document.addEventListener('input',e=>{if(e.target.tagName==='TEXTAREA')window.inputs.add(document.querySelector('h1').dataset.section)});
                window.views=[];new MutationObserver(()=>{let text=document.querySelector('h1')?.textContent;
                if(text && text!==window.views.at(-1))window.views.push(text)}).observe(e,{subtree:true,childList:true});}""")
            probe=route<4 or shots
            start_time=monotonic();tap(f,'start')
            trace=[]
            applications=[case(page,f,n,team,probe,trace,shots) for n in NAMES[:2]]
            judgment(page,f,team,route,probe,trace,shots)
            stats=f.locator('body').evaluate('()=>({tipps:window.taps,ansichten:window.views,schreibfelder:window.inputs.size})')
            stats.update(papierweg=list(trace),anwendungen=[a for a in applications if a],sekunden=round(monotonic()-start_time,2),browser=engine,version=b.version,niveaus=team,
                         viewport=size,weg='Gegenprobe mit allen Fehlern und Hilfen' if probe else 'Regulärer Pflichtweg',
                         format='SCORM' if lms else 'Offline-HTML')
            if route<4 or shots:
                for n in NAMES[2:]:
                    tap(f,'open-'+n);case(page,f,n,team,probe,trace,shots)
            if route==0 or route==7:
                page.reload();shell=page.frame(name='sco') if lms else page
                shell.locator('#zweiter-tag').tap();f=shell.frame_locator('iframe[title^=Dienstag]')
                recover(page,f,shell,team,'Freundin',5)
                expect(f.locator('section')).to_contain_text(BANK['cases']['Freundin']['tasks'][-1]['prompt'])
                paper(f,'FR-erst',team,[])
                for n,prefix in [('Großmutter','GM'),('Vater','VA')]:
                    recover(page,f,shell,team,n,5)
                    direct=paper(f,prefix+'-einstieg',team,trace)
                    if engine=='webkit' and route==7 and n=='Vater':snap(page,'Reserve-Neustart')
                    tap(f,'next');arrived(f,direct)
                recover(page,f,shell,team,'Freundin','transfer')
                expect(f.locator('[data-application]')).to_have_attribute('data-application',BANK['media']['steps']['FR-ergebnis']['restartApplication']['id'])
                expect(f.locator('[data-handoff]')).to_have_count(0)
                tap(f,'answer-1');direct=paper(f,'FR-ergebnis',team,trace)
                tap(f,'next');arrived(f,direct)
                recover(page,f,shell,team,'Freundin',5)
                if engine=='webkit' and route==7:snap(page,'Wiedereinstieg')
                if route==7:
                    recover(page,f,shell,team,'Lauras Frage',2)
                    tap(f,'weight-0');tap(f,'concern-1');tap(f,'fact-1');tap(f,'other')
                    tap(f,'edit-weight');expect(f.locator('#weight-2')).to_be_visible()
                    for member,(family,concern) in enumerate([(0,1),(1,0)]):
                        tap(f,'weight-'+str(family));tap(f,'concern-'+str(concern));tap(f,'fact-'+str(concern))
                        expect(f.locator('section')).to_contain_text(BANK['crossReference'][concern])
                        if not member:
                            tap(f,'rechoose');tap(f,'concern-1');tap(f,'fact-1')
                        tap(f,'other');expect(f.locator('#check-reason')).to_be_disabled()
                        expect(f.locator('#answer-0')).to_have_count(0)
                        f.locator('textarea').fill(['Zur Sorge der Mutter um Laura gehört für mich auch die spätere Fruchtbarkeit.',
                                                  'Für ihre Ausbildung ist auch wichtig, wie es Laura jetzt geht.'][member])
                        tap(f,'check-reason');tap(f,'answer-1');assert not can_continue(f)
                        tap(f,'answer-0');tap(f,'next')
                    expect(f.locator('section')).to_contain_text(BANK['ui']['limitChecked'])
                    expect(f.get_by_text(BANK['ui']['reasonOpen'],exact=True)).to_have_count(2)
                    expect(f.locator('section')).not_to_contain_text(BANK['ui']['own'])
                    stats['eigene_verbindungen']=f.locator('section').inner_text()
                    if engine=='webkit':snap(page,'Eigene-Verbindung')
                for n in [*NAMES,'Lauras Frage']:
                    recover(page,f,shell,team,n,0)
                    expect(f.locator('aside')).to_contain_text('Laura')
                # A shortcut imports underlying facts as help without granting prior answers.
                f.locator('aside > details > summary').tap();expect(f.locator('aside')).to_contain_text('Als Hilfe bereitgestellt')
                # Leave the first case after a full hint on an earlier analysis question.
                # The factual check stays available, including after a detour to Laura.
                recover(page,f,shell,team,'Mutter',1)
                tap(f,'help');tap(f,'hint-last');tap(f,'dismiss');tap(f,'jump')
                f.locator('aside > details > summary').tap()
                expect(f.locator('aside')).to_contain_text(BANK['ui']['pending'])
                recover(page,f,shell,team,'Mutter',6)
                expect(f.locator('#next')).to_have_count(0)
                shell.locator('[data-action=resources]').tap();tap(f,'dismiss')
                tap(f,'answer-0')
                expect(f.locator('section')).to_contain_text(BANK['ui']['assisted'])
            if lms:
                assert page.evaluate('[localStorage.length,sessionStorage.length]')==[0,0]
                page.locator('iframe').evaluate("e=>e.src='about:blank'")
                page.wait_for_function("calls.some(c=>c[0]==='LMSFinish')")
                assert page.evaluate('calls')==[['LMSInitialize',''],['LMSFinish','']]
            assert not errors and not requests,(errors,requests)
            stats['alle_uebergaben']=[r['schritt'] for r in trace]
            results.append(stats);ctx.close();print(engine,team,stats['tipps'],flush=True)
        p=b.new_page();p.goto(APP.as_uri())
        if engine=='webkit':snap(p,'Tagesauswahl')
        b.close()
    return dict(wege=results,pixelvergleich=freeze)

def main():
    QA.mkdir(parents=True,exist_ok=True)
    raw=APP.read_bytes()
    assert sha(base64.b64decode(payload(raw,b'02')))==DAY02
    second=fromstring(base64.b64decode(payload(raw,b'08')))
    assert json.loads(second.get_element_by_id('material').text)==BANK
    assert markdown(BANK) in (OUT/'Work-Materialvertrag.md').read_text()
    assert all(len(t['hints'])==5 and sum(o['ok'] for o in t['answers'])==1
               for c in BANK['cases'].values() for t in c['tasks']+[c['transfer']])
    prior=json.loads(git('show','b0b5d0f3dd76e444ad99de0129724da899f3efe0:module/familienrat/material.json'))
    for key in ('opening','second','cards','limits','evaluation','expectation'):
        assert BANK[key]==prior[key],key
    for person,c in BANK['cases'].items():
        old={k:v for k,v in prior['cases'][person].items() if k not in ('first','paper','return','destination')}
        assert {k:v for k,v in c.items() if k not in ('tasks','transfer')}=={k:v for k,v in old.items() if k not in ('tasks','transfer')}
        assert [{k:v for k,v in t.items() if k!='evidenceSentences'} for t in c['tasks']]==old['tasks']
    baseline=json.loads(git('show','aee6716bad4e0729b21d52cb0459cf467ccc9d3c:module/familienrat/material.json'))
    for name,case_data in BANK['cases'].items():
        assert case_data['tasks']==baseline['cases'][name]['tasks'] and case_data['transfer']==baseline['cases'][name]['transfer']
    for old,new in [(baseline['evaluationHints'],BANK['evaluationHints']),*[(baseline['evaluationHelpByLevel'][t],BANK['evaluationHelpByLevel'][t]) for t in LEVELS]]:
        assert new[:-1]==old[:-1] and new[-1]+' Halte deine Verbindung auf dem Bogen fest.'==old[-1]
    media=BANK['media']
    sections={r['id']:r['section'] for c in BANK['cases'].values() for r in c['recovery']}
    sections.update({r['id']:r['section'] for r in BANK['evaluationRecovery']})
    assert set(media['fields'])==set(BANK['paperFields'])=={r['field'] for r in media['steps'].values()}
    matrix=(OUT/'Medienwechsel-und-Papierfeldmatrix.md').read_text()
    for key,r in media['steps'].items():
        assert r['id']==key and r['section']==sections[r['sectionId']]
        assert r['returnText']=='Weiter im Chat: '+sections[r['nextId']] and r['restart'].endswith(sections[r['nextId']])
        assert set(r['orders'])==set(LEVELS) and r['help'] and r['kind'] and r['returnText'] in matrix
        for level,order in r['orders'].items():
            assert order['action'] in matrix and r['field'] in order['screen']
            if level in LEVELS[:2]:assert 'schreibe' not in order['action'].lower() and 'notiere' not in order['action'].lower()
    with TemporaryDirectory() as td:
        path=Path(td);unpack(OUT,'Fallakte',path);(path/'host.html').write_text(HOST)
        with host(path) as url,ThreadPoolExecutor(max_workers=2) as pool:
            checks=list(pool.map(lambda name:engine_run(name,url),('chromium','webkit')))
    for engine in checks:
        assert {k for row in engine['wege'] for k in row['alle_uebergaben']}==set(media['steps'])
        for row in engine['wege']:
            assert [s['schritt'] for s in row['papierweg']]==['MU-erst','MU-ergebnis','FR-erst','FR-ergebnis','LA-eigen','LA-abschluss']
    (QA/'Browser.json').write_text(json.dumps(dict(commit=BANK['commit'],sha256=sha(raw),browser=checks),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
