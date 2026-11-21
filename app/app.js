'use strict';

const $ = id => document.getElementById(id);
const paths = {
  chat:'M4 4h12a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H9l-5 4v-4H3a1 1 0 0 1-1-1V6a2 2 0 0 1 2-2z M20 9h1v11l-4-3h-3',
  folder:'M3 7V5a1 1 0 0 1 1-1h6l2 3h8a1 1 0 0 1 1 1v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z M3 9h18',
  book:'M12 6C8 4 5 4 2 5v14c3-1 6-1 10 1 4-2 7-2 10-1V5c-3-1-6-1-10 1z M12 6v14',
  group:'M15 20v-2a5 5 0 0 0-5-5H8a5 5 0 0 0-5 5v2 M9 10a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z M16 4a3 3 0 0 1 0 6 M18 14a5 5 0 0 1 3 5',
  layers:'m12 3 9 5-9 5-9-5 9-5z M3 12l9 5 9-5 M3 16l9 5 9-5',
  pencil:'m4 16 11-11 4 4L8 20l-5 1 1-5z M13 7l4 4 M16 4l1-1a2 2 0 0 1 3 0l1 1a2 2 0 0 1 0 3l-1 1',
  next:'M4 12h15m-6-6 6 6-6 6', back:'M20 12H5m6 6-6-6 6-6', down:'M12 4v16m-6-6 6 6 6-6',
  help:'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z M9.5 9a2.5 2.5 0 1 1 4 2c-1 .7-1.5 1.1-1.5 2.5 M12 17h.01',
  send:'m3 3 19 9-19 9 3-9-3-9z M6 12h13'
};
function icon(name) {
  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns,'svg');
  svg.setAttribute('viewBox','0 0 24 24');
  svg.setAttribute('aria-hidden','true');
  const path = document.createElementNS(ns,'path');
  path.setAttribute('d',paths[name]);
  svg.append(path);
  return svg;
}
document.querySelectorAll('[data-icon]').forEach(el => el.append(icon(el.dataset.icon)));
function el(tag, cls, text) {
  const element = document.createElement(tag);
  if (cls) element.className = cls;
  if (text !== undefined) element.textContent = text;
  return element;
}
function button(label, action, cls, symbol) {
  const b = el('button', cls, label);
  b.type = 'button';
  if (symbol) b.append(icon(symbol));
  b.onclick = action;
  return b;
}

