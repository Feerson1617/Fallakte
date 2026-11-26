"""Aufgaben und beobachtete Ausgaben mit ihren didaktischen Anforderungen verbinden."""
import csv
from io import StringIO
import json
from zipfile import ZipFile
from erstellen import HERE, OUT, ROOT, sha, pack

THEORIE="""# Didaktische Abnahmegrundlage

Die fachlich notwendige Belastung hängt davon ab, welche Beziehungen jemand bereits versteht. Beim Kondom verbindet die Klasse Hülle, Sperma und freie Haut. Bei der Familienbewertung müssen hingegen medizinische Aussage, Reichweite und persönliches Anliegen zusammengedacht werden. Die Zahl sichtbarer Wörter misst diese Unterschiede nicht.

Vermeidbare Belastung entsteht etwa durch wechselnde Suchorte, doppelte Dokumentation oder unklare Zielobjekte. Signalwörter und Bilder stehen bei der Aussage, für die sie gebraucht werden. Hilfen werden freiwillig geöffnet. Erst gibt es einen Suchort oder eine Denkfrage, danach einen Satzanfang oder ein ausgearbeitetes Beispiel. Wer schon selbst erklären kann, geht direkt weiter. Eigene Erklärungen, begründete Änderungen und der Vergleich mit einem Beispiel verwenden lernbezogene Ressourcen. Diese sind in der neueren CLT keine zwingend zusätzliche dritte Last.

Die Matrix beschreibt Gestaltungsentscheidungen und verbleibende Anforderungen. Sie enthält keine Messung der kognitiven Belastung von Lernenden.

## Wissenschaftliche Grundlagen

- Sweller, van Merriënboer & Paas (2019). Cognitive Architecture and Instructional Design: 20 Years Later. https://doi.org/10.1007/s10648-019-09465-5
- Mayer (2017). Using Multimedia for E-Learning. https://doi.org/10.1111/jcal.12197
- Fiorella & Mayer (2021). Principles for Reducing Extraneous Processing in Multimedia Learning. In The Cambridge Handbook of Multimedia Learning.
- Kalyuga, Ayres, Chandler & Sweller (2003). The Expertise Reversal Effect. https://doi.org/10.1207/S15326985EP3801_4
- Renkl & Atkinson (2003). Structuring the Transition From Example Study to Problem Solving in Cognitive Skill Acquisition. https://doi.org/10.1207/S15326985EP3801_3
- Shute (2008). Focus on Formative Feedback. https://doi.org/10.3102/0034654307313795
"""
PROFILE={
'Orientierung':('Niveau bzw. Kapitel auf dem eigenen Blatt zuordnen.','Blatt und gleich beschriftete Taste.','Nächste eigene Handlung wählen.','Orientierung ersetzt eine zweite fachliche Aufgabe.','Bei fehlender Lesefähigkeit bleibt das Erkennen des Methodennamens eine Hürde.'),
'Information':('Die abgebildete Methode und den beschriebenen Vorgang verbinden.','Körperstelle, Ursache und Wirkung.','Den Vorgang später ohne Grafik erklären.','Zwei Kernaussagen beim betreffenden Bild.','Das Bild kann anatomisches Vorwissen nur teilweise ersetzen.'),
'Papier':('Kartenhälfte und vier Einträge zuordnen.','Seite, Position, identische Feldnummer und Wort.','Bereits passende Wörter stehen lassen.','Vier gleich ausgerichtete Felder und dasselbe Muster.','Der Eintrag zeigt den Papierstand. Verständnis braucht die anschließende Anwendung.'),
'Wahl':('Fachlich passende Aussage von einer konkreten Fehlvorstellung unterscheiden.','Kartenüberschrift und biologische Wirkung.','Wirkungsweise auswählen und bei einer Fehlwahl überdenken.','Konkrete Frage steht unmittelbar bei den Antwortmöglichkeiten.','Zufallstreffer bleiben bei geschlossenen Fragen möglich.'),
'Erklärung':('Ursache und biologische Folge in eigenen Worten verbinden.','Auslöser, Körpervorgang und Ergebnis.','Eine eigene kausale Erklärung formulieren.','Ein Textfeld und eine Prüftaste.','Richtige ungewohnte Formulierungen können zum Selbstvergleich führen.'),
'Rückmeldung':('Eigene Aussage mit der biologischen Beziehung abgleichen.','Erkannter Teil, mögliche Fehlvorstellung und Kartenstelle.','Bei Bedarf nur die unklare Beziehung überarbeiten.','Fehlversuch und passende Kartenstelle stehen beieinander.','Die Erkennung arbeitet regelbasiert. Ihre Grenzen sind im externen Test nachlesbar.'),
'Hilfe':('Den jeweils benötigten Teil der Erklärung erschließen.','Suchüberschrift, Denkimpuls oder Beispiel und eigener Entwurf.','Zur Aufgabe zurückkehren und selbst weiterarbeiten.','Die Hilfe ersetzt den Arbeitsbereich.','Das vollständige Beispiel ist als Unterstützung sichtbar und kein Wissensnachweis.'),
'Vergleich':('Eigene Aussage und Beispiel auf dieselbe Ursache und Folge prüfen.','Eigener Wortlaut, Vergleichsfrage und Beispiel.','Unklare Formulierung selbst prüfen.','Eigener Text bleibt neben dem fachlichen Beispiel erreichbar.','Selbstvergleich und eigenständiger fachlicher Nachweis sind verschieden.'),
'Reserve':('Zwei Pearl-Werte auf denselben Bezugszeitraum beziehen.','100 Frauen, ein Jahr und Grenze der Aussage zu Infektionen.','Eine Kennzahl auf zwei Methoden beziehen.','Erst nach Abschluss freiwillig auf den zwei vorhandenen Karten.','Der Pearl-Index ist kein individuelles Schwangerschaftsrisiko.')}
def ausgabe():
    from lxml import html
    doc=html.fromstring((OUT/'Vorbereitung.html').read_bytes())
    m=json.loads(doc.xpath('string(//script[@id="material"])'));head=doc.xpath('string(//meta[@name="revision"]/@content)')
    with ZipFile(OUT/'Feedback-Testkatalog.zip') as z:diag=json.loads(z.read('Ergebnisse.json'))
    with ZipFile(OUT/'Vorbereitung-Sichtpruefung.zip') as z:views=json.loads(z.read('Sichtbarer-Wortlaut.json'))
    buf=StringIO();w=csv.writer(buf)
    w.writerow(['Niveau','Aufgabe oder Weg','Zustand','Wortlaut','Intrinsic Load','Element Interactivity','Lernbezogene Verarbeitung','Extraneous Load / Befund und Änderung','Split Attention','Redundanz','Kohärenz','Signalisierung','Segmentierung','Vorwissen','Transient Information','Worked Examples','Guidance Fading','Expertise Reversal','Verbleibende Anforderung'])
    def row(t,auf,zust,text,profil,goal):
        intr,elem,learn,extra,limit=PROFILE[profil]
        w.writerow([t,auf,zust,text,goal or intr,elem,learn,extra,
          'Karte und Suchüberschrift sind gleich benannt.' if profil not in ('Orientierung','Papier') else 'Blattposition und digitale Auswahl stimmen überein.',
          'Ein Lernauftrag bzw. ein freiwilliger Impuls.','Fokus auf '+(goal or intr),'Gelbe Hilfe; Rückmeldung mit Wortlaut.', 'Aktuelle Kartenstelle oder Frage bleibt einzeln erreichbar.',
          intr,'Papierkarte bleibt verfügbar. Der digitale Entwurf bleibt in der Sitzung.','Stufe 5 zeigt das aufgabenbezogene Beispiel.' if profil in ('Hilfe','Erklärung','Wahl','Vergleich','Rückmeldung') else 'Kein Lösungsbeispiel in dieser Phase nötig.',
          'Hilfe schließen und selbst weiterarbeiten.','Beispiel freiwillig; direkter Weg für Lernende mit Vorwissen.',limit])
    for v in views:
        screen=v['ansicht'];text=v['text'];t=v['niveau'];prof={'info':'Information','paper':'Papier','help':'Hilfe','reference':'Hilfe','feedback':'Rückmeldung','compare':'Vergleich','reserve':'Reserve'}.get(screen,'Orientierung')
        if screen=='question':prof='Erklärung' if 'Antwort prüfen' in text else 'Wahl'
        goal=next((q['ziel'] for q in m['levels'][t]['fragen'] if q['frage'] in text),'')
        row(t,v['weg'],screen,text,prof,goal)
    for d in diag:
        tier=d['niveau'];q=m['levels'][tier]['fragen'][d['kapitel']-1]
        for key in ('rueckmeldung','wiederholt','dritter_versuch'):
            row(tier,q['frage'],d['ist']+' · '+key,d[key],'Rückmeldung',q['ziel'])
        for index,h in enumerate(d['hilfen'],1):row(tier,q['frage'],d['ist']+' · Hilfe '+str(index),h,'Hilfe',q['ziel'])
    from clt_wege import pruefen
    additional=pruefen()
    for v in additional:
        q=m['levels'][v['niveau']]['fragen'][v['kapitel']-1]
        row(v['niveau'],q['frage'],v['browser']+' · '+v['phase'],v['text'],{'help':'Hilfe','compare':'Vergleich'}.get(v['ansicht'],'Rückmeldung'),q['ziel'])
    perspectives="""# Planung der Vorbereitung · 45 Minuten

| Sicht | Konkreter Prüfpunkt und verbleibende Anforderung |
|---|---|
| Förder | Bild ansehen, ein Wort finden, dieselbe Lücke füllen. Bei fast fehlendem Textverständnis bleiben das Lesen der Frage und das Verstehen einer Grafik im Unterricht zu beobachten. |
| ESA | Samenzelle und Eizelle unterscheiden; nach einer Fehlwahl die genannte Stelle finden. |
| MSA | Eigene Ursache und Folge schreiben, ohne dass die Formulierung vorgegeben wird. |
| AHR | Alternativen sowie die Grenze einer Aussage benennen; unklare eigene Erklärungen am Beispiel prüfen. |
| Eine Lehrkraft mit 28 Lernenden | Vier Niveaustapel vorab auslegen, Papier beidseitig drucken. Die Klasse kann auf Papier einsteigen und die Hilfe selbst öffnen. Für einzelne Lernende eine gemeinsame Demonstration der ersten Lücke einplanen. |
| Studienleitung Biologie | Wirkmechanismus, Infektionsschutz, Zustimmung und Risiken im fachlichen Kontext. Die Kartenvollständigkeit belegt noch kein Verständnis. |
| Studienleitung Pädagogik | Sichtbare eigene Erklärung und selbstgewählter Hilfegrad; Lernwirkung der Hilfen mit Lernenden beobachten. |

Planungsannahme: 4 Minuten für Material und Einstieg, 20 für vier Karten, 13 für die vier Anwendungen, 6 für Sicherung und 2 für Reflexion. Die freiwillige Pearl-Index-Reserve beansprucht keine Pflichtzeit. Bei Zeitnot übernimmt die Lehrkraft die Sicherung mit dem tatsächlichen Papierstand. Die Zeiten sind keine Unterrichtsmessung.
"""
    pack(OUT/'CLT-Abnahme.zip',{'Matrix.csv':'\ufeff'+buf.getvalue(),'CLT-Lernwege.json.gz':(ROOT/'build/Kartenlernen/CLT-Lernwege.json.gz').read_bytes(),'Grundlagen.md':THEORIE,'Perspektiven-und-Zeit.md':perspectives,
      'Stand.json':json.dumps(dict(commit=head,gerenderte_wortlaute=len(views),diagnosefaelle=len(diag),sha256=sha((OUT/'Vorbereitung.html').read_bytes())),indent=2)})
