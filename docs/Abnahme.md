# Fachliche und technische Abnahme für den 02.12.2026

## Vereinfachte Fallübersicht gegenüber `c1e5ce6`

„Nach Neustart weitermachen“ befindet sich in der Kopfzeile der Übersicht. Niveauwahl, Laura und Arbeitsauftrag stehen vor den kleineren Zusatzfallkarten. Die geöffneten Fälle liegen im Arbeitsspeicher der Sitzung. Nach dem Neuladen öffnet die Fallkarte direkt Abschnitt 1. Über die Abschnittsnummer lässt sich die Arbeit bei Laura, Celina oder Tom auch später fortsetzen.

Die folgende fachliche Abnahme beschreibt die bereits im Referenzstand `ca77bf7` geprüften Hilfen. Der aktuelle UI-Vergleich und die Bilder vor und nach der Umstellung stehen im gemeinsamen Paketbericht.

## Korrekturen an den fünf Hilfestufen im fachlichen Referenzstand

Bei einer leeren Auswahl nennen Fundstelle und Beispiel dieselbe Methode. Bei einem eigenen Vorschlag bleibt seine Karte für die Prüfung verfügbar. Wenn die Beispielbegründung zu einer anderen Methode übergeht, erklärt sie zuerst, was die gelesene Karte für diesen Fall bedeutet. Die fünfte Hilfe öffnet den dazugehörigen Entwurf. Das Senden erfolgt durch die lernende Person.

| Abschnitt | Änderung und fachlicher Bezug |
| --- | --- |
| Laura 1 | Der Förder-Satzanfang führt vom Infektionsschutz zum eigenen Vorschlag. Wer eine Pille oder Spirale prüft, erfährt, warum im Beispiel ein Kondom erwogen wird. Es senkt das Risiko vieler Infektionen. |
| Laura 2 | Ohne Auswahl beginnt die Hilfe bei der Anwendung des Kondoms. Nach einer Auswahl erklärt der Vergleich den Unterschied zwischen regelmäßiger Pilleneinnahme, einer medizinischen Einlage und der Anwendung beim Sex. |
| Laura 3 | Ohne Auswahl zeigt die Kondomkarte, wie das Kondom angewendet wird. Das Beispiel respektiert Lauras Nein zur Pille und ihre offene Frage zur Spirale. Bei einem Pillenvorschlag führt die Nebenwirkungsangabe zum Unterschied zwischen der Erfahrung der Freundin und Lauras eigener Verträglichkeit. MSA und AHR greifen diese Schlussgrenze auch im Einstiegsbeispiel auf. |
| Laura 4 | Die Kondomkarte verbindet die unveränderte Periode mit dem weiter gewünschten Infektionsschutz. Bei der Kupferspirale bleiben mögliche stärkere Schmerzen, bei der Hormonspirale die individuelle Eignung und bei der Pille Lauras Nein maßgeblich. |
| Laura 5 | Beim letzten Rat erklärt die Vergleichshilfe, welche Grenze der gewählten Methode für Laura zählt. Das Kondom allein bleibt begründbar. MSA und AHR wägen weiterhin zwei Strategien und Bedingungen für eine Alternative ab. |
| Celina 1 bis 5 | Bei freier Auswahl beginnt die Hilfe in den Abschnitten 1, 3, 4 und 5 beim Kondom. In Abschnitt 2 führt sie von der Kupferspiralen-Karte zum Beispiel für längeren Schutz. Die gewählte Karte bestimmt den Vergleich zu Hormonen, Anwendungsaufwand, Einlage oder Infektionsschutz. Bei einer kombinierten Empfehlung wird auch der zusätzliche Aufwand berücksichtigt. |
| Tom 1 bis 3 | Der Methodenvergleich ordnet Tom und seiner Freundin die jeweilige körperliche Anwendung zu. Bei den beiden Artikelaufgaben führen Fundstelle, Sachhinweis, Satzanfang und Beispiel weiterhin zur passenden Lese- oder Schreibaufgabe. Die letzte Hilfe lenkt den Fokus auf deren vorhandene Schaltfläche. |

Die Förder- und ESA-Aufträge in Lauras mittleren Abschnitten benennen die anstehende Prüfung jeweils direkt. Der ESA-Schlussrat verlangt einen Grund und einen Nachteil. Jede Person kann auf ihrem eigenen iPad im eigenen Niveau arbeiten. Ein Austausch ist freiwillig.

Nach einer gesendeten Revision stehen Beibehalten und Zurückziehen zur Wahl. In diesem Zustand bezieht sich die vierte Hilfe auf den tatsächlich gesendeten Rat. Bei einem erkannten Widerspruch wie der abgelehnten Pille begründet sie eine mögliche Rücknahme mit der Fachinformation. Bei einer anderen vertretbaren Empfehlung benennt sie die gewählten Methoden und die Einschränkung des Rats. Die fünfte Hilfe fokussiert die entsprechende Schaltfläche. Erst ein weiterer bewusster Tastendruck trifft die Entscheidung.

