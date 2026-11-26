"""Teste die tatsächlichen HTML-/SCO-Ansichten mit zwei Browsern und einem lokalen LMS."""
import argparse
import functools
import json
import os
from pathlib import Path
import sys
import re
import tempfile
import subprocess
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from zipfile import ZipFile
from lxml import etree,html
from playwright.sync_api import sync_playwright


from feldabgleich import pruefe
from erstellen import HERE,ROOT,OUT,START,sha,reference
QA=ROOT/'build/Kartenlernen'
sys.path.insert(0,str(ROOT/'gesamt'))
from karten import printed,LEVELS,NUM,spaced
HOST='''<!doctype html><meta charset="utf-8"><style>*{box-sizing:border-box}body{margin:0}iframe{border:0;width:100vw;height:calc(100dvh - 54px);display:block}p{height:54px;margin:0}</style><p>Test-Lernplattform</p><script>window.calls=[];window.API={LMSInitialize(x){calls.push(['Start',x]);return 'true'},LMSFinish(x){calls.push(['Ende',x]);return 'true'},LMSSetValue(){throw Error('Speicherzugriff')}};</script><iframe title="Vorbereitung" src="index.html"></iframe>'''
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass


def protected(folder):
    subprocess.run(['git','diff','--exit-code',START,'--','02-12.html','index.html','app','assets','data','gesamt','module','scorm','scripts','tagesauswahl','vorbereitung'],cwd=ROOT,check=True)
    with ZipFile(ROOT/'gesamt/kompakt/Kompakt-Abnahmenachweise.zip') as z:
        sums={n:h for h,n in (l.split('  ') for l in z.read('Programmdateien.sha256').decode().splitlines())}
    out={}
    for name,h in sums.items():
        assert sha((folder/name).read_bytes())==h,name
        out[name]=h
    raw=(OUT/'Vorbereitung.html').read_bytes()
    doc=html.fromstring(raw)
    assert not doc.xpath('//script[@src or @type="application/octet-stream"]|//link[@href]|//iframe|//input|//textarea')
    assert not any(s in raw.decode() for s in ('Laufzettel','Code prüfen','Lauras Frage','Nachricht senden','Fallakte Laura'))
    cards,old=reference()
    checked=printed()
    from base64 import b64decode
    old_dom=html.fromstring((folder/'Fallakte-Vorbereitung.html').read_bytes())
    ref_bank=json.loads(html.fromstring(b64decode(old_dom.get_element_by_id('modul-vor').text)).get_element_by_id('material').text)
    m=json.loads(doc.get_element_by_id('material').text);results=[]
    with ZipFile(OUT/'Kartenvertrag-Work.zip') as z:work=json.loads(z.read('Kartenvertrag.json'))
    for t in LEVELS:
        actual=m['levels'][t]['cards'];assert actual==work['niveaus'][t]
        for n,(c,r,w) in enumerate(zip(actual,ref_bank['cards'][t],cards[t]),1):
            assert c['ueberschrift']==f'Kapitel {n} – '+r['title']
            assert c['pearl']==r['pearlIndex'] and c['pearl_erklaerung']==r['pearlExplanation']
            assert [f['wort'] for f in c['felder']]==[f['answer'] for f in r['fields']]
            assert [f['volltext'] for f in c['texte']]==[s['completedText'] for s in r['sections']]
            assert [f['lueckentext'] for f in c['texte']]==[s['template'] for s in w['sections']]
            if (t,n) in {('ESA',2),('AHR',3),('AHR',4)}:
                assert c['felder'][1]['wort']=='kein STI-Schutz'
                assert '*kein STI-Schutz*' in m['levels'][t]['info'][n-1][0]['text'][1]
            paper=checked[t,w['method']]
            assert paper['page']==(1 if n<=2 else 2)
            text=r['title']+' Pearl-Index: '+r['pearlIndex']+' · Richtwert nach pro familia '+r['pearlExplanation']+' Kein Maß für den Schutz vor sexuell übertragbaren Infektionen (STI). '+' '.join(s['title']+' '+s['completedText'] for s in r['sections'])
            # Originaldruck hat ein eigenes Pearl-Layout. Die Funktion kontrolliert
            # zusätzlich jede einzelne nummerierte Lücke unabhängig anhand beider PDFs.
            norm=lambda s:re.sub(r' +([,.;:])',r'\1',spaced(s))
            filled=NUM.sub(lambda x:x[1]+' '+c['felder'][int(x[1])-1]['wort'],paper['blank'])
            assert norm(filled)==norm(paper['reference'])
            assert norm(text)==norm(r['title']+' '+NUM.sub('',paper['reference']))
            results.append(dict(niveau=t,kapitel=n,felder=[f['wort'] for f in c['felder']],druck=paper['reference_sha256'],schueler=paper['student_sha256']))
    return dict(bestandsdateien=out,karten=results)


