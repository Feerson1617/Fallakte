"""Operate the eight new sections through the actual B deliveries in two engines."""
import base64
import json
import os
import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from playwright.sync_api import expect, sync_playwright
from bestandsschutz import archive, build, digest
from tagesauswahl import HOST, host
from grundweg import measure_route

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'build/08-12'
QA = OUT/'Abnahme'
BANK = json.loads((OUT/'Aufgabenbank.json').read_text())
REVIEWED = '66c66ed1548c3baa50d01386fe6b400ae23e714b'
PHOTOS = {}
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
    assert digest((ROOT/'module/08-12/nachrichten.json').read_bytes())=='2744d3335774ba496c52be34e19dba12b3cc2bee5d49cd3de6be4a3d33288742'
    assert all(word not in json.dumps(BANK,ensure_ascii=False).lower() for word in (
        'bewertungskompetenz','bewertungskriterium','argumentationsqualität','kriteriengeleitet'))
    return digest((ref/'dist/Version-A/Fallakte.html').read_bytes())


def check_content():
    # Expectation from the correction brief, independent of the authoring module.
    reference = {
        'Mutter': ([1,2,3,5], 'Die Gebärmutter zieht sich zusammen. Gewebe wird ausgestoßen.',
                   'Sie bietet Hilfe mit dem Kind an. Laura möchte erst beide Wege kennen.'),
        'Freundin': ([1,2,3,4], 'Medikamente wirken ohne Operation. Beim Ausstoßen von Gewebe blutet es.',
                     'Die Mutter setzt auf Familienhilfe und rät zum Fortsetzen. Die Freundin denkt an die Zukunft und rät zum Abbruch.'),
        'Großmutter': ([1,2,3,4], 'Nach der Einnistung wächst der Embryo in der Gebärmutter weiter.',
                       'Sie bleibt bei Laura. Laura kann selbst entscheiden.'),
        'Vater': ([1,2,3,4], 'Sie informiert. Für die Beratungsregelung sind eine anerkannte Stelle und mindestens drei Tage Abstand vorgeschrieben.',
                  'Sie kann sich informieren und danach selbst entscheiden.'),
    }
    document=(OUT/'Fallakte.html').read_text()
    raw=re.search(r'<script type="application/json" id="material">(.*?)</script>',document,re.S)[1]
    assert json.loads(raw)==BANK
    assert not any(old in document.lower() for old in ('video','weder blutungen noch schmerzen','verbessert den satz','ein feld kann fehlen','falsche behauptung der freundin'))
    for phrase in ['Wähle dein Urteil','Welcher Beleg wiegt','Was zählt für Laura mehr','Wäge ab:', 'Suche für „']:
        assert phrase not in document, phrase
    original=json.loads((ROOT/'module/08-12/nachrichten.json').read_text())
    assert BANK['laura']==original['laura']
    for person,case in BANK['cases'].items():
        assert case['message']==original['nachrichten'][person]
        assert case['sections']==[person+' 1 – Argumenten-Check',person+' 2 – Nachricht prüfen']
        mapping, fact, link=reference[person]
        for level,tasks in case['levels'].items():
            assert list(dict.fromkeys(t['heading'] for t in tasks))==['Argumenten-Check',*BANK['questions']]
            assert [(f['name'],f['line']) for f in tasks[0]['fields']]==list(zip(('Fakt','Wert','Norm','Folgerung'),mapping))
            for f in tasks[0]['fields']:
                valid={o['line'] for o in f['options'] if o['correct']}
                expected={f['line']}
                if person=='Vater' and f['name']=='Fakt':
                    if level in ('MSA','AHR'): expected.add(3)
                    else: assert 3 not in [o['line'] for o in f['options']]
                assert valid==expected and all(o['feedback'] for o in f['options'])
            checks=tasks[1:-1]
            solutions=[next(o['label'] for o in t['options'] if o['correct']) for t in checks]
            assert solutions[0]==fact and link in solutions
            if person=='Freundin':
                assert checks[0]['mother']==[1] and any(3 in t['mother'] for t in checks)
            assert len(tasks)==4 and [t['heading'] for t in tasks[1:]]==BANK['questions']
            assert tasks[-1]['options']==['Sie hilft viel.','Sie hilft zum Teil.','Sie hilft wenig.']
            assert bool(tasks[-1]['counter'])==(level=='AHR')
            assert 'results' not in tasks[-1]
            assert all(o['citation'] for o in checks[0]['options'])
            depth=checks[1].get('depth')
            assert bool(depth)==(level in ('MSA','AHR'))
            if person=='Freundin' and level=='AHR':
                assert depth['mother']==[3,5] and 'zugleich' in depth['prompt']
            if person=='Vater' and depth:
                assert any('Wortlaut ist prüfbar' in o['label'] and o['correct'] for o in depth['options'])
            sets=[t['hints'] for t in tasks[1:]]+[f['hints'] for f in tasks[0]['fields']]
            if depth: sets.append(depth['hints'])
            assert all(len(h)==len(set(h))==5 for h in sets)
            assert all(f"Zeile {f['line']}" in f['hints'][4] for f in tasks[0]['fields'])
            for t in checks:
                assert sum(o['correct'] for o in t['options'])==1
                assert all(1<=n<=len(case['message']) for n in t['lines'])
                assert all(1<=n<=len(BANK['laura']) for n in t['wishes'])
                assert all(1<=n<=len(BANK['cases']['Mutter']['message']) for n in t['mother'])
                if t['card']:
                    key,lines=t['card']
                    assert all(1<=n<=len(BANK['cards'][key]['lines']) for n in lines)



