"""Package only browser evidence for the two modules embedded in this specific build."""
import io
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
    media=bank['media']
    rows=[r for engine in runs['browser'] for r in engine['wege']]
    traces=[dict(browser=r['browser'],niveaus=r['niveaus'],format=r['format'],papierweg=r['papierweg']) for r in rows]
    coverage={key for r in rows for key in r['alle_uebergaben']}
    assert coverage==set(media['steps']) and len(traces)==24
    states=ROOT/'build/Familienrat-Zustaende/Zustaende.json'
    learning=ROOT/'build/Familienrat-Lernwege/Lernwege.json'
    proof=ROOT/'docs/pruefnachweise'
    for file in (states,learning):
        log=json.loads(file.read_text())
        assert log['commit']==head and log['html_sha256']==checksum
    assert len(json.loads(learning.read_text())['wege'])==8
    assert all(sum('team' in case for case in engine['pruefungen'])==16 for engine in json.loads(states.read_text())['browser'])
    freeze=json.loads((shield/'Dateivergleich.json').read_text())
    assert freeze['commit']==head and freeze['referenz']==BASE
    reports=['Fachgutachten.md','Aenderungsbericht.md']
    for name in reports:
        content=(ROOT/'docs'/('0812-'+name)).read_text()
        (OUT/name).write_text(content.replace('RELEASE_COMMIT',head))
    matrix_files=['Medienwechsel-und-Papierfeldmatrix.'+ext for ext in ('md','json')]
    assert json.loads((OUT/matrix_files[1]).read_text())==dict(commit=head,**media)
    media_report=[
        '# Prüfbericht · Fallakte und persönlicher Lernbogen',f'Commit `{head}` · geprüfte gemeinsame HTML-Datei `{checksum}`',
        'Im Pflichtweg wurden vor der Auswahl die persönlichen Erstfelder geöffnet, nach der fachlichen Rückmeldung die getrennten Ergebnisfelder angezeigt. Nach vorab offengelegter Ergänzung erschien der Ergebnisauftrag nach erfolgreicher Anwendung. Eine Hilfenutzung bei anderen Denkhandlungen löste diesen Zwischenschritt nicht aus. Beide persönlichen Einträge zu Laura nutzen dieselbe Fläche.',
        '## Wege in der gebauten Anwendung',
        '| Niveau | Beobachtete Wegfolge | Browser |\n|---|---|---|',
    ]
    for tier in bank['levels']:
        matches=[r for r in traces if r['niveaus']==[tier]]
        browsers=sorted({r['browser'] for r in matches})
        assert len(browsers)==2
        path=' → '.join(s['feld']+' → '+s['rueckweg'].removeprefix('Weiter im Chat: ') for s in matches[0]['papierweg'])
        media_report[-1]+='\n| '+tier+' | '+path+' → gemeinsame Sicherung | '+', '.join(browsers)+' |'
    media_report.extend([
        '## Paararbeit, Wiedereinstieg und Reserven',
        'Für jede Person wurden Niveau, sichtbarer Wortlaut, Feld und Folgeschritt separat am Bildschirm abgeglichen. Getestete Paare waren Förder/ESA, ESA/MSA, MSA/AHR und Förder/AHR. In „Lauras Frage – Prüfen“ wurde jeder Beleg einzeln bearbeitet. Die persönliche Begründung bleibt offen.',
        'Bei den freiwilligen Fällen wurde die Rückkehrtaste sowohl nach regulärem Abschluss als auch nach einem frischen Direkteinstieg betätigt. Nach einem Neuladen waren die Ergänzung der Freundin, die kurze Anwendung und der Belegvergleich direkt erreichbar. Die Ergebnisfelder behielten ihre Bezeichnung.',
        f'{len(coverage)} Übergaben einschließlich bedingter Rückwege, {len(media["fields"])} Papierfelder und 24 Durchläufe. Die sichtbaren Aufträge und Rückkehrtexte stehen in 08-12/Medienwege.json. Die zwölf Übergabepunkte beziehen sich auf neun bereits vereinbarte Papierfelder. Die Erstspur bleibt im Abschnitt. Der Abschluss führt in die analoge Sicherung.',
        '## Grenzen der Prüfung',
        'Die Browserprüfung bediente Offline-HTML und SCORM mit simuliertem LMS im Hoch- und Querformat sowie bei großer Schrift. Geprüft wurden die Bildschirmhandlungen und der Fertigungsvertrag. Drucklayout, tatsächliche Papierbearbeitung in 25 Minuten, ein Schul-iPad und itslearning erfordern eine Erprobung mit dem von Work gesetzten Material.',
        f'Der eingebettete Unterrichtstag vom 02.12. entspricht bytegenau der Referenz `{BASE}` mit SHA-256 `{DAY02}`. Die Browser- und Bildvergleiche sind im Abnahmebericht dokumentiert.'
    ])
    (OUT/'Medienfuehrung-Pruefbericht.md').write_text('\n\n'.join(media_report)+'\n')
    with ZipFile(OUT/'Fallakte-Sichtpruefung.zip','w',ZIP_DEFLATED) as z:
        for name,caption in screenshots.items():
            data=(qa/name).read_bytes()
            assert data.startswith(b'\xff\xd8\xff') and len(data)>3000,(name,caption)
            z.writestr(name,data)
        z.writestr('Bildverzeichnis.md','# Ansichten der getesteten Auslieferung\n\n'+'\n'.join('- '+k+' · '+v for k,v in screenshots.items()))
        z.write(qa/'Browser.json','08-12/Browser.json')
        z.writestr('08-12/Medienwege.json',json.dumps(dict(commit=head,html_sha256=checksum,wege=traces),ensure_ascii=False,indent=2))
        z.write(OUT/'Medienfuehrung-Pruefbericht.md','08-12/Medienfuehrung-Pruefbericht.md')
        z.write(before,'08-12/Ausgangspruefung.json')
        for file in (states,learning):z.write(file,'08-12/'+file.name)
        for name in ('0812-ecab26f-browser.json','0812-quellenstand.json','0812-bedienprotokoll.json'):
            z.write(proof/name,'08-12/'+name)
        for name in reports:z.write(OUT/name,name)
        for name in ['Dateivergleich.json','Abnahme.json','Referenz.json']:z.write(shield/name,'02-12/'+name)
    with ZipFile(OUT/'Work-Uebergabe.zip','w',ZIP_DEFLATED) as z:
        for filename in ['Work-Materialvertrag.json','Work-Materialvertrag.md',*matrix_files,'Medienfuehrung-Pruefbericht.md','Fallakte-Sichtpruefung.zip',*reports]:z.write(OUT/filename,filename)
        for person,file in bank['designFiles'].items():
            raw=(ROOT/'assets'/file).read_bytes() if person=='Laura' else git('show',OLD+':module/08-12/assets/'+file)
            z.writestr('Portraets/'+file,raw)
        for file in sorted((REF/'dist/Runde-1').glob('*Material*')):z.write(file,'Referenz-02/'+file.name)
        for file in sorted((REF/'dist/Uebungsakte').glob('*Material*')):z.write(file,'Referenz-02/'+file.name)
    timing=[r for r in rows if r['weg']=='Regulärer Pflichtweg']
    assert len(rows)==24 and len(coupled['wege'])==8 and timing
    samples=[a for row in rows for a in row['anwendungen']]
    assert len(samples)>=16 and all(any(a['status']==bank['ui'][status] for a in samples) for status in ('applied','assisted'))
    assert sum('eigene_verbindungen' in row for row in rows)==2
    word_counts=[a['woerter_vor_antwort'] for a in samples]
    report=[
        '# Abnahme · Familiennachrichten am 08.12.2026',f'Entwicklungsstand `{head}` · Inhaltsbank {bank["version"]}',
        '## Medienführung für Work',
        'Die verpflichtenden Erst- und Ergebnisfelder, die persönliche Bewertungsfläche, die bedingten Rückwege und die digitale Anwendung nach Hilfe 5 sind in der Medienwechsel- und Papierfeldmatrix festgelegt. Der gesonderte Medienführungsbericht enthält die in Chromium und WebKit bedienten Wege pro Niveau.',
        '## Korrekturstand und belastbare Nachweise',
        'Ausgangsstand ecab26f. Der Änderungsbericht ordnet jedem Befund den zugehörigen Browser- oder Dateinachweis zu. Das Fachgutachten dokumentiert die medizinische und curriculare Prüfung sowie die offene praktische Abnahme.',
        'Für beide Browser liegen alle 16 geordneten Niveaupaare vor. Der gesonderte Test der Schülerwege bedient acht vollständige Wege anhand sichtbarer Antworttexte mit eigenen Formulierungen. Das Protokoll der interaktiven Durchsicht dokumentiert die gesonderte Bedienung aus Förder-Perspektive sowie je Niveau zwei interaktive WebKit-Durchläufe.',
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
        f'Ohne vollständige Lösungshilfe gibt es keinen neuen Anwendungsabschnitt. Nach einer offengelegten Ergänzung kommt im betroffenen Fall im vorhandenen Abschnitt „Festhalten“ eine Auswahl hinzu. Die gemessene Frage einschließlich sichtbarer Optionen und Bedienbeschriftungen umfasst vor der Antwort {min(word_counts)} bis {max(word_counts)} Wörter. Bei einem fallübergreifenden Beleg kommen ein kurzer Grund und eine Bestätigung im bestehenden Bewertungsabschnitt hinzu. Auf MSA und AHR gehören eigene Worte vor den Vergleich. Bei den ausdrücklich genannten Bestandteilen kann ein Originalsatz als zusätzlicher Beleg dienen.',
        '| Browser | Team | Berührungen ab Fallstart | Abschnittsansichten | Digitale Schreibfelder | Sekunden |\n|---|---|---:|---:|---:|---:|\n'+'\n'.join(
            '| '+r['browser']+' '+r['version']+' | '+' + '.join(r['niveaus'])+f" | {r['tipps']} | {len(r['ansichten'])} | {r['schreibfelder']} | {r['sekunden']:.1f} |" for r in timing),
        'Messung ab Öffnen der Mutter bis zum Angebot der Vertiefungen, einschließlich des persönlichen Belegvergleichs pro Person. '
        'Die Ansichten zählen aufeinanderfolgende sichtbare Abschnittstitel. Teilfragen mit gleichem Titel können mehrere Berührungen erfordern. '
        'Die Messung verwendet automatisierte Touch-Eingaben ohne Lese-, Gesprächs- und Schreibzeit.',
        'Die im gebauten Offline-Modul eingebettete Aufgabenbank wurde vollständig gegen den JSON-Vertrag geprüft, alle Werte auch gegen die Markdown-Fassung. Der Startinhalt im SCORM-Paket ist bytegleich zur Offline-Datei. Pflichtaufgaben, Antwortmatrix, Fallnachrichten, Fachkarten und persönliche Bewertungsaufträge wurden mit ecab26f abgeglichen. Die freigegebenen fachsprachlichen Präzisierungen sind im Änderungsbericht ausgewiesen.',
        '## E · Verbleibende Praxistests',
        'Automatisierte Bedienzeiten sind keine Schülerbearbeitungszeiten. Ob 25 Minuten einschließlich individueller Papierarbeit ausreichen, muss die Lerngruppe zeigen. '
        'Auf einem echten Schul-iPad im itslearning-Testkurs das SCO starten, in einem gemischten Team eine Karte öffnen und zurückkehren, '
        'eine eigene Formulierung bei eingeblendeter Tastatur eingeben, neu laden und direkt in Freundin 3 sowie in Lauras Frage einsteigen. '
        'Die analoge Sicherung nutzt die persönlichen Bögen. Work benötigt zur Endgestaltung die separate Original-Materialserie vom 02.12.'
    ]
    (OUT/'Abnahmebericht.md').write_text('\n\n'.join(report)+'\n')
    changed=git('diff','--name-status',BASE,head).decode()
    (OUT/'Dateiuebersicht.md').write_text('# Änderungen am Entwicklungszweig\n\nBasis `'+BASE+'`\n\n```text\n'+changed+'```\n')
    with ZipFile(OUT/'Fallakte-HTML-Pruefpaket.zip','w',ZIP_DEFLATED) as z:
        z.write(OUT/'Fallakte.html','Fallakte.html')
        z.writestr('Liesmich.txt','Stand '+head+'\nEntpacke das Paket. Öffne Fallakte.html lokal im Browser. Wähle den 08.12. und ein Niveau. Das Gerät benötigt keine Internetverbindung. Persönliche Einträge auf dem Lernbogen sichern.\n')
    with ZipFile(OUT/'Fallakte-Pruefquellen.zip','w',ZIP_DEFLATED) as z:
        with ZipFile(io.BytesIO(git('archive','--format=zip',head))) as tree:
            for path in tree.namelist():
                if not path.endswith('/'):z.writestr('Repository/'+path,tree.read(path))
        z.write(OUT/'Work-Materialvertrag.json','Gebaut/Inhaltsdatenbank.json')
        z.write(REF/'dist/Vorabkandidat/Fallakte.html','Referenz/Unveraenderter-Rahmen.html')
        for name,file in bank['designFiles'].items():
            if name!='Laura':z.writestr('Referenz/Portraets/'+file,git('show',OLD+':module/08-12/assets/'+file))
        z.writestr('Stand.txt',head+'\nFür die automatisierte Reproduktion im Git-Checkout mit vollen Objekten: python scripts/familienrat_build.py\n')
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
