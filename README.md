# Fallakte. Zwei Unterrichtstage

Die Anwendung startet mit „Wähle deinen Unterrichtstag.“ Beide Datumsfelder zeigen dieselbe 19-jährige Laura. Am 02.12. öffnet sich die kompakte Fallübersicht. Am 08.12. prüfen die Lernenden vier Nachrichten an Laura.

| Auslieferung in GitHub Actions | Verwendung |
| --- | --- |
| **Fallakte-Version-A-02-12** | Für den 02.12. ist die erste Karte aktiv und die zweite mit einem Schloss gekennzeichnet. Das Paket enthält ausschließlich das erste Unterrichtsmodul. |
| **Fallakte-Version-B-08-12** | Beide Karten lassen sich öffnen. Am 08.12. sind Mutter und Freundin die Pflichtstrecke. Großmutter und Vater sind direkt zugängliche Reserven. |
| **Fallakte-Nachrichten-08-12** | Sichtprüfung, Prüfbericht und vollständige Materialübergabe für Work zum zweiten Tag. |
| **Fallakte-Abnahme** | Gemeinsamer Prüfbericht und Sichtprüfungs-ZIP mit Bildschirmfotos, JSON-Protokollen und der Abnahme des eingebetteten Moduls vom 02.12. |

Im gewählten Versionsordner **Fallakte.html** direkt im Browser öffnen oder **Fallakte-SCORM12.zip** als geschlossenes Paket in das LMS importieren. Alle benötigten Bilder, Schriften und Moduldokumente sind eingebettet. Beide Pakete haben eigene SCORM-Kennungen.

## Tageswechsel und Bestandsschutz

Die gemeinsame Leiste öffnet **Tagesauswahl**, **Fallakten**, **Infokarten** und **Nach Neustart** auch aus einer laufenden Beratung. Im Gespräch zeigt sie Fallperson, Abschnitt und Niveau. Der Tageswechsel blendet das geöffnete Modul aus. Beim erneuten Antippen des Tages öffnet sich dieselbe Ansicht mit dem bisherigen Entwurf, Verlauf und Hilfestand. „Nach Neustart“ öffnet die Abschnittsauswahl. Erst das Antippen eines konkreten Abschnitts beginnt diesen neu. „Zurück“ bricht die Auswahl ab.

Das einzeln geöffnete Dokument **02-12.html** und seine Offline-Datei **build/02-12/Fallakte.html** verwenden ihre bisherige Kopfzeile. Die gemeinsame Leiste übernimmt die Navigation, sobald das Modul eine Verbindung zum Tagesmenü hat.

Die Quelldatei **index.html** ist die Tagesauswahl und öffnet in der Entwicklung die A-Fassung. **02-12.html** enthält die Fallübersicht des ersten Moduls. Der unabhängige Vergleich mit `ca77bf7` schützt Falldaten, Hilfe, Entscheidung, Rückmeldung, Wiedereinstieg und Abschluss. Der Referenzbau berücksichtigt die geprüften Änderungen an der Fallübersicht und die Anbindung an die gemeinsame Leiste. Beide Auslieferungen müssen genau das daraus entstandene Dokument einbetten. Die Prüfungen schützen die beiden Tageskarten gegenüber `c1e5ce6`. Ein weiterer Referenzbau schützt die gesamte A-Fassung und die B-Fassung außerhalb des neuen Moduldokuments gegenüber `ec94147`. Bildschirmfotos und Höhenmessungen vergleichen die Navigation mit dem Stand `41504cc`.

