"""Prüfkandidat mit Prüfsummen. Offene Einzelprüfungen schließen die Materialfreigabe aus."""
import json
from collections import Counter
from zipfile import ZipFile
from lxml import html
from auslieferung import OUT,QA,sha,json_text,pack,ROOT
from sprachpruefung import BASE

def read(name):return json.loads((QA/(name+'.json')).read_text())
def write():
    head=html.parse(str(OUT/'Fallakte-Gesamt.html')).xpath('string(//meta[@name="revision"]/@content)')
    checks=read('Browserpruefung');cards=read('Kartenpruefung');ub=read('Unterrichtspruefung')
    scope=read('Sprachumfang');compare=read('Bestandsvergleich');work=read('Work-Gegenprobe')
    assert checks['commit']==cards['commit']==ub['commit']==compare['commit']==head
    herkunft=read('Pruefherkunft') if (QA/'Pruefherkunft.json').exists() else None
    assert len(work)==72 and len(read('Empfehlungen'))==140 and len(read('Pflichtbogenabgleich')['seiten'])==6
    assert len(cards['karten'])==16 and sum(len(r['felder']) for r in cards['karten'])==64
    assert len(checks['wege'])==32 and len(checks['sitzungen'])==16
    family={};tandem={}
    for engine in ('chromium','webkit'):
        family[engine]=read('Familienwege-verlauf-'+engine)['wege'];assert len(family[engine])==12
        tandem[engine]=read('Familienwege-tandem-'+engine)
        assert len({tuple(r['team']) for r in tandem[engine]['pruefungen'] if isinstance(r.get('team'),list)})==16
    reserve=json.loads((ROOT/'build/vertiefungen/Vertiefungspruefung.json').read_text());assert len(reserve)==8
    layout=read('Layoutstichprobe')
    issues=Counter(i[0] for r in layout for i in r['befunde'])
    report=f"""# Prüfstand der Sprachfassung

Softwarecommit `{head}`. Referenz `{BASE}`. Diese Ausgabe ist ein Prüfkandidat. Für den 26.11. liegt die bereits geprüfte Vorbereitung weiter separat vor.

## Änderungen für die Lernenden

In der Vorbereitung nennen die Aufträge die Felder auf der Infokarte. Die MSA- und AHR-Frage gehört auf den Laufzettel. Nach dem B-Vergleich folgt dort „Karte kontrolliert“ und anschließend „Weiter im Chat“. Die Schlussansicht beschreibt den einen Schnitt durch das Duplexblatt. Die Rückmeldungen auf die 135 Fehloptionen der regulären Fachfragen einschließlich Pearl-Index und der acht Papierfragen erklären den jeweiligen Unterschied. Bei einer falschen Antwort zur Hormonfreiheit und zu Regelschmerzen erklärt der Papiercheck jetzt die mögliche Veränderung der Schmerzen. In der Anwendung 3A auf MSA und AHR fragt der Text ausdrücklich nach der nicht untersuchten Schutzwirkung. Damit lässt sich die Frage von der Einordnung der Spermien als Zellen unterscheiden. Hilfen führen vom konkreten Lesetipp zur Lösung und der zusätzlichen Anwendung.

In der Beratung mit Laura beziehen sich die Aufträge auf die biologische Wirkung und Lauras aktuellen Wunsch. Der persönliche Schlussrat kommt einmal auf den Laufzettel. Beim Stopp kann die Lehrkraft unmittelbar zur Sicherung wechseln. Die beiden Abstimmungen mit dem Empfehlungsrad stehen im Lehrkrafthinweis. Nach Laura sind Tom und Celina beide anwählbar.

Im Familienrat setzen Förder- und ESA-Lernende das erste Kreuz links und das geprüfte Kreuz rechts. Das erste bleibt lesbar. Im Förderauftrag auf Seite 4 können sie eine oder beide Fragen und Nachrichten wählen. Sie ordnen M oder F dem Fakt zu und erklären ihre Wahl. Unter „Festhalten“ bleibt die erste Antwort erhalten. Persönliche Begründungen werden im Unterricht besprochen.

## Ausgeführte Prüfungen

- Vier Offline-HTMLs und vier SCORM-1.2-Pakete mit gestaffelten Dateninhalten. 16 Kombinationen aus Auslieferung, Freigabestufe und Browser. Das entpackte Startdokument stimmt jeweils byteweise mit der entsprechenden HTML-Datei überein. Die Manifeste wurden gegen das Schema validiert.
- 32 Vorbereitungsdurchläufe, vier Niveaus, 68 reguläre Fragen, acht Papierfragen. Der Browser prüfte Fehlversuche, fünf Hilfen, Anwendungen nach der Lösung und alle vier Wege zur Musterkarte. 16 Vollkarten und 64 Einträge stimmen mit den Druckkarten überein.
- Je acht vollständige Laura- und Familienratswege in der gemeinsamen Fassung. Zusätzlich 140 Kombinationen aus Lauras fünf Abschnitten, vier Niveaus und sieben Empfehlungen in Chromium. Tom und Celina wurden in beiden Engines auf vier Niveaus geöffnet, beraten und über ihre Abschnittsauswahl wieder aufgenommen.
- Im Familienrat zusätzlich {sum(map(len,family.values()))} Wege einschließlich gemischter Teams. In jeder Engine wurden alle 16 Paarungen der vier Niveaus geprüft. Die Zustandsprotokolle erfassen Fehler, späte Hilfen, Anwendungen, Direkteinstieg, Abbruch und Wiederaufnahme. Der Work-Vergleich umfasst {len(work)} Vorher-/Nachher-Einträge zu sechs Übergaben und vier Teamkonstellationen. Zwei Original-PDFs wurden auf je drei Seiten verglichen.
- Die Browserprüfungen überwachten Netzwerkzugriffe, Cookies und Schreibzugriffe. Der Testhost erhielt nur SCORM-Sitzungsbeginn und -ende. Alle Texte der Prüfsitzungen stammen aus simulierten Lernwegen.
- {len(layout)} Layoutansichten in Chromium und WebKit bei 150 % Grundschrift. Befunde in den gemessenen Ansichten: {dict(issues) if issues else 'keine'}. Layoutstichprobe.json führt die betroffenen Bedienelemente auf. Die Kontrastmessung erfasst deckende Flächen mit auswertbarer Hintergrundfarbe.

## Umfang der Textprüfung

{scope['fundstellen_alt']} Fundstellen im Ausgangsinventar, {scope['fundstellen_export']} statische Fundstellen im Export und {scope['beobachtungen']} protokollierte Bildschirmzustände. Zusätzlich sind {scope['paarweise']} Vorher-/Nachher-Vergleiche nach derselben Bedienhandlung enthalten. Dieselbe Ansicht kann in mehreren Prüfwegen vorkommen. Die {scope['medienwechsel']} Zeilen der Medienwechselmatrix benennen Papierort, Handlung, Rückkehr und Zielzustand.

| Bereich | Fundstellen im Export | Geändert oder neu | Gleicher Wortlaut | Einzelprüfung offen |
|---|---:|---:|---:|---:|
"""
    for m,r in scope['nach_modul'].items():
        report+=f"| {m} | {r['fundstellen']} | {r['geaendert']} | {r['fundstellen']-r['geaendert']} | {r['offen']} |\n"
    report+=f"""
Für {scope['lernwegbelege']} Fundstellen gibt es einen direkten Verweis auf den Wortlaut in einem passenden aufgezeichneten Vorher-/Nachher-Lernweg. Umfang.csv enthält die Aufteilung nach Niveau, Texttyp und Prüfstatus. Fundstellen.csv unterscheidet Quellenvergleich, geschützte Werte, Beobachtung des Wortlauts und Prüfung der konkreten Verwendung. Die Laufzeitvergleiche stellen die konkreten alten und neuen Texte nach derselben Eingabe gegenüber. Work-Bildschirmvergleich.csv dokumentiert die Papieraufträge gesondert. Für zusätzliche Zustandskombinationen außerhalb der protokollierten Wege liegt kein paarweiser Nachweis vor.

## Grenze der Abnahme

Die sprachliche Einzelabnahme aller verbleibenden Fundstellen, aller zusammengesetzten Texte und ihrer kontextgleichen Verwendung steht aus. Die Medienwechselmatrix ist bis dahin eine Prüffassung für Work. Die Unterrichts-PDFs wurden in dieser Runde ausschließlich als Referenz gelesen.

Für den Praxistest den Kandidaten auf einem Schul-iPad offline öffnen und als separate Testressource in itslearning importieren. Im Hoch- und Querformat eine Papieraufgabe bearbeiten, die App neu laden und mit dem markierten Abschnitt weiterarbeiten. Mit Förder- und ESA-Lernenden prüfen, ob sie Papierfeld, Schreibhandlung und Rückkehrknopf selbst finden. Die Bearbeitungszeit und der von der Lehrkraft angeleitete Wechsel in Minute 23 wurden im Klassenraum noch nicht erprobt.
"""
    if herkunft:
        report+=f"\nDie Detailprotokolle für UB02 und UB08 aus dem Prüflauf `{herkunft['quelle']}` wurden anhand der SHA-256-Werte der tatsächlich eingebetteten Module übernommen. Pruefherkunft.json nennt die betroffenen Dateien. Paketprüfung und Gesamtlernwege liefen auf dem oben genannten Softwarecommit.\n"
    (OUT/'Pruefbericht.md').write_text(report)
    proof={p+'.json':(QA/(p+'.json')).read_bytes() for p in ('Browserpruefung','Kartenpruefung','Pflichtbogenabgleich','Work-Gegenprobe','Layoutstichprobe','Sprachumfang','Empfehlungen')}
    proof.update({p.name:p.read_bytes() for p in sorted(QA.glob('*-LA-*.jpg'))+sorted(QA.glob('nachher-MU-*.jpg'))+[QA/'Start-Gesamt.jpg',QA/'Musterkarte-Foerder.jpg']})
    for p in ['Modulquellen.json','Unterrichtspruefung.json','Pruefherkunft.json']:
        if (QA/p).exists():proof[p]=(QA/p).read_bytes()
    for p in QA.glob('Familienwege-*.json'):
        proof[p.name]=p.read_bytes()
    proof['Vertiefungspruefung.json']=(ROOT/'build/vertiefungen/Vertiefungspruefung.json').read_bytes()
    proof['Pruefbericht.md']=report
    pack(OUT/'Fallakte-Sichtpruefung.zip',proof)
    files={}
    for p in sorted(OUT.iterdir()):
        if p.name=='Buildnachweis.json':continue
        if p.suffix=='.zip':
            with ZipFile(p) as z:assert z.testzip() is None
        files[p.name]=dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes()))
    (OUT/'Buildnachweis.json').write_text(json_text(dict(softwarecommit=head,basis=BASE,status='Prüfkandidat',module=read('Module'),dateien=files)))
if __name__=='__main__':write()
