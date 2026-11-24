"""Packt ausschließlich vollständig geprüfte Vorbereitungsausgaben desselben Commits."""
import json
import os
from zipfile import ZipFile

from bauen import OUT, QA, PLAN, contracts, digest, json_text, pack, revision

TECH='Technischer-Pruefbericht.md'
DID='Fachlich-didaktischer-Abgleich.md'


def work_files(head,words):
    with ZipFile(PLAN) as source:
        files={n:source.read(n) for n in source.namelist() if not n.endswith('/')}
    files['Bildschirmwortlaut.json']=json_text(words)
    files['Bildschirmauftraege.md']='\n\n'.join(
        f"### {s['Niveau'].replace('Foerder','Förder')} · {s['Abschnitt']} · {s['Schritt']}\n\n{s['Bildschirm']}"
        for s in words)+'\n'
    files['Vorbereitung.html']=(OUT/'Vorbereitung.html').read_bytes()
    files['Uebergabe-an-Work.md']=f"""# Vorbereitung auf den 02.12.2026

Getesteter Programmstand `{head}`. Die vier Schülerfassungen und die ausgefüllten Referenzkarten im Ordner Karten stammen bytegleich aus dem Planungspaket. Bitte vor der Druckfreigabe auf dem vorgesehenen Schulkopierer prüfen.

Bildschirmauftraege.md enthält die in Chromium gelesenen regulären Ansichten in Unterrichtsreihenfolge. Stationsvertrag.json enthält zusätzlich den genauen Wortlaut jeder Fehlerrückmeldung, Hilfe und Anwendungsfrage. Die mitgepackte Offline-Datei zeigt auch Abschnittsauswahl, Wiederaufnahme und Ausfallweg. Kartenvertrag.json ordnet Kapitel, Papierfelder, Lösungen und Drucktexte einander zu.

## Vom Papier zurück zum Chat

Je Kapitel markieren die Lernenden ihre Abschnittskennung und ergänzen nach zwei Prüfungen zwei Felder. In den A-Kapiteln markieren MSA und AHR zusätzlich auf Papier eine der drei gedruckten Aussagen und begründen in Stichwörtern. Zurück am iPad geben sie den Buchstaben ein, tippen auf „Code prüfen“, dann auf „Nachricht senden“ und anschließend auf „Weiter im Chat“. Die Codefolge lautet B, A, C, B. Die ausklappbaren digitalen Aussagen sind als Ausfallhilfe für einen fehlenden Papierbogen beschriftet. Förder und ESA kehren nach dem Vergleich der Einträge über „Weiter im Chat“ zurück.

**Rückkehrhinweis für alle vier Druckfassungen in 1B, 2B, 3B und 4B**

Ergänze die Felder 3 und 4 auf Papier. Tippe am iPad auf „Vollständige Karte vergleichen“. Vergleiche alle vier Felder mit der Musterkarte. Verbessere sie bei Bedarf. Markiere „Karte kontrolliert“ auf Papier. Tippe dann auf „Weiter im Chat“.

Diesen Wortlaut bei der nächsten Gestaltung für den B-Rückweg verwenden. Die beigefügten Planungs-PDFs enthalten den bisherigen kürzeren Hinweis. Die tatsächlich getesteten Bildschirmtexte stehen in Bildschirmauftraege.md je Niveau und Kapitel.

Nach 2B endet die erste Stunde mit der Kontrolle der beiden Karten und der Markierung des nächsten Abschnitts auf Papier. Schnelle Lernende können sofort weiterarbeiten. Nach 4B vergleichen alle ihre vier Papierkarten mit den Musterkarten, ergänzen fehlende Einträge, schneiden die Karten aus und bewahren sie für den Unterrichtsbesuch auf. Die Liste der am iPad abgeschlossenen Fachchecks bezieht sich auf das gewählte Niveau und die aktuelle Sitzung. Die analoge Kartenkontrolle übernehmen die Lernenden.
"""
    return files


