# Fachliche und technische Abnahme der digitalen Erarbeitungsphase

## Was die Teams gemeinsam erfahren

| Abschnitt | Fallinformation auf Förder, ESA, MSA und AHR | Fachliche Entscheidung |
| --- | --- | --- |
| 1 | Laura ist 19 und fragt nach Infektionsschutz. | Den bereits notierten ersten Rat als Einzelmethode aufgreifen. |
| 2 | Sie möchte auch eine Schwangerschaft vermeiden. Regelmäßige Handlungen vergisst sie mitunter. | Den bisherigen Rat an beiden Schutzzielen und dem Aufwand im Alltag prüfen. Ab hier ist ein Kondom zusammen mit genau einer weiteren Methode möglich. |
| 3 | Der Freundin wurde von der Pille übel. Lauras eigene Verträglichkeit bleibt offen. Sie lehnt die Pille ab, ist für andere hormonelle Methoden offen und hat Fragen zum Einsetzen einer Spirale. | Beim Lesen der Karte zwischen möglicher Nebenwirkung, persönlichem Nein und Beratungsbedarf unterscheiden. Das Nein gilt auch für die Kombination mit der Pille. |
| 4 | Laura hat oft starke Regelschmerzen. Die Ursache wurde noch nicht untersucht. Sie möchte stärkere Schmerzen vermeiden. Infektionsschutz bleibt wichtig und Laura sagt, dass ein Kondom für sie infrage kommt. | Mögliche zusätzliche Schmerzen bei der Kupferspirale und fehlenden Infektionsschutz einer Spirale allein berücksichtigen. Die Hormonspirale braucht individuelle Beratung und Lauras Zustimmung. |
| 5 | Laura möchte nach der Beratung selbst entscheiden. | Einen vorläufigen Rat begründen. Das Kondom allein bleibt vertretbar. Wer eine zweite Methode erwägt, begründet ihren zusätzlichen Nutzen und berücksichtigt Nachteile. |

Die Nachrichten zu Freundin, Pillenablehnung und Spirale stehen in einem Gesprächsschritt. Dasselbe gilt für Regelschmerzen und fortbestehenden Infektionsschutz. Die beiden zusammengeführten Abschnitte verwenden auf allen Niveaus dieselben drei kurzen Nachrichten. Die Aufgaben unterscheiden sich. Förder und ESA benennen Wünsche und Nachteile. MSA prüft die Aussagekraft des Einzelfalls und vergleicht zwei Strategien anhand konkurrierender Kriterien. AHR begründet zusätzlich, unter welcher medizinischen oder persönlichen Bedingung eine Alternative anders zu gewichten wäre. Die Anwendung bewertet offene Begründungen nicht automatisch.

## Karten, Hilfen und Bedienung

Über dem scrollbar bleibenden Antwortbereich steht bei jeder Methodenentscheidung ein fester Verweis auf die eigene Infokarte auf Papier. Auf MSA und AHR fordert er einen Beleg. Er bleibt beim Prüfen des bisherigen Rats, beim Methodenwechsel, im Entwurf, nach einer Antwort und bei der Revision sichtbar. Die Hilfe öffnet bei Bedarf direkt den genannten Abschnitt der digitalen Karte. Nach der Rückkehr stehen die bisherigen Entscheidungen und der Entwurf wieder bereit.

Die fünf freiwilligen Hilfen führen zur Kartenstelle, zur Fachinformation, zu einem Satzanfang, zu einer möglichen Begründung und zu einer ausführbaren Handlung. Im dritten Abschnitt hilft die Pillenkarte beim Unterscheiden von möglicher Nebenwirkung und sicherer Vorhersage. Im vierten unterscheiden sich die Hilfen für Kupferspirale allein und Kupferspirale mit Kondom beim Infektionsschutz. Das Öffnen eines Beispielentwurfs sendet keine Nachricht. Ein abgelehnter letzter Vorschlag bleibt als Widerspruch im Abschluss erkennbar.

## Wiederaufnahme über den Laufzettel

Im normalen Gespräch zeigt die Kopfzeile durchgehend Fallperson, Nummer und Gesamtzahl, etwa **Laura 3 von 5**. Nach einem Neustart öffnet **Nach Neustart weitermachen** eine einzige Auswahlseite. Laura ist vorausgewählt. Für Laura genügen einschließlich des Einstiegs drei Berührungen, für Celina oder Tom kommt die Wahl der Person hinzu. Die Nummer startet den Abschnitt sofort. Auch bei verlorenem Laura-Abschluss sind die Zusatzfälle auf diesem Weg erreichbar.

Der Rückblick enthält kurze Fallangaben aus den vorherigen Abschnitten. Danach folgt die reguläre Nachricht des gewählten Abschnitts. Bei Abschnitt 1 beginnt der Fall direkt mit seiner ersten Nachricht. Frühere Empfehlungen liegen nach dem Neuladen nicht vor. Eine Methodenentscheidung beginnt daher mit freier Auswahl. Erst ein in der neuen Sitzung tatsächlich beibehaltener Rat steht anschließend zur Überprüfung. Bei Tom 3 ist der zuvor eingeführte Artikel über die Zusammenfassung und die Hilfen wieder erreichbar.

Der Wiederaufnahmetest öffnet alle 52 Kombinationen aus Fallabschnitt und Niveau je Browser in der lokalen Einzeldatei im iPad-Hochformat und im extrahierten SCORM-Paket im iPad-Querformat. Laura 3 und 5 werden zusätzlich aus einem regulären Verlauf mit gesendeter Empfehlung neu geladen. Geprüft werden Nummer, bekannte Fakten, sichtbare Nachricht, fehlende Vorwahl, fünf Hilfen, Karten- und Fallrückkehr sowie Feedback und Revision. Der Test erfasst Schreibversuche in Web Storage, IndexedDB und Cookies sowie die SCORM-Aufrufe. Zwei Fotos zeigen die Auswahlseite, ein weiteres den tatsächlichen Wiedereinstieg bei Laura 3 auf Förder.