Der Compiler für Version B verbindet die Vorlage in **module/08-12/** mit dem gemeinsamen UI-Code, lokalen Schriften, Lauras Porträt und der aufgelösten Aufgabenbank. **build/08-12/Fallakte.html** lässt sich auch direkt öffnen. Die beiden Module haben getrennte Dokumente und Arbeitsspeicher. Das Tagesmenü verwaltet die SCORM-Sitzung.

### Schnittstelle für die Modulnavigation

Module mit eigener Rückfallleiste sind an ihrer Tageskarte mit `data-modulnavigation` gekennzeichnet. Das Menü zeigt ihren Inhalt nach der Übernahme der Navigation. Es sendet dem geladenen Modul die Nachricht `fallakte:navigation` mit einem eigenen `MessagePort`. Das Modul nimmt sie vom direkten Elternfenster an. Über den Port meldet es einmal `{type: "ready", actions: [{id, label, icon}]}` und bei einem Ansichtswechsel `{type: "view", active, status}`. Bei Aktivierung einer Schaltfläche erhält es deren ID und führt die Navigation mit seinem eigenen Sitzungsstand aus. Die Tagesauswahl gehört zum Rahmen. Das Nachrichtenmodul meldet „Nachrichten“, „Fachkarten“ und „Nach Neustart“ an.

## Bauen und prüfen

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
python tests/tagesauswahl.py
python scripts/tagesbericht.py
```

Unter **dist/Version-A/** und **dist/Version-B/** liegen die jeweiligen HTML- und SCORM-Dateien, unter **dist/** der gemeinsame Bericht und das Sichtprüfungspaket. Mit `python scripts/build.py --version A` lässt sich die erste Auslieferung auch eigenständig bauen. Die Prüfungen benötigen die Git-Historie mit den Referenzständen `940138e`, `ca77bf7` und `c1e5ce6`.

## Unterrichtstag am 02.12.

Alle Teams beraten zuerst die 19-jährige Laura in fünf gemeinsamen Abschnitten. Sie greifen ihren notierten ersten Einzelrat auf und prüfen ihn bei drei neuen Gesprächsanlässen. Ab dem zweiten Schutzziel können sie ein Kondom mit einer weiteren Methode kombinieren. Beim letzten Rat nennen Förder- und ESA-Teams mündlich einen Grund und einen Nachteil. MSA und AHR wägen zwei Strategien ab. Auf allen Niveaus steht die Aufforderung zur eigenen Papierkarte direkt bei der Entscheidung. Die digitalen Karten und fünf freiwilligen Hilfen unterstützen bei Bedarf. Ohne Auswahl passen Kartenstelle und Beispielmethode zusammen. Bei einem Methodenvergleich erklärt das Beispiel, wie die Kartenangabe den Rat begründet. Jede Person arbeitet auf ihrem eigenen iPad im eigenen Niveau. Einen vorbereiteten Entwurf versendet das Team selbst. Celina und Tom sind freiwillige Zusatzfälle für die Zeit nach Laura. Beide sind auf jedem Niveau direkt erreichbar, auch nach einem Neustart.

Bei einer Unterbrechung kann die Seite in jedem Gesprächsschritt geöffnet bleiben. Infokarten und Fallübersicht erlauben die Rückkehr zum Gespräch desselben Niveaus. Der Verlauf liegt nur im Arbeitsspeicher der geöffneten Seite. Nach dem Neuladen führt **Nach Neustart** im gewählten Unterrichtstag direkt zur Auswahl von Fall, Niveau und markierter Abschnittsnummer. Wer zum Beispiel **Laura 3 – Lauras Entscheidung** wählt, liest eine kurze Zusammenfassung und gibt einen eigenen Rat. In der Kopfzeile steht **Laura 3 von 5**. Auch Celina und Tom sind über diesen Zugang direkt erreichbar. Der SCORM-Adapter öffnet und schließt die technische Sitzung. Das LMS kann unabhängig davon Zugriffe protokollieren.

[Technische Abnahme und offene Punkte](docs/Abnahme.md) · [Fachquellen](docs/Fachpruefung.md)

## Nachrichten am 08.12.

Alle acht Abschnitte stehen unmittelbar offen. Pro Person gibt es einen Argumenten-Check und drei nummerierte Fragen. Das Ergebnis verbindet eine Kartenstelle, Lauras eigene Worte und eine begründete Einschätzung. Die Rolle von Familienhilfe und Zukunftsplänen wird in „Freundin 2“ geprüft. Unter „Zu zweit auf zwei Niveaus“ kann ein Paar den gemeinsamen Grundweg bearbeiten. Den Auftrag zum Urteil lesen alle in kurzen Sätzen. „Weiterdenken“ enthält die zusätzlichen Fragen für MSA und AHR. Die Erklärung kann mündlich, auf dem persönlichen Lernbogen oder am iPad erfolgen. Innerhalb der Sitzung bleibt der Entwurf beim Niveauwechsel erhalten. „Nach Neustart“ öffnet auch jede der drei Teilfragen direkt. Hilfe 1 bis 5 bezieht sich auf das ausgewählte Feld oder die aktuelle Denkfrage.

`python scripts/build.py` baut beide Auslieferungen. Nach der Installation der Abhängigkeiten aus **tests/requirements.txt** und der beiden Playwright-Browser prüft `python tests/nachrichten.py` die zweite Fallakte. Anschließend erzeugt `python scripts/nachrichtenbericht.py` Bericht, Sichtprüfung und Work-Paket in **dist/**. Die fachlichen Belege, die Zeitplanung und der ausstehende Praxistest stehen im [Prüfvermerk](docs/Nachrichten-08-12.md).

## Herkunft der Assets

Die drei Porträts zeigen künstlich erzeugte fiktive Figuren. Das Gruppenbild in der Tagesauswahl wurde mit dem freigegebenen Laura-Porträt als Bildreferenz erstellt. DM Sans und DM Serif Text stammen aus Google Fonts und sind lokal als Zeichensatz für die Unterrichtstexte eingebunden. Die OFL-Lizenzen liegen in **assets/** und sind in der Einzeldatei enthalten. Die IMS-Schemas stammen aus dem [IMS-Schemaarchiv](https://www.imsglobal.org/xsd/), das ADL-Schema aus der [SCORM-1.2-Schemasammlung](https://github.com/cybercussion/SCOBot/blob/e7ddc823a39943ad48dfdfebcedb31d985409a1f/schemas/scorm12_schemas/adlcp_rootv1p2.xsd).
