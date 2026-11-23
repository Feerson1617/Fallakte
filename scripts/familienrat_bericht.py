"""Package only browser evidence for the two modules embedded in this specific build."""
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from familienrat_build import ROOT, REF, OUT, BASE, OLD, DAY02, PRACTICE, git, sha

def main():
    qa=ROOT/'build/Familienrat-QA'
    shield=ROOT/'build/Familienrat-Schutz'
    head=git('rev-parse','HEAD').decode().strip()
    bank=json.loads((OUT/'Work-Materialvertrag.json').read_text())
    runs=json.loads((qa/'Browser.json').read_text())
    protect=json.loads((shield/'Referenz.json').read_text())
    coupled=json.loads((shield/'Abnahme.json').read_text())
    checksum=sha((OUT/'Fallakte.html').read_bytes())
    assert bank['commit']==runs['commit']==head and checksum==runs['sha256']==coupled['html_sha256']
    assert protect['referenz']==BASE and protect['html_02']==DAY02
    before=ROOT/'docs/pruefnachweise/0812-korrektur-vorher.json'
    screenshots=bank['screens']
    with ZipFile(OUT/'Fallakte-Sichtpruefung.zip','w',ZIP_DEFLATED) as z:
        for name,caption in screenshots.items():
            data=(qa/name).read_bytes()
            assert data.startswith(b'\xff\xd8\xff') and len(data)>3000,(name,caption)
            z.writestr(name,data)
        z.writestr('Bildverzeichnis.md','# Ansichten der getesteten Auslieferung\n\n'+'\n'.join('- '+k+' · '+v for k,v in screenshots.items()))
        z.write(qa/'Browser.json','08-12/Browser.json')
        z.write(before,'08-12/Ausgangspruefung.json')
        for name in ['Abnahme.json','Referenz.json']:z.write(shield/name,'02-12/'+name)
    with ZipFile(OUT/'Work-Uebergabe.zip','w',ZIP_DEFLATED) as z:
        for filename in ['Work-Materialvertrag.json','Work-Materialvertrag.md','Fallakte-Sichtpruefung.zip']:z.write(OUT/filename,filename)
        for person,file in bank['designFiles'].items():
            raw=(ROOT/'assets'/file).read_bytes() if person=='Laura' else git('show',OLD+':module/08-12/assets/'+file)
            z.writestr('Portraets/'+file,raw)
        for file in sorted((REF/'dist/Runde-1').glob('*Material*')):z.write(file,'Referenz-02/'+file.name)
        for file in sorted((REF/'dist/Uebungsakte').glob('*Material*')):z.write(file,'Referenz-02/'+file.name)
    rows=[r for engine in runs['browser'] for r in engine['wege']]
    timing=[r for r in rows if r['weg']=='Regulärer Pflichtweg']
    assert len(rows)==24 and len(coupled['wege'])==8 and timing
    samples=[a for row in rows for a in row['anwendungen']]
    assert len(samples)>=16 and all(any(a['status']==bank['ui'][status] for a in samples) for status in ('applied','assisted'))
    assert sum('eigene_verbindungen' in row for row in rows)==2
    word_counts=[a['woerter_vor_antwort'] for a in samples]
    report=[
        '# Abnahme · Familiennachrichten am 08.12.2026',f'Entwicklungsstand `{head}` · Inhaltsbank {bank["version"]}',
        '## Drei Befunde an der Auslieferung und ihre Korrektur',
        'Die lokale HTML-Datei aus Actions-Lauf 45196390973 (Commit `b0b5d0f`) wurde vor dem Eingriff in Chromium und WebKit bedient. Die wörtlichen Ergebnisse stehen in 08-12/Ausgangspruefung.json im Sichtprüfungspaket.',
        '1. AHR konnte leer vergleichen und nach einer Auswahl „Ohne Hilfe zugeordnet“ erhalten. Jetzt geben MSA und AHR einen kurzen eigenen Gedanken ein. Bei ausdrücklich genannten Werten, Regeln und Ratschlägen können sie auch einen passenden Originalsatz markieren. Erst dann folgt die Bedeutungswahl. Die App bewertet freie Formulierungen nicht.',
        '2. Bei Mutter und späterer Fruchtbarkeit bescheinigte die Schlussansicht „Ohne Hilfe zugeordnet“. Jetzt nennt die App die Herkunft des Fakts. Wer die Verbindung beibehält, begründet sie in wenigen eigenen Worten, prüft die Grenze des Fakts und hält den Grund auf dem Bogen fest. Die Ergebnisansicht trennt die geprüfte Fachauswahl und den ungeprüften persönlichen Grund für jede Person.',
        '3. Nach Hilfe 5 kam man bei Mutter direkt zur Freundin und bei der Freundin direkt zu Laura. Jetzt erscheint beim Festhalten einmal eine veränderte Frage. Die ergänzte Lösung bleibt dabei verdeckt. Eine falsche Antwort erhält eine konkrete Erklärung und lässt den Weg offen. Hilfe während dieser neuen Frage und eine noch ausstehende Anwendung werden eigens gekennzeichnet.',
        '## A · Bestandsschutz des 02.12.',
        f'Das eingebettete Dezember-02-Modul hat die SHA-256-Prüfsumme `{DAY02}` des Release-Commits `{BASE}`. Auch Übungs-HTML und Übungs-SCORM stimmen mit der Veröffentlichung überein. '
        f'{protect["wege_laura"]} vollständige Laura-Wege liefen in der identischen Referenz. Geprüft wurden Kartenrückkehr, fünf Hilfen, individuelle Begründungen, Sicherung, Tom, Celina, Übung und Wiedereinstieg. '
        'Acht zusätzliche Laura-Durchläufe nutzten den neuen gemeinsamen Rahmen. Die ESA-Arbeitsansicht stimmte in beiden Browsern pixelgenau mit dem alten Release überein. Beim Tageswechsel blieben beide Entwürfe erhalten.',
        '## B · Unterrichtsweg des 08.12.',
        'Mutter und Freundin führen von den ausgesprochenen Werten und Normen zu zwei verschiedenen biologischen Ergänzungen. Die Ausgangsnachrichten bleiben sichtbar. '
        'Bei der Großmutter wird der im Schutzgebot enthaltene Wert ausdrücklich gemacht, beim Vater die im ärztlichen Rat enthaltene allgemeine Regel. '
        'Die Pflichtaufgabe „Lauras Frage“ verlangt persönliche Gewichtung, passenden biologischen Beleg und eine Aussage über dessen Grenzen. '
        'Mutter, Freundin und begründete Gleichgewichtung sind zulässig. Freie Sätze werden mit einer Bedeutungswahl verglichen. Nur diese Auswahl wird geprüft.',
        'Auf vier Niveaus und in vier gemischten Kombinationen wurden richtige und unpassende Antworten, alle Hilfestufen, die freiwilligen Fälle und die persönlichen Papieraufträge bedient. '
        'Die Protokolle unterscheiden reguläre Wege von zusätzlichen Fehler- und Hilfeproben. Die automatische Prüfung misst weder die Qualität des persönlichen Textes noch das Verständnis einer einzelnen Person.',
        '## C · Software und Papier',
        'Vor der gemeinsamen Prüfung markieren beide Lernenden ihren eigenen Gedanken. Nach der Rückmeldung halten sie die geprüfte Ergänzung getrennt fest. '
        'Bei Lauras zweiter Nachricht entstehen zuerst persönliche Begründungen auf zwei Bögen. Erst danach werden die Belege personweise verglichen. '
        'Über „Lauras Frage“ oder „Nach Neustart“ sind Bewertungsauftrag und Ergebnisgrundlagen früh erreichbar. Unterstützt gelesene Fakten werden als Hilfen gekennzeichnet.',
        '## D · Auslieferung und technische Messung',
        'Getestet wurden die lokale HTML-Datei und der entpackte SCORM-Einstieg mit simulierten LMS-Aufrufen. Das Manifest ist schemavalidiert. '
        'Beim SCO-Test wurden nur Initialisierung und Beendigung beobachtet. Die Anwendung hält die eigenen Antworten im Arbeitsspeicher. '
        'Hoch- und Querformat sowie 390 × 844 Pixel bei vergrößerter Schrift wurden per Touch bedient.',
        f'Ohne vollständige Lösungshilfe gibt es keinen neuen Anwendungsabschnitt. Nach Hilfe 5 kommt je betroffenem Fall im vorhandenen Abschnitt „Festhalten“ eine Auswahl hinzu. Die gemessene Frage einschließlich sichtbarer Optionen und Bedienbeschriftungen umfasst vor der Antwort {min(word_counts)} bis {max(word_counts)} Wörter. Bei einem fallübergreifenden Beleg kommen ein kurzer Grund und eine Bestätigung im bestehenden Bewertungsabschnitt hinzu. Auf MSA/AHR lässt sich für sechs der zehn Teilfragen eine Textstelle zeigen. In den übrigen vier Feldern genügen Stichworte.',
        '| Browser | Team | Berührungen ab Fallstart | Abschnittsansichten | Digitale Schreibfelder | Sekunden |\n|---|---|---:|---:|---:|---:|\n'+'\n'.join(
            '| '+r['browser']+' '+r['version']+' | '+' + '.join(r['niveaus'])+f" | {r['tipps']} | {len(r['ansichten'])} | {r['schreibfelder']} | {r['sekunden']:.1f} |" for r in timing),
        'Messung ab Öffnen der Mutter bis zum Angebot der Vertiefungen, einschließlich des persönlichen Belegvergleichs pro Person. '
        'Die Ansichten zählen aufeinanderfolgende sichtbare Abschnittstitel. Teilfragen mit gleichem Titel können mehrere Berührungen erfordern. '
        'Die Messung verwendet automatisierte Touch-Eingaben ohne Lese-, Gesprächs- und Schreibzeit.',
        'Die im gebauten Offline-Modul eingebettete Aufgabenbank wurde vollständig gegen den JSON-Vertrag geprüft, alle Werte auch gegen die Markdown-Fassung. Der Startinhalt im SCORM-Paket ist bytegleich zur Offline-Datei. Pflichtaufgaben, Antwortmatrix, Fallnachrichten, Fachkarten und persönliche Bewertungsaufträge wurden zusätzlich mit dem geprüften Stand b0b5d0f verglichen.',
        '## E · Verbleibende Praxistests',
        'Automatisierte Bedienzeiten sind keine Schülerbearbeitungszeiten. Ob 25 Minuten einschließlich individueller Papierarbeit ausreichen, muss die Lerngruppe zeigen. '
        'Auf einem echten Schul-iPad im itslearning-Testkurs das SCO starten, in einem gemischten Team eine Karte öffnen und zurückkehren, '
        'eine eigene Formulierung bei eingeblendeter Tastatur eingeben, neu laden und direkt in Freundin 3 sowie in Lauras Frage einsteigen. '
        'Die analoge Sicherung nutzt die persönlichen Bögen. Work benötigt zur Endgestaltung die separate Original-Materialserie vom 02.12.'
    ]
    (OUT/'Abnahmebericht.md').write_text('\n\n'.join(report)+'\n')
    changed=git('diff','--name-status',BASE,head).decode()
    (OUT/'Dateiuebersicht.md').write_text('# Änderungen am Entwicklungszweig\n\nBasis `'+BASE+'`\n\n```text\n'+changed+'```\n')
    files={}
    for p in sorted(OUT.iterdir()):
        if p.name=='Buildnachweis.json':continue
        if p.suffix=='.zip':
            with ZipFile(p) as z:assert z.testzip() is None
        files[p.name]=dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes()))
    metadata=dict(commit=head,branch='entwicklung/0812-neukonzeption-final',basis=BASE,tag02_sha256=DAY02,
                  uebungsakte_sha256=PRACTICE,version=bank['version'],dateien=files)
    (OUT/'Buildnachweis.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
