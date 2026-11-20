# Fallakte Verhütung – technische Vorabprüfung 0.1

Stand: 20.11.2026. **Prototyp, keine Unterrichtsfreigabe.**

## Tatsächlich implementiert
- Standalone-HTML ohne Server, externe Bibliotheken oder Netzwerkabfragen.
- Vier Niveaus: Förder, ESA, MSA, AHR; 3 Fälle: Laura, Celina und Tom.
- Alle bekannten Einzelfälle und die Kombination mit Kondom bleiben auswählbar.
- Acht bestehende Strategien werden durch vier Methodenfelder und ein neutrales Zusatzfeld abgebildet (kein Lösungs-Highlight).
- Vollständige selbständig anwachsende Messenger-Verläufe mit auswählungsabhängigen Reaktionen.
- Einmalige Revision einer Empfehlung pro Dialogstufe; auch bei offener Frage kann es weitergehen.
- Zwei kontextbezogene Hilfen, sofern sie in der ursprünglichen Datenvorlage vorliegen.
- Lesbarer Artikel und bei AHR ein aufklappbarer Forschungs-/Studienbereich bei Tom.
- Chat kann nach oben gescrollt werden; bei neuen Nachrichten erscheint ein Sprung-zum-Ende-Knopf. Beim Wechsel zur nächsten Stufe erfolgt Scrollen zur neuen Nachricht.
- Kein automatisches Freitext-Scoring. Inhalte existieren nur bis zum Neuladen in der laufenden Sitzung.
- Optionales SCORM-1.2-Initialisieren und Abschließen ohne Schreiben von Antworten, Noten, Lernständen oder persönlichen Daten.

## Reproduzierbare Browsertests
- Chromium / Desktop 1024 x 768: Laura in allen vier Stufen von Start bis Abschluss durchgeklickt, inkl. Zurücknehmen einer Pillenempfehlung und Auswahl einer kombinierten Strategie.
- Chromium / schmale Ansicht 390 x 844: Tom AHR, eingebetteter Artikel und Studie sichtbar, Weiterblättern.
- Chromium / Tablet-Hochformat 834 x 1112: Celina von Anfang bis Ende.
- Keine JavaScript-Laufzeitfehler in den ausgeführten Testläufen.
- Strukturtest: 15 Dialogstufen; alle benötigten Schlüssel für Optionen, Reaktionen und Hilfen liegen vor.

## Wichtige Grenzen
1. **Nicht auf echten Schul-iPads, in Safari oder in itslearning geprüft.** Chromium-Browsertests sind kein Ersatz.
2. Keine unabhängige medizinische Endabnahme sämtlicher Quelltexte im App-Test vorgenommen.
3. Die bisherigen Druckmaterialien / Laufzettel sowie Einstiegsaushänge enthalten teilweise noch den alten Laura-Fall (zunächst Schwangerschaftssicherheit und Pille). Sie sind vor einem Einsatz auf die neue Eingangssituation (STI-Schutz und Kondom als naheliegende Einzelmethode) abzustimmen.
4. Laura ist noch nicht durch reale Lernende bearbeitet worden. Lesezeit, Bedienbarkeit und 20-Minuten-Fenster sind ungeprüft.
5. Die erste Abstimmung, das Empfehlungsrad und der Lernzuwachsvergleich erfolgen bewusst außerhalb der Web-App auf Papier beziehungsweise gemeinsam an der Tafel.
6. Die vorformulierte Option „erst eine Frage klären“ wird als offene Frage dokumentiert, aber nicht semantisch beantwortet. Eine zukünftige Version kann gezielte Rückfragen als vorprogrammierte Dialogknoten aufnehmen.
7. Die AHR-Studien sind übertragene Inhalte des ursprünglichen Pakets. Ihre Quellen und fachlichen Grenzen müssen vor einem echten Einsatz erneut nachvollzogen werden.
8. Im SCORM-Testpaket sind keine Datenfelder für Noten oder Lernfortschritte befüllt. Die Plattform selbst kann dennoch Zugriffs-/Sitzungsdaten führen.
9. HTML enthält die aufbereiteten Unterrichtstexte, nicht die originalen Material-PDFs. Die Infokarten werden als Papiermaterial benötigt.

## Konkrete nächste Entwicklungsschritte
1. Laura-Einstieg, Reaktionen und Hilfen gemeinsam pädagogisch prüfen: Aus anfänglich einer klar naheliegenden STI-Schutzmethode sollen zwei oder mehr begründbare Gesamtstrategien entstehen.
2. Einstieg und Laufzettel der neuen Falllogik anpassen.
3. UI mit 2–3 Lernenden testen, darunter mindestens eine Person, die häufig Hilfe braucht. Ohne Lehrererklärung beobachten, wo Fragen entstehen.
4. Mit Schul-iPads und itslearning den SCORM-Kandidaten testen. Für den Unterrichtsversion Änderungen und Wiederholungen aus dem Test einarbeiten.
5. Erst anschließend die Endabnahme für die Stunde am 02.12. durchführen.