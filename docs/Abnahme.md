# Technische Abnahme der digitalen Erarbeitungsphase

## Umfang

Die Anwendung umfasst Fallübersicht, Chat und Infokarten. Aus der früheren Sicherung wurden der Menüpunkt, die Seite, die stufenabhängige Laura-Zusammenfassung, die Stoppaufgaben und sämtliche Hin- und Rückwege entfernt. Auf das Zeichen der Lehrkraft kann ein Team das Gerät in jeder Gesprächsstufe ablegen. Solange die Seite geöffnet bleibt, stehen Verlauf, Entwurf und Hilfen weiterhin bereit.

Alle drei Fälle enden mit „Gespräch abgeschlossen“. Eine Ablehnung, ein zurückgezogener Vorschlag oder eine ausstehende Beratung bleiben als fachliche Ergebnisse erkennbar. Die fünf freiwilligen Hilfestufen, Methodenwechsel und der fachliche Schlussrat gehören zur Erarbeitung. Die Ausgabe umfasst Offline-HTML, SCORM 1.2, Sichtprüfungs-ZIP und diesen Bericht.

Bei doppelter Schriftgröße in einem 820 × 650 Pixel großen WebKit-Fenster verdrängten die Hilfeschaltflächen den Text der geöffneten Hilfe. Die Schaltflächen dürfen jetzt auf mehrere Zeilen umbrechen. Der Layouttest misst die sichtbare Höhe des Hilfetexts und prüft die Erreichbarkeit aller Hilfeschaltflächen sowie der Sendetaste.

## Automatisch geprüfte Wege

| Prüfung | Ergebnis des erfolgreichen Paketlaufs |
| --- | --- |
| Fachlicher Bestand | Gegen den separat gebauten Stand `fc9b01c` wurden Falldaten, Hilfetexte und alle 84 vollständigen Gesprächswege verglichen. Aus den Falldaten entfielen ausschließlich die sieben Zusammenfassungen und die Stoppaufgaben. Die beiden wiederverwendbaren Skripte wurden zusätzlich byteweise geprüft. |
| Empfehlungen und Feedback | Je 84 Wege in Chromium und WebKit durch Laura (7 Stufen), Celina (5) und Tom (3) auf allen vier Niveaus. Zusätzlich je 12 wechselnde Laura-Verläufe und 6 Entscheidungsszenarien. Geprüft sind Einzelmethoden in L0, Kombinationen ab L1, Beibehalten, Ändern und Zurückziehen sowie der neutrale Abschluss bei ausdrücklicher Ablehnung. |
| Selbstständige Arbeit | 32 Hilfewege vor und nach einer Auswahl, bei Revision und Kartenrückkehr. Die fünfte Hilfe bereitet eine Handlung vor. Erst eine eigene Sendeaktion erzeugt eine Chatnachricht. Die unabhängige Verwendung des Hilfepanels wurde in beiden Browsern geprüft. |
| Unterbrechen und fortsetzen | An L2, L3 und L4 verstrichen je 25 simulierte Minuten ohne Bedienhandlung. Stufe, Arbeitsbereich und Chat blieben erhalten. Bei Karten-, Fall- und Niveauwechsel wurden Entwürfe, Verlauf und bei Toms Artikel auch die Leseposition geprüft. |
| Anzeige | iPad hoch und quer, Desktop, Mobilansicht und unter anderem eingebettete Fenster mit 820 × 650 und 1024 × 600 CSS-Pixeln. Geprüft sind beide Scrollbereiche, Hilfezugang, Touch-Ziele, lange Methodennamen, große Schrift und Zoom. |
| Offline und SCORM | Einzeldatei ohne externe Abrufe, gültiges SCORM-Manifest und byteidentische Startdatei. Der Test-LMS registrierte nur Sitzungsbeginn und -ende. Die Browsertests prüften Speicherzugriffe und einen leeren neuen Verlauf nach dem Neuladen. |

Das Sichtprüfungspaket enthält Bildschirmfotos der gebauten Anwendung und sechs JSON-Protokolle. Jedes Protokoll nennt die Prüfsumme der getesteten HTML-Datei.

## Ausstehender Praxistest

1. Das SCORM-ZIP in den schulischen itslearning-Testkurs importieren. In Safari auf einem echten Schul-iPad als lernende Person öffnen, das Gerät drehen und auf Förder oder ESA alle fünf Hilfen bis zum Entwurf aufrufen.
2. In L3 einen Entwurf offen lassen. Nach einer Arbeitspause eine Infokarte öffnen und zurückkehren. Verlauf und Entwurf müssen noch vorhanden sein. Das Verhalten nach einer Speicherfreigabe durch iPadOS ist gesondert zu beobachten.
3. Auf dem Unterrichtsgerät die lokale HTML-Datei ohne WLAN öffnen. Mit Förder- und ESA-Lernenden erproben, ob sie Hilfe und Rückweg von der Karte selbst finden und nach einer ungeeigneten Empfehlung weiterarbeiten können.
