"""Paketiert ausschließlich den überprüften Vorbereitungsstand."""
import argparse
import json
import subprocess
from pathlib import Path
from lxml import html
from erstellen import HERE,ROOT,OUT,START,REF,sha,pack
from pruefen import QA
from umfang import measure
from wiedereinstieg import run as touch
from feedbackpruefung import run as feedback

def dump(x):return json.dumps(x,ensure_ascii=False,indent=2)

def run(previous):
    t=touch()
    counts=feedback()
    costs=measure(previous)
    proof=json.loads((QA/'Browserpruefung.json').read_text())
    runs=proof['wege'];assert len(runs)==128 and not any(r['errors'] for r in runs)
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip()
    doc=html.fromstring((OUT/'Vorbereitung.html').read_bytes())
    assert doc.xpath('string(//meta[@name="revision"]/@content)')==head
    assert html.fromstring((previous/'Vorbereitung.html').read_bytes()).xpath('string(//meta[@name="revision"]/@content)')==START
    assert len(proof['feldbelege'])==64
    sizes=sorted({(r['breite'],r['hoehe'],r['schrift'],r['scorm']) for r in runs})
    ver={r['browser']:r['version'] for r in runs}
    pics={'Screenshots/'+p.name:p.read_bytes() for p in (QA/'Sichtbilder').glob('*.jpg')}
    scope=dict(commit=head,ausgangsstand=START,kartenreferenz=REF,wege=len(runs),bildschirmpruefungen=sum(r['count'] for r in runs),
               browser=ver,fenster=sizes,feedback=counts,kartenfelder=64,schutz=proof['bestandsdateien'],screenshots=len(pics))
    umfang=f'''# Arbeitsumfang und Unterrichtsplanung

Verglichen wurden der gebaute Stand {START[:7]} und die neue Vorbereitung ab der Niveauwahl in 1024 × 768 CSS-Pixeln. Angegeben sind der erfolgreiche Weg ohne Hilfe, alle Bildschirmtasten sowie die erstmals sichtbaren Textzeilen. Buchstaben einer Texteingabe zählen nicht als Bildschirmtasten. Eigene Erklärungen benötigen zusätzliche Denk- und Schreibzeit.

| Niveau | Aufgaben alt → neu | Freitexte alt → neu | Papierphasen alt → neu | Tasten alt → neu | Lesewörter alt → neu |
|---|---|---|---|---|---|
'''
    for row in costs:
        umfang+='| '+row['niveau']+' | '+' | '.join(f"{row['alt'][k]} → {row['neu'][k]}" for k in ('pflichtfragen','freitext','papierphasen','klicks','woerter'))+' |\n'
    umfang+='''
Für 45 Minuten sind 4 Minuten für die Orientierung, 20 Minuten für vier Methoden samt vier Papieraufträgen, 15 Minuten für die Kartenfragen mit Hilfe und 6 Minuten für Reserve und Abschluss vorgesehen. Alle beginnen bei Bedarf mit Kapitel 1. Kein zusätzliches Pflichtmaterial, keine freiwilligen Zusatzfragen. Die Zielzeiten sind noch an der Lerngruppe zu prüfen.
'''
    (OUT/'Arbeitsumfang.md').write_text(umfang)
    dev,hold=counts['entwicklung'],counts['reserve']
    report=f'''# Prüfbericht · Vorbereitung mit vier Infokarten

Geprüfter Commit `{head}` auf dem Vorbereitungszweig. Der vor der Bearbeitung mit dem entfernten Zweig abgeglichene Ausgangsstand ist `{START}`.

## Unterrichtsweg

Auf jedem Niveau führen acht kurze Informationsansichten zu vier Papieraufträgen. Vor jeder Karte erläutern zwei Bildseiten die vier einzutragenden Sachverhalte. Nummer, markierte Blatthälfte, Blattseite, Kartenname und vier einzelne Schreibzeilen benennen die Handlung. Bereits richtige Wörter bleiben stehen. Danach folgen vier Fragen in Papier-Reihenfolge. Die Lehrkraft gibt das Zeichen zum Schneiden. Ein Direkteinstieg mit vollständigem Papier und ein eigener Zeitnotweg stehen bei der Wiederaufnahme zur Verfügung.

Förder und ESA wählen Antworten. Auf MSA erklären Lernende den Zusammenhang zwischen ausbleibendem Eisprung und Befruchtung sowie zwischen Schleim und Durchtritt der Spermien. Auf AHR erläutern sie die Grenze des Kondomschutzes und die Wirkung von Kupfer trotz möglichen Eisprungs. Zwei weitere Auswahlfragen je Niveau prüfen Fehlvorstellungen. Die Lerntexte, Kartenstellen, Antwortalternativen, Begründungen und aufgabenspezifischen Hilfen sind im Vertrag gegenübergestellt. Die acht vorhandenen Funktionsskizzen zeigen Hülle, Hautkontakt, Eisprung, Einnahme, Kupfer, Schleim und mögliche Veränderungen der Blutung. Pfeile bezeichnen mögliche Veränderungen. Die Diagramme zum Schreiben zeigen ausschließlich die gesuchte Papierhälfte. Es gibt keine vorgezogene Fallberatung.

## Testergebnisse

- {len(runs)} vollständige Lernwege, alle vier Niveaus mit und ohne Fehlversuche und Hilfen. {scope['bildschirmpruefungen']} Kontrollen der gerenderten Texte, Grafiken, Tasten und Trefferflächen in Chromium {ver['chromium']} und WebKit {ver['webkit']}. Alle im Katalog geprüften Arbeitsschritte waren ohne Scrollen erreichbar. Das Sichtpaket enthält {len(pics)} echte Browseraufnahmen.
- 16 Originalkarten und alle 64 Feldlösungen mit Referenzarchiv, alten Auslieferungen sowie vier Schüler- und vier Muster-PDFs abgeglichen. Der Feldnachweis dokumentiert für jede Nummer den tatsächlich vor dem Schreiben gezeigten Text und den zugehörigen vollständigen Originalabsatz.
- Alle zwölf Auswahlfragen wurden mit jeder Antwort geprüft. Die vier lokalen Freitextmodelle wurden mit {dev['gesamt']} Entwicklungstexten geprüft, davon {dev['gleich']} entsprechend der Vorgabe klassifiziert. In der getrennt erstellten Reserve entsprachen {hold['gleich']} von {hold['gesamt']} Antworten der erwarteten Kategorie. Bei den übrigen {hold['gesamt']-hold['gleich']} blieb die Einschätzung offen. In beiden Beständen gab es {dev['falschpositiv']+hold['falschpositiv']} unberechtigte positive Rückmeldungen. Der Testkatalog enthält auch die nicht erkannten Inhalte im Wortlaut.
- Ein Browserweg prüfte wiederholte Fehlversuche, nachträglich geänderte Entwürfe, widersprüchliche und teilweise richtige Aussagen, erhaltene Hilfestufen, digitale Ersatzkarte und Selbstvergleich. Nach vollständigem Neuladen begann ein neuer Sitzungsstand. Auch das Ergänzen aller vier Karten über den Zeitnotweg vergibt keinen fachlichen Erfolg.
- Fokussierte Texteingaben wurden bei verkleinerten Arbeitsflächen in beiden Browsern geprüft. Verfügbare Höhen waren 580, 340, 240 und 285 CSS-Pixel. Der vollständige Text blieb auch nach Aufteilung, Hilfe und Selbstvergleich erhalten. Diese Messung simuliert den Platzbedarf der Bildschirmtastatur.
- Das SCORM-1.2-Manifest wurde am Schema geprüft. Das SCO initialisiert und beendet die Sitzung im lokalen LMS-Test. Die HTML-Datei im ZIP ist bytegleich mit der Offline-Datei. Es wurden keine Antworten übertragen oder dauerhaft gespeichert. Die acht bisherigen Veröffentlichungsdateien stimmen mit dem geprüften Hashmanifest überein. Die Quellpfade beider Unterrichtsbesuche wurden gegen {START[:7]} verglichen.

| Arbeitsfenster | Schrift | Auslieferung |
|---|---:|---|
'''
    for w,h,z,sco in sizes:report+=f"| {w} × {h} | {z} % | {'SCORM-Testfenster' if sco else 'Offline-HTML'} |\n"
    report+='''
## Grenzen und praktische Abnahme

Die lokale Prüfung erkennt nur bestimmte fachliche Aussagen und Beziehungen. Ungewöhnliche richtige Umschreibungen oder uneindeutige Verneinungen können zum Selbstvergleich führen. Ein erfolgreicher Vergleich ist kein automatisch bestätigter Wissensnachweis. Entwicklung und technische Prüfung erfolgten durch denselben Hauptagenten. Die getrennte Prüfreserve ersetzt keine unabhängige menschliche Bewertung.

Ein echtes Schul-iPad, die native Tastatur im produktiven itslearning-Kurs, die pädagogische Abnahme und gemessene Bearbeitungszeiten mit dieser Lerngruppe stehen aus. Für den Praxistest im Hoch- und Querformat die Infokarte 3 auf der Rückseite finden, auf MSA eine Teilantwort schreiben, bei offener Tastatur Hilfe verwenden, zurückkehren und überarbeiten. Danach vollständig neu laden und anhand des Papierstands wieder einsteigen. Beobachten, ob die Lernenden Hilfe und Lücken ohne individuelle Erklärung finden. Die Unterrichtsfreigabe folgt nach dieser Erprobung.
'''
    (OUT/'Pruefbericht.md').write_text(report)
    files={'Browserpruefung.json':(QA/'Browserpruefung.json').read_bytes(),'Touch-und-Tastatur.json':dump(t),'Feedback-Ergebnisse.json':dump(counts),
           'Kartenfelder-im-Lernweg.json':dump(proof['feldbelege']),'Arbeitsumfang.json':dump(costs),'Pruefumfang.json':dump(scope),'Pruefbericht.md':report}
    pack(OUT/'Vorbereitung-Sichtpruefung.zip',{**files,**pics})
    (OUT/'Testergebnisse.json').write_text(dump(dict(**scope,touch=t,arbeitsumfang=costs)))
    hashes={p.name:sha(p.read_bytes()) for p in sorted(OUT.iterdir()) if p.name not in ('SHA256SUMS','Buildnachweis.json')}
    (OUT/'Buildnachweis.json').write_text(dump(dict(**scope,dateien=hashes)))
    (OUT/'SHA256SUMS').write_text(''.join(sha(p.read_bytes())+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.name!='SHA256SUMS'))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('vorfassung',type=Path);run(parser.parse_args().vorfassung)
