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
from externpruefung import browserwege

def dump(x):return json.dumps(x,ensure_ascii=False,indent=2)

def run(previous):
    t=touch()
    externe_wege=browserwege()
    counts=feedback(previous)
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
    scope=dict(externe_browserwege=len(externe_wege),commit=head,ausgangsstand=START,kartenreferenz=REF,wege=len(runs),bildschirmpruefungen=sum(r['count'] for r in runs),
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
    reserve=counts['kontrollreserve']['satz']['kontrollreserve']
    extern=counts['extern']
    alle=counts['gesamt']['satz']
    fp=sum(v.get('falsch_positiv',0) for v in alle.values())
    fn=sum(v.get('ungerechtfertigt_negativ',0) for v in alle.values())
    assert fp==fn==0,(fp,fn)
    assert all(v>=200 for v in counts['verschiedene_texte'].values())
    assert all(x['alt']['klicks']==x['neu']['klicks'] and x['alt']['freitext']==x['neu']['freitext'] for x in costs)
    assert all(x['alt']['pflichtfragen']==x['neu']['pflichtfragen']==4 and x['alt']['papierphasen']==x['neu']['papierphasen']==4 for x in costs)
    titel={'passend':'Vollständig richtige Erklärungen','teilweise':'Richtige Teilaussagen','ergebnis':'Bloßes Ergebnis',
           'fehlvorstellung':'Fehlvorstellungen','widerspruch':'Widersprüche','beziehung':'Vertauschte Ursache und Wirkung',
           'unsicher':'Fachlich unklare Antworten','zusatz':'Richtiger Kern mit unklarem Zusatz'}
    tabelle='\n'.join(f"| {titel[key]} | {v['anzahl']} | {v['vorher']} | {v['jetzt']} |"
                      for key,v in extern.items())
    report=f'''# Prüfbericht · Vorbereitung mit vier Infokarten

Geprüfter Commit `{head}` auf dem Vorbereitungszweig. Der vor der Bearbeitung mit dem entfernten Zweig abgeglichene Ausgangsstand ist `{START}`.

## Unterrichtsweg

Auf jedem Niveau führen acht kurze Informationsansichten zu vier Papieraufträgen. Vor jeder Karte erläutern zwei Bildseiten die vier einzutragenden Sachverhalte. Nummer, markierte Blatthälfte, Blattseite, Kartenname und vier einzelne Schreibzeilen benennen die Handlung. Bereits richtige Wörter bleiben stehen. Danach folgen vier Fragen in Papier-Reihenfolge. Die Lehrkraft gibt das Zeichen zum Schneiden. Ein Direkteinstieg mit vollständigem Papier und ein eigener Zeitnotweg stehen bei der Wiederaufnahme zur Verfügung.

Förder und ESA wählen Antworten. Auf MSA erklären Lernende den Zusammenhang zwischen ausbleibendem Eisprung und Befruchtung sowie zwischen Schleim und Durchtritt der Spermien. Auf AHR erläutern sie die Grenze des Kondomschutzes und die Wirkung von Kupfer trotz möglichen Eisprungs. Zwei weitere Auswahlfragen je Niveau prüfen Fehlvorstellungen. Die Lerntexte, Kartenstellen, Antwortalternativen, Begründungen und aufgabenspezifischen Hilfen sind im Vertrag gegenübergestellt. Die acht vorhandenen Funktionsskizzen zeigen Hülle, Hautkontakt, Eisprung, Einnahme, Kupfer, Schleim und mögliche Veränderungen der Blutung. Pfeile bezeichnen mögliche Veränderungen. Die Miniatur zeigt Nummer und Methodennamen auf beiden Blatthälften. Die gesuchte Hälfte ist markiert. Vor den Fragen können Lernende direkt beginnen oder eine fehlende Karte ergänzen. Es gibt keine vorgezogene Fallberatung.

## Testergebnisse

- {len(runs)} vollständige Lernwege, alle vier Niveaus mit und ohne Fehlversuche und Hilfen. {scope['bildschirmpruefungen']} Kontrollen der gerenderten Texte, Grafiken, Tasten und Trefferflächen in Chromium {ver['chromium']} und WebKit {ver['webkit']}. Alle im Katalog geprüften Arbeitsschritte waren ohne Scrollen erreichbar. Das Sichtpaket enthält {len(pics)} echte Browseraufnahmen.
- 16 Originalkarten und alle 64 Feldlösungen mit Referenzarchiv, alten Auslieferungen sowie vier Schüler- und vier Muster-PDFs abgeglichen. Der Feldnachweis dokumentiert für jede Nummer den tatsächlich vor dem Schreiben gezeigten Text und den zugehörigen vollständigen Originalabsatz.
- Geprüft wurden die 961 bisherigen Freitexte, sämtliche zwölf Auswahlfragen und die 73 eingereichten CSV-Zeilen. Die Originaldatei ist mit unverändertem SHA-256 im Feedback-Testkatalog enthalten. Zeilennummer, Sollurteil, frühere Diagnose und aktuelle Ausgaben lassen sich dort nachschlagen. Im bisherigen Katalog blieben alle Diagnosen, Erstreaktionen und Hilfen 1 bis 4 identisch mit 30c32c4. Die frühere Kontrollreserve erreicht weiterhin {reserve['korrekt']}/{reserve['gesamt']}.
- Beim Beispiel „Die Pille hemmt den Eisprung. Keine Eizelle wird frei. Die Pille schützt vor HIV.“ zeigten beide Browser am Ausgangsstand in Hilfe 5 und im Selbstvergleich nur die Eisprung-Erklärung. Jetzt steht in beiden Ansichten zusätzlich „Pille und Spiralen schützen nicht vor HIV oder anderen STI.“ Nach dem Bearbeiten bezieht sich Hilfe 5 sofort auf den neuen Entwurf. Die Papieransicht für Kapitel 3 und ihre Hilfe geben auch beim Direkteinstieg die Position „Suche auf der Rückseite oben 3 – Kupferspirale.“ an.
- In der externen Stichprobe erhielten fünf Fehlvorstellungen, zwölf Widersprüche und drei vertauschte Ursache-Wirkungs-Beziehungen die zum Fehler passende Unterstützung. Sechs bisher offene Formulierungen führen jetzt zur bereits vorhandenen konkreten Fehlererklärung. Sieben zusätzliche Gegenproben prüfen Verneinungen, eine Frage und eine ausdrückliche Einschränkung zum Einnahmeplan. Im gesamten Testbestand gab es {fp} unberechtigte vollständige Bestätigungen und {fn} richtige Erklärungen mit eindeutiger Fehlerzuschreibung.
- Alle 73 CSV-Antworten wurden in Chromium und WebKit bei 390 × 560 CSS-Pixeln und 125 % Schrift über die gebaute HTML-Datei eingegeben. Geprüft wurde die angezeigte Denkfrage, die Korrektur in den Hilfeansichten und im angebotenen Selbstvergleich, der vollständige eigene Text einschließlich aller Textteile und das Weiterarbeiten. Die Sichtprüfung enthält für alle {len(externe_wege)} Wege die tatsächlichen Ausgaben.

### Unabhängiger Freitexttest

| Fachliches Soll aus der CSV | Texte | 30c32c4 richtig eingeordnet | Aktueller Stand richtig eingeordnet |
|---|---:|---:|---:|
{tabelle}

Diese gezielt schwierigen Texte sind laut Einreichung nicht repräsentativ. Die Übereinstimmung stieg von 24 auf 30 von 73. Nur eine der 40 vollständigen Erklärungen wurde direkt als passend erkannt. Die übrigen 39 und vier der neun Teilantworten führten zum angeleiteten Selbstvergleich. Ein Beispiel ist die richtige Erklärung zur Ovulation mit dem Wort „Wirkstoffe“. Die Software lässt die Einordnung offen und zeigt den eigenen Text neben dem Beispiel. Automatisiert geprüft wurde die Zuordnung der Hilfe zum fachlichen Fehler. Die Lernwirkung muss im Unterricht untersucht werden.

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
    files={'Externe-Freitextwege.json':dump(externe_wege),'Browserpruefung.json':(QA/'Browserpruefung.json').read_bytes(),'Touch-und-Tastatur.json':dump(t),'Feedback-Ergebnisse.json':dump(counts),
           'Kartenfelder-im-Lernweg.json':dump(proof['feldbelege']),'Arbeitsumfang.json':dump(costs),'Pruefumfang.json':dump(scope),'Pruefbericht.md':report}
    pack(OUT/'Vorbereitung-Sichtpruefung.zip',{**files,**pics})
    (OUT/'Testergebnisse.json').write_text(dump(dict(**scope,touch=t,arbeitsumfang=costs)))
    hashes={p.name:sha(p.read_bytes()) for p in sorted(OUT.iterdir()) if p.name not in ('SHA256SUMS','Buildnachweis.json')}
    (OUT/'Buildnachweis.json').write_text(dump(dict(**scope,dateien=hashes)))
    (OUT/'SHA256SUMS').write_text(''.join(sha(p.read_bytes())+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.name!='SHA256SUMS'))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('vorfassung',type=Path);run(parser.parse_args().vorfassung)
