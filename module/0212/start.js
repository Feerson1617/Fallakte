(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const bank=window.LAURA;
  if (!bank) {
    $('start').hidden=true;
    $('lokale-navigation').hidden=true;
    Arbeitsplatz.refresh();
    $('praesentation').hidden=true;
    $('quellhinweis').hidden=false;
    if (parent!==window) location.replace($('quellhinweis').querySelector('a').href);
    return;
  }
  const tierNames=bank.levels;
  const sections=['start','einstieg','beratung','reserve-platz'];
  let view='start',level='',pickerTier='',pickerPerson='Laura',origin='start',originLevel='',reserveStatus;
  let port;
  const available=new Set();
  let afterLevel=null;
  function grant(person,tier){available.add(tier+'/'+person);}
  window.addEventListener('beratung:abgeschlossen',e=>{
    grant('Tom',e.detail);
    grant('Celina',e.detail);
  });
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
    document.querySelector('[data-nav=abschluss]').disabled=!Lernspur.erlaubt(level);
    port?.postMessage({type:'view',abschluss:Lernspur.erlaubt(level),active:view==='start'?'home':view==='einstieg'?'recovery':'',status});
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
    levelGroup($('niveauplatz'),level,id=>{level=id;if(afterLevel){const act=afterLevel;afterLevel=null;act();}else drawHome();});
    const saved=Boolean(level && window.Beratung.has(level));
    $('weiterarbeiten').hidden=!saved;
    $('neu').disabled=!level;
    $('neu').classList.toggle('hauptaktion',!saved);
    const unlocked=available.has(level+'/Tom');
    for(const node of document.querySelectorAll('.vertiefungen,.vertiefungen+p,.reserven'))node.hidden=!unlocked;
    for(const b of document.querySelectorAll('[data-optional]'))b.disabled=!unlocked;
    Arbeitsplatz.setup($('start'),$('start'),null,$('start-titel'),null,b=>window.Material.orient('Wähle dein Niveau. Tippe auf „Neu beginnen“.',b));
  }
  function home() {
    Lernspur.close();show('start');drawHome();$('start-titel').focus({preventScroll:true});
  }
  function personal(phase,done){
    const titles=Object.values(bank.strategies).map(m=>m.label);
    const reasons={
      Foerder:'Was ist Laura wichtig? Wie hilft dein Rat? Stichworte reichen.',
      ESA:'Wie schützt dein Rat Laura? Welches Risiko bleibt?',
      MSA:'Wie passt die Wirkung zu Lauras Wunsch? Wann wäre ein anderer Rat möglich?',
      AHR:'Infektionen, Schwangerschaft, Schmerzen: Was zählt für deinen Rat am meisten? Wann würdest du Laura anders raten?'
    };
    Lernspur.open({status:text=>{const ok=Lernspur.erlaubt(level);document.querySelector('[data-nav=abschluss]').disabled=!ok;port?.postMessage({type:'view',abschluss:ok,active:'',status:text+' · '+tierNames[level]});},tier:level,firstTitle:'Dein erster Rat',finalTitle:'Dein Schlussrat',
      firstReason:choice=>'Dein erster Rat ist „'+choice+'“. Warum passt er für Laura?',firstQuestion:'Was rätst du Laura zuerst?',finalQuestion:'Was rätst du Laura jetzt?',
      warten:true,suggestion:Beratung.letzterRat(level),
      reference:label=>{
        const method=Object.keys(bank.strategies).find(k=>bank.strategies[k].label===label);
        return method && bank.stages.L05.levels[level].strategies[method].condition;
      },
      firstChoices:['Kondom',...titles.slice(1,4)],finalChoices:titles,reason:reasons[level],helpSteps:[
        'Lies Lauras Nachrichten neben deinem Rat.', 'Welcher Wunsch ist dir für Laura wichtig?',
        'Wie hilft deine Methode bei diesem Wunsch?', 'Beginne mit „Ich rate zu …, weil …“.',reasons[level]],
      startMessages:[['Laura',bank.opening]],endMessages:[
        ['Laura','Ich will mich vor einer Schwangerschaft und vor Infektionen schützen. Ich vertrage kein Latex.'],
        ['Laura','Mein Alltag wechselt. Manchmal vergesse ich etwas. Bei Hormonen bin ich unsicher. Meine Freundin hatte Probleme mit der Pille.'],
        ['Laura','Ich habe starke Regelschmerzen. Woher sie kommen, weiß ich noch nicht. Das Einsetzen einer Spirale macht mir Sorgen. Ich möchte selbst entscheiden.']],
      portrait:()=>document.querySelector('.hauptfall img').src,help:(text,more)=>Material.impuls(text,more),diagnosis:Entwurf.fehler,
      completed:()=>{grant('Tom',level);grant('Celina',level);},done},phase);
  }
  function final(){
    if(view==='einstieg' && pickerTier)level=pickerTier;
    if(!Lernspur.erlaubt(level))return;
    Material.close(false);Lernspur.state(level).begonnen=true;personal('schluss',home);
  }
  function start(stageId,resume=false,direct=false) {
    if (!level)return;
    if(!resume && window.Beratung.has(level) && !window.confirm('Diesen Abschnitt neu beginnen? Dein bisheriges Gespräch auf diesem Niveau wird ersetzt.'))return;
    const state=Lernspur.state(level);
    if(!resume && !direct && (!state.begonnen || state.entwuerfe.erst?.step==='warten')){
      personal('erst',()=>{state.entwuerfe.erst.step='fertig';start(stageId,false,true);});return;
    }
    state.begonnen=true;Lernspur.close();
    show('beratung');
    if (resume) window.Beratung.resume(level);
    else window.Beratung.begin(level,stageId);
    if(direct && !state.erst)state.wieder=true;
    communicate();
  }
  function reserve(person,index) {
    if (!level)return;

    if(!available.has(level+'/'+person))return;
    reserveStatus=null;
    show('reserve-platz');
    window.Reserve0212.open(person,level,index);
  }
  function drawPicker() {
    levelGroup($('wiederniveau'),pickerTier,id=>{pickerTier=id;drawPicker();});
    const people=['Laura',...['Tom','Celina'].filter(name=>available.has(pickerTier+'/'+name))];
    if(!people.includes(pickerPerson))pickerPerson='Laura';
    $('wiederfall').parentElement.hidden=people.length===1;
    $('wiederfall').replaceChildren(...people.map(person=>{
      const b=control(person,()=>{pickerPerson=person;drawPicker();$('wiederfall').querySelector('[aria-pressed=true]').focus();});
      b.setAttribute('aria-pressed',String(pickerPerson===person));return b;
    }));
    const steps=pickerPerson==='Laura' ? Object.values(bank.stages).filter(s=>s.playable).map(s=>[s.id,s.title]) :
      Array.from({length:pickerPerson==='Tom'?3:5},(_,i)=>[String(i+1),pickerPerson+' '+(i+1)]);
    $('abschnitte').replaceChildren(...steps.map(([id,title],i)=>{
      const b=control(title,()=>{
        level=pickerTier;
        if (pickerPerson==='Laura') start(id,false,true);
        else reserve(pickerPerson,i+1);
      });
      b.dataset.stage=id;b.disabled=!pickerTier;return b;
    }));
    Arbeitsplatz.setup($('einstieg'),$('einstieg'),null,$('einstieg-titel'),null,b=>window.Material.orient('Wähle dein Niveau und die Nachricht, bei der du weiterarbeiten möchtest.',b));
  }
  function recovery() {
    if (view==='einstieg')return;
    origin=view;originLevel=level;pickerTier=level;pickerPerson=view==='reserve-platz' && reserveStatus ? reserveStatus.person :'Laura';
    show('einstieg');drawPicker();$('einstieg-titel').focus({preventScroll:true});
  }
  function navigate(action,trigger) {
    if(action==='abschluss'){final();return;}
    if(action==='resources' && !Lernspur.state(level).begonnen){
      window.Material.orient('Halte zuerst deinen eigenen Rat fest.',trigger);return;
    }
    if(action==='home'||action==='recovery'){afterLevel=null;Lernspur.close();}
    if (action==='home')home();
    if (action==='recovery')recovery();
    if (action==='resources') {
      if (view==='reserve-platz')window.Reserve0212.cards();
      else window.Material.openCards(trigger,level || pickerTier || 'Foerder');
    }
  }
  $('sicherung-oeffnen').onclick=()=>{
    $('lehrkraft').open=false;
    window.Material.summary($('lehrkraft').querySelector('summary'), view==='einstieg' ? pickerTier : level);
  };
  $('neu').onclick=()=>start('L01');
  $('weiterarbeiten').onclick=()=>start(undefined,true);
  $('abschnitt-wahl').onclick=recovery;
  $('abbrechen').onclick=()=>{
    level=originLevel;
    if (origin==='beratung')start(undefined,true);
    else if (origin==='reserve-platz' && reserveStatus)reserve(reserveStatus.person);
    else home();
  };
  for (const b of document.querySelectorAll('[data-optional]')) b.onclick=()=>reserve(b.dataset.optional);
  for (const b of document.querySelectorAll('[data-nav]')) b.onclick=()=>navigate(b.dataset.nav,b);
  window.Runde1={home,final};
  window.addEventListener('beratung:view',communicate);
  window.addEventListener('reserve0212:status',e=>{reserveStatus=e.detail;communicate();});
  window.addEventListener('message',e=>{
    if (parent===window || e.source!==parent || e.data!=='fallakte:navigation' || !e.ports[0])return;
    port?.close();port=e.ports[0];port.onmessage=({data})=>{if(data==='lehrkraft')$('praesentation').hidden=false;else navigate(data);};
    $('lokale-navigation').hidden=true;
    Arbeitsplatz.refresh();
    port.postMessage({type:'ready',actions:[
      {id:'home',label:'Fallakten',icon:'folder'},{id:'resources',label:'Infokarten',icon:'book'},
      {id:'recovery',label:'Wiedereinstieg',icon:'restart'},{id:'abschluss',label:'Stundenabschluss'}
    ]});
    communicate();
  });
  $('praesentation').hidden=!new URLSearchParams(location.search).has('lehrkraft');
  drawHome();
})();
