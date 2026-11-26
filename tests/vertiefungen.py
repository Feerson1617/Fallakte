"""Exercise released optional cases via visible controls, including direct section entry."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist/Runde-1'
QA=ROOT/'build/vertiefungen'
LEVELS=('Foerder','ESA','MSA','AHR')

def enter(p,person,tier,index):
    integrated=os.getenv('FALLAKTE_ZUSATZ_HTML')
    if integrated:
        p.goto(Path(integrated).resolve().as_uri())
        p.locator('#erster-tag').click()
        day=p.frame_locator('iframe[title^=Mittwoch]')
        p.locator('[data-action=recovery]').click()
    else:
        p.goto((OUT/'Fallakte.html').as_uri())
        day=p;day.locator('#abschnitt-wahl').click()
    day.locator('#wieder-level-'+tier).click()
    assert not day.locator('#wiederfall').get_by_role('button',name=person,exact=True).count()
    day.locator('#papierstand').click()
    day.locator('#wiederfall').get_by_role('button',name=person,exact=True).click()
    day.locator('#abschnitte button').nth(index).click()
    return day.frame_locator('#rahmen-reserve-'+person)

def initial(f,tier,engine,person):
    shown=f.locator('[id^=method-]:visible').count()
    assert (2<=shown<=3 if tier in LEVELS[:2] else shown==7),(person,tier,shown)
    expect(f.locator('[id^=method-]')).to_have_count(7)
    if tier=='Foerder':f.locator('#desk').screenshot(path=QA/f'{engine}-{person}-Auswahl.jpg')

def choose(f,key):
    option=f.locator('[id="method-'+key+'"]')
    if not option.is_visible():f.locator('#more summary').click()
    option.click()

def blocked(f):
    expect(f.locator('#send,#code,#check,[id^=answer-]')).to_have_count(0)
    expect(f.locator('#feedback')).not_to_be_empty()
    expect(f.locator('#feedback')).not_to_contain_text('Das stimmt')

def answer(f,tier,letter):
    if tier in LEVELS[:2]:f.locator('#answer-'+letter).click()
    else:f.locator('#code').fill(letter);f.locator('#check').click()

def tom(p,tier,engine):
    for i,(truth,wrong) in enumerate([('B','A'),('C','A'),('A','B')]):
        f=enter(p,'Tom',tier,i);expect(f.locator('#step')).to_have_text(f'Tom {i+1} von 3')
        if i==0:
            initial(f,tier,engine,'Tom')
            for key in ('P','Cu','H','K+P','K+Cu','K+H','K'):
                if f.locator('#edit').is_visible():f.locator('#edit').click()
                choose(f,key)
                method=key.split('+')[-1]
                section={'K':'Ein neues Kondom für jeden Sex','P':'Die Pille bremst den Eisprung','Cu':'Du entscheidest über die Spirale','H':'Du entscheidest über die Spirale'}[method]
                f.locator('#help').click();expect(f.locator('#reading')).to_contain_text(section);f.locator('#back').click()
                f.locator('#source').click();expect(f.locator('#resource')).to_contain_text(section);f.locator('#back').click()
                if key!='K':blocked(f)
                if key=='K+Cu' and tier=='ESA':p.screenshot(path=QA/f'{engine}-Tom-Konflikt.jpg')
        elif tier in LEVELS[2:]:expect(f.locator('#code,#send')).to_have_count(0)
        else:expect(f.locator('#desk blockquote').last).to_contain_text('Forschende' if i==1 else 'Studie B')
        f.locator('#help').click();expect(f.locator('#reading')).not_to_be_empty();f.locator('#back').click()
        f.locator('#ask').click();f.locator('#q0').click()
        f.locator('#source').click()
        if i:
            f.locator('#reading summary').last.click()
            expect(f.locator('#reading')).to_contain_text('10.1038/s43856-025-01004-4')
            expect(f.locator('#reading')).to_contain_text('vasektomiert')
        if i==2 and tier=='AHR':p.screenshot(path=QA/f'{engine}-Tom-Quelle.jpg')
        f.locator('#back').click()
        answer(f,tier,wrong);expect(f.locator('#feedback')).not_to_be_empty();expect(f.locator('#send')).to_have_count(0)
        answer(f,tier,truth);expect(f.locator('#send')).to_be_visible()
        f.locator('#send').evaluate('b=>{b.click();b.click()}')
        expect(f.locator('#next')).to_be_visible()
        f.locator('#next').click()

def celina(p,tier,engine):
    counts=[]
    for i,truth in enumerate('BACBC'):
        f=enter(p,'Celina',tier,i)
        expect(f.locator('#step')).to_have_text(f'Celina {i+1} von 5')
        if i==0:initial(f,tier,engine,'Celina')
        for strategy in ('P','H','K+P','K+H','Cu','K+Cu','K'):
            if f.locator('#edit').is_visible():f.locator('#edit').click()
            expect(f.locator('#send')).to_have_count(0)
            choose(f,strategy)
            expect(f.locator('#desk')).not_to_contain_text('Latexallergie')
            f.locator('#ask').click();f.locator('#q0').click()
            if strategy=='K':expect(f.locator('#desk')).not_to_contain_text('Ob eine Kupferspirale zu mir passt')
            f.locator('#source').click();expect(f.locator('#reading')).not_to_be_empty();f.locator('#back').click()
            f.locator('#help').click();expect(f.locator('#reading')).not_to_be_empty();f.locator('#back').click()
            allowed=strategy in ('K','K+Cu') or strategy=='Cu' and i<3
            if allowed:
                wrong=next(k for k in 'ABC' if k!=truth and (tier not in LEVELS[:2] or f.locator('#answer-'+k).count()))
                answer(f,tier,wrong);expect(f.locator('#send')).to_have_count(0)
                answer(f,tier,truth);expect(f.locator('#send')).to_be_visible()
            else:
                blocked(f)
                expect(f.locator('#feedback')).to_contain_text('Infektionen' if strategy=='Cu' else 'Hormone')
            counts.append([i+1,strategy,allowed])
        if i==4 and tier=='ESA':p.screenshot(path=QA/f'{engine}-Celina-Schluss.jpg')
        f.locator('#send').click();f.locator('#next').click()
    return counts

def run():
    QA.mkdir(parents=True,exist_ok=True);log=[]
    with sync_playwright() as pw:
        for engine in ('chromium','webkit'):
            b=getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE'))
            for i,tier in enumerate(LEVELS):
                p=b.new_page(has_touch=True,viewport={'width':820 if i%2==0 else 1180,'height':1180 if i%2==0 else 820})
                issues=[];p.on('pageerror',lambda e:issues.append(str(e)))
                tom(p,tier,engine);choices=celina(p,tier,engine);assert not issues,issues
                log.append({'browser':engine,'niveau':tier,'Tom':3,'Celina':choices});p.close()
            b.close()
    (QA/'Vertiefungspruefung.json').write_text(json.dumps(log))
if __name__=='__main__':run()
