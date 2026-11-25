({key,tier})=>{
  const $=s=>document.querySelector(s);
  function click(el){
    if(typeof el==='string')el=$(el);
    if(!el || el.disabled)throw Error('Bedienelement fehlt '+key);
    const details=el.closest('details');
    if(details&&!details.open)details.querySelector('summary').click();
    if(!el.getClientRects().length)throw Error('Bedienelement ausgeblendet '+el.id);
    el.click();
  }
  const stage=window.LAURA.stages[$('#beratung-stage').dataset.stage],task=stage.levels[tier];
  function help(context){
    click('#hilfe');
    for(let i=0;i<5;i++){
      if($('#hilfe-text').innerText!==context.hints[i])throw Error('Falsche Hilfe '+i);
      if(i<4)click('#hilfe-weiter');
    }
    click('#material-zurueck');
  }
  function ask(context){
    for(const q of context.questions){
      click('#ask');click('[data-question-id="'+q.id+'"]');
      if(!$('#beratung').innerText.includes(q.answer))throw Error('Rückfrage '+q.id);
    }
  }
  if(key==='K'){help(task.before);ask(task.before);}
  click('[data-strategy="'+key+'"]');
  const way=task.strategies[key];
  help(way);ask(way);
  if($('#passende-karte')){click('#passende-karte');if($('#material-ganze-karte')){click('#material-ganze-karte');click('#material-zurueck');}click('#material-zurueck');}
  const paper=['MSA','AHR'].includes(tier), form=$('#pruefcode');
  const possible=paper?['Z',...Object.keys(stage.anchors).filter(x=>x!==stage.code),stage.code]:
    way.options.slice().sort((a,b)=>Number(a.correct)-Number(b.correct)).map(o=>o.id);
  for(const value of possible){
    if(paper){form.value=value;form.dispatchEvent(new Event('input',{bubbles:true}));click('#fachcheck-pruefen');}
    else click('[data-option="'+value+'"]');
    if(!$('#fachmeldung').innerText)throw Error('Rückmeldung fehlt '+value);
  }
  const submit=$('#nachricht-senden');
  if(!submit.disabled){click(submit);if(!$('#beratung .chat-entry[data-kind=send]'))throw Error('Nachricht fehlt');}
  return {abschnitt:stage.id,niveau:tier,methode:key,antworten:possible.length,rueckfragen:way.questions.length,hilfen:5};
}
