"""Vertrag aus echten Anzeigen und den zugehörigen Papierorten. Keine Schüler-PDFs erzeugen."""
import argparse,csv,gzip,io,json,re
from collections import defaultdict,Counter
from pathlib import Path
from auslieferung import QA,OUT,SRC,sha,pack,json_text
from endvergleich import vergleich,basis,REFERENZ
from endredaktion import inventory,AUSWAHL,freigaben
from karten import LEVELS,METHODS
from fundstellenbeleg import Lernwege
from redaktion import nachweise
from sprachpruefung import bank
from textvertrag import csvdata

def read(name):return json.loads((QA/(name+'.json')).read_text())
def narrow(s):return ' '.join(s.split())
def lines(rows):return '\n'.join(json.dumps(r,ensure_ascii=False,separators=(',',':')) for r in rows)+'\n'

class Bildschirm:
    def __init__(self):
        self.by=defaultdict(list)
        self.screens={}
        self.sources={}
        self.ganz=set()
    def add(self,m,t,text,buttons,ref,route,ganz=False):
        if not text.strip():return ''
        t='Förder' if t=='Foerder' else t
        pattern=AUSWAHL.search(text)
        assert not pattern,(m,t,ref,text[max(pattern.start()-70,0):pattern.end()+70]) if pattern else None
        key=sha((m+'\n'+t+'\n'+text).encode())[:22]
        if ganz:self.ganz.add(key)
        if key not in self.screens:
            self.screens[key]=dict(id=key,modul=m,niveau=t,bildschirm=text,bedienung=buttons,nachweis=ref)
            self.by[m,t].append((key,narrow(text),route))
        return key
    def collect(self):
        for f in sorted(QA.glob('Paarvergleich-*.ndjson.gz')):
            with gzip.open(f,'rt') as stream:
                for i,line in enumerate(stream,1):
                    r=json.loads(line);self.add(r['modul'],r['niveau'],r['ganzer_bildschirm'],r['bedienung'],f.name+'#'+str(i),r['weg'],True)
        for f in sorted(QA.glob('*.jsonl.gz')):
            with gzip.open(f,'rt') as stream:
                for i,line in enumerate(stream,1):
                    r=json.loads(line);self.add(r['modul'],r['niveau'],r['text'],r['bedienung'],f.name+'#'+str(i),'')
        for f in ('Work-Gegenprobe','Weitere-Papieransichten'):
            for i,r in enumerate(read(f),1):
                m=r.get('modul','UB02' if r['zustand']=='UB02-Stopp' else 'UB08')
                tier=r['niveau'].replace('Foerder','Förder')
                key=self.add(m,tier,r['bildschirm'],[],f+'.json#'+str(i),r['zustand'],True)
                self.sources[m,tier,r['zustand']]=key
    def find(self,m,t,needle,section=''):
        needles=[narrow(s) for s in ([needle] if isinstance(needle,str) else needle)]
        hits=[key for key,text,route in self.by[m,t] if key in self.ganz and all(s in text for s in needles) and (not section or route.startswith(section))]
        assert hits,(m,t,needles,section)
        return min(hits,key=lambda k:len(self.screens[k]['bildschirm']))

