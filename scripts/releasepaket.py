"""Collect the tested deliveries from this run; verify a downloaded release with --verify DIR."""
import argparse
import base64
import hashlib
import json
import os
import re
from pathlib import Path
from shutil import copy2
from zipfile import ZipFile, ZIP_DEFLATED
import sys

from modul_0212 import ROOT, commit
sys.path.insert(0, str(ROOT / 'tests'))
from kandidatenmaterial import verify

BASE = '8b8939c56c34c9c0771c2728a3c9821e6ed7f557'
BRANCH = 'release/fallakte-0212-kandidat'
SOURCE = ROOT / 'dist/Vorabkandidat'
DEST = ROOT / 'dist/Release'
WORK = 'Work-Material.zip'
SIGHT = 'Fallakte-Sichtpruefung.zip'
META = 'Buildnachweis.json'
REPORT = 'Abnahmebericht.md'
GUIDE = 'Work-Uebergabe.md'
APPS = ['Fallakte.html', 'Fallakte-SCORM12.zip', 'Uebungsakte.html', 'Uebungsakte-SCORM12.zip']
DELIVERY = APPS + [WORK, SIGHT, REPORT, GUIDE]
# The two actual downloads from successful run 45110959929, including all embedded resources.
FROZEN = {'Fallakte.html':'e93db3b3167329f31e717bfb7d4886b7de38d58bcbfc9e6284af6261ce4d4e1b',
          'Uebungsakte.html':'97cbff981200ca373fcb51cc77f2c4bf66b2a612e6dd52551641c5861140aa00'}
SLOT = re.compile(rb'(<script id="(?:modul-0[28]|reserve-(?:Tom|Celina))" type="application/octet-stream">)([A-Za-z0-9+/=]+)(</script>)')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def baseline(document, head):
    """Reinsert only the build stamp, also inside the nested embedded HTML files."""
    def nested(match):
        child = base64.b64decode(match[2], validate=True)
        return match[1] + base64.b64encode(baseline(child, head)) + match[3]
    return SLOT.sub(nested, document).replace(head.encode(), BASE.encode())


def banks(folder):
    with ZipFile(folder / WORK) as archive:
        result = {}
        for name in archive.namelist():
            if name.endswith('.json'):
                payload = archive.read(name)
                bank = json.loads(payload)
                result[name] = dict(version=bank.get('version', 'Referenz 5d27cc3'), sha256=digest(payload))
        assert len(result) == 5
        return result


def verify_release(folder):
    verify(folder)
    meta = json.loads((folder / META).read_text())
    head = commit()
    assert meta['commit'] == head and meta['branch'] == BRANCH
    assert set(p.name for p in folder.iterdir()) == set(DELIVERY + [META])
    assert set(meta['dateien']) == set(DELIVERY)
    for name in DELIVERY:
        data = (folder / name).read_bytes()
        assert meta['dateien'][name] == dict(bytes=len(data), sha256=digest(data)), name
    for name, expected in FROZEN.items():
        assert digest(baseline((folder / name).read_bytes(), head)) == expected, name
    assert meta['inhaltsbanken'] == banks(folder)
    with ZipFile(folder / WORK) as z:
        assert z.read('Start hier.md') == (folder / GUIDE).read_bytes()
    with ZipFile(folder / SIGHT) as z:
        record = json.loads(z.read('Releasepruefung/Abnahme.json'))
        assert record['html_sha256'] == meta['html_sha256']
        assert len(record['wege']) == 8
        assert all(json.loads(z.read('Laura/' + n + '.json'))['commit'] == head
                   for n in ('bestand', 'bedienung', 'material', 'browser', 'karten'))
    print('Release verifiziert', head, len(DELIVERY) + 1, 'Dateien')


