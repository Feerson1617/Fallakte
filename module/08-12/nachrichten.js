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
  let port, screen = 'overview', person = people[0], level = book.levels[0], section = 1;
  let returnScreen = 'overview', beforeCards = 'overview', recoveryPerson = '', recoveryLevel;
  let openedCard = '';
  const lastTask = new Map();
  const sessions = new Map();

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
    const key = [level,person,section].join('/');
    if (!sessions.has(key)) sessions.set(key, {index:section === 1 ? 0 : 1, drafts:{}, complete:false});
    return sessions.get(key);
  }
  function tasks() { return book.cases[person].levels[level]; }
  function item() { return tasks()[session().index]; }
  function draft() {
    const s = session();
    return s.drafts[s.index] ||= {answer:null, hint:0, help:false, mark:null, evidence:null, link:null,
      reason:'', spoken:false, own:false, reader:null, full:false, laura:false};
  }
  function show(view) {
    screen = view;
    render();
    window.scrollTo(0,0);
    main.querySelector('h1')?.focus({preventScroll:true});
  }
  function enter(who, part) {
    person = who; section = part; lastTask.set(level,[who,part]);
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
        recoveryPerson = ''; recoveryLevel = level; show('recovery');
      }
    } else if (action === 'overview') show('overview');
  }
  function levelChoice(current, fn) {
    const [box, options] = group('Niveau', 'levels');
    for (const l of book.levels) options.append(press(l, () => fn(l), l === current));
    return box;
  }
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
    main.append(hero,intro,levelChoice(level,l=>{level=l; render();}),groups);
    if (lastTask.has(level)) main.append(button('Zur offenen Stelle',()=>enter(...lastTask.get(level))));
  }
  function recovery() {
    main.append(heading('h1','Nach Neustart weitermachen'), levelChoice(recoveryLevel,l=>{recoveryLevel=l; render();}));
    const [box, list] = group('Wähle die Person.', 'row');
    for (const who of people) list.append(press(who,()=>{recoveryPerson=who;render();},who===recoveryPerson));
    main.append(box);
    if (recoveryPerson) {
      const [box, list] = group('Wähle den Abschnitt.', 'options');
      book.cases[recoveryPerson].sections.forEach((name,i) => list.append(button(name,()=>{
        level = recoveryLevel; enter(recoveryPerson,i+1);
      })));
      main.append(box);
    }
    main.append(button('Zurück',()=>show(returnScreen)));
  }
  function cardContent(key, ids, source) {
    const c = book.cards[key], part = block('stack');
    part.append(heading('h3',c.title),lines(c.lines,ids));
    if (source) part.append(el('p','sources','Quellen: '+c.sources.join(' · ')));
    return part;
  }
  function resources() {
    main.append(heading('h1','Fachkarten'));
    for (const [key, c] of Object.entries(book.cards)) {
      const body = block('stack');
      body.append(lines(c.lines),el('p','sources','Quellen: '+c.sources.join(' · ')));
      const d = disclosure(c.title,body,openedCard===key);
      d.className = 'panel';
      main.append(d);
    }
    main.append(button('Zurück',()=>show(beforeCards),'primary'));
  }
  function sourcePanel(task, state) {
    const panel = el('aside','panel stack'), message = book.cases[person].message;
    if (task.results) {
      const result = block('intro stack');
      result.append(heading('h2','Geprüft'),...task.results.map(t=>el('p','',t)));
      panel.append(result);
    }
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
      panel.append(disclosure('Ganze Nachricht lesen',lines(message),state.full,v=>{state.full=v;}),
        button('Zeile für Zeile lesen',()=>{state.reader=1;render();}));
    }
    if (task.wishes) {
      if (task.wishes.length) panel.append(heading('h3','Lauras Worte'),lines(book.laura,task.wishes));
    }
    panel.append(disclosure('Lauras ganze Nachricht',lines(book.laura),state.laura,v=>{state.laura=v;}));
    if (task.card) {
      const [key,ids] = task.card;
      const card = cardContent(key,ids,false);
      card.classList.add('intro');
      card.append(button('Ganze Fachkarte',()=>{beforeCards='task';openedCard=key;show('resources');}));
      panel.append(card);
    }
    return panel;
  }
  function helpBox(task,state) {
    const wrap = block('stack');
    const toggle = button(state.help?'Hilfe schließen':'Hilfe',()=>{
      state.help=!state.help;
      update();
    });
    const panel = block('note stack'), list = block('help-list'), content = el('p');
    content.setAttribute('aria-live','polite');
    const buttons = book.helps.map((title,i)=>{
      const b = button(String(i+1),()=>{state.hint=i;update();});
      b.setAttribute('aria-label','Hilfe '+(i+1)+' – '+title);
      list.append(b);
      return b;
    });
    const title = el('h3');
    panel.append(list,title,content);
    function update() {
      toggle.setAttribute('aria-expanded',String(state.help));
      toggle.textContent = state.help?'Hilfe schließen':'Hilfe';
      panel.hidden=!state.help;
      buttons.forEach((b,i)=>b.setAttribute('aria-pressed',String(state.hint===i)));
      title.textContent = book.helps[state.hint];
      content.textContent = task.hints[state.hint];
    }
    wrap.append(toggle,panel);
    update();
    return wrap;
  }
  function next() {
    if (section===1) {session().complete=true;enter(person,2);}
    else {session().index++;show('task');}
  }
  function check(task,state,body) {
    const cat = task.kind==='category';
    if (cat) body.append(el('p','small','Ein Feld kann fehlen. Eine Behauptung kann falsch sein.'));
    body.append(el('p','',task.prompt),helpBox(task,state));
    const options = block(cat?'category-grid':'options');
    const feedback = el('div');
    feedback.setAttribute('role','status');
    const onward = button('Weiter',next,'primary');
    const buttons = task.options.map((o,i)=>{
      const b = press(o.label,()=>{state.answer=i;update();},false);
      if (cat) b.append(el('small','',book.categories[o.label]));
      options.append(b);
      return b;
    });
    function update() {
      const o = task.options[state.answer];
      buttons.forEach((b,i)=>b.setAttribute('aria-pressed',String(i===state.answer)));
      feedback.hidden=!o;
      feedback.className = o?.correct?'feedback':'feedback retry';
      feedback.textContent = o ? (o.correct?'Das passt. ':'Prüfe noch einmal. ')+o.feedback : '';
      onward.hidden=!o?.correct;
    }
    body.append(options,feedback,onward);
    update();
  }
  function verdict(task,state,body) {
    const ui = book.verdictUI;
    body.append(el('p','',task.prompt),helpBox(task,state));
    const [rating, marks] = group(ui.rating, 'row');
    const [proof, proofs] = group(level==='Förder'?ui.simpleEvidence:ui.evidence, 'options');
    const [reason, links] = group(ui.reason, 'options');
    const panel = block('stack'), typed = el('textarea');
    const label = el('label','',ui.write); typed.id='mein-grund';label.htmlFor=typed.id;
    typed.value=state.reason; typed.oninput=()=>{state.reason=typed.value;clearNotice();};
    const say = press(ui.spoken,()=>{state.spoken=!state.spoken;sync();},state.spoken);
    panel.append(label,typed,el('p','small',ui.oral),say);
    const notice = el('p','note');notice.setAttribute('role','status');
    const finish = button(ui.done,()=>{
      let missing;
      if (state.mark===null) missing='Wähle dein Urteil.';
      else if (state.evidence===null) missing='Wähle eine Stelle aus der Nachricht.';
      else if (level==='Förder' && !state.reason.trim() && !state.spoken && state.link===null) missing='Wähle, warum die Stelle für Laura wichtig ist.';
      else if (level==='Förder' && !state.reason.trim() && !state.spoken && !task.matchingLinks[state.evidence].includes(state.link)) missing=ui.reconnect;
      else if (level!=='Förder' && !state.reason.trim() && !state.spoken) missing='Schreibe deinen Grund. Oder sage ihn und tippe auf „Ich habe meinen Grund gesagt.“';
      if (missing) {notice.hidden=false;notice.textContent=missing;return;}
      session().complete=true;show('done');
    },'primary');
    function clearNotice(){ notice.hidden=true; }
    function picks(list, labels, field) {
      labels.forEach((s,i)=>list.append(press(s,()=>{state[field]=i;sync();},false)));
    }
    picks(marks,task.options,'mark');picks(proofs,task.anchors,'evidence');picks(links,task.links,'link');
    function sync(){
      for (const [list,index] of [[marks,state.mark],[proofs,state.evidence],[links,state.link]]) {
        Array.from(list.children).forEach((b,i)=>b.setAttribute('aria-pressed',String(i===index)));
      }
      say.setAttribute('aria-pressed',String(state.spoken));clearNotice();
    }
    body.append(rating,proof);
    if (level==='Förder') {
      body.append(reason,disclosure(ui.own,panel,state.own,v=>{state.own=v;}));
    }
    else {
      if (task.counter) body.append(el('p','note',task.counter));
      body.append(panel);
    }
    body.append(notice,finish);sync();
  }
  function taskPage() {
    const s=session(), task=item(), state=draft(), box=block('work'), body=el('article','panel stack');
    main.append(el('p','eyebrow',book.cases[person].sections[section-1]+' · '+level));
    body.append(heading('h1',task.heading,'question'));
    if (task.kind==='judgment') verdict(task,state,body);
    else check(task,state,body);
    if (s.index>1) body.append(button('Vorige Frage',()=>{s.index--;show('task');}));
    box.append(sourcePanel(task,state),body);main.append(box);
  }
  function done() {
    const state=draft(), task=item();
    main.append(heading('h1',person+' · Abschnitt fertig'),el('p','',task.options[state.mark]),
      el('p','',task.anchors[state.evidence]));
    if (level==='Förder' && state.link!==null) main.append(el('p','',task.links[state.link]));
    if (state.reason.trim()) main.append(el('p','',state.reason));
    main.append(el('p','note',book.verdictUI.reflect),
      button('Mein Urteil ansehen',()=>show('task')));
    if (person==='Mutter') main.append(button('Weiter zur Freundin',()=>enter('Freundin',1),'primary'));
    main.append(button('Zur Nachrichtenübersicht',()=>show('overview')));
  }
  function render() {
    main.replaceChildren();
    ({overview,resources,recovery,task:taskPage,done})[screen]();
    const status = ['task','done'].includes(screen)?person+' '+section+' · '+level:'';
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
