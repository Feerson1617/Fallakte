"""Assemble verified evidence for both releases and the embedded first lesson."""
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
QA = ROOT / 'build/tagesauswahl'
FROZEN = ROOT / 'build/02-12'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


report = json.loads((QA / 'Tagesauswahl.json').read_text())
expected = {(engine, version, kind, size) for engine in ('chromium','webkit') for version in 'AB'
            for kind in ('HTML','SCORM') for size in ((820,1180),(1180,820))}
runs = report['durchlaeufe']
assert len(runs) == len(expected)
assert {(r['browser'], r['version'], r['format'], tuple(r['viewport'])) for r in runs} == expected
assert all(not r['fehler'] and not r['externe_zugriffe'] for r in runs)
assert digest(FROZEN/'Fallakte.html') == report['modul_02_sha256']
for version, files in report['pakete'].items():
    assert set(files) == {'Fallakte.html','Fallakte-SCORM12.zip'}
    for name, checked in files.items():
        assert digest(DIST / f'Version-{version}' / name) == checked
for name, checked in report['bilder'].items():
    assert digest(QA / name) == checked

browsers = sorted({r['browser']+' '+r['browserversion'] for r in runs})
body = f"""# Fallakte. Abnahme der gemeinsamen Tagesauswahl

## Auslieferung

| Stand | 02.12.2026 | 08.12.2026 |
| --- | --- | --- |
| Version A | Freigegebene Fallübersicht und Beratung | Gesperrte Karte mit Schloss. Das zweite Moduldokument fehlt im Paket. |
| Version B | Freigegebene Fallübersicht und Beratung | Eigener, erreichbarer Einstieg mit neutralem Vorbereitungshinweis. Die fachliche Freigabe steht aus. |

Jede Version enthält eine lokale Einzeldatei und ein SCORM-1.2-ZIP mit derselben Startdatei. Beide Startseiten zeigen das ursprüngliche Laura-Porträt und das daraus abgeleitete Gruppenbild. Die Bilder sind in beiden Versionen bytegleich. Die Gruppe zeigt Laura im Zentrum mit vier Personen in Kopf- und Schulteransicht.

## Bestandsschutz und Sitzungswechsel

Die Referenz ist `{report['referenz']}`. Der Test baut diese Revision separat und vergleicht das Ergebnis Byte für Byte mit dem eingebetteten Dokument des 02.12. in beiden HTML-Dateien und SCORM-Paketen. HTML, Dialog- und Hilfedaten, Skripte, Bilder und Schriftdateien des ersten Tages werden außerdem einzeln mit dem Git-Archiv verglichen. Der SHA-256-Wert des geprüften Moduls ist `{report['modul_02_sha256']}`.

Jedes Modul läuft in einem eigenen Dokument. Beim Tageswechsel behält das Programm dessen geöffnete Instanz im Arbeitsspeicher. Der Rückweg zum Menü ist am 02.12. in der Fallübersicht erreichbar. Während der Beratung nutzt das Modul die volle Höhe. Nach dem Neuladen führt der bestehende Wiedereinstieg wieder zum markierten Abschnitt.

## Ausgeführte Prüfungen

{len(runs)} Kombinationen aus Version, Browser, Auslieferungsformat und iPad-Ansicht wurden durchgespielt. Eingesetzt wurden {' und '.join(browsers)}, mit 820 × 1180 und 1180 × 820 CSS-Pixeln.

- Sichtbarer Wortlaut, Zahl der Schaltflächen, eingebettete Bilder und Sperre am 08.12. in A. In B wurde der zweite Tag auch zuerst geöffnet.
- Fünf geöffnete Hilfestufen, Rückmeldung auf einen Rat, Infokarten und Arbeitsstand nach Rückkehr über die Tagesauswahl. Der Wiedereinstieg nach Neuladen wurde bei Laura 3 auf ESA geprüft.
- Vollständige Laura-Wege mit Korrektur auf Förder, MSA und AHR innerhalb der gemeinsamen Anwendung. Weitere Prüfungen aller drei Fälle auf allen vier Niveaus liefen am identischen Dokument des 02.12. Die zugehörigen sieben Protokolle und Bilder liegen im Ordner `02-12`.
- Offlineaufruf bei blockiertem Netzzugriff. Importstruktur und Schema beider SCOs wurden geprüft. Im Test-LMS wurden ausschließlich Sitzungsbeginn und Sitzungsende beobachtet.

| Datei | SHA-256 |
| --- | --- |
"""
for version, files in report['pakete'].items():
    for name, checked in sorted(files.items()):
        body += f'| Version {version} · {name} | `{checked}` |\n'
body += """
## Offener Praxistest

Beide Versionen auf einem Schul-iPad in Safari öffnen und getrennt als SCORM-Aktivitäten in den schulischen itslearning-Testkurs importieren. In A die Sperre prüfen. In B beide Tageskarten öffnen. Bei Laura einen Rat senden und die Hilfe öffnen. Über „Übersicht“ zur Tagesauswahl gehen, wieder zu Laura wechseln und den Verlauf prüfen. Nach einem Neuladen über „Nach Neustart weitermachen“ den markierten Abschnitt öffnen.

Die Unterrichtsinhalte und die pädagogische Abnahme für den 08.12. stehen aus. Die Bedienung mit realen Förder- und ESA-Lernenden sowie die Bearbeitungszeit unter Unterrichtsbedingungen wurden nicht erprobt.
"""
bericht = DIST / 'Fallakte-Pruefbericht.md'
bericht.write_text(body)
with ZipFile(DIST / 'Fallakte-Sichtpruefung.zip','w',ZIP_DEFLATED) as package:
    package.write(bericht,bericht.name)
    package.write(QA / 'Tagesauswahl.json','Tagesauswahl/Protokolle/Tagesauswahl.json')
    for name in sorted(report['bilder']):
        package.write(QA / name,'Tagesauswahl/Bildschirmfotos/'+name)
    with ZipFile(FROZEN / 'Fallakte-Sichtpruefung.zip') as legacy:
        assert legacy.testzip() is None
        for name in legacy.namelist():
            content = legacy.read(name)
            if name.endswith('.json'):
                assert json.loads(content)['html_sha256'] == report['modul_02_sha256']
            package.writestr('02-12/'+name, content)
    package.write(FROZEN/'Fallakte-Pruefbericht.md','02-12/Modulabnahme.md')
with ZipFile(DIST / 'Fallakte-Sichtpruefung.zip') as package:
    assert package.testzip() is None
    print(bericht, len(package.namelist()), 'Dateien im Sichtprüfungspaket')
