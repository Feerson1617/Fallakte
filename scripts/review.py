"""Package evidence for the same standalone HTML that passed the browser suite."""
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
QA = ROOT / 'build/qa'
local = OUT / 'Fallakte.html'
digest = hashlib.sha256(local.read_bytes()).hexdigest()
names = ('dialogwege', 'scorm', 'bedienung', 'layout', 'inhaltsvergleich', 'lernhilfen')
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
    assert {r['level'] for r in mixed if r['unterbrochen']==['L0','L1','L3','L4','L6']} == {'Foerder','ESA','MSA','AHR'}
assert all(m['disclosure']['later_facts_visible'] is False for m in matrices)
assert all(m['article_return']['glossary_state_preserved'] and m['article_return']['jump_to_article'] for m in matrices)
assert reports['scorm']['schema_valid']
assert all(run['laura_age']==19 and run['age_levels']==4 for run in reports['scorm']['runs'])
assert all(run['kombination_ab_l1'] for run in reports['scorm']['runs'])
assert {r['engine'] for r in reports['scorm']['runs']} == {'chromium', 'webkit'}
content = reports['inhaltsvergleich']
assert content['additional_cases_equal'] and content['rendered_paths'] == 84
assert content['shared_help_equal'] and content['laura_abschnitte']==5
levels=('Foerder','ESA','MSA','AHR')
assert set(content['fachkern_geprueft'])==set(levels)
counts=content['bedienhandlungen']
assert len(counts)==16 and {r['engine'] for r in counts}=={'chromium','webkit'}
for row in counts:
    correction=int(row['korrektur_in_l0'])
    old=11 if row['niveau'] in ('Foerder','ESA') else 15
    assert row['vorher']['total']==old+3*correction and row['jetzt']['total']==9+3*correction
    assert row['vorher']['decisions']==6+correction and row['jetzt']['decisions']==5+correction
    for version,n in [('vorher',7),('jetzt',5)]:
        words=row[version]['words']
        assert len(words)==n and all(w['fall'] and w['auftrag'] for w in words)
        assert all(bool(w['kartenhinweis'])==(version=='jetzt') for w in words)
    match=next(r for r in counts if r['engine']!=row['engine'] and r['niveau']==row['niveau']
               and r['korrektur_in_l0']==row['korrektur_in_l0'])
    assert all(row[k]==match[k] for k in ('vorher','jetzt'))
assert {view['engine'] for view in views} == {'chromium','webkit'}
assert all(not row['errors'] and not row['external_requests'] for row in views)
help_runs=reports['lernhilfen']['runs']
assert {run['engine'] for run in help_runs} == {'chromium','webkit'}
assert all({r['niveau'] for r in run['wege']} == {'Foerder','ESA','MSA','AHR'} for run in help_runs)
for engine in help_runs:
    assert len(engine['wege'])==16
    assert {r['niveau'] for r in engine['fuenf_abschnitte']}==set(levels)
    for r in engine['fuenf_abschnitte']:
        assert [s['abschnitt'] for s in r['abschnitte'] if s['entwurf_ohne_senden']]==[1,2,3,4,5]
    assert {r['niveau'] for r in engine['weiterfuehrung']}=={'Foerder','ESA'}
    assert all(r['kombination_ab_l1'] for r in engine['wege'])
    assert all(r['hilfe_ohne_scroll'] and r['entwurf_ohne_senden'] and r['stufen']==5 for r in engine['wege'])
layout = reports['layout']
assert {run['engine'] for run in layout['runs']} == {'chromium','webkit'}
for run in layout['runs']:
    assert {row['width'] for row in run['phone_labels']} == {360,390,420}
    assert len(run['frames']) == 6
    assert all(row['papierhinweis_beim_scrollen'] for row in run['frames'])
    assert all(row['enlargedText']['doubled']>=2*row['enlargedText']['normal']
               for row in run['frames'] if row['size'] in ([820,650],[820,1180],[1180,820]))
    assert all(len(row['states']) == 4 for row in run['frames'])
assert len(layout['screenshots']) == 4
with ZipFile(OUT/'Fallakte-SCORM12.zip') as scorm:
    resources = list((ROOT/'scorm').iterdir())
    assert sorted(scorm.namelist()) == sorted(['index.html', *(p.name for p in resources)])
    assert scorm.testzip() is None
    for path in resources:
        assert scorm.read(path.name) == path.read_bytes()
    assert hashlib.sha256(scorm.read('index.html')).hexdigest() == digest

report = OUT/'Fallakte-Pruefbericht.md'
versions = ', '.join(f"{m['engine']} {m['version']}" for m in matrices)
release = (f"Geprüft mit {versions} gegen den Ausgangsstand `{content['reference_commit'][:7]}`. "
           f"SHA-256 der Offline-HTML und der SCORM-Startdatei: `{digest}`.")
measurement = [
    '| Niveau | Klicks direkt | Klicks mit Korrektur | Fallwörter | Auftragswörter | Wörter einschließlich Kartenhinweis |',
    '| --- | ---: | ---: | ---: | ---: | ---: |',
]
for level in levels:
    direct, corrected = sorted((r for r in counts if r['engine']=='chromium' and r['niveau']==level),
                               key=lambda r:r['korrektur_in_l0'])
    columns=[]
    for path in (direct,corrected):
        columns.append([path[v]['total'] for v in ('vorher','jetzt')])
    for fields in [('fall',),('auftrag',),('fall','auftrag','kartenhinweis')]:
        columns.append([sum(w[f] for w in direct[v]['words'] for f in fields) for v in ('vorher','jetzt')])
    label='Förder' if level=='Foerder' else level
    measurement.append('| '+label+' | '+' | '.join(f'{a} → {b}' for a,b in columns)+' |')
body=(ROOT/'docs/Abnahme.md').read_text()
body=body.replace('## Ausstehender Praxistest', '\n'.join(measurement)+'\n\n## Ausstehender Praxistest')
report.write_text(body.rstrip()+'\n\n'+release+'\n', encoding='utf-8')

evidence = {f'Protokolle/{name}.json': QA/(name+'.json') for name in names}
def add_photos(folder, photos):
    for filename, expected in photos.items():
        path = QA/folder/filename
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, filename
        evidence[str(Path('Bildschirmfotos')/folder/filename)] = path

add_photos('', reports['bedienung']['screenshots'])
add_photos('', reports['lernhilfen']['screenshots'])
for run in layout['runs']:
    add_photos('methoden', {row['screenshot']:row['sha256'] for row in run['phone_labels']})
add_photos('rahmen', layout['screenshots'])

package = OUT/'Fallakte-Sichtpruefung.zip'
with ZipFile(package, 'w', ZIP_DEFLATED) as z:
    for name, path in evidence.items():
        z.write(path, name)
with ZipFile(package) as z:
    assert z.testzip() is None and set(z.namelist()) == set(evidence)
    for name, path in evidence.items():
        assert z.read(name) == path.read_bytes(), name
print(package)
