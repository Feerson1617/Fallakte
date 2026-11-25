"""Create the teacher handover and seal the tested build."""
import json
import os
from zipfile import ZipFile
from auslieferung import OUT,QA,VERSIONS,ROOT,PRINT,PREP,FIRST,JOINT,MOD_HASH,sha,revision,json_text,pack

def read(name):
    return json.loads((QA/name).read_text())

def write():
    head=revision()
    cards=read('Kartenpruefung.json')
    checks=read('Browserpruefung.json')
    ub=read('Unterrichtspruefung.json')
    runs=read('Referenzlaeufe.json')
    assert cards['commit']==checks['commit']==ub['commit']==head
    assert {r['commit'] for r in runs if r['ergebnis']=='success'}=={PREP,FIRST,JOINT}
    assert len(cards['karten'])==16 and sum(len(r['felder']) for r in cards['karten'])==64
    assert len(ub['wege'])==8 and len(ub['karten'])==80
    table=['| Niveau | Methode | Schüler-/Referenzseite | Felder 1 · 2 · 3 · 4 | Volltext | Digitale Wege¹ | Ergebnis |',
           '|---|---|---|---|---|---|---|']
    for c in cards['karten']:
        assert len(c['laeufe'])==4 and len(c['wege'])==4
        answers=' · '.join(f["answer"] for f in c['felder'])
        table.append(f"| {c['niveau']} | {c['methode']} | {c['seite']} / {c['seite']} | {answers} | wortgleich | 4/4 | bestanden |")
    material=f"""# Musterkarten-Abgleich

Integration `{head}`. Prüfgrundlage ist das am 25.11.2026 beigefügte und als Unterrichtsmaterial bestätigte **Materialpaket_Proberunde_26-11-2026_Druckversion.zip**, SHA-256 `{sha(PRINT.read_bytes())}`. Geprüft wurden die vier tatsächlichen Schüler-PDFs unter 01_Schuelermaterial und die vier ausgefüllten PDFs unter 02_Lehrkraft/Referenzkarten. Die einzelnen PDF-Prüfsummen stehen in Kartenpruefung.json im Sichtprüfungspaket. Das separat genannte Archiv „mit_Screenshots(2)“ lag für einen zusätzlichen Binärvergleich zwischen Archiven nicht vor.

Der Browser las die beiden freigegebenen Felder in A und die beiden in B jeweils von der sichtbaren Papieransicht ab. Der Test setzte sie an den vier nummerierten Leerstellen der betreffenden PDF-Seite ein und verglich das Ergebnis einschließlich Nummern mit der gedruckten Referenz. Für den zweiten Vergleich wurden nur die Einfügemarken entfernt. Überschrift, Pearl-Index-Zeile, Erläuterung, fünf Abschnittstitel und alle fünf Absätze wurden in Lesereihenfolge mit den sichtbaren Texten der Browserkarte verglichen. Dabei wurden Zeilenumbrüche und druckbedingte Abstände vereinheitlicht. Interpunktion, Begriffe, Wortreihenfolge und Zahlen blieben Teil des Vergleichs. Niveau und Feldnummern wurden gesondert geprüft.

{chr(10).join(table)}

¹ Regulärer B-Kartenvergleich, wiederaufgenommener Kartenvergleich, Musterkarte über den Ausfall-/Zeitnotzugang nach frischem Start sowie Abschlussvergleich nach 4B. Jeder Weg wurde mit Chromium und WebKit im Offline-HTML und im entpackten SCO geprüft. Die regulären A/B-Feldfreigaben sind zusätzlich belegt. Ergebnis für das beigefügte Unterrichtsmaterial: 16 von 16 Volltexten und 64 von 64 Einträgen stimmen überein.

## Korrigierter Übertragungsfehler

Im Stand 7f26cd7 fehlten im Kopf der digitalen Vollkarte die gedruckten Angaben „Richtwert nach pro familia“ und „Kein Maß für den Schutz vor sexuell übertragbaren Infektionen (STI).“ Die integrierte Ansicht übernimmt beide Aussagen und die Interpunktion der Druckfassung. Alle vier Zugänge verwenden denselben korrigierten Kartenkopf. Wortlaut und Position der eingesetzten Begriffe stimmen mit den ausgefüllten Referenzsätzen überein.

## Abgleich mit der Beratung am 02.12.

Die 80 niveau- und abschnittsbezogenen Quelltexte im Kartenvertrag wurden mit den entsprechenden langen oder kurzen Texten in der ausgelieferten Laura-Akte verglichen. Unterrichtspruefung.json stellt jedem UB-Text die zugehörige vollständig ausgefüllte Vorbereitungspassage gegenüber. Beim Kondom stimmen Barrierewirkung und begrenzte STI-Risikominderung überein. Bei der Pille stimmen Eisprunghemmung und Einnahmebedingungen überein. Die Texte beider Spiralen unterscheiden Kupferwirkung und Gestagenwirkung und nennen mögliche Blutungsveränderungen, ärztliche Eignung und Zustimmung. Im Vergleich ergab sich kein fachlicher Widerspruch.

Die vorbereitenden Karten verwenden historische Pearl-Index-Richtwerte. Der Bezug sind 100 Anwendungsjahre, im vereinfachten Beispiel 100 Frauen während eines Jahres. Ein Anteil von Schwangerschaften im ersten Anwendungsjahr ist eine andere Kenngröße. Die vier fachlichen UB-Nachschlagekarten beschreiben die Bedingungen und Grenzen der Methoden qualitativ. Eine Umrechnung oder Gleichsetzung mit Erstjahresraten findet dort nicht statt.
"""
    (OUT/'Musterkarten-Abgleich.md').write_text(material)
    links='\n'.join(f"- `{r['commit'][:7]}` · {', '.join(r['jobs'])}. [Lauf {r['lauf']}]({r['url']})" for r in runs)
    report=f"""# Gesamtprüfbericht und Einsatz in itslearning

Stand `{head}` auf `integration/drei-unterrichtsmodule`. Die Tagesauswahl trägt die bisherigen neutralen Porträts und darüber einen direkten Einstieg in die Vorbereitung. Beide Vorbereitungsstunden befinden sich im selben Modul. Alle Module verwenden die gemeinsame Rückkehr zur Tagesauswahl. Die Auswahl einer Stufe oder eines Wiedereinstiegs findet im jeweiligen Modul statt.

## Unterrichtspakete

| Termin | SCORM-Datei | Zugang |
|---|---|---|
| Ab 26.11. | Fallakte-Vorbereitung-SCORM12.zip | Vorbereitung |
| 02.12. | Fallakte-02-12-SCORM12.zip | Vorbereitung und Laura |
| 08.12. | Fallakte-08-12-SCORM12.zip | Alle drei Module |
| Vollständige Fassung | Fallakte-Gesamt-SCORM12.zip | Alle drei Module |

Zu jeder Zeile gehört eine gleichnamige Offline-HTML ohne den Zusatz „-SCORM12“. Die beiden vollständigen HTML-Dateien sind bytegleich. Die SCO-Manifeste tragen eigene Paketkennungen. Für die Klasse jeweils das vorgesehene ZIP als eigene SCORM-1.2-Lernressource importieren, in der Lernendenansicht prüfen und die Ressource zum betreffenden Termin sichtbar schalten. Die vollständigen Fassungen erst für den zweiten Besuch freigeben. Ob beim Austausch eines ZIPs eine bestehende Kursverknüpfung erhalten bleibt, wurde in itslearning nicht erprobt.

## Neu ausgeführt

Die gebauten vier Offline-Dateien und die vier entpackten SCORM-Ausgaben wurden in Chromium und WebKit geöffnet. Das ergibt 16 Kombinationen aus Engine, Auslieferungsform und Freigabestufe. Freigaben und echte Nutzdaten wurden separat geprüft. Nur die freigegebenen Dokumente sind eingebettet. Die gesperrten Karten besitzen keinen Modulverweis. Die Pakete enthalten das jeweilige HTML, das Manifest an der Wurzel und die drei lokalen XSD-Dateien. Alle Manifeste wurden schema-validiert.

Auf der gemeinsamen Tagesauswahl wurden iPad-Hoch-/Querformat, ein kleines Test-LMS-Fenster, 150 % Grundschrift, Touchziele und die Rückkehr erprobt. Die Tests wechselten bei laufender Arbeit zwischen Modulen, prüften Auswahl und Hilfe nach der Rückkehr, vollständiges Neuladen und den direkten Wiedereinstieg. Im Test-LMS wurden nur Sitzungsbeginn und Sitzungsende registriert. Die Browserprüfung überwachte Cookies, Schreibaufrufe, IndexedDB und Netzwerkzugriffe.

In der vollständigen Integration liefen 32 Vorbereitungswege einschließlich aller vier Niveaus, korrekter Antworten, sämtlicher Fehlantworten, fünf Hilfen und zusätzlicher Anwendungsfragen. Geprüft wurden alle 68 regulären Fachfragen, acht Papiercodes, bewusster Versand, Freigabe der 64 Felder, beide Stundenabschlüsse, Fortsetzung und Wiedereinstieg. Freie Papierbegründungen unterliegen weiter der Prüfung im Unterricht.

Auf den neuen Tagesfassungen liefen zusätzlich je acht vollständige Laura- und Familienratswege über alle vier Niveaus und beide Engines. Die drei Original-Abnahmeworkflows wurden für diesen Auftrag auf ihren freigegebenen Commitständen neu gestartet und erfolgreich abgeschlossen:

{links}

## Bestandsschutz und Referenzen

Die Tagesauswahl geht auf `ec94147fd8d61442305a0281f7df032f3162362c` zurück. Verwendet wurde der ausgelieferte Rahmen der gemeinsamen Freigabe `{JOINT}`. Die Vorlage der Vorbereitung stammt aus `{PREP}`, die Beratung aus `{FIRST}`. Die ursprünglichen Dateien wurden reproduzierbar an diesen Commits gebaut und an publizierten SHA-256-Werten gemessen. Die eingebetteten UB-Dokumente sind in jeder freigegebenen Variante bytegleich zu diesen Referenzen:

- Laura am 02.12. · `{MOD_HASH['02']}`
- Familiennachrichten am 08.12. · `{MOD_HASH['08']}`

In der eingebetteten Vorbereitung wurden ausschließlich die Schnittstelle zur gemeinsamen Navigation/Sitzung, der nachgewiesen unvollständige gedruckte Kartenkopf und der abschließende organisatorische Hinweis angepasst. Die Inhaltsbank wird bytegleich übernommen. Die eigenständigen Vorbereitungs-, UB- und Übungsdateien stehen an ihren bisherigen Entwicklungsständen weiterhin als Rückfalloptionen zur Verfügung.

## Papier und verbleibende Praxistests

Für die gewählte Duplexfassung die Seiten 1 und 2 der Schüler-PDF bei 100 % auf ein A4-Blatt doppelseitig drucken. In der vorgesehenen Zuordnung liegen Kondom und Kupferspirale sowie Kombinationspille und Hormonspirale jeweils auf Vorder- und Rückseite. An der gestrichelten Mittellinie entstehen zwei A5-Karten. Die Laufzettelseiten 3 und 4 separat halten. Auf Seite 4 aller vier Schülerfassungen steht unter „Nach 4B“ noch „Schneide erst jetzt die vier Karten an den gestrichelten Linien aus.“ Für den Duplexdruck gilt die eine Mittellinie durch das beidseitig bedruckte Blatt. Die Handreichung im Druckpaket nennt noch einseitigen Kartendruck und vier Karten. Der beiliegende Prüfbericht zählt vier ausgeschnittene A5-Karten. Diese älteren Papierhinweise beziehen sich auf den einseitigen Druck; die PDFs wurden wie beauftragt unverändert verwendet.

Übernommene frühere Befunde sind die Freigabeprüfsummen und die Unterrichtsplanung mit rund 15 Minuten pro Methode. Offen sind der Probedruck am konkreten Schulkopierer (Kantenwendung, Vorder-/Rückseite und Schnittlinie), der Offline-Start auf einem verwalteten Schul-iPad, der Import und Kurswechsel in der produktiven itslearning-Installation sowie die tatsächliche Bearbeitungszeit mit Lernenden.
"""
    (OUT/'Gesamtpruefbericht.md').write_text(report)
    names=['Start-Vorbereitung','Start-02-12','Start-08-12','Wiederaufnahme','Laura-02','Familienrat-08',
           *['Vorbereitung-'+l for l in ('Foerder','ESA','MSA','AHR')],'Musterkarte-AHR','Musterkarte-Foerder']
    proof={n+'.jpg':(QA/(n+'.jpg')).read_bytes() for n in names}
    for n in ('Module','Kartenpruefung','Browserpruefung','Unterrichtspruefung','Referenzlaeufe'):
        proof[n+'.json']=(QA/(n+'.json')).read_bytes()
    proof.update({'Musterkarten-Abgleich.md':material,'Gesamtpruefbericht.md':report})
    pack(OUT/'Fallakte-Sichtpruefung.zip',proof)
    files={}
    for path in sorted(OUT.iterdir()):
        if path.name=='Buildnachweis.json':continue
        if path.suffix=='.zip':
            with ZipFile(path) as z:assert z.testzip() is None
        files[path.name]={'bytes':path.stat().st_size,'sha256':sha(path.read_bytes())}
    (OUT/'Buildnachweis.json').write_text(json_text(dict(commit=head,actions_run=os.getenv('GITHUB_RUN_ID'),referenzlaeufe=runs,
        daten=read('Module.json'),druckmaterial_sha256=sha(PRINT.read_bytes()),dateien=files)))
if __name__=='__main__':write()
