# Abnahme und Übergabe · Fallakte Klasse 8

Korrekturzweig `korrektur/lernwege-abnahme`, ausgehend vom Integrationsstand `23c3208`. Abschlusscommit COMMIT_DES_PAKETS. Die gemeinsame Fassung ist ein Vorabkandidat für die unabhängige Unterrichtserprobung. Die eigenständigen Referenzzweige und der produktive Schulzugang wurden durch die Integration nicht verändert.

| Phase | Status, Zweig und Stand | Prüfung und Ergebnis |
| --- | --- | --- |
| A · Laura | Abgeschlossen · entwicklung/0212-neukonzeption · 5242652 · 0212-r3.1 | C prüft Barrierewirkung, STI-Risikominderung und die zusätzliche Wirkung einer Spirale. Alle fünf Abschnitte, sieben Ausgangsstrategien und vier Niveaus in beiden Browsern. Korrekturen, Freigabeentzug bei Methodenwechsel, fünf Hilfen, Rückfragen, Karten, Wiedereinstieg und frühe Sicherung. |
| B · Übungsakte | Abgeschlossen · derselbe Entwicklungszweig · ef47bdd · uebung-1.0 | Vier Situationen auf vier Niveaus in Chromium und WebKit. Falschantwort, Korrektur, Rückweg aus der Karte, Papiercode und Direkteinstieg. Die entpackte SCORM-Datei initialisiert und beendet eine LMS-Sitzung. |
| C · Tom | Abgeschlossen · derselbe Entwicklungszweig · 6753fbb und 0796b78 · tom-1.1 | Drei Abschnitte auf vier Niveaus in beiden Browsern. Ablehnung einer fremdbestimmten Methode, Quellenzugriff nach Direkteinstieg, Hilfe, Rückfrage und erneute Prüfung. Wirkungsphase der Spritzenstudie und Einzeldosisstudie von YCT-529 sind getrennt ausgewiesen. |
| D · Celina | Abgeschlossen · derselbe Entwicklungszweig · 4688ad6 und f19ce57 · celina-1.0 | Pro Browser 140 Situationen. Hormone, STI-Barriere, Einlage, Zustimmung, mehrere vertretbare Ratschläge und Methodenwechsel geprüft. Der Kartenrückweg stellt eine vorher geöffnete Hilfe wieder her. Laura und Tom wurden erneut durchlaufen. |
| E · Vorintegration | Abgeschlossen · Integrationszweig · bf79a48 · Unterrichtstag 08.12. aus 5d27cc3 | Der Tagesrahmen enthält die bytegleiche Fassung des zweiten Moduls. Beide Tageskarten, modulspezifische Navigation, getrennte Entwürfe, Reload und Wiederaufnahme sowie Start und Ende im simulierten LMS wurden im gebauten Kandidaten geprüft. |
| F · Work | Abgeschlossen · Integrationszweig · COMMIT_DES_PAKETS | Fünf JSON-Banken aus der Auslieferung werden mit den eingebetteten Daten verglichen. Die lesbaren Fassungen benennen Aufgaben, Aussagen, Lösungen, Rückmeldungen, Quellen, Papierwege und die gemeinsame Sicherung. |

## Korrekturrunde nach der unabhängigen Abnahme

Die Übungsakte (uebung-1.1) übt Vermutung, Kartenprüfung, begründete Antwort, bewusstes Senden und Gesprächsreaktion. Ein korrigierter Entwurf lässt sich erneut bearbeiten. U3 ist der einzige reguläre Papierweg für MSA und AHR. Förder und ESA bleiben im Chat. Für die Vertiefungen gelten tom-1.2 und celina-1.1. Förder und ESA sehen höchstens drei Vorschläge auf einmal; weitere sind aufklappbar. Konflikte erscheinen vor dem Fachcheck. Bei Tom 2 und 3 lesen Förder und ESA einen Auszug direkt im Gespräch. MSA und AHR öffnen den Artikel oder die Studie vor dem Fachcheck. Die Freigabe Laura → Tom → Celina gilt für das gewählte Niveau in der aktuellen Sitzung. Der direkte Abschnittseinstieg ist jederzeit möglich.

Die Browserprotokolle im Sichtprüfungs-ZIP gehören zum ausgelieferten Build. Der Inhaltsstand von Laura und die eingebettete Originalfassung des 08.12. wurden gegen die Referenz geprüft.

## Lieferumfang

- Fallakte.html und Fallakte-SCORM12.zip enthalten die gemeinsame Anwendung.
- Uebungsakte.html und Uebungsakte-SCORM12.zip sind eigenständig nutzbar.
- Work-Material.zip enthält die Übergabegrundlagen einschließlich analoger Rückfallwege.
- Fallakte-Sichtpruefung.zip enthält ausgewählte echte Bildschirmaufnahmen aus Chromium und WebKit sowie JSON-Protokolle für beide Unterrichtstage, die Zusatzfälle und die Übungsakte.
- Buildnachweis.json nennt Commit, Dateigröße und Prüfsummen. Die automatischen Tests lesen die ausgelieferten Dateien und das Manifest an der ZIP-Wurzel.

## Beobachtete technische Fehler

Toms Hilfen zum ersten Vorschlag nannten frühere Kartenüberschriften. App und Export verwenden nun für jede der sieben Strategien dieselbe passende Kartenstelle. Beim Besuch der Infokarte aus Celinas Hilfe ging die vorherige Hilfeansicht verloren. Der korrigierte Rückweg wurde auf beiden Browsern bedient. Beim ersten Integrationslauf löste der historische Git-Vergleich Pfade relativ zum Unterordner auf. Der korrigierte Prüfaufruf hat den unveränderten Referenzvergleich ausgeführt. Die lesbare 08.12.-Materialbank wurde ursprünglich erst im alten Berichtsschritt erzeugt. Der Paketbau verwendet nun dessen Originalexporter.

## Praxistest

Die Tests nutzen Chromium und WebKit mit Touch-Emulation, insbesondere 820 × 1180 und 1180 × 820 Pixel. Die ursprünglichen 08.12.-Prüfungen umfassen zusätzlich kleine Fenster und vergrößerte Schrift. Die Browserprotokolle im Sichtprüfungspaket benennen die tatsächlich benutzten Ansichten.

Vor dem Unterricht im itslearning-Testkurs beide SCOs auf einem Schul-iPad öffnen, bei eingeblendeter Tastatur einen falschen und einen richtigen Code eingeben und zum Gespräch zurückkehren. Danach neu laden und über die Abschnittsauswahl wieder einsteigen. Bei realen Förder- und ESA-Lernenden prüfen, ob sie eine Aussage selbstständig korrigieren und den Schlussrat ohne zusätzliche Erklärung biologisch begründen. Bearbeitungszeiten und Begründungsqualität wurden durch die automatisierten Durchläufe nicht gemessen.
