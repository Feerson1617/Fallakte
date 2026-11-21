# Fallakte · Verhütungsberatung

Unterrichtsanwendung für Biologie in Klasse 8. In drei fiktiven Beratungsgesprächen prüfen Lernende ihre Empfehlungen anhand von Infokarten, persönlichen Grenzen und neuen Fallinformationen. Die 19-jährige Laura ist der gemeinsame Hauptfall. Celina und Tom ergänzen ihn. Alle drei Gespräche stehen auf Förder-, ESA-, MSA- und AHR-Niveau zur Verfügung.

## Digitale Erarbeitung öffnen

Im erfolgreichen GitHub-Actions-Lauf **Unterrichtspakete** das Artefakt **Fallakte-Unterricht** herunterladen und entpacken.

| Datei | Verwendung |
| --- | --- |
| **Fallakte.html** | Direkt im Browser öffnen, auch ohne Netzwerk. Bilder, Schriften, Dialoge und Hilfen sind eingebettet. |
| **Fallakte-SCORM12.zip** | Als geschlossenes SCORM-1.2-Paket in itslearning importieren. |
| **Fallakte-Sichtpruefung.zip** | Bildschirmfotos und sechs JSON-Testprotokolle der gebauten Anwendung. |
| **Fallakte-Pruefbericht.md** | Technische Ergebnisse und ausstehende Prüfungen auf Schulgeräten. |

In Laura greift das Team den auf dem persönlichen Laufzettel notierten Einzelrat auf. Ab der zweiten Gesprächsstufe kann es auch das Kondom mit einer weiteren Methode kombinieren. Der Hilfezugang führt bei Bedarf von einer Kartenstelle bis zu einem ausführbaren nächsten Schritt. Ein vorbereiteter Entwurf wird erst durch „Nachricht senden“ verschickt.

Bei einer Unterbrechung kann die Seite in jedem Gesprächsschritt geöffnet bleiben. Infokarten und Fallübersicht erlauben die Rückkehr zum Gespräch desselben Niveaus. Der Verlauf liegt nur im Arbeitsspeicher der geöffneten Seite. Neuladen beginnt eine neue Sitzung. Der SCORM-Adapter öffnet und schließt die technische Sitzung. Das LMS kann unabhängig davon Zugriffe protokollieren.

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
python scripts/review.py
```

Die vier Ausgabedateien liegen unter **dist/**. Einzelne Testnachweise entstehen unter **build/qa/**. Der Inhaltsvergleich benötigt den Commit `fc9b01c` aus der Git-Historie. Bereits vorhandene analoge Vorlagen liegen weiterhin unter **material/**, außerhalb der Softwareausgabe.

## Vorbereitung für die zweite Fallakte am 08.12.

Eine eigene Einstiegsseite kann **app/ui.js** und **app/lernhilfen.js** direkt laden. Der Unterrichtsfall vom 02.12. verwendet dieselben Dateien. `levelText(wert, niveau)` liest gemeinsame oder stufenspezifische Texte und wird auch für situative Rückmeldungen verwendet. `renderHelp` erhält die geordneten Hilfetexte, die bereits geöffnete Stufe, den Rückruf zum Stufenwechsel und eine Quelle mit Beschriftung und Öffnungsaktion sowie optional die Handlung der letzten Stufe. Den Stand hält die aufrufende Fallakte je Gespräch und Niveau im Arbeitsspeicher. Die beiden gemeinsamen Dateien lassen sich unabhängig von den Fall- und Methodendaten laden. Das prüft ein eigener Browsertest.

Für die getrennte Planung am 08.12. gilt dieselbe Fallperson Laura, 19 Jahre. Der zeitliche Abstand bleibt offen. Aus der späteren ungeplanten Schwangerschaft trotz Verhütung lässt sich weder ein Anwendungsfehler noch die Unwirksamkeit einer bestimmten Methode ableiten. Dieser Planungshinweis gehört ausschließlich in die Entwicklungsdokumentation.

Für den Argumenten-Check zum Thema Schwangerschaftsabbruch kann ein separat geprüfter Gesprächsschritt eine Textpassage als Quelle und eigene Rückmeldungen für die Unterscheidung von Fakt, Wert, Norm und Schlussfolgerung liefern. Die inhaltliche Redaktion und Prüfung dieses Moduls stehen aus. Die Unterrichtsfassung für den 02.12. lädt ausschließlich den Verhütungsfall.

## Herkunft der Assets

Die drei Illustrationen zeigen künstlich erzeugte fiktive Figuren. DM Sans und DM Serif Text stammen aus Google Fonts und sind lokal als Zeichensatz für die Unterrichtstexte eingebunden. Die OFL-Lizenzen liegen in **assets/** und sind in der Einzeldatei enthalten. Die IMS-Schemas stammen aus dem [IMS-Schemaarchiv](https://www.imsglobal.org/xsd/), das ADL-Schema aus der [SCORM-1.2-Schemasammlung](https://github.com/cybercussion/SCOBot/blob/e7ddc823a39943ad48dfdfebcedb31d985409a1f/schemas/scorm12_schemas/adlcp_rootv1p2.xsd).
