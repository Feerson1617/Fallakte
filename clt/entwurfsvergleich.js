// Teilzustände aus der eingebetteten Auslieferung. Fachlich geprüft werden ausschließlich geschlossene Aussagen.
({name,tier,tag})=>{
 const $=s=>document.querySelector(s);
 const tap=s=>{const n=$(s);if(!n||n.disabled)throw Error(s);const d=n.closest('details:not([open])');if(d)d.open=true;n.click();};
 const type=value=>{const f=$('textarea');f.value=value;f.dispatchEvent(new Event('input',{bubbles:true}));};
 const original='Das ist mein eigener Gedanke, weil Laura selbst entscheidet.';
 const myth='Die Pille schützt vor HIV. Ein Kondom ist nicht nötig.';
 const rows=[];
 if(tag==='08'){
   level=tier;const c=bank.cases[name];
   for(const [i,task] of c.tasks.entries()){
     resetPath();go('case',{person:name,at:i+1});
     for(const [satz,korrektur] of [[myth,'nicht vor HIV'],['Ein Abbruch macht immer unfruchtbar.',bank.cards[1].short]]){
       type(satz);tap('#compare');
       if(!$('#draft-error')?.innerText.includes(korrektur)||$('textarea').value!==satz||$('[id^="answer-"]'))throw Error(name+' / '+task.id);
       tap('#help');tap('#hint-last');if(!$('#dialog-body').innerText.includes(korrektur))throw Error('Hilfe 5');tap('#dismiss');
     }
     type(original);tap('#compare');tap('#answer-'+task.answers.findIndex(o=>o.ok));
     const own=saved.history.get(name+'/'+task.id+'/entwurf');
     if(own.text!==original||!own.speaker.includes('ungeprüft')||!$('#next'))throw Error('Eigenes Urteil im Familienrat');
     rows.push([name,tier,task.id]);
   }
 }else{
   port={postMessage(){}};window.setTierForTest(tier);
   for(const [i,s] of bank.stages.entries()){
     for(const m of Object.keys(s.choices).length?Object.keys(s.choices):['']){
       if(s.conflicts?.[m])continue;
       save(fresh(i));draw();
       if(m)tap('[id="method-'+m+'"]');
       if(needsSource()){tap('#source');dialog.close();draw();}
       type(myth);tap('#vergleichen');
       if(!$('#feedback').innerText.includes('nicht vor HIV')||$('#erklaerung').value!==myth||$('#send'))throw Error('Fehler im Zusatzfall');
       tap('#help');while($('#mehr-hilfe'))tap('#mehr-hilfe');
       if(!$('#reading').innerText.includes('nicht vor HIV'))throw Error('Zusatzhilfe');tap('#back');
       type(original);tap('#vergleichen');tap('#answer-'+currentCheck().code);tap('#send');
       if(!state.sent || state.history.at(-2).includes(original)||!$('.gespraech').innerText.includes('ungeprüft'))throw Error('Ungeprüfte Begründung');
       rows.push([name,tier,i,m]);
     }
   }
 }
 return rows;
}
