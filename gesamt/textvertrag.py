"""Quellfundstellen und tatsächlich beobachtete Bildschirmzustände separat nachweisen."""
import argparse,csv,gzip,io,json,re,subprocess
from collections import Counter,defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from auslieferung import OUT,QA,SRC,json_text,pack
from sprachpruefung import BASE,rebuild,pruefen,bank,leaves

def js(doc):
    sources={str(i):n.text or '' for i,n in enumerate(doc.xpath('//script')) if not n.get('type') or n.get('type')=='text/javascript'}
    return json.loads(subprocess.check_output(['node','--expose-internals',str(SRC/'jsinventar.cjs')],input=json.dumps(sources),text=True))

def js_changes(old,new):
    result={};extra=[]
    for i,original in old.items():
        current=new[i];a=[r['text'] for r in original];b=[r['text'] for r in current]
        for op,lo,hi,start,stop in SequenceMatcher(None,a,b,autojunk=False).get_opcodes():
            if op=='equal':pairs=zip(original[lo:hi],current[start:stop])
            elif op=='replace' and hi-lo==stop-start:pairs=zip(original[lo:hi],current[start:stop])
            else:
                pairs=[(r,None) for r in original[lo:hi]]
                extra.extend((i,r) for r in current[start:stop])
            for x,y in pairs:result[i,x['stelle'],x['text']]=y
    return result,extra

def csvdata(rows):
    stream=io.StringIO();writer=csv.DictWriter(stream,rows[0].keys());writer.writeheader();writer.writerows(rows);return stream.getvalue()
def media(docs):
    rows=[]
    def add(m,l,id,phase,field,action,back,target):
        rows.append(dict(modul=m,niveau=l,abschnitt=id,zustand=phase,papierfeld=field,handlung=action,rueckkehr=back,ziel=target))
    prep=bank(docs['PREP'][0])
    for level,lesson in prep['levels'].items():
        for c in lesson['chapters']:
            id=c['id'];method=c['title'].split(' – ')[1].split(':')[0];b=id.endswith('B');q=c.get('paperCheck');fields=c['cardEntries']
            add('PREP',level,id,'Kapitel öffnen','Laufzettel '+id,'Kapitel markieren.','Zur Fachfrage',c['questions'][0]['id'])
            add('PREP',level,id,'Wörter freigegeben',f'Infokarte {method}, Felder '+', '.join(str(f['number']) for f in fields),c['paperPrompt'],
                'Vollständige Karte vergleichen' if b else 'Code prüfen' if q else 'Weiter im Chat','Kartenvergleich' if b else 'Buchstabe prüfen' if q else c['nextChapter'])
            if q:add('PREP',level,id,'A mit Papierfrage','Laufzettel '+id,q['screen']+' '+q['return'],'Code prüfen → Nachricht senden → Weiter im Chat',c['nextChapter'])
            if b:add('PREP',level,id,'Musterkarte sichtbar',f'Infokarte {method} 1–4; Laufzettel {id}, Karte kontrolliert','Alle vier Felder vergleichen. Fehlende Wörter ergänzen. Auf dem Laufzettel das Kästchen ankreuzen.','Weiter im Chat',{'2B':'Zwischenansicht','4B':'Abschluss'}.get(id,c['nextChapter']))
        for id,action,back,target in [('2B','Kondom und Pille kontrollieren. Nächstes Kapitel markieren.','Jetzt mit … weiterarbeiten / Abschnitt auswählen','nächstes offenes Kapitel / Auswahl'),('4B','Vier Methoden vergleichen, Einträge ergänzen, Duplexblatt einmal schneiden. Beide Karten aufbewahren.','Methode auswählen → Schließen','Abschluss 4B')]:
            add('PREP',level,id,'Stundenende','Infokarten; Laufzettel',action,back,target)
        add('PREP',level,'alle','Zeitnot/Ausfall','Infokarte der gewählten Methode','Fehlende Wörter in den nummerierten Feldern ergänzen.','Schließen','vorherige Ansicht, Prüfstatus unverändert')
    first=bank(docs['UB02'][0])
    for s in first['stages'].values():
        for t,x in s['levels'].items():
            if s['id']=='L01':add('UB02',t,'L01','Einstieg','Laufzettel, erster Rat','Ersten Rat lesen und im Gespräch aufgreifen.','Neu beginnen','Laura 1')
            if x['paperPrompt']:add('UB02',t,s['id'],'Empfehlung ausgewählt','Laufzettel '+s['title'],x['task']+' '+x['paperPrompt'], 'Code prüfen → Nachricht senden','Rückmeldung zum Rat')
            if s['id']=='L05':add('UB02',t,'L05 / Stopp','persönlicher Schlussrat','Laufzettel „Mein Schlussrat“',x['task'],'beim Stopp kein Knopf','Unterrichtsgespräch')
    for m in ('Tom','Celina'):
        for i,s in enumerate(bank(docs[m][0])['stages'],1):
            for t in ('MSA','AHR'):
                add(m,t,str(i),'freiwillige Beratung','Laufzettel '+m+' '+str(i)+' – '+s['title'],s['task'][t]+' Begründung notieren. Richtige Aussage einkreisen.', 'Code prüfen → Nachricht senden', 'Antwort im Gespräch')
    family=bank(docs['UB08'][0])
    for id,step in family['media']['steps'].items():
        for t,v in step['orders'].items():
            back=step.get('buttonText') or ('Mit den Aussagen vergleichen' if t in ('MSA','AHR') else 'gewählte Antwort antippen') if step['nextId'] else 'kein Knopf'
            if step['mode']=='gleicher Abschnitt':back+='; bei gemischtem Team zuerst Freitext und „Mit den Aussagen vergleichen“'
            add('UB08',t,step['sectionId'],id,'Lernbogen „'+step['field']+'“',v['screen'],back,step['nextId'] or 'Sicherung im Unterricht')
    return rows

