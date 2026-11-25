"""Quellfundstellen und tatsächlich beobachtete Bildschirmzustände separat nachweisen."""
import argparse,csv,gzip,io,json,re,subprocess
from collections import Counter,defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from auslieferung import OUT,QA,SRC,json_text,pack
from sprachpruefung import BASE,rebuild,pruefen,bank,leaves
from fundstellenbeleg import Lernwege
from redaktion import nachweise

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

def html_texts(doc):
    result={}
    for node in doc.xpath('//*[not(ancestor-or-self::script or ancestor-or-self::style or ancestor-or-self::svg)]'):
        if not isinstance(node.tag,str):
            continue
        path=node.getroottree().getpath(node)
        label=node.tag+'#'+(node.get('id') or '')+' Zeile '+str(node.sourceline)
        for i,text in enumerate(node.xpath('text()')):
            if text.strip():result[path+'/text()['+str(i+1)+']']=(label,text.strip())
        for attr in ('alt','title','placeholder','aria-label'):
            if node.get(attr):result[path+'/@'+attr]=(label+' @'+attr,node.get(attr))
    return result

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
    for t in family['levels']:
        add('UB08',t,'LA-04','Wiedereinstieg mit analog geprüftem Beleg','Lernbogen „Lauras Frage – Festhalten“',
            family['ui']['endRecovery'],family['ui']['paperReady'],'LA-04 · Papierauftrag zur Sicherung')
    work=json.loads((QA/'Work-Gegenprobe.json').read_text())
    for r in rows:
        rowid=r['zustand']
        r['papierseite']=''
        r['rueckweg_auf_dem_bildschirm']=''
        if r['modul']=='UB08':
            if r['niveau'] in ('Förder','ESA'):
                prefix=r['abschnitt'].split('-')[0]
                r['papierseite']={'MU':'2','FR':'3','LA':'4'}.get(prefix,'')
            actual=[]
            for w in work:
                if w['version']=='nachher' and w['zustand']==rowid and w['niveau']==r['niveau']:
                    actual.append(' / '.join(w['team'])+' · Person '+str(w['person'])+' · '+w['rueckweg'])
            r['rueckweg_auf_dem_bildschirm']=' | '.join(actual)
        r['medium']='Lernbogen' if r['modul']=='UB08' else ('Infokarte und/oder Laufzettel' if r['modul']=='PREP' else 'Laufzettel')
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
    wege=Lernwege(QA)
    lesarten=nachweise(new)
    astrollen={}
    rows=[];counts=Counter()
    matrix=media(new)
    cases={m:bank(new[m][0]) for m in ('Tom','Celina')}
    # Die freiwilligen Fälle zeigen bei einem Widerspruch nur die Konfliktmeldung.
    # inspect() gibt für diese Methoden vor dem Zugriff auf die Codeantwort zurück.
    def match_matrix(mod,tier,path):
        for x in matrix:
            if x['modul']!=mod or x['niveau']!=tier:continue
            prefix=None
            if mod=='PREP' and '/chapters/' in path:
                index=int(path.split('/chapters/')[1].split('/')[0])
                if x['abschnitt']!=str(index//2+1)+'AB'[index%2]:continue
                if path.endswith('paperPrompt') and x['zustand']=='Wörter freigegeben':return x
                if '/paperCheck/' in path and x['zustand']=='A mit Papierfrage':return x
            if mod=='UB08' and '/steps/'+x['zustand']+'/' in path:return x
            if mod=='UB02' and x['abschnitt'] in path.split('/') and path.endswith(('paperPrompt','returnPrompt')):return x
        return {}
    changed_by_place={(x['modul'],x['stelle']) for x in changes}
    scope_summary=Counter()
    def add(m,t,section,state,source,place,alt,neu,reason,typ):
        beleg=wege.find(m,t,place,neu)
        observed=bool(beleg or (neu and neu in texts[m]))
        handoff=match_matrix(m,t,place)
        status='Einzelprüfung offen';kind='Text oder Metadatum'
        if source.startswith('JSON:') or source=='JSON':
            keys=place.split('/')
            if any(k in ('id','sectionId','taskId','fieldId','sectionIds','informationSections','previousSection','requiresAny','knownFacts','nextChapter','visualRef','shortOptions','restartId','nextId','version','designFiles','buildCommit','baseCommit') for k in keys) or keys[-1] in ('correct','ok','code','method','target'):
                status='technische Funktion anhand des Datenfelds bestimmt';kind='Technik'
            elif (m in ('UB02','Tom','Celina') and ('primary' in keys or 'methods' in keys or 'allowed' in keys or 'ref' in keys or ('section'==keys[-1] and any(name in keys for name in ('card','goalCard','extraCards'))))) or (m=='UB02' and keys[-1]=='status' and neu in ('A','B','C')) or (m=='UB08' and keys[-1]=='portrait' and str(neu).endswith('.webp')):
                status='technische Funktion anhand des Datenfelds bestimmt';kind='Technik'
            elif m=='PREP' and (keys[0]=='cards' or 'cardEntries' in keys or 'fullCardReview' in keys) and (QA/'Kartenpruefung.json').exists():
                status='Kartenvertrag gegen gedruckte und gerenderte Karten geprüft';kind='geschützte Kartendaten'
            elif handoff and m=='UB08' and (QA/'Work-Gegenprobe.json').exists() and place.endswith(('/action','/screen')) and t in ('Förder','ESA') and place.split('/')[2] in ('MU-erst','MU-ergebnis','FR-erst','FR-ergebnis','LA-eigen','LA-abschluss'):
                status='Work-Auftrag, PDF-Seite und Bildschirm verglichen';kind='Papierauftrag'
            elif m=='PREP' and place.endswith('/feedback') and (m,place) in changed_by_place and '/afterSolutionCheck/' not in place and any(field in place for field in ('/questions/','/paperCheck/','/intro/question/')) and (QA/'Browserpruefung.json').exists():
                answer=compiled[m].get(place.rsplit('/',1)[0]+'/correct')
                if answer is False:
                    status='Rückmeldung zur konkreten Fehloption redigiert und im Frageweg geprüft';kind='Rückmeldung'
            elif m=='UB02' and '/hints/' in place and (QA/'Empfehlungen.json').exists():
                status='Hinweis im Entscheidungsweg und in seiner Stufenfolge geprüft';kind='Hilfe'
            if m in cases and len(keys)>3 and keys[0]=='stages' and keys[2]=='checks':
                case=cases[m]['stages'][int(keys[1])]
                if keys[3] in case.get('conflicts',{}) and len(keys)>4 and keys[4] in ('feedback','answers','short'):
                    status='Antwortprüfung in diesem Konfliktweg gesperrt; Funktionsweg und Quellenfeld geprüft'
                    kind='gesperrter Prüfzweig'
            if (m=='PREP' and keys[-1] in ('focus','purpose','chapter','solutionExplanation','explanation') and any(k in keys for k in ('question','questions','paperCheck'))) or (m=='UB08' and keys[0] in ('differentiation','workingTrace','analogSteps','paperFields')):
                status='Planungsfeld im Datenvertrag; kein eigener Ausgabezugriff im Schüler-Renderer'
                kind='Planungsdaten'
        elif typ=='JS-Template':kind='Laufzeitvorlage'
        elif typ=='SVG':kind='Bildtext'
        elif typ=='HTML':kind='HTML oder zugängliche Beschriftung'
        elif typ=='JS-Literal' and (neu and re.fullmatch(r'#[a-z][\w-]*|aria-[a-z-]+|data-[a-z-]+',str(neu))):
            status='technische Zeichenkette im Skript';kind='Technik'
        interpretation=lesarten.get((m,place),'')
        if interpretation and status=='Einzelprüfung offen' and beleg:
            kind='Lerntext'
            status='Wortlaut mit fachlichem Kontext und zugehöriger Browseransicht geprüft'
        if m=='START' and typ=='HTML':
            kind='Navigation oder Bildbeschreibung'
            status='Tagesauswahl, Beschriftungen und Alternativtexte im gebauten Startdokument geprüft'
        if source.startswith('JS ') and (m=='START' or astrollen.get((m,source,place))):
            status='Funktion im JavaScript-Syntaxbaum bestimmt'
            kind='Technik'
            reason=astrollen.get((m,source,place)) or 'Startseitensteuerung: Sitzungsereignis, Kennung, Symbolpfad oder Protokollwert'
        if kind=='Technik' and observed and source.startswith('JSON'):
            kind='Schlüssel oder Verweis mit beobachtetem Anzeigewortlaut'
        if handoff and alt!=neu:reason='Papierort und Rückweg für den konkreten Zustand überarbeitet'
        elif kind=='Hilfe' and alt!=neu:reason='Kartenstelle, Denkfrage oder Lösung an Abschnitt und gewählte Methode gebunden'
        elif kind=='Rückmeldung':reason='Biologischer Unterschied zur gewählten falschen Aussage erklärt'
        elif (m,place) in changed_by_place:reason='Wortlaut in der ausgelieferten Datenbank geändert; Adresse und Schlüssel verglichen'
        rev='geändert' if alt!=neu else 'unverändert'
        scope_summary[(m,status)]+=1
        rows.append(dict(modul=m,niveau=t,abschnitt=section,zustand=state,quelle=source,stelle=place,alttext=alt,neutext=neu,grund=reason,kontextpruefung=interpretation,typ=typ,art=kind,
                         papierfeld=handoff.get('papierfeld',''),rueckkehr=handoff.get('rueckkehr',''),ziel=handoff.get('ziel',''),
                         sichtbeleg='Wortlaut im zugeordneten Lernweg beobachtet' if beleg else 'gleicher Wortlaut im Modul beobachtet' if observed else '',laufzeitstelle=beleg,einzelabnahme=status))
        counts[m,t,typ,rev,observed,status]+=1
    html_old={m:html_texts(v[0]) for m,v in old.items()}
    html_new={m:html_texts(v[0]) for m,v in new.items()}
    html_used=defaultdict(set)
    vorschlaege=[]
    for r in inventory:
        m,t,k,src,txt=r['modul'],r['niveau'],r['stelle'],r['quelle'],r['text'];reason='Wortlaut im Ausgangsscan';value=txt
        if src.startswith('JSON:'):
            value=compiled[m][k];reason='Wortlaut im gebauten Datenfeld verglichen'
        elif src.startswith('JS '):
            i=re.search(r'\[(\d+)\]',src)[1];entry=tokens[m][0].get((i,k,txt),{})
            if entry is None:value='';reason='Literal oder Vorlage im neuen Skript ersetzt; neue Fundstelle separat erfasst'
            elif entry:
                value=entry['text'];reason='JavaScript-Syntaxbaum beider gebauten Dokumente verglichen'
                astrollen[m,src,k]=entry['rolle']
            else:reason='Quellposition aus Fremdscan ohne eindeutige AST-Zuordnung'
        elif src=='HTML':
            hits=[path for path,(label,text) in html_old[m].items() if label==k and text==txt]
            if len(hits)==1:
                path=hits[0];html_used[m].add(path)
                value=html_new[m].get(path,('',''))[1]
                reason='HTML-Textknoten oder zugängliches Attribut an derselben DOM-Stelle verglichen'
            else:
                reason='HTML-Quellangabe ohne eindeutige Zuordnung; siehe HTML-Elemente.csv'
        for tier in ('Foerder','Förder','ESA','MSA','AHR'):
            if tier in k.split('/'):t=tier;break
        sec=re.search(r'(?:chapters|stages|steps|cases)/([^/]+)',k)
        add(m,t,sec[1] if sec else '',r['hinweise'],src,k,txt,value,reason,r['typ'])
        if r['vorschlag']:
            chosen=rows[-1]
            if value==r['vorschlag']:decision='Vorschlag wortgleich umgesetzt'
            elif value!=txt:decision='andere Formulierung im Kandidaten'
            elif chosen['einzelabnahme']=='Einzelprüfung offen':decision='Wortlaut beibehalten; redaktionelle Entscheidung offen'
            else:decision='Wortlaut beibehalten; dokumentierten Prüfnachweis beachten'
            vorschlaege.append(dict(modul=m,niveau=t,stelle=k,alt=txt,vorschlag=r['vorschlag'],kandidat=value,entscheidung=decision,grund=reason,beleg=chosen['laufzeitstelle']))
    domrows=[]
    for m,nodes in html_new.items():
        for path in sorted(html_old[m].keys() | nodes.keys()):
            alt=html_old[m].get(path,('',''))[1];label,neu=nodes.get(path,('',''))
            domrows.append(dict(modul=m,pfad=path,alttext=alt,neutext=neu))
            if neu and path not in html_used[m] and path not in html_old[m]:
                add(m,'übergreifend','','neu','HTML',path,'',neu,'zusätzlicher Textknoten oder zugängliche Beschriftung','HTML')
    for m,(lookup,extra) in tokens.items():
        for i,x in extra:
            source='JS script['+i+']'
            astrollen[m,source,x['stelle']]=x['rolle']
            add(m,'übergreifend','','neu',source,x['stelle'],'',x['text'],'neues Literal oder neue Vorlage',x['typ'])
    for x in changes:
        if x['alt'] is None and x['neu']:add(x['modul'],'übergreifend','','neu','JSON',x['stelle'],'',x['neu'],'zusätzliche Beschriftung','Daten')
    physical=json.loads((QA/'Work-Gegenprobe.json').read_text())
    pairs=defaultdict(dict)
    for r in physical:pairs[tuple(r['team']),r['person'],r['zustand']][r['version']]=r
    screens=[]
    for n,r in enumerate(states,1):
        screens.append(dict(id=n,quelle='Browser · '+r['lauf'],modul=r['modul'],niveau=r['niveau'],abschnitt=r['abschnitt'],zustand=r['aktion'],neutext=r['text'],bedienelemente=r['bedienung']))
    archive={'Offene-Einzelpruefungen.csv':csvdata([r for r in rows if r['einzelabnahme']=='Einzelprüfung offen']),
             'Work-Bildschirmvergleich.csv':csvdata([dict(team=' / '.join(k[0]),person=k[1],zustand=k[2],alt=v['vorher']['anzeige'],neu=v['nachher']['anzeige'],rueckweg_alt=v['vorher']['rueckweg'],rueckweg_neu=v['nachher']['rueckweg']) for k,v in pairs.items()]),
             'Fundstellen.csv':csvdata(rows),'HTML-Elemente.csv':csvdata(domrows),'Sprachscan-Vorschlaege.csv':csvdata(vorschlaege),'Medienwechselmatrix.csv':csvdata(matrix),
             'Umfang.csv':csvdata([dict(modul=k[0],niveau=k[1],typ=k[2],abgleich=k[3],im_browser=k[4],einzelabnahme=k[5],anzahl=v) for k,v in sorted(counts.items())]),
             'Bildschirmzustaende.jsonl':'\n'.join(json.dumps(r,ensure_ascii=False) for r in screens)}
    compared=sum(count for raw,count in wege.pairs.values())
    laufumfang=Counter()
    unique=defaultdict(set)
    for name,(raw,count) in wege.pairs.items():
        for line in raw.splitlines():
            snap=json.loads(line)
            key=(snap['modul'],snap['niveau'],snap['weg'],snap['aktion'],'geändert' if snap['alttext']!=snap['neutext'] else 'unverändert')
            laufumfang[key]+=1
            unique[key].add(snap['neutext'])
        archive['Laufzeitvergleich/'+name+'.jsonl']=raw
    archive['Laufzeitumfang.csv']=csvdata([dict(modul=k[0],niveau=k[1],weg=k[2],aktion=k[3],wortlaut=k[4],beobachtungen=v,verschiedene_ansichten=len(unique[k])) for k,v in sorted(laufumfang.items())])
    archive['Work-Druckhinweise.md']='''# Papierabgleich für die nächste Materialfassung

Die beigefügten Originale vom 25.11. sind die Referenz für beide Pflichtlernbögen. Die Sichtprüfung enthält die unveränderten Seiten als gerenderte Ansichten. Die Seiten 2 und 3 haben jeweils eine einzige Optionsliste. Links steht der erste Vorschlag, rechts die geprüfte Wahl. Das erste Kreuz bleibt stehen. Die Spaltenkoordinaten stehen in Pflichtbogenabgleich.json.

Auf Seite 4 führt „Weiter im Chat: Lauras Frage – Prüfen“ zum Abschnitt LA-03. Am iPad heißt der Knopf in LA-02 „Meine Antwort prüfen“. Die Formulierung „Fallakte schließen!“ auf Papier gehört zum Wechsel in die gemeinsame Sicherung. In LA-04 wird dafür kein zusätzlicher Knopf verlangt. Beim direkten Wiedereinstieg kennzeichnet „Ich habe den geprüften Fakt auf meinem Lernbogen eingetragen.“ einen bereits vorhandenen Papiereintrag. Im Wiederaufnahmedialog lautet der Knopf zum Öffnen des ausgewählten Abschnitts „Hier weiterarbeiten“.

Vorbereitung: Auf Seite 4 der vier früheren Schüler-Druckfassungen lautet der Schnittauftrag noch „vier Karten“. Für die Duplexfassung sind die Seiten 1 und 2 ein doppelseitiges Kartenblatt. Ein Schnitt an der Mittellinie ergibt zwei Karten mit vier Methodenflächen. Seiten 3 und 4 bilden den separaten Laufzettel. Der freigegebene Rückfallstand vom 26.11. bleibt separat nutzbar. Für die spätere Materialbearbeitung gelten die tatsächlich geprüften Zielansichten und die Medienwechselmatrix.

Für das im Work-Nachtrag erwähnte separate Ausfallmaterial gilt die Zuordnung des Familienrats: Mutter auf Seite 2, Freundin auf Seite 3, Lauras Antwort auf Seite 4. Der Seitenvergleich in dieser Runde bezieht sich auf die zwei beigefügten Pflichtbögen.
'''
    archive['Hinweise.md']='''# Softwarevertrag zur Prüfung

Fundstellen.csv verknüpft die Angaben aus dem Sprachaudit mit den neu gebauten Dokumenten. Derselbe Wortlaut kann in verschiedenen Situationen unterschiedliche Aufgaben erfüllen. Die Zuordnung zum Papierauftrag ist dort eingetragen, wo die Fundstelle einen konkreten Medienwechsel beschreibt. Den produktiven Zustand und seine erlaubten Bedienhandlungen zeigen die Browserprotokolle.

Die Spalte laufzeitstelle verweist auf die erste passende Zeile im Verzeichnis Laufzeitvergleich. Bei Daten mit Niveau-, Abschnitts- oder Methodenbindung werden diese Angaben für die Zuordnung berücksichtigt. Ein leerer Beleg bleibt offen. Die Dateien unter Laufzeitvergleich stellen die sichtbare alte und neue Ansicht nach derselben Aktion gegenüber. Der Weg enthält Niveau und Abschnitt beziehungsweise Methode. Bei Hilfen, falschen Antworten und nachträglichen Änderungen unterscheiden die laufende Schrittnummer und die betätigte Schaltfläche die Zustände. Die Eingaben sind simuliert. Bildschirmzustaende.jsonl umfasst zusätzliche echte Ansichten aus den Regressionstests. Eine Beobachtung beweist, welcher Wortlaut erschien. Sie ersetzt keine pädagogische Einzelabnahme.

## Blattzuordnung für Work

Vorbereitung: Kartenblatt doppelseitig, vier Methodenflächen auf zwei Karten. Ein Schnitt an der Mittellinie. Den separaten Laufzettel nach den vorhandenen Kapitelkennungen beschriften. Für UB02 die Titel „Laura 1“ bis „Laura 5“ und „Mein Schlussrat“ als Feldnamen nutzen. Keine individuelle Aufgabe zum Empfehlungsrad anlegen. Familienrat: In den tatsächlich beigefügten Förder-/ESA-Pflichtbögen belegt Mutter Seite 2, Freundin Seite 3 und die persönliche Antwort Seite 4. Die Einträge „digital geprüft“, „analog geprüft“ und „noch offen“ beziehen sich auf den Fachbeleg. Die Schüler entscheiden selbst, was sie Laura raten. Für andere Bögen sind die Feldüberschriften maßgeblich. Eine Seitennummer ist dort erst beim späteren Satz des Druckmaterials festzulegen.

Der Arbeitsstand wird bis zur vollständigen Einzelabnahme separat aufbewahrt.
'''
    pack(OUT/'Fallakte-Textvertrag-Prueffassung.zip',archive)
    (QA/'Sprachumfang.json').write_text(json_text(dict(fundstellen_alt=len(inventory),fundstellen_export=len(rows),medienwechsel=len(matrix),beobachtungen=len(states),paarweise=compared,offen=sum(v for (m,st),v in scope_summary.items() if st=='Einzelprüfung offen'),
        lernwegbelege=sum(bool(r['laufzeitstelle']) for r in rows),nach_modul={m:dict(fundstellen=sum(x['modul']==m for x in rows),geaendert=sum(x['modul']==m and x['alttext']!=x['neutext'] for x in rows),offen=scope_summary[m,'Einzelprüfung offen'],zustandsbeobachtungen=sum(s['modul']==m for s in states)) for m in new})))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--referenz',type=Path);a=parser.parse_args()
    report(a.referenz or rebuild(BASE,'gesamt/auslieferung.py','Gesamt')/'Fallakte-Gesamt.html')