## Automatische Prüfungen an der gebauten Anwendung

- Je 84 vollständige Beratungswege in Chromium und WebKit auf den vier Niveaus. Je Browser kommen zwölf wechselnde Laura-Verläufe und sechs gezielte Entscheidungsszenarien hinzu. Der Vergleich mit dem gebauten Stand `e455e4d` prüft die medizinischen Angaben, Karten, Rückmeldungen, Hilfen und gerenderten Verläufe aller drei Fälle. Zugelassene sprachliche Änderungen lösen die Pflicht zur Partnerarbeit in den Bedienhinweisen, beim Förder-Schlussrat und bei der Bestätigung des gelesenen Artikels.
- Kartenhinweis bei freier Auswahl, Übernahme eines Rats, eingeklapptem Arbeitsauftrag, Rückmeldung und Revision. Die Layoutprüfung kontrolliert auch die Position nach Scrollen und die Sichtbarkeit bei 200 Prozent Schriftgröße auf iPad hoch, quer und im eingebetteten Fenster. Zusätzliche Prüfungen betreffen 360, 390 und 420 Pixel Breite, kleine SCORM-Fenster und Zoom.
- Auf jedem Niveau werden die fünf Hilfen in jedem der fünf Abschnitte geöffnet und die angebotenen Entwürfe auf ausbleibenden automatischen Versand geprüft. Weitere Wege umfassen Quellenaufruf, Rückkehr, Korrektur, Fallwechsel und Niveauwechsel. Die gemeinsamen UI- und Hilfekomponenten werden auch unabhängig von den Verhütungsdaten geladen.
- Je 25 simulierte Minuten ohne Bedienung in jedem Kernabschnitt. Chat, Entwurf und Arbeitsstand bleiben in der geöffneten Sitzung erhalten. Es gibt keinen Timer und keine digitale Sicherung.
- Die Offline-Datei lädt ohne externe Anfragen. Beide Browser prüfen die entpackte SCORM-Startdatei in einem Test-LMS. Manifest und Paketinhalt werden geprüft. Die Anwendung ruft nur Sitzungsbeginn und Sitzungsende auf. In den getesteten Wegen gab es keine Browser-Speicherzugriffe für Antworten oder Leistungen. Neuladen beginnt eine neue Sitzung.

## Bedienaufwand gegenüber dem früheren Sieben-Abschnitt-Stand `0891d8c`

Im direkten Weg bleibt das Team beim Kondom. Es trifft fünf fachliche Methodenentscheidungen einschließlich der drei Überprüfungen. Zuvor traf es sechs und musste zusätzlich das Gespräch über die Freundin bestätigen. Der direkte Weg benötigt auf allen Niveaus 3, 1, 1, 1 und 3 Bedienhandlungen. Eine freiwillige Korrektur von der Pille zum Kondom im ersten Abschnitt fügt auf beiden Programmständen eine Methodenentscheidung und drei Bedienhandlungen hinzu.

Gezählt wurden tatsächliche Auswahlen, Sende- und Entscheidungsaktionen im bereits geöffneten Gespräch. Die Textzählung erfasst je Abschnitt die neue Fallnachricht, den Arbeitsauftrag und einmal den Kartenhinweis. Der Kartenhinweis umfasst insgesamt 40 Wörter über fünf Abschnitte. Rückmeldungen hängen vom Vorschlag ab. Sie sind ebenso wie optionale Hilfen, Rückfragen, Schaltflächen und wiederholtes Lesen aus der Wortzählung ausgenommen. Der Vergleich beschreibt die Einstiegstexte je Entscheidung. Vollständige Klickfolgen und Einzelzählungen stehen im Sichtprüfungspaket in `Protokolle/inhaltsvergleich.json`. Der Paketbericht stellt die Ausgangszahlen und die aktuellen Messwerte nebeneinander. Mit dem wiederholten Kartenhinweis sinkt die gezählte Textmenge auf Förder, ESA und MSA leicht. Auf AHR steigt sie um drei Wörter.

## Ausstehender Praxistest

1. Das SCORM-ZIP in den schulischen itslearning-Testkurs importieren. In Safari auf einem echten Schul-iPad als lernende Person öffnen, das Gerät drehen und die Schrift vergrößern. Den Papierkartenhinweis bei einer übernommenen Empfehlung und bei der Korrektur prüfen.
2. In Abschnitt 3 einen Pillenvorschlag ändern, die Kartenstelle und alle fünf Hilfen aufrufen. Nach dem Öffnen eines Beispielentwurfs muss das Team selbst senden. Die Nummer auf Papier markieren. Nach Neuladen oder einem iPad-Neustart mit diesem Abschnitt neu beginnen. Die ersten neuen Entscheidungen und die Rückkehr über die Fallübersicht prüfen. Die Einzeldatei zusätzlich ohne WLAN öffnen.
3. Förder- und ESA-Tandems zwischen Unterrichtsminute 10 und 30 beobachten. Finden sie nach dem Neuladen allein oder zu zweit ohne Erklärung wieder zur markierten Nummer und zur passenden Papierkarte? Erkennen sie den Unterschied zwischen Lauras Nein und einer offenen Frage? Wie weit kommen sie einschließlich Lesen und mündlicher Begründung bis zum Zeichen der Lehrkraft? Der Test mit Lernenden und eine Messung der Bearbeitungszeit stehen aus.