def run(reference_folder,quick=False):
    QA.mkdir(exist_ok=True,parents=True)
    report=protected(reference_folder)
    belege={}
    with ZipFile(OUT/'Kartenvertrag-Work.zip') as z:
        karten=json.loads(z.read('Kartenvertrag.json'))['niveaus']
    records=[];specs=[(1024,768,100,False),(768,1024,100,False),(1180,820,150,False),(820,1180,150,False),(740,480,100,True),(740,480,150,True),(640,420,125,True),(390,560,125,True)]
    if quick:specs=specs[-2:]
    with tempfile.TemporaryDirectory() as temp,sync_playwright() as pw:
        folder=Path(temp)
        with ZipFile(OUT/'Vorbereitung-SCORM12.zip') as z:
            assert z.testzip() is None
            assert set(z.namelist())=={'imsmanifest.xml','index.html',*(p.name for p in (ROOT/'scorm').glob('*.xsd'))}
            z.extractall(folder)
        assert (folder/'index.html').read_bytes()==(OUT/'Vorbereitung.html').read_bytes()
        manifest=etree.parse(str(folder/'imsmanifest.xml'))
        etree.XMLSchema(etree.parse(str(folder/'adlcp_rootv1p2.xsd'))).assertValid(manifest)
        assert manifest.xpath('string(//*[local-name()="schemaversion"])')=='1.2'
        (folder/'host.html').write_text(HOST)
        server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=folder))
        thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        url='http://127.0.0.1:'+str(server.server_port)+'/host.html'
        for engine in (['chromium'] if quick else ['chromium','webkit']):
            with getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as browser:
                for w,h,zoom,sco in specs:
                    ctx=browser.new_context(viewport={'width':w,'height':h+54 if sco else h},has_touch=True)
                    page=ctx.new_page();issues=[];addresses=[]
                    page.on('pageerror',lambda e:issues.append(str(e)))
                    page.on('request',lambda r:addresses.append(r.url))
                    for tier in LEVELS:
                        for assisted in (False,True):
                            page.goto(url if sco else (OUT/'Vorbereitung.html').as_uri())
                            f=page.frames[-1];f.locator('#page button').first.wait_for()
                            f.evaluate('(z)=>document.documentElement.style.fontSize=z+"%"',zoom)
                            f.evaluate('async()=>{await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))}')
                            result=f.evaluate((HERE/'sichttest.js').read_text(),dict(tier=tier,assist=assisted))
                            befund=result.pop('quellen')
                            assert len(befund)==16
                            pruefe(befund,karten[tier])
                            assert belege.setdefault(tier,befund)==befund
                            records.append(dict(browser=engine,version=browser.version,breite=w,hoehe=h,schrift=zoom,scorm=sco,**result))
                            if result['errors']:print('Layout',engine,tier,w,h,zoom,result['errors'][:2],flush=True)
                            assert f.evaluate('!document.querySelector("input,textarea,select")')
                            if sco:
                                assert f.evaluate('!localStorage.length && !sessionStorage.length')
                                assert page.evaluate('calls')==[['Start','']]
                                page.locator('iframe').evaluate("el=>el.src='about:blank'")
                                page.wait_for_function("calls.length===2");assert page.evaluate('calls')==[['Start',''],['Ende','']]
                    assert not issues,issues
                    assert all(a.startswith(('file:','data:','about:','http://127.0.0.1:')) for a in addresses),addresses
                    assert not ctx.cookies() and not ctx.storage_state()['origins']
                    ctx.close()
                    print(engine,w,h,zoom,'fertig',flush=True)
        server.shutdown();server.server_close()
    report['wege']=records
    report['feldbelege']=[feld for niveau in LEVELS for feld in belege[niveau]]
    assert len(report['feldbelege'])==64
    (QA/('Layout-Schnelltest.json' if quick else 'Browserpruefung.json')).write_text(json.dumps(report,ensure_ascii=False))
    assert not any(r['errors'] for r in records),'Layoutfehler im JSON'

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('bestand',type=Path);p.add_argument('--kurz',action='store_true')
    a=p.parse_args();run(a.bestand,a.kurz)
