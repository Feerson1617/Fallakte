# Fallakte Laura · Korrekturrunde 1b

## Entwicklungsstand und Einstieg

Arbeitszweig `entwicklung/0212-neukonzeption`. Grundlage der Korrekturen ist der am 22.11.2026 ausgelieferte Zwei-Abschnitt-Prototyp auf Commit `8c6bd80c7aa636b55e50ef7522c63f9b48df0cb8`, Inhaltsbank `0212-r1.1`, Actions-Lauf `45046241473`. Der ursprüngliche Zweig begann auf `ec94147fd8d61442305a0281f7df032f3162362c`.

- **Abschlusscommit der Auslieferung** · siehe `Materialvertrag.json`, Feld `buildCommit`.
- **Inhaltsbankversion** · `0212-r1.2`

Mit `python scripts/build.py` entstehen unter `dist/Runde-1/` die eigenständige `Fallakte.html`, der maschinenlesbare und der lesbare Materialvertrag sowie diese Fortsetzungsdokumentation. Die HTML-Datei direkt im Browser öffnen. Für den Weg am Gerät die Stufe wählen und bei Laura „Neu beginnen“ antippen. „Abschnitt auswählen“ führt mit einer Zusammenfassung direkt zu Laura 2. „Weiterarbeiten“ führt zum tatsächlichen Entwurf dieses Niveaus im noch geöffneten Dokument.

## Umfang der Erprobung

| Abschnitt | Stand und fachliche Leistung |
| --- | --- |
| Laura 1 – Latexallergie | Spielbar. Die Lerngruppe unterscheidet Material und Methode. Eine zutreffende erste Empfehlung lässt sich biologisch präzisieren oder bestätigen. |
| Laura 2 – Zwei Schutzziele | Spielbar. Das neu genannte STI-Anliegen verlangt eine erneute Prüfung der vollständigen Strategie. Eine Methode mit gutem Schwangerschaftsschutz kann allein das zweite Ziel offenlassen. |
| Laura 3 – Hormone und Alltag | Als Materialvertrag spezifiziert. Die regelmäßige Einnahme, Lauras Tagesablauf und die begrenzte Übertragbarkeit der Erfahrung ihrer Freundin werden relevant. |
| Laura 4 – Schmerzen und Einlage | Als Materialvertrag spezifiziert. Mögliche Wirkungen auf Schmerzen, ärztliche Abklärung und die eigene Entscheidung über die Einlage sind getrennte Kriterien. |
| Laura 5 – Mein Schlussrat | Als Materialvertrag spezifiziert. Der Schlussrat und die analoge Sicherung nutzen ein gemeinsames Schreibfeld. Die Begründung wird mit dem ersten Rat verglichen. |

Für die gemeinsame Sicherung am Seitenfuß „Für die Lehrkraft“ aufklappen und „Gemeinsame Sicherung öffnen“ wählen. Die Übersicht enthält auch Lauras spätere Anliegen. Die Lehrkraft kann sie schon während Laura 1 projizieren, etwa wenn die Erarbeitung früher endet. Beim Schließen kehrt die Lerngruppe zu ihrem bisherigen Bearbeitungsstand zurück. Die digitale Pflichtstrecke endet mit Lauras Antwort in Abschnitt 2.

## Was sich mit Runde 1b für die Bearbeitung ändert

