"""Compose the approved modules from the actual reviewed release of December 8."""
import base64, hashlib, io, json, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from modul_0212 import ROOT, OUT, build, commit
from uebung import build as build_practice

DAY8='5d27cc3d61db386468d3f851347690b33b5d86fe'
REF=ROOT/'build'/('Tag08-'+DAY8)
TARGET=ROOT/'dist/Vorabkandidat'
def digest(data):return hashlib.sha256(data).hexdigest()

def prepare_reference():
    REF.mkdir(parents=True,exist_ok=True)
    raw=subprocess.check_output(['git','archive','--format=zip',DAY8,'index.html','02-12.html',
        'app','assets','data','scorm','module','tagesauswahl','scripts','tests'],cwd=ROOT)
    with ZipFile(io.BytesIO(raw)) as z:z.extractall(REF)
    subprocess.run([sys.executable,'scripts/build.py'],cwd=REF,check=True)
    return REF/'dist/Version-B'

def assemble():
    first=build().read_bytes();build_practice()
    released=prepare_reference()
    shell=(released/'Fallakte.html').read_bytes()
    second=(REF/'build/08-12/Fallakte.html').read_bytes()
    assert digest(second)=='a0588500259cc6255462d8670f3aa08c396730a1c7bdf6a37d34b82434839609'
    def slot(day):
        matches=re.findall(rb'<script id="modul-'+day+rb'" type="application/octet-stream">([A-Za-z0-9+/=]+)</script>',shell)
        assert len(matches)==1
        return matches[0]
    assert base64.b64decode(slot(b'08'),validate=True)==second
    old=slot(b'02');assert shell.count(old)==1
    candidate=shell.replace(old,base64.b64encode(first))
    assert len(candidate)<10_000_000
    TARGET.mkdir(parents=True,exist_ok=True)
    (TARGET/'Fallakte.html').write_bytes(candidate)
    with ZipFile(released/'Fallakte-SCORM12.zip') as original,ZipFile(TARGET/'Fallakte-SCORM12.zip','w',ZIP_DEFLATED) as output:
        assert original.read('index.html')==shell
        for member in original.namelist():output.writestr(member,candidate if member=='index.html' else original.read(member))
    metadata=dict(build_utc=datetime.now(timezone.utc).isoformat(),commit=commit(),tag08=DAY8,tag08_sha256=digest(second),tag02_sha256=digest(first),html_sha256=digest(candidate),bytes=len(candidate))
    (TARGET/'Buildnachweis.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(TARGET,metadata['bytes'])
if __name__=='__main__':assemble()
