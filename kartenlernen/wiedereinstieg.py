"""Touchwege, frische Sitzungen und Texteingabe bei verkleinerter nutzbarer Fläche."""
import os
from playwright.sync_api import sync_playwright
from erstellen import OUT
from pruefen import QA

GEOMETRIE="""()=>{const h=Math.min(innerHeight,visualViewport.height),w=Math.min(innerWidth,visualViewport.width);
 const bad=[];for(const el of document.querySelectorAll('button,h1,textarea,#draft,#page p,#pieces,#segments')){
 if(!el.getClientRects().length)continue;
 const b=el.getBoundingClientRect();
 if(b.bottom>h+1||b.right>w+1||b.left< -1||b.top< -1)bad.push([el.tagName,el.innerText.slice(0,25),b.y,b.bottom,h]);
 if(el.tagName==='TEXTAREA' && el.scrollHeight>el.clientHeight+1)bad.push(['Text nicht sichtbar',el.scrollHeight,el.clientHeight]);
 }return bad;}"""

def run():
    results=[];folder=QA/'Sichtbilder';folder.mkdir(exist_ok=True,parents=True)
    with sync_playwright() as pw:
        for engine in ('chromium','webkit'):
            with getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as browser:
                p=browser.new_page(viewport={'width':1024,'height':768},has_touch=True)
                def tap(key,val=None):
                    p.locator('[data-action="'+key+'"]'+('' if val is None else f'[data-value="{val}"]')).tap()
                def shot(name):
                    assert not p.evaluate(GEOMETRIE),(engine,name,p.evaluate(GEOMETRIE))
                    p.screenshot(path=folder/(engine+'-'+name+'.jpg'),quality=63,type='jpeg')
                def page_name():return p.locator('#page').get_attribute('data-screen')
                for ix,tier in enumerate(('Foerder','ESA','MSA','AHR')):
                    p.goto((OUT/'Vorbereitung.html').as_uri());p.evaluate('document.fonts.ready')
                    if ix==0:shot('01-Niveau')
                    tap('level',tier)
                    if ix==0:shot('02-Wiederaufnahme')
                    tap('lookup');tap('fill',3);tap('written')
                    assert page_name()=='lookup';tap('menu')
                    assert '✓' not in p.locator('.grid').inner_text()
                    tap('open',0)
                    for i in range(4):
                        if ix==0:shot('03-Info-'+str(i+1))
                        tap('readnext');tap('readnext')
                        if ix==0:shot('04-Papier-'+str(i+1))
                        tap('written')
                    if ix==0:shot('05-Uebergang')
                    tap('startq')
                    bank=p.evaluate("t=>JSON.parse(document.querySelector('#material').textContent).levels[t]",tier)
                    for i,q in enumerate(bank['fragen']):
                        if ix==i:shot('06-Aufgabe-'+tier)
                        if q['typ']=='wahl':
                            tap('pick',q['optionen'].index(q['alternativen'][0]['text']))
                            before=p.locator('#page').inner_text()
                            tap('menu');tap('questions');assert p.locator('#page').inner_text()==before
                            if ix==0 and i==0:shot('07-Fehlwahl')
                            tap('revise');tap('pick',q['optionen'].index(q['passend']))
                            if ix==0 and i==0:shot('08-Richtig')
                        else:
                            shot('09-Eingabe-'+q['modell'])
                            partial={'pille':'Kein Eisprung.','haut':'Freie Haut.','kupfer':'Kupfer bremst Spermien.','schleim':'Der Schleim wird dicker.'}[q['modell']]
                            p.locator('#entry').fill(partial);tap('check');shot('10-Teilantwort-'+q['modell'])
                            tap('help');tap('more');shot('11-Adaptive-Hilfe-'+q['modell']);tap('back')
                            tap('revise');tap('menu');tap('questions')
                            assert p.locator('#entry').input_value()==partial
                            tap('help');assert 'Hilfe 2' in p.locator('#page h1').inner_text();tap('back')
                            if q['modell']=='schleim':
                                p.locator('#entry').fill('Der Schleim wird dicker, aber Spermien kommen leichter durch.');tap('check')
                                shot('12a-Widerspruch');tap('help');tap('more');tap('more');shot('12b-Hilfe-zum-Widerspruch')
                                tap('back');tap('revise')
                            p.locator('#entry').fill('Das könnte auch anders zusammenhängen.');tap('check')
                            if i==3:shot('12-Unsicher');tap('compare');shot('13-Selbstvergleich');tap('compared');continue
                            tap('revise')
                            model=p.evaluate("k=>JSON.parse(document.querySelector('#material').textContent).modelle[k]",q['modell'])
                            p.locator('#entry').fill(model['beispiel']);tap('check')
                        tap('advance')
                    assert page_name()=='end'
                    if ix==0:shot('14-Abschluss')
                    p.reload();tap('level',tier);tap('questions')
                    assert page_name()=='question' and 'Frage 1 von 4' in p.locator('#page').inner_text()
                    results.append(dict(browser=engine,niveau=tier,reload=True,zeitnot=True,unterbrechung=True))
                # Fokussierter Editor bei eingeschränkter sichtbarer Höhe: keine echte Systemtastatur.
                for w,whole,available,zoom in [(768,1024,580,100),(1024,768,340,125),(740,480,240,150),(390,560,285,125)]:
                    p.set_viewport_size({'width':w,'height':whole})
                    p.goto((OUT/'Vorbereitung.html').as_uri());p.evaluate("(z)=>document.documentElement.style.fontSize=z+'%'",zoom)
                    tap('level','MSA');tap('questions');tap('pick',0);tap('advance')
                    edit=p.locator('#entry');edit.focus();p.set_viewport_size({'width':w,'height':available})
                    p.wait_for_timeout(70)
                    long='Weil die Pille den Eisprung hemmt, wird keine Eizelle zur Befruchtung frei. Das möchte ich mit meiner Karte vergleichen. '*3
                    edit.fill(long)
                    assert not p.evaluate(GEOMETRIE),(engine,w,p.evaluate(GEOMETRIE))
                    shot('15-Tastatur-'+str(w))
                    # Alle eingegebenen Textteile müssen weiterhin genau rekonstruierbar sein.
                    tap('help');p.set_viewport_size({'width':w,'height':whole});tap('back')
                    while p.locator('[data-action=earlier]').count():tap('earlier')
                    parts=[edit.input_value()]
                    while p.locator('[data-action=later]').count():tap('later');parts.append(edit.input_value())
                    assert ''.join(parts)==long,(engine,w,parts)
                    tap('check');tap('compare')
                    chunks=[p.locator('#draft').text_content()]
                    while p.locator('[data-action=later]').count():
                        tap('later');chunks.append(p.locator('#draft').text_content())
                    assert ''.join(chunks)==long
                    assert not p.evaluate(GEOMETRIE),(engine,w,p.evaluate(GEOMETRIE))
                    tap('compared')
                    results.append(dict(browser=engine,breite=w,hoehe=whole,tastatur_resthoehe=available,schrift=zoom,textteile=len(parts)))
                # Dieselbe kleinste Querfläche auch mit jeder der vier konkreten Freitextfragen.
                for tier,index in [('MSA',1),('MSA',3),('AHR',0),('AHR',2)]:
                    p.set_viewport_size({'width':740,'height':480});p.goto((OUT/'Vorbereitung.html').as_uri())
                    p.evaluate("document.documentElement.style.fontSize='150%'");tap('level',tier);tap('questions')
                    for j in range(index):
                        task=p.evaluate("(x)=>JSON.parse(document.querySelector('#material').textContent).levels[x[0]].fragen[x[1]]",[tier,j])
                        if task['typ']=='wahl':tap('pick',task['optionen'].index(task['passend']))
                        else:
                            example=p.evaluate("id=>JSON.parse(document.querySelector('#material').textContent).modelle[id].beispiel",task['modell'])
                            p.locator('#entry').fill(example);tap('check')
                        tap('advance')
                    p.locator('#entry').focus();p.set_viewport_size({'width':740,'height':240});p.wait_for_timeout(80)
                    assert not p.evaluate(GEOMETRIE),(engine,tier,index,p.evaluate(GEOMETRIE))
                    results.append(dict(browser=engine,niveau=tier,frage=index+1,tastatur_resthoehe=240))
                # Der äußere Viewport schrumpft, die vom LMS gesetzte Rahmenhöhe bleibt groß.
                p.set_viewport_size({'width':740,'height':780})
                p.goto('about:blank')
                p.set_content('<body style="margin:0"><div style="height:54px">LMS</div><iframe style="display:block;width:100%;height:700px;border:0"></iframe></body>')
                p.locator('iframe').evaluate('(el,text)=>el.srcdoc=text',(OUT/'Vorbereitung.html').read_text())
                f=p.frames[-1];f.locator('[data-action=level]').first.wait_for()
                f.locator('[data-action=level][data-value=AHR]').tap()
                f.locator('[data-action=questions]').tap();f.locator('#entry').focus()
                p.set_viewport_size({'width':740,'height':294})
                f.wait_for_function("document.querySelector('#workspace').getBoundingClientRect().height<=241")
                for b in ['#entry','[data-action=check]','#page h1','[data-action=help]']:
                    box=f.locator(b).bounding_box();assert 0<=box['y'] and box['y']+box['height']<=295,(engine,b,box)
                results.append(dict(browser=engine,iframehoehe=700,sichtbare_rahmenhoehe=240,editor_erreichbar=True))
    return results
