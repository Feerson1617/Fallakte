"""Erzeuge die Übergabe aus den Prüfprotokollen desselben Actions-Laufs."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from shutil import copyfile
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import html


def release(source, out):
    def find(name):
        matches=list(source.rglob(name))
        if len(matches)!=1:raise ValueError(f'{name} · {len(matches)} Fundstellen')
        return matches[0]
    def read(name):return json.loads(find(name).read_text())
    out.mkdir(parents=True,exist_ok=True)
    day={}
    for date in ('02-12','08-12'):
        stem='Fallakte-'+date
        page=find(stem+'.html')
        package=find(stem+'-SCORM12.zip')
        with ZipFile(package) as z:
            assert z.testzip() is None and z.read('index.html')==page.read_bytes()
        day[date]=sha256(page.read_bytes()).hexdigest()
        rev=html.parse(str(page)).xpath('string(//meta[@name="revision"]/@content)')
        if date=='02-12':head=rev
        assert head==rev and len(head)==40
        for p in (page,package):copyfile(p,out/p.name)
    layout=read('Sprachansichten.json');assert layout['module']['02-12']['02']==layout['module']['08-12']['02']
    hit=read('Trefferpruefung.json');assert hit['html_sha256']==day['08-12'] and len(hit['wege'])==40
    advice=read('bedienung.json');assert advice['commit']==head
    logfiles=['Sprachansichten.json','Trefferpruefung.json','bedienung.json','Vertiefungspruefung.json']
    families=[];states=[];routes=[]
    for engine in ('chromium','webkit'):
        name='Empfehlungen-'+engine+'.json';routes+=read(name);logfiles.append(name)
        name='Familienwege-tandem-'+engine+'.json';states.append(read(name));logfiles.append(name)
        for i in range(8):
            name=f'Familienroute-{engine}-{i}.json';row=read(name);assert row['html_sha256']==day['08-12']
            families.extend(row['wege']);logfiles.append(name)
    assert len(routes)==280 and len(families)==16
    extra=read('Vertiefungspruefung.json');assert len(extra)==8
    report=f"""# Ergonomische Abnahme · Unterrichtsbesuche am 02. und 08. Dezember

Stand `{head}`. Für den ersten Unterrichtsbesuch ist nur der 02.12. freigeschaltet und enthalten. Die spätere Version enthält beide Tage. Die Offline-Datei und der Startinhalt ihres jeweiligen SCORM-Pakets stimmen byteweise überein. Das Modul vom 02.12. ist in beiden Versionen identisch.

## Änderungen für die Lernenden

- Ein gelber Hilfezugang im Kopf des Arbeitsbereichs führt zur aktuellen Hilfestufe oder zur Orientierung. Die Hilfe nimmt vorübergehend den Platz der Aufgabe ein. Die Eingabe bleibt in der laufenden Sitzung erhalten.
- Im Gespräch bleiben die bisherigen fachlich tragfähigen Beiträge in zeitlicher Folge lesbar. In engen Fenstern zeigt die Vorschau die neueste Nachricht. „Gespräch lesen“ öffnet direkt den Verlauf, „Zur Aufgabe“ führt zurück. Längere Aufgaben oder Quellen werden bei Platzmangel in sichtbare Teile mit Blättertasten aufgeteilt.
- Ein erkannter Fehler und die passende Auswahl haben verschiedene Rückmeldungen und Hervorhebungen. Eine persönliche Gewichtung bleibt eine eigene Entscheidung. Freie Erklärungen im Familienrat bleiben für die Besprechung im Unterricht offen.
- Die reguläre Oberfläche zeigt freiwillige Fälle nach der Pflichtarbeit. Beim Wiedereinstieg kann ein bereits auf Papier abgeschlossener Pflichtteil ausdrücklich angegeben werden. Diese Angabe vergibt keine digitale Leistungsbestätigung. Änderungen, die ein vorhandenes Gespräch oder die Prüfung einer Gewichtung ersetzen, verlangen eine bewusste Bestätigung. Die Lehrkraftansicht des 02.12. lässt sich über `?lehrkraft` am Ende der Startadresse öffnen.

