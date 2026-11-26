"""Echte Bildschirmfotos, direkte Kapitelwahl, Musterkarten und unterbrochene Antworten."""
import json
import os
from playwright.sync_api import sync_playwright
from erstellen import OUT,HERE,ROOT
from pruefen import QA,LEVELS

def run():
    folder=QA/'Bilder';folder.mkdir(exist_ok=True,parents=True)
    evidence=[];captured=set()
    with sync_playwright() as pw:
        for engine in ('chromium','webkit'):
            with getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as b:
                p=b.new_page(viewport={'width':1024 if engine=='chromium' else 768,'height':768 if engine=='chromium' else 1024},has_touch=True)
                def tap(action,value=None):
                    sel='[data-action="'+action+'"]'+('' if value is None else '[data-value="'+str(value)+'"]')
                    p.locator(sel).tap()
                def photograph(name):
                    if name in captured:return
                    captured.add(name);p.screenshot(path=folder/(name+'.jpg'),type='jpeg',quality=66,animations='disabled')
                for i,tier in enumerate(LEVELS):
                    p.goto((OUT/'Vorbereitung.html').as_uri());p.evaluate('document.fonts.ready')
                    if i==0:photograph('01-Einstieg-Niveauwahl-'+engine)
                    tap('level',tier)
                    if i==0:photograph('02-Kapitelauswahl-'+engine)
                    tap('open',i);photograph('03-Aufgabe-'+tier+'-'+engine)
                    q=p.evaluate("t=>Object.values(JSON.parse(document.querySelector('#material').textContent).levels[t].fragen)",tier)
                    ix=[0,3,5,7][i];tap('answer',1-q[ix]['richtig'])
                    before=p.locator('#page').inner_text();tap('help')
                    for n in range(1,6):
                        if i==1:photograph('05-Hilfe-'+str(n))
                        if n<5:tap('more')
                    tap('back');assert before==p.locator('#page').inner_text()
                    if i==1:photograph('04-Fehlerrueckmeldung')
                    tap('menu');tap('open',i);assert q[ix]['fehler'] in p.locator('#page').inner_text()
                    tap('answer',q[ix]['richtig']);tap('menu');tap('open',i)
                    assert p.locator('[data-action=next]').is_enabled()
                    p.reload();tap('level',tier);assert not p.locator('[data-action=answer],[data-action=next]').count()
                    if i==1:photograph('06-Wiederaufnahme')
                    tap('open',i);assert not p.locator('.yes,.no,.feedback').count()
                    for idx in range(ix,[3,5,7,9][i]):tap('answer',q[idx]['richtig']);tap('next')
                    photograph('07-Papier-'+str(i+1)+'-'+engine)
                    tap('finish')
                    if i==3:
                        assert 'ein Kapitel' in p.locator('#page').inner_text();photograph('08-Abschluss-Direkteinstieg');tap('menu')
                    else:tap('menu')
                    # Papier ist eine Orientierung. Auch ein kompletter Musterkartengang
                    # nach dem Reload darf keinen digitalen Abschluss erzeugen.
                    p.reload();tap('level',tier)
                    for k in range(4):
                        tap('models');tap('model',k)
                        cards=p.evaluate("t=>JSON.parse(document.querySelector('#material').textContent).levels[t].cards",tier)
                        for s in cards[k]['texte']:
                            assert s['volltext'] in p.locator('#page').inner_text();tap('section')
                        assert cards[k]['pearl'] in p.locator('#page').inner_text()
                        tap('prevsection');tap('fill');tap('finish')
                        if k==3:assert 'bearbeitete Kapitel: 0' in p.locator('#page').inner_text()
                        tap('menu')
                    evidence.append(dict(browser=engine,niveau=tier,direkt=i+1,neuladen=True,musterkarten=4,ganze_texte=20,digital_nach_musterkarten=0))
                p.goto((OUT/'Vorbereitung.html').as_uri());tap('level','ESA');tap('open',0)
                topics=p.evaluate("JSON.parse(document.querySelector('#material').textContent).topics")
                qs=p.evaluate("JSON.parse(document.querySelector('#material').textContent).levels.ESA.fragen")
                for idx,key in enumerate(topics):
                    photograph('09-Biologie-'+key)
                    tap('answer',qs[key]['richtig']);tap('next')
                    if idx in [2,4,6,8]:tap('finish')
                assert 'alle vier Kapitel' in p.locator('#page').inner_text()
                photograph('10-Abschluss-nach-vier-Kapiteln')
                p.close()
    (QA/'Wiedereinstieg.json').write_text(json.dumps(evidence,ensure_ascii=False))
