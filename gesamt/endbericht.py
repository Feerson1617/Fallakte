"""Prüfschranke für die endgültige Übergabe und die vier identischen Programmstände."""
from zipfile import ZipFile
from lxml import html
from auslieferung import OUT,QA,ROOT,VERSIONS,json_text,pack,sha
from endvertrag import read
from endvergleich import REFERENZ
import json

def write():
    commit=html.parse(str(OUT/'Fallakte-Gesamt.html')).xpath('string(//meta[@name="revision"]/@content)')
    scope=read('Endumfang')
    checks,cards,classes=[read(k) for k in ('Browserpruefung','Kartenpruefung','Unterrichtspruefung')]
    assert all(r['commit']==commit for r in (scope,checks,cards,classes))
    assert len(checks['wege'])==32 and len(checks['sitzungen'])==16
    assert len(cards['karten'])==16 and sum(len(x['felder']) for x in cards['karten'])==64
    assert len(classes['wege'])==8 and len(read('Empfehlungen'))==140
    assert len(read('Layoutstichprobe'))==42 and not any(x['befunde'] for x in read('Layoutstichprobe'))
    assert len(read('Work-Gegenprobe'))==112 and len(read('Pflichtbogenabgleich')['seiten'])==6
    assert len(read('Weitere-Papieransichten'))>50
    additional=json.loads((ROOT/'build/vertiefungen/Vertiefungspruefung.json').read_text())
    assert len(additional)==8
    paired=sum(read('Paarvergleich-'+m)['zustaende'] for m in ('PREP','UB02','UB08','Zusatz'))
    for e in ('chromium','webkit'):
        regular=read('Familienwege-verlauf-'+e)['wege'];state=read('Familienwege-tandem-'+e)
        assert len(regular)==8 and all(len(x['niveaus'])==1 for x in regular)
        assert len({(x['wahl'],tuple(x['fragen'])) for x in state['pruefungen'] if 'wahl' in x})==8
        assert len(state['quellenarbeit'])>=10
    for v in VERSIONS:
        base='Fallakte-'+v
        with ZipFile(OUT/(base+'-SCORM12.zip')) as z:
            assert z.testzip() is None and z.read('index.html')==(OUT/(base+'.html')).read_bytes()
    sight={p.name:p.read_bytes() for p in QA.glob('*.json') if p.stem in {
        'Module','Modulquellen','Endumfang','Empfehlungen','Layoutstichprobe','Paarvergleich-PREP','Paarvergleich-UB02',
        'Paarvergleich-UB08','Paarvergleich-Zusatz','Endvergleich','Kartenpruefung','Browserpruefung','Unterrichtspruefung',
        'Reproduzierbarer-Bau','Zusatzfall-Bestand','Work-Gegenprobe','Weitere-Papieransichten','Bildtexte','Pflichtbogenabgleich','Hilfenvergleich'} or p.name.startswith('Familienwege-')}
    for n in ('Start-Gesamt','Work-LA-eigen','Work-LA-offen','Work-LA-abschluss','Work-MU-erst','Work-FR-ergebnis','Work-GM-erst','Work-VA-ergebnis',
              'Work-Schlussrat-Stopp','Musterkarte-ESA','chromium-MSA-Fachcheck'):
        sight[n+'.jpg']=(QA/(n+'.jpg')).read_bytes()
    for name in ('webkit-Tom-Quelle.jpg','chromium-Celina-Schluss.jpg'):
        sight[name]=(ROOT/'build/vertiefungen'/name).read_bytes()
    sight['Druckvergleich-Foerder-4.jpg']=(QA/'Druckvergleich-Foerder-4.jpg').read_bytes()
    sight['Vertiefungspruefung.json']=json_text(additional).encode()
    zweiter=''
    if (QA/'Reproduzierbarer-Bau.json').exists():
        belege=read('Reproduzierbarer-Bau')
        assert belege['commit']==commit and len(belege['dateien'])==8
        assert all(sha((OUT/r['name']).read_bytes())==r['sha256'] for r in belege['dateien'])
        zweiter=' Ein zweiter Bau aus einem eigenen Checkout ergab bei allen acht Dateien dieselbe SHA-256-Prüfsumme.'
    zusatz=''
    if (QA/'Zusatzfall-Bestand.json').exists():
        z=read('Zusatzfall-Bestand')
        assert z['software']==commit and z['sha256_0212']==read('Module')['02']
        zusatz=' Die separaten Langtests liefen auf dem identischen Modul vom 02.12. unter '+z['teststand'][:7]+'. Der Wortlautvergleich mit identischen Bedienwegen lief auch auf der Endfassung.'
    zahl=lambda n:format(n,',').replace(',','.')
    report=f"""# Fallakte · Softwareübergabe an Work

Softwarecommit `{commit}`. Geprüfter Ausgangsstand `{REFERENZ}`.

## Änderungen für den Unterricht

- Die sichtbaren Aufträge, Chatbeiträge und Rückkehrhinweise sprechen eine Person an. Im Familienrat gibt es eine Niveauwahl und einen persönlichen Prüfstand. Wer das Niveau während der Bearbeitung ändert, kann die Änderung abbrechen und den bisherigen Weg fortsetzen.
- In der Vorbereitung benennen Lesetipps und Anwendungsfragen den untersuchten Vorgang. Die Papierhinweise unterscheiden Kartenblatt und Laufzettel und benennen den Rückkehrknopf. Der Abschluss beschreibt den einen Schnitt für zwei doppelseitige Karten.
- Am 02.12. prüfen die Fragen, was die gewählte Methode für Lauras jeweiliges Anliegen leisten kann. Der Schlussrat ist nummeriert. Rückfragen, Papierwege und Chatbeiträge in den freiwilligen Fällen Tom und Celina wurden ebenfalls durchgesehen.
- Am 08.12. unterscheiden Mutter und Freundin die erste von der fachlich geprüften Faktwahl. Großmutter fragt nach einem Wert, Vater nach einer allgemeinen Regel. Die Seite für Lauras persönliche Antwort entspricht den unterschiedlichen Feldern im Förder- und im ESA-Bogen. LA-03 trennt Frage, biologischen Fakt und Grenze seiner Aussage.

## Ergebnisse

- Alle drei Module, alle vier Niveaus und die freiwilligen Fälle wurden in den gebauten Ausgaben geprüft. In der Vorbereitung liefen 32 vollständige Wege in Chromium und WebKit durch Offline-HTML und SCORM-Testhost. Alle 16 Musterkarten mit 64 Einträgen stimmen mit den Druckvorlagen überein.
- Für den 02.12. wurden fünf Abschnitte mit sieben Methodenentscheidungen auf vier Niveaus geprüft (140 Kombinationen). Die Abschlussansicht lässt sich beim Stopp über den Lehrkraftzugang ohne Prüfcode öffnen. Die erste und die zweite Abstimmung bleiben Unterrichtshandlungen der Lehrkraft. Tom und Celina wurden auf allen vier Niveaus in beiden Browsern bearbeitet.{zusatz}
- Im Familienrat wurde jeder der vier persönlichen Lernwege in beiden Browsern mit und ohne Fehler bzw. angeforderte Hilfe durchlaufen. Zusätzliche Prüfungen umfassten acht Kombinationen aus Nachricht(en) und Frage(n), eigene fachübergreifende Begründungen, die fünf Hilfen, Unterbrechung, erneute Auswahl und Neustart. Die Antwort über die persönliche Gewichtung bleibt fachlich offen. Die selbstständige Nutzung einer Fachkarte gilt weiterhin als Quellenarbeit.
- In LA-04 zeigt der direkte Einstieg die noch offene Prüfung und den Rückweg nach LA-03. Nach der persönlichen Prüfung führt LA-04 zum Feld „Festhalten“. Die 112 Bildschirmbelege erfassen alle Niveaus in Chromium und WebKit. Für Förder und ESA wurden außerdem die sechs Originalseiten der Pflichtbögen verglichen.
- Die 42 Layoutstichproben bei 150 Prozent Schriftgröße in beiden Browsern zeigten keine Befunde. Offline-Datei und Startdokument im jeweiligen SCORM-ZIP sind bytegleich. Während der SCORM-Prüfungen wurden im Testhost nur Initialisierung und Beendigung registriert.{zweiter}
- {zahl(paired)} vor und nach der Überarbeitung mit gleichen Bedienhandlungen erfasste Zustände belegen den Verlauf der weiter unterstützten Lernwege. Der Textvertrag umfasst {zahl(scope['ansichten'])} unterschiedliche gerenderte Ansichten und {scope['papierwege']} Papierübergänge. Das Quellinventar ordnet {zahl(scope['quellen'])} Fundstellen ihrem Verwendungszweck zu. Die bisherigen 3.571 offenen Fundstellen sind einzeln auf das neue Inventar bzw. die entfallene Personenwahl und Selbstauskunft zurückgeführt.

## Grenzen und Praxistest

Die Browser liefen mit simulierten Touchfenstern. Ein echtes Schul-iPad, der lokale PDF-Ausdruck nach dem Neusatz, ein Import in das produktive itslearning und ein Verständlichkeitstest mit realen Förder- und ESA-Lernenden stehen aus. Die Sprachprüfung und die Browserprotokolle sind eine redaktionelle Softwareabnahme. Freie Begründungen in den Tests sind Simulationen.

Für den Praxistest das zur Stunde passende ZIP in itslearning importieren, auf einem Schul-iPad im Hoch- und Querformat öffnen und die Verbindung anschließend für den Offline-Test trennen. Am 02.12. die Sicherung während eines offenen Falls aufrufen. Am 08.12. nach dem Neuladen direkt LA-04 öffnen, über LA-03 die Auswahl prüfen und anschließend die ergänzende Notiz mit dem Feld auf Seite 4 vergleichen. Die PDF-Referenzen und die zuvor geprüfte Rückfallversion wurden separat aufbewahrt.
"""
    (OUT/'Pruefbericht.md').write_text(report)
    sight['Pruefbericht.md']=(OUT/'Pruefbericht.md').read_bytes()
    pack(OUT/'Fallakte-Sichtpruefung.zip',sight)
    files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name not in ('SHA256SUMS','Buildnachweis.json'))
    result={p.name:dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files}
    (OUT/'Buildnachweis.json').write_text(json_text(dict(softwarecommit=commit,basis=REFERENZ,dateien=result)))
    (OUT/'SHA256SUMS').write_text(''.join(sha(p.read_bytes())+'  '+p.name+'\n' for p in [*files,OUT/'Buildnachweis.json']))
if __name__=='__main__':write()
