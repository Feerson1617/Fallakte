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
           'fehlvorstellung':'Fehlvorstellungen','widerspruch':'Widersprüche','vertauscht':'Vertauschte Ursache und Wirkung',
           'unsicher':'Fachlich unklare Antworten','zusatz':'Richtiger Kern mit unklarem Zusatz'}
    tabelle='\n'.join(f"| {titel[key]} | {v['anzahl']} | {v['vorher']} | {v['jetzt']} |"
                      for key,v in extern.items())
    sichttexte=(QA/'Sichtbarer-Wortlaut.json').read_bytes()
    report=f'''# Prüfbericht · Vorbereitung mit vier Infokarten

Geprüfter Commit `{head}` auf dem Vorbereitungszweig. Der vor der Bearbeitung mit dem entfernten Zweig abgeglichene Ausgangsstand ist `{START}`.

## Unterrichtsweg

Auf jedem Niveau führen acht kurze Informationsansichten zu vier Papieraufträgen. Vor jeder Karte erläutern zwei Bildseiten die vier einzutragenden Sachverhalte. Nummer, markierte Blatthälfte, Blattseite, Kartenname und vier einzelne Schreibzeilen benennen die Handlung. Bereits richtige Wörter bleiben stehen. Danach folgen vier Fragen in Papier-Reihenfolge. Die Lehrkraft gibt das Zeichen zum Schneiden. Ein Direkteinstieg mit vollständigem Papier und ein eigener Zeitnotweg stehen bei der Wiederaufnahme zur Verfügung.

Förder und ESA wählen Antworten. Auf MSA erklären Lernende den Zusammenhang zwischen ausbleibendem Eisprung und Befruchtung sowie zwischen Schleim und Durchtritt der Spermien. Auf AHR erläutern sie die Grenze des Kondomschutzes und die Wirkung von Kupfer trotz möglichen Eisprungs. Zwei weitere Auswahlfragen je Niveau prüfen Fehlvorstellungen. Die Lerntexte, Kartenstellen, Antwortalternativen, Begründungen und aufgabenspezifischen Hilfen sind im Vertrag gegenübergestellt. Die acht vorhandenen Funktionsskizzen zeigen Hülle, Hautkontakt, Eisprung, Einnahme, Kupfer, Schleim und mögliche Veränderungen der Blutung. Pfeile bezeichnen mögliche Veränderungen. Die Miniatur zeigt Nummer und Methodennamen auf beiden Blatthälften. Die gesuchte Hälfte ist markiert. Vor den Fragen können Lernende direkt beginnen oder eine fehlende Karte ergänzen. Es gibt keine vorgezogene Fallberatung.

## Verbindlicher CLT-Stand für Work

Die Schreibfelder beginnen in jeder Kartenhälfte links. Schüler- und Musterfassung verwenden dieselbe Satzroutine. Die kurze Lesefassung für Förder und ESA benennt die Samenzelle, die freie Eizelle, die Zustimmung zum Einsetzen und mögliche Schmerzen direkt. Die höhere Anforderung auf MSA und AHR liegt weiterhin in der eigenen Erklärung. Der optionale Pearl-Index-Vergleich wird erst nach der vierten Aufgabe angeboten und findet mit den Papierkarten statt.

## Ergonomische Abnahme gegenüber 2c2d952

Die gelbe Taste „Ich brauche Hilfe“ bleibt bei Niveauwahl, Kartenwahl, Nachschlagen, Übergang und Abschluss am selben rechten oberen Rand. Eine kurze Orientierung führt jeweils zur Ausgangsansicht zurück. Fachfehler, Teilergebnisse und passende Erklärungen haben zusätzlich zur Rückmeldung unterschiedliche Hervorhebungen. Allgemeine Aktionstasten sind blau. Enge Fenster nutzen weniger Zwischenraum und eine kürzere Blattorientierung. Die Aufgabenschrift wird dafür nicht verkleinert.

Geprüft werden die Lage der Hilfetaste und die Trefferflächen aller Tasten in den protokollierten Ansichten. Der Fehlerweg umfasst jede vorgegebene Alternative. Die Vorbereitung arbeitet mit Infokarten und Papier. Ein Gesprächsverlauf gehört erst zu den Unterrichtsbesuchen. Ungeprüft bleiben beliebige andere Fenstermaße und Schriftstufen, sämtliche möglichen Freitexte sowie Kombinationen beliebig vieler Unterbrechungen.

## Sprachliche Abnahme

Für jede Methode führt der Weg vom Bild über zwei kurze Kernsätze zur selben Aussage auf dem Blatt. Eine fett gedruckte Lösung gehört zu genau einer nummerierten Lücke. Die Suchhilfe nennt Methode und gedruckte Überschrift. Auf Förder und ESA stehen konkrete Personen, Körperteile und Handlungen im Satz. Die beiden höheren Niveaus verlangen weiter eigene biologische Erklärungen oder das Abwägen einer Aussage. Im Zeitnotweg führt der Rückweg zur fehlenden Karte.

„Eisprung“ bleibt nötig, um die Pille zu erklären. Der nächste Satz nennt die frei werdende Eizelle. „Spermien“ wird mit „Samenzellen“ erklärt. Die Bildseite zeigt den Gebärmutterhals und beschreibt den Schleim mit „zäher“. Die gedruckte Karte erläutert die Stelle unten an der Gebärmutter. „Pearl-Index“ bezeichnet den Vergleichswert für Schwangerschaften bei einem Jahr Anwendung. „Gestagen“ und „Östrogen“ sind als Hormonnamen gekennzeichnet. Die Arbeitsaufträge verlangen die Namen nicht. Blutgerinnsel werden bei den höheren Niveaus unmittelbar erklärt.

„Material und Allergie“ führt jetzt zu „Kondome ohne Latex“, „Persönliche Verträglichkeit“ zu „Jeder Körper reagiert anders“. Alle 80 Abschnittspaare und alle 64 Feldpaare stehen in Textaenderungen.md im Work-Paket. Die vollständigen Ansichten der Browserwege stehen im Sichtpaket, die fallbezogenen Reaktionen im Feedback-Testkatalog. Echte Lesesicherheit lässt sich aus diesen Prüfungen nicht ableiten.

## Testergebnisse

- {len(runs)} vollständige Lernwege, alle vier Niveaus mit und ohne Fehlversuche und Hilfen. {scope['bildschirmpruefungen']} Kontrollen der gerenderten Texte, Grafiken, Tasten und Trefferflächen in Chromium {ver['chromium']} und WebKit {ver['webkit']}. Alle im Katalog geprüften Arbeitsschritte waren ohne Scrollen erreichbar. Das Sichtpaket enthält {len(pics)} echte Browseraufnahmen.
- Alle 80 früheren Abschnitte und 64 früheren Feldlösungen wurden mit der mitgelieferten Abgleichtabelle verknüpft. Alle neuen Überschriften, Lücken, Lösungen und Pearl-Werte wurden auf den richtigen Seiten der acht neuen PDFs ausgelesen und mit dem Vertrag verglichen. Der Feldnachweis belegt jede Lösung bereits auf der vorhergehenden Bildseite.
- Geprüft wurden die 961 bisherigen Freitexte, sämtliche zwölf Auswahlfragen und die 73 eingereichten CSV-Zeilen. Die Originaldatei ist mit unverändertem SHA-256 im Feedback-Testkatalog enthalten. Zeilennummer, Sollurteil, frühere Diagnose und aktuelle Ausgaben lassen sich dort nachschlagen. Die diagnostischen Einordnungen entsprechen 542eddf. Alle fünf Hilfeausgaben wurden für die jeweiligen Teilaussagen und Denkfehler geprüft. Die frühere Kontrollreserve erreicht weiterhin {reserve['korrekt']}/{reserve['gesamt']}.
- Beide Browser zeigen beim HIV-Irrtum auch in Hilfe 5 und im Selbstvergleich die konkrete Korrektur. Kapitel 3 nennt bei jedem Einstieg die Rückseite oben. Im gesamten Testbestand gab es {fp} unberechtigte vollständige Bestätigungen und {fn} richtige Erklärungen mit eindeutiger Fehlerzuschreibung.
- Alle 73 CSV-Antworten wurden in Chromium und WebKit bei 390 × 560 CSS-Pixeln und 125 % Schrift über die gebaute HTML-Datei eingegeben. Geprüft wurde die angezeigte Denkfrage, die Korrektur in den Hilfeansichten und im angebotenen Selbstvergleich, der vollständige eigene Text einschließlich aller Textteile und das Weiterarbeiten. Die Sichtprüfung enthält für alle {len(externe_wege)} Wege die tatsächlichen Ausgaben.

### Unabhängiger Freitexttest

| Fachliches Soll aus der CSV | Texte | 30c32c4 richtig eingeordnet | Aktueller Stand richtig eingeordnet |
|---|---:|---:|---:|
{tabelle}

Diese gezielt schwierigen Texte sind laut Einreichung nicht repräsentativ. Wie in 542eddf stimmten 30 von 73 Einordnungen mit dem externen Urteil überein. Nur eine der 40 vollständigen Erklärungen wurde direkt als passend erkannt. Die übrigen 39 und vier der neun Teilantworten führten zum angeleiteten Selbstvergleich. Ein Beispiel ist die richtige Erklärung zur Ovulation mit dem Wort „Wirkstoffe“. Die Software lässt die Einordnung offen und zeigt den eigenen Text neben dem Beispiel. Automatisiert geprüft wurde die Zuordnung der Hilfe zum fachlichen Fehler. Die Lernwirkung muss im Unterricht untersucht werden.

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
    files={'Sichtbarer-Wortlaut.json':sichttexte,'Externe-Freitextwege.json':dump(externe_wege),'Browserpruefung.json':(QA/'Browserpruefung.json').read_bytes(),'Touch-und-Tastatur.json':dump(t),'Feedback-Ergebnisse.json':dump(counts),
           'Kartenfelder-im-Lernweg.json':dump(proof['feldbelege']),'Arbeitsumfang.json':dump(costs),'Pruefumfang.json':dump(scope),'Pruefbericht.md':report}
    pack(OUT/'Vorbereitung-Sichtpruefung.zip',{**files,**pics})
    (OUT/'Testergebnisse.json').write_text(dump(dict(**scope,touch=t,arbeitsumfang=costs)))
    from clt import ausgabe
    ausgabe()
    hashes={p.name:sha(p.read_bytes()) for p in sorted(OUT.iterdir()) if p.name not in ('SHA256SUMS','Buildnachweis.json')}
    (OUT/'Buildnachweis.json').write_text(dump(dict(**scope,dateien=hashes)))
    (OUT/'SHA256SUMS').write_text(''.join(sha(p.read_bytes())+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.name!='SHA256SUMS'))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('vorfassung',type=Path);run(parser.parse_args().vorfassung)