def btn(frame,label):
    return frame.get_by_role('button',name=label,exact=True)


def layout(frame):
    result = frame.locator('body').evaluate("""body=>({
      overflow: document.documentElement.scrollWidth-innerWidth,
      small: [...body.querySelectorAll('button,summary,select')].filter(e=>e.getClientRects().length && (e.getBoundingClientRect().height < 43.9 || e.getBoundingClientRect().width < 43.9)).map(e=>e.textContent)
    })""")
    assert result['overflow']<=1 and not result['small'], result
    clipped=frame.locator('select:visible').evaluate_all("""els=>els.filter(el=>{
      const ctx=document.createElement('canvas').getContext('2d');
      ctx.font=getComputedStyle(el).font;
      return [...el.options].some(o=>Math.ceil(ctx.measureText(o.text).width)+24>el.clientWidth);
    }).map(el=>el.getAttribute('aria-label'))""")
    assert not clipped, ('Abgeschnittene Zeilenauswahl',clipped)


def shot(page,name):
    path=QA/(name+'.jpg')
    page.screenshot(path=path,type='jpeg',quality=73,animations='disabled')
    PHOTOS[path.name]=digest(path.read_bytes())


def inspect_task(frame,task,level):
    expect(frame.get_by_role('heading',name=task['heading'],exact=True)).to_be_visible()
    article = frame.locator('article')
    expect(article.get_by_text(task['prompt'],exact=True)).to_be_visible()
    # A real learner can go straight to 5, then back to any level without submitting.
    if task['kind']=='map':
        topics={f['name']:f['hints'] for f in task['fields']}
    else:
        topics={'Grundfrage':task['hints']}
    btn(article,'Hilfe').tap()
    for name,hints in topics.items():
        if len(topics)>1:article.get_by_label('Hilfe zu',exact=True).select_option(name)
        for index in [4,0,1,2,3,4]:
            btn(article,f'Hilfe {index+1} – '+BANK['helps'][index]).dispatch_event('click')
            expect(article.locator('.help-list ~ p').first).to_have_text(hints[index])
    btn(article,'Hilfe schließen').dispatch_event('click')
    if task['kind']=='judgment':
        return
    if task['kind']=='map':
        expect(btn(article,'Weiter')).to_be_hidden()
        for field in task['fields']:
            select=article.get_by_role('combobox',name=field['name'],exact=True)
            feedback=select.locator('xpath=../..').get_by_role('status')
            for option in field['options']:
                select.select_option(str(option['line']))
                expect(feedback).to_contain_text(option['feedback'])
                if not option['correct']: expect(btn(article,'Weiter')).to_be_hidden()
            select.select_option(str(field['line']))
        expect(btn(article,'Weiter')).to_be_visible()
        for field in task['fields']:
            for alternative in field['options']:
                if alternative['correct'] and alternative['line']!=field['line']:
                    select=article.get_by_role('combobox',name=field['name'],exact=True)
                    select.select_option(str(alternative['line']))
                    expect(btn(article,'Weiter')).to_be_visible()
                    select.select_option(str(field['line']))
        return
    for part,q in enumerate([task]+([task['depth']] if task.get('depth') else [])):
        if part:
            btn(article,'Hilfe').tap()
            for index in [4,0,1,2,3,4]:
                btn(article,f'Hilfe {index+1} – '+BANK['helps'][index]).dispatch_event('click')
                expect(article.locator('.help-list ~ p')).to_have_text(q['hints'][index])
            btn(article,'Hilfe schließen').tap()
        options=article.locator('.options').nth(part).get_by_role('button')
        status=article.get_by_role('status',include_hidden=True).nth(part)
        for pos,option in enumerate(q['options']):
            if not option['correct']:
                options.nth(pos).dispatch_event('click')
                expect(status).to_contain_text(option['feedback'])
                expect(btn(article,'Weiter')).to_be_hidden()
        correct=next(i for i,o in enumerate(q['options']) if o['correct'])
        options.nth(correct).tap()
        expect(status).to_contain_text(q['options'][correct]['feedback'])
    expect(btn(article,'Weiter')).to_be_visible()