def reports(head,qa,checks):
    runs=qa['Wege']
    assert len(runs)==32 and len(qa['Navigation'])==12
    for r in runs:
        assert len(r['Fragen'])==(21 if r['Niveau'] in ('MSA','AHR') else 17)
    endings=qa['Abschlusswege']
    assert {(r['Browser'],r['Ausgabe'],r['Niveau']) for r in endings}=={
        (b,d,l) for b in ('chromium','webkit') for d in ('Offline','SCORM') for l in ('Foerder','ESA','MSA','AHR')}
    n=sum(len(r['Fragen']) for r in runs)
    errors=sum(q['Fehlantworten'] for r in runs for q in r['Fragen'])
    apps=sum(q['Anwendung'] for r in runs for q in r['Fragen'])
    base=checks['Bestand']
    table=['| Niveau | Information je Kapitel¹ | Fragen mit Auswahl¹ | Abschrift¹ | Bedienhandlungen A / B² |',
           '|---|---:|---:|---:|---:|']
    for level in ('Foerder','ESA','MSA','AHR'):
        data=[r for r in checks['Umfang'] if r['Niveau']==level]
        def span(k):
            values=[r[k] for r in data]
            return f'{min(values)}–{max(values)}'
        steps=next(r for r in runs if r['Niveau']==level and not r['Loesungshilfe'])['Interaktionen']
        table.append('| '+' | '.join([level.replace('Foerder','Förder'),span('Woerter_Information'),
            span('Woerter_Hauptfragen_mit_Auswahl'),span('Woerter_Abschrift'),f"{steps['1A']} / {steps['1B']}"])+' |')
    technical=f"""# Technischer Prüfbericht

Stand `{head}`. Getestet wurden die lokale Einzeldatei und das aus dem SCORM-ZIP entpackte Lernobjekt innerhalb eines übergeordneten SCORM-1.2-Testfensters. Das ZIP enthält ein gegen IMS- und ADL-Schemata validiertes Manifest an der Wurzel. Die HTML-Nutzdaten der beiden Ausgaben sind bytegleich.

## Änderungen seit d89e667

Nach dem Kartenvergleich führt „Weiter im Chat“ in 2B zur Zwischenansicht mit Papiermarkierung und freiwilliger Fortsetzung. In 4B öffnet die Schaltfläche den Abschluss mit vier Musterkarten, Ergänzen, Ausschneiden und Aufbewahren. Die Papier-Aussagen in den A-Kapiteln sind ausdrücklich als Ausfallhilfe beschriftet. Die Work-Übergabe enthält den vollständigen B-Rückweg für die Druckgestaltung.

In {len(endings)} zusätzlichen Browserwegen wurden die beiden Ansichten auf allen vier Niveaus nach Unterbrechung, Wiederaufnahme, direkter Kapitelwahl und vollständigem Neuladen geprüft. Frühere Kapitel erhalten im frischen 4B-Direkteinstieg keinen Nachweis. Die Anzeige liest die tatsächlich gelösten Fachfragen und bei MSA/AHR in A den gesendeten Papiercode. Das Öffnen von Musterkarten verändert diese Liste nicht. Der fachliche Datenblock einschließlich Abbildungen ist bytegleich zur geprüften Auslieferung d89e667 (SHA-256 `{checks['Material_SHA256_wie_d89e667']}`).

## Ausgeführte Prüfung

- Chromium und WebKit absolvierten je Ausgabe alle vier Niveaus einmal regulär und einmal auf dem Weg über die vollständige Lösungshilfe. Das ergibt {len(runs)} vollständige Durchläufe und {n} Haupt- bzw. Papierprüfungen einschließlich der Einstiege.
- Die Fehlerwege überprüften {errors} bestätigte Fehlantworten über die vier Kombinationen von Browser und Ausgabe hinweg. Geprüft wurden der jeweilige Rückmeldetext und alle fünf zugeordneten Hilfetexte. In {apps} Anwendungen nach Lösungshilfe wurden sämtliche falschen und die richtige Antwort bestätigt. Auf dem regulären Weg blieb die Zusatzfrage verborgen.
- Die acht Papierwechsel je Niveau, die zusätzlichen vier Codewege bei MSA/AHR, Freigabe nach eigener Prüfung, Korrektur bei Fehleingabe, Kleinschreibung mit Leerzeichen, Entzug einer Sendefreigabe nach Änderung und einmaliger Versand wurden am gebauten Programm geprüft. Die B-Kapitel zeigen alle vier Einträge zur persönlichen Kontrolle.
- Zwölf Kombinationen aus Ausgabe, Browser und Fenstergröße decken 768 × 1024, 1024 × 768 und 390 × 600 Pixel ab. Die Tests prüfen Direkteinstieg in alle acht Kapitel, Nachlesen bei einer Korrektur, getrennte Sitzungen, Abbruch und Bestätigung von „Neu beginnen“, Musterkarten und Neuladen mit frischem Einstieg in 3A. In der kleinen Ansicht wurde zusätzlich mit 150 % Grundschrift auf horizontales Überlaufen geprüft.
- Im Testhost protokollierte die LMS-Schnittstelle ausschließlich Start und Ende. Die Tests überwachten Laufzeitaufrufe und Cookies. Die Vorbereitung hält den Lernstand im Arbeitsspeicher.
- {base['verglichene_quellpfade']} historische Produktionsdateien sowie die veröffentlichten Prüfsummen der gemeinsamen HTML-/SCORM-Ausgabe und der beiden darin enthaltenen UB-Module wurden verglichen. Bezugsstände sind `{base['gemeinsame_referenz']}` und `{base['referenz_02']}`.

Die einzelnen Fragen, Prüfsummen und Ansichtsgrößen stehen in den JSON-Dateien der Sichtprüfung. Die Screenshots stammen aus den beiden verwendeten Browser-Engines.

## Noch vor dem Unterricht erproben

1. Das ZIP in itslearning als SCORM 1.2 importieren. Auf einem Schul-iPad den Start, Hoch-/Querformat und Rückkehr zum Kurs erproben. Die Einzeldatei zusätzlich über den vorgesehenen Offline-Öffnungsweg des Geräts starten.
2. In MSA bei 3A die Karte markieren, neu laden und über „Abschnitt auswählen“ wieder öffnen. Einen falschen und anschließend den richtigen Buchstaben prüfen, einmal senden und die Rückkehr beobachten.
3. Die Karten in tatsächlicher Größe ausdrucken. Lesbarkeit, Schreibplatz und die Passung zwischen Papier und iPad mit Förder- und ESA-Lernenden erproben. Für beide Stunden die Zeit für Lesen, Schreiben, Hilfen und Gerätewechsel erfassen.
"""
    did=f"""# Fachlich-didaktischer Abgleich

Geprüfter Stand `{head}`. Die Vorbereitung übernimmt die vorgelegten Stationsaufgaben und die wortgleichen Feldlösungen. Der Abgleich umfasste alle 32 Kombinationen aus Kapitel und Niveau, 64 Feldlösungen sowie 80 Zuordnungen zu Abschnittstitel und Original-Fachtext der UB-Bank. Auch die Lückentexte der vier Schüler-PDFs, die vollständigen Referenztexte und die gedruckte A/B/C-Reihenfolge der acht Papier-Fachchecks stimmen mit den Verträgen überein.

Die Informationsansichten unterscheiden die mechanische Barriere des Kondoms, den vorwiegend gehemmten Eisprung bei der Kombinationspille, die Kupferwirkung auf Spermien und die veränderte Durchlässigkeit des Schleims bei der Hormonspirale. Die Abbildungen zeigen Wirkprinzipien und Anwendungsgrenzen. Persönliche Eignung, Zustimmung und mögliche Beschwerden bleiben dort sichtbar, wo sie im Vertrag vorgesehen sind. Die Pearl-Index-Werte werden als historische Orientierungswerte mit eigener Quellenangabe verwendet. Ein individueller Schutz oder eine persönliche Verträglichkeit lässt sich daraus nicht ableiten.

Zwei Fachfragen geben pro Kapitel zwei Papierfelder frei. Die normale Materialnutzung gehört zur eigenständigen Arbeit. Nach der fünften Hilfe folgt die vertragliche Anwendung. Eine zuvor geöffnete Ausfallkarte wird bei einem späteren Erfolg berücksichtigt. Bereits festgehaltene Ergebnisse behalten ihre Einordnung. Gedruckte Begründungen und Abschriften beurteilt die Lehrkraft im Unterricht.

## Umfang der regulären Kapitel

{chr(10).join(table)}

¹ Wortzahlen als Spannen über die acht Kapitel des jeweiligen Niveaus. Die Informationsspalte zählt Fließtext und ergänzende Hinweise. Überschriften, Grafikbeschriftungen und freiwillige Quellenwege sind darin nicht enthalten. Die Abschrift umfasst ausschließlich die Feldlösungen.

² Gemessene Auswahl-, Prüf-, Eingabe- und Weiterhandlungen innerhalb eines regulären Kapitels. Eine Codeeingabe zählt als eine Handlung. Lesen, Handschrift, Scrollen und die anfängliche Niveauwahl sind gesondert zu berücksichtigen. Die Sollzeit von etwa 15 Minuten pro Methode ist ein Planungswert. Die tatsächliche Bearbeitungszeit und die Selbstständigkeit der Lerngruppe sind offen.

## Unterrichtliche Grenzen

Der Code prüft nur die ausgewählte biologische Aussage. Nach einem Geräteausfall zeigen die Markierungen auf Papier den Wiedereinstieg an. Bei Zeitnot kann die passende Musterkarte helfen, das einzige bleibende Lernprodukt zu vervollständigen. Ein auf diese Weise ergänztes Feld belegt keinen bestandenen digitalen Fachcheck.
"""
    return {TECH:technical,DID:did}


