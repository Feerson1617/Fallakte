'use strict';

const $ = id => document.getElementById(id);
document.querySelectorAll('[data-icon]').forEach(el => el.append(icon(el.dataset.icon)));

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
const forLevel = value => levelText(value,current.level);
function code() {
  if (current.mode==='review') return current.lastKept;
  if (current.selected==='K' && current.additional) return 'K+'+current.additional;
  return current.combined ? 'K+'+current.selected : current.selected;
}
const orderedMethods = Object.entries(FALLAKTE.methods).sort((a,b)=>a[1][0].localeCompare(b[1][0],'de'));
function show(id) {
  if (screen === 'room') {
    current.scroll=$('history').scrollTop;
    current.workScroll=$('work').scrollTop;
    current.glossaryOpen=$('history').querySelector('.article details')?.open;
  }
  if (screen==='pause') {
    $('pause-facts').hidden=true;
    $('pause-facts').querySelector('ul').replaceChildren();
    $('stop-task').textContent='';
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
  positionHelp();
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
  else if (item.bottom>box.bottom-2) work.scrollTop+=Math.ceil(item.bottom-box.bottom+2);
}
function focusInWork(target) {
  target.focus({preventScroll:true});
  revealInWork(target);
}
function enterStage(index) {
  Object.assign(current,{index,mode:'choose',selected:'',additional:'',combined:false,tentative:false,help:0,asked:[],questionsOpen:false,revised:false});
  if (stage().reviewPrevious && current.lastKept) current.mode='review';
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
  gloss.open=Boolean(current.glossaryOpen);
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
  const last=h.lastElementChild;
  // A long article can already be in view while its end is several screens away.
  const readingLast=last && last.offsetHeight>h.clientHeight &&
    last.getBoundingClientRect().top<=h.getBoundingClientRect().top+12;
  $('latest').hidden=readingLast || h.scrollHeight-h.scrollTop-h.clientHeight<65;
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
function proposalText() {
  const s=stage();
  const proposal=s.options[code()];
  return current.tentative ? proposal+' '+s.tentative : proposal;
}
function sendChoice() {
  const s=stage();
  const selected=code();
  if (!selected || current.mode!=='choose') return;
  changeHistory(()=>{
    say('team',proposalText());
    say('person',forLevel(s.replies[selected]));
  });
  current.mode='reply';
  current.replyQuestion=false;
  current.questionsOpen=false;
  current.help=0;
  drawWork();
  focusTask();
}
function decideProposal(keep) {
  const s=stage();
  const choice=code();
  const declined=s.declined?.[choice.split('+').pop()];
  if (s.tentative) {
    current.finalRefusal=keep ? declined : null;
    current.withdrawn=!keep;
  }
  current.lastKept=keep ? choice : '';
  const clarifyTom=s.id==='T0' && (!keep || choice!=='K');
  changeHistory(()=>{
    if (current.mode==='review') {
      say('team','Wir bleiben bei unserem Vorschlag. '+s.options[choice]);
      say('person',forLevel(s.replies[choice]));
    } else say('team',keep ? 'Wir bleiben bei unserem Vorschlag.' : 'Wir ziehen unseren Vorschlag zurück.');
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
  const revised=current.mode==='reply';
  Object.assign(current,{mode:'choose',revised,selected:'',additional:'',combined:false,tentative:false,help:0,questionsOpen:false});
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
  current.replyQuestion=current.mode==='reply';
  current.questionsOpen=false;
  drawWork();
  // If a partner is rereading, the answer is also available beside the controls.
  focusTask();
}
function stageSupport() {
  const s=stage();
  const support=LERNHILFEN[s.id];
  const choice=code();
  const method=choice.split('+').pop() || support.karte;
  const raw=s.hints[choice || (s.options.DONE?'DONE':method)];
  let pair;
  let source;
  if (method) {
    const name=FALLAKTE.methods[method][0];
    if (Array.isArray(raw)) pair=raw;
    else {
      const question=choice && ['MSA','AHR'].includes(current.level) ? s.hintQuestions[current.level] : raw.find;
      pair=['Karte „'+name+'“, Abschnitt „'+raw.section+'“. '+question,raw.fact];
    }
    const section=raw.section || sections.find(title=>pair[0].includes('„'+title+'“'));
    source={label:'Karte „'+name+'“ lesen',open:()=>{
      auxiliary('resources');
      const card=$('card-'+method);
      card.open=true;
      const heading=[...card.querySelectorAll('dt')].find(dt=>dt.textContent===section);
      heading.tabIndex=-1;
      heading.focus({preventScroll:true});
      heading.scrollIntoView({block:'center'});
    }};
  } else {
    pair=forLevel(raw);
    source={label:'Artikel nachlesen',open:()=>{
      showPane('chat');
      const article=$('history').querySelector('.article');
      const paragraphs=article.querySelectorAll(':scope > p');
      const passage=current.level==='AHR' ? article.querySelector('h4') :
        current.level==='Foerder' ? paragraphs[paragraphs.length-1] : paragraphs[2];
      const history=$('history');
      history.scrollTop+=passage.getBoundingClientRect().top-history.getBoundingClientRect().top-10;
      updateJump();
      article.tabIndex=-1;
      article.focus({preventScroll:true});
    }};
  }
  return {steps:[...pair,support[current.level]],source};
}

function positionHelp() {
  const hint=$('hint-current');
  if (!hint) return;
  const notes=hint.parentElement;
  notes.scrollTop+=hint.getBoundingClientRect().top-notes.getBoundingClientRect().top;
}

function changeHelp(depth) {
  current.help=depth;
  drawWork();
  if (!depth) {focusInWork($('help'));return;}
  const control=document.querySelector('#work .row, #work .methods, #work .primary');
  if (control && !$('send')) revealInWork(control);
  $('hint-current').focus({preventScroll:true});
}

function addTools(area) {
  const actions=el('div','tools');
  const access=current.help ? el('div','help-controls') : actions;
  const {steps,source}=stageSupport();
  renderHelp($('support-panel'),access,steps,current.help,changeHelp,source);
  positionHelp();
  if (stage().questions.length>current.asked.length) {
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
  if (current.questionsOpen) {
    stage().questions.forEach(([question],i)=>{
      if (!current.asked.includes(i)) area.append(button(question,()=>ask(i),'question'));
    });
  }

}
function showQuestionAnswer(area) {
  if (current.asked.length) {
    const index=current.asked[current.asked.length-1];
    const answer=el('div','preview');
    answer.append(el('small','',current.person+' auf eure Rückfrage'),el('p','',stage().questions[index][1]));
    area.append(answer);
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
  $('support-panel').hidden=true;
  $('support-panel').replaceChildren();
  $('step').textContent='Schritt '+(current.index+1)+' von '+stages().length;
  if (current.mode==='finished') {
    taskTitle(area,current.finalRefusal?'Die Empfehlung bleibt offen':'Gespräch abgeschlossen');
    if (current.withdrawn) area.append(el('p','response','Ihr habt den letzten Vorschlag zurückgezogen. Was bleibt zu klären?'));
    else if (current.tentative && !current.finalRefusal) area.append(el('p','response','Euer Rat ist vorläufig. '+current.person+' entscheidet nach der Beratung selbst.'));
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
  if (current.mode==='review') {
    taskTitle(area,'Passt euer bisheriger Rat noch?');
    const names=code().split('+').map(id=>FALLAKTE.methods[id][0]);
    area.append(el('p','preview','Euer letzter Rat war '+names.join(' und ')+'.'),
                el('p','',s.task[current.level]),
                el('p','response',current.person+' zu eurem Rat: „'+forLevel(s.replies[code()])+'“'));
    showQuestionAnswer(area);
    const row=el('div','row');
    const change=button('Vorschlag ändern',reviseProposal,'outline');
    change.id='change-prior';
    row.append(button('Vorschlag beibehalten',()=>decideProposal(true),'outline'),change);
    area.append(row);
    addTools(area);
    return;
  }
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
    if (current.replyQuestion) showQuestionAnswer(area);
    let guide='Besprecht kurz euren Grund. Behaltet den Vorschlag bei oder ändert ihn.';
    if (current.revised) guide='Besprecht euren neuen Rat. Behaltet ihn bei oder zieht ihn zurück.';
    else if (s.id==='L0') guide='Stimmt zuerst in der Klasse ab. Entscheidet danach mit einem Grund: beibehalten oder ändern?';
    area.append(el('p',s.id==='L0' && !current.revised?'decision-guide paper-note':'decision-guide',guide));
    const row=el('div','row');
    row.append(button('Vorschlag beibehalten',()=>decideProposal(true),'outline'));
    if (current.revised) {
      row.append(button('Vorschlag zurückziehen',()=>decideProposal(false),'outline'));
    } else row.append(button('Vorschlag ändern',reviseProposal,'outline'));
    area.append(row);
    addTools(area);
    return;
  }
  taskTitle(area,s.options.DONE ? s.title : current.selected ? 'Prüfe deine Nachricht' :
    s.id==='L0' || s.id==='L6' ? 'Zuerst auf dem Laufzettel' : 'Wähle eine Methode');
  const task=el('p',s.id==='L0' || s.id==='T2'?'paper-note':'',s.task[current.level]);
  if (current.selected) {
    const reminder=el('details','task-reminder');
    reminder.append(el('summary','','Arbeitsauftrag nachlesen'),task);
    area.append(reminder);
  } else area.append(task);
  showQuestionAnswer(area);
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
    if (s.tentative) {
      const label=el('label','combine');
      const check=el('input');
      check.type='checkbox';check.id='tentative';check.checked=current.tentative;
      check.onchange=()=>{
        current.tentative=check.checked;
        drawWork();$('tentative').focus({preventScroll:true});revealInWork($('draft-preview'));
      };
      label.append(check,'Als vorläufigen Rat bis zur Beratung senden');
      area.append(label);
    }
    const preview=el('div','preview');
    preview.append(el('small','','Eure Nachricht'),el('p','',proposalText()));
    const send=button('Nachricht senden',sendChoice,'primary','send');
    preview.id='draft-preview';
    send.id='send'; send.setAttribute('aria-describedby','draft-preview');
    area.append(preview);
    $('answer-panel').append(send);
  }
  addTools(area);
}
function auxiliary(id) {
  if (screen==='home'||screen==='room') returnTo=screen;
  show(id);
  if (id==='pause') {
    const laura=sessions.get(sessionKey('Laura',level));
    const facts=$('pause-facts');
    facts.open=false;
    facts.hidden=!laura || laura.mode==='finished';
    const known=facts.hidden ? [] : FALLAKTE.cases.Laura.slice(0,laura.index+1);
    facts.querySelector('ul').replaceChildren(...known.map(s=>el('li','',s.pauseFact)));
    $('early-stop').hidden=laura?.mode==='finished';
    $('stop-task').textContent=$('early-stop').hidden ? '' : FALLAKTE.meta.stopTask[level];
    $('review-laura').hidden=!laura;
    let outcome='';
    if (laura?.finalRefusal) outcome='Laura hat eurem letzten Vorschlag nicht zugestimmt. Sie sagt: „'+laura.finalRefusal+'“';
    else if (laura?.withdrawn) outcome='Ihr habt euren letzten Vorschlag zurückgezogen.';
    else if (laura?.mode==='finished' && laura.tentative) outcome='Euer Rat ist vorläufig. Laura entscheidet nach der Beratung selbst.';
    $('pause-conflict').hidden=!outcome;
    $('pause-conflict').textContent=outcome;
  }
  $(id).querySelector('h1').focus({preventScroll:true});
}
function resume() {
  if (returnTo==='room' && current) openCase(current.person,current.level);
  else home();
}
const sections=['Wirkung','Schwangerschaftsschutz im Alltag','Anwendung','Mögliche Nachteile','Blutung und Schmerzen','Infektionsschutz'];
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
