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
from familienrat_build import OUT, REF, ROOT, DAY02, payload, sha, markdown

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

def case(page,f,person,team,probe,shots=False):
    c=BANK['cases'][person]
    expect(f.locator('aside')).to_contain_text(c['original'].split('.')[0])
    tap(f,'next')
    for j,(task,key) in enumerate(zip(c['tasks'],KEYS[person],strict=True)):
        expect(f.locator('main h2').last).to_have_text(task['prompt'])
        assert not can_continue(f)
        if f.locator('#compare').is_visible():
            if probe:f.locator('textarea').fill(BANK['variants'][LEVELS.index(team[-1])%3] if j==0 else 'Mein eigener Satz zu dieser Textstelle.')
            tap(f,'compare')
            if probe:expect(f.locator('main')).to_contain_text(BANK['ui']['freeNote'])
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
        tap(f,'next')
    if probe and person in NAMES[:2]:
        tap(f,'optional-transfer')
    if probe:
        expect(f.locator('main h2').last).to_have_text(c['transfer']['prompt'])
        hints(f,c['transfer'],team)
        for i in range(1,len(c['transfer']['answers'])):
            tap(f,'answer-'+str(i));expect(f.locator('#response')).to_have_text(c['transfer']['answers'][i]['feedback'])
        tap(f,'answer-0');tap(f,'next')
    expect(f.locator('aside')).to_contain_text('Unsere Ergänzung für Laura')
    expect(f.locator('aside')).to_contain_text(c['addition'])
    expect(f.locator('section')).to_contain_text(c['paper'])
    expect(f.locator('#next')).to_have_text(c['return']);tap(f,'next')

def judgment(page,f,team,route,probe,shots):
    expect(f.locator('aside')).to_contain_text('Entscheiden möchte ich selbst.')
    if shots:snap(page,'Lauras-zweite-Nachricht')
    tap(f,'next')
    for t in team:expect(f.locator('section')).to_contain_text(BANK['evaluation'][t])
    if shots:snap(page,'Persoenliche-Bewertung')
    assert not f.locator('#open-Vater').is_visible()
    if probe:
        tap(f,'help');tap(f,'hint-last');expect(f.locator('#dialog-body')).to_contain_text('Eine andere mögliche Antwort')
        tap(f,'dismiss')
    tap(f,'next')
    for index,t in enumerate(team):
        choice=(route+index)%3
        expect(f.locator('section h2')).to_contain_text(t)
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
                window.views=[];new MutationObserver(()=>{let text=document.querySelector('h1')?.textContent;
                if(text && text!==window.views.at(-1))window.views.push(text)}).observe(e,{subtree:true,childList:true});}""")
            probe=route<4 or shots
            start_time=monotonic();tap(f,'start')
            for n in NAMES[:2]:case(page,f,n,team,probe,shots)
            judgment(page,f,team,route,probe,shots)
            stats=f.locator('body').evaluate('()=>({tipps:window.taps,ansichten:window.views})')
            stats.update(sekunden=round(monotonic()-start_time,2),browser=engine,version=b.version,niveaus=team,
                         viewport=size,weg='Gegenprobe mit allen Fehlern und Hilfen' if probe else 'Regulärer Pflichtweg',
                         format='SCORM' if lms else 'Offline-HTML')
            if route<4 or shots:
                for n in NAMES[2:]:
                    tap(f,'open-'+n);case(page,f,n,team,probe,shots)
            if route==0 or route==7:
                page.reload();shell=page.frame(name='sco') if lms else page
                shell.locator('#zweiter-tag').tap();f=shell.frame_locator('iframe[title^=Dienstag]')
                recover(page,f,shell,team,'Freundin',5)
                expect(f.locator('section')).to_contain_text(BANK['cases']['Freundin']['tasks'][-1]['prompt'])
                if engine=='webkit' and route==7:snap(page,'Wiedereinstieg')
                if route==7:
                    recover(page,f,shell,team,'Lauras Frage',2)
                    tap(f,'weight-0');tap(f,'concern-1');tap(f,'fact-1')
                    expect(f.locator('section')).to_contain_text(BANK['review'][8][1].split('“')[0])
                    tap(f,'other')
                    expect(f.locator('section')).to_contain_text(BANK['ui']['otherNote'])
                    tap(f,'edit-weight');expect(f.locator('#weight-2')).to_be_visible()
                for n in [*NAMES,'Lauras Frage']:
                    recover(page,f,shell,team,n,0)
                    expect(f.locator('aside')).to_contain_text('Laura')
                # A shortcut imports underlying facts as help without granting prior answers.
                f.locator('aside > details > summary').tap();expect(f.locator('aside')).to_contain_text('Als Hilfe bereitgestellt')
            if lms:
                assert page.evaluate('[localStorage.length,sessionStorage.length]')==[0,0]
                page.locator('iframe').evaluate("e=>e.src='about:blank'")
                page.wait_for_function("calls.some(c=>c[0]==='LMSFinish')")
                assert page.evaluate('calls')==[['LMSInitialize',''],['LMSFinish','']]
            assert not errors and not requests,(errors,requests)
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
    with TemporaryDirectory() as td:
        path=Path(td);unpack(OUT,'Fallakte',path);(path/'host.html').write_text(HOST)
        with host(path) as url,ThreadPoolExecutor(max_workers=2) as pool:
            checks=list(pool.map(lambda name:engine_run(name,url),('chromium','webkit')))
    (QA/'Browser.json').write_text(json.dumps(dict(commit=BANK['commit'],sha256=sha(raw),browser=checks),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
