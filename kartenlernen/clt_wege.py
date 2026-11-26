"""Alle bekannten Diagnoseprofile und geschlossenen Antworten im gebauten Lernweg."""
import gzip,json,os,sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from playwright.sync_api import sync_playwright
from erstellen import HERE,OUT,ROOT,sha
from pruefen import QA


def pruefen():
    with ZipFile(OUT/'Feedback-Testkatalog.zip') as z:cases=json.loads(z.read('Ergebnisse.json'))
    groups={}
    for r in cases:
        key=(r['niveau'],r['kapitel'],r.get('choice'),json.dumps(r['diagnose'],sort_keys=True))
        groups.setdefault(key,[]).append(r.get('choice',r.get('text')))
    script=(HERE/'clt_wege.js').read_text()
    states={}
    with TemporaryDirectory() as temp,sync_playwright() as pw:
        site=Path(temp)
        with ZipFile(OUT/'Vorbereitung-SCORM12.zip') as z:z.extractall(site)
        assert (site/'index.html').read_bytes()==(OUT/'Vorbereitung.html').read_bytes()
        for engine in ('chromium','webkit'):
            with getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as b:
                p=b.new_page(viewport={'width':740,'height':480},has_touch=True)
                for (tier,chapter,choice,signature),samples in groups.items():
                    signature=json.loads(signature)
                    for retry in ((False,True) if signature['state']!='passend' else (False,)):
                        p.goto(((site/'index.html') if engine=='webkit' else OUT/'Vorbereitung.html').as_uri())
                        p.evaluate("async()=>{document.documentElement.style.fontSize='125%';await document.fonts.ready}")
                        # Inhalt und Länge der Antwort bleiben als Parameter im Protokoll erhalten.
                        sample=max(samples,key=len)
                        rows=p.evaluate(script,dict(tier=tier,task=chapter-1,sample=sample,repeat=retry))
                        for phase,screen,text in rows:
                            key=(engine,tier,chapter,phase,screen,text)
                            states.setdefault(key,[]).append(dict(diagnose=signature,eingabe=sample,wiederholt=retry))
    paths=[dict(browser=e,niveau=t,kapitel=c,phase=z,ansicht=s,text=text,ausloeser=cases) for (e,t,c,z,s,text),cases in states.items()]
    raw=json.dumps(dict(html_sha256=sha((OUT/'Vorbereitung.html').read_bytes()),profile=len(groups),zustaende=paths),ensure_ascii=False).encode()
    (QA/'CLT-Lernwege.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    return paths
