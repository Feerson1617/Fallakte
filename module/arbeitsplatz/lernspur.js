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
    current={...config,phase};draw();
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
    const messages=first?cfg.startMessages:cfg.endMessages;
    for(const [who,text] of messages){
      const bubble=node(chat,'div',undefined,'bubble');
      const portrait=cfg.portrait(who);
      if(portrait){const img=node(bubble,'img');img.src=portrait;img.alt='';}
      node(bubble,'strong',who);node(bubble,'p',text);
    }
    function finish(){
      close();cfg.done(first);
    }
    let hint;
    if(comparison){
      hint='Lies deine beiden Gründe. Was kannst du jetzt genauer erklären?';
      for(const [label,answer] of [['Am Anfang',s.erst],['Am Ende',s.schluss]]){
        node(work,'h2',label);
        if(answer){node(work,'strong',answer.choice);node(work,'p',answer.reason,'spur-zitat');}
        else node(work,'p','In dieser Sitzung gibt es keine erste Antwort.');
      }
      node(work,'p','Was begründest du jetzt anders oder genauer?');
      button(work,'Schlussantwort bearbeiten','spur-aendern',()=>{cfg.editing=true;draw();});
      button(work,'Zur Übersicht','spur-fertig',finish).className='spur-weiter';
    }else{
      const key=cfg.phase;
      const draft=s.entwuerfe[key]||={choice:!first?cfg.suggestion||'':'',reason:!first?cfg.reasonDraft||'':''};
      const prompt=first?cfg.firstQuestion:cfg.finalQuestion;
      const choiceBox=node(work,'div',undefined,'spur-eingabe');
      const label=node(choiceBox,'label',prompt);label.htmlFor='spur-wahl';
      const select=node(choiceBox,'select');select.id='spur-wahl';
      for(const text of ['',...(first?cfg.firstChoices:cfg.finalChoices)]){
        const option=node(select,'option',text||'Bitte wählen');option.value=text;
      }
      select.value=draft.choice;
      const reasonBox=node(work,'div',undefined,'spur-eingabe');
      const reason=node(reasonBox,'label',first?'Warum denkst du das?':cfg.reason);reason.htmlFor='spur-grund';
      const input=node(reasonBox,'textarea');input.id='spur-grund';input.rows=2;input.value=draft.reason;
      if(first && ['ESA','Foerder','Förder'].includes(cfg.tier))input.placeholder='Stichworte reichen.';
      const feedback=node(work,'p','','spur-korrektur');feedback.hidden=true;feedback.setAttribute('role','status');
      const submit=button(work,first?'Erste Antwort festhalten':'Antworten vergleichen','spur-speichern',()=>{
        if(!draft.choice || !draft.reason.trim())return;
        const error=!first && cfg.diagnosis(draft.reason);
        if(error){feedback.textContent=error.info;feedback.hidden=false;Arbeitsplatz.refresh();Arbeitsplatz.zeigen(feedback);return;}
        s[key]=Object.freeze({choice:draft.choice,reason:draft.reason});
        if(first){s.begonnen=true;finish();}
        else{cfg.editing=false;cfg.completed();draw();}
      });
      submit.className='spur-weiter';
      function edit(){
        draft.choice=select.value;draft.reason=input.value;feedback.hidden=true;
        submit.disabled=!draft.choice||!draft.reason.trim();
      }
      select.onchange=input.oninput=edit;edit();
      hint=first?'Wähle deine Antwort. Schreibe deinen eigenen Grund in das Feld.':
        'Wähle deine Antwort. Nutze für deinen Grund eine Information aus den Nachrichten.';
    }
    const help=button(work,'Ich brauche Hilfe','spur-hilfe',()=>{
      const error=!first && !comparison && cfg.diagnosis(s.entwuerfe.schluss.reason);
      const steps=first||comparison?null:error?Entwurf.hilfen('Fachinformation',error.frage,error.info):cfg.helpSteps;
      cfg.help(hint,steps);
    });
    Arbeitsplatz.setup(room,work,chat,heading,help);
    heading.tabIndex=-1;heading.focus({preventScroll:true});
  }
  return {state,open,close,get offen(){return !!current;}};
})();
