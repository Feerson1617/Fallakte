"""Erzeuge nach den Browserprüfungen die vollständige Übergabe aus demselben Build."""
import argparse
import json
import math
import subprocess
from pathlib import Path
from lxml import html
from erstellen import HERE,ROOT,OUT,START,REF,sha,pack
from pruefen import QA
from umfang import measure
from wiedereinstieg import run as restart


def run(ref):
    restart()
    costs=measure(ref)
    (QA/'Arbeitsumfang.json').write_text(json.dumps(costs,ensure_ascii=False,indent=2))
    records=json.loads((QA/'Browserpruefung.json').read_text())
    runs=records['wege'];assert len(runs)==128 and not any(r['errors'] for r in runs)
    digest=sha((OUT/'Vorbereitung.html').read_bytes())
    head=html.parse(str(OUT/'Vorbereitung.html')).xpath('string(//meta[@name="revision"]/@content)')
    assert head==subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    report='''# Arbeitsumfang und Zeitplanung

Verglichen wurden der gebaute Referenzstand 562ea25 und die neue Offline-Anwendung. Beide Wege beginnen bei der sichtbaren Niveauwahl und enden beim Abschluss. Gemessen wird ein vollständiger Weg ohne Fehler und Hilfen im iPad-Querformat mit 1024 × 768 CSS-Pixeln. Eine Eingabe eines Buchstabens zählt als eine Handlung. Ein Bildschirmwechsel ist jede Änderung des sichtbaren Wortlauts im Arbeitsbereich, einschließlich eingeblendeter Rückmeldung. Die gemeinsame Tagesauswahl der alten Auslieferung ist nicht mitgezählt.

| Niveau | Pflichtfragen alt → neu | Bedienhandlungen alt → neu | Bildschirmwechsel alt → neu | Lesewörter alt → neu | Lesezeit alt → neu |
|---|---:|---:|---:|---:|---|
'''
    def interval(n):return str(math.ceil(n/120))+'–'+str(math.ceil(n/80))+' min'
    for row in costs:
        old,new=row['alt'],row['neu']
        report+='| '+('Förder' if row['niveau']=='Foerder' else row['niveau'])+' | '+' | '.join(str(old[k])+' → '+str(new[k]) for k in ('fragen','bedienhandlungen','bildschirmwechsel','lesewoerter'))+' | '+interval(old['lesewoerter'])+' → '+interval(new['lesewoerter'])+' |\n'
    taps=[r['taps'] for r in runs if not r['assist']]
    report+='''
Die Lesemenge umfasst erstmals sichtbare Textzeilen einschließlich der angebotenen Aussagen. Identische, erneut angezeigte Zeilen zählen einmal. 80–120 Wörter pro Minute sind eine Planungsannahme für das Lesen. Bildbetrachtung, Nachdenken und erneutes Lesen kommen hinzu. Im kleinen Fenster trennen sich bei Platzbedarf Bildinformation und Antwortwahl. Über alle geprüften Fenster und Schriftgrößen lag der fehlerfreie Weg bei '''+str(min(taps))+'–'+str(max(taps))+''' Bedienhandlungen.

**Papier.** Früher waren bereits acht Abschnittsmarkierungen und acht Eintragungsphasen angeleitet. Hinzu kamen vier erneute Kartenkontrollen, ein Zwischenstopp und der Schlussvergleich. Auf MSA und AHR gehörten vier begründete Papier-Fachchecks mit Buchstabeneingabe dazu. Die Zahl tatsächlicher Handgriffe der Klasse wurde am 26.11. nicht gemessen. Jetzt gibt es genau vier angeleitete Papierphasen, jeweils einmal nach einer Methode. Das sind vier Hinwege und vier Rückwege. Auf dem ganzen Kartenblatt sind höchstens 16 Lösungswörter bzw. kurze Wortgruppen einzutragen. Richtige Einträge bleiben stehen. Es gibt keine weiteren schriftlichen Pflichtantworten.

**Didaktische Auswahl.** Eine Frage zum Pearl-Index und zwei Entscheidungen je Methode ergeben neun Pflichtfragen für alle Niveaus. Die erste erschließt die biologische Wirkung, die zweite Anwendung oder Grenzen. Schwangerschaftsschutz und STI-Schutz werden getrennt behandelt. Individuelle Verträglichkeit, mögliche Beschwerden und Zustimmung werden in den Situationen für Pille und Spiralen konkret. Förder benennt Vorgänge im Bild, ESA wendet die Information angeleitet an, MSA erklärt Zusammenhänge und AHR prüft Schlussfolgerungen und vergleicht. Nach einer geöffneten Lösung zeigt die Software die Erklärung zur gewählten Antwort. Den fachlichen Transfer übernimmt der reguläre Weg. Ein zusätzlicher Aufgabenblock entfällt.

**Planung für 45 Minuten.** 2 Minuten für Start und Niveauwahl, 4 Minuten für den Pearl-Index, viermal 5 Minuten für Bild, Information und die beiden Entscheidungen sowie viermal 2 Minuten für das Kartenblatt ergeben 34 Minuten. Weitere 6 Minuten sind für Fehlversuche und Hilfen vorgesehen, 5 Minuten als Reserve. Wer schon eine Karte vollständig bearbeitet hat, kann direkt ins nächste offene Kapitel einsteigen. Bei Zeitnot sind die Musterkarten separat erreichbar. Eine ausgefüllte Karte bescheinigt keinen digitalen Erfolg. Die Zeiten sind Unterrichtsplanung. Wie viel Zeit die konkrete Lerngruppe tatsächlich braucht, ist offen.
'''
    (OUT/'Arbeitsumfang.md').write_text(report)
    sizes=sorted({(r['breite'],r['hoehe'],r['schrift'],r['scorm']) for r in runs})
    summary=dict(softwarecommit=head,letzter_entwicklungsstand=START,kartenreferenz=REF,html_sha256=digest,
        browser={r['browser']:r['version'] for r in runs},durchlaeufe=len(runs),
        zustandskontrollen=sum(r['count'] for r in runs),methoden=4,niveaus=4,fachfragen_je_niveau=9,
        muster=16,feldvergleiche=64,bildschirmgrenzen_fehler=0,
        fenster=[dict(breite=w,hoehe=h,schrift_prozent=z,format='SCORM' if l else 'HTML') for w,h,z,l in sizes],
        originaldateien=records['bestandsdateien'])
    assert len(records['feldbelege'])==64
    (QA/'Kartenfelder-im-Lernweg.json').write_text(json.dumps(records['feldbelege'],ensure_ascii=False,indent=2))
    (QA/'Pruefumfang.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    vergleich=records['umfang_gegen_88ec053']
    text=f'''# Technischer Prüfbericht · Vorbereitung für vier Methoden

Softwarecommit `{head}` auf `entwicklung/vorbereitung-vier-kapitel`. Der zuletzt abgeschlossene Entwicklungsstand ist `{START}`. Die fachliche Referenz der Vorbereitung ist `{REF}`.

## Endkorrektur gegenüber 88ec053

- Jede reguläre Frage zeigt Kapitel und Fragenposition. Ein Häkchen kennzeichnet in der Kapitelauswahl die im gewählten Niveau und in dieser Sitzung abgeschlossenen Kapitel. Ein vollständiges Neuladen löscht den Sitzungsstand.
- Beim erneuten Öffnen zeigt die Hilfe die zuletzt gelesene Stufe dieser Frage. Die nächste Frage beginnt bei Stufe 1. Beim Pearl-Index auf AHR geht es um die Bedingungen beider Studien. Die Pillenhilfen unterscheiden eigene Verträglichkeit und fremde Erfahrung. Die Hilfe zum Einsetzen der Kupferspirale unterscheidet ärztliche Eignung und persönliche Zustimmung.
- Unklare Fragen nennen jetzt den biologischen Gegenstand. Die erste Kapitelauswahl erklärt STI. Auf MSA und AHR prüfen die Antwortalternativen unter anderem den Unterschied zwischen Zykluswirkung und Erregerschutz sowie die Grenzen eines Vergleichs. Fragen und Antwortoptionen zusammen umfassen auf MSA {vergleich['MSA']['frage_und_optionen_woerter_neu']} statt {vergleich['MSA']['frage_und_optionen_woerter_alt']} Wörter, auf AHR {vergleich['AHR']['frage_und_optionen_woerter_neu']} statt {vergleich['AHR']['frage_und_optionen_woerter_alt']}. Je Frage sind sowohl die gesamte Hilfekette als auch ihr längster Einzeltext höchstens so lang wie in 88ec053. Es bleiben neun Pflichtfragen und vier Papierphasen je Niveau.
- Der Papierauftrag nennt das Kapitel, Vorder- oder Rückseite und die Position. Die vier fett gedruckten Wörter gehören in die jeweils gleich nummerierte Lücke. Bereits richtig eingetragene Wörter bleiben stehen. Die Reihenfolge entspricht dem Kartenblatt. Nach einer über den Zeitnotweg ergänzten Karte erscheint wieder die Musterkartenauswahl.
- Für jedes der 64 Felder nennt das Protokoll „Kartenfelder-im-Lernweg.json“ das Original-Lösungswort und die tatsächlich angezeigte Stelle im Lerntext oder in der Rückmeldung vor der Papierphase. Die vollständige Musterkarte und freiwillige Hilfen zählen für diesen Nachweis nicht mit.

## Ergebnisse am gebauten Unterrichtsprogramm

- {len(runs)} vollständige instrumentierte Wege in Chromium {summary['browser']['chromium']} und WebKit {summary['browser']['webkit']}, alle vier Niveaus, je Fenster ein direkter Weg und ein Weg mit Fehlantwort sowie allen fünf Hilfen. {summary['zustandskontrollen']} Prüfzeitpunkte einschließlich digitaler Musterkarten. Alle Textbereiche, Grafiken und Schaltflächen lagen innerhalb des sichtbaren Ausschnitts. Die Mitte jedes Knopfs war per Treffertest erreichbar. Mindest-Touchfläche 44 × 44 CSS-Pixel, sichtbarer Schülertext ab 16 CSS-Pixeln bei Normalschrift.
- In allen regulären Aufgabenansichten blieb „Ich brauche Hilfe“ am oberen rechten Rand. Die Prüfung öffnete die Hilfe erneut auf Stufe 2, nach einer Fehlantwort auf Stufe 3 und nach der richtigen Antwort auf Stufe 5. Auch ein Umweg über eine Musterkarte erhielt die Antwort und Hilfestufe. Bei knappem Platz gibt es kurze Lese-, Auswahl- und Rückmeldeseiten. Alle vier Wörter der Papierphase stehen gleichzeitig auf derselben Seite. Dort ist „Karte fertig – weiter“ die einzige Schaltfläche.
- Eigenständige Wege mit echten Touchaktionen prüften Niveauwahl, direkten Einstieg in ein bereits begonnenes Kapitel, Rückkehr nach einer unterbrochenen Auswahl und vollständiges Neuladen. Jeder Neustart beginnt ohne behaupteten digitalen Erfolg. Die Musterkarten zeigen alle fünf geprüften Textabschnitte und den Pearl-Index je Methode. Nach vier auf diesem Weg ergänzten Karten bleibt die Zahl digital bearbeiteter Kapitel null.
- Der Abgleich ordnete die 64 Lösungsfelder aller 16 Karten den acht PDFs (vier Schüler- und vier Referenzfassungen) zu. Er verglich jeden vollständigen Kartentext, die Lückentexte und die Pearl-Werte mit dem geprüften Vorbereitungsstand. Die Druckanweisung für Work beschreibt Vorder-/Rückseite, oberes/unteres Feld und die durchgehende Nummerierung. Work gestaltet das endgültige Blatt nach der Abnahme.
- SCORM 1.2 wurde im lokalen LMS-Testfenster geladen und ordnungsgemäß beendet. Das Manifest ist schema-validiert. Die eingebettete index.html ist bytegleich mit der Offline-Datei. Die Auslieferung enthält nur die Vorbereitung. Im Browser wurden keine externen Unterrichtsressourcen, Cookies oder dauerhaften Lernantworten festgestellt. Da alle Antworten angetippt werden, gibt es kein Eingabefeld für eine Bildschirmtastatur.
- Die acht bisherigen HTML-/SCORM-Auslieferungen wurden unabhängig mit dem Manifest des abgeschlossenen Entwicklungsstands verglichen. Ihre SHA-256-Werte stehen in Pruefumfang.json. Die zuvor ausgelieferte Vorbereitungsfassung ist als Rückfallversion unter dem bisherigen Branch und im bestehenden Lieferpaket verfügbar. Die neuen Bedienelemente bestehen als eigenständige Ansichten für Aufgabe, Hilfe und Kartenübertragung. Die beiden Unterrichtsbesuche verwenden weiterhin ihren abgenommenen Stand.

## Fenster der Abnahme

| Arbeitsfläche (CSS-Pixel) | Schrift | Auslieferung |
|---|---:|---|
'''
    for w,h,z,l in sizes:text+=f"| {w} × {h} | {z} % | {'SCORM im Lernplattform-Testfenster' if l else 'Offline im Vollfenster'} |\n"
    text+='''
## Noch praktisch zu prüfen

Die am 26.11. beobachtete Überforderung betrifft die alte Fassung. Für die neue Fassung sind ein echtes Schul-iPad, die tatsächliche Einbettung in itslearning und ein erneuter Durchlauf mit der heterogenen Lerngruppe offen. Am Schulgerät ein Kapitel im Hoch- und Querformat öffnen, Schrift vergrößern, eine falsche Wahl antippen, Hilfe öffnen und schließen. Beim dritten Kapitel das Blatt wenden. Nach vollständigem Neuladen den Einstieg anhand der teilweise ausgefüllten Karte finden. Im Unterricht beobachten, ob insbesondere Förder- und ESA-Lernende die Hilfe selbst finden, die biologischen Erklärungen verstehen und die eine Papierphase je Kapitel ohne Nachfrage bewältigen. Zeit vom Start bis zur letzten tatsächlich bearbeiteten Karte erfassen. Erst danach über die Unterrichtsfreigabe und eine Übertragung der Oberfläche auf die UB-Module entscheiden.
'''
    (OUT/'Pruefbericht.md').write_text(text)
    files={p.name:p.read_bytes() for p in QA.glob('*.json') if p.name in ('Browserpruefung.json','Arbeitsumfang.json','Wiedereinstieg.json','Pruefumfang.json','Kartenfelder-im-Lernweg.json')}
    files.update({'Screenshots/'+p.name:p.read_bytes() for p in (QA/'Bilder').glob('*.jpg')})
    files['Pruefbericht.md']=text;pack(OUT/'Vorbereitung-Sichtpruefung.zip',files)
    (OUT/'Buildnachweis.json').write_text(json.dumps(dict(**summary,dateien={p.name:sha(p.read_bytes()) for p in sorted(OUT.iterdir()) if p.name not in ('Buildnachweis.json','SHA256SUMS')}),ensure_ascii=False,indent=2))
    (OUT/'SHA256SUMS').write_text(''.join(sha(p.read_bytes())+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.name!='SHA256SUMS'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('bestand',type=Path);run(parser.parse_args().bestand)
