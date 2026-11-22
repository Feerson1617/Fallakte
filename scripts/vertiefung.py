"""Combine the verified case dialogue, new checks and local reading material."""
import json
from modul_0212 import ROOT, OUT, commit

def legacy():
    return json.loads((ROOT/'data/dialogdaten.js').read_text().split('const FALLAKTE = ',1)[1].strip().removesuffix(';'))

def make_bank(person):
    old=legacy()
    stages=old['cases'][person]
    checks=json.loads((ROOT/'data'/f'{person.lower()}-pruefung.json').read_text())
    laura=json.loads((ROOT/'data/laura-0212.json').read_text())
    records=[]
    for original,check in zip(stages,checks,strict=True):
        record={k:original[k] for k in ('id','title','message','task','questions','replies','helpBefore')}
        record.update(check)
        record['previousFacts']=[s['recap'] for s in stages[:len(records)] if s.get('recap')]
        if person=='Celina':
            record['task']={**record['task'],'Foerder':'Welcher Grund passt zu diesem Vorschlag?','ESA':'Prüfe den Vorschlag an Celinas Anliegen. Wähle den passenden Grund.'}
        record['choices']=original['options'] if original['type']=='recommend' else {}
        if person=='Tom' and record['choices']:
            refs={'K':'alltag','P':'wirkung','Cu':'einlage','H':'einlage'}
            record['checks']={}
            for strategy in record['choices']:
                method=strategy.split('+')[-1]
                context={k:record[k] for k in ('answers','code','short','feedback')}
                record['checks'][strategy]={**context,'ref':[method,refs[method]]}
        record['hints']=original['hints'].copy()
        for key,context in record.get('checks',{}).items():
            method,section=context['ref']
            card=laura['cards'][method]
            fact=original['hints'][key][-1] if person=='Tom' else context['answers']['ABC'.index(context['code'])]
            record['hints'][key]=['Lies '+card['title']+' · '+card['sections'][section]['title']+'.',fact]
        record['return']='Kehre zum Gespräch zurück. Gib den Buchstaben der fachlich passenden Aussage ein.'
        record['paper']={t:f"Laufzettel · {person} {len(records)+1} – {record['title']}. "+task for t,task in record['task'].items()}
        records.append(record)
    bank={'version':person.lower()+('-1.1' if person=='Tom' else '-1.0'),'buildCommit':commit(),'person':person,'levels':laura['levels'],
          'stages':records,'cards':laura['cards']}
    if person=='Tom':
        bank.update(articles=old['tom_articles'],studies=old['research'])
    return bank

def document(bank):
    return (ROOT/'module/vertiefung/index.html').read_text().replace('STYLE_CSS',(ROOT/'module/vertiefung/style.css').read_text()).replace(
        'BANK_JSON',json.dumps(bank,ensure_ascii=False).replace('<','\\u003c')).replace('APP_JS',(ROOT/'module/vertiefung/app.js').read_text())

def export(bank):
    person=bank['person']
    (OUT/f'{person}-Material.json').write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n')
    lines=[f'# {person} · Aufgaben und Rückwege',bank['buildCommit']]
    def items(value):
        if isinstance(value,dict):
            for k,v in value.items():
                lines.append('**'+k+'**');items(v)
        elif isinstance(value,list):
            for entry in value:items(entry)
        else:lines.append(str(value))
    for i,s in enumerate(bank['stages'],1):
        lines+=['## '+person+' '+str(i)+' – '+s['title']]
        for t,name in bank['levels'].items():
            lines+=['### '+name,*s['message'][t],s['task'][t]]
            if t in ('MSA','AHR'):lines.extend([s['paper'][t],s['return']])
        for k in ('choices','answers','code','feedback','replies','questions','helpBefore','hints','shortSource','checks','ref'):
            if k in s:
                lines.append('**'+{'answers':'Aussagen A, B, C','code':'Lösungsbuchstabe','checks':'Prüfung je Strategie','ref':'Kartenanker'}.get(k,k)+'**');items(s[k])
    for k in ('articles','studies','cards'):
        if k in bank:items(bank[k])
    (OUT/f'{person}-Material.md').write_text('\n\n'.join(lines)+'\n')
