tier=>{
 const doc=JSON.parse(document.querySelector('#bank').textContent);
 const s=doc.stages[Number(document.querySelector('#step').textContent.match(/\d+/)[0])-1];
 const {click,observe}=cltTest;let answers=0;
 // Prüfe auch nach einer bereits tragfähigen Auswahl den Wechsel zu den anderen Vorschlägen.
 for(const key of (Object.keys(s.choices).length?Object.keys(s.choices):[''])){
   if(key){
     if(document.querySelector('#edit'))click('#edit');
     click('[id="method-'+key+'"]');
   }
   click('#help');
   while(document.querySelector('#mehr-hilfe'))click('#mehr-hilfe');
   click('#back');click('#source');click('#back');
   if(document.querySelector('#ask')){
     const q=(s.checks?.[key]||s).questions||s.questions;
     for(let n=0;n<q.length;n++){click('#ask');click(document.querySelectorAll('#reading button[id^=q]')[n]);}
   }
   if(s.conflicts?.[key]){if(document.querySelector('#send'))throw Error('Zielkonflikt');continue;}
   if(document.querySelector('#erklaerung')){
     const input=document.querySelector('#erklaerung');input.value='Ich berücksichtige die Wünsche und die Wirkung der Methode.';input.dispatchEvent(new Event('input'));click('#vergleichen');
   }
   const c=s.checks?.[key]||s;
   const ids=[...document.querySelectorAll('[id^=answer-]')].map(e=>e.id.slice(-1));
   for(const letter of ids.filter(l=>l!==c.code)){click('#answer-'+letter);answers++;if(document.querySelector('#send'))throw Error('Unzutreffender Grund');}
   click('#answer-'+c.code);answers++;
   if(!document.querySelector('#send'))throw Error('Passender Grund gesperrt');
 }
 observe('Zusatzfall abgeschlossen');return answers;
}
