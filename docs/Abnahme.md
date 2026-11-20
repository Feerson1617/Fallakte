# Fallakte · Prüfbericht für die Unterrichtserprobung

## Programmstand und Einsatz

Die Fassung baut auf dem gemergten Prototyp v0.1 (main, 471e4cc) auf. Sie ist für eine begleitete Unterrichtserprobung vorbereitet. Vor der Stunde am **2. Dezember 2026** stehen der Kurztest auf einem Schul-iPad in der schulischen itslearning-Instanz und der Abgleich der vorhandenen Papiermaterialien aus. Die Einzeldatei auf dem Mac ist die serverlose Sicherung.

## Was sich geändert hat

- Ein redaktioneller Datenbestand speist die Vorschau, die lokale Einzeldatei und das SCO. Der Prototyp enthielt zwei unabhängig editierbare Kopien.
- In jeder Entscheidungsstufe stehen vier gleich gestaltete Methoden in alphabetischer Reihenfolge zur Wahl. Alle drei Ergänzungen mit Kondom sind von beiden Ausgangsmethoden erreichbar. Erst die Vorschau lesen, dann senden. Die Figuren reagieren auf die gewählte Strategie. Einmal je Stufe lässt sich die Empfehlung revidieren, anschließend geht jeder Weg weiter.
- Echte, begrenzte Rückfragen ersetzen das unbeantwortete Freitextfeld. Jede Frage lässt sich pro Stufe einmal stellen. Zwei freiwillige Hilfen benennen zuerst eine Karte oder Chatstelle und geben anschließend eine konkrete Fachinformation.
- Beim Wechsel zwischen Fällen, Niveaus, Infokarten und Sicherung bleiben die Gespräche auf dieser Seite erhalten. Nachlesen und Zurückspringen sind möglich. Das Programm erfasst keine persönlichen Erfahrungen, bewertet keine frei formulierten Gründe und vergibt keine Punkte.

## Fälle und Denkhandlungen

| Fall | Gesprächsverlauf | Beobachtbare Denkhandlung |
| --- | --- | --- |
| Laura | Sieben Stufen. Infektionsschutz und erste Abstimmung, zusätzlicher Schwangerschaftsschutz und Alltag, Übelkeit einer Freundin, Nein zur Pille und offene Sorge vor einer Einlage, Schmerzen, erneute Prüfung beider Schutzziele, Schlussvorschlag. | Das Paar darf bestätigen, erweitern oder ändern. Die Schlussnotiz entsteht nach der letzten Entscheidung. Die Klasse vergleicht mehrere vertretbare Vorschläge mit ihrer ersten Begründung. |
| Celina | Fünf Stufen. Verhütung ohne zusätzliche Hormone, längerfristiger und beendbarer Schutz, Sorge vor der Einlage, Infektionsschutz in der Beziehung, Vergleich zweier Strategien. | Celinas Nein zu Hormonen gilt auch für die Hormonspirale. Eine Sorge vor der Kupferspirale lässt Beratung und spätere Zustimmung offen. Sicherheit, Aufwand und ein möglicher Eingriff sind abzuwägen. |
| Tom | Drei Stufen. Eigene Anwendung, Forschungsartikel, Schlussfolgerung mit offener Frage. | Die Figur erklärt körperliche Voraussetzungen und respektiert die Entscheidung der Partnerin. AHR vergleicht zwei Originalstudien nach Messgröße, Dauer, Risiken und Übertragbarkeit. |

Förder arbeitet mit kurzen Nachrichten, konkreten Kartenstellen und Satzanfängen. ESA erhält angeleitete Vergleiche und begründet eine Auswahl mit dem wichtigsten Kriterium. MSA gewichtet eigene Kriterien und entkräftet oder akzeptiert einen Einwand. AHR trennt Befund und Vermutung, formuliert eine bedingte Empfehlung und prüft Alternativen. Die persönlichen Grenzen und der gemeinsame fachliche Kern gelten auf allen Stufen.

## Durchgeführte Prüfungen

