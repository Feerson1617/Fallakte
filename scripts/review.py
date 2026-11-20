"""Package evidence for the same standalone HTML that passed the browser suite."""
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
QA = OUT / 'qa'
local = OUT / 'Fallakte.html'
digest = hashlib.sha256(local.read_bytes()).hexdigest()
names = ('dialogwege', 'scorm', 'bedienung')
reports = {}
for name in names:
    reports[name] = json.loads((QA / (name + '.json')).read_text())
    if reports[name]['html_sha256'] != digest:
        raise SystemExit('Prüflauf gehört zu einer anderen HTML-Version: ' + name)

paths = reports['dialogwege']['paths']
views = reports['bedienung']['runs']
assert len(paths) == 84 and len(views) == 8
assert reports['scorm']['schema_valid']
assert {view['engine'] for view in views} == {'chromium','webkit'}
assert all(not row['errors'] and not row['external_requests'] for row in views)
assert not reports['dialogwege']['errors']
with ZipFile(OUT/'Fallakte-SCORM12.zip') as scorm:
    assert hashlib.sha256(scorm.read('index.html')).hexdigest() == digest

package = OUT / 'Fallakte-Sichtpruefung.zip'
with ZipFile(package, 'w', ZIP_DEFLATED) as z:
    z.write(local, 'Fallakte.html')
    z.write(ROOT/'docs/Abnahme.md', 'Pruefbericht.md')
    z.write(ROOT/'docs/Fachpruefung.md', 'Fachquellen.md')
    for name in names:
        z.write(QA/(name+'.json'), 'Protokolle/'+name+'.json')
    for shot in ('Falluebersicht', 'iPad-hoch', 'iPad-quer', 'Mobil'):
        filename=shot+'.jpg'
        expected=reports['bedienung']['screenshots'][filename]
        assert hashlib.sha256((QA/filename).read_bytes()).hexdigest() == expected
        z.write(QA/filename, 'Bildschirmfotos/'+filename)
with ZipFile(package) as z:
    assert z.testzip() is None and z.read('Fallakte.html') == local.read_bytes()
print(package)
