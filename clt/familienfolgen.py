from playwright.sync_api import sync_playwright
from pathlib import Path
import json,itertools,time
import os,sys,hashlib
R=Path(__file__).resolve().parents[1]
engine,tier=sys.argv[1:]
release=R/'dist/Gesamt/Fallakte-08-12.html'
html=release.read_text()
out=R/'build/CLT'/f'08-{tier}-{engine}'/'Familienfolgen.json'
out.parent.mkdir(parents=True,exist_ok=True)
res={'html_sha256':hashlib.sha256(release.read_bytes()).hexdigest(),'counts':{},'errors':[]}
# independent input combinations using the actual parent navigation and UI, not internal function calls
JS=r'''async ({tier,mode,jobs})=>{
const b=JSON.parse(document.querySelector('#material').textContent),u=b.ui,results=[];const q=s=>document.querySelector(s);function click(s){const n=q(s);if(!n||n.disabled)throw Error('Missing or disabled '+s+' / '+q('#app').innerText);let d=n.closest('details:not([open])');if(d)d.querySelector('summary').click();n.click()};const pause=ms=>new Promise(r=>setTimeout(r,ms));async function until(s){for(let i=0;i<200;i++){if(q(s))return;await pause(1)}throw Error('Waiting for '+s)};function select(s,val){const n=q(s);if(!n)throw Error(s);n.value=val;n.dispatchEvent(new Event('change',{bubbles:true}))};function type(txt){const f=q('textarea');if(!f)throw Error('No textarea');f.value=txt;f.dispatchEvent(new Event('input',{bubbles:true}))};function help(n){if(!n)return;click('#help');for(let i=1;i<n;i++)click('#hint-next');click('#dismiss')};async function nav(key,s){parent.document.querySelector('[data-action='+key+']').click();await until(s)};function personal(){if(q('#spur-wahl')){select('#spur-wahl',q('#spur-wahl').options[1].value);const field=q('#spur-grund');field.value='Ich möchte Lauras Anliegen berücksichtigen.';field.dispatchEvent(new Event('input'));click('#spur-speichern')}if(q('#spur-fertig'))click('#spur-fertig')};async function reset(){parent.document.querySelector('[data-action=home]').click();for(let j=0;j<100&&!q('#level-0');j++)await pause(2);if(q('#level-0').value!==tier)select('#level-0',tier);click('#start');if(q('#confirm-start'))click('#confirm-start');personal();await until('#next')};async function recover(person,at){await nav('recovery','#open-entry');if(q('#level-0').value!==tier)select('#level-0',tier);if(!Array.from(q('#person').options).some(o=>o.value===person)){await nav('abschluss','#spur-wahl');personal();await nav('recovery','#open-entry')};select('#person',person);select('#entry',String(at));click('#open-entry')};
for(const job of jobs){try{await reset();if(mode==='case'){const {name,at,depth,wrong,late}=job;await recover(name,at+1);const t=b.cases[name].tasks[at];if(q('textarea')){if(t.evidenceSentences?.length)click('#source-'+t.evidenceSentences[0]);type('Der Text nennt ein Anliegen. Ich begründe es mit der Nachricht.');click('#compare')};help(depth);for(const i of wrong){click('#answer-'+i);if(q('#next'))throw Error('Falsch freigegeben');if(q('#response')?.textContent!==t.answers[i].feedback)throw Error('Falscher Feedbacktext')};const i=t.answers.findIndex(x=>x.ok);click('#answer-'+i);const r=q('.tag').textContent,exp=depth===5||wrong.some(i=>t.answers[i].revealsSolution)?u.used:depth?u.explain:wrong.length?u.corrected:u.own;if(r!==exp)throw Error('Status '+r+' != '+exp);if(late){help(5);if(q('.tag').textContent!==r)throw Error('Status nach Hilfe geändert')};click('#next');results.push({ok:true})}
else{await recover('Lauras Frage',2);const {weight,concerns,facts,limits}=job;click('#weight-'+weight);for(let k=0;k<concerns.length;k++){const c=concerns[k],f=facts[k],l=limits[k];click('#concern-'+c);click('#fact-'+f);if(f!==c){if(q('#answer-0'))throw Error('Unpassender Fakt freigegeben');click('#fact-'+c)}if(q('#other')){click('#other');type('Die Frage ist für Laura wichtig, weil beide Informationen helfen können.');click('#check-reason')};let correct=b.limits[c].answers.findIndex(x=>x.ok);click('#answer-'+l);if(l!==correct){if(q('#next'))throw Error('Falsche Reichweite freigegeben');click('#answer-'+correct)}click('#next')};if(!q('#spur-wahl')&&!q('#spur-fertig'))throw Error('Digitaler Abschluss fehlt');personal();results.push({ok:true})}}
catch(e){results.push({ok:false,error:String(e),job})}}return results}'''
with sync_playwright() as w:
 br=getattr(w,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE'));p=br.new_page(viewport={'width':1180,'height':820});p.on('dialog',lambda d:d.accept());p.set_content(html);p.locator('#zweiter-tag').click();f=p.frame_locator('#arbeitsplatz iframe').first;f.locator('#level-0').wait_for();frame=p.frames[-1];bank=frame.evaluate("JSON.parse(document.querySelector('#material').textContent)"); print('ready',flush=True)
 if tier in bank['levels']:
  for mode in ['case','weight']:
   jobs=[]
   if mode=='case':
    for name,c in bank['cases'].items():
     for at,t in enumerate(c['tasks']):
      bad=[i for i,a in enumerate(t['answers']) if not a['ok']]
      # ordered subsets cover last failure and set of prior errors; same repeated error handled separately below
      seq=[tuple(s) for n in range(len(bad)+1) for s in itertools.permutations(bad,n)]
      for dep,wrong in itertools.product(range(6),seq):jobs.append(dict(name=name,at=at,depth=dep,wrong=wrong,late=True))
   else:
    for weight in range(4):
     n=1 if weight<2 else 2
     opts=[(c,f,l) for c in range(2) for f in range(4) for l in range(len(bank['limits'][c]['answers']))]
     for combo in itertools.product(opts,repeat=n):jobs.append(dict(weight=weight,concerns=[a[0] for a in combo],facts=[a[1] for a in combo],limits=[a[2] for a in combo]))
   print(tier,mode,'total',len(jobs),flush=True); key=tier+' '+mode;res['counts'][key]={'total':len(jobs),'attempted':0,'pass':0}
   for i in range(0,len(jobs),32):
    batch=jobs[i:i+32]; rr=frame.evaluate(JS,{'tier':tier,'mode':mode,'jobs':batch});res['counts'][key]['attempted']+=len(rr);res['counts'][key]['pass']+=sum(x['ok'] for x in rr);res['errors'] += [[tier,mode,x] for x in rr if not x['ok']];out.write_text(json.dumps(res,ensure_ascii=False));print(key,res['counts'][key],flush=True)
 br.close()

assert not res['errors'] and sum(row['total'] for row in res['counts'].values())==1414,res['errors'][:1]
