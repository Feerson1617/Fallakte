"""Packe nur mit vollständig nachgewiesenen Work-Zuständen und Browserwegen."""
import argparse
import csv
import json
import shutil
from pathlib import Path
from auslieferung import OUT,QA,ROOT,sha,pack
from abnahme import SOURCE


def load(name):return json.loads((QA/(name+'.json')).read_text())


def run(dest,ref):
    dest.mkdir(parents=True,exist_ok=True)
    scope=load('Vertragsumfang')
    assert scope['vertrag']=={'wortgleich':8021} and 'Separater Wortlautvergleich offen' not in scope['weitere']
    media=list(csv.DictReader((QA/'Medienwechselmatrix.csv').open()))
    assert len(media)==122 and all(r['Sollprüfung']=='wortgleich' and r['Verifizierte Druckanker'] for r in media)
    assert len(load('Unterrichtspruefung')['wege'])==8
    assert len(load('Lehrkraftstopp'))==40 and len(load('Papierfachchecks'))==26
    assert len(load('Celina-Varianten'))==140 and len(load('Empfehlungen'))==140
    assert len(load('Browserpruefung')['sitzungen'])==16 and len(load('Browserpruefung')['wege'])==32
    assert len(load('Work-Gegenprobe'))==112
    for engine in ('chromium','webkit'):
        assert len(load('Familienwege-verlauf-'+engine)['wege'])==8
        assert len(load('Familienwege-tandem-'+engine)['pruefungen'])==47
    sw='b166bce44d4b07d0a87ccc64b4471fa7410ad71e'
    names=load('CI-Abgleich')['artefakte']
    for name,spec in names.items():
        assert sha((OUT/name).read_bytes())==spec['sha256']
        shutil.copyfile(OUT/name,dest/name)
    fallback='Rueckfall-Vorbereitung.zip';shutil.copyfile(ref/fallback,dest/fallback)
    assert sha((dest/fallback).read_bytes())==load('CI-Abgleich')['rueckfall']
    report='''# Prüfbericht zur kompakten Fallakte

Software `'''+sw+'''`, Entwicklungszweig `korrektur/ub-kompakt`. Vergleichsstand `562ea2566dd80e31c093f313b925adcb31e22c9a`. Der jüngere Ausgangscommit `2c07ca0` ergänzte Prüfungen und Übergabewerkzeuge. Die Ausgangsauslieferung für den Wortlautvergleich stammt aus dem bereitgestellten Release 562ea25.

## Was im Unterricht anders erscheint

- Die Papierverweise führen bei Mutter und Freundin auf Seite 1, bei Lauras eigener Antwort und „Festhalten“ auf Seite 2. Die freiwilligen Nachrichten führen auf Seite 1 des Vertiefungsbogens. Am 02.12. liegen Lauras Schlussrat auf Seite 1 (Förder/ESA) bzw. Seite 3 (MSA/AHR), Tom auf Seite 1 und Celina auf Seiten 1–2.
- Celina zeigt auf MSA und AHR unmittelbar nach der zulässigen Methodenwahl die dazugehörigen drei Aussagen am iPad. Die Begründung und der Buchstabe gehören auf den Bogen. Am Gerät folgen „Code prüfen“ und bei passendem Code „Nachricht senden“.
- Nach einem Neustart erklärt „Festhalten“ auf allen Niveaus den Papiernachweis „digital geprüft“ oder „analog geprüft“ sowie den Rückweg für „noch offen“ und ein leeres Feld. Der direkte Einstieg erzeugt keinen gespeicherten Prüfungserfolg. Die erste persönliche Antwort bleibt stehen. Bei Förder verlangt die Begründung ausdrücklich die Bewertung der Nachricht mit einem biologischen Fakt.

## Nachweise am ausgelieferten Programm

Alle 8.021 ursprünglichen UB-Ansichten wurden auf beiden Seiten mit vollständigem Wortlaut und SHA-256 verglichen. Für jede ist die aktuelle Browserbeobachtung hinterlegt. Alle 1.338 Zeilenänderungen in 1.170 Ansichten wurden gegen die Excel-Prüfsummen rekonstruiert. Die drei zusätzlichen Vorgaben für Celina und Lauras Frage sind je betroffener Ansicht gesondert ausgewiesen. Zusätzliche Aufnahmezeitpunkte und Zustände stehen mit ihrem eigenen Vergleich im Bildschirmtextvertrag.

Die 122 UB-Medienwechsel sind einzeln mit gedrucktem Feld, Seite, Bildschirm und Rückweg belegt. Work hatte 94 Auftragsänderungen, vier reine Papierzuordnungen und 24 gleichbleibende Übergänge ausgewiesen. Die 18 PDF-Referenzen stimmen byteweise mit den separaten Druckpaketen überein. Alle 26 Papierfragen auf MSA und AHR wurden samt A/B/C-Reihenfolge und Lehrkraftcode kontrolliert. Bei Celina ist der vorliegende Druck die Kondomfassung; die Übergabe enthält das neue Papierfeld und ein druckbares Ersatzblatt mit allen 13 zulässigen Abschnitts-/Methodenkombinationen.

| Niveau | Vollständiger Lernweg 02.12. | Vollständiger Lernweg 08.12. | Weitere Prüfungen am Gerät |
|---|---|---|---|
| Förder | Chromium und WebKit | Chromium und WebKit | Erstes Kreuz, geprüfte Wahl, Hilfen, Anwendung, LA-02 mit Satzstarter, Wiedereinstieg |
| ESA | Chromium und WebKit | Chromium und WebKit | Erstes Kreuz, geprüfte Wahl, Hilfen, Anwendung, Wiedereinstieg |
| MSA | Chromium und WebKit | Chromium und WebKit | Papierbegründung und Code, Neuwahl, Celinas 35 Abschnitts-/Methodenwahlen je Browser |
| AHR | Chromium und WebKit | Chromium und WebKit | Papierbegründung und Code, Neuwahl, Celinas 35 Abschnitts-/Methodenwahlen je Browser |

Für Laura wurden 140 Abschnitts-/Niveau-/Methodenkombinationen und fünf Hilfen geprüft, dazu 40 Lehrkraftstopps (alle fünf Abschnitte auf vier Niveaus in beiden Browsern). Bei jedem Stopp sind alle Anliegen und der Schlussrat ohne Code erreichbar. Für Celina wurde je hohem Niveau und Browser bei 13 zulässigen Wahlen die vollständige Aussagenreihenfolge sowie jede falsche und richtige Codeeingabe geprüft. Bei 22 weiteren Wahlen greift die vorhandene Konfliktrückmeldung. Für Tom und Celina liegen zusätzlich vollständige Gesprächsdurchläufe vor.

Der Familienrat wurde zusätzlich auf acht regulären und unterstützten Wegen je Browser bedient. Die Prüfung umfasst Fach- und Fehlerwege, persönliche Entscheidungen, freie Eingaben, Wechsel, direkte Wiederaufnahme, freiwillige Nachrichten, Lösungshilfen und Folgefragen. Die Statusprüfung umfasst je Browser 47 Fälle und zwölf Gegenproben zur Quellenarbeit. 112 gezielte Papieransichten dokumentieren Erst- und Ergebnisspur, Abschluss, Neustart und Stopp. Die fachliche Beurteilung freier Begründungen bleibt Aufgabe des Unterrichts.

Alle vier Offline-HTML-Dateien sind bytegleich mit der jeweiligen index.html im SCORM. Geprüft sind SCORM-1.2-Manifest und Ressourcen, Initialisierung und Beenden im Test-LMS, gestaffelte Freigabe, Speicher- und Netzwerkkontrolle sowie alle vier Varianten in beiden Browsern. In der ersten Freigabe ist kein späteres Modul eingebettet. Die Vorbereitungs-HTML, die Vorbereitungs-SCORM-Datei und die separat beigefügte Rückfallauslieferung stimmen byteweise mit dem Referenzstand überein. Der Datenvergleich erfasst alle eingebetteten Module; Fragen, Antworten, Reihenfolge, fachliche Rückmeldungen, Karten und Schlüssel sind außerhalb der beauftragten Papiertextkorrekturen unverändert.

Der unabhängige GitHub-Runner hat alle acht Programmdateien erneut gebaut. Die heruntergeladenen Dateien stimmen mit den lokal geprüften Dateien überein. Der Lauf ist unter https://github.com/Feerson1617/Fallakte/actions/runs/45768593839 dokumentiert. Der erste CI-Versuch benutzte im Test den falschen Namen für „Zurück“. Bei den lokalen Prüfläufen wurden außerdem Wartezeit und die Suche nach dem SCORM-Rahmen beim Neuladen korrigiert. Die betroffenen Wege liefen anschließend vollständig durch.

## Verbleibende Abnahme

Work setzt die aufgeführten Änderungen in den kompakten Druckbögen um. Anschließend die endgültigen Druckseiten mit der ausgelieferten Software unabhängig gegenlesen. Insbesondere bei Celina eine andere zulässige Empfehlung als das Kondom wählen und den Ausfallweg auf Papier benutzen. Bei „Festhalten“ einmal mit „analog geprüft“ und einmal mit „noch offen“ direkt einsteigen. Ein echtes Schul-iPad, der produktive itslearning-Kurs und eine Prüfung durch Lernende standen hier nicht zur Verfügung. Die Unterrichtsfreigabe bleibt der gemeinsamen Endabnahme vorbehalten.
'''
    (dest/'Pruefbericht.md').write_text(report)
    evidence=['Vertragsumfang','Browserpruefung','Unterrichtspruefung','Lehrkraftstopp','Papierfachchecks',
        'Druckabgleich','Celina-Varianten','Textdiff','Kartenpruefung','Work-Gegenprobe','Empfehlungen',
        'Familienwege-verlauf-chromium','Familienwege-verlauf-webkit','Familienwege-tandem-chromium','Familienwege-tandem-webkit','CI-Abgleich']
    sight={name+'.json':(QA/(name+'.json')).read_bytes() for name in evidence}
    sight['Vertiefungspruefung.json']=(ROOT/'build/vertiefungen/Vertiefungspruefung.json').read_bytes()
    for name in ('chromium-Celina-4-Kupfer','webkit-Celina-4-Kupfer','Work-Schlussrat-Stopp','Work-LA-offen','Work-LA-eigen',
                 'Work-LA-abschluss','Work-MU-erst','Work-FR-ergebnis','Work-GM-einstieg','Work-VA-erst'):
        sight['Screenshots/'+name+'.jpg']=(QA/(name+'.jpg')).read_bytes()
    sight['Pruefbericht.md']=report
    pack(dest/'Fallakte-Sichtpruefung.zip',sight)
    docs=['Fallakte-Bildschirmtextvertrag.zip','Medienwechselmatrix.csv','Letzte_Materialkorrekturen_Work.md','Work-Materialexport.zip','Textdiff.json']
    for name in docs:shutil.copyfile(QA/name,dest/name)
    manifest=''.join(s['sha256']+'  '+k+'\n' for k,s in sorted(names.items()))
    review={n:(dest/n).read_bytes() for n in docs+['Pruefbericht.md','Fallakte-Sichtpruefung.zip']}
    review['Programmdateien.sha256']=manifest
    pack(SOURCE/'Kompakt-Abnahmenachweise.zip',review)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('ziel',type=Path);p.add_argument('referenz',type=Path)
    a=p.parse_args();run(a.ziel,a.referenz)