def report(ref):
    old,new,changes=pruefen(ref)
    states=[]
    for p in sorted(QA.glob('*.jsonl.gz')):
        with gzip.open(p,'rt') as f:
            for line in f:
                r=json.loads(line);r['lauf']=p.name;states.append(r)
    texts=defaultdict(set)
    for r in states:
        texts[r['modul']].update(line.strip() for line in r['text'].splitlines())
        texts[r['modul']].update(b[1] for b in r['bedienung'])
    with gzip.open(SRC/'pruefgrundlagen/Ausgangsinventar.csv.gz','rt',encoding='utf-8-sig') as f:inventory=list(csv.DictReader(f))
    compiled={m:dict(leaves(bank(v[0]))) for m,v in new.items()}
    tokens={m:js_changes(js(old[m][0]),js(v[0])) for m,v in new.items()}
    rows=[];counts=Counter()
    matrix=media(new)
    def add(m,t,section,state,source,place,alt,neu,reason,typ):
        observed=bool(neu and neu in texts[m])
        rows.append(dict(modul=m,niveau=t,abschnitt=section,zustand=state,quelle=source,stelle=place,alttext=alt,neutext=neu,grund=reason,typ=typ,
                         sichtbeleg='exakter Text im Browserprotokoll' if observed else '',einzelabnahme='offen'))
        counts[m,t,typ,'geändert' if alt!=neu else 'unverändert',observed]+=1
    for r in inventory:
        m,t,k,src,txt=r['modul'],r['niveau'],r['stelle'],r['quelle'],r['text'];reason='Wortlaut im Ausgangsscan';value=txt
        if src.startswith('JSON:'):
            value=compiled[m][k];reason='Wortlaut im gebauten Datenfeld verglichen'
        elif src.startswith('JS '):
            i=re.search(r'\[(\d+)\]',src)[1];entry=tokens[m][0].get((i,k,txt),{})
            if entry is None:value='';reason='Literal oder Vorlage im neuen Skript ersetzt; neue Fundstelle separat erfasst'
            elif entry:value=entry['text'];reason='JavaScript-Syntaxbaum beider gebauten Dokumente verglichen'
            else:reason='Quellposition aus Fremdscan ohne eindeutige AST-Zuordnung'
        elif src=='HTML':
            tag=k.split('#')[0];attr=k.split(' @')[-1] if ' @' in k else None
            def visible(doc):
                return [(n.get(attr) if attr else (n.text or '').strip()) for n in doc.xpath('//'+tag)]
            a=visible(old[m][0]);b=visible(new[m][0])
            if txt in a and txt not in b:
                j=a.index(txt);prev=next((s for s in reversed(a[:j]) if s and s in b),None)
                cand=[s for s in b[(b.index(prev)+1 if prev else 0):] if s and s not in a]
                value=cand[0] if cand else '';reason='HTML-Element neu beschriftet'
        sec=re.search(r'(?:chapters|stages|steps|cases)/([^/]+)',k)
        add(m,t,sec[1] if sec else '',r['hinweise'],src,k,txt,value,reason,r['typ'])
    for m,(lookup,extra) in tokens.items():
        for i,x in extra:add(m,'übergreifend','','neu','JS script['+i+']',x['stelle'],'',x['text'],'neues Literal oder neue Vorlage',x['typ'])
    for x in changes:
        if x['alt'] is None and x['neu']:add(x['modul'],'übergreifend','','neu','JSON',x['stelle'],'',x['neu'],'zusätzliche Beschriftung','Daten')
    archive={'Fundstellen.csv':csvdata(rows),'Medienwechselmatrix.csv':csvdata(matrix),
             'Umfang.csv':csvdata([dict(modul=k[0],niveau=k[1],typ=k[2],abgleich=k[3],im_browser=k[4],anzahl=v) for k,v in sorted(counts.items())]),
             'Bildschirmzustaende.jsonl':'\n'.join(json.dumps(r,ensure_ascii=False) for r in states)}
    pack(OUT/'Fallakte-Textvertrag-Prueffassung.zip',archive)
    (QA/'Sprachumfang.json').write_text(json_text(dict(fundstellen_alt=len(inventory),fundstellen_export=len(rows),medienwechsel=len(matrix),beobachtungen=len(states),
        nach_modul={m:dict(fundstellen=sum(x['modul']==m for x in rows),geaendert=sum(x['modul']==m and x['alttext']!=x['neutext'] for x in rows),zustandsbeobachtungen=sum(s['modul']==m for s in states)) for m in new})))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--referenz',type=Path);a=parser.parse_args()
    report(a.referenz or rebuild(BASE,'gesamt/auslieferung.py','Gesamt')/'Fallakte-Gesamt.html')
