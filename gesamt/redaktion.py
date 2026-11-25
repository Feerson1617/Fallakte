"""Prüfurteile zu begrenzten Textgruppen mit explizitem Kontext und gebundenem Wortlaut."""
import hashlib
import json
import re
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
            for i,a in enumerate(t['answers']):
                collect(key,prefix+'/answers/'+str(i)+'/text',a['text'])
                collect(key,prefix+'/answers/'+str(i)+'/feedback',a['feedback'])
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
