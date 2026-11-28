"""Feste Sollwerte und reale Übergänge von der eigenen Formulierung zur Hilfe und zur Überarbeitung."""
import base64
import csv
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from playwright.sync_api import sync_playwright
from pruefen import QA,OUT,HERE,sha

def run(engine):
    results=[]; developments=[];models={};stress={}
    html=(OUT/'Fallakte-08-12.html').read_bytes()
    family=base64.b64decode(re.search(rb'<script id="modul-08"[^>]*>([^<]+)',html)[1]).decode()
    raw=(OUT/'Fallakte-02-12.html').read_bytes()
    ub1=base64.b64decode(re.search(rb'<script id="modul-02"[^>]*>([^<]+)',raw)[1]).decode()
    with sync_playwright() as pw,getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as browser:
        p=browser.new_page();p.set_content(family)
        models['familie']=p.evaluate("""()=>Object.fromEntries(Object.entries(bank.cases).flatMap(([person,c])=>c.tasks.map(t=>[person+'/'+t.id,{key:person+'/'+t.id,frage:t.prompt,beispiel:t.answers.find(a=>a.ok).text,alternativen:t.answers}])) )""")
        test="""([model,text])=>Diagnose.analyse(text,model,medizin)"""
        dev={'Mutter/Wert':{'vollständig':['Gesundheit','Lauras Gesundheit','Dass Laura gesund bleibt','Sie möchte nicht, dass Laura krank wird.','Dass es Laura körperlich gut geht.'],'verwechslung':['Man sollte auf seinen Körper achten.','Laura soll das Kind bekommen.']}}
        for key,model in models['familie'].items():
            corpus=dev.get(key,{})
            for ans in model['alternativen']:
                corpus.setdefault('vollständig' if ans['ok'] else 'andere',[]).append(ans['text'])
            for expected,words in corpus.items():
                for word in words:
                    result=p.evaluate(test,[model,word])
                    assert (result['status']==expected if expected!='andere' else result['status']!='vollständig'),(key,word,result)
                    developments.append([key,word,expected,result['status']])
        personal=dict(key='Laura/Pille',persoenlich=True,pille=True,frage='Was verändert die Pille beim Eisprung?',beispiel='Die Pille hemmt meist den Eisprung.')
        for row in [dict(r,Bestand=file.stem) for file in (HERE/'Sprachreserve.tsv',HERE/'Sprachreserve-blind.tsv') for r in csv.DictReader(file.open(),delimiter='\t')]:
            key=row['Aufgabe'];model=models['familie'].get(key,personal)
            result=p.evaluate(test,[model,row['Antwort']])
            assert not(result['status']=='vollständig' and row['Soll']!='vollständig'),(row,result)
            results.append({**row,'Ist':result['status'],'Rueckmeldung':result['feedback'],'Hilfen':result['hints']})
        # Sichtbare Diagnose, alle fünf Hilfen und Fortsetzung am echten Aufgabenfeld.
        visible=[]
        for text in ['Gesundheit','Man sollte auf seinen Körper achten.','Laura soll das Kind bekommen.','Sie hat das anders gemeint.','Die Pille verhindert eine HIV-Infektion.']:
            obs=p.evaluate("""text=>{level='AHR';resetPath();go('case',{person:'Mutter',at:1});
              const q=s=>document.querySelector(s),set=t=>{q('textarea').value=t;q('textarea').dispatchEvent(new Event('input'))};
              set(text);q('#compare').click();const initial=q('[data-diagnose]')?.textContent||q('#draft-error')?.textContent;
              q('#help').click();const hints=[];for(let i=0;i<5;i++){hints.push(q('#dialog-body p').textContent);if(i<4)q('#hint-next').click()}
              q('#dismiss').click();if(q('#entwurf-bearbeiten')){q('#entwurf-bearbeiten').click();set('Gesundheit');q('#compare').click()}
              const task=bank.cases.Mutter.tasks[0];q('#answer-'+task.answers.findIndex(a=>a.ok)).click();q('#next').click();
              return {text,initial,hints,weiter:current.at}}""",text)
            assert obs['initial'] and obs['weiter']==2 and len(obs['hints'])==5,obs
            visible.append(obs)
        p.set_content(ub1)
        models['beratung']=p.evaluate("""()=>Object.fromEntries(Object.values(LAURA.stages).flatMap(s=>Object.entries(s.levels).filter(([t])=>['MSA','AHR'].includes(t)).flatMap(([t,l])=>Object.entries(l.strategies).map(([m,a])=>[s.id+'/'+m+'/'+t,{...Aussagen.beratung(s.id,LAURA.strategies[m].methods,a,a.writeQuestion),ziele:s.knownFacts,fehler:a.options.filter(o=>!o.correct)}]))))""")
        models['zusatz']={}
        for person in ('Tom','Celina'):
            module=base64.b64decode(re.search('<script id="reserve-'+person+'"[^>]*>([^<]+)',ub1)[1]).decode()
            p.set_content(module);data=p.evaluate("JSON.parse(document.getElementById('bank').textContent)")
            models['zusatz'][person]=[{k:s[k] for k in ('task','checks','conflicts') if k in s} for s in data['stages']]
        models['persoenlich']='Erste und letzte Einschätzung, Gewichtung und alternative Begründungen sind persönlich. Offene Texte erhalten keine Gesamtnote. Beim Abschluss werden eindeutige medizinische Aussagen geprüft. Erstposition und Schlussposition werden getrennt gespeichert.'
        pool=json.loads((HERE/'Belastung.json').read_text())
        texts=[[a+' '+b,c] for a in pool['vorsatz'] for b,c in pool['teilsaetze']]
        assert len({r[0] for r in texts})==len(texts)>=100
        def stress_test(frame,group,items):
            observed=frame.evaluate('''([items,texts])=>items.map(model=>{
              const counts={};for(const [text,correction] of texts){
                const a=Diagnose.analyse(text,model);
                if(correction ? !a.error?.info.includes(correction) : !!a.error || a.status==='vollständig')throw Error(model.key+' / '+text+' / '+a.status);
                counts[a.status]=(counts[a.status]||0)+1;
              }return {aufgabe:model.key,zaehlung:counts};})''',[items,texts])
            stress[group]=observed
        stress_test(p,'Familiennachrichten',list(models['familie'].values()))
        stress_test(p,'Beratung',[dict(v,key=k) for k,v in models['beratung'].items()])
        others=[]
        for person,stages in models['zusatz'].items():
            for i,s in enumerate(stages,1):
                for m,c in s.get('checks',{}).items():
                    for t in ('MSA','AHR'):
                        others.append(dict(key=f'{person}/{i}/{m}/{t}',frage=s['task'][t],persoenlich=True))
        stress_test(p,'Zusatzfälle',others)
        stress_test(p,'Eigene Lernspuren',[dict(key=f'{day}/{tier}/{stage}',persoenlich=True) for day in ('02','08') for tier in ('Förder','ESA','MSA','AHR') for stage in ('Erster Grund','Schlussgrund')]+[dict(key='Gewichtung/'+str(i),persoenlich=True) for i in (0,1)])
    folder=QA/'Freigabestufen';folder.mkdir(parents=True,exist_ok=True)
    rates={k:dict(Counter('erkannt' if r['Ist']==r['Soll'] else 'abweichend' for r in results if r['Art']==k and r['Bestand']=='Sprachreserve-blind')) for k in sorted({r['Art'] for r in results})}
    (folder/f'Sprache-{engine}.json').write_text(json.dumps(dict(html_sha256=sha(html),ub1_sha256=sha(raw),reserve=results,entwicklung=developments,sichtbar=visible,quoten=rates,systematische_Zusatztests=stress,zusatztexte=texts),ensure_ascii=False,indent=2))
    (folder/'Antwortmodelle.json').write_text(json.dumps(models,ensure_ascii=False,indent=2))
    print(engine,rates)
if __name__=='__main__':run(sys.argv[1])
