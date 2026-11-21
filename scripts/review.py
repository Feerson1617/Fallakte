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
names = ('dialogwege', 'scorm', 'bedienung', 'laufzettel', 'layout')
reports = {}
for name in names:
    reports[name] = json.loads((QA / (name + '.json')).read_text())
    if reports[name]['html_sha256'] != digest:
        raise SystemExit('Prüflauf gehört zu einer anderen HTML-Version: ' + name)

matrices = reports['dialogwege']['runs']
views = reports['bedienung']['runs']
assert len(views) == 8
assert {r['engine'] for r in matrices} == {'chromium','webkit'}
assert all(len(r['paths']) == 84 and len(r['scenarios']) == 5 and not r['errors'] for r in matrices)
assert reports['scorm']['schema_valid']
assert {view['engine'] for view in views} == {'chromium','webkit'}
assert all(not row['errors'] and not row['external_requests'] for row in views)
layout = reports['layout']
assert {run['engine'] for run in layout['runs']} == {'chromium','webkit'}
for run in layout['runs']:
    assert len(run['frames']) == 12
    assert all(len(row['states']) == 4 for row in run['frames'])
assert len(layout['screenshots']) == 8
for sheet in reports['laufzettel']['pdfs']:
    assert hashlib.sha256((OUT/'Laufzettel'/sheet['datei']).read_bytes()).hexdigest() == sheet['sha256']
with ZipFile(OUT/'Fallakte-SCORM12.zip') as scorm:
    assert hashlib.sha256(scorm.read('index.html')).hexdigest() == digest

package = OUT / 'Fallakte-Sichtpruefung.zip'
with ZipFile(package, 'w', ZIP_DEFLATED) as z:
    z.write(local, 'Fallakte.html')
    z.write(ROOT/'docs/Abnahme.md', 'Pruefbericht.md')
    z.write(ROOT/'docs/Fachpruefung.md', 'Fachquellen.md')
    for name in names:
        z.write(QA/(name+'.json'), 'Protokolle/'+name+'.json')
    for shot in ('Falluebersicht', 'iPad-hoch', 'iPad-quer', 'Mobil', 'Laura-Entscheidung', 'Tom-Eigener-Beitrag'):
        filename=shot+'.jpg'
        expected=reports['bedienung']['screenshots'][filename]
        assert hashlib.sha256((QA/filename).read_bytes()).hexdigest() == expected
        z.write(QA/filename, 'Bildschirmfotos/'+filename)
    for name, expected in layout['screenshots'].items():
        path=QA/'vergleich'/name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
        z.write(path, 'Bildschirmfotos/Vergleich/'+name)
with ZipFile(package) as z:
    assert z.testzip() is None and z.read('Fallakte.html') == local.read_bytes()
print(package)
