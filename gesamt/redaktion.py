"""Prüfurteile zu begrenzten Textgruppen mit explizitem Kontext und gebundenem Wortlaut."""
import hashlib
import json
from collections import defaultdict
from auslieferung import SRC
from sprachpruefung import bank


STATIONEN = {
    'PI': 'Bezugszeit und Schwangerschaftshäufigkeit; keine persönliche Garantie und keine Aussage über STI.',
    '1A': 'Material und Eignung zur Verhütung getrennt betrachten; die intakte Hülle hält Sperma zurück.',
    '1B': 'Schutz hängt vom Sitz, vom Anwendungsbeginn und von bedeckten Hautstellen ab.',
    '2A': 'Eisprung, Eizelle und fehlender Schutz vor STI auseinanderhalten. AHR sucht in Frage 2 die zu widerlegende Behauptung.',
    '2B': 'Einnahmeplan und persönliche Verträglichkeit unterscheiden; aus einer Erfahrung folgt keine sichere Prognose.',
    '3A': 'Kupfer beeinträchtigt Spermien. Der Befund zur Bewegung beantwortet keine Frage zu STI.',
    '3B': 'Ärztliches Einsetzen braucht Zustimmung. Stärkere Blutungen und Schmerzen sind möglich.',
    '4A': 'Gestagen verändert den Schleim am Gebärmutterhals. Erschwerter Durchtritt von Spermien belegt keinen STI-Schutz.',
    '4B': 'Die Spirale gibt das Hormon längerfristig ab. Veränderungen der Blutung und der Schmerzen sind individuell.',
}
FAMILIE = {
    'Mutter':'Sie nennt Gesundheit, Schutzregel und Rat. Der fehlende Fakt erklärt mögliche Beschwerden. Laura entscheidet selbst.',
    'Freundin':'Die Freundin nennt Zukunftspläne. Der medizinische Fakt betrifft die Möglichkeit einer späteren Schwangerschaft, ohne eine zu garantieren.',
    'Großmutter':'Die Nachricht nennt einen Vorgang, eine Schutzregel und einen Rat. Ergänzt wird der Wert, den die Großmutter vertritt.',
    'Vater':'Die Nachricht unterscheidet medizinische Information, Selbstbestimmung und den konkreten Rat. Ergänzt wird seine allgemeine Regel.',
}
BERATUNG = {
    'L01':'Latexallergie: Material, Methode und eigene Empfehlung unterscheiden.',
    'L02':'Schwangerschaftsschutz und Senkung des STI-Risikos werden getrennt begründet.',
    'L03':'Anforderungen im Alltag und die Erfahrung einer anderen Person unterscheiden.',
    'L04':'Mögliche Veränderung der Schmerzen, medizinische Abklärung und persönliche Zustimmung unterscheiden.',
    'L05':'Die eigene Empfehlung begründen und mit dem ersten Rat vergleichen. Die Papierbegründung bleibt einmalig.',
}


