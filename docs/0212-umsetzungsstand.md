# Fallakte Laura · Runde 2A für den 02.12.2026

## Fassung und Arbeitsmaterial

Arbeitszweig `entwicklung/0212-neukonzeption`, Basiscommit `62b6dca2723006c25cc7724f5f595799b5743dd2`. Die Ausgangsfassung war die Auslieferung mit Bank `0212-r1.2` aus Actions-Lauf `45049836491`.

- **Abschlusscommit der Auslieferung** · siehe `Materialvertrag.json`, Feld `buildCommit`.
- **Inhaltsbankversion** · `0212-r2a.1`.

Im Artefakt **Fallakte-Runde-2A** die Datei **Fallakte.html** direkt im Browser öffnen. **Materialvertrag.md** enthält die lesbare Übergabe für Work. **Materialvertrag.json** enthält dieselben Aufgaben, Fachanker, Lösungen, Kartenstellen und Rückmeldungen wie die eingebettete Inhaltsbank. Die individuelle Begründung verbleibt auf Papier. Die HTML-Datei speichert den Beratungsstand im Arbeitsspeicher, getrennt nach Niveau.

## Unterrichtsweg

| Abschnitt | Woran das Team seinen Rat prüft |
| --- | --- |
| Laura 1 – Latexallergie | Die Allergie betrifft das Material. Der erste Rat aus dem analogen Einstieg kann bestätigt oder präzisiert werden. |
| Laura 2 – Zwei Schutzziele | Zum Schwangerschaftsschutz kommt STI-Risikominderung hinzu. Das Team prüft, welchen Beitrag jede gewählte Methode leistet. |
| Laura 3 – Hormone und Alltag | Ein unregelmäßiger Tagesablauf erschwert die Einnahmeroutine. Die Erfahrung der Freundin erlaubt keine sichere Vorhersage über Lauras Verträglichkeit. |
| Laura 4 – Schmerzen und Einlage | Die Wirkung auf Beschwerden, eine ärztliche Abklärung und Lauras Zustimmung sind eigenständige Gesichtspunkte. |
| Laura 5 – Mein Schlussrat | Das Team begründet seine Gewichtung. Der erste und der letzte Grund werden verglichen, auch wenn die Empfehlung gleich bleibt. |

Nach der Wahl tritt der vollständige Rat an die Stelle der Auswahlliste. Der Fachcheck kann direkt bearbeitet werden. Eine bewusste neue Wahl entwertet die alte Sendefreigabe. Ein gezielter Kartenaufruf zeigt die betreffende Textstelle. Von dort ist die ganze Karte erreichbar. Förder und ESA prüfen Gründe im Gespräch. MSA und AHR nutzen regulär den Papierauftrag und einen Buchstaben. Die ausklappbare digitale Ersatzaufgabe enthält denselben Denkauftrag. Der Buchstabe bestätigt den Fachanker. Die Qualität des eigenen Schlussrats wird im Unterricht besprochen.

Nach einem Neuladen führen Niveau und „Abschnitt auswählen“ zu jedem der fünf Abschnitte. Der Einstieg nennt die erforderlichen bisherigen Fakten. „Weiterarbeiten“ setzt den tatsächlichen Entwurf im geöffneten Dokument fort. „Neu beginnen“ beginnt die gewählte Sitzung neu.

Für die gemeinsame Sicherung am Seitenfuß „Für die Lehrkraft“ öffnen. Die vollständige Fallübersicht ist auch bei vorzeitigem Ende der Erarbeitung erreichbar. Alle verwenden das Feld „Mein Schlussrat“ auf dem Laufzettel. Wer den Schlussrat schon formuliert hat, nutzt diesen für den Vergleich. Tom und anschließend Celina sind freiwillige Vertiefungen.

## Prüffolge und geänderte Erwartungen

1. Die überarbeitete Oberfläche wurde mit ausschließlich Laura 1 und 2 in der gebauten HTML geprüft. Das archivierte Protokoll enthält die Prüfsumme dieser Fassung und die damaligen Bildschirmaufnahmen.
2. Nach dieser Prüfung wurden die drei weiteren Abschnitte aktiviert. Der Materialtest vergleicht Fallfakten, Abschnittstitel, IDs und Fachanker mit der Ausgangsbank. Die frühere Erwartung „zwei spielbare Abschnitte“ ist durch fünf spielbare Abschnitte und fünf reguläre Fachchecks ersetzt.
3. Die Browserprüfungen unterscheiden Wahl, Begründung, Korrektur, Versand und Antwort. Sie bedienen zum Ändern eines Entwurfs den sichtbaren Auswahlzugang. Ein gezielter Kartenaufruf wird zuerst auf die einzelne Textstelle geprüft, die Vollansicht separat. Der Direkteinstieg und der Fortgang nach L02 werden anhand aller fünf freigegebenen Abschnitte geprüft. Für Laura 3 prüft der Kartentest bei Kombinationen den Alltagsbezug und das STI-Ziel. Für Laura 4 und 5 prüft er bei jeder Spirale zusätzlich die Kartenstelle zur Einlage. Die Sicherungsprüfung auf AHR erwartet den niveauspezifischen Satzanfang „Seit ich weiß, dass …“, die Gewichtung zweier Anliegen, eine Alternative und den Vergleich der Gründe. Die Prüfung unvollständiger Ratschläge erfasst bei Förder und ESA auch die ausdrückliche Erklärung zu Krankheitserregern, bei MSA und AHR die offenen Fragen zur fehlenden Schutzwirkung.
4. Die vollständigen Browserwege prüfen alle vier Niveaus, sieben Strategien und beide Browser. Der technische Bericht dokumentiert die tatsächlich bedienten Hauptentscheidungen, Papierwechsel, Codes und sichtbaren Pflichtwörter. Der fachliche Bericht erläutert die unabhängig geprüften Erwartungen zu Alltag, Schmerzen und Schlussrat.
5. Der Bestandstest setzt die gemeinsame Tagesauswahl für die Integration mit dem tatsächlichen Nachrichtenmodul aus `5d27cc3d61db386468d3f851347690b33b5d86fe` zusammen. Eigenständige CI-Jobs prüfen außerdem die früher ausgelieferte 02.12.-Fassung und das Originalmodul vom 08.12.

Zur Wiederholung im selben Checkout mit den Abhängigkeiten aus `tests/requirements.txt` und installierten Playwright-Browsern:

```sh
python scripts/build.py
python tests/runde1_vertrag.py
python tests/runde1_browser.py
python tests/runde2a_bedienung.py
python tests/runde1_karten.py
python tests/runde1_bestand.py
python scripts/runde1_bericht.py
```

## Offen für die Unterrichtserprobung

Auf echten Schul-iPads und im itslearning-Kurs den ersten Einstieg, eine Korrektur, die Codeeingabe mit der Bildschirmtastatur und die Rückkehr zur Sicherung prüfen. Mit realen Förder- und ESA-Lernenden beobachten, wie selbstständig die Kartenstelle genutzt und ein früherer Rat neu begründet wird. Das Zeitfenster von rund 22 Minuten ist ein Planungswert. Die automatisierten Bedienwege messen keine Schülerarbeitszeit. Die spätere Integration beider Tage, die fachliche Revision der Vertiefungen und die separate Übungsakte haben eigene Abnahmen.
