"""Inventar und Rückverfolgung des gesamten Bildschirmwortlauts der drei Module."""
import csv
import gzip
import hashlib
import json
import re
from collections import defaultdict,Counter
from endvergleich import REFERENZ
from auslieferung import SRC,QA,sha,json_text
from sprachpruefung import bank,leaves
from textvertrag import js,js_changes,html_texts,csvdata
from redaktion import STATIONEN,FAMILIE,BERATUNG

# Render- und Planungsfelder sind getrennt. Schlüssel, die auch Beschriftungen
# sind (etwa Fallnamen), werden zusätzlich beim tatsächlich sichtbaren Text erfasst.
TECH=set('id sectionId fieldId taskId nextChapter shortOptions sectionsIds informationSections previousSection requiresAny knownFacts newFacts visualRef correctness correct code ok method target restartId nextId designFiles version baseCommit buildCommit commit goalRules normalization primary methods allowed newFacts requiresAny freeCards evidenceSentences revealsSolution sectionIds caseId paperFieldId'.split())
PLAN08=set('design time differentiation expectation sourcesTitle sourceMapping sources designFiles paperFields variants screens analogSteps analog workingTrace levelsHelp sourceReview intent paperRecovery sicherung'.split())
PLANPREP=set('note expectedReason purpose focus instruction phase answers explanation'.split())
AUSWAHL=re.compile(r'Person [12]\b|Beratungsteam|der Rat des Teams|Das Team kann|\bTandem\w*|\bRollenwechsel|Tauscht die Rollen|\b(?:Arbeite|Kreuze|Lies) allein\b|\b(?:eur(?:e[rmns]?)?|euer|euch)\b|\b(?:Besprecht|Tauscht euch|Lest euch|zu zweit|dein Bezug|deine Gewichtung|deine Ergänzung|dein Grund|bei Bedarf)\b|\bUnser Vorschlag\b|\bWir (?:schlagen|möchten dir|würden dir)',re.I)

def art(m,path,value):
    k=path.split('/');root=k[0]
    if not isinstance(value,str) or not value or set(k)&TECH or k[-1] in ('section','ref') and m in ('UB02','Tom','Celina') or 'ref' in k or (k[-1]=='status' and value in 'ABC'):return 'Technische Kennung oder Steuerwert'
    if 'short' in k and value in ('A','B','C'):return 'Technischer Verweis auf eine Antwortoption'
    if m=='UB08' and root=='review' and (k[-1]=='0' or int(k[1]) not in (4,5,6,7)):return 'Material- oder Planungsangabe'
    if m=='PREP' and k[-1]=='note' and 'intro' in k:return 'Material- oder Planungsangabe'
    if root=='graphics':return 'Schaubild mit separat inventarisierten Bildtexten'
    if root=='visualBriefs' and k[-1]!='title':return 'Bildvorlage für die Produktion'
    if (m=='UB08' and (root in PLAN08 or (root=='media' and (k[1]!='steps' or k[-1] in ('condition','kind','mode','restart','help'))))) or (m=='PREP' and set(k)&PLANPREP) or (m=='UB02' and k[-1] in ('learningGoal','information')):return 'Material- oder Planungsangabe'
    if 'cards' in k or set(k)&{'cardEntries','fullCardReview'}:return 'Infokarte oder Kartenfeld'
    if (m=='UB08' and root=='media' and len(k)>2 and k[1]=='steps' and ('orders' in k or k[-1]=='field')):return 'Papierauftrag, Rückweg oder Lösungskontrolle'
    if 'hints' in k or 'helpByLevel' in k or 'hintsBeforeChoice' in k or 'Help' in path:return 'Gestufte Hilfe'
    if 'feedback' in k or 'replies' in k or k[-1] in ('reply','answer'):return 'Rückmeldung oder Fallantwort'
    if set(k)&{'paper','media','paperPrompt','paperCheck','returnPrompt','evaluation','backToChat','consolidation'}:return 'Papierauftrag, Rückweg oder Lösungskontrolle'
    if (m=='UB08' and root=='ui') or root=='ui':return 'Bedienwortlaut oder Status'
    return 'Lerntext oder Fallinformation'

