"""Combine the verified case dialogue, new checks and local reading material."""
import json
from modul_0212 import ROOT, OUT, commit

from arbeitsplatz import einbetten

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
        record['replies']={**original['replies'],**record.pop('sentReplies',{})}
        record['previousFacts']=[s['recap'] for s in stages[:len(records)] if s.get('recap')]
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
        if record['choices']:
            record['primary']={'Foerder':['K','Cu'],'ESA':['K','Cu','P']}
            record['conflicts']={}
            for key in record['choices']:
                if key in record['allowed']:continue
                method=key.split('+')[-1]
                if person=='Tom':
                    reason={'P':'Die Kombinationspille wirkt auf einen Zyklus mit Eisprung.',
                            'Cu':'Die Kupferspirale wird in eine Gebärmutter eingesetzt.',
                            'H':'Die Hormonspirale wird in eine Gebärmutter eingesetzt.'}[method]
                    short=reason+' Tom kann sie nicht selbst anwenden.'
                    if '+' in key:short+=' Nur das Kondom könnte Tom selbst benutzen.'
                    full=short+' Welcher Vorschlag passt zu seiner Frage?'
                elif method=='Cu':
                    short='Kupfer schützt vor Schwangerschaft. Der Schutz vor Infektionen fehlt.'
                    full=short+' Was schützt Celina auch vor Ansteckung beim Sex?'
                else:
                    label={'P':'Die Kombinationspille','H':'Die Hormonspirale'}[method]
                    short=label+' enthält Hormone. Celina möchte keine zusätzlichen Hormone.'
                    full=short+' Was kann Celina ohne Hormone benutzen?'
                record['conflicts'][key]={'short':short,'full':full}
        if person=='Tom' and not records:
            record['questions'][1][0]='Wenn du mit deiner Partnerin über Verhütung sprichst: Wer entscheidet über den eigenen Körper?'
        if person=='Celina':
            einfacher=['Was kann Celina ohne Hormone benutzen?', 'Welche Methode schützt Celina lange?',
                       'Wer entscheidet, ob Celina sich eine Spirale einsetzen lässt?',
                       'Was schützt Celina auch vor Ansteckung beim Sex?', 'Was rätst du Celina am Ende?']
            tiefer=['Wie wirkt die Methode ohne Hormone?', 'Wann braucht Celina wieder ein Kondom oder eine neue Spirale?',
                    'Was kann die Ärztin erklären? Wer entscheidet danach?', 'Was schützt vor Schwangerschaft und was vor HIV?',
                    'Welcher Wunsch von Celina zählt für dich am meisten? Wann würdest du ihr anders raten?']
        else:
            einfacher=['Welche Methode kann Tom selbst benutzen?', 'Was bedeutet eine kleinere Zahl von Spermien für die Befruchtung?',
                       'Was wurde in Studie B bei den Männern gemessen?']
            tiefer=['Was kann Tom selbst benutzen? Wer entscheidet über den Körper seiner Partnerin?',
                    'Weniger Spermien: Wie könnte das vor Schwangerschaft schützen? Was müsste man noch messen?',
                    'Welche Studie zählt Schwangerschaften? Was weiß man über Schutz bei längerer Anwendung?']
        for level in record['task']:
            record['task'][level]=(einfacher if level in ('Foerder','ESA') else tiefer)[len(records)]
        records.append(record)
    bank={'version':person.lower()+('-1.2' if person=='Tom' else '-1.1'),'buildCommit':commit(),'person':person,'levels':laura['levels'],
          'stages':records,'cards':laura['cards']}
    if person=='Tom':
        bank.update(articles=old['tom_articles'],studies=old['research'])
    return bank

def document(bank):
    from clt_inhalte import karten
    karten(bank)
    page=(ROOT/'module/vertiefung/index.html').read_text().replace('STYLE_CSS',(ROOT/'module/vertiefung/style.css').read_text()).replace(
        'BANK_JSON',json.dumps(bank,ensure_ascii=False).replace('<','\\u003c')).replace('APP_JS',(ROOT/'module/vertiefung/app.js').read_text())
    return einbetten(page)

