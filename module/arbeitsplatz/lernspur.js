// Zwei persönliche Momentaufnahmen. Nur das geöffnete Dokument besitzt diesen Speicher.
const Lernspur = (() => {
  const sessions=new Map();
  let current;
  function state(tier){
    if(!sessions.has(tier))sessions.set(tier,{begonnen:false,erst:null,schluss:null,entwuerfe:{}});
    return sessions.get(tier);
  }
  function node(parent,tag,text,cls){
    const n=document.createElement(tag);
    if(text!==undefined)n.textContent=text;
    if(cls)n.className=cls;
    parent.append(n);return n;
  }
  function button(parent,label,id,action){
    const b=node(parent,'button',label);b.type='button';b.id=id;b.onclick=action;return b;
  }
  function close(){
    document.getElementById('lernspur')?.remove();
    document.body.classList.remove('spur-offen');current=null;
  }
  function open(config,phase){
    const session=state(config.tier);
    const prior=phase==='schluss' && config.suggestion;
    const draft=session.entwuerfe[phase]||={choice:prior?.choice||'',reason:prior?.reason||'',step:phase==='erst'?'lesen':prior?'grund':'wahl'};
    current={...config,phase,draft};draw();
  }
  function draw(){
    const cfg=current,s=state(cfg.tier),first=cfg.phase==='erst';
    const comparison=!first && !!s.schluss && !cfg.editing;
    const title=comparison?'Dein Vergleich':first?cfg.firstTitle:cfg.finalTitle;
    cfg.status(title);
    let room=document.getElementById('lernspur');
    if(!room){room=node(document.body,'main');room.id='lernspur';}
    room.replaceChildren();room.className='';document.body.classList.add('spur-offen');
    const heading=node(room,'h1',title);
    const split=node(room,'div',undefined,'spur-spalten');
    const chat=node(split,'aside',undefined,'spur-chat');
    const work=node(split,'section',undefined,'spur-arbeit');
    const draft=cfg.draft;
    const reading=first && draft.step==='lesen';
    const waiting=first && draft.step==='warten';
    room.classList.toggle('lesephase',reading);
    const messages=first?cfg.startMessages:cfg.endMessages;
    const forwarded=reading && messages.some(([who])=>who==='Mutter');
    if(forwarded)chat.classList.add('nachrichten-einstieg');
    const inbox=forwarded?node(chat,'div',undefined,'nachrichten-liste'):chat;
    for(const [i,[who,text]] of messages.entries()){
      const bubble=node(forwarded && i===messages.length-1?chat:inbox,'div',undefined,'bubble');
      if(first && ['Mutter','Freundin'].includes(who)){bubble.classList.add('weitergeleitet');node(bubble,'small','Weitergeleitet');}
      const portrait=cfg.portrait(who);
      if(portrait){const img=node(bubble,'img');img.src=portrait;img.alt='';}
      node(bubble,'strong',who);
      if(bubble.classList.contains('weitergeleitet')){
        const lines=text.match(/[^.!?]+[.!?]+|[^.!?]+$/gu)||[text];
        node(bubble,'p',lines.shift().trim());node(bubble,'p',lines.join('').trim());
      }else node(bubble,'p',text);
    }
    function finish(){
      close();cfg.done(first);
    }
    let hint,auftrag;
    if(reading){
      auftrag=forwarded?'Lies die Nachrichten von Mama und der Freundin.':'Lies Lauras Nachricht im Chat.';hint=forwarded?'Im Chat stehen die beiden Nachrichten unter „Weitergeleitet“.':'Im Chat steht Lauras erste Frage unter ihrem Namen.';
      button(work,'Weiter','spur-lesen',()=>{draft.step='wahl';draw();}).className='spur-weiter';
    }else if(waiting){
      auftrag='Warte auf das Zeichen deiner Lehrkraft.';hint='Nach der gemeinsamen Abstimmung kannst du den Chat starten.';
      button(work,'Chat starten','spur-chat',finish).className='spur-weiter';
    }else if(comparison){
      auftrag=s.erst?'Was hat sich zwischen „Am Anfang“ und „Am Ende“ für dich geändert?':'Deine Antwort am Ende';
      hint=s.erst?'Unter „Am Anfang“ und „Am Ende“ stehen deine eigenen Worte.':'Unter „Am Ende“ steht dein eigener Satz.';
      for(const [label,answer] of [['Am Anfang',s.erst],['Am Ende',s.schluss]]){
        node(work,'h2',label);
        if(answer){node(work,'strong',answer.choice);node(work,'p',answer.reason,'spur-zitat');}
        else node(work,'p','In dieser Sitzung gibt es keine erste Antwort.');
      }

      const reference=cfg.reference?.(s.schluss.choice);
      if(reference){
        const detail=node(work,'details',undefined,'selbstvergleich');
        node(detail,'summary','Meinen Grund fachlich vergleichen');
        node(detail,'p',reference);
      }
      button(work,'Schlussantwort bearbeiten','spur-aendern',()=>{cfg.editing=true;draft.step='grund';draw();});
      button(work,'Zur Übersicht','spur-fertig',finish).className='spur-weiter';
    }else{
      const key=cfg.phase;
      const choosing=draft.step==='wahl';
      auftrag=choosing?(first?cfg.firstQuestion:cfg.finalQuestion):(first?cfg.firstReason(draft.choice):cfg.finalReason?.(draft.choice)||cfg.reason);
      if(!first && cfg.facts){
        const facts=node(work,'div',undefined,'faktenpaar');
        for(const fact of cfg.facts)node(facts,'p',fact);
      }
      if(choosing){
        const select=node(work,'select');select.id='spur-wahl';select.setAttribute('aria-label',auftrag);
        for(const text of ['',...(first?cfg.firstChoices:cfg.finalChoices)]){
          const option=node(select,'option',text||'Bitte wählen');option.value=text;
        }
        select.value='';
        select.onchange=()=>{if(select.value){draft.choice=select.value;draft.step='grund';draw();}};
        hint='Tippe auf „Bitte wählen“.';
      }else{
      if(!first && cfg.suggestion){
        const select=node(work,'select');select.id='spur-wahl';select.setAttribute('aria-label',cfg.finalQuestion);
        for(const label of cfg.finalChoices)node(select,'option',label).value=label;
        select.value=draft.choice;select.onchange=()=>{draft.choice=select.value;draw();};
      }else button(work,draft.choice+' · ändern','spur-wahl-aendern',()=>{draft.step='wahl';draw();});
      const reasonBox=node(work,'div',undefined,'spur-eingabe');
      const reason=node(reasonBox,'label',auftrag);reason.htmlFor='spur-grund';reason.className='nur-vorlesen';
      const input=node(reasonBox,'textarea');input.id='spur-grund';input.rows=2;input.value=draft.reason;
      if(first && ['ESA','Foerder','Förder'].includes(cfg.tier))input.placeholder='Stichworte reichen.';
      const feedback=node(work,'p','','spur-korrektur');feedback.hidden=true;feedback.setAttribute('role','status');
      const submit=button(work,first?'Erste Antwort festhalten':'Antworten vergleichen','spur-speichern',()=>{
        if(!draft.choice || !draft.reason.trim())return;
        const error=!first && cfg.diagnosis(draft.reason);
        if(error){feedback.textContent=error.info;feedback.hidden=false;Arbeitsplatz.refresh();Arbeitsplatz.zeigen(feedback);return;}
        s[key]=Object.freeze({choice:draft.choice,reason:draft.reason});
        if(first){s.begonnen=true;if(cfg.warten){draft.step='warten';draw();}else finish();}
        else{cfg.editing=false;cfg.completed();draw();}
      });
      submit.className='spur-weiter';
      function edit(){
        draft.reason=input.value;feedback.hidden=true;
        submit.disabled=!draft.choice||!draft.reason.trim();
      }
      input.oninput=edit;edit();
      hint=auftrag+' Schreibe in das weiße Feld.';
    }
    }
    const help=button(work,'Ich brauche Hilfe','spur-hilfe',()=>{
      const error=!first && !comparison && cfg.diagnosis(s.entwuerfe.schluss.reason);
      const steps=first||comparison?null:error?Entwurf.hilfen('Fachinformation',error.frage,error.info,error):cfg.helpSteps;
      const reference=!first && cfg.reference?.(draft.choice);
      if(steps && !error && reference)cfg.help(hint,[steps[0],reference,steps[2],steps[3],reference+' '+cfg.reason]);
      else cfg.help(hint,steps);
    });
    Arbeitsplatz.setup(room,work,chat,heading,help,null,auftrag);
    heading.tabIndex=-1;heading.focus({preventScroll:true});
  }
  function erlaubt(tier){const s=sessions.get(tier);return Boolean(s?.erst||s?.wieder);}
  return {state,open,close,erlaubt,get offen(){return !!current;}};
})();