def matrix(docs,s):
    out=[]
    def add(m,t,section,state,sheet,page,title,field,action,back,dest,key):
        r=s.screens[key]
        assert key in s.ganz and t==r['niveau'] and r['modul']==m
        out.append(dict(modul=m,niveau=t,abschnitt=section,zustand=state,bogen=sheet,seite=str(page),ueberschrift=title,
                        feld=field,handlung=action,rueckkehrbutton=back,ziel=dest,bildschirm=r['bildschirm'],ansicht=key))
    prep=bank(docs['PREP'][0]);first=bank(docs['UB02'][0]);family=bank(docs['UB08'][0])
    for tier,t in LEVELS.items():
        for c in prep['levels'][tier]['chapters']:
            k=c['id'];title=METHODS[c['method']];n=int(k[0]);cardpage=1 if n<3 else 2;paperpage=cardpage+2
            numbers=', '.join(str(e['number'])+' · '+e['sectionTitle'] for e in c['cardEntries'])
            q=c.get('paperCheck');is_b=k.endswith('B')
            next_state={'2B':'Ende der ersten Vorbereitungsstunde','4B':'Abschluss der Vorbereitung'}.get(k,c['nextChapter'])
            add('PREP',t,k,'Kapitelbeginn','Laufzettel',paperpage,title,k,'Kästchen beim geöffneten Kapitel ankreuzen.','Zur Fachfrage',c['questions'][0]['prompt'],s.find('PREP',t,'Papier · Markiere '+k))
            state=s.find('PREP',t,c['paperPrompt'])
            add('PREP',t,k,'Freigegebene Wörter','Kartenblatt',cardpage,title,numbers,c['paperPrompt'],
                'Code prüfen' if q else 'Vollständige Karte vergleichen' if is_b else 'Weiter im Chat','Code-Rückmeldung' if q else 'Musterkarte '+title if is_b else next_state,state)
            if q:
                add('PREP',t,k,'Papier-Fachcheck','Laufzettel',paperpage,title,k+' · A/B/C und Begründung',q['screen']+' '+q['return'],
                    'Code prüfen → Nachricht senden → Weiter im Chat',next_state,state)
            if is_b:
                state=s.find('PREP',t,[c['title'],'Kreuze „Karte kontrolliert“'])
                add('PREP',t,k,'Kartenvergleich','Kartenblatt / Laufzettel',f'{cardpage} / {paperpage}',title,'Felder 1–4 / '+k+' · Karte kontrolliert','Alle vier Felder mit der Musterkarte vergleichen. Fehlendes ergänzen. Kartenkontrolle ankreuzen.','Weiter im Chat',next_state,state)
        for method,title in METHODS.items():
            add('PREP',t,'Ausfallhilfe',title,'Kartenblatt',1 if method in ('K','P') else 2,title,'Felder 1–4','Fehlende Wörter auf der passenden Kartenfläche ergänzen. Prüfungen bleiben offen.','Schließen','Vorherige Ansicht',s.sources['PREP',t,'Muster-'+method])
        add('PREP',t,'2B','Stundenende','Kartenblatt / Laufzettel','1 / 3','Kondom und Kombinationspille / Nach 2B','Felder 1–4 / Hier arbeite ich weiter','Beide Methodenflächen prüfen. Nächstes Kapitel eintragen.','Jetzt mit 3A weiterarbeiten oder Abschnitt auswählen','3A oder Abschnittsauswahl',s.find('PREP',t,'Ende der ersten Vorbereitungsstunde\nDu hast Kondom'))
        add('PREP',t,'4B','Abschluss','Kartenblatt','1–2','Alle vier Methodenflächen','Felder 1–4','Mit den Musterkarten vergleichen. Ergänzen. Duplexblatt einmal durchschneiden und beide Karten aufbewahren.','Schließen (Musterkarte) / Abschnitt auswählen','Abschluss / Abschnittsauswahl',s.find('PREP',t,'Zwei doppelseitige Infokarten kontrollieren'))
        add('PREP',t,'Neustart','Abschnitt wählen','Laufzettel','3–4','Laufzettel 1A bis 2B / 3A bis 4B','zuletzt markiertes Kapitel','Markierung lesen. Dieses oder das folgende offene Kapitel öffnen.',' / '.join(c['title'] for c in prep['levels'][tier]['chapters']),'Einstieg in das gewählte Kapitel',s.find('PREP',t,'Laufzettel: Suche das zuletzt markierte Kapitel'))
        add('UB02',t,'L01','Einstieg','Laufzettel',1,'Laura 1 – Latexallergie','Mein erster Rat','Analogen ersten Rat lesen.','Neu beginnen','Laura 1',s.sources['UB02',t,'Einstieg'])
        add('UB02',t,'Wiederaufnahme','Abschnitt wählen','Laufzettel','1–5','Laura 1 bis Laura 5','Markierung am letzten Abschnitt','Letzten bearbeiteten Abschnitt lesen und im gewählten Fall öffnen.',' / '.join(c['title'] for c in first['stages'].values()),'Ausgewählter Abschnitt',s.sources['UB02',t,'Neustart'])
        for i,(k,c) in enumerate(first['stages'].items(),1):
            task=c['levels'][tier]
            if task['paperPrompt']:
                state=s.find('UB02',t,task['paperPrompt'],k)
                for cond,act,lookup in [('Empfehlung gewählt',task['paperPrompt'],state),('Ersatzanzeige ohne Bogen',first['paperFallbackInstruction'],s.sources['UB02',t,k+'-Ausfall']),('Geänderte Empfehlung','Begründung lesen und bei geändertem Grund ergänzen. Buchstaben noch einmal prüfen.',s.sources['UB02',t,k+'-Wechsel'])]:
                    add('UB02',t,k,cond,'Laufzettel',i,c['title'],'Mein Schlussrat / A/B/C' if i==5 else 'Begründung / A/B/C',act,'Code prüfen','Rückmeldung zur markierten Aussage',lookup)
            if i==5:
                state=s.find('UB02',t,task['task'],k)
                if tier in ('MSA','AHR'):
                    back='Code prüfen'
                else:
                    buttons=s.screens[state]['bedienung']
                    options={o['text'] for way in task['strategies'].values() for o in way['options']}
                    present=[b for b in buttons if isinstance(b,str) and b in options]
                    if not present:
                        # The chosen example must precede the answer, with actual available reply labels.
                        state=next(key for key,txt,route in s.by['UB02',t] if key in s.ganz and route.startswith(k)
                                   and narrow(task['task']) in txt and any(o in s.screens[key]['bedienung'] for o in options))
                        present=[b for b in s.screens[state]['bedienung'] if b in options]
                    back=' / '.join(present)+' → Nachricht senden'
                add('UB02',t,k,'Regulärer Schlussrat','Laufzettel',5,c['title'],'Mein Schlussrat',task['task'],
                    back,'Fachrückmeldung / Lauras Antwort',state)
                add('UB02',t,k,'Stopp der Lehrkraft','Laufzettel',5,c['title'],'Mein Schlussrat',task['task'],'Kein digitaler Rückkehrknopf erforderlich','Unterrichtsgespräch',s.sources['UB02',t,'UB02-Stopp'])
        if tier in ('MSA','AHR'):
            for m in ('Tom','Celina'):
                for i,c in enumerate(bank(docs[m][0])['stages'],1):
                    title=f'{m} {i} – '+c['title'];state=s.find(m,t,'Zusatzbogen '+m+' · Seite '+str(i))
                    add(m,t,str(i),'Freiwilliger Fachcheck','Zusatzbogen '+m,i,title,'Begründung / A/B/C',c['task'][tier]+' Begründung aufschreiben und die richtige Aussage einkreisen.','Code prüfen → Nachricht senden','Fachrückmeldung / Antwort von '+m,state)
        for k,step in family['media']['steps'].items():
            prefix=k.split('-')[0];page={'MU':2,'FR':3,'GM':1,'VA':2,'LA':4}[prefix]
            sheet='Vertiefungsbogen' if prefix in ('GM','VA') else 'Pflichtlernbogen'
            r=step['orders'][t];field=step['field'];back=step['buttonText']
            if step['mode']=='gleicher Abschnitt':
                if tier in ('MSA','AHR'):back='Mit den Aussagen vergleichen'
                else:
                    paper=family['media']['fields'][field]
                    back=' / '.join(paper['foerder' if tier=='Foerder' else 'options'])
            if k=='LA-eigen':
                field={'Foerder':'1. Lauras Frage / 2. Fakt (M oder F) / 3. Nachricht / 4. Warum hilft der Fakt Laura?',
                    'ESA':'Meine Wahl und Lauras Frage(n) / Der passende Fakt dazu ist / Das hilft Laura zu verstehen'}.get(tier,'Lauras Frage – Meine Antwort')
            add('UB08',t,step['sectionId'],k,sheet,page,step['section'],field,r['action'],back or 'Kein Knopf · Lernbogen mitnehmen',step['nextId'] or 'Besprechung auf Papier',s.sources['UB08',t,k])
        add('UB08',t,'LA-04','Prüfung am iPad offen','Pflichtlernbogen',4,'Lauras Frage – Festhalten','Festhalten','Zur persönlichen Prüfung gehen. In diesem Zustand ist kein neuer Papiereintrag verlangt.',family['evaluationSteps'][2],'LA-03',s.sources['UB08',t,'LA-offen'])
    return out