## Ausgeführte Prüfungen

- {len(hit['wege'])} Trefferflächen-Durchläufe von der Tagesauswahl über Aufgaben, Fehler, Hilfe und Korrektur in beiden Browsern auf vier Niveaus. 1180 × 820 und 390 × 600 als Offline-Datei, 820 × 1180, 640 × 420 und 740 × 340 als gepacktes SCO im lokalen LMS. Geprüfte Schriftstufen 100, 125 und 150 Prozent. Bei fokussiertem Textfeld wurde das äußere Fenster zusätzlich auf 740 × 294 verkleinert. Die Trefferprüfung benutzt sichtbare Blättertasten und prüft den Antipppunkt bis zum äußersten Dokument.
- {len(advice['durchlaeufe'])} Beratungswege sowie {len(routes)} Prüfungen aus Niveau, Abschnitt und Empfehlung über beide Browser. Geprüft wurden {sum(x['antworten'] for x in routes)} Fachantworten bzw. Codeeingaben und die fünf Hilfestufen. Hinzu kamen {len(extra)} Durchläufe von Tom und Celina.
- {len(families)} vollständige Familienwege in Chromium und WebKit mit den vier Niveaus, Fehlerkorrektur, Papierwechsel, Anwendung, eigenen Erklärungen und persönlicher Gewichtung. {sum(len(s['pruefungen']) for s in states)} zusätzliche Statusprüfungen und {sum(len(s['quellenarbeit']) for s in states)} Beobachtungen zur selbstständigen Quellenarbeit. {len(layout['wege'])} weitere Layoutprüfungen schlossen die Originalnachricht und frühere Empfehlungen ein.
- Die Datenblätter im Sichtprüfungspaket nennen die tatsächlich geprüften Wege. Die Vorbereitung wird separat ausgeliefert und hat einen eigenen Prüfbericht.

## Grenzen der Abnahme

Die Prüfungen decken fachlich verschiedene Antwortwege und Rückmeldungen ab. Die vollständige Kreuzung jeder Antwort mit jeder Schriftgröße, Bildschirmgröße, Kartenreihenfolge und jeder beliebig wiederholten Unterbrechung wurde nicht ausgeführt. Die Trefferflächenprüfung unter eingeschränkter Höhe benutzt Laura und Mutter als konkrete Fälle. Die übrigen Fälle haben gesonderte Funktionsprüfungen. Ungeprüft bleiben Texte beliebiger Länge, Betriebssystem-Zoom und die native Tastatur auf einem echten Schul-iPad, der produktive itslearning-Kurs, Screenreader und tatsächliche Lernwirkung.

Für den Praxistest das jeweilige ZIP im Kurs öffnen, zunächst quer, dann hochkant. Auf Förder eine Fehlwahl korrigieren. Auf AHR bei offener Bildschirmtastatur die gelbe Hilfe aufrufen und die eigene Erklärung weiterbearbeiten. Neu laden, den Abschnitt vom Papier wählen und auf die fehlende digitale Bestätigung früherer Arbeit achten.
"""
    (out/'Pruefbericht.md').write_text(report)
    with ZipFile(out/'UB-Sichtpruefung.zip','w',ZIP_DEFLATED) as z:
        z.writestr('Pruefbericht.md',report)
        for name in logfiles:z.write(find(name),'Protokolle/'+name)
        for folder in ('Ergonomie','Sprachansichten'):
            for p in sorted(source.rglob(folder+'/*.jpg')):z.write(p,'Bilder/'+folder+'/'+p.name)
    (out/'SHA256SUMS').write_text(''.join(f'{sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in sorted(out.iterdir()) if p.is_file() and p.name!='SHA256SUMS'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('protokolle',type=Path);parser.add_argument('ziel',type=Path)
    args=parser.parse_args();release(args.protokolle,args.ziel)
