({tier, task, sample, repeat})=>{
  const material=JSON.parse(document.querySelector('#material').textContent), lesson=material.levels[tier];
  const view=document.querySelector('#page'),rows=[];
  const act=(key,value)=>document.querySelector('[data-action="'+key+'"]'+(value===undefined?'':'[data-value="'+value+'"]'));
  function hit(e){
    const b=e.getBoundingClientRect();
    if(b.width<43.5 || b.height<43.5 || b.top<-.5 || b.bottom>innerHeight+1 || !e.contains(document.elementFromPoint(b.x+b.width/2,b.y+b.height/2)))throw Error('Taste '+e.textContent+' / '+view.innerText);
  }
  function click(key,value){const b=act(key,value);if(!b)throw Error('Taste fehlt '+key+' '+tier+' '+sample+' / '+view.innerText);hit(b);b.click();}
  function record(phase){
    for(const b of document.querySelectorAll('button'))hit(b);
    rows.push([phase,view.dataset.screen,view.innerText]);
  }
  function answer(q,text){
    if(q.typ==='wahl'){click('pick',q.optionen.indexOf(text));return;}
    const field=document.querySelector('#entry');
    while(act('earlier'))click('earlier');
    while(field.value){field.value='';field.dispatchEvent(new Event('input',{bubbles:true}));}
    field.value=text;field.dispatchEvent(new Event('input',{bubbles:true}));click('check');
  }
  click('level',tier);click('questions');
  for(const q of lesson.fragen.slice(0,task)){answer(q,q.passend||material.modelle[q.modell].beispiel);click('advance');}
  const q=lesson.fragen[task];answer(q,sample);record('erster Versuch');
  if(repeat && act('revise')){click('revise');answer(q,sample);record('wiederholter Versuch');}
  click('help');for(let i=1;i<=5;i++){record('Hilfe '+i);if(i<5)click('more');}
  click('back');
  if(act('compare')){
    click('compare');record('Selbstvergleich');
    let text=document.querySelector('#draft').textContent;
    while(act('later')){click('later');text+=document.querySelector('#draft').textContent;}
    if(text!==sample)throw Error('Eigener Wortlaut');
    click('revise');answer(q,material.modelle[q.modell].beispiel);record('nach Korrektur');
  }else if(act('revise')){click('revise');answer(q,q.passend||material.modelle[q.modell].beispiel);record('nach Korrektur');}
  click('advance');return rows;
}
