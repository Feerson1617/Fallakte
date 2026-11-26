// Jeden unterscheidbaren Fehler über die ausgelieferten Tasten herstellen und alle fünf Hilfen lesen.
async ({name,niveau,tag})=>{
 const $=s=>document.querySelector(s);
 const tap=s=>{const n=$(s);if(!n||n.disabled)throw Error(name+'/'+niveau+': '+s);
   for(let d=n.parentElement;d;d=d.parentElement)if(d.tagName==='DETAILS')d.open=true;n.click();};
 const advanced=['MSA','AHR'].includes(niveau);
 const results=[];
 function hints(key,where,last){
   const family=tag==='08',next=family?'#hint-next':'#mehr-hilfe',box=family?'#dialog-body':'#reading';
   tap('#help');const lines=[];
   for(let i=0;i<5;i++){if(i)tap(next);lines.push($(box).querySelector('p').textContent);}
   tap(family?'#dismiss':'#back');
   if(lines.some(s=>!s.trim()) || !lines[4].includes(last) || (where&&!lines[0].includes(where)))throw Error(JSON.stringify([key,where,last,lines]));
   results.push({name,niveau,key,lines});
 }
 const fill=()=>{const f=$('textarea');f.value='Ich begründe meine Auswahl mit der Nachricht.';f.dispatchEvent(new Event('input',{bubbles:true}));};
 if(tag==='08'){
   level=niveau;const c=bank.cases[name];
   for(const [i,t] of [...c.tasks,c.transfer].entries()){
     resetPath();
     const transfer=i===c.tasks.length;
     if(transfer)record(name+'/Transfer').resumed=true;
     go('case',{person:name,at:i+1});
     if(advanced&&!transfer){
       if(t.evidenceSentences){
         const original=sentences(c.original);
         for(const [j] of original.entries())if(!t.evidenceSentences.includes(j)){
           tap('#source-'+j);hints(t.id+'/Quelle/'+j,name,original[t.evidenceSentences[0]]);
         }
       }
       fill();tap('#compare');
     }
     for(const [j,op] of t.answers.entries())if(!op.ok){
       tap('#answer-'+j);hints(t.id+'/'+j,null,(transfer&&advanced&&op.advancedText)?op.advancedFeedback:op.feedback);
     }
   }
 }else{
   port={postMessage(){}};window.setTierForTest(niveau);
   for(const [i,s] of bank.stages.entries()){
     for(const m of Object.keys(s.choices).length?Object.keys(s.choices):['']){
       save(fresh(i));draw();if(m)tap('[id="method-'+m+'"]');
       const clash=conflict();
       if(clash){hints([i,m,'Konflikt'],null,clash[lower()?'short':'full']);continue;}
       if(needsSource()){tap('#source');tap('#back');await new Promise(r=>setTimeout(r,35));}
       if(advanced){fill();tap('#vergleichen');}
       const check=currentCheck();
       for(const k of niveau==='Foerder'?check.short:'ABC')if(k!==check.code){
         tap('#answer-'+k);hints([i,m,k],null,check.feedback['ABC'.indexOf(k)]);
       }
     }
   }
 }
 return results;
}
