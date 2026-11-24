"""Baut die separate Vorbereitung aus dem unveränderten Planungspaket."""
import base64
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from abbildungen import render_visuals

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent
sys.path.insert(0, str(ROOT/'scripts'))
from build import manifest

OUT = ROOT/'dist/Vorbereitung'
QA = ROOT/'build/Vorbereitung-QA'
PLAN = SRC/'Stationsplanung.zip'


def revision():
    return subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def pack(path, entries):
    with ZipFile(path,'w') as z:
        for name, raw in sorted(entries.items()):
            z.writestr(ZipInfo(name),raw,compress_type=ZIP_DEFLATED)


def contracts():
    with ZipFile(PLAN) as z:
        assert z.testzip() is None
        s=json.loads(z.read('Stationsvertrag.json'))
        raw=z.read('Kartenvertrag.json')
        assert digest(raw)==s['cardContractSHA256']
        return s,json.loads(raw)


def build():
    s,c=contracts()
    # Die Alt-Falltexte und die Lehrer-Lösungsschlüssel der PDF-Vorlagen
    # gehören nicht in die Oberfläche. Vollkarten benötigen nur die Nutzdaten.
    cards={level:[{k:card[k] for k in ('method','title','pearlIndex','pearlExplanation','fields')} |
                   {'sections':[{k:section[k] for k in ('title','completedText')} for section in card['sections']]}
                   for card in methods] for level,methods in c['levels'].items()}
    material={k:s[k] for k in ('title','levels','ui','visualBriefs','pearlNote')}
    material.update(cards=cards,graphics=render_visuals(s['visualBriefs']))
    css=(SRC/'style.css').read_text()
    for token,name in [('FONT_SANS','dmsans.ttf'),('FONT_SERIF','dmseriftext.ttf')]:
        css=css.replace(token,'data:font/ttf;base64,'+base64.b64encode((ROOT/'assets'/name).read_bytes()).decode())
    values={'STYLES':css,'MATERIAL':json.dumps(material,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'),
            'SCORM_JS':(ROOT/'tagesauswahl/sitzung.js').read_text(),'APP_JS':(SRC/'app.js').read_text(),
            'LICENSES':'\n'.join(p.read_text() for p in sorted((ROOT/'assets').glob('*-OFL.txt'))),'REVISION':revision()}
    html=re.sub('|'.join(values),lambda m:values[m[0]],(SRC/'index.html').read_text()).encode()
    OUT.mkdir(exist_ok=True,parents=True)
    (OUT/'Vorbereitung.html').write_bytes(html)
    entries={p.name:p.read_bytes() for p in sorted((ROOT/'scorm').glob('*.xsd'))}
    entries.update({'index.html':html,'imsmanifest.xml':manifest('VORBEREITUNG').replace(b'>Fallakte.<',b'>Fallakte - Vorbereitung<')})
    pack(OUT/'Vorbereitung-SCORM12.zip',entries)


if __name__=='__main__':
    build()
