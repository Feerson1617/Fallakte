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
    reserve=counts['kontrollreserve']['satz']['kontrollreserve']
    vergleich=counts['vorher_nachher']
    alle=counts['gesamt']['satz']
    fp=sum(v.get('falsch_positiv',0) for v in alle.values())
    fn=sum(v.get('ungerechtfertigt_negativ',0) for v in alle.values())
    assert fp==fn==0,(fp,fn)
    freitexte=sum(counts['verschiedene_texte'].values())
    assert all(v>=200 for v in counts['verschiedene_texte'].values())
    assert all(x['alt']['klicks']==x['neu']['klicks'] and x['alt']['freitext']==x['neu']['freitext'] for x in costs)
    assert all(x['alt']['pflichtfragen']==x['neu']['pflichtfragen']==4 and x['alt']['papierphasen']==x['neu']['papierphasen']==4 for x in costs)
    titel={'passend':'Vollständig richtige Erklärungen','teilweise':'Richtige Teilaussagen','ergebnis':'Bloßes Ergebnis',
           'fehlvorstellung':'Fehlvorstellungen','widerspruch':'Widersprüche','beziehung':'Vertauschte Ursache und Wirkung',
           'unsicher':'Fachlich unklare Antworten','zusatz':'Richtiger Kern mit unklarem Zusatz'}
    tabelle='\n'.join(f"| {label} | {vergleich[key]['gesamt']} | {vergleich[key]['vorher']} | {vergleich[key]['jetzt']} |"
                      for key,label in titel.items())
    report=f'''# Prüfbericht · Vorbereitung mit vier Infokarten

Geprüfter Commit `{head}` auf dem Vorbereitungszweig. Der vor der Bearbeitung mit dem entfernten Zweig abgeglichene Ausgangsstand ist `{START}`.

## Unterrichtsweg

Auf jedem Niveau führen acht kurze Informationsansichten zu vier Papieraufträgen. Vor jeder Karte erläutern zwei Bildseiten die vier einzutragenden Sachverhalte. Nummer, markierte Blatthälfte, Blattseite, Kartenname und vier einzelne Schreibzeilen benennen die Handlung. Bereits richtige Wörter bleiben stehen. Danach folgen vier Fragen in Papier-Reihenfolge. Die Lehrkraft gibt das Zeichen zum Schneiden. Ein Direkteinstieg mit vollständigem Papier und ein eigener Zeitnotweg stehen bei der Wiederaufnahme zur Verfügung.

Förder und ESA wählen Antworten. Auf MSA erklären Lernende den Zusammenhang zwischen ausbleibendem Eisprung und Befruchtung sowie zwischen Schleim und Durchtritt der Spermien. Auf AHR erläutern sie die Grenze des Kondomschutzes und die Wirkung von Kupfer trotz möglichen Eisprungs. Zwei weitere Auswahlfragen je Niveau prüfen Fehlvorstellungen. Die Lerntexte, Kartenstellen, Antwortalternativen, Begründungen und aufgabenspezifischen Hilfen sind im Vertrag gegenübergestellt. Die acht vorhandenen Funktionsskizzen zeigen Hülle, Hautkontakt, Eisprung, Einnahme, Kupfer, Schleim und mögliche Veränderungen der Blutung. Pfeile bezeichnen mögliche Veränderungen. Die Miniatur zeigt Nummer und Methodennamen auf beiden Blatthälften. Die gesuchte Hälfte ist markiert. Vor den Fragen können Lernende direkt beginnen oder eine fehlende Karte ergänzen. Es gibt keine vorgezogene Fallberatung.

## Testergebnisse

- {len(runs)} vollständige Lernwege, alle vier Niveaus mit und ohne Fehlversuche und Hilfen. {scope['bildschirmpruefungen']} Kontrollen der gerenderten Texte, Grafiken, Tasten und Trefferflächen in Chromium {ver['chromium']} und WebKit {ver['webkit']}. Alle im Katalog geprüften Arbeitsschritte waren ohne Scrollen erreichbar. Das Sichtpaket enthält {len(pics)} echte Browseraufnahmen.
- 16 Originalkarten und alle 64 Feldlösungen mit Referenzarchiv, alten Auslieferungen sowie vier Schüler- und vier Muster-PDFs abgeglichen. Der Feldnachweis dokumentiert für jede Nummer den tatsächlich vor dem Schreiben gezeigten Text und den zugehörigen vollständigen Originalabsatz.
- Alle zwölf Auswahlfragen wurden mit beiden Antworten geprüft. Für die vier freien Aufgaben liegen {freitexte} verschiedene Eingaben samt Sollbewertung, Ausgaben der beiden Softwarestände und Hilfestufen vor. In diesen Beständen gab es {fp} falsche vollständige Bestätigungen und {fn} richtige Antworten mit eindeutiger Fehlerzuschreibung. Die 109 extern geprüften Schülertexte lagen nicht vollständig im Wortlaut vor. Die fünf im Auftrag zitierten richtigen Formulierungen sowie ihre fachlichen Gegenproben sind als Regression enthalten.
- Alle fünf Beispiele werden jetzt als passend erkannt. Bei „Die Pille verhindert den Eisprung. Eine Befruchtung ist nicht möglich.“ wird das Ergebnis erkannt und gezielt nach der Eizelle gefragt. Bei umgekehrter Kausalrichtung fragt die Anwendung nach dem ersten Vorgang. Ein erkennbarer Zusatz wie „Die Pille schützt vor HIV“ führt auch in einer anderen Aufgabe zur konkreten Fehlererklärung, Infokarte und Belegstelle. Bei offener Bedeutung dürfen Schüler ihren Text mit den beiden Kernaussagen und dem Beispiel vergleichen, bearbeiten oder weitergehen.
- In der neuen Kontrollreserve stimmten {reserve['korrekt']} von {reserve['gesamt']} Diagnosen mit den festgelegten Bedeutungen überein. Vier richtige natürliche Erklärungen führten zum vorsichtigen Selbstvergleich. Beispiel: „Kupfer macht die Schwimmer im Sperma träge, sodass sie das Ei kaum noch erreichen.“ Die frühere Zielmarke von 95 % für normale richtige Antworten wurde in dieser anspruchsvollen Stichprobe verfehlt (12 von 16). Vier von vier Schreibvarianten und 32 von 32 Teilantworten, Fehlvorstellungen und Widersprüchen wurden korrekt erkannt.
- Für jede Eingabe wurden die sichtbare Rückmeldung und alle fünf Hilfetexte geprüft. Bei {counts['hilfen']['sollbezogen']} von {reserve['gesamt']} Reservetexten entsprachen Diagnose und Hilfebezug dem vorab festgelegten Soll. Bei vier richtigen Antworten blieben Ursache oder Folge unerkannt. Hier war der neutrale Vergleich verfügbar, ohne einen bestimmten fehlenden Inhalt zu unterstellen. Das Verfahren überprüft Zuordnung, Texte, Quellen und Abschlusswege. Die Wirkung auf das Verständnis muss im Unterricht beobachtet werden.
- Die Daten der Entwicklung, zwei neue Zwischenproben (86 und 85 Texte) und die nach Festlegung von Erkennung und Hilfen bei a59c7c3 erstellte Kontrollreserve (80 andere Texte) sind getrennt archiviert. Die erstmaligen Zwischenproben ergaben 78/86 und 78/85. Spätere Verbesserungen an diesen beiden Beständen zählen als Regression. Die Diagnosen und Hilfeansichten lassen sich im Testkatalog für jede Formulierung nachlesen.

| Erwartete Bedeutung in der Kontrollreserve | Texte | b3abb52 richtig zugeordnet | Aktueller Stand richtig zugeordnet |
|---|---:|---:|---:|
{tabelle}

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