def materialtext(commit):
    return f"""# Satzauftrag für Work

Software {commit}. Die Medienwechselmatrix enthält je Niveau die verbindliche Seite, Überschrift, das Feld, den Bildschirmwortlaut, die Handlung und den Rückweg. Die vier Schüler-PDFs und die beiden geprüften Pflichtbögen sind Referenzen. In dieser Runde wurde kein PDF bearbeitet.

## Alle Materialien

- Schüleraufträge durchgehend im Singular schreiben. Personenwahl, Nummern 1 und 2 für Lernende, Rollen, Vorlesewechsel, Reihenfolgen zwischen Personen und verpflichtende Gespräche streichen. Das gilt auch für Ausfallbögen, Hilfen, Übersichten und Neustartkästen.
- Eine persönliche Antwort bleibt sichtbar, wenn sie später überprüft oder ergänzt wird. Die Software prüft auswählbare Fachinformationen. Eine freie Begründung erhält im Programm kein fachliches Urteil.
- Jeder Rückweg trägt die Beschriftung des tatsächlichen Knopfs. Steht in der Matrix eine Antwort als Rückweg, ist genau diese Auswahl die digitale Handlung. Bei der Besprechung auf Papier gibt es keinen zusätzlichen Abschlussknopf.

## Vorbereitung

- Seite 1 trägt Kondom und Kombinationspille, Seite 2 Kupfer- und Hormonspirale. Die 64 Einträge, ihre Nummern und die 16 Musterkarten aus den Druckreferenzen wortgleich übernehmen. Das Kartenblatt bleibt doppelseitig.
- Der separate Laufzettel steht auf Seite 3 für 1A bis 2B und auf Seite 4 für 3A bis 4B. In den A-Kapiteln mit Papier-Fachcheck bleiben A, B, C und das Feld „Begründung“ in ihrer geprüften Reihenfolge. Der genaue Abgleich der digitalen Ersatzanzeige steht im Bildschirmvertrag.
- In B-Kapiteln zuerst „Vollständige Karte vergleichen“, danach „Karte kontrolliert“ auf dem Laufzettel ankreuzen und „Weiter im Chat“ antippen. „Nach 2B“ enthält „Hier arbeite ich weiter“. Am Ende alle vier Methodenflächen prüfen, ergänzen und einmal durch die Mittellinie schneiden. Beide doppelseitigen Karten aufbewahren.

## 02.12. · Beratung

- Für den Satz je eine Seite für Laura 1 bis 5 vorsehen. „Mein erster Rat“ steht auf Seite 1, „Mein Schlussrat“ auf Seite 5. Die ersten vier Seiten tragen die jeweilige Laura-Überschrift aus der Matrix. Auf MSA und AHR die freien Zeilen, A/B/C-Aussagen und deren Prüfcodes beibehalten.
- Den Schlussrat nach Niveau in den kurzen Schritten des Softwarevertrags setzen. Beim Stopp der Lehrkraft kann auf Seite 5 geschrieben werden, auch wenn im Chat noch Abschnitte offen sind. Dafür ist kein Prüfcode nötig. Beide Abstimmungen mit dem Empfehlungsrad ausschließlich im Lehrkraftmaterial anleiten.
- Tom erhält einen freiwilligen Zusatzbogen mit drei Abschnittsseiten, Celina einen mit fünf. Die Zuordnung gilt für den Neusatz. Bei MSA und AHR pro Abschnitt „Begründung“ und A/B/C vorsehen. Auf Förder und ESA entsteht daraus keine neue Schreibaufgabe. Toms Forschungsartikel und Studienkästen bleiben zugänglich.

## Konkrete Druckkorrekturen in den Pflichtbögen vom 25.11.

| Seite | Bisheriger Druckhinweis | Verbindlicher Neusatz |
|---|---|---|
| 2 | „Öffnet“, „Wählt euer Niveau bei Person 1 …“, „Tippt“ | „1. Öffne Dienstag, 08.12.2026. 2. Wähle dein Niveau. 3. Tippe auf Mutter – Nachricht öffnen.“ |
| 2–3 | „Lest die Nachricht. Bearbeitet den Argumenten-Check.“ | „Lies die Nachricht. Bearbeite den Argumenten-Check.“ |
| 2–3 | „Bei Dein Lernbogen … jede Person für sich“ | Den konkreten Hinweis „Pflichtlernbogen · Seite 2“ bzw. „Pflichtlernbogen · Seite 3“ und den Feldnamen aus der Matrix übernehmen. |
| 2–3 | „Erste Antwort allein ankreuzen“ | „Setze dein erstes Kreuz links in Meine erste Antwort.“ Rechts bleibt Platz für den geprüften Fakt. |
| 3 | „Wechselt: Wer gelesen hat, tippt jetzt.“ / „Behaltet eure Personennummer und euer Niveau.“ | Beide Zeilen streichen. Es gibt keine Ersatzhandlung. |
| 4 | „Jede Person antwortet zuerst allein.“ | „Meine Antwort“ und darunter die nummerierten Schritte des jeweiligen Niveaus. |
| 4 | „Prüft nacheinander unter eurer Personennummer.“ | „Tippe auf Meine Antwort prüfen.“ |
| 4 | „Prüfe deinen Fakt …“ bzw. „Prüfe Fakt und Grund …“ | Den zustandsabhängigen Auftrag für „Festhalten“ aus der Matrix übernehmen. Erste Antwort lesbar lassen. |
| 2–4 | „gleiche Niveaus“, „eigene Person“ | „Nach Neustart“ → dein Niveau → Nachricht bzw. „Lauras Frage“ → Abschnitt → „Hier weiterarbeiten“. Prüfabschnitt und Festhalten unterscheiden. |

## 08.12. · Familiennachrichten

- Pflichtbogen Seite 1 für die Orientierung, Seite 2 „Mutter – Fakt“, Seite 3 „Freundin – Fakt“, Seite 4 für Lauras persönliche Antwort, Prüfung und „Festhalten“. Auf Seiten 2 und 3 stehen dieselben Aussagen nur einmal. Links „Meine erste Antwort“, rechts „Nach dem Prüfen“. Das erste Kreuz bleibt. Auf MSA und AHR die getrennten Schreibfelder erhalten.
- Auf Seite 4 für Förder die Fragen nach Beschwerden und späteren Kindern, M und F vor der passenden biologischen Information, die Wahl einer oder beider Nachrichten und die persönliche Begründung erhalten. Bei ESA gelten die vorhandenen Schreibfelder für Wahl und Frage, passenden Fakt und Erklärung. Bei MSA bleibt die Begründung in zwei bis drei Sätzen, bei AHR der Vergleich samt Aussagegrenze.
- Auf „Meine Antwort prüfen“ folgt LA-03. Dort bleiben Wahl der Frage, Zuordnung der Information und Grenze dieser Information unterscheidbar. Bei beiden Nachrichten werden beide Bezüge geprüft.
- LA-04 hat zwei Zustände. Nach digitaler Prüfung die erste Antwort lesen und eine mögliche Verbesserung im Feld „Festhalten“ eintragen. Beim direkten Einstieg ohne digitale Prüfung führt „Lauras Frage – Prüfen“ zu LA-03. Den alten Druckauftrag „Prüfe deinen Fakt“ und alle Verweise auf eine Personennummer entfernen. Ein auf Papier bereits vorhandenes Ergebnis bleibt lesbar. Die Einträge „digital geprüft“, „analog geprüft“ und „noch offen“ dürfen unterschiedliche Nachweise bezeichnen.
- Freiwilliger Vertiefungsbogen, Seite 1 „Großmutter – Wert“, Seite 2 „Vater – Norm“. Auch hier den ersten und den geprüften Eintrag trennen. Die Frage nach dem persönlichen Wert bzw. der allgemeinen Regel verwenden. Die Arbeitsaufträge zum biologischen Fakt der Mutter oder Freundin passen hier nicht.
- Für Ausfallbögen dieselben Überschriften, Seitenverweise und Hilfestufen verwenden. Platz und Zeilenumbrüche der neu gesetzten Seiten anschließend am Ausdruck prüfen. Der Abgleich gegen die vorliegenden Förder-/ESA-Pflichtbögen betrifft Seiten 2 bis 4. Die übrigen Seitenvorgaben sind Satzvorgaben für Work.
"""

