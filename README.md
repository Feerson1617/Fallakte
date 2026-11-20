# Fallakte – digitaler Verhütungsberatungs-Chat

**Entwicklungsstand: Prototyp v0.1 vom 20.11.2026. Nicht für den Unterricht freigegeben.**

Interaktive Unterrichtsfallakte für Biologie, Klasse 8, mit drei fiktiven Beratungsfällen (Laura, Celina, Tom), vier Unterstützungsstufen (Förder, ESA, MSA, AHR) und vorprogrammierten Chatreaktionen.

## Vorschau starten

Die Datei `index.html` im Browser öffnen. Der Prototyp ist eine einzige HTML-Datei ohne Build-Schritt, externe Bibliotheken oder Netzwerkzugriff. Der Browser hält den Gesprächsverlauf nur bis zum Neuladen vor.

## Dateien

- `index.html`: direkt ausführbare Vorschau inklusive Styles, Anwendungslogik und eingebetteter Falldaten
- `data/dialogdaten_prototyp.json`: dieselben Falldaten separat und lesbar strukturiert, als Grundlage für eine spätere Trennung von Daten und UI
- `docs/QA_Bericht_v01.md`: getestete Funktionen, Einschränkungen und offene Punkte

**Wichtig:** Der JSON-Datensatz ist aktuell eine Kopie der in der HTML-Datei eingebetteten Daten. Änderungen an nur einer der Dateien aktualisieren die andere nicht automatisch. Codex soll eine einzige kanonische Datenquelle schaffen.

## Didaktische Anforderungen für die weitere Entwicklung

1. Laura beginnt mit einem STI-Schutz-Anliegen, für das unter den vier behandelten Methoden das Kondom zunächst die naheliegende Antwort ist. Neue Informationen eröffnen später mehrere vertretbare Gesamtstrategien. Keine erzwungene eindeutige Endmethode.
2. Lauras ausführlicher Chat und die schrittweise Informationsfreigabe sollen erhalten bleiben. Feedback durch die fiktive Figur muss zu der vorherigen Entscheidung passen und darf nicht die nächste Antwort verraten.
3. Entscheidungen der beratenen Person respektieren. Eine Sorge ist nicht automatisch eine Ablehnung.
4. Vier tatsächliche Anspruchs- und Unterstützungsniveaus; insbesondere kurze, **konkrete** Hilfen für Förder und ESA, etwa „Lies die Kupferspiralen-Karte: Was steht dort zu Regelschmerzen?“
5. Antworten in vollständigen, natürlich formulierten Sätzen. Kein Antwortwortlaut, der bereits die „richtige“ Auswahl verrät.
6. Jede Person muss erkennen, welche Aktion als Nächstes erwartet wird. Einfache Touch-Bedienung, klarer Senden-Button, keine überflüssigen Klicks.
7. Der gesamte Messenger-Verlauf muss lesbar und frei scrollbar bleiben; frühere Entscheidungen bleiben nachvollziehbar.
8. Kein automatisches Bewerten offener Begründungen. Der individuelle Lernzuwachs wird im Unterricht anhand des Laufzettels und der doppelten Laura-Abstimmung sichtbar gemacht.
9. Celina ist der eigenständige zweite Beratungsfall; Tom behandelt als Vertiefung die Forschung an Verhütungsmitteln für Männer.
10. Zielumgebung: Safari auf Schul-iPads, Bereitstellung über itslearning als SCORM-1.2-ZIP; **keine dauerhafte Speicherung** von Lernantworten, Punkten oder Spielständen in der Anwendung oder über SCORM.

## Wichtige Grenzen dieser Version

- Der Prototyp wurde per Chromium getestet, **nicht** auf echten Schul-iPads oder in itslearning.
- Die analogen Laufzettel und Einstiegsmaterialien enthalten teilweise noch den früheren Laura-Einstieg und müssen vor einem Einsatz angepasst werden.
- Die komplette medizinische, pädagogische und sprachliche Endabnahme aller Dialogverzweigungen steht noch aus.
- Ein SCORM-Testpaket existiert separat, ist jedoch **nicht** Bestandteil dieses Repository-Imports und keine Unterrichtsfreigabe.
- Keine sensiblen Schülerdaten und keine schulinternen Lehrkraftdokumente in das öffentliche Repository aufnehmen.

## Nächster Schritt für Codex

Die vorhandene Fassung zuerst lokal starten, die drei Fälle in allen vier Niveaus prüfen, die Dialogdaten von der HTML-Oberfläche entkoppeln und eine bedienungsarme iPad-Fassung entwickeln. Anschließend alle Fehlentscheidungen, Rückfragen, Hilfen, mögliche Kombinationen und Revisionswege automatisiert und manuell testen. Ein SCORM-1.2-Paket und eine kleine lokale Sichtprüfungsversion sollen aus derselben getesteten Quelle erzeugt werden.
