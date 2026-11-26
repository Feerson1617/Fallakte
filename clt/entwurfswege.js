// Jede sendbare Empfehlung wird mit demselben Gegenbeispiel und einem eigenen neutralen Grund versucht.
({tier,stage,method})=>{
 const $=s=>document.querySelector(s);
 const tap=sel=>{const b=$(sel);if(!b||b.disabled)throw Error(sel);b.closest('details:not([open])')?.querySelector('summary')?.click();b.click();};
 const type=text=>{const f=$('#erklaerung');f.value=text;f.dispatchEvent(new Event('input',{bubbles:true}));};
 const myth='Die Pille schützt vor HIV. Ein Kondom ist nicht nötig.';
 const own='Ich berücksichtige Lauras persönliche Wünsche.';
 const correct='Pille und Spiralen schützen nicht vor HIV.';
 tap('[data-nav=home]');tap('#level-'+tier);tap('#abschnitt-wahl');tap('#wieder-level-'+tier);
 tap('[data-stage='+stage+']');tap('[data-strategy="'+method+'"]');
 const way=LAURA.stages[stage].levels[tier].strategies[method];
 type(myth);tap('#vergleichen');
 if(!$('#fachmeldung').textContent.includes(correct)||$('#erklaerung')?.value!==myth || $('[data-option]') || !$('#nachricht-senden').disabled)throw Error('Freigabe eines falschen Entwurfs');
 tap('#hilfe');const hilfen=[$('#hilfe-text').textContent];
 while($('#hilfe-weiter')){tap('#hilfe-weiter');hilfen.push($('#hilfe-text').textContent);}
 if(hilfen.length!==5||!hilfen[0].includes('Kombinationspille')||!hilfen[4].includes(correct))throw Error(hilfen.join(' / '));
 tap('#material-zurueck');type(own);tap('#vergleichen');
 const errors=[];
 for(const bad of way.options.filter(o=>!o.correct)){
   tap('[data-option="'+bad.id+'"]');tap('#hilfe');
   const s=[$('#hilfe-text').textContent];while($('#hilfe-weiter')){tap('#hilfe-weiter');s.push($('#hilfe-text').textContent);}
   if(!s[4].includes(bad.feedback))throw Error('Fachfehler ohne passende Hilfe');errors.push(s);tap('#material-zurueck');
 }
 tap('[data-option="'+way.options.find(o=>o.correct).id+'"]');
 if(way.status==='C'){
   if(!$('#beratung-arbeit').innerText.includes('Vergleiche deinen Grund'))throw Error('Vergleich fehlt');
   tap('#nachricht-senden');
   if($('[data-kind=send]').textContent.includes(own)||$('[data-kind=entwurf] p')?.textContent!==own ||
      !$('[data-kind=entwurf] strong').textContent.includes('ungeprüft'))throw Error('Eigener Grund falsch gekennzeichnet');
 }else if(!$('#nachricht-senden').disabled)throw Error('Zielkonflikt');
 return {tier,stage,method,sendbar:way.status==='C',hilfen,fehlerhilfen:errors};
}
