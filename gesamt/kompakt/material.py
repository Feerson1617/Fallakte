"""Druckkorrekturen für Work und Vergleich der beiden gebauten Datenverträge."""
import argparse
import csv
import io
import json
import re
from pathlib import Path
from zipfile import ZipFile
from auslieferung import OUT,QA,sha
from sprachpruefung import documents,bank,leaves
from abnahme import SOURCE


def run(ref):
    old=documents((ref/'Fallakte-Gesamt.html').read_bytes())
    current=documents((OUT/'Fallakte-Gesamt.html').read_bytes())
    allow={'UB02':r'buildCommit|stages/L0[1-5]/levels/[^/]+/(?:paperPrompt|task|strategies/[^/]+/hints/4)',
           'UB08':r'commit|media/.*|evaluation/Förder|ui/endRecovery',
           'Tom':r'buildCommit|stages/[0-9]+/paper/[^/]+','Celina':r'buildCommit|stages/[0-9]+/paper/[^/]+'}
    diff=[];unchanged={}
    for module in current:
        a=dict(leaves(bank(old[module][0])));b=dict(leaves(bank(current[module][0])))
        assert a.keys()==b.keys(),module
        retained={}
        for k in a:
            if a[k]!=b[k]:
                assert re.fullmatch(allow.get(module,'(?!)'),k),(module,k)
                diff.append(dict(modul=module,stelle=k,vorher=a[k],nachher=b[k]))
            else:retained[k]=a[k]
        unchanged[module]=dict(unveraenderte_werte=len(retained),sha256=sha(json.dumps(retained,sort_keys=True,ensure_ascii=False).encode()))
    assert current['PREP'][1]==old['PREP'][1]
    tiers={}
    for key in ['Vorbereitung','02-12','08-12','Gesamt']:
        file=OUT/('Fallakte-'+key+'.html');raw=file.read_bytes()
        with ZipFile(OUT/('Fallakte-'+key+'-SCORM12.zip')) as z:
            assert z.testzip() is None and z.read('index.html')==raw
        used=documents(raw)
        assert set(used)==({'START','PREP'} | ({'UB02','Celina','Tom'} if key!='Vorbereitung' else set()) | ({'UB08'} if key in ['08-12','Gesamt'] else set()))
        for m in set(used)-{'START'}:assert used[m][1]==current[m][1]
        tiers[key]={m:h for m,(_,h) in used.items()}
    for suffix in ('.html','-SCORM12.zip'):
        name='Fallakte-Vorbereitung'+suffix
        assert (OUT/name).read_bytes()==(ref/name).read_bytes()
    (QA/'Textdiff.json').write_text(json.dumps(dict(eingebettete_Module=tiers,unveraendert=unchanged,aenderungen=diff),ensure_ascii=False,indent=2))
    fam=bank(current['UB08'][0]);celina=bank(current['Celina'][0])
    names={'K':'Kondom','Cu':'Kupferspirale','K+Cu':'Kondom + Kupferspirale','P':'Kombinationspille','H':'Hormonspirale','K+P':'Kondom + Kombinationspille','K+H':'Kondom + Hormonspirale'}
    t=io.StringIO();w=csv.writer(t,delimiter='\t');w.writerow(['Abschnitt','Vorschlag','A','B','C'])
    conflicts=io.StringIO();cw=csv.writer(conflicts,delimiter='\t');cw.writerow(['Abschnitt','Vorschlag','Rückmeldung zur erneuten Auswahl'])
    rows=[]
    for i,s in enumerate(celina['stages'],1):
        name='Celina '+str(i)+' – '+s['title']
        rows.append('| '+str(1 if i<=3 else 2)+' | '+name+' | '+' / '.join(l+' '+v for l,v in zip('ABC',s['answers']))+' |')
        for k,v in s['checks'].items():
            if k in s['allowed']:w.writerow([name,names[k],*v['answers']])
            else:cw.writerow([name,names[k],s['conflicts'][k]['full']])
    (QA/'Celina_Ausfall_Aussagen.tsv').write_text(t.getvalue())
    (QA/'Celina_Ausfall_Rueckmeldungen_Lehrkraft.tsv').write_text(conflicts.getvalue())
    text='''# Letzte Materialkorrekturen für Work

Softwarestand `b166bce`. Die Seitenzahlen beziehen sich auf die gelieferten kompakten Druckfassungen. Gleichlautende Felder beider Niveaus sind zusammen aufgeführt.

## 02.12. · Celina auf MSA und AHR

**02_Freiwillig/Celina_MSA.pdf und 02_Freiwillig/Celina_AHR.pdf, Seiten 1 und 2, jeweils die Arbeitsanweisung über dem ersten Abschnitt.**

Bisher: „Beantworte die Frage und kreise A, B oder C ein. Gib den Buchstaben ein → „Code prüfen“ → „Nachricht senden“.“

Neu: „Lies die Frage auf diesem Bogen. Lies A, B und C zu deiner Wahl am iPad. Schreibe deine Begründung auf diesen Bogen. Kreise hier den Buchstaben der passenden Aussage ein. Gib den Buchstaben am iPad ein. Tippe auf „Code prüfen“. Ist der Code richtig, tippe auf „Nachricht senden“.“

**Dieselben PDFs, Seiten 1 und 2, Antwortfelder.** Die Fachfrage jedes Abschnitts und die vorhandenen Schreibzeilen bleiben stehen. Ersetze in jeder Tabellenzeile die drei bisher fest gedruckten Aussagen durch dasselbe neutrale Feld: „Meine Begründung:“ [Schreibzeilen] und darunter „Meine Wahl:   A     B     C“. Kein Buchstabe ist markiert.

| Seite | Feld | Bisher gedruckte Aussagen A / B / C |
|---|---|---|
'''+ '\n'.join(rows)+'''

**03_Ausfall/Freiwillige_Faelle_ohne_iPad_MSA.pdf und 03_Ausfall/Freiwillige_Faelle_ohne_iPad_AHR.pdf, Seite 1, jeweils der letzte Satz unter Celina 1 bis Celina 5.**

Bisher in jedem Abschnitt: „Bearbeite die Frage auf deinem Zusatzbogen. Zur Kontrolle hilft die Lehrkraft.“

Neu in jedem Abschnitt: „Nenne deinen Vorschlag. Suche auf dem Ersatzblatt deinen Abschnitt und deinen Vorschlag. Lies die drei Aussagen. Schreibe deine Begründung auf den Celina-Bogen. Kreise dort A, B oder C ein. Bitte die Lehrkraft, deine Wahl zu prüfen.“

Setze für beide Niveaus dasselbe Ersatzblatt aus **Celina_Ausfall_Aussagen.tsv**. Jede Zeile enthält eine eigene Überschrift aus Abschnitt und Vorschlag sowie die drei unveränderten Aussagen in Bildschirmreihenfolge. Ist ein Vorschlag im Abschnitt nicht aufgeführt, nutzt die Lehrkraft die zugehörige Rückmeldung in **Celina_Ausfall_Rueckmeldungen_Lehrkraft.tsv** und lässt erneut wählen. Die vorhandenen Abschnittscodes B, A, C, B, C dienen ausschließlich der Lehrkraft. Im durchgehenden Geräteausfall führt die Lehrkraft nach der Kontrolle zum nächsten Abschnitt.

## 08.12. · Lauras Frage

**01_Pflicht/Pflichtlernbogen_Foerder.pdf, Seite 2, „Lauras Frage – Meine Antwort“, Punkt 4.**

Bisher: „4. Warum hilft der Fakt Laura?“ und „„Das hilft Laura, weil …“ Wenn du beide wählst, erkläre beide.“

Neu, entsprechend dem Bildschirmauftrag: „'''+fam['evaluation']['Förder'].splitlines()[-1]+'''“

**01_Pflicht/Pflichtlernbogen_Foerder.pdf, Pflichtlernbogen_ESA.pdf, Pflichtlernbogen_MSA.pdf und Pflichtlernbogen_AHR.pdf, jeweils Seite 2, Feld „Festhalten“, Hinweis vor der Statusmarkierung.**

Bisher: „Prüfung am iPad noch offen? Tippe auf „Lauras Frage – Prüfen“.“

Neu: „'''+ ' '.join(fam['ui']['endRecovery'].split())+'''“

Die drei vorhandenen Statusfelder bleiben unmarkiert. Die erste eigene Antwort bleibt lesbar. Unter „Festhalten“ ist Platz für eine freiwillige Präzisierung. Die Einschätzung der eigenen Begründung erfolgt im Unterricht.
'''
    (QA/'Letzte_Materialkorrekturen_Work.md').write_text(text)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('referenz',type=Path)
    run(parser.parse_args().referenz)
