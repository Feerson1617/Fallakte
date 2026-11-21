"""Package the tested B build, its actual task bank and real browser evidence for Work."""
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'build/08-12'
QA = OUT/'Abnahme'
DIST = ROOT/'dist'


def sha(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def numbered(lines, numbers=None):
    return [f'**Zeile {number}** · {lines[number-1]}' for number in (numbers or range(1,len(lines)+1))]


def material(bank):
    ui = bank['verdictUI']
    text = ['# Materialübergabe · 08.12.2026',bank['lead'],bank['context'],'## Lauras Nachricht',*numbered(bank['laura'])]
    for person, case in bank['cases'].items():
        text.extend(['## Nachricht · '+person,*numbered(case['message'])])
    text.append('## Fachkarten')
    for c in bank['cards'].values():
        text.extend(['### '+c['title'],*numbered(c['lines'])])
        text.extend(f"- [{name}]({bank['sources'][name]})" for name in c['sources'])
    text.extend(['## Argumenten-Check',*(f'- **{label}** · {q}' for label,q in bank['categories'].items())])
    for person,case in bank['cases'].items():
        for level,tasks in case['levels'].items():
            text.append(f'## {person} · {level}')
            for i,t in enumerate(tasks):
                if i<=1:text.append('### '+case['sections'][i])
                text.extend(['#### '+t['heading'],t['prompt']])
                if t.get('lines'):
                    text.extend([person,*numbered(case['message'],t['lines'])])
                if t.get('wishes'):
                    text.extend(['Lauras Worte',*numbered(bank['laura'],t['wishes'])])
                if t.get('card'):
                    key,ids=t['card']
                    card=bank['cards'][key]
                    text.extend([card['title'],*numbered(card['lines'],ids)])
                if t['kind']=='judgment':
                    text.extend(['**Geprüft**',*t['results'],ui['rating'],*t['options'],
                                 ui['simpleEvidence'] if level=='Förder' else ui['evidence'],*t['anchors']])
                    if level=='Förder':
                        text.extend([ui['reason'],*t['links'],ui['own'],ui['write'],ui['oral'],ui['spoken']])
                        for a,ids in enumerate(t['matchingLinks']):
                            text.append(t['anchors'][a]+' → '+' / '.join(t['links'][x] for x in ids))
                        if any(len(v)<len(t['links']) for v in t['matchingLinks']):
                            text.append('Rückfrage bei anderem Baustein: '+ui['reconnect'])
                    else:
                        if t['counter']:text.append(t['counter'])
                        text.extend([ui['write'],ui['oral'],ui['spoken']])
                    text.extend([ui['done'],ui['reflect'],'Alle drei Urteile stehen offen. Eine Musterantwort folgt bei Hilfe 5.'])
                else:
                    for opt in t['options']:
                        start='Das passt. ' if opt['correct'] else 'Prüfe noch einmal. '
                        text.append(f"- **{opt['label']}** — {start}{opt['feedback']}")
                for h,(title,body) in enumerate(zip(bank['helps'],t['hints'],strict=True),1):
                    text.append(f'- Hilfe {h} · **{title}** {body}')
    return '\n\n'.join(text)+'\n'


def package(path, entries):
    with ZipFile(path,'w',ZIP_DEFLATED) as z:
        for file,name in entries:z.write(file,name)
    with ZipFile(path) as z:
        assert z.testzip() is None
        assert {name for _,name in entries}==set(z.namelist())
        for file,name in entries:assert z.read(name)==file.read_bytes()


def main():
    log=QA/'Nachrichten.json'
    r=json.loads(log.read_text())
    data=OUT/'Aufgabenbank.json'
    bank=json.loads(data.read_text())
    legacy=ROOT/'build/tagesauswahl/Tagesauswahl.json'
    shared=json.loads(legacy.read_text())
    assert r['html_sha256']==sha(DIST/'Version-B/Fallakte.html')==shared['pakete']['B']['Fallakte.html']
    assert r['scorm_sha256']==sha(DIST/'Version-B/Fallakte-SCORM12.zip')==shared['pakete']['B']['Fallakte-SCORM12.zip']
    assert r['version_a_sha256']==sha(DIST/'Version-A/Fallakte.html') and r['bank_sha256']==sha(data)
    runs=r['durchlaeufe']
    assert len(runs)==32 and {(v['browser'],v['person'],v['niveau']) for v in runs}=={
        (e,p,l) for e in ('chromium','webkit') for p in bank['cases'] for l in bank['levels']}
    assert all(v['hilfen_je_aufgabe']==5 and len(v['urteile'])==3 and not v['skriptfehler'] and not v['externe_anfragen'] for v in runs)
    assert {x['browser'] for x in r['kleinfenster'] if x['schrift_prozent']==200 and x['abschnitte']==8}=={'chromium','webkit'}
    photos=[(QA/name,'Bildschirmfotos/'+name) for name in r['bilder']]
    assert all(r['bilder'][file.name]==sha(file) for file,_ in photos)
    assert len(photos)==20
    body=(ROOT/'docs/Nachrichten-08-12.md').read_text()
    summary = ['## Technische Abnahme',f"Geprüfter Ausgangsstand: `{r['referenz']}`. Der Referenzbau vergleicht Version A vollständig sowie Version B außerhalb des zweiten Moduldokuments byteweise. Die vorhandenen Prüfungen für den 02.12. liefen am eingebetteten Programmstand. Die Dateiinhalte von Offline-HTML und SCORM-Startdatei stimmen überein.",
               f"{len(runs)} vollständige Wege in Chromium und WebKit decken alle vier Personen und Niveaus ab. Getestet wurden richtige und falsche Textantworten, alle fünf Hilfen, Abschluss nach Hilfe 5 und alle drei Urteile. Die Tests öffnen Karten, wechseln die Ansicht und steigen nach vollständigem Neuladen in beide Abschnitte ein. Die Protokolle nennen Browserstand, Touch-Viewport, Schrift und Format für jeden Weg.",
               'iPad-Ansichten: 820 × 1180 und 1180 × 820 CSS-Pixel bei 100 oder 150 Prozent Schrift im Modul. Der separate lokale Einstieg wurde bei 390 × 650 und 200 Prozent Schrift mit allen acht Abschnitten und geöffneter Hilfe geprüft. Die Offline-Prüfung blockiert externe Verbindungen. Das SCORM-Testsystem protokolliert Sitzungsbeginn und Sitzungsende. Schülerantworten werden im Arbeitsspeicher gehalten. Das LMS kann Zugriffe separat protokollieren.',
               '| Niveau | Aufgaben Mutter | Aufgaben Freundin | davon eigene Urteile |','| --- | ---: | ---: | ---: |']
    for level in bank['levels']:
        summary.append('| '+level+' | '+' | '.join(str(len(bank['cases'][p]['levels'][level])) for p in ('Mutter','Freundin'))+' | 2 |')
    summary+=['','Die Zahlen erfassen Aufgabenbildschirme einschließlich beider Urteile. Sie messen keine Lernzeit.','',
              '| Geprüfte Datei | SHA-256 |','| --- | --- |']
    for key,name in [('html_sha256','Fallakte.html · B'),('scorm_sha256','Fallakte-SCORM12.zip · B'),('bank_sha256','Aufgabenbank.json'),('version_a_sha256','Fallakte.html · A')]:
        summary.append(f'| {name} | `{r[key]}` |')
    report=DIST/'Nachrichten-Pruefbericht.md'
    report.write_text(body+'\n'+'\n'.join(s+'\n' if not s.startswith('|') else s for s in summary)+'\n')
    readable=OUT/'Materialbank.md'
    readable.write_text(material(bank))
    evidence=[(report,report.name),(log,'Protokolle/'+log.name),(legacy,'Protokolle/'+legacy.name),*photos]
    package(DIST/'Nachrichten-Sichtpruefung.zip',evidence)
    package(DIST/'Materialuebergabe-Work.zip',[(data,data.name),(readable,readable.name),*evidence])
    print(len(runs),'Browserwege,',len(photos),'Bildschirmfotos. Alle Übergabedateien geprüft.')


if __name__=='__main__':main()
