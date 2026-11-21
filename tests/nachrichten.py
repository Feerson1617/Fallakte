"""Operate the eight new sections through the actual B deliveries in two engines."""
import base64
import json
import os
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from playwright.sync_api import expect, sync_playwright
from bestandsschutz import archive, build, digest
from tagesauswahl import HOST, host

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'build/08-12'
QA = OUT/'Abnahme'
BANK = json.loads((OUT/'Aufgabenbank.json').read_text())
REVIEWED = 'ec94147fd8d61442305a0281f7df032f3162362c'
B = ROOT/'dist/Version-B'
PATTERN = rb'(<script id="modul-08" type="application/octet-stream">)([A-Za-z0-9+/=]+)(</script>)'


def protect(temp):
    ref = temp/'ref'
    archive(REVIEWED,ref,['index.html','02-12.html','assets','app','data','module','tagesauswahl','scorm','scripts'])
    build(ref)
    for v in 'AB':
        name = 'Version-'+v
        current = (ROOT/'dist'/name/'Fallakte.html').read_bytes()
        before = (ref/'dist'/name/'Fallakte.html').read_bytes()
        if v=='B':
            module = (OUT/'Fallakte.html').read_bytes()
            assert base64.b64decode(re.search(PATTERN,current)[2],validate=True)==module
            assert re.findall(PATTERN,before) and len(re.findall(PATTERN,current))==1
            current = re.sub(PATTERN,lambda m: re.search(PATTERN,before)[0],current)
        assert current==before, name
    assert digest((ROOT/'module/08-12/nachrichten.json').read_bytes())=='f25563a5bc6d30528e3f47bc42412b03a054c9dc35df5322bc4624231a3b3278'
    assert all(word not in json.dumps(BANK,ensure_ascii=False).lower() for word in (
        'bewertungskompetenz','bewertungskriterium','argumentationsqualität','kriteriengeleitet'))
    return digest((ref/'dist/Version-A/Fallakte.html').read_bytes())


def check_content():
    # Independent anchors for the intended medical, legal and textual decisions.
    anchors = {
        'Mutter': ('Norm','Blutungen treten auf. Schmerzen sind möglich.'),
        'Freundin': ('Fakt','Nein. Es geht grundsätzlich ohne Operation.',
                     'Nein. Es kommt zu Blutungen. Schmerzen sind möglich.'),
        'Großmutter': ('Wert','Sie nennt ihren Glauben und wünscht sich, dass Laura das Kind bekommt.'),
        'Vater': ('Folgerung','Anerkannte Stelle und mindestens drei Tage Abstand.'),
    }
    for person,case in BANK['cases'].items():
        for level,tasks in case['levels'].items():
            solutions=[next(o['label'] for o in t['options'] if o['correct']) for t in tasks[:-1]]
            assert solutions[:len(anchors[person])]==list(anchors[person])
            assert list(dict.fromkeys(t['heading'] for t in tasks))==['Argumenten-Check',*BANK['questions']]
            assert tasks[-1]['kind']=='judgment' and len(tasks[-1]['options'])==3
            assert all(len(t['hints'])==5 and len(set(t['hints']))==5 for t in tasks)
            for t in tasks[:-1]:
                assert sum(o['correct'] for o in t['options'])==1
                for line in t['lines']: assert 1<=line<=len(case['message'])
                for line in t['wishes']: assert 1<=line<=len(BANK['laura'])
                if t['card']:
                    key,lines=t['card']
                    assert all(1<=i<=len(BANK['cards'][key]['lines']) for i in lines)
            if person=='Freundin' and level in ['MSA','AHR']:
                assert 'Nein. Richtige Informationen helfen. Laura entscheidet selbst.' in solutions
            if person=='Vater' and level in ['MSA','AHR']:
                assert 'Ja. Man kann nachlesen, was vorgeschrieben ist.' in solutions
            assert bool(tasks[-1]['counter'])==(level=='AHR')


def btn(frame,label):
    return frame.get_by_role('button',name=label,exact=True)


def layout(frame):
    result = frame.locator('body').evaluate("""body=>({
      overflow: document.documentElement.scrollWidth-innerWidth,
      small: [...body.querySelectorAll('button,summary')].filter(e=>e.getClientRects().length && e.getBoundingClientRect().height < 43.9).map(e=>e.textContent)
    })""")
    assert result['overflow']<=1 and not result['small'], result


def shot(page,name):
    page.screenshot(path=QA/(name+'.jpg'),type='jpeg',quality=73,animations='disabled')


