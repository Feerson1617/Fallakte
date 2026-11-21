# Fallakte · Prüfung der Korrekturfassung von PR #2

**Einsatzurteil.** Die Fassung ist technisch und fachlich-didaktisch für eine begleitete Erprobung vorbereitet. Der Transfer auf das Schul-iPad, der Import im konkreten itslearning-Kurs und ein Probelauf mit Lernenden stehen aus. Erprobungstermin ist der 2. Dezember 2026.

## Arbeitsfläche im eingebetteten Beratungsraum

Der Vergleich nutzt denselben Gesprächsstand in Laura, ESA. Nach zwei Vorschlägen und dem Gespräch über die Freundin öffnet das Team „Lauras Entscheidung“. Die frühere Fassung stammt aus Commit `3071562`. Beide Fassungen laufen in einem echten HTML-Frame innerhalb eines größeren Browserfensters. Die Maße beziehen sich auf den Chat-Scrollbereich einschließlich seiner Innenabstände, in gerundeten CSS-Pixeln.

| Sichtbarer Frame | Chat bei neuer Nachricht, vorher | Chat bei neuer Nachricht, jetzt | Sichtbare Chathöhe nach zweiter Hilfe, vorher → jetzt |
| --- | --- | --- | --- |
| 1366 × 768 | 610 × 480 | 731 × 716 | 406 → 716 |
| 1180 × 820 | 582 × 532 | 631 × 768 | 532 → 768 |
| 820 × 1180 | 384 × 788 | 439 × 1128 | 788 → 1128 |
| 1024 × 600 | 499 × 312 | 548 × 548 | 22 → 548 |
| 820 × 650 | 384 × 362 | 439 × 598 | 32 → 598 |
| 390 × 844 | 360 × 340 | 390 × 747 | „Antwort geben“ geöffnet, „Chat lesen“ in einem Schritt erreichbar |

Im kurzen 820er-Frame stand die Seite nach der Methodenauswahl bei 78 Pixeln. Beim Öffnen beider Hilfen sprang sie auf 563 Pixel nach unten. Jetzt bewegt sich nur der Inhalt des Antwortbereichs. Die neue Nachricht bleibt sichtbar, auch wenn beide Hilfen geöffnet sind. Der Chat gewinnt hier schon vor der Auswahl 55 Pixel Breite und 236 Pixel Höhe, rund 123.300 CSS-Quadratpixel. Mit beiden Hilfen beträgt der Gewinn an sichtbarer Chathöhe 566 Pixel. Der Antwortbereich nutzt zugleich die übrigen 381 × 598 Pixel. Die Seitenscrollposition blieb bei allen sechs Formaten in allen vier neuen Zuständen auf null.

Eine gemeinsame 52 Pixel hohe Leiste enthält Fall, Niveau, Fortschritt, Übersicht, Infokarten und Sicherung. Sie ersetzt im Gespräch den Seitenkopf, die eigene Rücksprungzeile, den Messenger-Kopf und die zusätzliche Fortschrittszeile. Der Footer und die maximale Seitenbreite entfallen im Gespräch. Auf dem Smartphone kommen zwei Umschaltflächen hinzu. Sie erhalten Nachrichten, Auswahl, Hilfen und Leseposition. Der Senden-Button besitzt einen eigenen Platz direkt unter dem scrollbaren Antwortinhalt.