def exercise(browser,engine,person,level,n,base):
    scorm=(n+(engine=='webkit'))%2==0
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
        if n==1 and i==0:
            shot(p,engine+'-Argumenten-Check')
        inspect_task(frame,task,level)
        layout(frame)
        if person=='Freundin' and task.get('mother'):
            for line in task['mother']:
                expect(frame.locator('aside').get_by_text(BANK['cases']['Mutter']['message'][line-1],exact=True).first).to_be_visible()
            if n==5 and task['heading']==BANK['questions'][1]:shot(p,engine+'-Regeln-und-Rat')
        if i==0:
            if n==1:shot(p,engine+'-Vier-Zuordnungen')
            action('overview').tap();btn(frame,sections[0]).tap()
            for field in task['fields']:
                expect(frame.get_by_role('combobox',name=field['name'],exact=True)).to_have_value(str(field['line']))
            btn(frame,'Zeile für Zeile lesen').tap()
            btn(frame,'Nächster Teil').tap()
            expect(frame.locator('aside .lines').first).to_contain_text(case['message'][1])
            btn(frame,'Lesen beenden').tap()
        if i==1:
            # Keep the answer and opened hint through card, shell and same-tier section changes.
            btn(frame,'Hilfe').tap()
            btn(frame,'Hilfe 3 – '+BANK['helps'][2]).tap()
            if n==1:
                btn(frame,'Ganze Fachkarte').tap()
                expect(frame.locator('details[open]')).to_contain_text('Manchmal ist eine weitere Behandlung nötig.')
                shot(p,engine+'-Fachkarte')
                btn(frame,'Zurück').tap()
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
        key,ids=task['card']
        facts=[BANK['cards'][key]['lines'][n-1] for n in ids]
        goals=[BANK['laura'][n-1] for n in task['goals']]
        expect(btn(article,'Abschnitt beenden')).to_be_hidden()
        expect(btn(article,task['options'][0])).to_be_hidden()
        expect(article.get_by_text(task['hints'][4],exact=True)).to_be_hidden()
        if n==7:
            btn(frame,'Hilfe').tap();btn(frame,'Hilfe 5 – So geht es.').tap()
            shot(p,engine+'-Beispielurteil');btn(frame,'Hilfe schließen').tap()
        for j,label in enumerate(task['options']):
            fact=facts[j%2];goal=goals[j%2]
            btn(article,fact).tap()
            btn(article,goal).tap()
            btn(article,label).tap()
            if level=='Förder':
                btn(article,task['links'][j%2]).tap()
            elif j==0:
                btn(frame,'Abschnitt beenden').tap()
                expect(article.get_by_role('status')).to_contain_text('deinen Grund')
                reason=fact+' Laura sagt: „'+goal+'“ '+task['links'][0]
                article.get_by_label('Dein Grund').fill(reason)
                action('overview').tap()
                other=next(l for l in BANK['levels'] if l!=level)
                btn(frame,other).tap();btn(frame,sections[1]).tap()
                expect(frame.get_by_role('heading',name=BANK['questions'][2])).to_be_visible()
                action('overview').tap();btn(frame,level).tap();btn(frame,'Zur offenen Stelle').tap()
                expect(article.get_by_label('Dein Grund')).to_have_value(reason)
                article.get_by_text('Grund selbst prüfen',exact=True).tap()
                expect(article.get_by_text(task['selfCheck'],exact=True)).to_be_visible()
            elif j==1:
                article.get_by_label('Dein Grund').fill('')
                btn(article,'Ich habe meinen Grund gesagt.').tap()
            if task['counter']:expect(article.get_by_text(task['counter'],exact=True)).to_be_visible()
            if n==5 and j==0:shot(p,engine+'-Urteil')
            btn(frame,'Abschnitt beenden').tap()
            expect(frame.get_by_role('heading',name=person+' · Abschnitt fertig')).to_be_visible()
            expect(frame.get_by_text(label,exact=True)).to_be_visible()
            expect(frame.get_by_text(fact,exact=True)).to_be_visible()
            expect(frame.get_by_text('Laura: „'+goal+'“',exact=True)).to_be_visible()
            if j<2:btn(frame,'Mein Urteil ansehen').tap()
    assert frame.locator('body').evaluate('()=>storageWrites')==[]
    if scorm:assert p.evaluate('calls')==[['LMSInitialize','']]
    p.reload()
    shell=p.frame(name='sco') if scorm else p.main_frame
    shell.locator('#zweiter-tag').tap()
    frame=shell.frame_locator('iframe[title="Dienstag, 08.12.2026"]')
    action('recovery').tap();btn(frame,level).tap();btn(frame,person).tap()
    for index in [3,2,1,0]:
        if index:
            btn(frame,sections[1]).tap()
            if n==3 and index==3:shot(p,engine+'-Wiedereinstieg')
            btn(frame,f'{index}. '+BANK['questions'][index-1]).tap()
            expect(frame.locator('.eyebrow')).to_have_text(sections[1]+f' · Frage {index} von 3')
            expect(frame.get_by_role('heading',name=BANK['questions'][index-1],exact=True)).to_be_visible()
            if index==3:
                expect(btn(frame,facts[0])).to_be_visible()
                expect(btn(frame,'Abschnitt beenden')).to_be_hidden()
                btn(frame,'Ganze Fachkarte').tap();btn(frame,'Zurück').tap()
            else:
                expect(btn(frame,'Weiter')).to_be_hidden()
                expect(frame.locator('aside')).to_contain_text(case['message'][tasks[index]['lines'][0]-1])
        else:
            btn(frame,sections[0]).tap()
            expect(frame.get_by_role('combobox',name='Norm',exact=True)).to_have_value('')
        if index:
            action('recovery').tap();btn(frame,person).tap()
    if scorm:
        p.locator('iframe').evaluate("e=>e.src='about:blank'")
        p.wait_for_function('calls.length===2')
        assert p.evaluate('calls')==[['LMSInitialize',''],['LMSFinish','']]
    assert not errors and not requests,(errors,requests)
    context.close()
    return dict(browser=engine,version=browser.version,person=person,niveau=level,format='SCORM' if scorm else 'HTML',
                viewport=[w,h],schrift_prozent=font,aufgaben=len(tasks),hilfen_je_aufgabe=5,
                urteile=task['options'],wiedereinstieg=sections,externe_anfragen=requests,skriptfehler=errors)


