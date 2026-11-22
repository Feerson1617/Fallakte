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


def main():
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    app_hash = digest(OUT / 'Fallakte.html')
    files = {k: QA / (k+'.json') for k in ('browser', 'material', 'karten')}
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
    screenshots = browser['screenshots']
    assert set(screenshots) == {f'{engine}-{key}.jpg' for engine in expected for key in CAPTIONS}
    for name, checksum in screenshots.items():
        path = QA / name
        assert digest(path) == checksum and path.read_bytes().startswith(b'\xff\xd8\xff')
    table = ['| Browser | Version | Beratungswege | Abgeschlossene Kapitel |', '| --- | --- | ---: | ---: |']
    for b in browser['browsers']:
        paths = b['paths']
        assert len(paths)==28 and all(len(p['chapters'])==2 for p in paths)
        table.append(f"| {b['engine'].capitalize()} | {b['version']} | {len(paths)} | {sum(len(p['chapters']) for p in paths)} |")
    report = [
        '# Technischer Prüfbericht · Korrekturrunde 1b für den 02.12.2026',
        f"Branch `entwicklung/0212-neukonzeption` · Commit `{commit}` · Inhaltsbank `{material['bankversion']}`.",
        f"Die geprüfte **Fallakte.html** ist {material['bytes']:_} Bytes groß. SHA-256 `{app_hash}`.".replace('_', ' '),
        '## Browserdurchläufe', '\n'.join(table),
        'Die Vergleichsbasis der sechs Korrekturen war die aus Actions-Lauf 45046241473 heruntergeladene HTML-Datei '
        'des Commits `8c6bd80`. Die Zustände vor und nach der Korrektur sind im fachlichen Prüfbericht beschrieben.',
        'Jede Zeile umfasst vier Niveaus und sieben Ausgangsstrategien. In jedem Weg wurde Laura 1 mit einer Begründung versendet und Laura 2 neu beurteilt. '
        'Bei Pille oder Spirale allein in Laura 2 wurde das fehlende Schutzziel erklärt. Die Lernenden konnten die Strategie ergänzen und erneut prüfen. Die Browserprotokolle enthalten die tatsächlich gesendete Strategie und die Antwort von Laura.',
        'Geprüft wurden korrekte und falsche Gründe beziehungsweise Buchstaben, leere Eingaben, Leerzeichen, Kleinschreibung, Methodenwechsel nach Freigabe und wiederholtes Senden. '
        'Die Rückfragen und fünf Hilfen wurden vor und nach der Auswahl geöffnet. Frühere Fragen blieben als frühere Gesprächsteile erkennbar. '
        'Weitere Durchläufe prüften die Sicherung in beiden Abschnitten, die Rückkehr zur Übersicht, Niveauwechsel, Neustart und den Direkteinstieg in Laura 2 ohne erfundene Vorgeschichte.',
        'Die lokale Datei lief ohne externe Netzabrufe, beobachtete Schreibzugriffe auf dauerhafte Webspeicher oder Skriptausnahmen. Ein vollständiges Neuladen führte zur bewussten Wahl eines neuen Einstiegs.',
        '## Nachprüfung der sechs Korrekturen',
        '1. In der Fallübersicht und im Gespräch liegt die Sicherung im geschlossenen Lehrkraftzugang. '
        'Der ausdrücklich geöffnete Überblick zeigt die vollständigen Informationen und erhält den aktuellen Entwurf.\n'
        '2. Nach einer Auswahl gehören Arbeitsimpuls und Kartenstelle zur gewählten Strategie. Bei Kombinationen lassen sich beide Beiträge gezielt nachlesen.\n'
        '3. Bei einem offenen Schutzziel können Förder und ESA bewusst ergänzen. MSA und AHR treffen eine neue Wahl und bearbeiten den Fachcheck erneut.\n'
        '4. Förder erhält die Materialinformation unmittelbar. ESA, MSA und AHR können die Latexfrage vor der fachlichen Prüfung anhand der Karte untersuchen.\n'
        '5. Der reguläre Weg in MSA und AHR führt zum bezeichneten Papierabschnitt. Die freiwillige Ersatzansicht enthält denselben Denkauftrag und alle drei Aussagen.\n'
        '6. Beim Wiedereinstieg sind genau die beiden spielbaren Abschnitte mit ihren vollständigen, einmal genannten Titeln zugänglich.',
        '## Material und Darstellung',
        f"Die in der HTML eingebettete Bank und der Work-Export wurden verglichen. Geprüft wurden {material['aufgaben']} Niveauaufgaben, {material['strategiekontexte']} Strategiekontexte und {material['begruendungsoptionen']} geschlossene Antwortmöglichkeiten, einschließlich der Planung für Laura 3 bis 5.",
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
        'Ein Buchstabe prüft den gewählten Fachanker. Die Qualität der selbst geschriebenen Begründung wird im Unterricht besprochen. Der digitale Prototyp endet nach Laura 2. '
        'Die bisherigen Zusatzfälle wurden funktional geprüft. Ihre vollständige fachliche Revision steht aus.',
        'Die fachlichen Vorher-Nachher-Befunde stehen in Fachpruefung.md. Das Sichtprüfungspaket ordnet die echten Browserbilder ihren Zuständen zu und enthält die zugehörigen JSON-Protokolle.'
    ]
    doc = OUT / 'Technischer-Pruefbericht.md'
    doc.write_text('\n\n'.join(report)+'\n')
    fach = OUT / 'Fachpruefung.md'
    files['ausgangsstand'] = ROOT / 'docs/pruefnachweise/0212-1b-vorher.json'
    files['fachliche-gegenpruefung'] = ROOT / 'docs/pruefnachweise/0212-fachliche-gegenpruefung-1b.json'
    review_path = files['fachliche-gegenpruefung'].relative_to(ROOT).as_posix()
    review_url = f'https://github.com/Feerson1617/Fallakte/blob/{commit}/{review_path}'
    fach.write_text((ROOT / 'docs/0212-fachpruefung-1b.md').read_text().replace(
        'pruefnachweise/'+files['fachliche-gegenpruefung'].name, review_url))
    review = json.loads(files['fachliche-gegenpruefung'].read_text())
    assert review['datenSHA256'] == digest(ROOT / 'data/laura-0212.json')
    assert review['auslieferungRunde1SHA256'] == json.loads(files['ausgangsstand'].read_text())['artefaktSHA256']
    index = ['# Sichtprüfung · Korrekturrunde 1b', f'Commit `{commit}`. Dieselben Zustände wurden in Chromium und WebKit aufgenommen.']
    for key, text in CAPTIONS.items():
        links = ' · '.join(f'[{engine.capitalize()}](Bilder/{engine}-{key}.jpg)' for engine in sorted(expected))
        index.append(f'- {text} {links}')
    index.append('Die vier technischen Protokolle beziehen sich auf die ausgelieferte HTML. '
                 'Die fachliche Gegenprüfung ist das Originalprotokoll der unabhängigen Durchsicht derselben '
                 'Inhaltsbank vor dem Abschlusscommit. Das Protokoll zum Ausgangsstand dokumentiert die frühere Fassung.')
    archive = OUT / 'Fallakte-Sichtpruefung.zip'
    with ZipFile(archive,'w',ZIP_DEFLATED) as z:
        z.writestr('Uebersicht.md','\n\n'.join(index)+'\n')
        for name in sorted(screenshots):
            z.write(QA/name, 'Bilder/'+name)
        for key,path in files.items():
            z.write(path,'Protokolle/'+key+'.json')
        for path in (doc,fach):
            z.write(path,path.name)
    with ZipFile(archive) as z:
        assert z.testzip() is None
    print(f"{len(screenshots)} zugeordnete Screenshots und {len(files)} Protokolle · {archive.stat().st_size:,} Bytes")


if __name__ == '__main__':
    main()