def gruppen(docs):
    groups=defaultdict(dict)
    def collect(key,path,value):
        if value:groups[key][path]=value
    prep=bank(docs['PREP'][0])
    for tier,lesson in prep['levels'].items():
        prefix='levels/'+tier+'/'
        records=[('PI',prefix+'intro/question',lesson['intro']['question'])]
        for i,ch in enumerate(lesson['chapters']):
            here=prefix+'chapters/'+str(i)+'/'
            records.extend((ch['id'],here+'questions/'+str(n),q) for n,q in enumerate(ch['questions']))
            if ch.get('paperCheck'):records.append((ch['id'],here+'paperCheck',ch['paperCheck']))
        for chapter,path,q in records:
            key=('PREP',tier,q['id'],STATIONEN[chapter])
            for sub,task in [('',q),('/afterSolutionCheck',q['afterSolutionCheck'])]:
                p=path+sub
                collect(key,p+'/prompt',task['prompt'])
                for i,o in enumerate(task['options']):
                    collect(key,p+'/options/'+str(i)+'/text',o['text'])
                    collect(key,p+'/options/'+str(i)+'/feedback',o['feedback'])
            # Alle fünf Hinweise wurden im Browser nach jeder einzelnen Fehlwahl ausgelöst.
            # Im Vergleich bleiben Antwortoption und tatsächlicher Kapitelkontext getrennt.
            for suffix,seq in [('hintsBeforeChoice',q['hintsBeforeChoice'])]+[
                    ('options/'+str(i)+'/hints',o['hints']) for i,o in enumerate(q['options']) if 'hints' in o]:
                assert len(seq)==5
                for i,text in enumerate(seq):
                    collect(key,path+'/'+suffix+'/'+str(i),text)
    family=bank(docs['UB08'][0])
    for name,c in family['cases'].items():
        key=('UB08','alle vier',name,FAMILIE[name])
        collect(key,'cases/'+name+'/original',c['original'])
        tasks=[('tasks/'+str(i),t) for i,t in enumerate(c['tasks'])]+[('transfer',c['transfer'])]
        for sub,t in tasks:
            assert sum(a['ok'] for a in t['answers'])==1
            prefix='cases/'+name+'/'+sub
            collect(key,prefix+'/prompt',t['prompt'])
            if t.get('advancedPrompt'):
                collect(key,prefix+'/advancedPrompt',t['advancedPrompt'])
            for i,a in enumerate(t['answers']):
                for field in ('advancedText','advancedFeedback'):
                    if a.get(field):collect(key,prefix+'/answers/'+str(i)+'/'+field,a[field])
                collect(key,prefix+'/answers/'+str(i)+'/text',a['text'])
                collect(key,prefix+'/answers/'+str(i)+'/feedback',a['feedback'])
            for tier,hs in t['helpByLevel'].items():
                hint_key=('UB08',tier,name+' · '+sub,FAMILIE[name]+' Lesestelle, Denkfrage, Satzanfang und anschließende Lösung sind getrennt.')
                for i,h in enumerate(hs):
                    collect(hint_key,prefix+'/helpByLevel/'+tier+'/'+str(i),h)
    for i,t in enumerate(family['limits']):
        key=('UB08','alle vier',t['id'],'Aus der medizinischen Information folgt für Laura keine verpflichtende persönliche Entscheidung.')
        collect(key,'limits/'+str(i)+'/prompt',t['prompt'])
        for j,a in enumerate(t['answers']):
            for field in ('text','feedback'):collect(key,f'limits/{i}/answers/{j}/'+field,a[field])
    for sid,step in bank(docs['UB02'][0])['stages'].items():
        for tier,task in step['levels'].items():
            key=('UB02',tier,sid,BERATUNG[sid])
            for field in ('task','paperPrompt','returnPrompt'):
                collect(key,f'stages/{sid}/levels/{tier}/'+field,task[field])
            for method,way in task['strategies'].items():
                base=f'stages/{sid}/levels/{tier}/strategies/{method}'
                k=('UB02',tier,sid+' · '+method,BERATUNG[sid]+' Rückfragen und Bedingungen gehören zur gewählten Methode.')
                for field in ('condition','feedback'):
                    collect(k,base+'/'+field,way[field])
                for i,q in enumerate(way['questions']):
                    for field in ('text','answer'):
                        collect(k,f'{base}/questions/{i}/'+field,q[field])
                for i,o in enumerate(way['options']):
                    for field in ('text','feedback'):
                        collect(k,f'{base}/options/{i}/'+field,o[field])
    for person in ('Tom','Celina'):
        case=bank(docs[person][0])
        if person=='Tom':
            for tier,art in case['articles'].items():
                key=('Tom',tier,'Lesematerial','Verhütungsmethoden, Forschungsansätze und bisher gemessene Ergebnisse sind unterschieden.')
                collect(key,'articles/'+tier+'/title',art['title'])
                for j,para in enumerate(art['paragraphs']):collect(key,f'articles/{tier}/paragraphs/{j}',para)
            for j,study in enumerate(case['studies']):
                key=('Tom','alle vier','Studie '+str(j+1),'Studie A erfasst Schwangerschaften in der Wirksamkeitsphase. Studie B untersucht Einzeldosen bei vasektomierten Männern. Sie belegt keine Verhütungswirkung.')
                for field in ('label','body','source','meaning'):collect(key,f'studies/{j}/'+field,study[field])
        for i,step in enumerate(case['stages']):
            base='stages/'+str(i)
            for tier,task in step['task'].items():
                k=(person,tier,step['title'],'Auftrag im Gespräch, Methode und Papierfeld gehören zur aktuellen Frage von '+person+'.')
                collect(k,base+'/task/'+tier,task)
                collect(k,base+'/paper/'+tier,step['paper'][tier])
                for j,x in enumerate(step['message'][tier]):collect(k,f'{base}/message/{tier}/{j}',x)
            methods=step.get('checks',{})
            checks=methods.items() if methods else [('',step)]
            for method,check in checks:
                stem=base+'/checks/'+method if method else base
                k=(person,'alle vier',step['title']+' '+method,'Die Erklärung bezieht sich auf die konkrete Aussage und '+('Toms eigene Anwendung bzw. die Reichweite des Studienbefunds.' if person=='Tom' else 'Celinas Wünsche, Anwendungsform oder Zustimmung.'))
                for j,(answer,feedback) in enumerate(zip(check['answers'],check['feedback'],strict=True)):
                    collect(k,stem+'/answers/'+str(j),answer)
                    collect(k,stem+'/feedback/'+str(j),feedback)
    return groups


def digest(values):
    return hashlib.sha256(json.dumps(values,ensure_ascii=False,sort_keys=True).encode()).hexdigest()


def nachweise(docs):
    approved=json.loads((SRC/'pruefgrundlagen/Redaktionsstand.json').read_text())
    lookup={}
    for key,values in gruppen(docs).items():
        module,tier,step,grund=key
        if approved.get('|'.join(key[:3]))!=digest(values):
            continue
        for path in values:lookup[module,path]=grund
    return lookup
