(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const bank=window.LAURA;
  if (!bank) {
    $('start').hidden=true;
    $('lokale-navigation').hidden=true;
    $('praesentation').hidden=true;
    $('quellhinweis').hidden=false;
    if (parent!==window) location.replace($('quellhinweis').querySelector('a').href);
    return;
  }
  const tierNames=bank.levels;
  const sections=['start','einstieg','beratung','reserve-platz'];
  let view='start',level='',pickerTier='',pickerPerson='Laura',origin='start',reserveStatus;
  let port;
  function control(label,callback) {
    const button=document.createElement('button');
    button.type='button';button.textContent=label;button.onclick=callback;
    return button;
  }
  function levelGroup(parent,selected,choose) {
    const field=document.createElement('fieldset'),legend=document.createElement('legend'),buttons=document.createElement('div');
    legend.textContent='Wähle dein Niveau';buttons.className='niveaus';
    for (const [id,label] of Object.entries(tierNames)) {
      const b=control(label,()=>{
        choose(id);
        parent.querySelector('[aria-pressed="true"]')?.focus({preventScroll:true});
      });
      b.setAttribute('aria-pressed',String(id===selected));
      b.id=(parent.id==='niveauplatz'?'level-':'wieder-level-')+id;
      buttons.append(b);
    }
    field.append(legend,buttons);parent.replaceChildren(field);
  }
  function communicate() {
    const s=view==='beratung' ? window.Beratung.status() : null;
    const status=s ? 'Laura '+Number(s.stageId.slice(1))+' · '+tierNames[s.tier] :
      view==='reserve-platz' && reserveStatus ? reserveStatus.person+' '+reserveStatus.abschnitt+' · '+tierNames[reserveStatus.tier] : '';
    port?.postMessage({type:'view',active:view==='start'?'home':view==='einstieg'?'recovery':'',status});
  }
  function show(next) {
    if (view==='beratung' && next!=='beratung') window.Beratung.pause();
    window.Material.close(false);
    $('lehrkraft').open=false;
    if (view==='reserve-platz' && next!==view) window.Reserve0212.hide();
    view=next;
    for (const id of sections) $(id).hidden=id!==next;
    document.querySelector('[data-nav="recovery"]').hidden=next==='start' || next==='einstieg';
    for (const b of $('lokale-navigation').querySelectorAll('button')) {
      if ((next==='start' && b.dataset.nav==='home') || (next==='einstieg' && b.dataset.nav==='recovery')) b.setAttribute('aria-current','page');
      else b.removeAttribute('aria-current');
    }
    window.scrollTo(0,0);
    communicate();
  }
  function drawHome() {
    levelGroup($('niveauplatz'),level,id=>{level=id;drawHome();});
    const saved=Boolean(level && window.Beratung.has(level));
    $('weiterarbeiten').hidden=!saved;
    $('neu').disabled=!level;
    $('neu').classList.toggle('hauptaktion',!saved);
    for (const b of document.querySelectorAll('[data-optional]')) b.disabled=!level;
  }
  function home() {
    show('start');drawHome();$('start-titel').focus({preventScroll:true});
  }
  function start(stageId,resume=false) {
    if (!level)return;
    show('beratung');
    if (resume) window.Beratung.resume(level);
    else window.Beratung.begin(level,stageId);
    communicate();
  }
  function reserve(person,index) {
    if (!level)return;
    reserveStatus=null;
    show('reserve-platz');
    window.Reserve0212.open(person,level,index);
  }
  function drawPicker() {
    levelGroup($('wiederniveau'),pickerTier,id=>{pickerTier=id;drawPicker();});
    $('wiederfall').replaceChildren(...['Laura','Tom','Celina'].map(person=>{
      const b=control(person,()=>{pickerPerson=person;drawPicker();$('wiederfall').querySelector('[aria-pressed=true]').focus();});
      b.setAttribute('aria-pressed',String(pickerPerson===person));return b;
    }));
    const steps=pickerPerson==='Laura' ? Object.values(bank.stages).filter(s=>s.playable).map(s=>[s.id,s.title]) :
      Array.from({length:pickerPerson==='Tom'?3:5},(_,i)=>[String(i+1),pickerPerson+' '+(i+1)]);
    $('abschnitte').replaceChildren(...steps.map(([id,title],i)=>{
      const b=control(title,()=>{
        level=pickerTier;
        if (pickerPerson==='Laura') start(id);
        else reserve(pickerPerson,i+1);
      });
      b.dataset.stage=id;b.disabled=!pickerTier;return b;
    }));
  }
  function recovery() {
    if (view==='einstieg')return;
    origin=view;pickerTier=level;pickerPerson=view==='reserve-platz' && reserveStatus ? reserveStatus.person :'Laura';
    show('einstieg');drawPicker();$('einstieg-titel').focus({preventScroll:true});
  }
  function navigate(action,trigger) {
    if (action==='home')home();
    if (action==='recovery')recovery();
    if (action==='resources') {
      if (view==='reserve-platz')window.Reserve0212.cards();
      else window.Material.openCards(trigger);
    }
  }
  $('sicherung-oeffnen').onclick=()=>{
    $('lehrkraft').open=false;
    window.Material.summary($('lehrkraft').querySelector('summary'));
  };
  $('neu').onclick=()=>start('L01');
  $('weiterarbeiten').onclick=()=>start(undefined,true);
  $('abschnitt-wahl').onclick=recovery;
  $('abbrechen').onclick=()=>{
    if (origin==='beratung')start(undefined,true);
    else if (origin==='reserve-platz' && reserveStatus)reserve(reserveStatus.person);
    else home();
  };
  for (const b of document.querySelectorAll('[data-optional]')) b.onclick=()=>reserve(b.dataset.optional);
  for (const b of document.querySelectorAll('[data-nav]')) b.onclick=()=>navigate(b.dataset.nav,b);
  window.Runde1={home};
  window.addEventListener('beratung:view',communicate);
  window.addEventListener('reserve0212:status',e=>{reserveStatus=e.detail;communicate();});
  window.addEventListener('message',e=>{
    if (parent===window || e.source!==parent || e.data!=='fallakte:navigation' || !e.ports[0])return;
    port?.close();port=e.ports[0];port.onmessage=({data})=>navigate(data);
    $('lokale-navigation').hidden=true;
    port.postMessage({type:'ready',actions:[
      {id:'home',label:'Fallakten',icon:'folder'},{id:'resources',label:'Infokarten',icon:'book'},
      {id:'recovery',label:'Abschnitt auswählen',icon:'restart'}
    ]});
    communicate();
  });
  drawHome();
})();
