"""Lesbare Einzelnachweise am ausgelieferten Bildschirm, einschließlich der Dialogvarianten."""
import csv
import hashlib
import json
from io import StringIO
from collections import Counter
import re

def tabelle(kopf):
    out=StringIO(newline='')
    writer=csv.writer(out,delimiter=';',lineterminator='\n')
    writer.writerow(kopf)
    return out,writer

def wortregister(banken):
    """Referenz auch für aufklappbare Quellen und selten kombinierte Wortlaute."""
    out,writer=tabelle(['Modul','Feld im ausgelieferten Dokument','Wortlaut'])
    skip={'designFiles','commit','baseCommit','buildCommit','version','kartenbilder','paper','return','learningGoal',
          'status','id','taskId','code','correctionCode','sectionId','correct','levelsMap','goalRules','consolidation'}
    def visit(modul,path,value):
        if isinstance(value,dict):
            for key,child in value.items():
                if key not in skip:visit(modul,path+[key],child)
        elif isinstance(value,list):
            for i,child in enumerate(value):visit(modul,path+[str(i+1)],child)
        elif isinstance(value,str) and len(value)>2 and not value.startswith(('data:','<svg')):
            writer.writerow([modul,' / '.join(path),value])
    for modul,bank in banken.items():visit(modul,[],bank)
    return out.getvalue()