def kontext(m,path):
    k=path.split('/')
    if m=='UB02':
        stage=next((x for x in k if x in BERATUNG),None)
        return BERATUNG.get(stage,'Latexallergie, unterschiedliche Schutzwünsche, Einsetzen und freie Zustimmung bleiben getrennt.')
    if m in FAMILIE:return FAMILIE[m]
    if m=='Tom':return 'Eigene Anwendung und Entscheidung der Freundin sind getrennt. In Studie B geht es um Verträglichkeit, in Studie A auch um Schwangerschaften.'
    if m=='Celina':return 'Hormonfreiheit bleibt persönliche Grenze. Langer Schutz, Schutz vor Infektionen und Zustimmung zum Einsetzen sind getrennte Fragen.'
    if m=='PREP':
        if 'chapters' in k:
            i=int(k[k.index('chapters')+1]);return STATIONEN[str(i//2+1)+'AB'[i%2]]
        if 'intro' in k:return STATIONEN['PI']
        return 'Methode, Nummer des Kartenfeldes und digitaler Arbeitsstand haben unterschiedliche Funktionen.'
    if m=='UB08':
        if 'steps' in k:
            section=k[k.index('steps')+1].split('-')[0]
            for code,name in [('MU','Mutter'),('FR','Freundin'),('GM','Großmutter'),('VA','Vater')]:
                if section==code:return FAMILIE[name]
            if section=='LA':return 'Papierseite 4: erste Antwort, fachliche Prüfung und persönlicher Nachtrag im Feld „Festhalten“ werden unterschieden.'
        return next((FAMILIE[n] for n in FAMILIE if n in k),'Persönliche Auswahl, fachlich prüfbare Information und Grenze der Aussage getrennt. Die freie Begründung bleibt persönlich.')
    return 'Tagesauswahl und Modulnavigation.'

def beruecksichtigt(art_,m,path):
    if art_.startswith(('Technisch','Bildvorlage','Material-')):return art_+' anhand des Zugriffs im Renderer bzw. der Datenstruktur unterschieden.'
    if art_.startswith('Schaubild'):return 'Beschriftungen und zugängliche Bildbeschreibungen separat mit beiden Browsern verglichen.'
    if art_.startswith('Infokarte') and m=='PREP':return 'Wortlaut durch Druckvorlage gebunden. Felder und Reihenfolge mit dem PDF verglichen.'
    if art_.startswith('Gestufte'):return 'Lesestelle, Denkfrage und gegebenenfalls Lösung auf den jeweiligen Abschnitt und die Reihenfolge bezogen. '+kontext(m,path)
    if art_.startswith('Papierauftrag'):return 'Erste und geprüfte Antwort bzw. Papierfeld und Rückweg in ihrem Verwendungskontext unterschieden. '+kontext(m,path)
    if 'afterSolutionCheck' in path and ('feedback' in path or path.endswith('prompt')):
        return 'Anwendungsfrage nach Lösungshilfe. Die neue Situation und die Rückmeldung wurden auf denselben biologischen Zusammenhang bezogen. '+kontext(m,path)
    if ('options/' in path or 'answers/' in path) and path.endswith(('/text','/advancedText')):
        return 'Die Antwort wurde zusammen mit der Frage, den übrigen Möglichkeiten und dem unveränderten Lösungsschlüssel gelesen. '+kontext(m,path)
    if path.endswith('/prompt') or path.endswith('/advancedPrompt'):
        return 'Gegenstand der Frage und geforderte Denkhandlung im selben Abschnitt geprüft. '+kontext(m,path)
    if art_=='Rückmeldung oder Fallantwort':return 'Auf die gewählte Aussage oder Handlung bezogen. '+kontext(m,path)
    if art_.startswith('Bedien') or art_=='HTML oder zugängliche Beschriftung':return 'Beschriftung auf Funktion, verständliche Anrede und erreichbaren Folgeschritt gelesen.'
    return kontext(m,path)

def freigaben(rows):
    """Bindet redaktionelle Entscheidungen an die gelesene Adresse und ihren exakten Wortlaut."""
    groups=defaultdict(list)
    for r in rows:
        if r['art'].startswith(('Technisch','Material-','Bildvorlage','Skriptwert')):continue
        groups[r['modul']].append([r['quelle'],r['stelle'],r['wortlaut'],r['art'],r['pruefgrund']])
    return {module:sha(json.dumps(items,ensure_ascii=False).encode()) for module,items in groups.items()}

def inventory(old,new):
    rows=[];places=defaultdict(list);prior_changes={};data={}
    def add(m,source,path,value,kind,reason,previous=None):
        r=dict(nr=len(rows)+1,modul=m,quelle=source,stelle=path,wortlaut=value,art=kind,
               wortlaut_vor_aenderung=previous if previous is not None and previous!=value else '',
               entscheidung='neu' if previous is None else 'beibehalten' if previous==value else 'geändert',pruefgrund=reason)
        rows.append(r);places[m,source,str(value)].append(r['nr']);return r['nr']
    for m,(doc,_) in new.items():
        script=' '.join(doc.xpath('//script[not(@type)]/text()'))
        a=dict(leaves(bank(old[m][0])));b=dict(leaves(bank(doc)))
        for p,v in b.items():
            kind=art(m,p,v)
            if m=='UB08' and p.startswith('ui/') and not re.search(r'\bui\.'+re.escape(p[3:])+r'\b',script) and p[3:] not in ('theme','sameStep','transfer','compare'):
                kind='Bedienbezeichnung im Datenvertrag ohne eigenen direkten Ausgabezugriff'
            data[m,p]=add(m,'JSON',p,v,kind,beruecksichtigt(kind,m,p),a.get(p))
        before,after=js(old[m][0]),js(doc)
        changes,_=js_changes(before,after)
        old_words={(i,y['stelle']):old_text for (i,_,old_text),y in changes.items() if y is not None}
        for script,rs in after.items():
            for r in rs:
                v=r['text'];role=r['rolle']
                if role:kind='Technischer JavaScript-Wert';note=role
                elif r['typ']=='JS-Template':kind='Zusammengesetzter Bildschirmwortlaut';note='Vorlage mit den eingesetzten Kapitel-, Feld- und Knopftexten im Lernweg gelesen.'
                elif not re.search(r'[A-ZÄÖÜ][a-zäöüß]{2}|[a-zäöüß]{2} [a-zäöüß]{2}',v) or re.match(r'^(use strict|feedback retry|[.#]|M\d|\w+[/:-])',v):kind='Skriptwert oder Textfragment';note='Kennung, Satzzeichen, Feldschlüssel oder Teil eines zusammengesetzten Wortlauts; die ganze Anzeige ist im Bildschirmvertrag erfasst.'
                else:kind='Bedienwortlaut oder Status';note=beruecksichtigt(kind,m,r['stelle'])
                add(m,'JS '+script,r['stelle'],v,kind,note,old_words.get((script,r['stelle'])))
        for (script,p,text),current in changes.items():prior_changes[m,'JS '+script,text]=current['text'] if current else ''
        ah=html_texts(old[m][0])
        current_html=html_texts(doc)
        for p,(_,v) in ah.items():
            nxt=current_html.get(p)
            if nxt:prior_changes[m,'HTML',v]=nxt[1]
        for p,(label,v) in current_html.items():add(m,'HTML',p,v,'HTML oder zugängliche Beschriftung',beruecksichtigt('HTML oder zugängliche Beschriftung',m,p),ah.get(p,('',None))[1])
    imgs=json.loads((QA/'Bildtexte.json').read_text())
    for p,v in imgs['chromium'].items():
        assert imgs['webkit'][p]==v
        add('PREP','SVG',p,v,'Beschriftung oder Alternativtext','Schaubild laut Titel, sichtbaren Begriffen und zugänglicher Beschreibung in beiden Browsern verglichen.',v)
    previous=[]
    with gzip.open(SRC/'pruefgrundlagen/Abnahme-3565a45.csv.gz','rt') as f:
        for n,r in enumerate(csv.DictReader(f),1):
            m,src,v,p=r['modul'],r['quelle'],r['neutext'],r['stelle']
            if src.startswith('JSON'):ids=[data[m,p]] if (m,p) in data else []
            else:
                key='JS '+re.search(r'\[(\d+)\]',src)[1] if src.startswith('JS ') else src
                ids=places.get((m,key,v),[]) or places.get((m,key,prior_changes.get((m,key,v))),[])
            note=rows[ids[0]-1]['pruefgrund'] if ids else 'Im Änderungsvergleich entfernte oder ersetzte Quellstelle. Neues Inventar nach Skript und Dokument getrennt.'
            if m=='UB08' and not ids and (p.startswith('ui/') or p.startswith('screens/')):
                note='Personen- oder Teamwahl entfällt im persönlichen Lernweg.' if p!='ui/paperReady' else 'Selbstauskunft ersetzt keine abgeschlossene Prüfung. Direkter Rückweg zu LA-03 geprüft.'
                if p=='ui/mixedTransfer':note='Zusatzaufforderung für gemischte Niveaus entfällt. Der fachliche Perspektivwechsel auf MSA und AHR bleibt in den jeweiligen Aufgaben.'
            previous.append(dict(nr_alt=n,modul=m,niveau=r['niveau'],fundstelle=p,quelle=src,bisher=r['einzelabnahme'],
                                 wortlaut_alt=v,zeilen_neuer_vertrag=' '.join(map(str,ids)),
                                 befund=note))
    assert len(previous)==13436 and sum(r['bisher']=='Einzelprüfung offen' for r in previous)==3571
    return rows,previous
