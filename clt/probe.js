// Ausschließlich Testseite: über DOM-Bedienelemente in der ausgelieferten Datei arbeiten.
() => {
 const el=s=>document.querySelector(s), seen=new Map();
 let task='',caseName='';
 const root=()=>el('dialog[open]')||el('.lernraum:not([hidden])');
 function observe(event){
   const node=root();if(!node)return;
   const area=node.querySelector('.blatt')||node;
   const question=node.querySelector('.arbeitskopf h1')?.textContent||node.querySelector('h2')?.textContent||'';
   const text=area.innerText;
   const ids=[...area.querySelectorAll('button,textarea,summary')].filter(e=>e.getClientRects().length).map(e=>(e.id||e.textContent)+(e.disabled?' · gesperrt':''));
   if(/Laufzettel|Lernbogen|Prüfcode|Code prüfen|Zusatzbogen|Kreise .* ein|Seite [123]\b/i.test(text))throw Error('Alter Papierauftrag: '+text);
   const key=JSON.stringify([task,caseName,question,text,ids]);window.geometrie?.(key,node);if(!seen.has(key))seen.set(key,{task,caseName,question,text,ids,event});
 }
 function get(selector){const node=typeof selector==='string'?el(selector):selector;if(!node)throw Error('Fehlt '+selector+' · '+root()?.innerText);return node;}
 function click(selector){
   const n=get(selector);
   const d=n.closest('details:not([open])');if(d && n.tagName!=='SUMMARY')d.querySelector('summary').click();
   if(n.disabled || !n.getClientRects().length)throw Error('Gesperrt '+n.id+' '+task);
   n.click();observe(n.id||n.textContent);
 }
 function type(selector,value){const field=get(selector);field.value=value;field.dispatchEvent(new Event('input',{bubbles:true}));}
 function assert(ok,why){if(!ok)throw Error(why+' · '+task);}
 function help(day,depth){
   click(day===2?'#hilfe':'#help');
   for(let n=1;n<=depth;n++){
     assert(root().innerText.includes('Hilfe '+n),'Hilfestufe '+n);
     if(n<depth)click(day===2?'#hilfe-weiter':'#hint-next');
   }
   click(day===2?'#material-zurueck':'#dismiss');
 }
 function family({person,tier,mode}){
   const bank=JSON.parse(el('#material').textContent),c=bank.cases[person];caseName=person;
   const app=el('#app');task='Nachricht';observe('Einstieg');click('#next');
   const source=task=>task.evidenceSentences||[];
   let choices=0;
   for(const q of c.tasks){
     task=q.id;observe('Aufgabe');
     if(mode==='eigen'){
       click('#terms');
       if(q.id==='Leerstelle'){
         for(const word of Object.keys(bank.definitions)){
           click('#begriff-'+word);assert(root().textContent.includes(bank.definitions[word]),'Definition '+word);click('#dismiss');click('#terms');
         }
       }else assert(root().textContent.includes(bank.definitions[q.id==='Ergänzung'?c.missing:q.id]),'Definition');
       click('#dismiss');click('#cards');click('#dismiss');
     }
     if(el('textarea')){
       if(mode==='fehler' && source(q).length){
         const sentences=[...app.querySelectorAll('[id^=source-]')];
         for(const n of sentences.filter(n=>!source(q).includes(Number(n.id.split('-')[1]))))click(n);
         for(const i of source(q))click('#source-'+i);
       }
       type('textarea','Ich stütze meine Erklärung auf die Nachricht von '+person+'.');
       if(mode==='hilfe'||mode==='beispiel'){help(8,mode==='hilfe'?2:5);assert(el('textarea').value.includes(person),'Entwurf nach Hilfe');}
       click('#compare');
     }else if(mode==='hilfe'||mode==='beispiel')help(8,mode==='hilfe'?2:5);
     const bad=q.answers.flatMap((a,i)=>a.ok?[]:[i]),good=q.answers.findIndex(a=>a.ok);
     if(mode==='fehler'||mode==='beispiel')for(const i of [...bad,...bad.slice(0,1)]){
       click('#answer-'+i);assert(el('#response').textContent===q.answers[i].feedback,'Fehlertext');assert(!el('#next'),'Sperre');choices++;
     }
     click('#answer-'+good);choices++;
     assert(el('#response').textContent===q.answers[good].feedback,'Fachtext');
     assert(!bad.some(i=>el('#answer-'+i)),'Falsche Auswahl bleibt');
     if(mode==='eigen'){const status=app.querySelector('.tag').textContent;help(8,5);assert(app.querySelector('.tag').textContent===status,'Späte Hilfe ändert Status');}
     click('#next');
   }
   task='Anwendung';
   const exposed=mode==='beispiel'||(mode==='fehler' && c.tasks.find(t=>t.id==='Ergänzung').answers.some(a=>!a.ok && a.revealsSolution));
   if(exposed){
     const q=c.transfer;assert(el('[data-application]'),'Anwendung fehlt');help(8,5);
     for(const [i,a] of q.answers.entries())if(!a.ok){click('#answer-'+i);choices++;}
     click('#answer-'+q.answers.findIndex(a=>a.ok));choices++;
   }else assert(!el('[data-application]'),'Anwendung ohne Lösungsaufruf');
   observe('Fachinformation');click('#next');return choices;
 }
 function evaluateWeight({weight,concerns,errors}){
   const bank=JSON.parse(el('#material').textContent);caseName='Lauras Frage';task='Gewichtung '+weight;
   click('#weight-'+weight);
   for(const [part,concern] of concerns.entries()){
     click('#concern-'+concern);task='Fakt '+concern;
     if(errors)for(const i of [2,3,1-concern]){click('#fact-'+i);assert(!el('#answer-0'),'Unpassender Fakt');}
     click('#fact-'+concern);
     if(el('#other')){click('#other');assert(el('#check-reason').disabled,'Eigener Grund erforderlich');type('textarea','Beide Informationen gehören für mich zu Lauras Sorge.');click('#check-reason');}
     task='Reichweite '+concern;
     const q=bank.limits[concern];
     if(errors){help(8,5);for(const [i,a] of q.answers.entries())if(!a.ok)click('#answer-'+i);}
     click('#answer-'+q.answers.findIndex(a=>a.ok));click('#next');
   }
   assert(el('#spur-wahl') && !el('#spur-fertig'),'Individueller Abschluss fehlt');
 }
 function advice({tier,stage,method,mode}){
   if(el('#beratung-lesen'))click('#beratung-lesen');
   const data=window.LAURA.stages[stage],t=data.levels[tier],way=t.strategies[method];caseName='Laura '+stage;task='Empfehlung '+method;
   observe('Wahl');if(mode==='beispiel' && method==='K')help(2,5);
   click('[data-strategy="'+method+'"]');
   if(el('#erklaerung')){type('#erklaerung','Mein Vorschlag berücksichtigt Lauras Anliegen.');if(mode==='beispiel')help(2,5);assert(el('#erklaerung').value.startsWith('Mein Vorschlag'),'Verlust');click('#vergleichen');}
   const bad=way.options.filter(o=>!o.correct);let answers=0;
   if(mode==='beispiel'){
     help(2,5);
     for(const q of way.questions){click('#ask');click('[data-question-id="'+q.id+'"]');assert(el('#chat-meldungen').textContent.includes(q.answer),'Rückfrage fehlt');}
     click('#passende-karte');assert(el('#material-dialog [data-target=true]'),'Falsche Kartenstelle');click('#material-zurueck');
     for(const o of [...bad,...bad.slice(0,1)]){
       click('[data-option="'+o.id+'"]');answers++;
       assert(el('#fachmeldung').textContent===o.feedback && el('#nachricht-senden').disabled,'Falscher Grund');
     }
   }
   const o=way.options.find(o=>o.correct);click('[data-option="'+o.id+'"]');answers++;
   if(way.status==='C'){assert(!el('#nachricht-senden').disabled,'Passende Empfehlung gesperrt');click('#nachricht-senden');assert(el('[data-kind=send]'),'Gesendete Empfehlung fehlt');}
   else assert(el('#nachricht-senden').disabled && el('#fachmeldung').dataset.type==='B','Zielkonflikt');
   return answers;
 }
 return window.cltTest={click,observe,family,evaluateWeight,advice,label:value=>{caseName=value;task='Zusatzfall';},records:()=>[...seen.values()],clear:()=>seen.clear()};
}
