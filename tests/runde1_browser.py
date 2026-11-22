"""Pupil-side acceptance of the actual offline prototype. Run after the round-one build."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

from playwright.sync_api import expect, sync_playwright

from runde1_orakel import correct_reason

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT/'dist/Runde-1'
HTML = DIST/'Fallakte.html'
QA = ROOT/'build/runde1/qa'
LEVELS = ('Foerder', 'ESA', 'MSA', 'AHR')
STRATEGIES = ('K','P','Cu','H','K+P','K+Cu','K+H')
CODES = {'L01':'B','L02':'C','L03':'A','L04':'B','L05':'C'}
SHOTS = {}
TITLES = ('Laura 1 – Latexallergie','Laura 2 – Zwei Schutzziele','Laura 3 – Hormone und Alltag',
          'Laura 4 – Schmerzen und Einlage','Laura 5 – Mein Schlussrat')
DIAGNOSTIC = {
    'L01':{'A':('K','material'),'C':('K','material')},
    'L02':{'A':('P','sti'),'B':('Cu','sti')},
    'L03':{'B':('H','alltag'),'C':('P','eignung')},
    'L04':{'A':('Cu','schmerzen'),'C':('H','einlage')},
    'L05':{'A':('P','sti'),'B':('K','sti')},
}


def expected_references(stage, strategy):
    """The pupil needs the chosen components, with the mechanism relevant at this stage."""
    if stage in ('L03','L04','L05'):
        method=strategy.split('+')[-1]
        section={'L03':'alltag','L04':'schmerzen','L05':{
            'K':'sti','P':'alltag','Cu':'schmerzen','H':'schmerzen'}[method]}[stage]
        refs=[(method,section)]
        if '+' in strategy:refs.append(('K','sti'))
        if stage in ('L04','L05') and method in ('Cu','H'):refs.append((method,'einlage'))
        return refs
    condom_section = 'material' if stage == 'L01' else 'sti'
    if '+' in strategy:
        return [(strategy.split('+')[1], 'wirkung'), ('K', condom_section)]
    if strategy == 'K':
        return ([('K', 'material')] if stage == 'L01' else [('K', 'sti'), ('K', 'wirkung')])
    return [(strategy, 'wirkung' if stage == 'L01' else 'sti')]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def shot(page, name):
    path = QA/(name+'.jpg')
    page.screenshot(path=path,type='jpeg',quality=74,animations='disabled')
    SHOTS[path.name] = sha(path)


def text_log(page, kind=None):
    selector = '#beratung-verlauf .chat-entry' + (f'[data-kind="{kind}"]' if kind else '')
    return page.locator(selector+' > p').all_text_contents()


def start(page, tier):
    page.goto(HTML.as_uri())
    expect(page.locator('#start')).to_be_visible()
    expect(page.locator('#start [aria-pressed=true]')).to_have_count(0)
    expect(page.locator('#weiterarbeiten')).to_be_hidden()
    expect(page.locator('#neu')).to_be_disabled()
    page.locator('#level-'+tier).tap()
    page.locator('#neu').tap()
    expect(page.locator('#beratung-stage')).to_have_attribute('data-stage','L01')
    no_send(page)


def no_send(page):
    send=page.locator('#nachricht-senden')
    assert not send.is_visible() or send.is_disabled()


def choose(page, strategy):
    if not page.locator('#beratung-arbeit[data-step=wahl]').is_visible():
        page.locator('#strategie-bearbeiten:visible, #strategie-neu-waehlen:visible').tap()
    control = page.locator(f'[data-strategy="{strategy}"]')
    if not control.is_visible():
        page.locator('#weitere-strategien summary').tap()
    control.tap()
    expect(page.locator('#aktueller-rat')).to_have_attribute('data-about-strategy',strategy)
    expect(page.locator('button[data-strategy]:visible')).to_have_count(0)


def dialogue_guard(page):
    """A DOM enable alone must never turn an unvalidated draft into a real send."""
    before = text_log(page)
    page.locator('#nachricht-senden').evaluate("""button=>{
        const was=button.disabled;
        button.disabled=false;
        button.click();
        if(button.isConnected)button.disabled=was;
    }""")
    assert before == text_log(page), 'Versand ohne aktuelle Fachprüfung'


def back_from_material(page):
    page.locator('#material-zurueck').tap()
    expect(page.locator('#material-dialog')).not_to_be_visible()


def marked_card(page):
    d=page.locator('#material-dialog[open]')
    expect(d).to_have_attribute('data-view','card')
    selected=d.locator('[data-section-id][data-target=true]')
    expect(selected).to_have_count(1)
    expect(d.locator('[data-section-id]:visible')).to_have_count(1)
    expect(page.locator('#material-ganze-karte')).to_be_visible()
    section=selected.get_attribute('data-section-id')
    assert section==d.get_attribute('data-section') and selected.inner_text().strip()
    expect(selected.locator('h3')).to_be_focused()
    return d.get_attribute('data-method'),section


def open_wrong_card(page, ref):
    before=text_log(page)
    page.locator('#passende-karte').tap()
    method,section=marked_card(page)
    assert (method,section)==(ref['method'],ref['section']), (method,section,ref)
    back_from_material(page)
    assert before==text_log(page)
    return [method,section]


def active_material(page, bank, tier, stage, strategy):
    task = bank['stages'][stage]['levels'][tier]
    context = task['strategies'][strategy]
    source = page.locator('.abschnittshinweis')
    expect(source).to_be_visible()
    expect(source).to_have_text(context['evidence'])
    txt = source.inner_text()
    methods = strategy.split('+')
    named = {'K':r'Kondom','P':r'Pille','Cu':r'Kupfer','H':r'Hormonspirale|Schleim|Gestagen'}
    for method in methods:
        assert re.search(named[method],txt,re.I),(stage,tier,strategy,txt)
    if 'K' not in methods:
        assert not re.search(r'(?:Kondomkarte|(?:Karte|Abschnitt) [„»]?Kondom)',txt,re.I),txt
    references = expected_references(stage,strategy)
    controls = page.locator('.beratung-tools button[id^=passende-karte]')
    expect(controls).to_have_count(len(references))
    history = text_log(page)
    for i, (method, section) in enumerate(references):
        ref = controls.nth(i)
        card = bank['cards'][method]
        passage = card['sections'][section]
        expect(ref).to_have_attribute('data-method',method)
        expect(ref).to_have_attribute('data-section',section)
        expect(ref).to_have_accessible_name(re.compile(re.escape(card['title']),re.I))
        expect(ref).to_have_accessible_name(re.compile(re.escape(passage['title']),re.I))
        ref.tap()
        assert marked_card(page) == (method,section)
        expect(page.locator('#material-titel')).to_have_text(card['title'])
        target = page.locator('#material-dialog [data-target=true]')
        expect(target.locator('h3')).to_have_text(passage['title'])
        visible_text=passage['shortText'] if tier in LEVELS[:2] else passage['text']
        expect(target.locator('p')).to_have_text(visible_text)
        if strategy=='Cu':
            page.locator('#material-ganze-karte').tap()
            full=page.locator('#material-dialog')
            expect(full.locator('[data-section-id]:visible')).to_have_count(len(card['sections']))
            for key, entry in card['sections'].items():
                expect(full.locator(f'[data-section-id="{key}"] p')).to_have_text(entry['text'])
            page.locator('#material-zurueck').tap()
            expect(page.locator('#material-ganze-karte')).to_be_focused()
        back_from_material(page)
        expect(ref).to_be_focused()
    assert text_log(page)==history
    return {'impuls':txt,'ziele':references}


def pupil_view(page, stage):
    """Look at the visible pupil view, without reading detached/hidden teacher material."""
    expect(page.locator('#lokale-navigation').get_by_text(re.compile('Sicherung|Lehrkraft'))).to_have_count(0)
    expect(page.locator('#lehrkraft')).not_to_have_attribute('open','')
    expect(page.locator('#sicherung-oeffnen')).not_to_be_visible()
    text=page.locator('#beratung').inner_text()
    if stage < 'L03':
        assert not re.search(r'(?:mein|ihr|Lauras) Alltag ist unregelmäßig|(?:eine|meine) Freundin hat',text,re.I),text
    if stage < 'L04':
        assert not re.search(r'(?:ich habe|Laura hat) starke Regelschmerzen|'
                             r'(?:das Einsetzen einer Spirale|die Einlage) macht (?:mir|Laura) Sorgen',text,re.I),text
    if stage == 'L01':
        assert not re.search(r'(?:ich möchte|Laura möchte) (?:auch|zusätzlich).{0,45}(?:STI|Infektion)',text,re.I),text


def introductory_clue(page, tier, stage, data):
    source = page.locator('.abschnittshinweis')
    expect(source).to_have_text(data['evidence'])
    pupil_view(page,stage)
    if stage != 'L01':
        return
    clue = source.inner_text()
    if tier == 'Foerder':
        assert re.search(r'(latexfrei|ohne Latex)',clue,re.I) and re.search(r'Sperm|Barriere',clue,re.I),clue
        return
    assert re.search(r'[?]|prüf|vergleich|untersuch|erkund',clue,re.I),clue
    if tier == 'ESA':
        assert re.search('Karte|Material',clue,re.I),clue
    assert not re.search(r'(?:hält|halten|fängt|fangen).{0,12}Sperm|bildet.{0,15}Barriere|'
                         r'(?:geeignet|wirksam).{0,25}(?:latexfrei|ohne Latex)',clue,re.I),clue
    more = page.locator('#weitere-strategien summary')
    if more.is_visible(): more.tap()
    buttons = page.locator('#beratung button[data-strategy]:visible')
    names = buttons.all_inner_texts()
    assert len(names)==7 and not re.search(r'latexfrei|ohne Latex|synthetisch',' '.join(names),re.I),names
    if more.is_visible(): more.tap()


def paper_route(page, bank, tier, stage, screenshot=None):
    task = bank['stages'][stage]['levels'][tier]
    field = page.locator('.fachcheck')
    fallback = field.locator('details#papier-ersatz')
    expect(field.get_by_text(task['paperPrompt'],exact=True)).to_be_visible()
    expect(page.locator('#pruefcode')).to_have_accessible_name(re.compile(r'Prüfcode.*Laufzettel'))
    assert TITLES[int(stage[-1])-1] in task['paperPrompt']
    expect(fallback.locator('summary')).to_have_text(re.compile(r'Laufzettel nicht zur Hand.+Aufgabe',re.I))
    expect(fallback).not_to_have_attribute('open','')
    anchors = bank['stages'][stage]['anchors']
    for letter, statement in anchors.items():
        expect(field.get_by_text(letter+' · '+statement,exact=True)).not_to_be_visible()
    if screenshot:shot(page,screenshot+'-Papierweg-MSA')
    before = text_log(page)
    fallback.locator('summary').tap()
    expect(fallback.get_by_text(task['task'],exact=True)).to_be_visible()
    expect(fallback.get_by_text(task['returnPrompt'],exact=True)).to_be_visible()
    expect(fallback.get_by_text(bank['paperFallbackInstruction'],exact=True)).to_be_visible()
    for letter, statement in anchors.items():
        line=fallback.get_by_text(letter+' · '+statement,exact=True)
        expect(line).to_be_visible()
        assert not line.evaluate("el=>Boolean(el.closest('[aria-selected=true], [aria-current=true], mark'))")
    expect(page.locator('#pruefcode')).to_have_value('')
    assert not re.search(r'(?:korrekt|richtig|Lösung|Prüfcode)(?:e[rn]?)? (?:ist |lautet )?[:=] ?[ABC]\b',
                         fallback.inner_text(),re.I)
    if screenshot:shot(page,screenshot+'-Papierersatz-MSA')
    fallback.locator('summary').tap()
    assert text_log(page)==before
    no_send(page)


def exercise_check(page,tier,stage,strategy,context):
    send=page.locator('#nachricht-senden')
    status=page.locator('#fachmeldung')
    history=text_log(page)
    expect(send).to_be_disabled()
    results=[]
    if tier in LEVELS[:2]:
        expect(page.locator('#pruefcode')).to_have_count(0)
        options=page.locator('#begruendungen button[data-option]')
        count=options.count()
        assert count in ((2,) if tier=='Foerder' else (2,3))
        options_by_id={v['id']:v for v in context['options']}
        labels=options.all_text_contents()
        right=correct_reason(tier,stage,strategy,labels)
        good=None
        for index,label in enumerate(labels):
            option=options.nth(index)
            author=options_by_id[option.get_attribute('data-option')]
            assert label.strip()==author['text'] and author['correct']==(index==right),(stage,strategy,label)
            if index==right:
                good=option
                continue
            option.tap()
            expect(status).to_have_attribute('data-type','A')
            expect(status).to_be_visible()
            expect(status).to_have_text(author['feedback'])
            expect(send).to_be_disabled()
            ref=open_wrong_card(page,author['card'])
            results.append(dict(antwort=label,erwartet='A',quelle=ref))
        assert good is not None
        good.tap()
        results.append(dict(antwort=labels[right],erwartet='B' if stage!='L01' and strategy in ('P','Cu','H') else 'C'))
    else:
        expect(page.locator('#begruendungen button[data-option]')).to_have_count(0)
        code=page.locator('#pruefcode')
        check=page.locator('#fachcheck-pruefen')
        expect(code).to_be_visible()
        # All other single-letter answers, a blank and a multi-letter input must fail.
        wrong=['',*sorted(set('ABC')-{CODES[stage]}),'xx']
        for value in wrong:
            code.fill(value)
            method, section = expected_references(stage,strategy)[0]
            primary = page.locator('#passende-karte')
            expect(primary).to_have_attribute('data-method',method)
            expect(primary).to_have_attribute('data-section',section)
            check.tap()
            expect(send).to_be_disabled()
            expect(status).to_be_visible()
            assert status.inner_text().strip()
            expect(status).to_have_attribute('data-type','A')
            opened=None
            if value in ('A','B','C'):
                method,section=DIAGNOSTIC[stage][value]
                ref={'method':method,'section':section}
                opened=open_wrong_card(page,ref)
                expect(code).to_have_value(value)
            results.append(dict(eingabe=value,erwartet='A',quelle=opened))
        code.fill(' '+CODES[stage].lower()+' ')
        check.tap()
        results.append(dict(eingabe=' '+CODES[stage].lower()+' ',erwartet='B' if stage!='L01' and strategy in ('P','Cu','H') else 'C'))
    assert text_log(page)==history, 'Fachprüfung schickt automatisch Nachrichten'
    incomplete=stage!='L01' and strategy in ('P','Cu','H')
    expect(status).to_have_attribute('data-type','B' if incomplete else 'C')
    if incomplete:
        expect(send).to_be_disabled()
        expect(status).to_have_text(context['feedback'])
        assert re.search(r'Infektion|STI|Schutzlücke|Ziel.{0,45}offen|Anliegen',status.inner_text(),re.I),status.inner_text()
        if tier in LEVELS[2:]:
            assert not re.search(r'Kondom',status.inner_text(),re.I),status.inner_text()
        results[-1]['rueckmeldung']=status.inner_text()
        results[-1]['quelle']=open_wrong_card(page,{'method':strategy,'section':'sti'})
    else:
        expect(send).to_be_enabled()
    return results


def materials(page,tier,stage,strategy,context,screenshot=None):
    """Walk the entire optional chain; it may inform a choice, never make one."""
    before=text_log(page)
    selected=page.locator(f'[data-strategy="{strategy}"]')
    page.locator('#hilfe').tap()
    d=page.locator('#material-dialog[open]')
    expect(d).to_have_attribute('data-view','help')
    hints=[]
    for i,expected in enumerate(context['hints'],1):
        hint=d.locator('#hilfe-text')
        expect(hint).to_have_attribute('data-depth',str(i))
        expect(hint).to_have_text(expected)
        hints.append(hint.inner_text())
        if i<5:d.locator('#hilfe-weiter').tap()
    assert len(hints)==5
    expect(d.locator('#hilfe-weiter')).not_to_be_visible()
    if screenshot:shot(page,screenshot+'-Hilfe-5')
    for index,extra in enumerate(context.get('extraCards',[]),1):
        d.locator(f'#hilfe-karte-{index}').tap()
        assert marked_card(page)==(extra['method'],extra['section'])
        page.locator('#material-zurueck').tap()
        expect(d).to_have_attribute('data-view','help')
    if stage=='L05' and not strategy:
        expect(d.locator('#hilfe-karte')).to_have_count(0)
        d.locator('#hilfe-kartenauswahl').tap()
        expect(d).to_have_attribute('data-view','cards')
        expect(d.locator('button[id^=material-karte-]')).to_have_count(4)
        d.locator('#material-karte-Cu').tap()
        expect(d).to_have_attribute('data-method','Cu')
        expect(d.locator('[data-section-id]:visible')).to_have_count(5)
        page.locator('#material-zurueck').tap()
        expect(d).to_have_attribute('data-view','cards')
        page.locator('#material-zurueck').tap()
        ref=[]
    else:
        d.locator('#hilfe-karte').tap()
        ref=marked_card(page)
        assert ref==(context['card']['method'],context['card']['section']),(tier,stage,strategy,ref)
        if screenshot:shot(page,screenshot+'-Markierte-Kartenstelle')
        page.locator('#material-zurueck').tap()
    expect(d).to_have_attribute('data-view','help')
    back_from_material(page)
    if strategy:
        expect(page.locator('#aktueller-rat')).to_have_attribute('data-about-strategy',strategy)
    else:
        expect(page.locator('button[data-strategy][aria-pressed=true]')).to_have_count(0)
    expect(page.locator('#hilfe')).to_be_focused()
    assert text_log(page)==before
    return list(ref)


def send_once(page,stage):
    """A second event on the original element must be harmless even after a redraw."""
    before=len(text_log(page,'send'))
    before_reply=len(text_log(page,'reaction'))
    page.locator('#nachricht-senden').evaluate('b=>{b.click(); b.click()}')
    actual=text_log(page,'reaction')
    assert len(text_log(page,'send'))==before+1 and len(actual)==before_reply+1
    expect(page.locator('#beratung-stage')).to_have_attribute('data-stage',stage)
    return actual[-1]


def matrix(page,tier,strategy,bank,engine,stages=tuple(CODES)):
    start(page,tier)
    if tier in LEVELS[:2]:
        expected=['K','Cu'] if tier=='Foerder' else ['K','Cu','H']
        shown=page.locator('#beratung button[data-strategy]:visible').evaluate_all('els=>els.map(el=>el.dataset.strategy)')
        assert set(shown)==set(expected),(tier,shown)
    chapters=[]
    previous=None
    for index,stage in enumerate(stages):
        expect(page.locator('#beratung-stage')).to_have_attribute('data-stage',stage)
        expect(page.locator('#beratung-arbeit')).to_have_attribute('data-step','wahl')
        expect(page.locator('button[data-strategy][aria-pressed=true]')).to_have_count(0)
        expect(page.locator('.fachcheck:visible')).to_have_count(0)
        no_send(page)
        assert len(text_log(page,'reaction'))==index
        message=text_log(page,'opening')[-1]
        current_fact={'L01':'Latex','L02':'Infektion|STI','L03':'Freundin','L04':'Schmerz','L05':'Rat|raten'}[stage]
        assert re.search(current_fact,message,re.I),message
        assert page.locator(f'#beratung-verlauf [data-kind="opening"][data-stage="{stage}"]').is_visible()
        if previous:
            assert page.locator(f'[data-strategy="{previous}"]').is_visible(),'Bisherigen Rat erst suchen müssen'
            if tier in LEVELS[:2]:
                assert page.locator('#beratung button[data-strategy]:visible').count()<=3
        if stage=='L01' and tier=='ESA' and strategy=='K':shot(page,engine+'-Start-ESA')
        data=bank['stages'][stage]['levels'][tier]
        assert message==data['message']
        introductory_clue(page,tier,stage,data)
        if strategy=='K':
            materials(page,tier,stage,None,data['before'])
            questions(page,data['before'],ask=True)
            no_send(page)
        choose(page,strategy)
        expect(page.locator('#beratung-arbeit')).to_have_attribute('data-step','grund')
        expect(page.locator('#fachmeldung')).to_have_attribute('data-type','')
        expect(page.locator('#strategie-ergaenzen')).not_to_be_visible()
        actual_material=active_material(page,bank,tier,stage,strategy)
        if tier in LEVELS[2:]:
            snap=engine if (tier,stage,strategy)==('MSA','L01','Cu') else None
            paper_route(page,bank,tier,stage,snap)
        dialogue_guard(page)
        ctx=data['strategies'][strategy]
        offered=questions(page,ctx)
        assert dict(offered)=={q['id']:q['text'] for q in ctx['questions']}
        for _ in offered:
            questions(page,ctx,ask=True)
        expect(page.locator('#ask')).not_to_be_visible()
        example=engine+'-Foerder-Cu' if (tier,stage,strategy)==('Foerder','L01','Cu') else None
        source=materials(page,tier,stage,strategy,ctx,example)
        checks=exercise_check(page,tier,stage,strategy,ctx)
        original=strategy
        if stage!='L01' and strategy in ('P','Cu','H'):
            dialogue_guard(page)
            expect(page.locator('#beratung-arbeit')).to_have_attribute('data-step','korrektur')
            expect(page.locator('#aktueller-rat')).to_have_attribute('data-about-strategy',strategy)
            if stage=='L02' and strategy=='Cu' and tier!='AHR':shot(page,engine+'-B-Korrektur-'+tier)
            if tier in LEVELS[:2]:
                original=f'K+{strategy}'
                lower=page.locator('#strategie-ergaenzen')
                expect(lower).to_have_text(re.compile('Kondom',re.I))
                checks[-1]['korrekturweg']=lower.inner_text()
                lower.tap()
            else:
                expect(page.locator('#strategie-ergaenzen')).to_have_count(0)
                change=page.locator('#strategie-neu-waehlen')
                expect(change).to_be_visible()
                assert not re.search('Kondom|Pille|Spirale',change.inner_text(),re.I)
                checks[-1]['korrekturweg']=change.inner_text()
                change.tap()
                no_send(page)
                expect(page.locator(f'button[data-strategy="{strategy}"]')).to_have_attribute('aria-pressed','true')
                # A complete recommendation may keep, replace, or omit the initial component.
                original={'P':'K+H','Cu':'K','H':'K+H'}[strategy]
                choose(page,original)
            expect(page.locator('#aktueller-rat')).to_have_attribute('data-about-strategy',original)
            no_send(page)
            checks+=exercise_check(page,tier,stage,original,data['strategies'][original])
        expect(page.locator('#beratung-arbeit')).to_have_attribute('data-step','senden')
        expect(page.locator('#nachricht-senden')).to_be_visible()
        expect(page.locator('.fachcheck:visible')).to_have_count(0)
        reply=send_once(page,stage)
        previous=original
        expect(page.locator('#beratung-arbeit')).to_have_attribute('data-step','antwort')
        expect(page.locator('#beratung-reaktion')).to_be_visible()
        assert page.locator('html').evaluate('e=>e.scrollWidth<=innerWidth+1'),page.viewport_size
        assert bank['strategies'][original]['label'] in text_log(page,'send')[-1]
        if tier in LEVELS[:2]:assert checks[-1]['antwort'] in text_log(page,'send')[-1]
        assert data['strategies'][original]['reply'] in reply,(stage,original,reply)
        assert not re.search(r'(lehne.*Pille.*ab|Pille.*(?:will|möchte) ich nicht|[iI]ch (?:will|möchte) die Pille nicht|[Bb]egründet (?:bitte |eure))',reply),reply
        if stage<'L04':
            assert not re.search('ich habe.*Regelschmerzen',reply,re.I)
        if stage=='L03':
            assert re.search('Sex|regelmäßig|täglich|Tablette|Einnahme|jeden Tag',reply,re.I),reply
        if stage=='L04':
            if original=='K+Cu':assert re.search('schlimmer|verstärk',reply,re.I)
            if original=='K+H':assert re.search('nicht|offen|könnte',reply,re.I)
            if original=='K':assert re.search('Praxis|abklären|ärzt|untersuch',reply,re.I)
        if stage=='L05':
            assert not re.search('bestanden|volle Punkt|Begründung ist richtig',page.locator('#beratung-arbeit').inner_text(),re.I)
        scene={('L03','ESA','K+P'):'Alltag-Kombinationspille-ESA',
               ('L04','MSA','K+Cu'):'Schmerzen-Kupferspirale-MSA',
               ('L05','AHR','K+H'):'Schlussrat-AHR'}.get((stage,tier,strategy))
        if scene:shot(page,engine+'-'+scene)
        if tier=='Foerder' and strategy=='K' and stage=='L01':
            shot(page,engine+'-Foerder-L01-Gesendet')
        if index<len(stages)-1:
            page.locator('#beratung-weiter').tap()
        elif stage=='L05':
            expect(page.locator('#beratung-fertig')).to_be_visible()
            page.locator('#beratung-fertig').tap()
            expect(page.locator('#start')).to_be_visible()
        chapters.append(dict(stage=stage,strategy=strategy,status=ctx['status'],
                             versendete_strategie=original,kartenstelle=source,arbeitsmaterial=actual_material,
                             pruefversuche=checks,verfuegbare_fragen=offered,reaktion=reply))
    return dict(niveau=tier,strategy=strategy,chapters=chapters)


def questions(page, context, ask=False):
    if not page.locator('#ask').is_visible():
        assert not ask
        return []
    page.locator('#ask').tap()
    d=page.locator('#material-dialog[open]')
    expect(d).to_have_attribute('data-view','questions')
    choices=d.locator('button[data-question-id]')
    observed=choices.evaluate_all('nodes=>nodes.map(b=>[b.dataset.questionId,b.textContent])')
    wanted={item['id']:item for item in context['questions']}
    assert all(q in wanted and wanted[q]['text']==text for q,text in observed),(observed,wanted)
    if not ask:
        back_from_material(page)
        return observed
    assert observed
    item=wanted[observed[0][0]]
    prior=len(text_log(page))
    choices.first.tap()
    expect(d).not_to_be_visible()
    assert len(text_log(page))==prior+2
    assert item['text'] in text_log(page,'question')[-1]
    assert item['answer'] in text_log(page,'answer')[-1]
    return item


def correct_directly(page,tier,stage,strategy):
    if tier in LEVELS[:2]:
        options=page.locator('#begruendungen button[data-option]')
        options.nth(correct_reason(tier,stage,strategy,options.all_text_contents())).tap()
    else:
        page.locator('#pruefcode').fill(CODES[stage])
        page.locator('#fachcheck-pruefen').tap()


def incomplete_text(page):
    text=page.locator('#fachmeldung').inner_text().strip()
    assert re.search(r'Infektion|STI|Schutzlücke|Ziel.{0,45}offen',text,re.I),text
    return text


def on_screen(locator):
    locator.scroll_into_view_if_needed()
    assert locator.evaluate("""el=>{
      const r=el.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2;
      return x>=0 && x<innerWidth && y>=0 && y<innerHeight && el.contains(document.elementFromPoint(x,y));
    }"""),locator


def switch_and_resume(page,engine,bank):
    start(page,'MSA')
    choose(page,'Cu')
    data=bank['stages']['L01']['levels']['MSA']
    earlier=questions(page,data['strategies']['Cu'],ask=True)
    assert all(q!=earlier['id'] for q,_ in questions(page,data['strategies']['Cu']))
    page.locator('#pruefcode').fill(' b ')
    before=text_log(page)
    materials(page,'MSA','L01','Cu',data['strategies']['Cu'])
    expect(page.locator('#pruefcode')).to_have_value(' b ')
    assert text_log(page)==before
    page.locator('#fachcheck-pruefen').tap()
    expect(page.locator('#nachricht-senden')).to_be_enabled()
    choose(page,'K+H')
    expect(page.locator('#nachricht-senden')).to_be_disabled()
    dialogue_guard(page)
    assert text_log(page)==before and not text_log(page,'reaction')
    historical=page.locator('#beratung-verlauf [data-historical=true][data-about-strategy=Cu]')
    expect(historical).to_have_count(2)
    toggle=page.locator('#fruehere-nachrichten')
    expect(historical.first).to_be_hidden()
    toggle.tap()
    expect(historical.first).to_be_visible()
    expect(historical.first.locator('strong')).to_contain_text('Frühere Rückfrage')
    expect(historical.last.locator('strong')).to_contain_text('frühere Antwort')
    toggle.tap()
    assert all(q!=earlier['id'] for q,_ in questions(page,data['strategies']['K+H']))
    materials(page,'MSA','L01','K+H',data['strategies']['K+H'])
    expect(page.locator('#aktueller-rat')).to_have_attribute('data-about-strategy','K+H')
    correct_directly(page,'MSA','L01','K+H')
    expect(page.locator('#nachricht-senden')).to_be_enabled()
    page.locator('#grund-bearbeiten').tap()
    page.locator('#pruefcode').fill('unpassend')
    expect(page.locator('#nachricht-senden')).to_be_disabled()
    dialogue_guard(page)
    page.locator('#pruefcode').fill('b')
    page.locator('[data-nav=resources]').tap()
    d=page.locator('#material-dialog[open]')
    expect(d).to_have_attribute('data-view','cards')
    page.locator('#material-karte-H').tap()
    assert d.get_attribute('data-method')=='H'
    page.locator('#material-zurueck').tap()
    back_from_material(page)
    expect(page.locator('#pruefcode')).to_have_value('b')
    page.locator('[data-nav=home]').tap()
    page.locator('#level-ESA').tap()
    page.locator('#neu').tap()
    assert not text_log(page,'answer') and not text_log(page,'send')
    choose(page,'P')
    page.locator('[data-nav=home]').tap()
    page.locator('#level-MSA').tap()
    page.locator('#weiterarbeiten').tap()
    expect(page.locator('#pruefcode')).to_have_value('b')
    assert text_log(page)==before
    page.locator('#fachcheck-pruefen').tap()
    expect(page.locator('#nachricht-senden')).to_be_enabled()
    shot(page,engine+'-Gepruefter-Kombinationsrat')
    send_once(page,'L01')
    page.locator('#beratung-weiter').tap()
    no_send(page)
    choose(page,'K+H')
    expect(page.locator('#nachricht-senden')).to_be_disabled()
    assert 'L01' not in (page.locator('#fachmeldung').get_attribute('data-stage') or '')
    previous_ids=set()
    for method in ('Cu','H','K'):
        choose(page,method)
        ctx=bank['stages']['L02']['levels']['MSA']['strategies'][method]
        active_material(page,bank,'MSA','L02',method)
        offered=questions(page,ctx)
        current_ids={qid for qid,_ in offered}
        assert current_ids and not (previous_ids & current_ids)
        previous_ids.update(current_ids)
        questions(page,ctx,ask=True)
        current=page.locator('#beratung-verlauf [data-kind=answer][data-historical=false]')
        expect(current).to_have_count(1)
        expect(current).to_have_attribute('data-about-strategy',method)
        materials(page,'MSA','L02',method,ctx)
        no_send(page)
    page.locator('[data-nav=home]').tap()
    expect(page.locator('#weiterarbeiten')).to_be_visible()
    page.locator('#neu').tap()
    expect(page.locator('#beratung-stage')).to_have_attribute('data-stage','L01')
    assert len(text_log(page)) == len(text_log(page,'opening')) == 1
    expect(page.locator('button[data-strategy][aria-pressed=true]')).to_have_count(0)
    no_send(page)
    return dict(test='E/F/G/J',alte_frage=earlier['text'],erste_auswahl='Cu',neue_auswahl='K+H',
                weitere_wechsel=['Cu','H','K'],bewusster_neubeginn=True,
                verlauf_erhalten=True,freigabe_nach_strategie_und_codeaenderung_ungueltig=True,
                tageswechsel='build/runde1/bestand.json · tageswechsel')


def consolidation_and_keyboard(page,engine):
    def summary(capture=False):
        before=text_log(page)
        send=page.locator('#nachricht-senden')
        pending=send.is_visible() and send.is_enabled()
        state=page.locator('#beratung-stage').get_attribute('data-stage')
        code=page.locator('#pruefcode')
        value=code.input_value() if code.is_visible() else None
        expect(page.locator('nav').get_by_text(re.compile('Sicherung|Lehrkraft'))).to_have_count(0)
        teacher=page.locator('#lehrkraft summary')
        expect(teacher).to_have_text(re.compile('Lehrkraft'))
        expect(page.locator('#sicherung-oeffnen')).not_to_be_visible()
        teacher.tap()
        page.locator('#sicherung-oeffnen').tap()
        d=page.locator('#material-dialog[open]')
        expect(d).to_have_attribute('data-view','summary')
        text=d.inner_text()
        for term in ('Latex','Hormon','Infektion|STI','unregelmäßig','Freundin','Regelschmerz','Einsetzen|Einlage',
                     'Praxis|ärzt','später','biologisch'):
            assert re.search(term,text,re.I),(term,text)
        expect(d.locator('input')).to_have_count(0)
        if capture:shot(page,engine+'-Lehreransicht')
        back_from_material(page)
        expect(teacher).to_be_focused()
        expect(page.locator('#sicherung-oeffnen')).not_to_be_visible()
        expect(page.locator('#beratung-stage')).to_have_attribute('data-stage',state)
        if value is not None:expect(code).to_have_value(value)
        assert text_log(page)==before and (send.is_visible() and send.is_enabled())==pending
    start(page,'AHR')
    summary(capture=True)
    choose(page,'Cu')
    correct_directly(page,'AHR','L01','Cu')
    summary()
    send_once(page,'L01')
    page.locator('#beratung-weiter').tap()
    summary()
    page.reload()
    expect(page.locator('#start')).to_be_visible()
    assert not text_log(page,'send')
    expect(page.locator('#start [aria-pressed=true]')).to_have_count(0)
    page.locator('#level-AHR').tap()
    assert not page.locator('#weiterarbeiten').is_visible() or page.locator('#weiterarbeiten').is_disabled()
    page.locator('#abschnitt-wahl').tap()
    expect(page.locator('#einstieg [data-stage]:visible')).to_have_count(5)
    assert page.locator('#einstieg [data-stage]:visible').all_inner_texts()==list(TITLES)
    page.locator('#einstieg [data-stage=L02]').tap()
    expect(page.locator('#beratung-stage')).to_have_attribute('data-stage','L02')
    assert len(text_log(page,'send'))==len(text_log(page,'reaction'))==0
    recap=' '.join(text_log(page,'recap'))
    assert re.search('Latex',recap) and re.search('schwanger',recap,re.I),recap
    assert not re.search(r'Laura\s*[12]\s*–\s*Laura\s*[12]',page.locator('#beratung').inner_text())
    no_send(page)
    choose(page,'Cu')
    page.locator('#pruefcode').fill('b')
    page.locator('#fachcheck-pruefen').tap()
    expect(page.locator('#nachricht-senden')).to_be_disabled()
    correct_directly(page,'AHR','L02','Cu')
    expect(page.locator('#fachmeldung')).to_have_attribute('data-type','B')
    issue=incomplete_text(page)
    shot(page,engine+'-Zweites-Schutzziel-fehlt')
    choose(page,'K+Cu')
    page.set_viewport_size({'width':820,'height':470})
    field=page.locator('#pruefcode')
    on_screen(field)
    field.tap()
    expect(field).to_be_focused()
    field.fill(' c ')
    on_screen(page.locator('#fachcheck-pruefen'))
    page.locator('#fachcheck-pruefen').tap()
    send=page.locator('#nachricht-senden')
    expect(send).to_be_enabled()
    on_screen(send)
    shot(page,engine+'-Verkleinerter-Tastaturbereich')
    assert page.locator('html').evaluate('e=>e.scrollWidth<=innerWidth+1')
    send.tap()
    expect(page.locator('#beratung-weiter')).to_be_visible()
    assert len(text_log(page,'send'))==1
    return dict(test='H/I/J',neustart='L02',fiktive_fruehere_antworten=0,sicherung=['L01','L02'],
                tastatur={'viewport':[820,470],'art':'Verkleinertes Browserfenster bei Touchsimulation'},unvollstaendig=issue)


def direct_recovery(page,bank):
    """Every section starts with actual earlier facts, never a fabricated recommendation."""
    rows=[]
    for tier in LEVELS:
        for index,(stage,code) in enumerate(CODES.items()):
            page.reload()
            expect(page.locator('#start')).to_be_visible()
            expect(page.locator('#start [aria-pressed=true]')).to_have_count(0)
            page.locator('#level-'+tier).tap()
            expect(page.locator('#weiterarbeiten')).not_to_be_visible()
            page.locator('#abschnitt-wahl').tap()
            assert page.locator('#einstieg button[data-stage]:visible').all_inner_texts()==list(TITLES)
            page.locator(f'#einstieg button[data-stage="{stage}"]').tap()
            expect(page.locator('#beratung-stage')).to_have_text(TITLES[index])
            expect(page.locator('#beratung-arbeit')).to_have_attribute('data-step','wahl')
            assert not (text_log(page,'send') or text_log(page,'reaction') or text_log(page,'answer'))
            assert not page.locator('button[data-strategy][aria-pressed=true]').count()
            recap=' '.join(text_log(page,'recap'))
            if index:
                assert recap==bank['stages'][stage]['recovery']
                assert re.search('Latex',recap) and re.search('schwanger',recap,re.I)
            if index>=2:assert re.search('STI|Infektion',recap,re.I)
            if index>=3:assert re.search('Freundin',recap) and re.search('unregelmäßig|täglich',recap,re.I)
            if index==4:assert re.search('Schmerz',recap,re.I) and re.search('Einsetzen|Einlage',recap,re.I)
            pupil_view(page,stage)
            choose(page,'K')
            dialogue_guard(page)
            if tier in LEVELS[2:]:
                expect(page.locator('#pruefcode')).to_have_value('')
                page.locator('#pruefcode').fill('X')
                page.locator('#fachcheck-pruefen').tap()
                expect(page.locator('#fachmeldung')).to_have_attribute('data-type','A')
                no_send(page)
            correct_directly(page,tier,stage,'K')
            history=text_log(page)
            page.locator('[data-nav=home]').tap()
            page.locator('#weiterarbeiten').tap()
            expect(page.locator('#beratung-stage')).to_have_text(TITLES[index])
            assert text_log(page)==history
            expect(page.locator('#nachricht-senden')).to_be_enabled()
            send_once(page,stage)
            assert len(text_log(page,'send'))==len(text_log(page,'reaction'))==1
            rows.append({'niveau':tier,'abschnitt':stage,'code':code if tier in LEVELS[2:] else None,
                         'vorwissen':recap,'gesendet':1})
    return rows


def scenario(ctx,engine,bank):
    page=ctx.new_page()
    result=[switch_and_resume(page,engine,bank),consolidation_and_keyboard(page,engine)]
    start(page,'Foerder')
    choose(page,'K')
    correct_directly(page,'Foerder','L01','K')
    expect(page.locator('#nachricht-senden')).to_be_enabled()
    page.locator('#grund-bearbeiten').tap()
    opts=page.locator('#begruendungen button[data-option]')
    wrong=1-correct_reason('Foerder','L01','K',opts.all_text_contents())
    opts.nth(wrong).tap()
    expect(page.locator('#nachricht-senden')).to_be_disabled()
    dialogue_guard(page)
    choose(page,'H')
    expect(page.locator('#nachricht-senden')).to_be_disabled()
    expect(page.locator('#ask')).to_be_visible()
    ctx_h=bank['stages']['L01']['levels']['Foerder']['strategies']['H']
    materials(page,'Foerder','L01','H',ctx_h)
    assert not text_log(page,'send') and not text_log(page,'reaction')
    result.append(dict(test='C/D/G',korrekte_antwort_widerrufen=True,hormonspirale_erhalten=True))
    result.append(dict(test='Direkteinstieg und Weiterarbeiten auf allen Niveaus',einstiege=direct_recovery(page,bank)))
    page.close()
    return result


def main():
    QA.mkdir(parents=True,exist_ok=True)
    bank=json.loads((DIST/'Materialvertrag.json').read_text())
    raw=json.loads((ROOT/'data/laura-0212.json').read_text())
    assert bank=={**raw,'buildCommit':bank['buildCommit']}
    work=(DIST/'Materialvertrag.md').read_text()
    assert bank['paperFallbackInstruction'] in work
    for sid in CODES:
        for task in bank['stages'][sid]['levels'].values():
            for key in ('task','paperPrompt','returnPrompt','message'):
                assert task[key] in work
            for ctx in task['strategies'].values():
                assert all(h in work for h in ctx['hints'])
                assert all(q['text'] in work and q['answer'] in work for q in ctx['questions'])
    report={'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'html_sha256':sha(HTML),'bankversion':bank['version'],'material_sha256':sha(DIST/'Materialvertrag.json'),'browsers':[],'screenshots':SHOTS}
    with sync_playwright() as pw:
        for name in ('chromium','webkit'):
            engine=getattr(pw,name)
            browser=engine.launch(executable_path=os.getenv(name.upper()+'_EXECUTABLE'))
            errors=[]
            network=[]
            writes=[]
            context=browser.new_context(viewport={'width':820,'height':1180},has_touch=True,is_mobile=True,
                                        device_scale_factor=1,accept_downloads=False)
            context.route('http*/**',lambda route:(network.append(route.request.url),route.abort()))
            context.expose_function('recordWrite',lambda k:writes.append(k))
            context.add_init_script("""for(const [name,methods] of [['Storage',['setItem','removeItem','clear']],
                       ['IDBFactory',['open','deleteDatabase']],['CacheStorage',['open']]]){
              const p=window[name]?.prototype;
              for(const method of methods){if(!p || !p[method])continue;
                const prev=p[method];p[method]=function(...args){recordWrite(name+'.'+method);return prev.apply(this,args);};}
            }
            let owner=document;while(owner && !Object.getOwnPropertyDescriptor(owner,'cookie'))owner=Object.getPrototypeOf(owner);
            const cookie=owner && Object.getOwnPropertyDescriptor(owner,'cookie');
            if(cookie)Object.defineProperty(document,'cookie',{get:()=>cookie.get.call(document),set:v=>{
              recordWrite('cookie');cookie.set.call(document,v);}});
            """)
            context.on('page',lambda p:p.on('pageerror',lambda e:errors.append(str(e))))
            entry={'engine':name,'version':browser.version,'paths':[]}
            page=context.new_page()
            page.goto(HTML.as_uri())
            assert json.loads(page.locator('#materialvertrag').text_content())==bank
            assert bank['buildCommit']==report['commit']
            expect(page.locator('#start')).to_be_visible()
            expect(page.locator('#start [aria-pressed=true]')).to_have_count(0)
            shot(page,name+'-Falluebersicht')
            for i,tier in enumerate(LEVELS):
                for j,strategy in enumerate(STRATEGIES):
                    viewport=(820,1180) if (i+j)%2==0 else (1180,820)
                    page.set_viewport_size(dict(zip(('width','height'),viewport)))
                    row=matrix(page,tier,strategy,bank,name)
                    row['viewport']=list(viewport)
                    entry['paths'].append(row)
                print(name,tier,'alle sieben Strategien in L01 bis L05 geprüft',flush=True)
            entry['scenarios']=scenario(context,name,bank)
            assert not writes and not context.cookies() and not errors and not network,(writes,errors,network)
            assert page.url==HTML.as_uri()
            assert page.evaluate('[localStorage.length,sessionStorage.length]')==[0,0]
            entry.update(speichervorgaenge=writes,skriptfehler=errors,externe_zugriffe=network)
            report['browsers'].append(entry)
            browser.close()
    assert sha(HTML)==report['html_sha256'] and sha(DIST/'Materialvertrag.json')==report['material_sha256']
    (QA/'browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
