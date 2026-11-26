"""Trefferprüfung ohne automatisches Scrollen an der ausgelieferten Offline-Datei und im SCO."""
import argparse
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from playwright.sync_api import sync_playwright
from auslieferung import ROOT, OUT, QA, sha
sys.path.insert(0,str(ROOT/'tests'))
from tagesauswahl import HOST, host

HIT="""e=>{
 const r=e.getBoundingClientRect(); if(!r.width || !r.height)return false;
 let w=window,x=r.x+r.width/2,y=r.y+r.height/2,target=e;
 const field=e.closest('.blatt-inhalt');
 if(field){const b=field.getBoundingClientRect();if(r.x<b.x-1||r.right>b.right+1||r.top<b.top-1||r.bottom>b.bottom+1)return false;}
 for(;;){
   const hit=w.document.elementFromPoint(x,y);
   if(!target.contains(hit))return false;
   if(w===w.parent || !w.frameElement)break;
   target=w.frameElement;const box=target.getBoundingClientRect();x+=box.x+target.clientLeft;y+=box.y+target.clientTop;w=w.parent;
 }
 return r.width>=43.5 && r.height>=43.5;
}"""

def reach(frame,control):
    folded=control.locator('xpath=ancestor::details[not(@open)]/summary').first
    if folded.count(): reach(frame,folded);folded.tap()
    if control.evaluate(HIT):return
    paper=control.locator('xpath=ancestor::*[contains(concat(" ",normalize-space(@class)," ")," blatt ")][1]')
    assert paper.count(),control.get_attribute('id')
    pager=paper.locator(':scope > .blatt-wechsel')
    for direction in ('first','last'):
        nav=getattr(pager.locator('button'),direction)
        while nav.is_visible() and nav.is_enabled():
            assert nav.evaluate(HIT),nav.text_content()
            nav.tap()
            if control.evaluate(HIT):return
    raise AssertionError((control.get_attribute('id'),control.text_content()[:75],control.bounding_box(),frame.locator('.arbeitskopf:visible').inner_text()))

def touch(frame,selector):
    loc=frame.locator(selector)
    reach(frame,loc);loc.tap()

def room(shell,day):
    shell.locator('#'+day+'-tag').tap()
    return shell.locator('#arbeitsplatz > iframe:visible').element_handle().content_frame()

def check_help(f,button,back,stages):
    normal=f.locator(button);reach(f,normal)
    place=normal.bounding_box();normal.tap()
    active=f.locator('dialog[open] .dialoghilfe')
    assert active.evaluate(HIT)
    modal=active.bounding_box()
    assert abs((place['x']+place['width'])-(modal['x']+modal['width']))<4 and abs(place['y']-modal['y'])<4,(place,modal)
    for selector in stages:touch(f,selector)
    touch(f,back)

