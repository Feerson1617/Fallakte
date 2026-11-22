"""Audit the actual HTML and both Work formats against the five-section specification."""
import hashlib
import json
from pathlib import Path
import subprocess

from lxml import html

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist/Runde-1'
QA=ROOT/'build/runde1/qa'
LEVELS={'Foerder','ESA','MSA','AHR'}
METHODS={'K','P','Cu','H'}
STRATEGIES=METHODS|{'K+P','K+Cu','K+H'}
BASE='62b6dca2723006c25cc7724f5f595799b5743dd2'
TITLES=['Latexallergie','Zwei Schutzziele','Hormone und Alltag','Schmerzen und Einlage','Mein Schlussrat']


def main():
    app=(OUT/'Fallakte.html').read_bytes()
    doc=html.fromstring(app)
    bank=json.loads((OUT/'Materialvertrag.json').read_text())
    source=json.loads((ROOT/'data/laura-0212.json').read_text())
    work=(OUT/'Materialvertrag.md').read_text()
    assert bank==json.loads(doc.get_element_by_id('materialvertrag').text)
    assert {k:v for k,v in bank.items() if k!='buildCommit'}==source
    old=json.loads(subprocess.check_output(['git','show',BASE+':data/laura-0212.json'],cwd=ROOT))
    assert bank['version']=='0212-r2a.1'
    for sid,stage in bank['stages'].items():
        for key in ('id','title','knownFacts','newFacts','code','anchors'):
            assert stage[key]==old['stages'][sid][key], (sid,key)
    sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    assert bank['buildCommit']==sha and sha in work
    assert len(app)<10_000_000 and not doc.xpath('//script[@src]|//link[@rel="stylesheet"]')
    assert all(src.startswith('data:image/') for src in doc.xpath('//img/@src'))
    assert set(bank['levels'])==LEVELS and set(bank['strategies'])==STRATEGIES and set(bank['cards'])==METHODS
    for key,card in bank['cards'].items():
        for section,passage in card['sections'].items():
            assert passage['text']==old['cards'][key]['sections'][section]['text']
            assert passage['shortText'] in work and passage['text'] in work
    ending=bank['consolidation']['finalAdvice']
    assert ending['title']==bank['consolidation']['paperField'] and ending['compare'] in work
    for tier in LEVELS:
        writing=ending['levels'][tier]
        assert writing['focus'] in work and all(stem in work for stem in writing['stems'])
    for code,item in bank['strategies'].items():assert item['methods']==code.split('+')
    assert list(bank['stages'])==['L01','L02','L03','L04','L05']
    assert all(stage['playable'] for stage in bank['stages'].values())
    # Independent expectation from the brief. The tests never supply codes to the application or Work.
    assert ''.join(s['code'] for s in bank['stages'].values())=='BCABC'
    def audit_ref(ref):
        title=bank['cards'][ref['method']]['sections'][ref['section']]['title']
        assert title in work
    assert bank['normalization'] in work
    assert bank['paperFallbackInstruction'] in work
    assert all(rule['fact'] in bank['facts'] for rule in bank['goalRules'])
    previous=set()
    tasks=set()
    options=0
    for sid,stage in bank['stages'].items():
        n=int(sid[1:])
        assert stage['title']==f'Laura {n} – {TITLES[n-1]}'
        assert f'Laura {n} – Laura {n}' not in work
        assert previous<=set(stage['knownFacts'])
        previous=set(stage['knownFacts'])
        assert set(stage['newFacts'])<=previous
        assert all(bank['facts'][key] in work for key in previous) and stage['evidence'] in work
        assert stage['id']==sid and stage['title'] in work and stage['recovery'] in work and stage['information'] in work
        assert set(stage['anchors'])=={'A','B','C'} and all(v in work for v in stage['anchors'].values())
        for fb in stage['anchorFeedback'].values():
            assert fb['text'] in work
            audit_ref(fb['card'])
        assert set(stage['levels'])==LEVELS
        for tier,item in stage['levels'].items():
            task=item['taskId']
            original=old['stages'][sid]['levels'][tier]
            assert item['id']==original['id'] and task==original['taskId']
            assert task not in tasks and task in work
            tasks.add(task)
            assert item['task'] in work and item['message'] in work and set(item['strategies'])==STRATEGIES
            assert item.get('evidence',stage['evidence']) in work
            before=item['before']
            audit_ref(before['card'])
            assert len(before['hints'])==5 and all(h in work for h in before['hints'])
            assert all(q['id'] in work and q['text'] in work and q['answer'] in work for q in before['questions'])
            if tier in ('MSA','AHR'):
                assert item['paperPrompt'] and item['returnPrompt'] and item['paperPrompt'] in work and item['returnPrompt'] in work
                assert stage['title'] in item['paperPrompt'],(sid,tier)
                if stage['playable']:
                    assert item['paperFallback'] in work
            for key,label in item.get('choiceLabels',{}).items():
                assert key in STRATEGIES and label in work
            for code,strategy in item['strategies'].items():
                expected='B' if sid!='L01' and 'K' not in code.split('+') else 'C'
                assert strategy['status']==expected,(sid,tier,code)
                assert strategy['condition'] and strategy['feedback'] and strategy['feedback'] in work
                audit_ref(strategy['card'])
                if stage['playable']:
                    assert strategy['evidence'].strip() and strategy['evidence'] in work
                    corr=strategy.get('correction')
                    if expected=='B':
                        assert corr['label'] in work
                        if tier in ('MSA','AHR'):
                            assert not corr.get('target')
                        else:
                            assert corr['target']=='K+'+code
                for ref in strategy['extraCards']:audit_ref(ref)
                if strategy.get('goalCard'):audit_ref(strategy['goalCard'])
                assert len(strategy['hints'])==len(set(strategy['hints']))==5
                assert all(h in work for h in strategy['hints'])
                questions=strategy['questions']
                assert len({q['id'] for q in questions})==len(questions)
                for q in questions:assert q['text'] in work and q['answer'] in work
                o=strategy['options']
                if tier in ('MSA','AHR'):
                    assert not o
                else:
                    assert len(o) in ((2,) if tier=='Foerder' else (2,3))
                    assert sum(v['correct'] for v in o)==1
                    assert len({v['id'] for v in o})==len(o)
                    for v in o:
                        assert v['text'] in work and v['feedback'] in work
                        audit_ref(v['card'])
                        options+=1
    assert len(tasks)==20
    assert bank['stages']['L01']['levels']['Foerder']['primary']==['K','Cu']
    assert bank['stages']['L01']['levels']['ESA']['primary']==['K','Cu','H']
    assert len(bank['consolidation']['facts'])>1 and bank['consolidation']['paperField'] in work
    QA.mkdir(parents=True,exist_ok=True)
    (QA/'material.json').write_text(json.dumps(dict(commit=sha,bankversion=bank['version'],
        html_sha256=hashlib.sha256(app).hexdigest(),bytes=len(app),abschnitte=5,spielbar=5,aufgaben=len(tasks),
        strategiekontexte=len(tasks)*len(STRATEGIES),begruendungsoptionen=options,
        vertrag_sha256=hashlib.sha256((OUT/'Materialvertrag.json').read_bytes()).hexdigest()),indent=2)+'\n')
    print(f'20 Aufgaben, 140 Strategiekontexte und {options} begründete Antwortmöglichkeiten mit Work abgeglichen.')


if __name__=='__main__':main()