def audit(rows,tag,revision,sha,logs,bilder):
    screen,sw=tabelle(['Ansicht','Niveau','Fall','Schritt','Auslöser','Aufgabenfeld','Arbeitsfläche','Aktueller Chatbezug','Rückmeldung'])
    elements,ew=tabelle(['Ansicht','Steuerung','Sichtbare Beschriftung oder zugänglicher Name','Gesperrt'])
    checklist,cw=tabelle(['Ansicht','1 Was ist gemeint?','2 Welches Element?','3 Rückgriff auf früheren Auftrag nötig?',
                          '4 Operator in Handlung übersetzen?','5 Konkretisierung','6 Kann der Auftrag entfallen?'])
    forbidden=('Vergleiche deinen Grund.', 'Nutze das Material.', 'Überarbeite deine Einschätzung.',
               'Wähle den nächsten Schritt.', 'Vergleiche deinen Gedanken mit dem Beispiel.',
               'Lies die Information.', 'Prüfe deinen Grund.')
    counts=Counter()
    def add(tier,r):
        cue=r.get('cue','')
        text=r['text']
        controls=r.get('buttons') or [dict(id='',wort=s,gesperrt=False) for s in r['ids']]
        names=[e['wort'].strip() for e in controls if e['wort'].strip()]
        rowid=hashlib.sha256(json.dumps([tier,r],ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:16]
        context=r['caseName'] or r['question']
        anchor=r.get('message','')
        feedback=r.get('feedback','')
        sw.writerow([rowid,tier,context,r['task'],r['event'],cue,text,anchor,feedback])
        for c in controls:ew.writerow([rowid,c.get('id',''),c['wort'],c['gesperrt']])
        lines=[s.strip() for s in text.splitlines() if s.strip()]
        action=cue or r.get('title') or r['question'] or next(iter(lines),'')
        category=('Hilfe' if 'Hilfe ' in action or 'Hilfe ' in (lines or [''])[0] else 'Eingabe' if any(c.get('id') in ('erklaerung','compare','spur-grund') for c in controls)
                  else 'Rückmeldung' if feedback else 'Auswahl' if any(c.get('id','').startswith(('answer-','grund-','strategie-','level-','weight-')) for c in controls)
                  else 'Lesen oder Navigation')
        counts[tier,category]+=1
        ref=' / '.join(re.findall(r'„[^“]+“',cue)) or anchor or context or action
        current=next((s for s in lines if any(w in s for w in ('Pille','Kondom','Spirale','Karte','Mama','Mutter','Freundin','Großmutter','Vater','Studie','Laura','Celina','Tom'))),action)
        # Keine Vermutung über das Lesevermögen; je Zeile die tatsächlich prüfbaren Bezugspunkte.
        source='Chatwortlaut in derselben Ansicht erfasst.' if anchor else 'Aktueller Wortlaut: '+current
        operation={'Hilfe':'Hinweis lesen; Rückweg über Dialogtaste.', 'Eingabe':'Eigenen Satz ins Textfeld schreiben; die Frage steht beim Feld.',
                   'Rückmeldung':'Fachlichen Satz lesen. Verfügbare Antworten siehe Steuerungen.',
                   'Auswahl':'Die sichtbaren Alternativen beantworten die Frage.',
                   'Lesen oder Navigation':'Nächste verfügbare Bedienung siehe Steuerungen.'}[category]
        concrete=next((s for s in (cue,current,feedback) if s and ('?' in s or '„' in s)),current)
        rationale={'Hilfe':'Freiwilliger Hinweis; keine zweite Aufgabe erforderlich.', 'Eingabe':'Die Frage bestimmt, worüber das Kind selbst schreibt.',
                   'Rückmeldung':'Der Fachsatz erklärt die Auswahl. Eine zusätzliche Schreibaufforderung wäre überflüssig.',
                   'Auswahl':'Die Frage bestimmt, welche Unterschiede zwischen den Tasten zählen.',
                   'Lesen oder Navigation':'Leseschritt oder Navigation; die Tasten tragen die Handlungsbezeichnung.'}[category]
        cw.writerow([rowid,action,ref,source,operation,concrete,rationale])
        for bad in forbidden:
            assert bad.casefold() not in cue.casefold(),(tier,context,bad,cue)
    for tier,r in rows:add(tier,r)
    for r in bilder:
        add(r['niveau'],dict(caseName='Navigation und Einzelprüfung',task=r['ansicht'],event=r['format'],question=r['ansicht'],
                             text=r['text'],ids=[],buttons=r.get('buttons',[]),cue=r.get('cue','')))
    sources={k:v for k,v in logs.items() if k.startswith(('Freigabestufen/','Entwuerfe-und-Fehlerhilfen/'))}
    summary={'commit':revision,'html_sha256':sha,'tag':tag,'ansichten':sum(counts.values()),'gruppen':[
        dict(niveau=t,typ=k,anzahl=v) for (t,k),v in sorted(counts.items())]}
    return {'Ansichten.csv':screen.getvalue(),'Bedienelemente.csv':elements.getvalue(),'Sechs-Prueffragen.csv':checklist.getvalue(),
            'Umfang.json':json.dumps(summary,ensure_ascii=False,indent=2),'Leseschluessel.md':ANLEITUNG,
            **{'Wortlautnachweise/'+k:v for k,v in sources.items()}}

ANLEITUNG="""# Sprachaudit der Schüleransichten

Ansichten.csv ordnet den tatsächlich aus dem Browser gelesenen Wortlaut dem Niveau, Gespräch, Abschnitt und auslösenden Bedienweg zu. Die Ansichtskennung verbindet ihn mit den Steuerungen und den sechs Prüffragen. Beschriftungen können bei geschlossenen Klappelementen und geteilter Arbeitsfläche je nach Fenster variieren. Die Tabellen enthalten auch zu Testzwecken eingegebene eigene Sätze.

Die sechs Spalten dokumentieren den gemeinten Schritt, den im Bildschirm nachlesbaren Bezug, die verfügbare Gedächtnisstütze, die konkrete Bedienung, den maßgeblichen Wortlaut und die Funktion des Auftrags. Gleichartige Bedienhandlungen teilen eine Begründung. Die Zuordnung wird aus den Browserbeobachtungen erzeugt. Sie misst kein individuelles Leseverständnis. Das zusätzliche Wortregister erschließt auch aufklappbare Fachkarten, Forschungsartikel und seltene Textvarianten im ausgelieferten Dokument. Ein Registereintrag allein belegt keinen Aufruf. Unter Wortlautnachweise stehen die einzelnen fachlichen Rückmeldungen, Hinweise und Quellen der gesonderten Freitext- und Fehlerversuche. Die Prüfprotokolle der Auslieferung enthalten außerdem die vollständigen Browser- und Geometrieprotokolle.

Die gedankliche Begründung bleibt bei den Lernenden. Ob ein konkretes Kind sie ohne Begleitung versteht, lässt sich erst im Unterricht feststellen. Eigene freie Formulierungen, beliebig häufige Wiederholungen und beliebige Reihenfolgen der freiwilligen Bedienhandlungen bilden keinen endlichen Prüfbestand.
"""

