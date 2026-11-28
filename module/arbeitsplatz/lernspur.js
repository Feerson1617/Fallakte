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
    const draft=session.entwuerfe[phase]||={choice:'',reason:'',step:phase==='erst'?'lesen':'wahl'};
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
    for(const [who,text] of messages){
      const bubble=node(chat,'div',undefined,'bubble');
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
      auftrag='Lies die Nachrichten im Chat. →';hint='Lies zuerst, was dir die Personen schreiben.';
      button(work,'Weiter','spur-lesen',()=>{draft.step='wahl';draw();}).className='spur-weiter';
    }else if(waiting){
      auftrag='Warte auf das Zeichen deiner Lehrkraft.';hint='Nach der gemeinsamen Abstimmung kannst du den Chat starten.';
      node(work,'p','Dein erster Rat ist gespeichert.');
      button(work,'Chat starten','spur-chat',finish).className='spur-weiter';
    }else if(comparison){
      auftrag='Vergleiche deine beiden Gründe.';
      hint='Lies deine beiden Gründe. Was kannst du jetzt genauer erklären?';
      for(const [label,answer] of [['Am Anfang',s.erst],['Am Ende',s.schluss]]){
        node(work,'h2',label);
        if(answer){node(work,'strong',answer.choice);node(work,'p',answer.reason,'spur-zitat');}
        else node(work,'p','In dieser Sitzung gibt es keine erste Antwort.');
      }

      button(work,'Schlussantwort bearbeiten','spur-aendern',()=>{cfg.editing=true;draft.step='grund';draw();});
      button(work,'Zur Übersicht','spur-fertig',finish).className='spur-weiter';
    }else{
      const key=cfg.phase;
      const choosing=draft.step==='wahl';
      auftrag=choosing?(first?cfg.firstQuestion:cfg.finalQuestion):(first?'Warum denkst du das?':cfg.reason);
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
        hint='Öffne die Auswahl. Tippe auf deine Antwort.';
      }else{
      button(work,draft.choice+' · ändern','spur-wahl-aendern',()=>{draft.step='wahl';draw();});
      const reasonBox=node(work,'div',undefined,'spur-eingabe');
      const reason=node(reasonBox,'label',first?'Warum denkst du das?':cfg.reason);reason.htmlFor='spur-grund';reason.className='nur-vorlesen';
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
      hint=first?'Warum hast du das gewählt? Schreibe deinen Gedanken auf.':
        'Wähle deine Antwort. Nutze für deinen Grund eine Information aus den Nachrichten.';
    }
    }
    const help=button(work,'Ich brauche Hilfe','spur-hilfe',()=>{
      const error=!first && !comparison && cfg.diagnosis(s.entwuerfe.schluss.reason);
      const steps=first||comparison?null:error?Entwurf.hilfen('Fachinformation',error.frage,error.info):cfg.helpSteps;
      cfg.help(hint,steps);
    });
    Arbeitsplatz.setup(room,work,chat,heading,help,null,auftrag);
    heading.tabIndex=-1;heading.focus({preventScroll:true});
  }
  function erlaubt(tier){const s=sessions.get(tier);return Boolean(s?.erst||s?.wieder);}
  return {state,open,close,erlaubt,get offen(){return !!current;}};
})();
