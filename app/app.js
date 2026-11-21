'use strict';

const $ = id => document.getElementById(id);
document.querySelectorAll('[data-icon]').forEach(el => el.append(icon(el.dataset.icon)));

const cases = {
  Laura:['Hauptfall','Laura fragt nach Schutz vor Infektionen. Was rätst du ihr?'],
  Celina:['Zusatzfall','Celina möchte ohne zusätzliche Hormone verhüten.'],
  Tom:['Zusatzfall','Tom möchte selbst verhüten. Welche Wege gibt es?']
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
const shortLaura = () => current.person==='Laura' && ['Foerder','ESA'].includes(current.level);
function code() {
  if (current.mode==='review') return current.lastKept;
  const second=current.selected==='K' ? current.additional : current.combined && current.selected;
  const choice=second ? 'K+'+second : current.selected;
  return Object.hasOwn(stage().options,choice) ? choice : '';
}
const orderedMethods = Object.entries(FALLAKTE.methods).sort((a,b)=>a[1][0].localeCompare(b[1][0],'de'));
function show(id) {
  if (screen === 'room') {
    current.scroll=$('history').scrollTop;
    current.workScroll=$('work').scrollTop;
    current.glossaryOpen=$('history').querySelector('.article details')?.open;
  }
  screen = id;
  document.documentElement.classList.toggle('consulting',id==='room');
  $('room-identity').hidden=id!=='room';
  $('home-label').textContent=id==='room'?'Übersicht':'Fallakten';
  $('home-nav').setAttribute('aria-label','Fallübersicht');
  for (const section of ['home','recovery','room','resources']) $(section).hidden = section !== id;
  const active = id==='resources' ? 'cards-nav' : 'home-nav';
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
  const extrasAvailable = sessions.get(sessionKey('Laura',level))?.mode==='finished';
  $('case-order').textContent=extrasAvailable ? 'Weitere Fälle sind freigeschaltet.' : 'Beginne mit Laura. Danach kannst du Celina oder Tom wählen.';
  if (!extrasAvailable && Object.keys(cases).some(name=>name!=='Laura' && sessions.has(sessionKey(name,level))))
    $('case-order').textContent='Begonnene Fälle kannst du wieder öffnen.';
  const list = $('case-list');
  list.replaceChildren();
  for (const [person,[role,summary]] of Object.entries(cases)) {
    const card = el('article','case-card '+person.toLowerCase());
    const body = el('div','case-info');
    const resume = sessions.has(sessionKey(person,level));
    const start = button(person+(resume?' öffnen':' starten'), () => openCase(person,level),person==='Laura'?'primary':'outline','next');
    start.disabled=person!=='Laura' && !extrasAvailable && !resume;
    start.dataset.person=person;
    body.append(el('span','role',role),el('h3','',person),el('p','',summary),start);
    card.append(el('div','cover'),body);
    list.append(card);
  }
}
function openCase(person,tier,startIndex) {
  show('room');
  const key=sessionKey(person,tier);
  current=sessions.get(key);
  let recapIndex;
  if (!current || startIndex!==undefined) {
    current={person,level:tier,log:[],scroll:0,workScroll:0,pane:'chat',lastKept:''};
    sessions.set(key,current);
    if (startIndex>0) {
      const earlier=stages().slice(0,startIndex);
      // Keep an already introduced source available to later tasks and their help buttons.
      if (earlier.some(s=>s.type==='article')) current.log.push({type:'article'});
      recapIndex=current.log.length;
      current.log.push({type:'recap',lines:earlier.map(s=>forLevel(s.recap))});
    }
    enterStage(startIndex ?? 0);
  }
  $('avatar').className='avatar '+person.toLowerCase();
  $('room-level').textContent=FALLAKTE.meta.levels[tier];
  showPane(current.pane);
  drawHistory();
  $('history').scrollTop=current.scroll;
  if (recapIndex!==undefined) toEntry(recapIndex);
  updateJump();
  drawWork();
  $('work').scrollTop=current.workScroll;
  positionHelp();
  $('step').focus({preventScroll:true});
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
  if (current.lastKept && stage().reviewPrevious && Object.hasOwn(stage().options,current.lastKept)) current.mode='review';
  current.log.push({type:'step',title:stage().title});
  current.log.push({type:'person',lines:forLevel(stage().message)});
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
  if (entry.type==='recap') {
    const box=el('section','recap');
    const list=el('ul');
    for (const fact of entry.lines) list.append(el('li','',fact));
    box.append(el('h2','','Bisher im Fall'),list);
    const articleIndex=current.log.findIndex(item=>item.type==='article');
    if (articleIndex>=0 && articleIndex<current.log.indexOf(entry)) {
      box.append(button('Artikel noch einmal lesen',()=>{
        toEntry(articleIndex);
        const article=$('history').children[articleIndex];
        article.tabIndex=-1;
        article.focus({preventScroll:true});
      },'text-button','book'));
    }
    return box;
  }
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
  const first=current.log.length;
  changeHistory(()=>enterStage(current.index+1));
  showPane('chat');
  if (current.mode==='review' && current.person==='Laura') toEntry(first);
  drawWork();
  $('work').scrollTop=0;
  $('step').focus({preventScroll:true});
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
function feedbackIssue(s,choice) {
  const last=choice.split('+').pop();
  if (s.declined?.[last]) return current.person==='Laura' ? 'Laura hat die Pille abgelehnt. Das gilt auch für eine Kombination.' : 'Celina möchte keine zusätzlichen Hormone. Diese Methode enthält Hormone.';
  if (['L0','L4','C3'].includes(s.id) && !choice.includes('K'))
    return 'Dieser Vorschlag allein schützt nicht vor Infektionen beim Sex.';
  if (s.id==='T0' && choice!=='K') return choice.includes('+') ?
    'Nur das Kondom in eurem Vorschlag kann Tom selbst benutzen.' : 'Diese Methode kann Tom nicht am eigenen Körper anwenden.';
  return '';
}

function lastHelp(s,method) {
  // The final hint may prepare a draft. Sending or deciding stays with the team.
  if (s.options.DONE || current.mode==='tomSelf') {
    const next=$('work').querySelector('.primary');
    const paper=s.id==='T2' ? s.task[current.level]+' ' :
      s.id==='T1' ? 'Überlege dir einen Grund. ' : '';
    return {text:paper+'Tippe auf „'+next.textContent+'“.',label:'Zur Schaltfläche',run:()=>focusInWork(next)};
  }
  if (current.mode==='reply' || current.mode==='review') {
    const options=$('work').querySelector('.row').querySelectorAll('button');
    if (current.revised || code()===method) {
      const issue=current.revised && feedbackIssue(s,code());
      const target=issue ? options[1] : options[0];
      const text=issue ? 'Passt dein neuer Rat nicht? Dann tippe auf „Vorschlag zurückziehen“.' :
        'Passt dein Rat? Dann tippe auf „Vorschlag beibehalten“.';
      return {text,label:'Zur Schaltfläche',run:()=>focusInWork(target)};
    }
  }
  const name=FALLAKTE.methods[method][0];
  const label=name+' als Entwurf öffnen';
  return {text:'Tippe auf „'+label+'“. Prüfe den Entwurf. Passt er, tippe auf „Nachricht senden“.',label,run:()=>{
      if (current.mode==='reply' || current.mode==='review') reviseProposal();
      selectMethod(method);
    }};
}

function stageSupport() {
  const s=stage();
  const support=LERNHILFEN[s.id];
  let choice=code();
  if (current.mode==='tomSelf' || (current.mode==='reply' && !current.revised && ['L0','C3','T0'].includes(s.id) &&
      !choice.includes('K') && !s.declined?.[choice])) choice='K';
  const method=choice.split('+').pop() || support.beispielMethode;
  const raw=s.hints[choice || (s.options.DONE?'DONE':method)];
  let pair;
  let source;
  if (method) {
    const name=FALLAKTE.methods[method][0];
    if (Array.isArray(raw)) pair=raw;
    else {
      const cardQuestion=(shortLaura() && support.kartenfrage?.[method]) || raw.find;
      const question=choice && ['MSA','AHR'].includes(current.level) ? s.hintQuestions[current.level] : cardQuestion;
      pair=['Karte „'+name+'“, Abschnitt „'+raw.section+'“. '+question,raw.fact];
    }
    const section=raw.section || sections.find(title=>pair[0].includes('„'+title+'“'));
    source={label:'Karte „'+name+'“ lesen',open:()=>{
      openCards();
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
  let example=forLevel(support.beispiel);
  const comparison=support.vergleich?.[choice] || support.vergleich?.[method];
  if (current.mode==='reply' && current.revised) {
    // After a revision the only remaining actions are keeping or withdrawing the actual proposal.
    const issue=feedbackIssue(s,choice);
    if (issue) example='Ich ziehe meinen Rat zurück. '+pair[1];
    else if (choice!==support.beispielMethode) {
      const names=choice.split('+').map(key=>FALLAKTE.methods[key][0]).join(' und ');
      example='Mein Rat mit '+names+' bleibt vorläufig. '+pair[1];
    }
  } else if (comparison) {
    example=comparison+' '+support.vergleichsrat;
  }
  const action=lastHelp(s,support.beispielMethode);
  return {steps:[...pair,support[current.level],example,action.text],source,action};
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
  if (!depth) {$('help').focus({preventScroll:true});return;}
  const control=document.querySelector('#work .row, #work .methods, #work .primary');
  if (control && !$('send')) revealInWork(control);
  $('hint-current').focus({preventScroll:true});
}

function addTools(area) {
  const actions=el('div','tools');
  const {steps,source,action}=stageSupport();
  renderHelp($('support-panel'),$('help-dock'),steps,current.help,changeHelp,source,action);
  positionHelp();
  if (current.mode!=='tomSelf' && stage().questions.length>current.asked.length) {
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
function selectMethod(id) {
  Object.assign(current,{selected:id,additional:'',combined:false,help:0,questionsOpen:false});
  drawWork();
  $('method-'+id).focus({preventScroll:true});
  revealInWork($('draft-preview'));
}
function drawWork() {
  const area=$('work');
  $('send')?.remove();
  area.replaceChildren();
  $('help-dock').replaceChildren();
  $('help-dock').hidden=true;
  $('chat-help').hidden=current.mode==='finished';
  $('support-panel').hidden=true;
  $('support-panel').replaceChildren();
  $('step').textContent=current.person+' '+(current.index+1)+' von '+stages().length;
  const cue=$('card-cue');
  cue.hidden=current.mode==='finished' || !!stage().options.DONE;
  cue.textContent=['Foerder','ESA'].includes(current.level)
    ? 'Prüfe deinen Rat mit deiner Infokarte auf Papier.' : 'Belege deinen Rat mit deiner Infokarte auf Papier.';
  if (current.mode==='finished') {
    taskTitle(area,'Gespräch abgeschlossen');
    if (current.withdrawn) area.append(el('p','response','Ihr habt den letzten Vorschlag zurückgezogen. Was bleibt zu klären?'));
    else if (current.tentative && !current.finalRefusal) area.append(el('p','response','Euer Rat ist vorläufig. '+current.person+' entscheidet nach der Beratung selbst.'));
    if (current.finalRefusal) {
      area.append(el('p','unresolved',current.person+' hat eurem letzten Vorschlag nicht zugestimmt.'),
                  el('p','response',current.finalRefusal));
    }
    if (current.person==='Laura' && !shortLaura()) {
      area.append(el('p','paper-note','Schreibe bei „Mein letzter Rat“ deinen eigenen Vorschlag und deinen wichtigsten Grund auf.'));
    } else if (current.person==='Celina') {
      area.append(el('p','paper-note','Fülle auf dem Laufzettel das Feld „Celina“ aus. Nenne deinen Rat und einen Grund.'));
    }
    area.append(button('Zur Fallübersicht',home,'outline','folder'));
    return;
  }
  const s=stage();
  if (current.mode==='review') {
    taskTitle(area,'Passt euer bisheriger Rat noch?');
    const names=code().split('+').map(id=>FALLAKTE.methods[id][0]);
    area.append(el('p','preview','Euer letzter Rat war '+names.join(' und ')+'.'),
                el('p','',s.task[current.level]),
                el('p','response',current.person+' zu eurem Rat: „'+forLevel(s.replies[code()])+'“'));
    if (shortLaura() && s.declined?.[code().split('+').pop()]) {
      area.append(el('p','decision-guide','Tippe auf „Vorschlag ändern“, um einen Rat ohne Pille zu geben.'));
    } else if (shortLaura() && feedbackIssue(s,code())) {
      area.append(el('p','decision-guide','Prüfe den Schutz vor Infektionen. Mit „Vorschlag ändern“ kannst du anders wählen.'));
    }
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
    addTools(area);
    return;
  }
  if (current.mode==='reply') {
    taskTitle(area,current.person+' antwortet');
    area.append(el('p','response',forLevel(s.replies[code()])));
    if (current.replyQuestion) showQuestionAnswer(area);
    let guide='Prüfe deinen Grund. Behalte den Vorschlag bei oder ändere ihn.';
    if (current.revised) guide='Prüfe deinen neuen Rat. Behalte ihn bei oder ziehe ihn zurück.';
    const issue=feedbackIssue(s,code());
    if (issue) {
      const next=current.revised ? 'Vorschlag zurückziehen' : 'Vorschlag ändern';
      guide=issue+' Tippe auf „'+next+'“, wenn du deinen Rat korrigieren möchtest. Die Hilfe zeigt dir die Kartenstelle.';
    }
    area.append(el('p','decision-guide',guide));
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
    s.id==='L0' ? 'Mein erster Rat' : s.id==='L6' && shortLaura() ? 'Euer vorläufiger Rat' : s.id==='L6' ? 'Zuerst auf dem Laufzettel' : 'Wähle eine Methode');
  const task=el('p',s.id==='L0' || s.id==='T2'?'paper-note':'',
    s.id==='L0' && current.revised ? 'Wähle die Methode für deinen neuen Vorschlag.' : s.task[current.level]);
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
    const b=button(name,()=>selectMethod(id),'method');
    b.id='method-'+id;
    b.setAttribute('aria-pressed',current.selected===id);
    methods.append(b);
  }
  area.append(methods);
  const partners=orderedMethods.filter(([id])=>Object.hasOwn(s.options,'K+'+id));
  if (current.selected==='K' && partners.length) {
    const label=el('label','extra-method','Kondom kombinieren');
    const menu=el('select');
    menu.id='additional';
    menu.add(new Option('Kondom allein',''));
    for (const [id,[name]] of partners) menu.add(new Option('Mit '+name,id));
    menu.value=current.additional;
    menu.onchange=()=>{
      current.additional=menu.value; current.help=0;
      drawWork(); $('additional').focus({preventScroll:true}); revealInWork($('draft-preview'));
    };
    label.append(menu);area.append(label);
  } else if (partners.some(([id])=>id===current.selected)) {
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
    $('help-dock').before(send);
  }
  addTools(area);
}
function openCards() {
  if (screen!=='resources') returnTo=screen;
  show('resources');
  $('resources').querySelector('h1').focus({preventScroll:true});
}
function resume() {
  if (returnTo==='room' && current) openCase(current.person,current.level);
  else if (returnTo==='recovery') {
    show('recovery');
    $('recovery-title').focus({preventScroll:true});
  } else home();
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
$('chat-help').onclick=()=>{
  showPane('answer');
  changeHelp(current.help || 1);
};
$('read-chat').onclick=()=>showPane('chat');
$('write-answer').onclick=()=>showPane('answer');
$('open-recovery').onclick=()=>{
  renderRecovery($('recovery-picker'),FALLAKTE.cases,FALLAKTE.meta.levels,(person,tier,index)=>{
    level=tier;
    openCase(person,tier,index);
  });
  show('recovery');
  $('recovery-title').focus({preventScroll:true});
};
$('leave-recovery').onclick=()=>{
  home();
  $('open-recovery').focus();
};
$('home-nav').onclick=home;
$('brand').onclick=e=>{e.preventDefault();home();};
$('cards-nav').onclick=openCards;
$('resources').querySelector('.return').onclick=resume;
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
