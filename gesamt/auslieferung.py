"""Build four staged deliveries from the checksum-pinned, independently usable releases."""
import argparse
import base64
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'gesamt'
OUT=ROOT/'dist/Gesamt'
QA=ROOT/'build/Gesamtpruefung'
REF=ROOT/'build/Gesamtreferenzen'
sys.path.insert(0,str(ROOT/'vorbereitung'))
from bauen import pack, json_text, revision
from build import manifest, single_replace

PREP='7f26cd7b2fbb2477b3a810eb6437f90293385ae5'
JOINT='d24308f4a0eca8ed39f0f75b04b890b78bcc8332'
FIRST='8b50305b6d98a19e1771a842ea9917c67282ecb9'
MOD_HASH={'02':'6f969460d00005fefd27fed985b6c95b7f1203bee0a9e4d72fcaaf9aea605cb2',
          '08':'0606de0b43bcbe4ef28b9fb0b036ee6ae1a8179d855b6af47baa5246438f1d2f'}
VERSIONS={'Vorbereitung':('vor',),'02-12':('vor','02'),'08-12':('vor','02','08'),'Gesamt':('vor','02','08')}
PAYLOAD=r'<script id="modul-(02|08)" type="application/octet-stream">([A-Za-z0-9+/=]+)</script>'
PRINT=SRC/'Materialpaket_Proberunde_26-11-2026_Druckversion.zip'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def rebuild(commit,script,directory):
    path=REF/commit
    if not path.exists():
        path.parent.mkdir(exist_ok=True,parents=True)
        subprocess.run(['git','clone','--quiet','--shared','--no-checkout',str(ROOT),str(path)],check=True)
        subprocess.run(['git','checkout','--quiet','--detach',commit],cwd=path,check=True)
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=path,text=True).strip()==commit
    subprocess.run(['git','diff','--exit-code','HEAD'],cwd=path,check=True)
    subprocess.run([sys.executable,script],cwd=path,check=True)
    return path/'dist'/directory

def embedded_preparation(raw):
    assert sha(raw)=='5478c3c93d80ed5c3b368257a2754f5e585eefd63c9fd3cc74860b93bd75d49b'
    page=raw.decode()
    # The printed full card has two header statements missed by the standalone renderer.
    page=single_replace(page,'Pearl-Index · ${esc(card.pearlIndex)}</strong> ${esc(card.pearlExplanation)}</p>',
        'Pearl-Index: ${esc(card.pearlIndex)} · Richtwert nach pro familia</strong> ${esc(card.pearlExplanation)} '
        'Kein Maß für den Schutz vor sexuell übertragbaren Infektionen (STI).</p>')
    page=single_replace(page,'Sind alle vier Karten vollständig? Dann schneide sie jetzt aus. Bewahre sie für den Unterrichtsbesuch auf.',
        'Sind die Einträge zu allen vier Methoden vollständig? Schneide die Infokarten an der gestrichelten Linie aus und bewahre sie für den Unterrichtsbesuch auf.')
    adapter=(ROOT/'tagesauswahl/sitzung.js').read_text()
    page=single_replace(page,'<script>'+adapter+'</script>','<script>'+(SRC/'navigation.js').read_text()+'</script>')
    return page.encode()

def build(prep,joint):
    raw=(joint/'Fallakte.html').read_bytes()
    assert sha(raw)=='254e5d06cb9190250bacc63fa9eea6c118846b45ce2b305ffa640d766f44a820'
    shell=raw.decode()
    modules={k:base64.b64decode(b,validate=True) for k,b in re.findall(PAYLOAD,shell)}
    assert {k:sha(v) for k,v in modules.items()}==MOD_HASH
    modules['vor']=embedded_preparation((prep/'Vorbereitung.html').read_bytes())
    shell=re.sub(PAYLOAD,'',shell)
    shell=single_replace(shell,'<div class="tage">','''<div class="tage">
      <h2 class="vorbereitung"><button class="tag" id="vorbereitung" data-modulnavigation data-entry="modul-vor">
        <span class="beschriftung">Vorbereitung – Verhütungsmethoden<span class="zeichen" aria-hidden="true"></span></span>
      </button></h2>''')
    shell=single_replace(shell,'id="zweiter-tag"','id="zweiter-tag" data-modulnavigation')
    shell=single_replace(shell,'</style>','''.vorbereitung{grid-column:1/-1}
.vorbereitung .tag{display:block}.vorbereitung .beschriftung{flex-direction:row;align-items:center}
.beschriftung{overflow-wrap:anywhere}.tag{min-height:44px}
</style>''')
    shell=single_replace(shell,'</head>',f'<meta name="revision" content="{revision()}"></head>')
    OUT.mkdir(parents=True,exist_ok=True)
    for version,allowed in VERSIONS.items():
        page=shell
        for key in modules.keys()-set(allowed):
            page=single_replace(page,f'data-entry="modul-{key}"','disabled')
        data=''.join(f'<script id="modul-{key}" type="application/octet-stream">{base64.b64encode(modules[key]).decode()}</script>' for key in allowed)
        html=single_replace(page,'</body>',data+'</body>').encode()
        stem='Fallakte-'+version
        (OUT/(stem+'.html')).write_bytes(html)
        files={p.name:p.read_bytes() for p in (ROOT/'scorm').glob('*.xsd')}
        files.update({'index.html':html,'imsmanifest.xml':manifest(version.upper()).replace(b'>Fallakte.<',('>Fallakte - '+version+'<').encode())})
        pack(OUT/(stem+'-SCORM12.zip'),files)
    QA.mkdir(exist_ok=True,parents=True)
    (QA/'Module.json').write_text(json_text({k:sha(v) for k,v in modules.items()}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vorbereitung',type=Path)
    parser.add_argument('--unterricht',type=Path)
    args=parser.parse_args()
    build(args.vorbereitung or rebuild(PREP,'vorbereitung/bauen.py','Vorbereitung'),
          args.unterricht or rebuild(JOINT,'scripts/familienrat_build.py','Familienrat'))