def vertrag(ref):
    old,new=vergleich(ref);texts=Bildschirm();texts.collect()
    rows,previous=inventory(old,new);handoffs=matrix(new,texts)
    assert freigaben(rows)==json.loads((SRC/'pruefgrundlagen/Sprachfreigabe-Endstand.json').read_text()), 'Wortlaut, Adresse oder Prüfgrund nach der Sprachprüfung verändert'
    commit=new['START'][0].xpath('string(//meta[@name="revision"]/@content)')
    # Put each complete source text in the index and connect exact rendered lines.
    index=defaultdict(dict)
    for key,r in texts.screens.items():
        for value in [*r['bildschirm'].splitlines(),*(b[1] if isinstance(b,list) else b for b in r['bedienung'])]:
            index[r['modul']].setdefault(narrow(value),key)
    wege=Lernwege(QA)
    altfreigabe=nachweise(new)
    for r in rows:
        text=r['wortlaut']
        parts=r['stelle'].split('/')
        tier=next((x for x in parts if x in (*LEVELS,'Förder')),'alle')
        r['niveau']=tier.replace('Foerder','Förder')
        r['gleicher_lernweg']=''
        if r['quelle']=='JSON' and isinstance(text,str) and len(text)>2 and not r['art'].startswith(('Technisch','Material-','Bildvorlage','Schaubild')):
            r['gleicher_lernweg']=wege.find(r['modul'],tier,r['stelle'],text)
        if (r['modul'],r['stelle']) in altfreigabe:
            r['uebernommene_einzelpruefung']=altfreigabe[r['modul'],r['stelle']]
        else:r['uebernommene_einzelpruefung']=''
        key=index[r['modul']].get(narrow(text),'') if isinstance(text,str) else ''
        r['wortlaut_im_browser']=key
    # All addresses of the old open ledger must have a successor or an individually
    # identified removal. This guards against closing unmapped records by counting them.
    for p in previous:
        if p['bisher']=='Einzelprüfung offen' and not p['zeilen_neuer_vertrag']:
            assert p['modul']=='UB08' and (p['fundstelle'].startswith('ui/') or p['fundstelle']=='screens/Erste-Nachricht-und-Team.jpg'),p
    work=materialtext(commit)
    pack(OUT/'Fallakte-Bildschirmtextvertrag.zip',{**{'Laufzeitvergleich/'+name+'.jsonl':raw for name,(raw,count) in wege.pairs.items()},
        'Einzelfreigaben-SHA256.json':json_text(freigaben(rows)),
        'Liesmich.md':f"""# Bildschirmtextvertrag

Softwarecommit {commit}. Vergleichsstand {REFERENZ}.

Medienwechselmatrix.csv enthält die Papieraufträge mit einer vollständig ausgeschriebenen beobachteten Bildschirmansicht. Bildschirmzustaende.jsonl erfasst weitere Varianten mit Fallnachrichten, individuellen Rückfragen, Hilfeaufrufen und Fehlern. Die Ansichtskennung verknüpft beide Dateien. Die Matrix enthält auch die sichtbare Navigation der Elternrahmen. Bei einem offenen Dialog nennt sie den aktiven Dialog und die äußere Navigation. Eine frühere Nachricht im Verlauf kann den Gesamtwortlaut verlängern.

Quellfundstellen.csv inventarisiert die gebauten Moduldaten, JavaScript-Werte und Vorlagen, HTML-Beschriftungen und SVG-Texte. Komplette gerenderte Zeilen sind, wo wortgleich beobachtet, zusätzlich über eine Ansichtskennung belegt. Texte aus mehreren DOM-Knoten sind im Gesamtbildschirm nachlesbar. Der Prüfgrund beschreibt die redaktionelle oder technische Einordnung. Einzelfreigaben-SHA256.json bindet Wortlaut, Fundstelle und Prüfgrund der Schülertexte je Modul an diese Fassung. Technische Werte und Planungsangaben sind gesondert benannt. Als Quellenverweise dienen Modul, Adresse und Inhalt; identische Texte können an mehreren Stellen verwendet werden.

Rueckverfolgung-3565a45.csv verbindet alle 13.436 Einträge der früheren Übergabe mit dem neuen Inventar. Alt-Offen-3571.csv enthält die ehemals offenen Einträge. Die beim direkten Einstieg entfernte Selbstauskunft und die entfallenen Teamanzeigen sind ausdrücklich ausgewiesen.

Die ursprünglichen Druck-PDFs gelten für den Vergleich der Karten und der beiden unteren Pflichtbögen. Die Matrix gibt die Seiten für den Neusatz verbindlich an. Keine Schülerdaten, nur simulierte Testeingaben.
""",'Quellfundstellen.csv':csvdata(rows),'Rueckverfolgung-3565a45.csv':csvdata(previous),
        'Alt-Offen-3571.csv':csvdata([r for r in previous if r['bisher']=='Einzelprüfung offen']),
        'Medienwechselmatrix.csv':csvdata(handoffs),'Bildschirmzustaende.jsonl':lines(texts.screens.values()),'Materialaenderungen-Work.md':work})
    (OUT/'Materialaenderungen-Work.md').write_text(work)
    (OUT/'Medienwechselmatrix.csv').write_text(csvdata(handoffs),encoding='utf-8-sig')
    (QA/'Endumfang.json').write_text(json_text(dict(commit=commit,quellen=len(rows),alte_quellen=len(previous),ehemals_offen=3571,
        entfernte_offene=sum(p['bisher']=='Einzelprüfung offen' and not p['zeilen_neuer_vertrag'] for p in previous),
        papierwege=len(handoffs),ansichten=len(texts.screens),
        entscheidungen=dict(Counter(r['entscheidung'] for r in rows)),quelltypen=dict(Counter(r['art'] for r in rows)),
        fundstellen_mit_lernweg=sum(bool(r['gleicher_lernweg']) for r in rows),
        module=dict(Counter(r['modul'] for r in texts.screens.values())))))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--referenz',type=Path);args=parser.parse_args()
    vertrag(args.referenz or basis())
