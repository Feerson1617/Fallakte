({key,tier})=>{
  const $=s=>document.querySelector(s);
  let hits=0;
  function visible(el){
    const r=el.getBoundingClientRect(),p=el.closest('.blatt-inhalt')?.getBoundingClientRect();
    return r.height>=43.5 && r.width>=43.5 && (!p || r.left>=p.left-1 && r.right<=p.right+1 && r.bottom<=p.bottom+1 && r.top>=p.top-1) &&
      el.contains(document.elementFromPoint(r.left+r.width/2,r.top+r.height/2));
  }
  function click(el){
    if(typeof el==='string')el=$(el);
    if(!el || el.disabled)throw Error('Bedienelement fehlt '+key);
    const details=el.closest('details');
    if(details&&!details.open && el.tagName!=='SUMMARY')click(details.querySelector('summary'));
    if(!el.getClientRects().length)throw Error('Bedienelement ausgeblendet '+el.id);
    if(!visible(el)){
      const sheet=el.closest('.blatt'),controls=sheet?.querySelector(':scope>.blatt-wechsel');
      for(const dir of ['firstElementChild','lastElementChild']){
        const turn=controls?.[dir];
        while(!visible(el) && turn && !turn.disabled && !controls.hidden){
          if(!visible(turn))throw Error('Blättertaste verdeckt '+el.id);
          turn.click();
        }
      }
    }
    if(!visible(el))throw Error('Trefferfläche nicht erreichbar '+el.id+' '+tier+' '+key);
    hits++;el.click();
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
  const paper=['MSA','AHR'].includes(tier);
  const possible=paper?['Z',...Object.keys(stage.anchors).filter(x=>x!==stage.code),stage.code]:
    way.options.slice().sort((a,b)=>Number(a.correct)-Number(b.correct)).map(o=>o.id);
  for(const value of possible){
    if(paper){const form=$('#pruefcode');form.value=value;form.dispatchEvent(new Event('input',{bubbles:true}));click('#fachcheck-pruefen');}
    else click('[data-option="'+value+'"]');
    if(!$('#fachmeldung').innerText)throw Error('Rückmeldung fehlt '+value);
  }
  const submit=$('#nachricht-senden');
  if(!submit.disabled){click(submit);if(!$('#beratung .chat-entry[data-kind=send]'))throw Error('Nachricht fehlt');}
  return {abschnitt:stage.id,niveau:tier,methode:key,antworten:possible.length,rueckfragen:way.questions.length,hilfen:5,treffer:hits};
}