def export(bank):
    person=bank['person']
    (OUT/f'{person}-Material.json').write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n')
    lines=[f'# {person} · Material für Work',f"Inhaltsbank {bank['version']} · Commit {bank['buildCommit']}",
           'Die Reihenfolge und Buchstaben unten entsprechen der App. Förder und ESA prüfen ihre Gründe im Gespräch. MSA und AHR begründen auf Papier und prüfen den Buchstaben im Chat.']
    for index,stage in enumerate(bank['stages'],1):
        lines+=['## '+person+' '+str(index)+' – '+stage['title'], 'Kennung '+stage['id']]
        if stage['previousFacts']:lines+=['**Bisher im Fall**',*stage['previousFacts']]
        for tier,label in bank['levels'].items():
            lines+=['### '+label,*stage['message'][tier],stage['task'][tier]]
            if tier in ('MSA','AHR'):lines+=[stage['paper'][tier],stage['return']]
        lines+=['**Hilfe vor der Auswahl**',*stage['helpBefore']]
        contexts=stage['choices'] or {'DONE':'Quelle auswerten'}
        for key,label in contexts.items():
            check=stage.get('checks',{}).get(key,stage)
            lines+=['### '+label]
            if key!='DONE':
                method,section=check['ref']
                card=bank['cards'][method]
                lines+=['**Kartenstelle** '+card['title']+' · '+card['sections'][section]['title']]
            else:
                lines+=['**Materialstelle** Artikel und Studien öffnen. Siehe Lesematerial am Ende.',stage['shortSource']]
            conflict=stage.get('conflicts',{}).get(key)
            if conflict:
                lines+=['**Direkt nach der Auswahl**',conflict['short'],conflict['full'],
                        'Auswahl ändern. Für diesen Vorschlag gibt es keinen Fachcheck.',
                        *stage['hints'][key]]
                questions=check.get('questions',stage['questions'])
                lines += [q+' — '+a for q,a in questions]
                continue
            lines+=['**Förder** · Aussagen '+' und '.join(check['short']),
                    '**ESA, MSA, AHR** · Aussagen A, B und C']
            for letter,answer,feedback in zip('ABC',check['answers'],check['feedback'],strict=True):
                lines+=[f'- {letter} · {answer}',f'  Rückmeldung · {feedback}']
            lines+=['**Zutreffender Fachanker** '+check['code']]
            if key!='DONE' and key not in stage['allowed']:
                lines+=['Der Fachanker kann zutreffen und der Vorschlag dennoch unvollständig sein oder eine Grenze verletzen. Die App fordert zur erneuten Wahl auf.']
            lines+=['**Fallbezogene Rückmeldung** '+stage['replies'][key]]
            questions=check.get('questions',stage['questions'])
            lines+=['**Rückfragen**',*[q+' — '+a for q,a in questions]]
            hints=stage['hints'].get(key,stage['helpBefore']) if key!='DONE' else stage['helpBefore']
            lines+=['**Hilfe im aktuellen Schritt**',*hints]
    if 'articles' in bank:
        lines+=['## Lesematerial zur Forschung']
        for tier,article in bank['articles'].items():
            lines+=['### '+bank['levels'][tier]+' · '+article['title'],*article['paragraphs']]
            lines += [word+' · '+definition for word,definition in article['glossary'].items()]
        for study in bank['studies']:lines+=['### '+study['label'],study['body'],study['meaning'],study['source']]
    lines+=['## Infokarten']
    for card in bank['cards'].values():
        lines+=['### '+card['title']]
        for passage in card['sections'].values():
            lines+=['**'+passage['title']+'**',passage['text'],'Kurzfassung · '+passage['shortText']]
    (OUT/f'{person}-Material.md').write_text('\n\n'.join(lines)+'\n')