| Situation | Verhalten im korrigierten Prototyp |
| --- | --- |
| Start von Laura 1 | Förder erhält die Materialinformation direkt. ESA untersucht die Latexfrage mit einem konkreten Hinweis. MSA und AHR prüfen die Bedeutung für den eigenen Rat. Auf diesen drei Niveaus heißen die unbestätigten Wahlmöglichkeiten zunächst „Kondom“ beziehungsweise „Kondom und …“. |
| Auswahl einer Strategie | Der Arbeitsimpuls wechselt mit dem Entwurf. Bei der Kupferspirale steht die Wirkung von Kupfer auf Spermien im Mittelpunkt. Bei Kombinationen sind die Beiträge beider Methoden und die zugehörigen Kartenstellen erreichbar. |
| Fehlendes STI-Schutzziel in Laura 2 | Förder und ESA können eine ausdrücklich angebotene Ergänzung wählen. MSA und AHR erhalten einen Bewertungsimpuls und wählen selbst, wie sie ihren Rat ändern. Jeder geänderte Rat benötigt einen neuen Fachcheck. |
| Papierarbeit auf MSA und AHR | Der reguläre Weg führt zum genannten Abschnitt auf dem Laufzettel und zurück zur Codeeingabe. Wer das Blatt nicht zur Hand hat, kann den Denkauftrag mit sämtlichen Aussagen digital öffnen. |
| Direkter Wiedereinstieg | Die Abschnittsauswahl übernimmt genau einmal den Titel aus der Inhaltsbank. Laura 1 und Laura 2 sind auswählbar. |

Der fachliche Vorher-Nachher-Bericht und das Sichtprüfungspaket im Actions-Artefakt dokumentieren die Korrekturen am gebauten HTML. Die vier technischen JSON-Protokolle darin nennen den geprüften Commit und die HTML-Prüfsumme.

## Technische Abhängigkeiten

- `data/laura-0212.json` liefert Fallnachrichten, Aufgaben, strategienspezifische Gründe und Rückmeldungen, Fachanker, Codes, Kartenstellen, Hilfen, Wiederaufnahme und Sicherung. Der Build löst Quellenverweise auf und verwendet dieselben Daten für HTML und Work. Der Fall benutzt ausschließlich die sieben im Materialvertrag aufgeführten Strategien.
- `module/0212/beratung.js` hält die Sitzungen getrennt nach Niveau im Arbeitsspeicher. Ein Fachcheck bezieht sich auf Abschnitt, bekannte Anliegen, Niveau und vollständige Strategie. Ein Methodenwechsel oder ein neuer Abschnitt verlangt einen neuen Fachcheck. Bei einem fachlich falschen Grund gibt es eine fachliche Korrektur. Ein zutreffender Grund kann zu einem noch unvollständigen Rat gehören. Eine unter Bedingungen vertretbare Strategie bleibt wählbar.
- `module/0212/material.js` öffnet Hilfen, Rückfragen, Karten und Sicherung. Die Beantwortung einer Rückfrage erscheint im zeitlichen Verlauf des Gesprächs. Der Wechsel der Strategie aktualisiert das aktuelle Hilfe- und Fragenangebot.
- `module/0212/start.js` steuert Einstieg und Rückkehr. Die bestehende Tagesauswahl kann das Dokument über ihren MessagePort einbetten. Der Test für die gemeinsame Hülle verwendet das echte Nachrichtenmodul des 08.12. vom geprüften Commit `5d27cc3d61db386468d3f851347690b33b5d86fe`. Für eine spätere gemeinsame Freigabe den dann aktuellen Kopf des 08.12.-Zweigs vergleichen, den 02.12.-Payload integrieren und beide Modultests erneut ausführen.
- Die bisherigen Gesprächsdaten und Funktionen für Tom und Celina werden im eigenen Reservedokument weiterverwendet. Die erste freiwillige Vertiefung ist Tom, die zweite Celina. Ihre vollständige fachliche Neubewertung ist einer späteren Runde vorbehalten.

## Material und offene Erprobung

Work übernimmt Aufgaben, Begründungsoptionen und Hin- und Rückverweise aus dem Materialvertrag. Der Export unterscheidet den Einstieg vor der Wahl vom konkreten Arbeitsimpuls nach der Wahl. Ein richtiger Buchstabe bestätigt den fachlichen Anker. Die Qualität der persönlich geschriebenen Begründung wird im Unterricht geprüft.

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