def release():
    head=revision()
    qa=json.loads((QA/'Browserpruefung.json').read_text())
    checks=json.loads((QA/'Vertragspruefung.json').read_text())
    assert head==checks['commit']==qa['commit']
    assert qa['HTML_SHA256']==digest((OUT/'Vorbereitung.html').read_bytes())
    words=json.loads((QA/'Bildschirmwortlaut.json').read_text())
    assert {s['Niveau'] for s in words}==set(contracts()[0]['levels'])
    # Work erhält den tatsächlichen Rückweg aus allen 16 getesteten B-Ansichten.
    for level in contracts()[0]['levels']:
        for key in ('1B','2B','3B','4B'):
            path={r['Schritt']:r['Bildschirm'] for r in words if r['Niveau']==level and r['Abschnitt']==key}
            assert 'Vollständige Karte vergleichen' in path['Papierauftrag und Rückkehr']
            assert 'Karte kontrolliert' in path['Kartenkontrolle'] and 'Weiter im Chat' in path['Kartenkontrolle']
            if key=='2B':assert 'Zwischenansicht nach 2B' in path
            if key=='4B':assert 'Abschlussansicht nach 4B' in path
    docs=reports(head,qa,checks)
    for name,data in docs.items():(OUT/name).write_text(data)
    work=work_files(head,words)
    work[DID]=docs[DID]
    pack(OUT/'Work-Material-Vorbereitung.zip',work)
    evidence={p.name:p.read_bytes() for p in QA.glob('*.png')}
    assert {'Zwischenansicht-2B.png','Abschluss-4B.png','Zwischenansicht-2B-Direkteinstieg.png',
            'Abschluss-4B-nach-Neuladen.png'} <= evidence.keys()
    assert len(evidence)>=20 and all(b.startswith(b'\x89PNG') for b in evidence.values())
    for name in ('Vertragspruefung.json','Browserpruefung.json'):
        evidence[name]=(QA/name).read_bytes()
    pack(OUT/'Vorbereitung-Sichtpruefung.zip',evidence|docs)
    files={}
    for name in ('Vorbereitung.html','Vorbereitung-SCORM12.zip','Work-Material-Vorbereitung.zip',
                 'Vorbereitung-Sichtpruefung.zip',TECH,DID):
        p=OUT/name
        if p.suffix=='.zip':
            with ZipFile(p) as z:
                assert z.testzip() is None
                if name.startswith('Work-'):assert digest(z.read('Vorbereitung.html'))==qa['HTML_SHA256']
        files[name]=dict(sha256=digest(p.read_bytes()),bytes=p.stat().st_size)
    (OUT/'Buildnachweis.json').write_text(json_text(dict(commit=head,actions_run=os.getenv('GITHUB_RUN_ID'),
        planung_sha256=digest(PLAN.read_bytes()),geschuetzte_ausgabe=checks['Bestand'],dateien=files)))


if __name__=='__main__':release()