def parcour(page,shell,tier,zoom,folder,tag):
    f=room(shell,'erster')
    f.evaluate('z=>{document.documentElement.style.fontSize=z+"%";Arbeitsplatz.refresh()}',zoom)
    touch(f,'#level-'+tier.replace('Förder','Foerder'))
    touch(f,'#neu')
    assert not f.locator('#praesentation').is_visible()
    check_help(f,'#hilfe','#material-zurueck',['#hilfe-weiter']*4)
    touch(f,'[data-strategy=K]')
    if tier in ('MSA','AHR'):
        field=f.locator('#erklaerung');reach(f,field);field.fill('Laura kann ein passendes Kondom ohne Latex wählen.')
        check_help(f,'#hilfe','#material-zurueck',[])
        assert field.input_value().endswith('ohne Latex wählen.')
        touch(f,'#vergleichen')
    options=f.evaluate("t=>window.LAURA.stages.L01.levels[t].strategies.K.options",tier.replace('Förder','Foerder'))
    for valid in (False,True):
        opt=next(x for x in options if x['correct']==valid)
        touch(f,'[data-option="'+opt['id']+'"]')
        if not valid:check_help(f,'#hilfe','#material-zurueck',[])
    touch(f,'#nachricht-senden');touch(f,'#beratung-weiter')
    assert f.locator('[data-stage=L01][data-kind=send]').count()==1
    if tag:page.screenshot(path=folder/(tag+'-Laura.jpg'),quality=65)
    shell.locator('#zurueck').tap()
    f=room(shell,'zweiter')
    f.evaluate('z=>{document.documentElement.style.fontSize=z+"%";Arbeitsplatz.refresh()}',zoom)
    level=f.locator('#level-0');reach(f,level);level.select_option(tier)
    touch(f,'#start');touch(f,'#next')
    if tier in ('MSA','AHR'):
        field=f.locator('textarea');reach(f,field);field.fill('Der Mutter ist Lauras Gesundheit wichtig.')
        initial=page.viewport_size
        if initial['width']==740:
            page.set_viewport_size(dict(width=740,height=294))
            f.wait_for_function("innerHeight<260")
            reach(f,field)
        check_help(f,'#help','#dismiss',['#hint-next']*4)
        page.set_viewport_size(initial)
        assert field.input_value()=='Der Mutter ist Lauras Gesundheit wichtig.'
        touch(f,'#compare')
    touch(f,'#answer-2')
    assert f.locator('#answer-2').get_attribute('data-urteil')=='falsch'
    check_help(f,'#help','#dismiss',['#hint-next']*4)
    touch(f,'#answer-0');assert not f.locator('#answer-2').count()
    touch(f,'#next')
    assert f.locator('.chat-history').text_content().count('Du · Mutter')==1
    if tag:page.screenshot(path=folder/(tag+'-Familie.jpg'),quality=65)
    assert f.evaluate('!scrollY && !scrollX')
    shell.locator('#zurueck').tap()

def run(engine=None,width=None,tier_filter=None):
    folder=QA/'Ergonomie';folder.mkdir(parents=True,exist_ok=True);rows=[]
    with TemporaryDirectory() as tmp, sync_playwright() as pw:
        tmp=Path(tmp)
        with ZipFile(OUT/'Fallakte-08-12-SCORM12.zip') as z:z.extractall(tmp)
        assert (tmp/'index.html').read_bytes()==(OUT/'Fallakte-08-12.html').read_bytes()
        (tmp/'host.html').write_text(HOST)
        with host(tmp) as url:
            for name in ([engine] if engine else ('chromium','webkit')):
                with getattr(pw,name).launch(executable_path=os.getenv(name.upper()+'_EXECUTABLE')) as b:
                    for w,h,z,sco in [(1180,820,100,False),(820,1180,150,True),(640,420,125,True),(390,600,125,False),(740,340,150,True)]:
                        if width and w!=width:continue
                        for tier in ([tier_filter] if tier_filter else ('Förder','ESA','MSA','AHR')):
                            p=b.new_page(viewport={'width':w,'height':h},has_touch=True)
                            p.set_default_timeout(4500)
                            errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
                            p.goto(url+'/host.html' if sco else (OUT/'Fallakte-08-12.html').as_uri())
                            shell=p.frame(name='sco') if sco else p.main_frame
                            tag=f'{name}-{w}-{h}' if tier=='AHR' else None
                            print(name,w,h,z,tier,flush=True)
                            parcour(p,shell,tier,z,folder,tag)
                            assert not errors,errors
                            rows.append(dict(browser=name,breite=w,hoehe=h,schrift=z,niveau=tier,scorm=sco))
                            p.close()
    name='Trefferpruefung'+('' if not (engine or width or tier_filter) else '-'+str(engine)+'-'+str(width)+'-'+str(tier_filter))
    (folder/(name+'.json')).write_text(json.dumps(dict(html_sha256=sha((OUT/'Fallakte-08-12.html').read_bytes()),wege=rows),indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--browser',choices=['chromium','webkit']);parser.add_argument('--breite',type=int);parser.add_argument('--niveau',choices=['Förder','ESA','MSA','AHR']);args=parser.parse_args();run(args.browser,args.breite,args.niveau)
