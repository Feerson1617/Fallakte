"""Package only evidence that belongs to the delivered standalone HTML."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist/Runde-1'
QA = ROOT / 'build/runde1/qa'
CAPTIONS = {
    'Alltag-Kombinationspille-ESA': 'Laura 3. Die Einnahmeroutine wird für die gewählte Strategie geprüft.',
    'Schmerzen-Kupferspirale-MSA': 'Laura 4. Kupferspirale, Beschwerden und Lauras Zustimmung.',
    'Schlussrat-AHR': 'Laura 5. Gesendeter Schlussrat nach dem erneuten Fachcheck.',
    'Falluebersicht': 'Einstiegsseite mit bewusster Niveauwahl, Laura als Pflichtfall und beiden Vertiefungen.',
    'Start-ESA': 'Laura 1 bei ESA vor der ersten Auswahl.',
    'Lehreransicht': 'Die ausdrücklich aufgerufene Übersicht für die gemeinsame Sicherung.',
    'B-Korrektur-Foerder': 'Förder erhält eine konkrete Hilfe zur bewussten Ergänzung des Rats.',
    'B-Korrektur-ESA': 'Rückmeldung bei ESA zum offenen Schutzziel.',
    'B-Korrektur-MSA': 'Bei MSA führt der Korrekturweg zurück zur eigenen Auswahl.',
    'Papierweg-MSA': 'Regulärer Weg zur Aufgabe auf dem Laufzettel und zurück zur Codeeingabe.',
    'Papierersatz-MSA': 'Digital geöffnete Ersatzaufgabe mit Denkauftrag und drei Fachankern.',
    'Foerder-L01-Gesendet': 'Schülerrat mit fachlichem Grund und Lauras tatsächliche Antwort.',
    'Foerder-Cu-Hilfe-5': 'Fünfte freiwillige Hilfe zum Entwurf mit der Kupferspirale.',
    'Foerder-Cu-Markierte-Kartenstelle': 'Aus der Kupferberatung aufgerufener Fachkartenabschnitt.',
    'Gepruefter-Kombinationsrat': 'Erneut geprüfter Kombinationsrat nach Rückkehr aus der Übersicht.',
    'Zweites-Schutzziel-fehlt': 'Feedback bei fachlich möglicher Methode und offenem STI-Anliegen.',
    'Verkleinerter-Tastaturbereich': 'Buchstabenprüfung und Sendefunktion bei verminderter Fensterhöhe.',
}


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def load_table(usage):
    fields = ('entscheidungen','tipps','codeeingaben','papierphasen','medienwechsel','pflichtwoerter_im_blick_max')
    rows = ['| Niveau | Ratsentscheidungen | Erforderliche Berührungen | Codeeingaben | Papierphasen | Medienwechsel | Pflichtwörter zugleich, maximal |',
            '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for key in ('Foerder','ESA','MSA','AHR'):
        measures = usage['niveaus'][key]
        label = 'Förder' if key=='Foerder' else key
        rows.append('| '+' | '.join([label,*(str(measures[f]) for f in fields)])+' |')
    return '\n'.join(rows)


def main():
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    app_hash = digest(OUT / 'Fallakte.html')
    files = {k: QA / (k+'.json') for k in ('browser', 'material', 'karten', 'bedienung')}
    files['bestand'] = QA.parent / 'bestand.json'
    records = {k: json.loads(p.read_text()) for k,p in files.items()}
    for record in records.values():
        assert record['commit'] == commit and record['html_sha256'] == app_hash
    browser, material, bestand, cards = (records[k] for k in ('browser', 'material', 'bestand', 'karten'))
    assert browser['material_sha256'] == material['vertrag_sha256'] == digest(OUT / 'Materialvertrag.json')
    assert browser['bankversion'] == material['bankversion']
    assert commit in (OUT / '0212-umsetzungsstand.md').read_text()
    expected = {'chromium','webkit'}
    assert {b['engine'] for b in browser['browsers']} == expected
    assert {b['engine'] for b in cards['browsers']} == expected
    usage = records['bedienung']
    screenshots = browser['screenshots'].copy()
    assert set(screenshots) == {f'{engine}-{key}.jpg' for engine in expected for key in CAPTIONS}
    assert not set(screenshots).intersection(usage['bilder'])
    screenshots.update(usage['bilder'])
    for name, checksum in screenshots.items():
        path = QA / name
        assert digest(path) == checksum and path.read_bytes().startswith(b'\xff\xd8\xff')
    table = ['| Browser | Version | Beratungswege | Abgeschlossene Kapitel |', '| --- | --- | ---: | ---: |']
    for b in browser['browsers']:
        paths = b['paths']
        assert len(paths)==28 and all([c['stage'] for c in p['chapters']]==['L01','L02','L03','L04','L05'] for p in paths)
        table.append(f"| {b['engine'].capitalize()} | {b['version']} | {len(paths)} | {sum(len(p['chapters']) for p in paths)} |")
    report = [
        '# Technischer Prüfbericht · Laura-Regression für den 02.12.2026',
        f"Branch `entwicklung/0212-neukonzeption` · Commit `{commit}` · Inhaltsbank `{material['bankversion']}`.",
        f"Die geprüfte **Fallakte.html** ist {material['bytes']:_} Bytes groß. SHA-256 `{app_hash}`.".replace('_', ' '),
        '## Browserdurchläufe', '\n'.join(table),
        'Alle vier Niveaus durchliefen fünf Abschnitte mit sieben Ausgangsstrategien. Die Protokolle halten die tatsächlich gewählte und versendete Strategie, die Fachprüfung und Lauras Reaktion fest. '
        'Eine biologisch richtige Begründung kann ab Laura 2 ein noch offenes Schutzziel sichtbar machen. Auf Förder und ESA konnte das Team bewusst ergänzen. Auf MSA und AHR wählte es selbst einen neuen vollständigen Rat.',
        'Geprüft wurden richtige und falsche Begründungen, Fehleingaben und erneute Fachchecks nach neuen Anliegen oder einem Wechsel der Methode. '
        'Die Tests umfassten auch bedingte Empfehlungen, Rückfragen, fokussierte Kartenstellen und die ganze Karte, Rückkehr in den Entwurf, fünf Direkteinstiege, fortgesetzte Sitzungen und die vorgezogene Sicherung.',
        'Die Offline-Datei lief ohne externe Netzabrufe oder Skriptausnahmen. Im Browserprotokoll sind die beobachteten Schreibzugriffe auf Webspeicher ausgewiesen.',
        '## Bedienung und Bearbeitungslast',
        load_table(usage),
        'Die Messung erfasst einen erfolgreichen Beispielweg. Wiederholungen nach einem Fehler, das freiwillige Lesen von Hilfen und individuelle Schreibzeiten kommen je nach Lernweg hinzu. '
        'Der persönliche Schlussrat wird einmal auf dem Laufzettel festgehalten. Ein früher Wechsel in die gemeinsame Sicherung führt zum selben Feld.',
        '## Material und Darstellung',
        f"Die in der HTML eingebettete Bank und der Work-Export wurden verglichen. Geprüft wurden {material['aufgaben']} Niveauaufgaben, {material['strategiekontexte']} Strategiekontexte und {material['begruendungsoptionen']} geschlossene Antwortmöglichkeiten, für die fünf spielbaren Abschnitte.",
        'Vier Infokarten mit je fünf Abschnitten wurden in beiden Engines bei 820 × 1180 Pixeln (100 % Schrift), 1180 × 820 (150 %) und 390 × 450 (200 %) geöffnet. '
        'Beide Enden langer Texte, der Rückweg, Fokus und Scrollposition nach dem Kartenbesuch sowie die Korrektur eines falschen Codes wurden geprüft. '
        'Für die Codeeingabe bei Touchbedienung wurde die verfügbare Höhe auf 470 Pixel verkleinert.',
        'Die fünfte Hilfe im iPad-Hochformat richtet ihre Höhe nach dem Inhalt. Gemessene Dialoghöhen: '+
        ', '.join(f"{b['engine'].capitalize()} {b['hilfe_5_hochformat']['dialog_px']:.0f} Pixel" for b in cards['browsers'])+'.',
        '## Zusatzfälle und Bestandsschutz',
        f"Die Tests durchliefen {len(bestand['tageswechsel'])} Wechsel über die gemeinsame Tagesauswahl, per Datei und im simulierten LMS, sowie Tom und Celina in beiden Browsern. "
        f"Das tatsächlich eingebettete Modul des 08.12. stammt aus `{bestand['schutz_08']['commit']}` (SHA-256 `{bestand['schutz_08']['sha256']}`). "
        'Die SCORM-Probe erfasste Initialisierung und Beendigung der Sitzung. Der Testverbund dient der Integrationsprüfung.',
        '## Grenzen und nächster Praxistest',
        'Die Browserläufe verwenden Touch-Emulation. Für den Schulversuch stehen ein echtes iPad mit Bildschirmtastatur und VoiceOver, die Einbettung in itslearning sowie die selbstständige Arbeit von Förder- und ESA-Lernenden im vorgesehenen Zeitrahmen aus. '
        'Ein Buchstabe prüft den gewählten Fachanker. Die Qualität der selbst geschriebenen Begründung wird im Unterricht besprochen. Der individuelle Anfangs- und Schlussgrund wird auf Papier verglichen. '
        'Die bisherigen Zusatzfälle wurden funktional geprüft. Ihre vollständige fachliche Revision steht aus.',
        'Die fachlichen Vorher-Nachher-Befunde stehen in Fachpruefung.md. Das Sichtprüfungspaket ordnet die echten Browserbilder ihren Zuständen zu und enthält die zugehörigen JSON-Protokolle.'
    ]
    doc = OUT / 'Technischer-Pruefbericht.md'
    doc.write_text('\n\n'.join(report)+'\n')
    fach = OUT / 'Fachpruefung.md'
    pre = ROOT / 'docs/pruefnachweise/2a-vorpruefung'
    files['vorpruefung'] = pre / 'bedienung.json'
    files['fachliche-gegenpruefung'] = ROOT / 'docs/pruefnachweise/0212-fachliche-gegenpruefung-2a.json'
    review_path = files['fachliche-gegenpruefung'].relative_to(ROOT).as_posix()
    review_url = f'https://github.com/Feerson1617/Fallakte/blob/{commit}/{review_path}'
    fach.write_text((ROOT / 'docs/0212-fachpruefung-2a.md').read_text().replace(
        'pruefnachweise/'+files['fachliche-gegenpruefung'].name, review_url))
    review = json.loads(files['fachliche-gegenpruefung'].read_text())
    prior = subprocess.check_output(['git','show','8e87505:data/laura-0212.json'],cwd=ROOT)
    assert review['datenSHA256'] == sha256(prior).hexdigest()
    original=json.loads(prior)
    updated=json.loads((ROOT/'data/laura-0212.json').read_text())
    original['version']=updated['version']
    for key in ('anchors','anchorFeedback'):
        original['stages']['L05'][key]=updated['stages']['L05'][key]
    assert original==updated, 'Unbeabsichtigte Änderung außerhalb des biologischen Schlusschecks'
    index = ['# Sichtprüfung · Runde 2A', f'Commit `{commit}`. Die Bilder zeigen die offline geöffnete Anwendung.']
    for key, text in CAPTIONS.items():
        links = ' · '.join(f'[{engine.capitalize()}](Bilder/{engine}-{key}.jpg)' for engine in sorted(expected))
        index.append(f'- {text} {links}')
    for name in sorted(usage['bilder']):
        index.append(f'- [Bedienprüfung · {name.removesuffix(".jpg")}](Bilder/{name})')
    index.append('Die Aufnahmen der Bedienprüfung und die zugehörigen Bildschirmgrößen stehen im Bedienprotokoll. '
                 'Der Ordner Vorpruefung enthält echte Aufnahmen der vor dem Ausbau geprüften Zwei-Abschnitt-Fassung.')
    archive = OUT / 'Fallakte-Sichtpruefung.zip'
    gate = json.loads(files['vorpruefung'].read_text())
    assert gate['erprobte_abschnitte']==['L01','L02'] and gate['bilder']
    assert usage['erprobte_abschnitte']==['L01','L02','L03','L04','L05']
    with ZipFile(archive,'w',ZIP_DEFLATED) as z:
        z.writestr('Uebersicht.md','\n\n'.join(index)+'\n')
        for name in sorted(screenshots):
            z.write(QA/name, 'Bilder/'+name)
        for name, checksum in gate['bilder'].items():
            assert digest(pre/name)==checksum
            z.write(pre/name,'Vorpruefung/'+name)
        for key,path in files.items():
            z.write(path,'Protokolle/'+key+'.json')
        for path in (doc,fach):
            z.write(path,path.name)
    with ZipFile(archive) as z:
        assert z.testzip() is None
    print(f"{len(screenshots)} zugeordnete Screenshots und {len(files)} Protokolle · {archive.stat().st_size:,} Bytes")


if __name__ == '__main__':
    main()