Der Paketbericht führt die geänderten Texte am Ende im Wortlaut auf. Bei einer Vergleichshilfe werden der Eintrag zur gelesenen Methode und der Beispielrat des Abschnitts nacheinander angezeigt. Für wiederholt gesendete Vorschläge lauten die neuen Einleitungen „Ich ziehe meinen Rat zurück.“ bzw. „Mein Rat mit [Methoden] bleibt vorläufig.“ Darauf folgt die zur Auswahl gehörende Fachinformation. Die gekürzten Handlungshinweise nennen den jeweiligen Entwurf oder die erreichbare Schaltfläche.

## Technische Abnahme

- Der Vergleich mit der gebauten Referenz `940138e` prüft Fallinformationen, Altersangaben, Methodenkarten, Artikel, Fragen, Antwortmöglichkeiten, persönliche Grenzen, Rückmeldungen und die Rückblicke zur Wiederaufnahme. Die geänderten Aufträge und Hilfetexte sind im Protokoll `inhaltsvergleich.json` mit Abschnitt sowie altem und neuem Wortlaut erfasst.
- Chromium und WebKit durchlaufen jeweils 84 vollständige Dialogwege, zwölf wechselnde Laura-Verläufe und sechs Entscheidungsszenarien. Die Hilfekettenprüfung öffnet alle fünf Stufen vor der Auswahl, bei jeder Einzelmethode und Kombination, nach der ersten Rückmeldung, bei der Revision und nach der zweiten Rückmeldung. Hinzu kommen die Überprüfung eines übernommenen Rats, Toms eigener Beitrag und seine beiden Artikelaufgaben. Bei jeder Ausführung der letzten Hilfe werden Chat und Abschnitt auf unbeabsichtigtes Senden oder Weiterschalten geprüft.
- Die 52 möglichen Abschnittseinstiege werden je Browser in der lokalen HTML-Datei im iPad-Hochformat und im entpackten SCORM-Paket im iPad-Querformat geprüft. Nach Neuladen bei Laura 3 und 5 beginnt die Auswahl leer. Der Rückblick enthält die früheren Fallangaben. Auch die Zusatzfälle sind direkt erreichbar. Direkte Rückkehr von Karten, Übersichts- und Niveauwechsel sowie der Artikel bei Tom 3 gehören zum Test.
- Die Layoutprüfung umfasst Papierkartenhinweis, Hilfezugang, sichtbare Nachricht, Bedienelemente, getrennte Scrollbereiche, 200 Prozent Schriftgröße, schmale Ansichten und kleine eingebettete Fenster. Die Arbeit kann in allen fünf Laura-Abschnitten auf das mündliche Zeichen der Lehrkraft unterbrochen werden.
- Offline-HTML und SCORM-Startdatei sind bytegleich. Geprüft werden auch Manifest, externe Anforderungen, Web Storage, IndexedDB, Cookies und die SCORM-Aufrufe. Im Test-LMS werden ausschließlich Sitzungsbeginn und -ende gemeldet. Die Anwendung speichert weder Schülerantworten noch Leistungen dauerhaft.

## Bedienaufwand gegenüber `940138e`

Gezählt werden Betätigungen nach dem Öffnen von Laura bis zur Schlussentscheidung. Beim durchgängigen Kondomvorschlag sind es auf jedem Niveau neun Betätigungen für fünf fachliche Entscheidungen. Eine Korrektur im ersten Abschnitt ergibt zwölf Betätigungen für sechs Entscheidungen. Der Ausgangsstand und der Release-Kandidat werden über ihre sichtbaren Schaltflächen bedient. Die ergänzende Wortzählung umfasst je Abschnitt die neue Fallnachricht, den Auftrag und einmal den Kartenhinweis. Die Lesezeit im Unterricht wurde noch nicht gemessen.

## Ausstehender Praxistest

1. Die SCORM-ZIP in den schulischen itslearning-Testkurs importieren. Mit Safari auf einem echten Schul-iPad auf Förder oder ESA die Hilfe vor und nach einer unpassenden Empfehlung öffnen, das Gerät drehen und die Schrift vergrößern.
2. Laura 3 auf Papier markieren, die Seite neu laden und über die Nummer zurückkehren. Einen korrigierten Entwurf prüfen, bewusst senden und die Reaktion lesen. Die Einzeldatei zusätzlich ohne WLAN öffnen.
3. Mit Förder- und ESA-Lernenden beobachten, ob sie auf ihrem eigenen Gerät ohne Erklärung von der Kartenstelle zum begründeten Rat gelangen. Einzelarbeit und freiwilligen Austausch zulassen. Für Lesen, Entscheiden und Begründen steht im Unterricht das Fenster von Minute 10 bis 30 zur Verfügung.