def inspect_task(frame,task):
    expect(frame.get_by_role('heading',name=task['heading'],exact=True)).to_be_visible()
    article = frame.locator('article')
    expect(article.get_by_text(task['prompt'],exact=True)).to_be_visible()
    # A real learner can go straight to 5, then back to any level without submitting.
    btn(article,'Hilfe').tap()
    for index in [4,0,1,2,3,4]:
        btn(article,f'Hilfe {index+1} – '+BANK['helps'][index]).dispatch_event('click')
        expect(article.locator('.note p').first).to_have_text(task['hints'][index])
    btn(article,'Hilfe schließen').dispatch_event('click')
    if task['kind']=='judgment':
        return
    options=article.locator('.category-grid button,.options button')
    for pos,option in enumerate(task['options']):
        if not option['correct']:
            options.nth(pos).dispatch_event('click')
            expect(article.get_by_role('status')).to_contain_text(option['feedback'])
            expect(btn(article,'Weiter')).to_be_hidden()
    correct=next(i for i,o in enumerate(task['options']) if o['correct'])
    options.nth(correct).tap()
    expect(article.get_by_role('status')).to_contain_text(task['options'][correct]['feedback'])


def exercise(browser,engine,person,level,n,base):
    scorm=n%2==0
    w,h=(820,1180) if n%4 in (0,3) else (1180,820)
    font=150 if n%3==0 else 100
    context=browser.new_context(viewport={'width':w,'height':h},has_touch=True,is_mobile=True)
    errors,requests=[],[]
    allowed = {base+'/host.html',base+'/index.html'} if scorm else set()
    def route(r):
        if r.request.url in allowed:
            r.continue_()
        else:
            requests.append(r.request.url)
            r.abort()
    context.route('http*/**',route)
    context.add_init_script("""window.storageWrites=[];for(const name of ['setItem','removeItem','clear']){
      const fn=Storage.prototype[name]; Storage.prototype[name]=function(...args){storageWrites.push(name);return fn.apply(this,args);}
    }""")
    p=context.new_page()
    p.on('pageerror',lambda err:errors.append(str(err)))
    p.goto(base+'/host.html' if scorm else (B/'Fallakte.html').as_uri())
    shell=p.frame(name='sco') if scorm else p.main_frame
    shell.locator('#zweiter-tag').tap()
    frame=shell.frame_locator('iframe[title="Dienstag, 08.12.2026"]')
    sections=BANK['cases'][person]['sections']
    action=lambda a:shell.locator('#modulaktionen [data-action="'+a+'"]')
    def scale():
        frame.locator('html').evaluate('(el,n)=>el.style.fontSize=n+"%"',font)
    scale()
    expect(frame.get_by_role('heading',name=BANK['lead'])).to_be_visible()
    for case in BANK['cases'].values():
        for s in case['sections']: expect(btn(frame,s)).to_be_visible()
    layout(frame)
    if n==0: shot(p,engine+'-Übersicht')
    btn(frame,level).tap()
    btn(frame,sections[0]).tap()
    case=BANK['cases'][person]
    tasks=case['levels'][level]
    for i,task in enumerate(tasks):
        inspect_task(frame,task)
        layout(frame)
        if i==0:
            btn(frame,'Zeile für Zeile lesen').tap()
            btn(frame,'Nächster Teil').tap()
            expect(frame.locator('aside .lines').first).to_contain_text(case['message'][1])
            btn(frame,'Lesen beenden').tap()
        if i==1:
            # Keep the answer and opened hint through card, shell and same-tier section changes.
            btn(frame,'Hilfe').tap()
            btn(frame,'Hilfe 3 – '+BANK['helps'][2]).tap()
            action('resources').tap()
            expect(frame.get_by_role('heading',name='Fachkarten')).to_be_visible()
            btn(frame,'Zurück').tap()
            shell.locator('#zurueck').tap();shell.locator('#zweiter-tag').tap()
            action('overview').tap();btn(frame,sections[1]).tap()
            expect(frame.locator('article .note h3')).to_have_text(BANK['helps'][2])
            expect(btn(frame,'Weiter')).to_be_visible()
            if n in (0,5,10,15): shot(p,engine+'-'+person+'-'+level)
            btn(frame,'Hilfe schließen').tap()
        if task['kind']!='judgment':
            btn(frame,'Weiter').tap()
            continue
        article=frame.locator('article')
        for result in task['results']:expect(article.get_by_text(result,exact=True)).to_be_visible()
        btn(frame,'Abschnitt beenden').tap()
        expect(article.get_by_role('status')).to_have_text('Wähle dein Urteil.')
        # Deliberately submit all three judgements with evidence. None gets a score.
        for j,label in enumerate(task['options']):
            btn(article,label).tap()
            btn(article,task['anchors'][j%2]).tap()
            if level=='Förder':
                if j==0 and person!='Vater':
                    btn(article,task['links'][1]).tap()
                    btn(frame,'Abschnitt beenden').tap()
                    expect(article.get_by_role('status')).to_have_text(BANK['verdictUI']['reconnect'])
                btn(article,task['links'][j%2]).tap()
            elif j==0:
                article.get_by_label('Dein Grund').fill('Ich beziehe mich auf die Stelle in der Nachricht.')
            elif j==1:
                article.get_by_label('Dein Grund').fill('')
                btn(article,'Ich habe meinen Grund gesagt.').tap()
            if task['counter']:expect(article.get_by_text(task['counter'],exact=True)).to_be_visible()
            if n==5 and j==0:shot(p,engine+'-Urteil')
            btn(frame,'Abschnitt beenden').tap()
            expect(frame.get_by_role('heading',name=person+' · Abschnitt fertig')).to_be_visible()
            expect(frame.get_by_text(label,exact=True)).to_be_visible()
            if j<2:btn(frame,'Mein Urteil ansehen').tap()
    assert frame.locator('body').evaluate('()=>storageWrites')==[]
    if scorm:assert p.evaluate('calls')==[['LMSInitialize','']]
    p.reload()
    shell=p.frame(name='sco') if scorm else p.main_frame
    shell.locator('#zweiter-tag').tap()
    frame=shell.frame_locator('iframe[title="Dienstag, 08.12.2026"]')
    action('recovery').tap();btn(frame,level).tap();btn(frame,person).tap()
    if n==3:shot(p,engine+'-Wiedereinstieg')
    # A true reload starts at the chosen section with an original source and no filled answer.
    for j in [1,0]:
        btn(frame,sections[j]).tap()
        expect(frame.locator('.eyebrow')).to_have_text(sections[j]+' · '+level)
        expect(frame.locator('aside')).to_contain_text(case['message'][tasks[j]['lines'][0]-1])
        expect(btn(frame,'Weiter')).to_be_hidden()
        if j:
            action('recovery').tap()
            btn(frame,person).tap()
    if scorm:
        p.locator('iframe').evaluate("e=>e.src='about:blank'")
        p.wait_for_function('calls.length===2')
        assert p.evaluate('calls')==[['LMSInitialize',''],['LMSFinish','']]
    assert not errors and not requests,(errors,requests)
    context.close()
    return dict(browser=engine,version=browser.version,person=person,niveau=level,format='SCORM' if scorm else 'HTML',
                viewport=[w,h],schrift_prozent=font,aufgaben=len(tasks),hilfen_je_aufgabe=5,
                urteile=task['options'],wiedereinstieg=sections,externe_anfragen=requests,skriptfehler=errors)


