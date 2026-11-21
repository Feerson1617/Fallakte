# Fallakte · Verhütungsberatung

Unterrichtsanwendung für Biologie in Klasse 8. In drei fiktiven Beratungsgesprächen prüfen Lernende ihre Empfehlungen anhand von Infokarten, persönlichen Grenzen und neuen Fallinformationen. Die 19-jährige Laura ist der gemeinsame Hauptfall. Celina und Tom ergänzen ihn. Alle drei Gespräche stehen auf Förder-, ESA-, MSA- und AHR-Niveau zur Verfügung.

## Digitale Erarbeitung öffnen

Im erfolgreichen GitHub-Actions-Lauf **Unterrichtspakete** das Artefakt **Fallakte-Unterricht** herunterladen und entpacken.

| Datei | Verwendung |
| --- | --- |
| **Fallakte.html** | Direkt im Browser öffnen, auch ohne Netzwerk. Bilder, Schriften, Dialoge und Hilfen sind eingebettet. |
| **Fallakte-SCORM12.zip** | Als geschlossenes SCORM-1.2-Paket in itslearning importieren. |
| **Fallakte-Sichtpruefung.zip** | Bildschirmfotos und sieben JSON-Testprotokolle der gebauten Anwendung. |
| **Fallakte-Pruefbericht.md** | Technische Ergebnisse und ausstehende Prüfungen auf Schulgeräten. |

Alle Teams beraten zuerst die 19-jährige Laura in fünf gemeinsamen Abschnitten. Sie greifen ihren notierten ersten Einzelrat auf und prüfen ihn bei drei neuen Gesprächsanlässen. Ab dem zweiten Schutzziel können sie ein Kondom mit einer weiteren Methode kombinieren. Beim letzten Rat nennen Förder- und ESA-Teams mündlich einen Grund und einen Nachteil. MSA und AHR wägen zwei Strategien ab. Auf allen Niveaus steht die Aufforderung zur eigenen Papierkarte direkt bei der Entscheidung. Die digitalen Karten und fünf freiwilligen Hilfen unterstützen bei Bedarf. Einen vorbereiteten Entwurf versendet das Team selbst. Nach Laura stehen im selben Niveau Celina und Tom zur Wahl.

Bei einer Unterbrechung kann die Seite in jedem Gesprächsschritt geöffnet bleiben. Infokarten und Fallübersicht erlauben die Rückkehr zum Gespräch desselben Niveaus. Der Verlauf liegt nur im Arbeitsspeicher der geöffneten Seite. Nach dem Neuladen führt **Nach Neustart weitermachen** direkt zur Auswahl von Fall, Niveau und markierter Abschnittsnummer. Wer zum Beispiel **Laura 3 – Lauras Entscheidung** wählt, liest eine kurze Zusammenfassung und gibt einen eigenen Rat. In der Kopfzeile steht **Laura 3 von 5**. Auch Celina und Tom sind über diesen Zugang direkt erreichbar. Der SCORM-Adapter öffnet und schließt die technische Sitzung. Das LMS kann unabhängig davon Zugriffe protokollieren.

[Technische Abnahme und offene Punkte](docs/Abnahme.md) · [Fachquellen](docs/Fachpruefung.md)

## Entwicklung und Prüfung

**data/dialogdaten.js** enthält die fachlichen Dialoge und Karten. **data/lernhilfen.js** enthält die stufenspezifischen Hilfen. **app/app.js** verwaltet die Gespräche, **app/ui.js** und **app/lernhilfen.js** stellen die gemeinsam verwendbaren Komponenten bereit.

```sh
python scripts/build.py
python -m pip install -r tests/requirements.txt
python -m playwright install --with-deps chromium webkit
python tests/acceptance.py
python tests/lernhilfen.py
python tests/layout.py
python tests/content.py
python tests/recovery.py
python scripts/review.py
```

Die vier Ausgabedateien liegen unter **dist/**. Einzelne Testnachweise entstehen unter **build/qa/**. Der Inhaltsvergleich benötigt den Stand `e455e4d` und für den früheren Bedienvergleich `0891d8c` aus der Git-Historie. Bereits vorhandene analoge Vorlagen liegen weiterhin unter **material/**, außerhalb der Softwareausgabe.

## Vorbereitung für die zweite Fallakte am 08.12.

Eine eigene Einstiegsseite kann **app/ui.js** und **app/lernhilfen.js** direkt laden. Der Unterrichtsfall vom 02.12. verwendet dieselben Dateien. `levelText(wert, niveau)` liest gemeinsame oder stufenspezifische Texte und wird auch für situative Rückmeldungen verwendet. `renderHelp` erhält die geordneten Hilfetexte, die bereits geöffnete Stufe, den Rückruf zum Stufenwechsel und eine Quelle mit Beschriftung und Öffnungsaktion sowie optional die Handlung der letzten Stufe. Den Stand hält die aufrufende Fallakte je Gespräch und Niveau im Arbeitsspeicher. Die beiden gemeinsamen Dateien lassen sich unabhängig von den Fall- und Methodendaten laden. Das prüft ein eigener Browsertest.

Die Abschnittsauswahl in **app/wiederaufnahme.js** erhält die geordneten Fälle und Niveaus sowie eine Funktion zum Einstieg in den gewählten Abschnitt. Jede Stufe liefert ihren Titel, bei Bedarf eine kürzere Beschriftung für den Laufzettel und einen kurzen Rückblick für spätere Einstiege. Über den fachlichen Kontext und eingeführte Quellen entscheidet das jeweilige Modul.

Für die getrennte Planung am 08.12. gilt dieselbe Fallperson Laura, 19 Jahre. Der zeitliche Abstand bleibt offen. Aus der späteren ungeplanten Schwangerschaft trotz Verhütung lässt sich weder ein Anwendungsfehler noch die Unwirksamkeit einer bestimmten Methode ableiten. Dieser Planungshinweis gehört ausschließlich in die Entwicklungsdokumentation.

Für den Argumenten-Check zum Thema Schwangerschaftsabbruch kann ein separat geprüfter Gesprächsschritt eine Textpassage als Quelle und eigene Rückmeldungen für die Unterscheidung von Fakt, Wert, Norm und Schlussfolgerung liefern. Die inhaltliche Redaktion und Prüfung dieses Moduls stehen aus. Die Unterrichtsfassung für den 02.12. lädt ausschließlich den Verhütungsfall.

## Herkunft der Assets

Die drei Illustrationen zeigen künstlich erzeugte fiktive Figuren. DM Sans und DM Serif Text stammen aus Google Fonts und sind lokal als Zeichensatz für die Unterrichtstexte eingebunden. Die OFL-Lizenzen liegen in **assets/** und sind in der Einzeldatei enthalten. Die IMS-Schemas stammen aus dem [IMS-Schemaarchiv](https://www.imsglobal.org/xsd/), das ADL-Schema aus der [SCORM-1.2-Schemasammlung](https://github.com/cybercussion/SCOBot/blob/e7ddc823a39943ad48dfdfebcedb31d985409a1f/schemas/scorm12_schemas/adlcp_rootv1p2.xsd).
