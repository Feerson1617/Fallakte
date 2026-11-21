# Fallakte · Verhütungsberatung

Unterrichtsanwendung für Biologie in Klasse 8. In drei fiktiven Beratungsgesprächen prüfen Lernende ihre Empfehlungen anhand von Infokarten, persönlichen Grenzen und neuen Fallinformationen. Laura ist der gemeinsame Hauptfall. Celina und Tom ergänzen ihn. Alle drei Gespräche stehen auf Förder-, ESA-, MSA- und AHR-Niveau zur Verfügung.

## Für den Unterricht öffnen

Im erfolgreichen GitHub-Actions-Lauf **Unterrichtspakete** das Artefakt **Fallakte-Unterricht** herunterladen und die äußere Download-ZIP entpacken.

| Datei | Verwendung |
| --- | --- |
| **Fallakte-SCORM12.zip** | Als SCORM-1.2-Paket in itslearning importieren. Diese innere ZIP geschlossen lassen. |
| **Fallakte.html** | Auf dem Mac per Doppelklick im Browser öffnen. Alle Bilder, Schriften, Dialoge und Infokarten sind eingebettet. |
| **Fallakte-Lehrkraft.pdf** | Seite 1 erst beim Stopp zentral zeigen oder vorlesen. Seite 2 dient zum Vergleich der individuellen Begründungen. |
| **Fallakte-Sichtpruefung.zip** | Enthält dieselbe HTML-Vorschau, echte Bildschirmfotos, einen Prüfbericht und maschinenlesbare Testprotokolle. |

**Fallakte-Pruefbericht.md** bündelt die Abnahme, Fachquellen, curriculare Zuordnung und Unterrichtsplanung für denselben Programmstand.

Das zweite Artefakt **Fallakte-Laufzettel** enthält vier Schüler-PDFs (Förder, ESA, MSA, AHR). Jede Fassung hat zwei A4-Seiten. Hinweise zur Moderation der Abstimmungen und zur Auswertung stehen separat im Unterrichtsablauf.

Auch im ausgecheckten Projekt lässt sich **index.html** direkt öffnen. Hierbei gehören die benachbarten Ordner zur Vorschau. Das einzelne weiterzugebende Offline-Dokument entsteht im Build.

## Im Klassenraum

Laura öffnen, die erste Empfehlung auf Papier begründen und gemeinsam abstimmen. Der Verlauf führt in sieben Abschnitten zur zweiten Empfehlung. Chat und Antworten haben eigene Scrollbereiche. Auf schmalen Displays wechselt das Team mit **Chat lesen** und **Antwort geben** zwischen beiden. Frühere Antworten, Änderungen und Rückfragen bleiben im Chat lesbar. **Sicherung** unterbricht jeden Fall sofort. Die Sicherung zeigt die bereits erreichten Angaben zu Laura. Beim gemeinsamen Stopp stellt die Lehrkraft die übrigen Angaben mit ihrer Folie bereit. Alle Teams vergleichen dann zwei Vorschläge auf dem Laufzettel. Über **Zurück** oder die Fallübersicht lässt sich die Arbeit derselben Stufe fortsetzen.

Die Anwendung hält die Gespräche ausschließlich im Arbeitsspeicher der geöffneten Seite. Neuladen beginnt eine neue Sitzung. Sie verlangt keine Namen oder persönlichen Erfahrungen. Der SCORM-Adapter öffnet und schließt lediglich die technische Sitzung. itslearning kann unabhängig davon Zugriffe protokollieren.

[Unterrichtsablauf für die Lehrkraft](docs/Unterricht.md) · [Fachquellen](docs/Fachpruefung.md) · [Abnahme und offene Punkte](docs/Abnahme.md)

## Entwicklung und Prüfung

**data/dialogdaten.js** enthält die freigegebenen Fälle, Methodeninformationen, Rückfragen, Antworten und fachlichen Hinweise. **data/lernhilfen.js** ordnet jeder Gesprächsstufe eine Einstiegskarte oder den bereits geteilten Artikel und je einen Satzanfang pro Niveau zu. Sie enthält ein Datenobjekt, das auch direkt über das lokale Dateisystem geladen werden kann. **app/app.js** verwaltet die Sitzungen und rendert die Ansichten. **index.html** und **app/style.css** bilden die Oberfläche.

Der Build verwendet nur Python 3. Die folgenden Befehle im Repository-Stamm bauen und prüfen die Unterrichtsausgabe. Druckausgabe und Prüfungen nutzen Playwright, lxml und pypdf in der Entwicklungsumgebung.

```sh
python scripts/build.py
python -m pip install -r tests/requirements.txt
python -m playwright install --with-deps chromium webkit
python tests/acceptance.py
python tests/lernhilfen.py
python tests/layout.py
python scripts/worksheets.py
python tests/worksheets.py
python tests/content.py
python scripts/review.py
```

Die Unterrichtsdateien liegen in **dist/**, die vier PDFs in **dist/Laufzettel/**. Die Sichtprüfung lässt sich erst nach erfolgreichen Tests des identischen HTML-Stands packen. Der Layoutvergleich verwendet den vorherigen PR-Stand `3071562` aus der Git-Historie. Die CI führt diese Schritte auch für Pull Requests aus.

## Vorbereitung für die zweite Fallakte am 08.12.

Eine eigene Einstiegsseite kann **app/ui.js** und **app/lernhilfen.js** direkt laden. Der Unterrichtsfall vom 02.12. verwendet dieselben Dateien. `levelText(wert, niveau)` liest gemeinsame oder stufenspezifische Texte und wird auch für situative Rückmeldungen verwendet. `renderHelp` erhält die geordneten Hilfetexte, die bereits geöffnete Stufe, den Rückruf zum Stufenwechsel und eine Quelle mit Beschriftung und Öffnungsaktion. Den Stand hält die aufrufende Fallakte je Gespräch und Niveau im Arbeitsspeicher. Die beiden gemeinsamen Dateien lassen sich unabhängig von den Fall- und Methodendaten laden. Das prüft ein eigener Browsertest.

Für den Argumenten-Check zum Thema Schwangerschaftsabbruch kann ein separat geprüfter Gesprächsschritt eine Textpassage als Quelle und eigene Rückmeldungen für die Unterscheidung von Fakt, Wert, Norm und Schlussfolgerung liefern. Die inhaltliche Redaktion und Prüfung dieses Moduls stehen aus. Die Unterrichtsfassung für den 02.12. lädt ausschließlich den Verhütungsfall.

## Herkunft der Assets

Die drei Illustrationen zeigen künstlich erzeugte fiktive Figuren. DM Sans und DM Serif Text stammen aus Google Fonts und sind lokal als Zeichensatz für die Unterrichtstexte eingebunden. Die OFL-Lizenzen liegen in **assets/** und sind in der Einzeldatei enthalten. Die IMS-Schemas stammen aus dem [IMS-Schemaarchiv](https://www.imsglobal.org/xsd/), das ADL-Schema aus der [SCORM-1.2-Schemasammlung](https://github.com/cybercussion/SCOBot/blob/e7ddc823a39943ad48dfdfebcedb31d985409a1f/schemas/scorm12_schemas/adlcp_rootv1p2.xsd).