def main():
    check_content()
    QA.mkdir(parents=True,exist_ok=True)
    runs=[]
    with TemporaryDirectory() as td:
        temp=Path(td)
        before=protect(temp)
        with ZipFile(B/'Fallakte-SCORM12.zip') as zipfile:
            assert zipfile.testzip() is None and zipfile.read('index.html')==(B/'Fallakte.html').read_bytes()
            zipfile.extractall(temp/'sco')
        (temp/'sco/host.html').write_text(HOST)
        with host(temp/'sco') as url,sync_playwright() as pw:
            for engine in ('chromium','webkit'):
                browser=getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE'))
                for pi,person in enumerate(BANK['cases']):
                    for li,level in enumerate(BANK['levels']):
                        runs.append(exercise(browser,engine,person,level,4*pi+li,url))
                        print(engine,person,level,flush=True)
                browser.close()
    report=dict(referenz=REVIEWED,version_a_sha256=before,html_sha256=digest((B/'Fallakte.html').read_bytes()),
                scorm_sha256=digest((B/'Fallakte-SCORM12.zip').read_bytes()),bank_sha256=digest((OUT/'Aufgabenbank.json').read_bytes()),
                durchlaeufe=runs,bilder={f.name:digest(f.read_bytes()) for f in sorted(QA.glob('*.jpg'))})
    (QA/'Nachrichten.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    main()
