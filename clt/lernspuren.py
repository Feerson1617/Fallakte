"""Unabhängige Solltexte, Trefferflächen und persönliche Antwortpaare in den beiden Ausgaben."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from playwright.sync_api import sync_playwright, expect
from pruefen import OUT, QA, PROFILES, host, HOST, room
from lernspur_test import antwort, touch, reach

HERE=Path(__file__).parent
INITIAL='Für mich zählt, was Laura möchte.'
FINAL='Ich berücksichtige jetzt auch, welche Frage Laura zum Körper hat.'
SNAP="""()=>{const n=document.querySelector('#lernspur');return {titel:n.querySelector('h1').textContent,
  text:n.innerText,teile:n.querySelector('.blatt-wechsel:not([hidden]) span')?.textContent||'1 / 1',
  tasten:[...n.querySelectorAll('button')].filter(x=>x.offsetWidth && !x.disabled).map(x=>x.textContent)};}"""
def run(engine,day,tier):
    folder=QA/'Lernspuren'/f'{day}-{tier}-{engine}';folder.mkdir(parents=True,exist_ok=True)
    file=OUT/f'Fallakte-{day}-12.html'
    rows=[];pairs=[];errors=[]
    with TemporaryDirectory() as tmp,sync_playwright() as pw:
        site=Path(tmp)
        with ZipFile(OUT/f'Fallakte-{day}-12-SCORM12.zip') as z:z.extractall(site)
        assert file.read_bytes()==(site/'index.html').read_bytes()
        (site/'host.html').write_text(HOST)
        with host(site) as url,getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as browser:
            def begin(page,source):
                page.goto(source);shell=page.main_frame
                if source.startswith('http'):
                    page.frame_locator('[name=sco]').locator('#erster-tag').wait_for();shell=page.frame(name='sco')
                f=room(shell,'erster' if day=='02' else 'zweiter')
                if day=='02':touch(f,'#level-'+tier.replace('Förder','Foerder'));touch(f,'#neu')
                else:f.locator('#level-0').select_option(tier);touch(f,'#start')
                return shell,f
            def notice(p):p.on('pageerror',lambda e:errors.append(str(e)))
            for profile,(width,height,scale) in PROFILES.items():
                demo=profile=='quer' and engine=='chromium' and tier=='ESA'
                context=browser.new_context(viewport={'width':width,'height':height},has_touch=True,
                    **({'record_video_dir':str(site/'video'),'record_video_size':{'width':800,'height':556}} if demo else {}))
                p=context.new_page();notice(p);p.set_default_timeout(5000)
                s,f=begin(p,url+'/host.html' if profile in ('kurs','hoch','tastatur') else file.as_uri())
                f.evaluate('z=>{document.documentElement.style.fontSize=z+"%";Arbeitsplatz.refresh()}',scale)
                def capture(step):
                    f.locator('#lernspur h1').wait_for()
                    rows.append(dict(profil=profile,schritt=step,**f.evaluate(SNAP)))
                    if profile==('quer' if engine=='chromium' else 'tastatur'):
                        p.screenshot(path=folder/(step+'.jpg'),quality=72)
                    if demo:p.wait_for_timeout(550)
                capture('Einstieg')
                pick=f.locator('#spur-wahl');reach(f,pick);pick.select_option(index=1)
                field=f.locator('#spur-grund');reach(f,field);field.fill(INITIAL)
                touch(f,'#spur-hilfe');touch(f,'#material-zurueck' if day=='02' else '#dismiss')
                assert field.input_value()==INITIAL
                capture('Erster-Grund');touch(f,'#spur-speichern')
                s.locator('[data-action=abschluss]').tap()
                capture('Abschluss')
                pick=f.locator('#spur-wahl');reach(f,pick);pick.select_option(index=1)
                field=f.locator('#spur-grund');reach(f,field);field.fill('Die Pille schützt vor HIV. Die Kupferspirale enthält Hormone.')
                touch(f,'#spur-speichern')
                for text in ('HIV','ohne Hormone'):expect(f.locator('.spur-korrektur')).to_contain_text(text)
                touch(f,'#spur-hilfe')
                for _ in range(4):touch(f,'#spur-mehr')
                helptext=f.locator('dialog[open]').inner_text()
                assert 'HIV' in helptext and 'ohne Hormone' in helptext
                touch(f,'#material-zurueck' if day=='02' else '#dismiss')
                reach(f,field);field.fill(FINAL);touch(f,'#spur-speichern')
                expect(f.locator('#lernspur')).to_contain_text(INITIAL);expect(f.locator('#lernspur')).to_contain_text(FINAL)
                capture('Vergleich');touch(f,'#spur-aendern')
                assert f.locator('#spur-grund').input_value()==FINAL
                touch(f,'#spur-speichern');touch(f,'#spur-fertig')
                assert not context.storage_state()['origins']
                video=p.video;context.close()
                if demo:video.save_as(folder/'Lernweg.webm')
            # Jedes geordnete Paar bei eigener Erst- und Schlusseingabe, ohne Rückschluss auf Lernerfolg.
            p=browser.new_page(viewport={'width':1180,'height':820},has_touch=True);notice(p)
            for before in range(1,5):
                for after in range(1,8 if day=='02' else 5):
                    s,f=begin(p,file.as_uri());antwort(f,INITIAL,before)
                    s.locator('[data-action=abschluss]').tap();antwort(f,FINAL,after)
                    labels=f.locator('.spur-arbeit strong').all_text_contents()
                    assert len(labels)==2 and f.locator('.spur-zitat').all_text_contents()==[INITIAL,FINAL]
                    pairs.append([before,after,*labels])
            tests=json.loads((HERE/'Freitext-Gegenbestand.json').read_text())
            diagnostics=[]
            for text,expected in tests:
                if day=='02' and any(k in text.lower() for k in ('abbruch','schmerzfrei','schwanger werden')):continue
                issue=f.evaluate('text=>'+('Entwurf.fehler(text)' if day=='02' else 'medizin(text)'),text)
                result=issue and issue['info']
                assert bool(result)==bool(expected) and all(term in result or (term=='Schmerzen' and 'wehtun' in result) for term in expected),(text,expected,result)
                diagnostics.append([text,expected,result])
            # Alle bisherigen unabhängigen Vorbereitungsantworten auf falsche Fehlermeldungen prüfen.
            pool=json.loads(gzip.decompress((HERE/'Gegenpruefung-CLT.json.gz').read_bytes()))
            outputs=f.evaluate('texts=>texts.map(t=>'+('Entwurf.fehler(t)' if day=='02' else 'medizin(t)')+'?.info||null)',[r['text'] for r in pool])
            for r,issue in zip(pool,outputs):
                assert not(issue and r['expected'] in ('passend','vollständig richtig')),(r,issue)
            with gzip.open(folder/'Altbestand.json.gz','wt',encoding='utf8') as out:
                json.dump([dict(**r,ub_rueckmeldung=v) for r,v in zip(pool,outputs)],out,ensure_ascii=False)
            assert not errors,errors
    (folder/'Lernspuren.json').write_text(json.dumps(dict(revision_html=hashlib.sha256(file.read_bytes()).hexdigest(),
        tag=day,browser=engine,niveau=tier,ansichten=rows,antwortpaare=pairs,gegenbestand=diagnostics,
        altbestand=len(pool),fehler=errors),ensure_ascii=False,indent=2))
if __name__=='__main__':
    import sys
    run(*sys.argv[1:])
