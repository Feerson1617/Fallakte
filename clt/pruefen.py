"""Fachlich unterschiedliche UI-Übergänge im ausgelieferten Unterrichtsmodul auslösen."""
import argparse,gzip,json,os,sys
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'gesamt'),str(ROOT/'tests')]
from auslieferung import OUT,sha
from tagesauswahl import HOST,host
from lernspur_test import antwort,schluss
from ergonomie import room
HERE=Path(__file__).parent
QA=ROOT/'build/CLT'
LEVELS=('Förder','ESA','MSA','AHR')
NAMES=('Mutter','Freundin','Großmutter','Vater')


PROFILES={'quer':(1180,820,100),'hoch':(820,1180,150),'kurs':(640,420,125),'schmal':(390,600,125),'tastatur':(740,340,150)}

def run(engine,day,tier,profil='quer'):
    width,height,zoom=PROFILES[profil]
    label=f'{day}-{tier}-{engine}';folder=QA/label/profil;folder.mkdir(parents=True,exist_ok=True)
    path=OUT/f'Fallakte-{day}-12.html';package=OUT/f'Fallakte-{day}-12-SCORM12.zip'
    observed={};counts=Counter();errors=[];layout=[]
    with TemporaryDirectory() as temp,sync_playwright() as pw:
        site=Path(temp)
        with ZipFile(package) as z:z.extractall(site)
        assert (site/'index.html').read_bytes()==path.read_bytes()
        (site/'host.html').write_text(HOST)
        with host(site) as url,getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as b:
            p=b.new_page(viewport={'width':width,'height':height},has_touch=True);p.set_default_timeout(4500)
            p.on('pageerror',lambda e:errors.append(str(e)));p.on('dialog',lambda d:d.accept())
            def instrument(f):
                f.evaluate('z=>{document.documentElement.style.fontSize=z+"%";Arbeitsplatz.refresh()}',zoom)
                f.evaluate((HERE/'geometrie.js').read_text());f.evaluate((HERE/'probe.js').read_text())
            def open_module(sco):
                p.goto(url+'/host.html' if sco else path.as_uri())
                if sco:
                    p.frame_locator('[name=sco]').locator('#erster-tag').wait_for()
                s=p.frame(name='sco') if sco else p.main_frame
                f=room(s,'erster' if day=='02' else 'zweiter')
                f.locator('.arbeitskopf:visible').wait_for();instrument(f)
                return s,f
            def harvest(f):
                for r in f.evaluate('cltTest.records()'):
                    observed[json.dumps(r,ensure_ascii=False,sort_keys=True)]=r
                f.evaluate('cltTest.clear()')
                layout.append(f.evaluate('()=>{const x=geometrieStand(),v=structuredClone(x);x.issues=[];x.seiten=[];x.screens=0;x.checks=0;return v;}'))
            if day=='02':
                t=tier.replace('Förder','Foerder')
                for mode in ('eigen','beispiel'):
                    s,f=open_module(mode=='beispiel')
                    for stage,methods in f.evaluate('t=>Object.fromEntries(Object.entries(LAURA.stages).map(([k,v])=>[k,Object.keys(v.levels[t].strategies)]))',t).items():
                        for method in methods:
                            s.locator('[data-action=recovery]').click()
                            f.locator('#wieder-level-'+t).click();f.locator('[data-stage="'+stage+'"][type=button]').click()
                            counts['Fachantworten']+=f.evaluate('x=>cltTest.advice(x)',dict(stage=stage,tier=t,method=method,mode=mode))
                            counts['Empfehlungswege']+=1;harvest(f)
                            if stage=='L04' and method=='K' and mode=='beispiel':p.screenshot(path=folder/'Laura.jpg',quality=62)
                    s.locator('[data-action=abschluss]').click();expect(f.locator('#lernspur h1')).to_have_text('Dein Schlussrat')
                # Regulärer Verlauf einschließlich des Übergangs zum ausdrücklich persönlichen Schlussrat.
                s,f=open_module(False);f.locator('#level-'+t).click();f.locator('#neu').click();antwort(f)
                for i in range(1,6):
                    f.evaluate('x=>cltTest.advice(x)',dict(tier=t,stage=f'L0{i}',method='K',mode='eigen'))
                    assert f.locator('#chat-meldungen [data-kind=send]').count()==i
                    if i<5:f.locator('#beratung-weiter').click()
                s.locator('[data-action=home]').click();assert not f.locator('[data-optional=Tom]').is_visible()
                f.locator('#weiterarbeiten').click();f.locator('#beratung-fertig').click();schluss(f)
                assert f.locator('[data-optional=Tom]').is_enabled()
                for person,stages in [('Tom',3),('Celina',5)]:
                    for at in range(stages):
                        s.locator('[data-action=recovery]').click();f.locator('#wieder-level-'+t).click()
                        f.locator('#wiederfall').get_by_role('button',name=person,exact=True).click()
                        f.locator('#abschnitte button').nth(at).click()
                        child=f.locator('#rahmen-reserve-'+person).element_handle().content_frame()
                        child.locator('#step').wait_for();instrument(child)
                        child.evaluate('v=>cltTest.label(v)',person+' '+str(at+1))
                        if child.locator('[id^=method-]').count():
                            child.locator('#source').click();child.locator('#karte-K').click();child.locator('#back').click();child.locator('#back').click()
                        counts['Zusatzantworten']+=child.evaluate((HERE/'reserve.js').read_text(),t)
                        harvest(child)
                s.locator('#zurueck').click()
            else:
                def picker(s,f,person,step):
                    s.locator('[data-action=recovery]').click()
                    if f.locator('#level-0').input_value()!=tier:f.locator('#level-0').select_option(tier)
                    if person in NAMES[2:] and not f.locator('#person option').filter(has_text=person).count():
                        s.locator('[data-action=abschluss]').click();schluss(f)
                        s.locator('[data-action=recovery]').click()
                    f.locator('#person').select_option(person);f.locator('#entry').select_option(str(step));f.locator('#open-entry').click()
                for mode in ('eigen','fehler','hilfe','beispiel'):
                    s,f=open_module(mode in ('fehler','beispiel'))
                    for name in NAMES:
                        picker(s,f,name,0)
                        counts['Fachantworten']+=f.evaluate('x=>cltTest.family(x)',dict(person=name,tier=tier,mode=mode))
                        counts['Familienwege']+=1;harvest(f)
                    if mode=='beispiel':p.screenshot(path=folder/'Familie.jpg',quality=62)
                # Alle Gewichtungen und Kombinationen beider Anliegen; unpassende Fakten und alternative Begründungen.
                for weight in range(4):
                    combos=((0,),(1,)) if weight<2 else ((0,0),(0,1),(1,0),(1,1))
                    for concerns in combos:
                        s,f=open_module(bool(sum(concerns)%2));picker(s,f,'Lauras Frage',2)
                        f.evaluate('x=>cltTest.evaluateWeight(x)',dict(weight=weight,concerns=concerns,errors=True));counts['Gewichtungen']+=1;harvest(f)
                s,f=open_module(False);f.locator('#level-0').select_option(tier);f.locator('#start').click();antwort(f)
                for name in NAMES[:2]:
                    f.evaluate('x=>cltTest.family(x)',dict(person=name,tier=tier,mode='eigen'))
                f.locator('#next').click()
                f.evaluate('x=>cltTest.evaluateWeight(x)',dict(weight=3,concerns=[1,0],errors=True))
                schluss(f);expect(f.locator('#open-Großmutter')).to_be_enabled();harvest(f)
                s,f=open_module(True);picker(s,f,'Freundin',3)
                expect(f.locator('#app .arbeitskopf')).to_contain_text('Freundin')
                s.locator('[data-action=abschluss]').click()
                schluss(f);assert not f.locator('#lernspur').count()
                assert not errors,errors
            # Die ausgelieferte SCORM-Hülle darf nur die Sitzung öffnen und beenden.
            s,f=open_module(True)
            assert p.evaluate('calls')==[['LMSInitialize','']]
            p.locator('[name=sco]').evaluate("e=>e.src='about:blank'")
            p.wait_for_function("calls.length>=2");assert p.evaluate('calls')==[['LMSInitialize',''],['LMSFinish','']]
            assert not p.context.cookies() and not p.context.storage_state()['origins']
            assert not errors,errors
    (folder/'Geometrie.json').write_text(json.dumps(layout,ensure_ascii=False))
    with gzip.open(folder/'Zustaende.json.gz','wt',encoding='utf8') as z:json.dump(list(observed.values()),z,ensure_ascii=False)
    (folder/'Pruefung.json').write_text(json.dumps(dict(html_sha256=sha(path.read_bytes()),modul=day,niveau=tier,browser=engine,zaehlungen=counts,zustaende=len(observed)),ensure_ascii=False,indent=2))
    print(label,counts,len(observed),flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('browser',choices=['chromium','webkit']);a.add_argument('tag',choices=['02','08']);a.add_argument('niveau',choices=LEVELS);a.add_argument('--profil',choices=PROFILES,default='quer');args=a.parse_args();run(args.browser,args.tag,args.niveau,args.profil)
