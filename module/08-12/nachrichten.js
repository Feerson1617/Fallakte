(() => {
  'use strict';
  const data = document.getElementById('material').textContent;
  if (!data) {
    const built = el('a','','Gebaute Fallakte öffnen');
    built.href = '../../build/08-12/Fallakte.html';
    document.getElementById('page').append(built);
    return;
  }
  const book = JSON.parse(data);
  const people = Object.keys(book.cases);
  const main = document.getElementById('page');
  const actions = [
    {id:'overview', label:'Nachrichten', icon:'folder'},
    {id:'resources', label:'Fachkarten', icon:'book'},
    {id:'recovery', label:'Nach Neustart', icon:'restart'}
  ];
  let port, screen='overview', person=people[0], section=1, lastTask=null;
  let mode={first:book.levels[0],second:''}, recoveryMode;
  let returnScreen='overview', beforeCards='overview', recoveryPerson='', recoveryQuestions=false;
  let openedCard='';
  const sessions=new Map();
  function range() {
    return book.levels.filter(l=>l===mode.first || l===mode.second);
  }
  function modeLabel() { return [mode.first,mode.second].filter(Boolean).join(' + '); }

  const block = (style = 'stack') => el('div', style);
  const heading = (tag, label, style) => {
    const h = el(tag, style, label);
    h.tabIndex = -1;
    return h;
  };
  function group(label, style) {
    const box = el('fieldset');
    box.append(el('legend', '', label));
    const list = block(style);
    box.append(list);
    return [box, list];
  }
  function press(label, fn, selected, cls) {
    const b = button(label, fn, cls);
    b.setAttribute('aria-pressed', String(selected));
    return b;
  }
  function session() {
    const key = [person,section].join('/');
    if (!sessions.has(key)) sessions.set(key, {index:section === 1 ? 0 : 1, drafts:{}, complete:false});
    return sessions.get(key);
  }
  function tasks() {
    const levels=range(), tier=session().index===0 ? levels[0] : levels.at(-1);
    return book.cases[person].levels[tier];
  }
  function item() { return tasks()[session().index]; }
  function draft() {
    const s = session();
    return s.drafts[s.index] ||= {answer:null, depthAnswers:{}, hint:0, help:false, topic:'', mark:null, evidence:null, goal:null, link:null,
      matches:{}, reason:'', spoken:false, own:false, reader:null, full:false, laura:false};
  }
  function show(view) {
    screen = view;
    render();
    window.scrollTo(0,0);
    main.querySelector('h1')?.focus({preventScroll:true});
  }
  function enter(who, part, question) {
    person=who; section=part; lastTask=[who,part];
    if (question!==undefined) session().index=question;
    show('task');
  }
  function navigate(action) {
    if (action === 'resources') {
      if (screen !== 'resources') { beforeCards = screen; openedCard = ''; show('resources'); }
    } else if (action === 'recovery') {
      if (screen !== 'recovery') {
        if (screen !== 'resources' || beforeCards !== 'recovery') {
          returnScreen = screen === 'resources' ? beforeCards : screen;
        }
        recoveryPerson=''; recoveryQuestions=false; recoveryMode={...mode}; show('recovery');
      }
    } else if (action === 'overview') show('overview');
  }
  function levelChoice(current,changed) {
    const [box, options]=group('Niveau','levels');
    for (const l of book.levels) options.append(press(l,()=>{
      changed({first:l,second:l===current.second?current.first:current.second});
    },l===current.first));
    const label=el('label','pair-label','Zweites Niveau ');
    const select=el('select');
    select.setAttribute('aria-label','Zweites Niveau');
    for (const l of ['',...book.levels.filter(l=>l!==current.first)]) {
      const o=el('option','',l || 'Keins'); o.value=l; select.append(o);
    }
    select.value=current.second;
    select.onchange=()=>changed({...current,second:select.value});
    label.append(select);
    box.append(disclosure('Zu zweit auf zwei Niveaus',label,Boolean(current.second)));
    return box;
  }
  function changeMode(nextMode) { mode=nextMode; render(); }
  function lines(texts, ids) {
    const list = el('ol', 'lines');
    for (const id of ids || texts.map((_,i)=>i+1)) {
      const row = el('li');
      row.append(el('b','',String(id)), el('span','',texts[id-1]));
      list.append(row);
    }
    return list;
  }
  function disclosure(label, content, open, changed) {
    const d = el('details');
    d.open = Boolean(open);
    d.append(el('summary','',label), content);
    if (changed) d.ontoggle = () => changed(d.open);
    return d;
  }
  function overview() {
    const hero = el('header','hero'), image = el('img','portrait');
    image.src = '../../assets/laura.webp'; image.alt = 'Laura';
    const title = block('');
    title.append(heading('h2','Dienstag, 08.12.2026','date'), heading('h1',book.lead));
    hero.append(image,title);
    const intro = el('section','intro');
    intro.append(el('p','',book.context+' Sie ist trotz Verhütung ungeplant schwanger.'),
      disclosure('Lauras ganze Nachricht',lines(book.laura)));
    const groups = block('groups');
    for (const [n, label] of ['Pflichtaufgaben – Bearbeite beide Nachrichten.', 'Zusatzaufgaben – Wenn du fertig bist.'].entries()) {
      const part = el('section','group');
      part.append(heading('h2',label));
      for (const who of people.slice(2*n,2*n+2)) {
        const entry = block('person');
        book.cases[who].sections.forEach((name,i) => entry.append(button(name,()=>enter(who,i+1),'section-link')));
        part.append(entry);
      }
      groups.append(part);
    }
    main.append(hero,intro,levelChoice(mode,changeMode),groups);
    if (lastTask) main.append(button('Zur offenen Stelle',()=>enter(...lastTask)));
  }
  function recovery() {
    main.append(heading('h1','Nach Neustart weitermachen'), levelChoice(recoveryMode,m=>{recoveryMode=m;render();}));
    const [box, list] = group('Wähle die Person.', 'row');
    for (const who of people) list.append(press(who,()=>{recoveryPerson=who;recoveryQuestions=false;render();},who===recoveryPerson));
    main.append(box);
    if (recoveryPerson) {
      const [box, list] = group('Wähle den Abschnitt.', 'options');
      book.cases[recoveryPerson].sections.forEach((name,i) => list.append(button(name,()=>{
        if (i===0) { mode={...recoveryMode}; enter(recoveryPerson,1,0); }
        else { recoveryQuestions=true; render(); }
      })));
      main.append(box);
    }
    if (recoveryQuestions) {
      const [part,choices]=group('Welche Frage steht auf deinem Lernbogen?', 'options');
      book.questions.forEach((q,i)=>choices.append(button((i+1)+'. '+q,()=>{
        mode={...recoveryMode};enter(recoveryPerson,2,i+1);
      })));
      main.append(part);
    }
    main.append(button('Zurück',()=>show(returnScreen)));
  }
  function cardLines(c,ids) {
    if (!c.parts) return lines(c.lines,ids);
    const part=block('stack');
    for (const [title,numbers] of Object.entries(c.parts)) {
      const selected=numbers.filter(n=>!ids || ids.includes(n));
      if (selected.length) part.append(heading('h3',title),lines(c.lines,selected));
    }
    return part;
  }
  function cardContent(key, ids) {
    const c = book.cards[key], part = block('stack');
    part.append(heading('h2',c.title),cardLines(c,ids));
    return part;
  }
  function resources() {
    main.append(heading('h1','Fachkarten'));
    for (const [key, c] of Object.entries(book.cards)) {
      const body = block('stack');
      body.append(cardLines(c),el('p','sources','Quellen: '+c.sources.join(' · ')));
      const d = disclosure(c.title,body,openedCard===key);
      d.className = 'panel';
      main.append(d);
    }
    main.append(button('Zurück',()=>show(beforeCards),'primary'));
  }
  function sourcePanel(task, state) {
    const panel = el('aside','panel stack'), message = book.cases[person].message;
    panel.append(heading('h2','Nachricht · '+person));
    if (state.reader !== null) {
      panel.append(lines(message,[state.reader]));
      const controls = block('row');
      if (state.reader>1) controls.append(button('Voriger Teil',()=>{state.reader--;render();}));
      if (state.reader<message.length) controls.append(button('Nächster Teil',()=>{state.reader++;render();}));
      controls.append(button('Lesen beenden',()=>{state.reader=null;render();}));
      panel.append(controls);
    } else {
      if (task.lines?.length) panel.append(lines(message,task.lines));
      if (task.lines?.length !== message.length)
        panel.append(disclosure('Ganze Nachricht lesen',lines(message),state.full,v=>{state.full=v;}));
      panel.append(button('Zeile für Zeile lesen',()=>{state.reader=1;render();}));
    }
    if (task.mother?.length) panel.append(heading('h3','Zum Vergleich · Mutter'),lines(book.cases.Mutter.message,task.mother));
    if (task.wishes) {
      if (task.wishes.length) panel.append(heading('h3','Lauras Worte'),lines(book.laura,task.wishes));
    }
    panel.append(disclosure('Lauras ganze Nachricht',lines(book.laura),state.laura,v=>{state.laura=v;}));
    if (task.kind==='judgment') {
      panel.append(button('Ganze Fachkarte',()=>{beforeCards='task';openedCard=task.card[0];show('resources');}));
    } else if (task.card) {
      const [key,ids] = task.card;
      const card = cardContent(key,ids);
      card.classList.add('intro');
      card.append(button('Ganze Fachkarte',()=>{beforeCards='task';openedCard=key;show('resources');}));
      panel.append(card);
    }
    return panel;
  }
  function helpBox(state,topics,chooseTopic=true) {
    const names=Object.keys(topics);
    const wrap=block('stack');
    if (!names.includes(state.topic)) state.topic=names[0];
    const toggle=button('Hilfe',()=>{state.help=!state.help;update();});
    const panel=block('note stack'), list=block('help-list'), content=el('p');
    content.setAttribute('aria-live','polite');
    const target=el('select');
    if (names.length>1 && chooseTopic) {
      const label=el('label','pair-label','Hilfe zu ');
      target.setAttribute('aria-label','Hilfe zu');
      for (const name of names) target.append(el('option','',name));
      target.onchange=()=>choose(target.value);
      label.append(target);panel.append(label);
    }
    const buttons=book.helps.map((title,i)=>{
      const b=button(String(i+1),()=>{state.hint=i;update();});
      b.setAttribute('aria-label','Hilfe '+(i+1)+' – '+title);
      list.append(b);return b;
    });
    const title=el('h3');
    panel.append(list,title,content);
    function choose(name) {
      if (state.topic!==name) {state.topic=name;state.hint=0;update();}
    }
    function update() {
      target.value=state.topic;
      toggle.setAttribute('aria-expanded',String(state.help));
      toggle.textContent=state.help?'Hilfe schließen':'Hilfe';
      panel.hidden=!state.help;
      buttons.forEach((b,i)=>b.setAttribute('aria-pressed',String(state.hint===i)));
      title.textContent=book.helps[state.hint];
      content.textContent=topics[state.topic][state.hint];
    }
    wrap.append(toggle,panel);update();
    return {wrap,choose};
  }
  function next() {
    if (section===1) {session().complete=true;enter(person,2);}
    else {session().index++;show('task');}
  }
  function argumentMap(task,state,body) {
    const help=helpBox(state,Object.fromEntries(task.fields.map(f=>[f.name,f.hints])));
    body.append(el('p','',task.prompt),help.wrap);
    const fields=block('category-grid');
    const onward=button('Weiter',next,'primary');
    function updateNext() {
      onward.hidden=!book.cases[person].levels.AHR[0].fields.every(f=>f.options.some(o=>o.line===state.matches[f.name] && o.correct));
    }
    for (const field of task.fields) {
      const label=el('label','map-field'), select=el('select');
      select.setAttribute('aria-label',field.name);
      const empty=el('option','','Zeile …');
      empty.value='';
      select.append(empty);
      const options=[...field.options];
      const prior=state.matches[field.name];
      if (prior && !options.some(o=>o.line===prior)) {
        const full=book.cases[person].levels.AHR[0].fields.find(f=>f.name===field.name);
        options.push(full.options.find(o=>o.line===prior));
      }
      for (const option of options) {
        const row=el('option','','Zeile '+option.line);
        row.value=String(option.line);
        select.append(row);
      }
      select.value=String(state.matches[field.name] ?? '');
      const result=el('small','');
      result.setAttribute('role','status');
      const update=()=>{
        const value=Number(select.value);
        state.matches[field.name]=value;
        const option=options.find(o=>o.line===value);
        result.hidden=!option;
        if (option) {
          result.className=option.correct?'feedback':'feedback retry';
          result.textContent=(option.correct?'Das passt. ':'Prüfe noch einmal. ')+option.feedback;
        }
        updateNext();
      };
      select.onfocus=()=>help.choose(field.name);
      select.onchange=()=>{help.choose(field.name);update();};
      label.append(el('strong','',field.name),el('small','',book.categories[field.name]),select);
      const cell=block('map-cell');
      cell.append(label,result);
      fields.append(cell);
      update();
    }
    body.append(fields,onward);
  }
  function check(task,state,body) {
    const tier=range().at(-1);
    const topics={Grundfrage:task.hints};
    if (task.depth) topics[tier]=task.depth.hints;
    const help=helpBox(state,topics,false);
    help.choose(task.options[state.answer]?.correct && task.depth?tier:'Grundfrage');
    body.append(el('p','',task.prompt),help.wrap);
    const onward=button('Weiter',next,'primary');
    const extra=block('intro stack');
    function refresh() {
      const ready=task.options[state.answer]?.correct;
      extra.hidden=!ready;
      onward.hidden=!ready || Boolean(task.depth && !task.depth.options[state.depthAnswers[tier]]?.correct);
    }
    function answers(container,question,selected,change) {
      const options=block('options'), feedback=el('div');
      feedback.setAttribute('role','status');
      const buttons=question.options.map((o,i)=>{
        const b=press(o.label,()=>{change(i);selected=i;update();refresh();},false);
        if (o.citation) b.append(el('small','source-ref','Kartenzeile '+o.citation));
        options.append(b);return b;
      });
      function update() {
        const o=question.options[selected];
        buttons.forEach((b,i)=>b.setAttribute('aria-pressed',String(i===selected)));
        feedback.hidden=!o;
        feedback.className=o?.correct?'feedback':'feedback retry';
        feedback.textContent=o?(o.correct?'Das passt. ':'Prüfe noch einmal. ')+o.feedback:'';
      }
      container.append(options,feedback);update();
    }
    answers(body,task,state.answer,i=>{
      state.answer=i;
      help.choose(task.options[i].correct && task.depth?tier:'Grundfrage');
    });
    if (task.depth) {
      extra.append(heading('h2',tier+' · Weiterdenken'),el('p','',task.depth.prompt));
      const remaining=task.depth.lines.filter(n=>!task.lines.includes(n));
      if (remaining.length) extra.append(lines(book.cases[person].message,remaining));
      answers(extra,task.depth,state.depthAnswers[tier],i=>{state.depthAnswers[tier]=i;help.choose(tier);});
      body.append(extra);
    }
    body.append(onward);refresh();
  }
  function verdict(task,state,body) {
    const ui=book.verdictUI, levels=range(), tier=levels.at(-1);
    const simple=levels[0]==='Förder', ownRequired=tier!=='Förder';
    const [key,ids]=task.card, card=book.cards[key];
    body.append(el('p','',task.prompt),helpBox(state,{Begründung:task.hints}).wrap);
    const steps=[];
    function picks(title,labels,field,style='options') {
      const [box,list]=group(title,style);
      const buttons=labels.map((s,i)=>{
        const b=press(s,()=>{state[field]=i;sync();},false);
        list.append(b);return b;
      });
      steps.push({box,buttons,field});body.append(box);
    }
    body.append(el('p','line-label','Fachkarte · '+card.title));
    picks(ui.evidence,ids.map(n=>card.lines[n-1]),'evidence');
    picks(ui.goal,task.goals.map(n=>book.laura[n-1]),'goal');
    picks(ui.rating,task.options,'mark','row');
    if (simple) picks(ui.reason,task.links,'link');
    const writing=block('stack'), typed=el('textarea'), label=el('label','',ui.write);
    typed.id='mein-grund';label.htmlFor=typed.id;typed.value=state.reason;
    typed.oninput=()=>{state.reason=typed.value;notice.hidden=true;};
    const say=press(ui.spoken,()=>{state.spoken=!state.spoken;sync();},state.spoken);
    if (task.counter) writing.append(el('p','note',task.counter));
    writing.append(label,typed,el('p','small',ui.oral),say);
    if (ownRequired) writing.append(disclosure('Grund selbst prüfen',el('p','note',task.selfCheck)));
    const own=ownRequired?writing:disclosure(ui.own,writing,state.own,v=>{state.own=v;});
    const notice=el('p','note');notice.setAttribute('role','status');
    const finish=button(ui.done,()=>{
      if (simple && ownRequired && state.link===null) {
        notice.textContent='Wählt einen Grund zur Fachinformation.';notice.hidden=false;return;
      }
      if (!state.reason.trim() && !state.spoken && (ownRequired || state.link===null)) {
        notice.textContent=ownRequired?'Schreibe deinen Grund. Oder sage ihn und bestätige ihn.':'Wähle einen Grund. Oder erkläre ihn selbst.';
        notice.hidden=false;return;
      }
      session().complete=true;show('done');
    },'primary');
    function sync() {
      let visible=true;
      for (const {box,buttons,field} of steps) {
        box.hidden=!visible;
        buttons.forEach((b,i)=>b.setAttribute('aria-pressed',String(i===state[field])));
        if (field!=='link') visible=visible && state[field]!==null;
      }
      own.hidden=!visible;finish.hidden=!visible;
      say.setAttribute('aria-pressed',String(state.spoken));notice.hidden=true;
    }
    body.append(own,notice,finish);sync();
  }
  function taskPage() {
    const s=session(), task=item(), state=draft(), box=block('work'), body=el('article','panel stack');
    const location=book.cases[person].sections[section-1]+(section===2?' · Frage '+s.index+' von 3':'');
    const top=block('row');
    top.append(el('p','eyebrow',location),disclosure('Niveau · '+modeLabel(),levelChoice(mode,changeMode)));
    main.append(top);
    body.append(heading('h1',task.heading,'question'));
    if (task.kind==='judgment') verdict(task,state,body);
    else if (task.kind==='map') argumentMap(task,state,body);
    else check(task,state,body);
    if (s.index>1) body.append(button('Vorige Frage',()=>{s.index--;show('task');}));
    box.append(sourcePanel(task,state),body);main.append(box);
  }
  function done() {
    const state=draft(), task=item();
    main.append(heading('h1',person+' · Abschnitt fertig'),heading('h2','Gewählte Fachinformation'),
      el('p','',book.cards[task.card[0]].lines[task.card[1][state.evidence]-1]),
      el('p','','Laura: „'+book.laura[task.goals[state.goal]-1]+'“'),
      heading('h2','Einschätzung'),el('p','',task.options[state.mark]));
    if (range()[0]==='Förder' && state.link!==null) main.append(el('p','',task.links[state.link]));
    if (state.reason.trim()) main.append(el('p','',state.reason));
    main.append(el('p','note',book.verdictUI.reflect),
      button('Mein Urteil ansehen',()=>show('task')));
    if (person==='Mutter') main.append(button('Weiter zur Freundin',()=>enter('Freundin',1),'primary'));
    main.append(button('Zur Nachrichtenübersicht',()=>show('overview')));
  }
  function render() {
    main.replaceChildren();
    ({overview,resources,recovery,task:taskPage,done})[screen]();
    const status = ['task','done'].includes(screen)?person+' '+section+' · '+modeLabel():'';
    port?.postMessage({type:'view',active:screen,status});
  }
  if (parent === window) {
    const nav=document.getElementById('local');nav.hidden=false;
    actions.forEach(a=>nav.append(button(a.label,()=>navigate(a.id))));
  }
  window.addEventListener('message',e=>{
    if (e.source!==parent || e.data!=='fallakte:navigation' || !e.ports[0]) return;
    port?.close();port=e.ports[0];port.onmessage=({data})=>navigate(data);
    port.postMessage({type:'ready',actions});render();
  });
  render();
})();
