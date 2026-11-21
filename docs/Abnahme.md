# Technische Abnahme der digitalen Erarbeitungsphase

## Umfang

Die Anwendung umfasst Fallübersicht, Chat und Infokarten. Aus der früheren Sicherung wurden der Menüpunkt, die Seite, die stufenabhängige Laura-Zusammenfassung, die Stoppaufgaben und sämtliche Hin- und Rückwege entfernt. Auf das Zeichen der Lehrkraft kann ein Team das Gerät in jeder Gesprächsstufe ablegen. Solange die Seite geöffnet bleibt, stehen Verlauf, Entwurf und Hilfen weiterhin bereit.

Alle drei Fälle enden mit „Gespräch abgeschlossen“. Eine Ablehnung, ein zurückgezogener Vorschlag oder eine ausstehende Beratung bleiben als fachliche Ergebnisse erkennbar. Die fünf freiwilligen Hilfestufen, Methodenwechsel und der fachliche Schlussrat gehören zur Erarbeitung. Die Ausgabe umfasst Offline-HTML, SCORM 1.2, Sichtprüfungs-ZIP und diesen Bericht.

## Förder und ESA im 20-Minuten-Fenster

In L1 und L3 stehen der beibehaltene Rat und Lauras aktuelle Rückmeldung bei der neuen Nachricht. Erst das Team entscheidet über Beibehalten oder Ändern. Auch nach dem Gespräch über die Freundin in L2 bleibt der zuletzt beibehaltene Rat verfügbar. Nach einer Rücknahme beginnt die nächste Methodenentscheidung mit leerer Auswahl. Beim Schlussrat in L6 begründen die Teams ihre Wahl mündlich mit einem Fallbezug und nennen einen Nachteil. MSA und AHR bearbeiten weiterhin den Vergleich zweier Strategien.

| Gemessener Laura-Pfad | Ausgangsstand `fa3009c` | Aktuell | Ersparnis |
| --- | ---: | ---: | ---: |
| Förder / ESA · durchgehend Kondom | 15 | 11 | 4 |
| Förder / ESA · in L0 zunächst Pille, nach Lauras Rückmeldung zum Kondom korrigiert | 18 | 14 | 4 |
| MSA / AHR · dieselben beiden Wege | 15 / 18 | 15 / 18 | 0 |

Gezählt wurden tatsächliche Betätigungen im geöffneten Gespräch, vom ersten Methodenfeld bis einschließlich Abschlussentscheidung. Auf dem einfachen Förder-/ESA-Weg entfallen auf L0 bis L6 jeweils **3, 1, 1, 1, 1, 1 und 3** Betätigungen. Bei der Korrektur kommen Pillenauswahl, erstes Senden und „Vorschlag ändern“ hinzu. Niveaustart, Öffnen der Fallakte, optionale Hilfen und Kartenbesuche sind separat vom Pflichtweg. Beide Browser haben beide Programmstände im iPad-Hochformat bedient. Die Klickfolgen je Stufe stehen in **Protokolle/inhaltsvergleich.json**.

Die Messung erfasst Bedienhandlungen. Ob die Teams Lesen, Beraten und Begründen in den 20 Minuten zwischen Unterrichtsminute 10 und 30 schaffen, muss mit Förder- und ESA-Lernenden erprobt werden. Ein Team kann an jeder Stufe auf das mündliche Zeichen der Lehrkraft aufhören.

## Automatisch geprüfte Wege

| Prüfung | Ergebnis des erfolgreichen Paketlaufs |
| --- | --- |
| Fachlicher Bestand | Der Vergleich mit `fa3009c` prüft die medizinischen Falldaten, die Rückmeldungen und die Chatverläufe aller drei Fälle. Bei Förder/ESA sind die zwei neuen Prüfentscheidungen und die geänderten Organisations- und Hilfetexte berücksichtigt. Bei Celina, Tom und Laura auf MSA/AHR wurden auch die gerenderten Arbeitsaufträge und Hilfen verglichen. |
| Empfehlungen und Feedback | Je 84 Wege in Chromium und WebKit durch Laura (7 Stufen), Celina (5) und Tom (3) auf allen vier Niveaus. Zusätzlich je 12 wechselnde Laura-Verläufe und 6 Entscheidungsszenarien. Geprüft sind Einzelmethoden in L0, Kombinationen ab L1, Beibehalten, Ändern und Zurückziehen sowie der neutrale Abschluss bei ausdrücklicher Ablehnung. |
| Selbstständige Arbeit | 32 Hilfewege vor und nach einer Auswahl, bei Revision und Kartenrückkehr. Die fünfte Hilfe bereitet eine Handlung vor. Erst eine eigene Sendeaktion erzeugt eine Chatnachricht. Bei einem beibehaltenen Pillenvorschlag wurden Kartenstelle, Ablehnung in L3, fünfte Hilfe und der bewusst gesendete neue Entwurf geprüft. Die unabhängige Verwendung des Hilfepanels wurde in beiden Browsern geprüft. |
| Unterbrechen und fortsetzen | An L1, L2, L3, L4 und L5 verstrichen je 25 simulierte Minuten ohne Bedienhandlung. Stufe, Arbeitsbereich und Chat blieben erhalten. Bei Karten-, Fall- und Niveauwechsel wurden Entwürfe, Verlauf und bei Toms Artikel auch die Leseposition geprüft. |
| Anzeige | iPad hoch und quer, Desktop, Mobilansicht und unter anderem eingebettete Fenster mit 820 × 650 und 1024 × 600 CSS-Pixeln. Geprüft sind beide Scrollbereiche, Hilfezugang, Touch-Ziele, lange Methodennamen, große Schrift und Zoom. |
| Offline und SCORM | Einzeldatei ohne externe Abrufe, gültiges SCORM-Manifest und byteidentische Startdatei. Der Test-LMS registrierte nur Sitzungsbeginn und -ende. Die Browsertests prüften Speicherzugriffe und einen leeren neuen Verlauf nach dem Neuladen. |

Das Sichtprüfungspaket enthält Bildschirmfotos der gebauten Anwendung und sechs JSON-Protokolle. Jedes Protokoll nennt die Prüfsumme der getesteten HTML-Datei.

## Ausstehender Praxistest

1. Das SCORM-ZIP in den schulischen itslearning-Testkurs importieren. In Safari auf einem echten Schul-iPad als lernende Person öffnen, das Gerät drehen und auf Förder oder ESA alle fünf Hilfen bis zum Entwurf aufrufen.
2. In L3 einen Entwurf offen lassen. Nach einer Arbeitspause eine Infokarte öffnen und zurückkehren. Verlauf und Entwurf müssen noch vorhanden sein. Das Verhalten nach einer Speicherfreigabe durch iPadOS ist gesondert zu beobachten.
3. Auf dem Unterrichtsgerät die lokale HTML-Datei ohne WLAN öffnen. Mit Förder- und ESA-Lernenden erproben, ob sie Hilfe und Rückweg von der Karte selbst finden und nach einer ungeeigneten Empfehlung weiterarbeiten können.