def package():
    verify(SOURCE)
    meta = json.loads((SOURCE / META).read_text())
    head = commit()
    assert head == meta['commit']
    DEST.mkdir(parents=True, exist_ok=True)
    for name in APPS:
        copy2(SOURCE / name, DEST / name)
    boundary = 'Offen sind der Import und Start auf einem Schul-iPad in itslearning, die echte Bildschirmtastatur sowie Bearbeitungszeit und selbstständige Nutzung durch Förder- und ESA-Lernende.'
    status = 'Technisch bereit für die Materialproduktion'
    identity = f"Zweig `{BRANCH}` · Commit `{head}` · Build (UTC) {meta['build_utc']}"
    guide = (ROOT / 'docs/work-uebergabe.md').read_text().replace('gemeinsamen Vorabkandidaten', 'Release-Kandidaten')
    guide += ('\n## Verbindlicher Stand für Work\n\n' + identity + '\n\n' +
              'Für die Materialproduktion gelten ausschließlich die fünf Banken dieser Ausgabe. Abschnittstitel, IDs, Aufträge, Kartenstellen und Codes wörtlich übernehmen. '
              'Lösungen und interne Prüfdaten bleiben im Lehrkraftmaterial. Bei einem Widerspruch Datei, Abschnitt, Niveau und betroffene Textstellen dokumentieren. '
              'Eine freigegebene Änderung erhält einen neuen Commit, Build und synchronen Work-Export. Dateigrößen und SHA-256 stehen in Buildnachweis.json.\n\n' + boundary + '\n')
    (DEST / GUIDE).write_text(guide)
    with ZipFile(SOURCE / WORK) as old, ZipFile(DEST / WORK, 'w', ZIP_DEFLATED) as new:
        for n in old.namelist():
            new.writestr(n, guide if n == 'Start hier.md' else old.read(n))
    with ZipFile(SOURCE / SIGHT) as old, ZipFile(DEST / SIGHT, 'w', ZIP_DEFLATED) as new:
        for n in old.namelist():
            if n != META:
                new.writestr(n, old.read(n))
        record = json.loads(old.read('Releasepruefung/Abnahme.json'))
        with ZipFile(ROOT / 'dist/Runde-1' / SIGHT) as laura:
            for n in ('bestand', 'bedienung', 'material', 'browser', 'karten'):
                new.writestr('Laura/' + n + '.json', laura.read('Protokolle/' + n + '.json'))
    engines = sorted({row['browser'] + ' ' + row['version'] for row in record['wege']})
    report = [
        '# Technische Endabnahme · Fallakte Klasse 8', identity, status,
        '## Gebaute Auslieferung',
        'Gemeinsame HTML und Übungsakte offline geöffnet. Für beide SCORM-Pakete wurden Manifest, Schemata, Referenzen und der tatsächliche Einstieg geprüft. '
        'Beide SCOs starteten ohne API und in der LMS-Simulation. Alle fünf Materialbanken wurden mit ihren eingebetteten Gegenstücken verglichen.',
        '## Geprüfte Unterrichtswege',
        ' und '.join(engines) + '. Touch-Ansichten mit 820 × 1180, 1180 × 820 und 390 × 844 Pixeln. Für den Fachcheck auf schmalen Geräten wurden 150 % Schrift und eine verkürzte Arbeitshöhe von 460 Pixeln geprüft.',
        'Laura 1–5 auf allen vier Niveaus mit sieben Ausgangsstrategien. Eigene Gegenproben zum latexfreien Kondom, STI-Rest­risiko, Einnahme, Regelschmerzen und Zustimmung. '
        'Falsche und richtige Gründe, leere und ungültige Codes, Kleinbuchstaben mit Leerzeichen, Methodenwechsel, Doppelversand, fünf Hilfen, Kartenrückweg, Sicherung und Direkteinstieg wurden bedient.',
        'Die vier Übungssituationen trainieren dieselbe Abfolge aus Begründung, bewusstem Senden und Reaktion wie Laura. Bei Laura kommt die fallbezogene Ratsentscheidung hinzu. '
        'Förder und ESA begründen digital, MSA und AHR üben in U3 den Papiercode. Tom 1–3 und Celina 1–5 wurden auf allen vier Niveaus geprüft, einschließlich Methodenwechsel, Quellen, Feedback und der Freigabereihenfolge.',
        'Der Tageswechsel erhielt laufende Entwürfe. Das 08.12.-Modul entspricht bytegenau der geprüften Referenz. Einzelwege, gemischte Niveaus sowie Wiedereinstieg wurden auch in der gemeinsamen Auslieferung bedient.',
        '## Befunde',
        'Die frühere Auslieferung hatte acht Dateien und keine eigenständige versionierte Work-Übergabe. Nun enthält das Release neun Dateien und dokumentiert für acht Nutzdateien Größe und SHA-256. '
        'Die Prüfsumme des Buildnachweises kann separat aus der Datei berechnet werden. Die Endabnahme hat keinen offenen P0- oder P1-Befund an den geprüften Lernwegen ergeben.',
        '## Ausstehender Praxistest', boundary,
        'Im Testkurs beide SCOs importieren. Jeweils starten, bei eingeblendeter Tastatur einen fehlerhaften und einen gültigen Code eingeben, zur Karte und zurück wechseln. '
        'Dann das iPad neu laden und den zuletzt markierten Abschnitt aufrufen. Die Bearbeitungszeit der Übungsakte und die Qualität eigener Begründungen im Unterricht beobachten.'
    ]
    (DEST / REPORT).write_text('\n\n'.join(report) + '\n')
    files = {}
    for name in DELIVERY:
        data = (DEST / name).read_bytes()
        files[name] = dict(bytes=len(data), sha256=digest(data))
    meta.update(branch=BRANCH, status=status, ausstehend=boundary, ausgangscommit=BASE,
                actions_lauf=os.getenv('GITHUB_RUN_ID'), inhaltsbanken=banks(DEST), dateien=files,
                auslieferungs_sha256={n: f['sha256'] for n, f in files.items()})
    (DEST / META).write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    verify_release(DEST)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', type=Path)
    args = parser.parse_args()
    if args.verify:
        verify_release(args.verify)
    else:
        package()
