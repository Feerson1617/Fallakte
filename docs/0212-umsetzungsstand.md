# Fallakte Laura · Runde 1

## Entwicklungsstand und Einstieg

Arbeitszweig `entwicklung/0212-neukonzeption`, Ausgangscommit `ec94147fd8d61442305a0281f7df032f3162362c`. Die gleichnamige Datei im Actions-Artefakt enthält zusätzlich den exakten Auslieferungscommit. Er steht auch im Feld `buildCommit` des Materialvertrags.

- **Abschlusscommit der Auslieferung** · siehe `Materialvertrag.json`, Feld `buildCommit`.
- **Abschlusscommit der Implementierung** · `821ff628390a1ff65352a11d83185ed3d1975dc9`.
- **Inhaltsbankversion** · `0212-r1.1`

Mit `python scripts/build.py` entstehen unter `dist/Runde-1/` die eigenständige `Fallakte.html`, der maschinenlesbare und der lesbare Materialvertrag sowie diese Fortsetzungsdokumentation. Die HTML-Datei direkt im Browser öffnen. Für den Weg am Gerät die Stufe wählen und bei Laura „Neu beginnen“ antippen. „Abschnitt auswählen“ führt mit einer Zusammenfassung direkt zu Laura 2. „Weiterarbeiten“ führt zum tatsächlichen Entwurf dieses Niveaus im noch geöffneten Dokument.

## Umfang der Erprobung

| Abschnitt | Stand und fachliche Leistung |
| --- | --- |
| Laura 1 – Latexallergie | Spielbar. Die Lerngruppe unterscheidet Material und Methode. Eine zutreffende erste Empfehlung lässt sich biologisch präzisieren oder bestätigen. |
| Laura 2 – Zwei Schutzziele | Spielbar. Das neu genannte STI-Anliegen verlangt eine erneute Prüfung der vollständigen Strategie. Eine Methode mit gutem Schwangerschaftsschutz kann allein das zweite Ziel offenlassen. |
| Laura 3 – Hormone und Alltag | Als Materialvertrag spezifiziert. Die regelmäßige Einnahme, Lauras Tagesablauf und die begrenzte Übertragbarkeit der Erfahrung ihrer Freundin werden relevant. |
| Laura 4 – Schmerzen und Einlage | Als Materialvertrag spezifiziert. Mögliche Wirkungen auf Schmerzen, ärztliche Abklärung und die eigene Entscheidung über die Einlage sind getrennte Kriterien. |
| Laura 5 – Mein Schlussrat | Als Materialvertrag spezifiziert. Der Schlussrat und die analoge Sicherung nutzen ein gemeinsames Schreibfeld. Die Begründung wird mit dem ersten Rat verglichen. |

Die Lehrkraft kann von Beginn an die gemeinsame Sicherung öffnen. Deren Fallübersicht enthält auch die späteren Anliegen. Das Öffnen verändert weder die Entscheidung noch den Bearbeitungsstand. Die digitale Pflichtstrecke dieser Entwicklungsrunde endet mit Lauras Antwort in Abschnitt 2.

## Technische Abhängigkeiten

- `data/laura-0212.json` liefert Fallnachrichten, Aufgaben, strategienspezifische Gründe und Rückmeldungen, Fachanker, Codes, Kartenstellen, Hilfen, Wiederaufnahme und Sicherung. Der Build löst Quellenverweise auf und verwendet dieselben Daten für HTML und Work. Der Fall benutzt ausschließlich die sieben im Materialvertrag aufgeführten Strategien.
- `module/0212/beratung.js` hält die Sitzungen getrennt nach Niveau im Arbeitsspeicher. Ein Fachcheck bezieht sich auf Abschnitt, bekannte Anliegen, Niveau und vollständige Strategie. Ein Methodenwechsel oder ein neuer Abschnitt verlangt einen neuen Fachcheck. Bei einem fachlich falschen Grund gibt es eine fachliche Korrektur. Ein zutreffender Grund kann zu einem noch unvollständigen Rat gehören. Eine unter Bedingungen vertretbare Strategie bleibt wählbar.
- `module/0212/material.js` öffnet Hilfen, Rückfragen, Karten und Sicherung. Die Beantwortung einer Rückfrage erscheint im zeitlichen Verlauf des Gesprächs. Der Wechsel der Strategie aktualisiert das aktuelle Hilfe- und Fragenangebot.
- `module/0212/start.js` steuert Einstieg und Rückkehr. Die bestehende Tagesauswahl kann das Dokument über ihren MessagePort einbetten. Der Test für die gemeinsame Hülle verwendet das echte Nachrichtenmodul des 08.12. vom geprüften Commit `5d27cc3d61db386468d3f851347690b33b5d86fe`. Für eine spätere gemeinsame Freigabe den dann aktuellen Kopf des 08.12.-Zweigs vergleichen, den 02.12.-Payload integrieren und beide Modultests erneut ausführen.
- Die bisherigen Gesprächsdaten und Funktionen für Tom und Celina werden im eigenen Reservedokument weiterverwendet. Die erste freiwillige Vertiefung ist Tom, die zweite Celina. Ihre vollständige fachliche Neubewertung ist einer späteren Runde vorbehalten.

## Material und offene Erprobung

Work übernimmt die freigegebenen Aufträge, Aussagen, Hin- und Rückverweise aus dem Materialvertrag. Die HTML-Datei lässt die Lernbogen-Aussagen auf Wunsch auch digital nachlesen. Ein richtiger Buchstabe bestätigt den fachlichen Anker. Die Qualität der persönlich geschriebenen Begründung wird im Unterricht geprüft.

Für den Praxistest die Datei auf einem Schul-iPad öffnen. Je ein Förder-/ESA-Team und ein MSA-/AHR-Team möglichst selbstständig starten lassen. Beobachten, ob sie den zusätzlichen STI-Wunsch bemerken, ihre Begründung ändern und bei einer offenen medizinischen Frage eine bedingte Empfehlung formulieren können. Beim Codefeld die echte Bildschirmtastatur verwenden. Nach Neuladen über „Abschnitt auswählen“ zu Laura 2 einsteigen. Die geplanten 22 Minuten, die Passung der später gedruckten Lernbogen und der itslearning-Kurs sind unter Schulbedingungen zu erproben.

Für die Fortsetzung zuerst die Papieraufträge mit Work abstimmen. Bevor Laura 3–5 spielbar werden, muss jedes Kapitel eigene unabhängige Tests für zusätzliche Kriterien, Widerruf der Freigabe und Wiedereinstieg bestehen. Der analoge Transfer zur Pearl-Index-App bleibt eine Unterrichtsreserve.

## Prüfung erneut ausführen

Mit den Python-Abhängigkeiten aus `tests/requirements.txt` und den zugehörigen Playwright-Browsern Chromium und WebKit im selben Checkout nacheinander ausführen:

```sh
python scripts/build.py
python tests/runde1_vertrag.py
python tests/runde1_browser.py
python tests/runde1_karten.py
python tests/runde1_bestand.py
python scripts/runde1_bericht.py
```

Der Bericht vergleicht die Commit- und Dateiprüfsummen aller vier Protokolle. Das Sichtprüfungspaket ordnet die Aufnahmen dem tatsächlich geöffneten HTML zu. Der Bestandstest benötigt die Git-Historie mit den beiden angegebenen Referenzcommits.