def standalone_zoom(browser,engine):
    context=browser.new_context(viewport={'width':390,'height':650},has_touch=True,is_mobile=True)
    page=context.new_page()
    page.goto((OUT/'Fallakte.html').as_uri())
    page.locator('html').evaluate("el=>el.style.fontSize='200%'")
    # Exercise the fallback bar, long source words and every direct entry at this width.
    for case in BANK['cases'].values():
        for section in case['sections']:
            layout(page)
            btn(page,section).tap()
            btn(page,'Hilfe').tap()
            btn(page,'Hilfe 5 – So geht es.').tap()
            layout(page)
            page.locator('aside summary').first.tap()
            layout(page)
            btn(page,'Nachrichten').tap()
    context.close()
    return dict(browser=engine,viewport=[390,650],schrift_prozent=200,abschnitte=8)


def main():
    check_content()
    QA.mkdir(parents=True,exist_ok=True)
    runs=[]
    routes=[]
    small=[]
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
                small.append(standalone_zoom(browser,engine))
                for pi,person in enumerate(BANK['cases']):
                    for li,level in enumerate(BANK['levels']):
                        runs.append(exercise(browser,engine,person,level,4*pi+li,url))
                        print(engine,person,level,flush=True)
                for first,second in [(l,'') for l in BANK['levels']]+[('Förder','AHR'),('ESA','MSA')]:
                    routes.append(measure_route(browser,engine,B,BANK,first,second,shot))
                browser.close()
    report=dict(commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),referenz=REVIEWED,version_a_sha256=before,html_sha256=digest((B/'Fallakte.html').read_bytes()),
                scorm_sha256=digest((B/'Fallakte-SCORM12.zip').read_bytes()),bank_sha256=digest((OUT/'Aufgabenbank.json').read_bytes()),
                durchlaeufe=runs,grundwege=routes,kleinfenster=small,bilder=PHOTOS)
    (QA/'Nachrichten.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    main()