1. **Ausgangsstand.** Den Originalprototyp im Browser über einen lokalen Server gestartet. Alle zwölf Fall-Niveau-Kombinationen durchlaufen, beide Hilfen bei Methodenentscheidungen geöffnet und die hinterlegten Optionen und Reaktionen untersucht.
2. **Dialogmatrix.** Die gebaute HTML-Datei in Chromium über die gerenderten Bedienelemente bedient. Sieben Strategiepfade für jede der zwölf Kombinationen ergeben 84 Abschlüsse. In den durchlaufenen Stufen wurden 336 Empfehlungen gesendet, 728 Rückfragen gestellt und 840 Hilfestufen geprüft. Dies sind wiederholte Testaktionen. Jeder Test vergleicht sichtbare Texte mit dem Fallbestand und prüft die Reihenfolge der Gesprächsstufen. Kombinationen wurden von beiden Methoden aus gebildet.
3. **Oberfläche.** Playwright-Prüfungen mit Chromium und WebKit unter Linux in vier Formaten (1366 × 900, 820 × 1180, 1180 × 820, 360 × 740). Echte Klicks auf beschriftete Hilfe- und Sende-Schaltflächen, Vorschau, Überarbeitung, Sprungfunktion, Infokarten, Sicherung mitten im Fall, Fallwechsel, Rückkehr zu Laura und Neustart nach Neuladen. Kontrolliert wurden Mindesttouchflächen von 44 CSS-Pixeln, seitlicher Überlauf, Sichtbarkeit von Senden, Scrollposition beim Nachlesen und Erhalt der Nachrichten. Ein im Test entdeckter Überlauf langer Methodennamen auf schmalen Geräten wurde behoben. Die Bildschirmfotos stammen aus Chromium.
4. **Offline.** Lokalen Einzeldateistart über einen file-Pfad geprüft. In Chromium war der Kontext offline. Bei WebKit blockiert die Offline-Emulation bereits die lokale Dateinavigation. Dort wurden beim lokalen Start alle HTTP(S)-Anfragen abgefangen und gesperrt. In den geprüften Abläufen gab es keine externen Anfragen oder JavaScript-Laufzeitfehler.
5. **SCORM und Ausgaben.** ZIP entpackt, CRC und beide Namensräume mit den beigelegten XSDs geprüft. Organisationsverweis, SCO-Typ, Startdatei und Bytegleichheit mit der lokalen HTML-Datei kontrolliert. Den extrahierten Inhalt in einem lokalen LMS-Testrahmen gestartet und eine Empfehlung gesendet. Beobachtet wurden nur LMSInitialize und LMSFinish mit leerem Argument. Das Sichtprüfungspaket enthält die identische HTML-Datei samt SHA-256-Zuordnung zu den JSON-Protokollen.
6. **Fachliche und didaktische Durchsicht.** Wirkprinzip, Alltagssicherheit, Infektionsschutz und mögliche Beschwerden anhand der BIÖG-Fachinformationen geprüft. Beide Zahlenbeispiele aus Toms Artikel mit den Originalarbeiten abgeglichen. Eingangsreaktionen, persönliche Grenzen, später freizugebende Informationen, neutral formulierte Beratungsnachrichten und Schreibaufträge gesichtet. Die Begründung beurteilen die Lernenden und die Lehrkraft im Gespräch.

Die technischen Einzelresultate stehen im Sichtprüfungspaket unter **Protokolle/**. Für biologische Quellen und Studiengrenzen siehe **Fachquellen.md** im Paket oder **docs/Fachpruefung.md** im Repository.

## Offene Punkte vor dem Unterrichtsbesuch

- **Geräte und Lernplattform.** Es standen keine echten Schul-iPads, kein macOS-Safari und kein Zugang zum schulischen itslearning-Kurs zur Verfügung. Das SCORM-Paket in einem Testkurs importieren. Auf einem Schul-iPad im Hoch- und Querformat Laura öffnen, eine Empfehlung senden, ändern, die Sicherung öffnen und zur früheren Nachricht zurückkehren. Den Doppelklick auf die einzelne HTML-Datei am Unterrichts-Mac prüfen.
- **Lesezeit und Selbstständigkeit.** Browserprüfungen belegen erreichbare Schaltflächen. Ob Förder- und ESA-Lernende sie ohne Erklärung finden und die Begründungen in 18–20 Minuten schaffen, muss ein kurzer Probedurchlauf mit Lernenden zeigen. Danach bei Bedarf einzelne Arbeitsaufträge kürzen. Fehlt Zeit, direkt über „Sicherung“ zur gemeinsamen Abstimmung wechseln.
- **Papiermaterial.** Die tatsächlichen Arbeitsblätter lagen dem Repository nicht bei. Einstieg auf STI-Schutz ausrichten. Jede Person braucht Platz für Anfangs- und Schlussbegründung. Die Vorlage im Unterrichtsablauf kann an die vorhandenen Zettel angelegt werden.
- **Freigabe.** Eine unabhängige medizinische oder pädagogische Begutachtung und eine Messung eines Lernzuwachses wurden nicht durchgeführt. Die Lehrkraft entscheidet nach dem Probelauf über den Einsatz.