**Prüfnachweise.** In Chromium und WebKit wurden dieselben vier Zustände vermessen: neue Nachricht, Auswahl mit Senden, zwei geöffnete Hilfen sowie kritische Rückmeldung mit beiden Entscheidungen. Die Prüfungen kontrollieren die Position der aktuellen Nachricht, getrennte Scrollpositionen, Sichtbarkeit und Treffbarkeit des Senden-Buttons, Textüberläufe und Touchziele ab 44 × 44 CSS-Pixeln. Zusätzlich geprüft wurden der Wechsel der Frame-Ausrichtung im Gespräch, dynamisch von 17 auf 34 Pixel vergrößerter Nachrichtentext, ein auf 410 × 325 CSS-Pixel verkleinertes Layout für 200 % Zoom und reduzierte Bewegung. Chromium prüft zusätzlich den emulierten Seitenzoom mit Faktor 2. Acht echte Bildschirmfotos der vier Zustände im 820 × 650 großen Frame stehen im Sichtprüfungspaket unter **Bildschirmfotos/Vergleich/**. **Protokolle/layout.json** enthält die Einzelmessungen und Browserstände.

## Gezielte Prüfung vor der Unterrichtserprobung

Auf dem Ausgangsstand `d08925f` blieb bei 360 Pixeln Breite mit Standardschrift das letzte „e“ von „Kombinationspille“ allein in der zweiten Zeile. Bei 390 Pixeln trat der Umbruch in WebKit bereits mit 105 % Schriftgröße auf. Die Spaltenzahl richtet sich jetzt nach der Breite innerhalb des Antwortbereichs. Bei 360 und 390 Pixeln stehen vier ganze Bezeichnungen untereinander. Bei 420 Pixeln sowie auf den geprüften iPad-Formaten passen sie bei Standardschrift in zwei Spalten. Beide Browser prüfen die tatsächlichen Textzeilen und ihre Lage im jeweiligen Button bei 360, 390 und 420 Pixeln mit 100, 105 und 110 % Schriftgröße. Sechs Bildschirmfotos stehen unter **Bildschirmfotos/Methodenfelder/**. Das Layoutprotokoll enthält die Messungen.

Beim gemeinsamen Stopp können Teams die Hilfe **Früher Stopp? Lauras Wünsche nachlesen** aufklappen. Sie zeigt kurze Fallangaben ab der gerade offenen Laura-Stufe des gewählten Niveaus. So bekommt das Team auch die aktuelle Nachricht, wenn der Stopp direkt nach deren Eintreffen kommt. Vor dem Start sind alle Fakten verfügbar. Nach dem Abschluss entfällt die Hilfe. Das Unterrichtsgespräch und der eigene Rat auf Papier bleiben Aufgabe des Teams. Die Abnahme umfasst Start, vorzeitigen Stopp mit Entwurf und zwei Hilfen, Wiederaufnahme sowie die Sicherung mit abgeschlossener und mit ausdrücklich strittiger Empfehlung. **Bildschirmfotos/Frueher-Stopp.jpg** zeigt die aufgeklappte Hilfe mitten im Fall.

## Rückmeldungen und Abschluss

Auf dem bisherigen PR-Stand (201d5f3) ließen sich beide Befunde im Browser reproduzieren. Nach einer Kupferspiralen-Empfehlung zu Lauras erster Frage und nach einer Pillenempfehlung für Tom übersprang „Nächste Nachricht“ die Auseinandersetzung mit der Antwort.

**Feedback.** Nach einer Methodenempfehlung bespricht das Team einen Grund und wählt ausdrücklich „Vorschlag beibehalten“ oder „Vorschlag ändern“. Nach einer Revision kann es beim Vorschlag bleiben oder ihn zurückziehen. Auch wenn das Team auf einer abgelehnten Methode besteht, gilt das Nein der Figur. Der Chat dokumentiert den Dissens. Bleibt das Team am Schluss bei der Pille oder einer Kombination mit Pille, steht im Abschluss „Die Empfehlung bleibt offen“. Darunter steht Lauras eigenes Nein. Bei der gemeinsamen Sicherung und beim Wiederöffnen bleibt dieser Widerspruch sichtbar. Auch Celinas ausdrücklich abgelehnte Hormone sind bei einem entsprechenden letzten Vorschlag im Abschluss erkennbar. Eine offene Frage zur Spirale bleibt dagegen offen für Beratung. Jede Entscheidung endet nach höchstens einer freien Revision. Schriftliche Gründe stehen auf Papier und werden im Gespräch beurteilt.

**Tom.** Bei Pille oder Spirale fragt Tom nach einer Methode für den eigenen Körper. Bei einer Kombination unterscheidet er seinen Anteil von der Entscheidung seiner Partnerin. Das Team kann selbst zum Kondom wechseln. Hält es an der ungeeigneten oder gemischten Empfehlung fest, benennt Tom seine eigene Möglichkeit. Das Team sieht und sendet dann einen ausdrücklich auf ihn bezogenen Kondomvorschlag. Erst danach äußert Tom den Wunsch nach weiteren Möglichkeiten und teilt den Forschungsartikel.

## Fachliche und didaktische Durchsicht

| Geprüfte Stufen | Denkhandlung und fachliche Grenze |
| --- | --- |
| Laura · Infektionsschutz und Alltag | Erstes Schutzziel, individuelle Begründung und Klassenabstimmung. Erst im nächsten Schritt kommen Schwangerschaftsschutz und Alltagsanwendung hinzu. Bei intaktem und richtig benutztem Kondom sinkt das Risiko vieler STI. |
| Laura · Erfahrung der Freundin, Entscheidung und Schmerzen | Eine mögliche Nebenwirkung erlaubt keine Vorhersage für Laura. Ihr Nein zur Pille gilt auch bei einer Kombination. Sorge vor der Einlage ist keine Absage. Bei Kupfer können Blutungen und Schmerzen zunehmen. Über die Eignung einer Spirale und die Ursache der Schmerzen lässt sich im Chat nicht entscheiden. |
| Laura · zwei Schutzziele und Schlussentscheidung | Alle vier Niveaus vergleichen zwei Strategien. Kondom allein und eine für Laura akzeptable Kombination nach Beratung lassen sich unterschiedlich begründen. In die Gewichtung gehen Anwendung, körperliche Belastung, persönliche Grenzen und beide Schutzziele ein. |
| Celina · fünf Stufen | Verzicht auf zusätzliche Hormone, längerfristiger Schutz, Bedenken zur Einlage, Schutz in der Beziehung und abschließender Vergleich bleiben getrennt. Vertrauen belegt keinen Infektionsstatus. |
| Tom · drei Stufen | Eigene Anwendung und Einverständnis der Partnerin werden unterschieden. Bei AHR bleiben die Forschungsdaten aus beiden Originalstudien im Artikel sichtbar. Schwangerschaften, Verträglichkeit, Dauer und Übertragbarkeit sind getrennt zu beurteilen. |

Die erneute Durchsicht umfasste Nachrichten, Antwortoptionen, Rückfragen, methodenspezifische Reaktionen, beide Hilfen und die Aufgaben für alle vier Niveaus. Die fachlichen Grundlagen und die mit den Originalarbeiten abgeglichenen Studienangaben sind in **Fachpruefung.md** dokumentiert. Die Methodenoptionen verwenden innerhalb einer Stufe gleichartige Formulierungen. Der Lösungshinweis zu Toms Selbstanwendung erscheint nach einem konkret gesendeten Vorschlag.

Förder arbeitet mit Satzanfängen und zwei kurzen Vergleichsfeldern. ESA verbindet Kartenwissen mit Lauras Wünschen. MSA bestimmt ein Kriterium, gewichtet es und nimmt zu einem Einwand Stellung. AHR prüft konkurrierende Kriterien, offene Annahmen und eine Bedingung für ein anderes Urteil. Die Sicherung vergleicht, wie gut Fallangaben und Fachwissen die Gründe tragen. Eine beibehaltene Methode kann am Schluss besser begründet sein.

## Ausgeführte Abnahme

- **Dialogmatrix in beiden Browsern.** Je 84 vollständige Pfade in Chromium und WebKit (drei Fälle × vier Niveaus × sieben Strategien). Je Methodenstufe wurden Einzelauswahl und Kombinationen, Vorschau und gesendeter Wortlaut, passende Rückmeldung, beide Hilfen sowie die begrenzten Rückfragen geprüft. Bei Tom umfasst der Lauf auch den Übergang zur Selbstanwendung.
- **Unabhängige Entscheidungstests.** Sechs zusätzliche Szenarien pro Browser nutzen eigenständig formulierte Erwartungen und sichtbare Bedienelemente. Sie prüfen den frühen Stopp einschließlich Niveauwechsel, wiederholte Pillenempfehlungen nach Lauras Nein, den offenen Widerspruch bei der letzten Empfehlung bis zur Sicherung und Wiederaufnahme, begründbare Spiralenberatung, Celinas Hormongrenze, Rücknahme nach Revision, zwei ungeeignete Vorschläge für Tom mit Fallwechsel und eine direkte Revision zum Kondom. Ein Vergleich mit erwarteten Texten aus der Datendatei allein würde den alten Überspringfehler übersehen.
- **Bedienung und Sitzungsdaten.** Desktop (1366 × 900), iPad-Hochformat (820 × 1180), iPad-Querformat (1180 × 820) und Mobilformat (360 × 740) je in Chromium und WebKit unter Linux. Geprüft wurden sichtbares Senden, Touchflächen, Überläufe, Karte und Artikel aus der Hilfe, Scrollen und Sprungfunktion, Erhalt früherer Vorschläge, Sicherung mitten im Fall, Fallwechsel und Wiederaufnahme. Nach Neuladen war der Chat leer. Während der Durchläufe wurden Schreibzugriffe auf Web Storage sowie Öffnungsversuche bei IndexedDB und Cache Storage überwacht. Der abschließende Vergleich prüfte Browser-Speicher und Cookies. Die Testläufe enthielten keine externen HTTP(S)-Anfragen.
- **SCORM und Offline.** Beide Browser öffneten die lokale Einzeldatei. Chromium lief offline. Unter WebKit wurden HTTP(S)-Anfragen gesperrt, da dessen Offline-Emulation auch die lokale Dateinavigation blockiert. ZIP-Prüfsummen, Manifest gegen die beigefügten XSDs, SCO-Verweis und Bytegleichheit der HTML-Dateien wurden geprüft. Im lokalen LMS-Testrahmen wurden ausschließlich LMSInitialize und LMSFinish mit leerem Argument beobachtet.
- **Druck und Sichtprüfung.** Vier druckfertige PDFs wurden erzeugt und wieder eingelesen. Jede Fassung hat genau zwei A4-Seiten, eine Hauptfallseite mit individuellem Anfangs- und Schlussurteil sowie eine Zusatzseite. Im Drucklayout wurde die Lage aller Textzeilen gegenüber Seitenrand, Textfeld und Fußzeile geprüft. Sämtliche stufenspezifischen Aufgaben und Feldbeschriftungen wurden im erzeugten PDF wiedergefunden. Die technische Sichtprüfung enthält Bildschirmfotos aus den Browsertests und JSON-Protokolle mit Prüfsummen.

## Vor dem Praxistest

1. Im Testkurs das geschlossene SCORM-ZIP importieren. Auf einem Schul-iPad in Safari senden, eine Empfehlung ändern, die Sicherung aufrufen und zu Laura zurückkehren. Auf dem Unterrichts-Mac die einzelne HTML-Datei öffnen. Browseremulation und der lokale LMS-Testrahmen decken diese schulischen Bedingungen nur teilweise ab.
2. Mit einem Förder- oder ESA-Team ohne Bedienerklärung erproben, ob „Beibehalten“, „Ändern“ und die Kartenhilfe verständlich sind. Die geplanten 18–20 Minuten für Laura und die Qualität individueller Begründungen wurden noch nicht mit einer Klasse untersucht.
3. Die passenden Laufzettel ausdrucken, Karten bereitlegen und die gemeinsame Abstimmung vorbereiten. Die Lehrkraft entscheidet über den Einsatz. Eine unabhängige medizinische Endbegutachtung steht aus.
