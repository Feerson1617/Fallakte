"""Exercise released optional cases via visible controls, including direct section entry."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist/Runde-1'
QA=ROOT/'build/vertiefungen'
LEVELS=('Foerder','ESA','MSA','AHR')

def enter(p,person,tier,index):
    p.goto((OUT/'Fallakte.html').as_uri())
    p.locator('#abschnitt-wahl').click();p.locator('#wieder-level-'+tier).click()
    p.locator('#wiederfall').get_by_role('button',name=person,exact=True).click()
    p.locator('#abschnitte button').nth(index).click()
    return p.frame_locator('#rahmen-reserve-'+person)

def answer(f,tier,letter):
    if tier in LEVELS[:2]:f.locator('#answer-'+letter).click()
    else:f.locator('#code').fill(letter);f.locator('#check').click()

def tom(p,tier,engine):
    for i,(truth,wrong) in enumerate([('B','A'),('C','A'),('A','B')]):
        f=enter(p,'Tom',tier,i);expect(f.locator('#step')).to_have_text(f'Tom {i+1} von 3')
        if i==0:
            f.locator('#method-P').click();answer(f,tier,truth);expect(f.locator('#send')).to_have_count(0)
            f.locator('#edit').click();f.locator('#method-K').click()
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

def run():
    QA.mkdir(parents=True,exist_ok=True);log=[]
    with sync_playwright() as pw:
        for engine in ('chromium','webkit'):
            b=getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE'))
            for i,tier in enumerate(LEVELS):
                p=b.new_page(has_touch=True,viewport={'width':820 if i%2==0 else 1180,'height':1180 if i%2==0 else 820})
                issues=[];p.on('pageerror',lambda e:issues.append(str(e)))
                tom(p,tier,engine);assert not issues,issues
                log.append([engine,tier,3]);p.close()
            b.close()
    (QA/'Vertiefungspruefung.json').write_text(json.dumps(log))
if __name__=='__main__':run()
