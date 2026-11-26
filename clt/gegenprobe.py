"""Unabhängig vorgegebenes Freitext-Gegenbeispiel auf sämtlichen Laura-Methodenwegen."""
from pathlib import Path
from zipfile import ZipFile
import base64,hashlib,json,os,re,sys
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
def pruefen(engine):
    folder=ROOT/'dist/Gesamt'
    with ZipFile(folder/'Fallakte-02-12-SCORM12.zip') as z:
        raw=z.read('index.html')
    assert raw==(folder/'Fallakte-02-12.html').read_bytes()
    page=base64.b64decode(re.search(rb'<script id="modul-02"[^>]*>([^<]+)',raw)[1]).decode()
    out=[]
    with sync_playwright() as pw,getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as b:
        p=b.new_page();p.on('dialog',lambda d:d.accept());p.set_content(page)
        for tier in ('MSA','AHR'):
            stages=p.evaluate('t=>Object.fromEntries(Object.entries(LAURA.stages).map(([k,s])=>[k,Object.keys(s.levels[t].strategies)]))',tier)
            for stage,items in stages.items():
                for method in items:
                    out.append(p.evaluate((HERE/'entwurfswege.js').read_text(),dict(tier=tier,stage=stage,method=method)))
        for text in ['Die Pille schützt nicht vor HIV.','Schützt die Pille vor HIV?', '„Die Pille schützt vor HIV.“ ist falsch.', 'Die Pille schützt vor HIV. Das ist falsch.','Laura ist Selbstbestimmung wichtig.']:
            assert not p.evaluate('text=>Entwurf.fehler(text)',text),text
        def extracted(doc, key):
            return base64.b64decode(re.search(r'<script id="'+key+r'"[^>]*>([^<]+)',doc)[1]).decode()
        with ZipFile(folder/'Fallakte-08-12-SCORM12.zip') as z:family_raw=z.read('index.html')
        assert family_raw==(folder/'Fallakte-08-12.html').read_bytes()
        family=extracted(family_raw.decode(),'modul-08')
        extra=[]
        for tag,persons in [('08',['Mutter','Freundin','Großmutter','Vater']),('02',['Tom','Celina'])]:
            for name in persons:
                p.goto('about:blank')
                p.set_content(family if tag=='08' else extracted(page,'reserve-'+name))
                if tag=='02':p.evaluate('window.setTierForTest = value => {tier=value;}')
                for level in ('MSA','AHR'):
                    extra.extend(p.evaluate((HERE/'entwurfsvergleich.js').read_text(),dict(name=name,tier=level,tag=tag)))
    assert len(out)==70 and sum(r['sendbar'] for r in out)==46
    dst=ROOT/'build/CLT/Gegenpruefung';dst.mkdir(parents=True,exist_ok=True)
    (dst/f'Entwuerfe-{engine}.json').write_text(json.dumps(dict(html_sha256=hashlib.sha256(raw).hexdigest(),wege=out,zusaetzliche_wege=extra,familien_html_sha256=hashlib.sha256(family_raw).hexdigest()),ensure_ascii=False))
if __name__=='__main__':pruefen(sys.argv[1])