const cases = {
  Laura:['Gemeinsamer Hauptfall','Laura fragt nach Schutz vor Infektionen. Was rätst du ihr?'],
  Celina:['Weiterer Fall','Celina möchte ohne zusätzliche Hormone verhüten.'],
  Tom:['Vertiefung','Tom möchte selbst verhüten. Welche Wege gibt es?']
};
const sessions = new Map();
let level = 'ESA';
let current = null;
let screen = 'home';
let returnTo = 'home';
const sessionKey = (person, tier) => person + '-' + tier;
const stages = () => FALLAKTE.cases[current.person];
const stage = () => stages()[current.index];
const forLevel = value => typeof value === 'string' || Array.isArray(value) ? value : value[current.level];
function code() {
  if (current.selected==='K' && current.additional) return 'K+'+current.additional;
  return current.combined ? 'K+'+current.selected : current.selected;
}
const orderedMethods = Object.entries(FALLAKTE.methods).sort((a,b)=>a[1][0].localeCompare(b[1][0],'de'));
function show(id) {
  if (screen === 'room') {
    current.scroll=$('history').scrollTop;
    current.workScroll=$('work').scrollTop;
  }
  screen = id;
  document.documentElement.classList.toggle('consulting',id==='room');
  $('room-identity').hidden=id!=='room';
  $('home-label').textContent=id==='room'?'Übersicht':'Fallakten';
  $('home-nav').setAttribute('aria-label','Fallübersicht');
  for (const section of ['home','room','resources','pause']) $(section).hidden = section !== id;
  const active = ({home:'home-nav',room:'home-nav',resources:'cards-nav',pause:'pause-nav'})[id];
  for (const b of document.querySelectorAll('nav button')) {
    if (b.id === active) b.setAttribute('aria-current','page');
    else b.removeAttribute('aria-current');
  }
  window.scrollTo(0,0);
}
function home() {
  show('home');
  const levels = $('levels');
  levels.replaceChildren();
  for (const [key,label] of Object.entries(FALLAKTE.meta.levels)) {
    const b = button(label, () => { level=key; home(); $(b.id).focus({preventScroll:true}); });
    b.id='level-'+key;
    b.setAttribute('aria-pressed',key === level);
    levels.append(b);
  }
  const list = $('case-list');
  list.replaceChildren();
  for (const [person,[role,summary]] of Object.entries(cases)) {
    const card = el('article','case-card '+person.toLowerCase());
    const body = el('div','case-info');
    const resume = sessions.has(sessionKey(person,level));
    const start = button(person+(resume?' öffnen':' starten'), () => openCase(person,level),person==='Laura'?'primary':'outline','next');
    start.dataset.person=person;
    body.append(el('span','role',role),el('h3','',person),el('p','',summary),start);
    card.append(el('div','cover'),body);
    list.append(card);
  }
}
function openCase(person,tier) {
  show('room');
  const key=sessionKey(person,tier);
  current=sessions.get(key);
  if (!current) {
    current={person,level:tier,index:0,log:[],scroll:0,workScroll:0,pane:'chat'};
    sessions.set(key,current);
    enterStage(0);
  }
  $('avatar').className='avatar '+person.toLowerCase();
  $('room-level').textContent=FALLAKTE.meta.levels[tier];
  $('chat-name').textContent=person;
  showPane(current.pane);
  drawHistory();
  $('history').scrollTop=current.scroll;
  updateJump();
  drawWork();
  $('work').scrollTop=current.workScroll;
  $('chat-name').focus({preventScroll:true});
}
function showPane(pane) {
  current.pane=pane;
  $('room').dataset.pane=pane;
  $('read-chat').setAttribute('aria-pressed',pane==='chat');
  $('write-answer').setAttribute('aria-pressed',pane==='answer');
}
function revealInWork(target) {
  const work=$('work');
  const box=work.getBoundingClientRect();
  const item=target.getBoundingClientRect();
  if (item.top<box.top || item.height>box.height) work.scrollTop+=item.top-box.top;
  else if (item.bottom>box.bottom) work.scrollTop+=item.bottom-box.bottom;
}
function focusInWork(target) {
  target.focus({preventScroll:true});
  revealInWork(target);
}
function enterStage(index) {
  Object.assign(current,{index,mode:'choose',selected:'',additional:'',combined:false,help:0,asked:[],questionsOpen:false,revised:false});
  current.log.push({type:'step',title:stage().title});
  current.log.push({type:'person',lines:stage().message[current.level]});
  if (stage().type==='article') current.log.push({type:'article'});
}
function appendArticle() {
  const data=FALLAKTE.tom_articles[current.level];
  const a=el('article','article');
  a.append(el('span','eyebrow','Geteilter Artikel'),el('h3','',data.title));
  for (const p of data.paragraphs) a.append(el('p','',p));
  if (current.level==='AHR') {
    for (const study of FALLAKTE.research) {
      a.append(el('h4','',study.label),el('p','',study.body),el('small','',study.source));
    }
  }
  const gloss=el('details');
  gloss.append(el('summary','','Wörter erklären'));
  for (const [word,meaning] of Object.entries(data.glossary)) gloss.append(el('p','',word+' – '+meaning));
  a.append(gloss);
  return a;
}
function entryNode(entry) {
  if (entry.type==='step') return el('div','chat-step',entry.title);
  if (entry.type==='article') return appendArticle();
  const bubble=el('div','bubble '+entry.type);
  bubble.append(el('strong','speaker',entry.type==='team'?'Beratungsteam':current.person));
  for (const line of entry.lines) bubble.append(el('p','',line));
  return bubble;
}
function drawHistory() {
  $('history').replaceChildren(...current.log.map(entryNode));
}
function updateJump() {
  const h=$('history');
  $('latest').hidden=h.scrollHeight-h.scrollTop-h.clientHeight<65;
}
function toEntry(index) {
  const h=$('history');
  const target=h.children[index];
  if (target) h.scrollTop+=target.getBoundingClientRect().top-h.getBoundingClientRect().top-10;
  updateJump();
}
function changeHistory(change) {
  const h=$('history');
  const readingOlder=h.scrollHeight-h.scrollTop-h.clientHeight>65;
  const first=current.log.length;
  change();
  h.append(...current.log.slice(first).map(entryNode));
  if (!readingOlder) toEntry(first);
  updateJump();
}
function say(type,text) { current.log.push({type,lines:[text]}); }
function nextStage() {
  if (current.index===stages().length-1) {
    current.mode='finished';
    drawWork();
    focusTask();
    return;
  }
  changeHistory(()=>enterStage(current.index+1));
  showPane('chat');
  drawWork();
  $('work').scrollTop=0;
  $('chat-name').focus({preventScroll:true});
}
function focusTask() {
  $('work').scrollTop=0;
  $('task-title')?.focus({preventScroll:true});
}
function sendChoice() {
  const s=stage();
  const selected=code();
  if (!selected || current.mode!=='choose') return;
  changeHistory(()=>{
    say('team',s.options[selected]);
    say('person',forLevel(s.replies[selected]));
  });
  current.mode='reply';
  current.help=0;
  drawWork();
  focusTask();
}
function decideProposal(keep) {
  const s=stage();
  const choice=code();
  const declined=s.declined?.[choice.split('+').pop()];
  if (current.index===stages().length-1) current.finalRefusal=keep ? declined : null;
  const clarifyTom=s.id==='T0' && (!keep || choice!=='K');
  changeHistory(()=>{
    say('team',keep ? 'Wir bleiben bei unserem Vorschlag.' : 'Wir ziehen unseren Vorschlag zurück.');
    if (keep && declined) say('person',declined);
    if (clarifyTom) say('person',s.selfAnswer);
  });
  if (clarifyTom) {
    current.mode='tomSelf';
    current.help=0;
    drawWork();
    focusTask();
  } else nextStage();
}
function reviseProposal() {
  Object.assign(current,{mode:'choose',revised:true,selected:'',additional:'',combined:false,help:0});
  drawWork();
  focusTask();
}
function completeDiscussion() {
  changeHistory(()=>{
    say('team',stage().options.DONE);
    say('person',forLevel(stage().replies.DONE));
  });
  nextStage();
}
function ask(index) {
  if (current.asked.includes(index)) return;
  const [question,answer]=stage().questions[index];
  changeHistory(()=>{say('team',question);say('person',answer);});
  current.asked.push(index);
  current.questionsOpen=false;
  drawWork();
  // If a partner is rereading, the answer is also available beside the controls.
  focusTask();
}
function addTools(area) {
  const actions=el('div','tools');
  if (current.help<2) {
    const help=button(current.help?'Zweite Hilfe':'Hilfe',()=>{
      current.help++;
      drawWork();
      focusInWork($('hint-current'));
    },'text-button','help');
    help.id='help';
    actions.append(help);
  }
  if (current.mode==='choose' && stage().questions.length>current.asked.length) {
    const q=button(current.questionsOpen?'Fragen schließen':'Rückfrage stellen',()=>{
      current.questionsOpen=!current.questionsOpen;
      drawWork();
      focusInWork(document.querySelector('.question') || $('ask'));
    },'text-button','chat');
    q.id='ask';
    q.setAttribute('aria-expanded',current.questionsOpen);
    actions.append(q);
  }
  area.append(actions);
  if (current.questionsOpen && current.mode==='choose') {
    stage().questions.forEach(([question],i)=>{
      if (!current.asked.includes(i)) area.append(button(question,()=>ask(i),'question'));
    });
  }
  if (current.help) {
    const hints=stage().hints[code() || 'DONE'];
    const pair=hints ? forLevel(hints) : stage().helpBefore;
    for (let i=0;i<current.help;i++) {
      const hint=el('div','hint');
      hint.append(el('small','','Hilfe '+(i+1)),el('p','',pair[i]));
      if (i===current.help-1) {hint.id='hint-current';hint.tabIndex=-1;}
      area.append(hint);
    }
    const method=code().split('+').pop() || (stage().id==='L2' ? 'P' : '');
    if (method) {
      const card=FALLAKTE.methods[method][0];
      area.append(button('Karte „'+card+'“ lesen',()=>{
        auxiliary('resources');
        const target=$('card-'+method);
        target.open=true;
        target.querySelector('summary').focus();
      },'text-button','book'));
    } else if (['T1','T2'].includes(stage().id)) {
      area.append(button('Artikel nachlesen',()=>{
        showPane('chat');
        const article=$('history').querySelector('.article');
        toEntry([...$('history').children].indexOf(article));
        article.tabIndex=-1;
        article.focus({preventScroll:true});
      },'text-button','book'));
    } else {
      area.append(button('Chatstelle lesen',()=>{
        showPane('chat');
        toEntry(current.log.findIndex(entry=>entry.type==='step' && entry.title===stage().title));
        $('history').focus({preventScroll:true});
      },'text-button','chat'));
    }
    const nextAction=current.mode==='reply' ? 'Besprecht euren Grund. Entscheidet euch dann.' :
      stage().options.DONE ? (stage().id==='T2' ? 'Schreibe jetzt deine Idee bei Tom auf.' : 'Besprecht die Frage zu zweit.') :
      current.selected ? 'Passt dein Vorschlag? Wähle neu oder sende ihn.' : 'Wähle jetzt eine Methode.';
    area.append(el('p','pick',nextAction));
  }
}
function taskTitle(area,title) {
  const h=el('h2','',title);
  h.id='task-title';h.tabIndex=-1;
  area.append(h);
}
function drawWork() {
  const area=$('work');
  $('send')?.remove();
  area.replaceChildren();
  $('step').textContent='Schritt '+(current.index+1)+' von '+stages().length;
  if (current.mode==='finished') {
    taskTitle(area,current.finalRefusal?'Die Empfehlung bleibt offen':'Gespräch abgeschlossen');
    if (current.finalRefusal) {
      area.append(el('p','unresolved',current.person+' hat eurem letzten Vorschlag nicht zugestimmt.'),
                  el('p','response',current.finalRefusal));
    }
    if (current.person==='Laura') {
      area.append(el('p','paper-note','Schreibe bei „Mein letzter Rat“ deinen eigenen Vorschlag und deinen wichtigsten Grund auf.'));
    } else if (current.person==='Celina') {
      area.append(el('p','paper-note','Fülle auf dem Laufzettel das Feld „Celina“ aus. Nenne deinen Rat und einen Grund.'));
    }
    if (current.person==='Laura') {
      area.append(el('p','','Zeit für die zweite Abstimmung. Vergleicht eure Gründe in der Klasse.'));
      area.append(button('Zur gemeinsamen Sicherung',()=>auxiliary('pause'),'primary','group'));
      area.append(el('p','extra','Noch Zeit bis zum Stopp? Öffne einen weiteren Fall.'));
      const row=el('div','row');
      for (const n of ['Celina','Tom']) row.append(button(n+' starten',()=>openCase(n,current.level),'outline','next'));
      area.append(row);
    } else area.append(button('Zur gemeinsamen Sicherung',()=>auxiliary('pause'),'primary','group'),button('Zur Fallübersicht',home,'text-button'));
    return;
  }
  const s=stage();
  if (current.mode==='tomSelf') {
    taskTitle(area,'Ein Vorschlag für Tom selbst');
    area.append(el('p','response',s.selfAnswer),el('p','preview',s.selfAdvice));
    area.append(button('Nachricht senden',()=>{
      changeHistory(()=>say('team',s.selfAdvice));
      nextStage();
    },'primary','send'));
    return;
  }
  if (current.mode==='reply') {
    taskTitle(area,current.person+' antwortet');
    area.append(el('p','response',forLevel(s.replies[code()])));
    const prompt=current.revised ? 'Bleibt ihr dabei oder zieht ihr den Vorschlag zurück?' : 'Bleibt ihr bei eurem Vorschlag oder ändert ihr ihn?';
    area.append(el('p','',prompt+' Sagt euch kurz, warum.'));
    if (s.id==='L0') area.append(el('p','paper-note','Stimmt in der Klasse über euren ersten Rat ab.'));
    const row=el('div','row');
    row.append(button('Vorschlag beibehalten',()=>decideProposal(true),'outline'));
    if (current.revised) {
      row.append(button('Vorschlag zurückziehen',()=>decideProposal(false),'outline'));
    } else row.append(button('Vorschlag ändern',reviseProposal,'outline'));
    area.append(row);
    addTools(area);
    return;
  }
  taskTitle(area,s.options.DONE?s.title:'Dein Vorschlag');
  area.append(el('p',s.id==='L0' || s.id==='T2'?'paper-note':'',s.task[current.level]));
  if (current.asked.length) {
    const index=current.asked[current.asked.length-1];
    const answer=el('div','preview');
    answer.append(el('small','',current.person+' auf eure Rückfrage'),el('p','',s.questions[index][1]));
    area.append(answer);
  }
  if (s.options.DONE) {
    area.append(button(s.id==='T2'?'Fall abschließen':s.id==='T1'?'Weiter nach dem Lesen':'Weiter nach dem Gespräch',completeDiscussion,'primary','next'));
    addTools(area);
    return;
  }
  const methods=el('div','methods');
  methods.setAttribute('role','group');methods.setAttribute('aria-label','Methode auswählen');
  for (const [id,[name]] of orderedMethods) {
    const b=button(name,()=>{
      Object.assign(current,{selected:id,additional:'',combined:false,help:0,questionsOpen:false});
      drawWork();
      $('method-'+id).focus({preventScroll:true});
      revealInWork($('draft-preview'));
    },'method');
    b.id='method-'+id;
    b.setAttribute('aria-pressed',current.selected===id);
    methods.append(b);
  }
  area.append(methods);
  if (current.selected==='K') {
    const label=el('label','extra-method','Kondom kombinieren');
    const menu=el('select');
    menu.id='additional';
    menu.add(new Option('Kondom allein',''));
    for (const [id,[name]] of orderedMethods) {
      if (id!=='K') menu.add(new Option('Mit '+name,id));
    }
    menu.value=current.additional;
    menu.onchange=()=>{
      current.additional=menu.value; current.help=0;
      drawWork(); $('additional').focus({preventScroll:true}); revealInWork($('draft-preview'));
    };
    label.append(menu);area.append(label);
  } else if (current.selected) {
    const label=el('label','combine');
    const check=el('input');
    check.type='checkbox';check.id='combine';check.checked=current.combined;
    check.onchange=()=>{
      current.combined=check.checked;current.help=0;
      drawWork();$('combine').focus({preventScroll:true}); revealInWork($('draft-preview'));
    };
    label.append(check,'Zusätzlich ein Kondom vorschlagen');
    area.append(label);
  }
  if (current.selected) {
    const preview=el('div','preview');
    preview.append(el('small','','Eure Nachricht'),el('p','',s.options[code()]));
    const send=button('Nachricht senden',sendChoice,'primary','send');
    preview.id='draft-preview';
    send.id='send'; send.setAttribute('aria-describedby','draft-preview');
    area.append(preview);
    $('answer-panel').append(send);
  } else area.append(el('p','pick','Wähle eine Methode aus.'));
  addTools(area);
}
function auxiliary(id) {
  if (screen==='home'||screen==='room') returnTo=screen;
  show(id);
  if (id==='pause') {
    const laura=sessions.get(sessionKey('Laura',level));
    const facts=$('pause-facts');
    facts.open=false;
    facts.hidden=laura?.mode==='finished';
    const remaining=facts.hidden ? [] : FALLAKTE.cases.Laura.slice(laura?.index ?? 0);
    facts.querySelector('ul').replaceChildren(...remaining.map(s=>el('li','',s.pauseFact)));
    $('review-laura').hidden=!laura;
    $('pause-conflict').hidden=!laura?.finalRefusal;
    $('pause-conflict').textContent=laura?.finalRefusal ? 'Laura hat eurem letzten Vorschlag nicht zugestimmt. Sie sagt: „'+laura.finalRefusal+'“' : '';
  }
  $(id).querySelector('h1').focus({preventScroll:true});
}
function resume() {
  if (returnTo==='room' && current) openCase(current.person,current.level);
  else home();
}
const sections=['Wirkung','Anwendung','Mögliche Nachteile','Blutung und Schmerzen','Infektionsschutz'];
for (const [id,[name,...facts]] of Object.entries(FALLAKTE.methods)) {
  const d=el('details');
  d.id='card-'+id;
  const dl=el('dl');
  facts.forEach((fact,i)=>dl.append(el('dt','',sections[i]),el('dd','',fact)));
  d.append(el('summary','',name),dl);
  $('method-cards').append(d);
}
$('history').onscroll=updateJump;
$('latest').onclick=()=>{
  // The newly shared article should start at its heading.
  const i=current.log.length-1;
  toEntry(i);
  $('history').focus({preventScroll:true});
};
$('read-chat').onclick=()=>showPane('chat');
$('write-answer').onclick=()=>showPane('answer');
$('home-nav').onclick=home;
$('brand').onclick=e=>{e.preventDefault();home();};
$('cards-nav').onclick=()=>auxiliary('resources');
$('pause-nav').onclick=()=>auxiliary('pause');
$('review-laura').onclick=()=>openCase('Laura',level);
document.querySelectorAll('.return').forEach(b=>b.onclick=resume);
home();

// SCORM 1.2 session lifecycle only. Look in the launch frame and popup opener.
function findAPI(start) {
  let frame=start;
  for (let i=0;frame && i<32;i++) {
    try {
      if (typeof frame.API?.LMSInitialize==='function') return frame.API;
      if (frame===frame.parent) break;
      frame=frame.parent;
    } catch {break;}
  }
  return null;
}
let api=null;
function initialize() {
  if (api) return;
  try {
    const candidate=findAPI(window)||findAPI(window.opener);
    if (candidate && String(candidate.LMSInitialize(''))==='true') api=candidate;
  } catch { /* The offline chat also works outside an LMS. */ }
}
initialize();
window.addEventListener('pageshow',initialize);
window.addEventListener('pagehide',()=>{
  try {api?.LMSFinish('');} catch { /* The launch frame may already be closed. */ } finally {api=null;}
});
