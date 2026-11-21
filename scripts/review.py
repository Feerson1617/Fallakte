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
names = ('dialogwege', 'scorm', 'bedienung', 'laufzettel', 'layout', 'inhaltsvergleich', 'lernhilfen')
reports = {}
for name in names:
    reports[name] = json.loads((QA / (name + '.json')).read_text())
    if reports[name]['html_sha256'] != digest:
        raise SystemExit('Prüflauf gehört zu einer anderen HTML-Version: ' + name)

matrices = reports['dialogwege']['runs']
views = reports['bedienung']['runs']
assert len(views) == 8
assert {r['engine'] for r in matrices} == {'chromium','webkit'}
assert all(len(r['paths']) == 84 and len(r['scenarios']) == 6 and not r['errors'] for r in matrices)
for matrix in matrices:
    mixed=matrix['transitions']
    assert len(mixed)==12
    assert all(len({tuple(r['choices']) for r in mixed if r['level']==tier})==3
               for tier in ('Foerder','ESA','MSA','AHR'))
assert all(m['disclosure']['later_facts_visible'] is False for m in matrices)
assert all(m['article_return']['glossary_state_preserved'] and m['article_return']['jump_to_article'] for m in matrices)
assert reports['scorm']['schema_valid']
assert all(run['laura_age']==19 and run['age_levels']==4 for run in reports['scorm']['runs'])
assert all(run['kombination_ab_l1'] for run in reports['scorm']['runs'])
assert {r['engine'] for r in reports['scorm']['runs']} == {'chromium', 'webkit'}
content = reports['inhaltsvergleich']
assert content['built_data_equal'] and content['rendered_paths'] == 84
assert set(content['pdf_page_text_sha256']) == {'Foerder', 'ESA', 'MSA', 'AHR'}
assert {view['engine'] for view in views} == {'chromium','webkit'}
assert all(not row['errors'] and not row['external_requests'] for row in views)
help_runs=reports['lernhilfen']['runs']
assert {run['engine'] for run in help_runs} == {'chromium','webkit'}
assert all({r['niveau'] for r in run['wege']} == {'Foerder','ESA','MSA','AHR'} for run in help_runs)
for engine in help_runs:
    assert len(engine['wege'])==16
    assert all(r['kombination_ab_l1'] for r in engine['wege'])
    assert all(r['hilfe_ohne_scroll'] and r['entwurf_ohne_senden'] and r['stufen']==5 for r in engine['wege'])
layout = reports['layout']
assert {run['engine'] for run in layout['runs']} == {'chromium','webkit'}
for run in layout['runs']:
    assert {row['width'] for row in run['phone_labels']} == {360,390,420}
    assert len(run['frames']) == 12
    assert all(len(row['states']) == 4 for row in run['frames'])
assert len(layout['screenshots']) == 8
for sheet in reports['laufzettel']['pdfs']:
    assert hashlib.sha256((OUT/'Laufzettel'/sheet['datei']).read_bytes()).hexdigest() == sheet['sha256']
teacher=reports['laufzettel']['lehrkraft']
assert hashlib.sha256((OUT/teacher['datei']).read_bytes()).hexdigest()==teacher['sha256']
for wheel in reports['laufzettel']['empfehlungsraeder']:
    assert hashlib.sha256((OUT/wheel['datei']).read_bytes()).hexdigest()==wheel['sha256']
with ZipFile(OUT/'Fallakte-SCORM12.zip') as scorm:
    resources = list((ROOT/'scorm').iterdir())
    assert sorted(scorm.namelist()) == sorted(['index.html', *(p.name for p in resources)])
    assert scorm.testzip() is None and teacher['datei'] not in scorm.namelist()
    for path in resources:
        assert scorm.read(path.name) == path.read_bytes()
    assert hashlib.sha256(scorm.read('index.html')).hexdigest() == digest

report = OUT/'Fallakte-Pruefbericht.md'
chapters = [(ROOT/'docs'/name).read_text().rstrip() for name in ('Abnahme.md','Fachpruefung.md','Unterricht.md')]
versions = ', '.join(f"{m['engine']} {m['version']}" for m in matrices)
release = (f"Geprüft mit {versions} gegen die Inhaltsreferenz `{content['reference_commit']}`. "
           f"Die HTML-Datei hat den SHA-256-Wert `{digest}`.")
report.write_text('\n\n'.join(chapters)+'\n\n'+release+'\n', encoding='utf-8')
package = OUT / 'Fallakte-Sichtpruefung.zip'
with ZipFile(package, 'w', ZIP_DEFLATED) as z:
    z.write(local, 'Fallakte.html')
    z.write(report, 'Pruefbericht.md')
    z.write(ROOT/'docs/Fachpruefung.md', 'Fachquellen.md')
    z.write(ROOT/'docs/Unterricht.md', 'Unterrichtsablauf.md')
    for name in names:
        z.write(QA/(name+'.json'), 'Protokolle/'+name+'.json')
    for shot in ('Falluebersicht', 'iPad-hoch', 'iPad-quer', 'Mobil', 'Laura-Entscheidung', 'Tom-Eigener-Beitrag', 'Frueher-Stopp', 'Sicherung-nach-Nachricht-1'):
        filename=shot+'.jpg'
        expected=reports['bedienung']['screenshots'][filename]
        assert hashlib.sha256((QA/filename).read_bytes()).hexdigest() == expected
        z.write(QA/filename, 'Bildschirmfotos/'+filename)
    help_photos=reports['lernhilfen']['screenshots']
    assert set(help_photos)=={'Hilfe-vor-Auswahl.jpg','Hilfe-nach-Rueckmeldung.jpg','Auffanghilfe.jpg'}
    for name, expected in help_photos.items():
        shot = QA/name
        assert hashlib.sha256(shot.read_bytes()).hexdigest()==expected
        z.write(shot,'Bildschirmfotos/'+name)
    for run in layout['runs']:
        for row in run['phone_labels']:
            path=QA/'methoden'/row['screenshot']
            assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
            z.write(path, 'Bildschirmfotos/Methodenfelder/'+path.name)
    for name, expected in layout['screenshots'].items():
        path=QA/'vergleich'/name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
        z.write(path, 'Bildschirmfotos/Vergleich/'+name)
with ZipFile(package) as z:
    assert z.testzip() is None and z.read('Fallakte.html') == local.read_bytes()
    assert z.read('Pruefbericht.md') == report.read_bytes()
    for name in names:
        assert z.read(f'Protokolle/{name}.json') == (QA/f'{name}.json').read_bytes()
print(package)
