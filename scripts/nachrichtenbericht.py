"""Package the tested B build, its actual task bank and real browser evidence for Work."""
import hashlib
import json
from pathlib import Path
from figuren import IMAGES, PORTRAITS, print_sheet
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
    def quotes(ids):
        return [bank['laura'][n-1] for n in ids]
    text = ['# Materialübergabe · 08.12.2026','## Laura, 19',bank['lead'],
            *(' '.join(quotes(ids)) for ids in bank['lauraAbsaetze']),
            'Niveau · '+' · '.join(bank['levels']),'Zu zweit auf zwei Niveaus',
            'Pflichtnachrichten · Mutter und Freundin','Zusatznachrichten · Großmutter und Vater',
            '1. Argumenten-Check · 2. Nachricht prüfen']
    for person, case in bank['cases'].items():
        text.extend(['## Nachricht · '+person,*numbered(case['message'])])
        text.append('**Zuordnung zum Originalwortlaut**')
        for field in case['levels']['AHR'][0]['fields']:
            text.append(f"- {field['name']} · Zeile {field['line']} · {field['meaning']}")
            for option in field['options']:
                if option['correct'] and option['line']!=field['line']:
                    text.append(f"  - Auch Zeile {option['line']}: {option['feedback']}")
    text.append('## Fachkarten')
    for c in bank['cards'].values():
        text.append('### '+c['title'])
        if 'parts' in c:
            for title,ids in c['parts'].items():
                text.extend(['#### '+title,*numbered(c['lines'],ids)])
        else:
            text.extend(numbered(c['lines']))
        text.extend(f"- [{name}]({bank['sources'][name]})" for name in c['sources'])
    text.extend(['## Argumenten-Check',*(f'- **{label}** · {q}' for label,q in bank['categories'].items())])
    def hints(descriptions):
        for i,(title,body) in enumerate(zip(bank['helps'],descriptions,strict=True),1):
            text.append(f'- Hilfe {i} · **{title}** {body}')

    def answers(t):
        for opt in t['options']:
            start='Das passt. ' if opt['correct'] else 'Prüfe noch einmal. '
            text.append(f"- **{opt['label']}** — {start}{opt['feedback']}")

    for person,case in bank['cases'].items():
        for level,tasks in case['levels'].items():
            text.append(f'## {person} · {level}')
            for i,t in enumerate(tasks):
                if i<=1:text.append('### '+case['sections'][i])
                number=f'{i}. ' if i else ''
                text.extend(['#### '+number+t['heading'],t['prompt']])
                if t.get('lines'):
                    numbered_message=i in (0,2) or (person=='Freundin' and i==1)
                    passage=numbered(case['message'],t['lines']) if numbered_message else [case['message'][n-1] for n in t['lines']]
                    text.extend([person,*passage])
                if t.get('mother'):text.extend(['Zum Vergleich · Mutter',*numbered(bank['cases']['Mutter']['message'],t['mother'])])
                if t.get('wishes'):text.extend(['Lauras Worte',*quotes(t['wishes'])])
                if t.get('card'):
                    key,ids=t['card']
                if t.get('card') and t['kind']!='judgment':
                    text.extend([bank['cards'][key]['title'],*numbered(bank['cards'][key]['lines'],ids)])
                if t['kind']=='map':
                    for field in t['fields']:
                        text.extend(['**'+field['name']+'**',bank['categories'][field['name']]])
                        for opt in field['options']:
                            start='Das passt. ' if opt['correct'] else 'Prüfe noch einmal. '
                            text.append(f"- Zeile {opt['line']} — {start}{opt['feedback']}")
                        hints(field['hints'])
                elif t['kind']=='judgment':
                    text.extend([ui['evidence']+' · '+bank['cards'][key]['title'],*(bank['cards'][key]['lines'][n-1] for n in ids),
                                 ui['goal'],*quotes(t['goals']),ui['rating'],*t['options']])
                    text.extend([ui['explain'],'Einzelarbeit: '+ui['solo']])
                    if level=='Förder':text.extend([ui['reason'],*t['links']])
                    if 'extension' in t:
                        text.extend(['**'+level+' · Weiterdenken**',t['extension']['prompt']])
                    text.extend([ui['spoken'],ui['paper'],ui['own'],ui['write']])
                    if level!='Förder':text.extend(['Grund selbst prüfen',t['selfCheck']])
                    text.extend([ui['done'],ui['missing'],'Viel, zum Teil und wenig sind mit einer Begründung möglich.'])
                    hints(t['hints'])
                    if 'extension' in t:
                        text.append('**'+level+' · Weiterdenken innerhalb der geöffneten Hilfe**')
                        hints(t['extension']['hints'])
                else:
                    answers(t)
                    hints(t['hints'])
                    if 'depth' in t:
                        depth=t['depth']
                        text.extend(['**'+level+' · Weiterdenken**',depth['prompt']])
                        more=[n for n in depth['lines'] if n not in t['lines']]
                        if more:text.extend(numbered(case['message'],more))
                        answers(depth)
                        hints(depth['hints'])
    text.extend(['## Gemischte Paare und Wiedereinstieg',
                 'Beide bearbeiten dieselben nummerierten Teilfragen. Der Auftrag vor den Auswahlen gilt für alle. Bei Förder/AHR kommen die freiwilligen Förder-Bausteine und unter „AHR · Weiterdenken“ die veränderte Voraussetzung hinzu. ESA/MSA erhält nach dem gemeinsamen Auftrag die MSA-Frage nach Nutzen und Grenze. Die Vertiefung gehört zum höheren Niveau. Die fünf Hilfen zur Vertiefung stehen in der jeweils geöffneten Hilfe unter „Weiterdenken“.',
                 'Hier kannst du weiterarbeiten.', 'Schau auf deinen Lernbogen. Wähle dein Niveau, die Person und deine letzte Frage.',
                 'Nach Neustart → Niveau wählen (für ein Paar auch das zweite Niveau) → Person → Abschnitt 2 → 1. Stimmt das? / 2. Was möchte Laura? Geht die Nachricht darauf ein? / 3. Hilft die Nachricht Laura? Warum?'])
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
    assert len(photos)==44
    for engine in ('chromium','webkit'):
        for view in ('Tagesauswahl','Posteingang-iPad','Übersicht-390','Pflichtkarte','Absender','Wiedereinstieg'):
            assert f'{engine}-{view}.jpg' in r['bilder']
        for state in ('Aufgabe','Fehlversuch'):
            assert f'{engine}-Quellenprüfung-{state}.jpg' in r['bilder']
    assert {(v['browser'],tuple(v['niveaus'])) for v in r['paar_neustart'] if v['teilfrage']==3}=={
        (e,p) for e in ('chromium','webkit') for p in [('Förder','AHR'),('ESA','MSA')]}
    body=(ROOT/'docs/Nachrichten-08-12.md').read_text()
    routes=r['grundwege']
    labels=[[l] for l in bank['levels']]+[['Förder','AHR'],['ESA','MSA']]
    assert sorted((x['browser'],x['niveaus']) for x in routes)==sorted((e,l) for e in ['chromium','webkit'] for l in labels)
    summary=['## Technische Abnahme',
             f"Referenz: `{r['referenz']}`. Geprüfter Commit: `{r['commit']}`. Version A und das erste Modul sind bytegleich mit dem Referenzbau. In der B-Startseite unterscheidet sich außerhalb des zweiten Moduls ausschließlich die Bilddatei der zweiten Tageskarte. Die SCORM-Startdatei entspricht der jeweiligen Offline-Datei.",
             f"{len(runs)} vollständige Einzelwege in Chromium und WebKit. Geprüft wurden alle Zuordnungen und Hilfeziele, falsche und richtige Teilantworten, drei Gesamturteile und der Neustart zu jeder einzelnen Teilfrage. Nach dem Neuladen ließ sich das Urteil bei allen 32 Einzelwegen direkt mit dem sichtbaren Beispiel aus Hilfe 5 abschließen. Vier zusätzliche Paarprüfungen führten nach dem Neuladen direkt zu Freundin 2, Frage 3. Dabei wurden die Materialien aufgerufen und das Niveau mit einer bereits gewählten Fachstelle gewechselt. Der Test-LMS empfing nur Sitzungsbeginn und -ende. Portrait und Querformat: 820 × 1180 und 1180 × 820 CSS-Pixel mit 100 oder 150 Prozent Schrift. Der Zusatztest nutzt 390 × 650 und 200 Prozent.",
             '## Umfang der Pflichtstrecke',
             'Jede Zeile beruht auf zwei tatsächlichen Durchläufen. Die Tabelle zeigt den Chromium-Wert, bei Abweichung zusätzlich den WebKit-Wert. Ausgangspunkt ist die Tagesauswahl, Endpunkt die fertige Begründung zur Freundin. Gezählt wurde ein fehlerfreier Weg mit mündlicher Bestätigung ohne freiwillige Hilfen und Begründungsbausteine. Die fachlichen Auswahlen zählen alle verlangten Zuordnungen, Antworten, Fachstellen, Laura-Aussagen und persönlichen Einschätzungen. Sie sind bereits in den Bedienhandlungen enthalten. Eine Zeilenauswahl zählt als eine Bedienhandlung. Das Öffnen und Bestätigen nativer Menüs, Scrollen, Lesezeit und Gesprächsdauer hängen vom Gerät und den Lernenden ab.',
             '| Niveau am Gerät | Aufgabenbildschirme | Ansichtswechsel | Schaltflächen | Auswahlmenüs | Fachliche Auswahlen | Angezeigte Wortvorkommen auf den acht Aufgaben |',
             '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for levels in labels:
        rows=[x for x in routes if x['niveaus']==levels]
        def cell(values):
            return ' / '.join(str(v) for v in dict.fromkeys(values))
        cells=[cell(x[k] for x in rows) for k in ('aufgaben','wechsel')]
        cells.extend(cell(x['bedienhandlungen'][k] for x in rows) for k in ('button','auswahl'))
        cells.extend(cell(x[k] for x in rows) for k in ('fachliche_auswahlen','wortvorkommen'))
        summary.append('| '+' + '.join(levels)+' | '+' | '.join(cells)+' |')
    summary+=['','Die Textmessung zählt sichtbare Passagen einschließlich wiederkehrender Oberfläche, Quelltexten, Alternativen, ausgewählten Zeilen und eingeblendeten Rückmeldungen je Aufgabenbildschirm. Bei mehreren Zuständen einer Aufgabe wird dieselbe Passage höchstens so oft gezählt, wie sie gleichzeitig vorkommt. Geschlossene Hilfen, Menüs und der freie mündliche Grund zählen nicht mit. Die Aufschlüsselung pro Frage steht im JSON-Protokoll. Die Wortzahl beschreibt das Textangebot, keine individuell gelesene Menge.',
              '','| Geprüfte Datei | SHA-256 |','| --- | --- |']
    for key,name in [('html_sha256','Fallakte.html · B'),('scorm_sha256','Fallakte-SCORM12.zip · B'),('bank_sha256','Aufgabenbank.json'),('version_a_sha256','Fallakte.html · A')]:
        summary.append(f'| {name} | `{r[key]}` |')
    report=DIST/'Nachrichten-Pruefbericht.md'
    detail=OUT/'Pruefdetails.md'
    detail.write_text(body+'\n'+'\n'.join(s+'\n' if not s.startswith('|') else s for s in summary)+'\n')
    readable=OUT/'Materialbank.md'
    readable.write_text(material(bank))
    small=[x for x in r['ansichten'] if x['viewport'][0]==390]
    report.write_text('\n\n'.join([
        '# Abnahme · Fallakte vom 08.12.2026',
        f"Geprüfter Commit `{r['commit']}`. Vergleich mit `{r['referenz']}`.",
        'Laura, 19, schreibt in drei direkt sichtbaren Absätzen. Die vier ursprünglichen Familiennachrichten, Fachkarten, Aufgaben, Antwortkontrollen und fünf Hilfen stimmen mit der geprüften Aufgabenbank überein. Die Zitate zu Ausbildung, Informationen und Selbstbestimmung wurden auf ihre neuen Wortlaute geprüft.',
        'Pflichtpersonen und Zusatzpersonen haben direkte Zugänge zu beiden Abschnitten. Die vier Porträts sind Ausschnitte des neuen Gruppenbilds. Die Abnahme vergleicht die Bildpixel und prüft die Bilddateien in Übersicht, Absender und Wiedereinstieg. Lauras Einzelporträt und die gesamte Offline-Datei A sind bytegleich mit der Referenz. Alle Dateien innerhalb des SCORM-Pakets A wurden byteweise verglichen.',
        f"Chromium und WebKit bestanden {len(runs)} Einzelwege, {len(routes)} Pflichtwege einschließlich gemischter Paare und vier Paar-Wiedereinstiege zu Freundin 2, Frage 3. Die Pflichtstrecke hat acht Aufgabenbildschirme, elf Ansichtswechsel und je nach Niveau oder Paar 31 bis 36 Bedienhandlungen. Die HTML-Datei ist identisch mit der SCORM-Startdatei.",
        'Die Messung vergleicht Übersicht, acht Abschnittseinstiege, alle weiteren Teilfragen und den Wiedereinstieg mit dem Referenzbau. Bei 390 × 650 Pixeln änderte sich der vertikale Scrollbereich der Übersicht wie folgt. '+', '.join(f"{v['browser'].capitalize()} von {v['vorher']['Übersicht']['seite']} auf {v['aktuell']['Übersicht']['seite']} CSS-Pixel" for v in small)+'. Auf beiden iPad-Formaten sind alle vier Personenkarten bei Standardschrift ohne Scrollen erreichbar.',
        'Offen für die Unterrichtserprobung bleiben die Verständlichkeit für Förder- und ESA-Lernende, die tatsächliche Arbeitszeit sowie der Test auf einem Schul-iPad im itslearning-Kurs. Dafür den Pflichtweg zu zweit beginnen und nach Neuladen über den Lernbogen direkt zu Freundin 2, Frage 3 zurückkehren.'
    ])+'\n')
    sheet=DIST/'Figurenuebersicht-08-12.pdf'
    print_sheet(sheet)
    evidence=[(report,report.name),(detail,detail.name),(log,'Protokolle/'+log.name),(legacy,'Protokolle/'+legacy.name),*photos]
    package(DIST/'Nachrichten-Sichtpruefung.zip',evidence)
    package(DIST/'Materialuebergabe-Work.zip',[(data,data.name),(readable,readable.name),
            (sheet,sheet.name),(OUT/'Fallakte.html','Schueleransicht-08-12.html'),
            *((p,'Figuren/'+p.name) for p in [*PORTRAITS.values(),IMAGES/'laura-umfeld.webp']),*evidence])
    print(len(runs),'Browserwege,',len(photos),'Bildschirmfotos. Alle Übergabedateien geprüft.')


if __name__=='__main__':main()
