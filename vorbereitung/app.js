(function () {
'use strict';
const bank = JSON.parse(document.getElementById('material').textContent);
const ui = bank.ui;
const view = document.querySelector('#view');
const sheet = document.querySelector('#sheet');
const sessions = new Map();
let level = '';
let screen = 'home';
function session() { return sessions.get(level); }
function chapters() { return bank.levels[level].chapters; }
function intro() { return bank.levels[level].intro; }
function chapter() { return chapters().find(c => c.id === session().id); }
function progress() { return session().progress[session().id]; }
function currentQuestion() {
  const s = progress();
  if (session().id === 'PI') return intro().question;
  return s.step === 'paper' ? chapter().paperCheck : chapter().questions[s.index];
}
function attempt() {
  const s = progress();
  return s.attempts[currentQuestion().id] ??= {
    choice: -1, checked: -1, depth: 0, maxDepth: 0, errors: 0, passed: false,
    raw: '', transfer: false, extraChoice: -1, extraChecked: -1, sent: false
  };
}
function esc(value) {
  return String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
}
function btn(action, label, opts={}) {
  return `<button data-do="${action}" ${opts.value !== undefined ? `data-value="${esc(opts.value)}"` : ''} ${opts.primary?'class="primary"':''} ${opts.disabled?'disabled':''} ${opts.pressed !== undefined ? `aria-pressed="${opts.pressed}"`:''}>${esc(label)}</button>`;
}
function name(key) { return key === 'Foerder' ? 'Förder' : key; }
function home() {
  const exists = level && session()?.id;
  return `<article class="home"><h1>${esc(bank.title)}</h1><p class="lead">Lies die Informationen, prüfe deine Antwort und ergänze deine Infokarte auf Papier.</p>
    <section class="panel"><h2>${ui.level}</h2><div class="levels">${Object.keys(bank.levels).map(k=>btn('level',name(k),{value:k,pressed:k===level})).join('')}</div>
    ${level ? `<div class="actions">${exists?btn('resume',ui.resume,{primary:true}):''}${btn('new',ui.start,{primary:!exists})}${btn('picker',ui.picker)}</div><p class="note">Nach einem Neustart: Wähle den zuletzt auf Papier markierten Abschnitt.</p>`:''}</section>
    ${level?btn('references',ui.reference):''}</article>`;
}
function picker() {
  return `<h1>${ui.picker}</h1><p>Laufzettel: Suche das zuletzt markierte Kapitel. Wähle es hier oder öffne das nächste Kapitel.</p><div class="chapters">${chapters().map(c=>{
    const p=session().progress[c.id];
    return `<button data-do="open" data-value="${c.id}">${esc(c.title)}${p?`<small>${p.finished?'In dieser Sitzung bearbeitet':'Begonnen'}</small>`:''}</button>`;
  }).join('')}</div>`;
}
function selectChapter(id) {
  const s=session();
  s.id=id;
  s.progress[id] ??= {step:'info',index:0,attempts:{},finished:false};
  screen='learn';
}
function pearl() {
  const p=intro();
  return `<p>${esc(p.information)}</p><dl>${Object.entries(p.values).map(([method,value])=>`<dt>${esc(method)}</dt><dd>${esc(value)}</dd>`).join('')}</dl><details><summary>Quelle der Richtwerte</summary><p class="note">${esc(bank.pearlNote)}</p></details>`;
}
function material() {
  if (session().id==='PI') return pearl();
  const c=chapter(), v=bank.visualBriefs[c.visualRef];
  return `<div class="grid"><div class="material">${c.information.map(i=>`<section><h3>${esc(i.title)}</h3><p>${esc(i.text)}</p></section>`).join('')}${c.supportingInfo?`<p class="tip" id="supporting">${esc(c.supportingInfo)}</p>`:''}</div>
    <figure class="figure"><h3>${esc(v.title)}</h3>${bank.graphics[c.visualRef]}<figcaption>${esc(c.observationPrompt)}</figcaption></figure></div><details><summary>${esc(intro().title)}</summary>${pearl()}</details>`;
}
function fullCard(card) {
  return `<article class="reference"><h2>${esc(card.title)}</h2><p><strong>Pearl-Index: ${esc(card.pearlIndex)} · Richtwert nach pro familia</strong> ${esc(card.pearlExplanation)} Kein Maß für den Schutz vor sexuell übertragbaren Infektionen (STI).</p>
    ${card.sections.map(s=>`<h3>${esc(s.title)}</h3><p>${esc(s.completedText)}</p>`).join('')}<ul class="fields">${card.fields.map(f=>`<li data-field="${f.id}">Feld ${f.number} <b>${esc(f.answer)}</b></li>`).join('')}</ul></article>`;
}
function dialog(title,html) {
  document.querySelector('#sheet-title').textContent=title;
  document.querySelector('#sheet-content').innerHTML=html;
  if(!sheet.open) sheet.showModal();
  sheet.scrollTop=0;
}
function showReferences() {
  dialog('Musterkarten',`<p>Infokarte: Wähle am iPad die Methode, zu der dir Wörter fehlen. Ergänze die nummerierten Felder. Die Fragen im Chat bleiben offen.</p><div class="chapters">${bank.cards[level].map(c=>btn('reference',c.title,{value:c.method})).join('')}</div>`);
}
function status(a) {
  const wasModel=session().models.has(chapter()?.method);
  if (a.maxDepth===5) return 'Mit Lösungshilfe und eigener Anwendung gelöst.';
  if (a.maxDepth) return `Mit Hilfe ${a.maxDepth} gelöst.`;
  if (wasModel) return 'Nach Ansicht der Musterkarte gelöst.';
  if (a.errors) return 'Nach Korrektur gelöst.';
  return 'Selbstständig gelöst.';
}
function help(q,a) {
  const list=q.options[a.checked]?.hints || q.hintsBeforeChoice;
  return `<div class="help">${a.depth ? `<div class="tip" role="status"><strong>Hilfe ${a.depth} von 5</strong><br>${esc(list[a.depth-1])}</div>`:''}
    <div class="actions">${a.depth<5?btn('hint',a.depth?ui.moreHelp:ui.help):''}${a.depth===5?btn('references',ui.reference):''}</div></div>`;
}
function feedback(text,retry=false) {
  return `<div class="feedback" data-kind="${retry?'retry':'ok'}" role="status">${esc(text)}</div>`;
}
function options(q, selected, extra, locked) {
  return `<div class="answers">${q.options.map((o,i)=>btn(extra?'extra-choice':'choice',o.text,{value:i,pressed:selected===i,disabled:locked})).join('')}</div>`;
}
function transfer(q,a) {
  const application=q.afterSolutionCheck;
  const checked=application.options[a.extraChecked];
  return `<section id="application"><h2>Nach der Lösungshilfe</h2><p>${esc(application.prompt)}</p>${options(application,a.extraChoice,true,a.passed)}
    ${!a.passed?btn('extra-check',ui.check,{disabled:a.extraChoice<0,primary:true}):''}
    ${checked?feedback(checked.feedback,!checked.correct):''}</section>`;
}
function confirmed(a) {
  return `<p class="status">${esc(a.outcome)}</p>`;
}
function question(q,a) {
  const chosen=q.options[a.checked];
  return `<article class="question"><h2>${esc(q.prompt)}</h2>
    ${options(q,a.choice,false,a.passed||a.transfer)}
    ${!a.passed&&!a.transfer?btn('check',ui.check,{disabled:a.choice<0,primary:true}):''}
    ${chosen?feedback(chosen.feedback,!chosen.correct):''}
    ${a.transfer?transfer(q,a):''}
    ${a.passed?confirmed(a)+btn('advance',ui.next,{primary:true}):!a.transfer?help(q,a):''}</article>`;
}
function fields(c) {
  return `<div class="paper"><h2>Infokarte ergänzen</h2><p>${esc(c.paperPrompt)}</p><ul class="fields">${c.cardEntries.map(f=>`<li data-field="${f.fieldId}">Feld ${f.number} · ${esc(f.sectionTitle)} <b>${esc(f.exactEntry)}</b></li>`).join('')}</ul></div>`;
}
function paperCheck(q,a) {
  const checked=q.options[a.checked];
  if(a.sent) return `<p>Nachricht gesendet · ${esc(q.options[a.choice].code)}</p>${feedback(checked.feedback)}${confirmed(a)}${btn('finish',ui.next,{primary:true})}`;
  return `<p>${esc(q.screen)}</p><details><summary>Ausfallhilfe · Aussagen ohne Papierbogen anzeigen</summary><strong>${esc(q.prompt)}</strong><ol type="A">${q.options.map(o=>`<li>${esc(o.text)}</li>`).join('')}</ol></details><p>${esc(q.return)}</p>
    <div class="actions"><label for="code">Buchstabe</label><input id="code" type="text" autocomplete="off" autocapitalize="characters" spellcheck="false" value="${esc(a.raw)}">
    ${btn('code-check',ui.codeCheck,{disabled:!a.raw.trim()||a.passed||a.transfer})}
    ${btn('send',ui.send,{disabled:!a.passed,primary:true})}</div>
    <div id="code-result">${a.invalid?feedback('Gib einen der Buchstaben A, B oder C ein.',true):checked?feedback(checked.feedback,!checked.correct):''}
    ${a.transfer?transfer(q,a):''}${a.passed?confirmed(a):!a.transfer?help(q,a):''}</div>`;
}
function digitalChecks(list) {
  const done=list.filter(c=>{
    const checks=session().progress[c.id]?.attempts;
    return checks && c.questions.every(q=>checks[q.id]?.passed) &&
      (!c.paperCheck || checks[c.paperCheck.id]?.sent);
  });
  return `<p class="note">In dieser Sitzung hast du alle Fachchecks für <strong id="checked-chapters">${done.map(c=>esc(c.id)).join(', ')}</strong> abgeschlossen.</p>`;
}
function firstHourEnd() {
  const all=chapters(), first=all.slice(0,4);
  const complete=first.every(c=>session().progress[c.id]?.finished);
  const next=all.slice(4).find(c=>!session().progress[c.id]?.finished);
  return `<h1>Ende der ersten Vorbereitungsstunde</h1>
    <p>${complete?'Du hast Kondom und Kombinationspille bearbeitet.':'In den Kapiteln 1A bis 2B geht es um Kondom und Kombinationspille.'}</p>
    <div class="paper"><p>Infokarten „Kondom“ und „Kombinationspille“: Prüfe die Felder 1 bis 4 auf beiden Kartenflächen.</p>
    <p>Laufzettel: Markiere das Kapitel, mit dem du weiterarbeitest.</p></div>
    <p>Öffne in der nächsten Stunde Kapitel 3A oder den nächsten offenen Abschnitt auf deinem Papier.</p>
    ${digitalChecks(first)}
    <div class="actions">${next?btn('open','Jetzt mit '+next.id+' weiterarbeiten',{value:next.id}):''}${btn('picker',ui.picker)}</div>`;
}
function preparationEnd() {
  return `<h1>Abschluss der Vorbereitung</h1>
    <section class="panel"><h2>Zwei doppelseitige Infokarten kontrollieren</h2>
    <p>Vergleiche für jede der vier Methoden die Felder 1 bis 4 mit der Musterkarte am iPad. Ergänze fehlende Wörter auf deiner Infokarte.</p>
    <div class="chapters">${bank.cards[level].map(c=>btn('reference',c.title,{value:c.method})).join('')}</div>
    <p class="paper">Schneide das beidseitig bedruckte Blatt einmal an der gestrichelten Linie durch. Bewahre beide Karten für den Unterrichtsbesuch auf.</p></section>
    ${digitalChecks(chapters())}${btn('picker',ui.picker)}`;
}
function learning() {
  const c=chapter(), s=progress(), title=c?.title||intro().title;
  let body;
  if (s.finished) {
    if(c?.id==='2B') return firstHourEnd();
    if(c?.id==='4B') return preparationEnd();
    body=`<p>Du hast diesen Abschnitt bearbeitet.</p>${btn('continue',c?.nextChapter?ui.next:ui.picker,{primary:true})}`;
  } else if(s.step==='info') {
    body=`${c?`<p class="paper">Papier · Markiere <strong>${c.id}</strong> auf deinem Laufzettel.</p>`:''}<section class="panel">${material()}</section>${btn('begin','Zur Fachfrage',{primary:true})}`;
  } else if(s.step==='question') {
    body=`<div class="tools"><strong>${c?'Fachfrage '+(s.index+1)+' von 2':'Fachfrage'}</strong>${btn('material',ui.read)}</div>${question(currentQuestion(),attempt())}`;
  } else if(s.step==='paper') {
    body=c.paperCheck && attempt().sent ? '' : fields(c);
    if (!c.paperCheck || !attempt().sent) body+=`<div class="tools">${c.paperCheck?'':'<strong>'+esc(c.backToChat)+'</strong>'}${btn('material',ui.read)}</div>`;
    body+=c.paperCheck?paperCheck(c.paperCheck,attempt()):btn(c.id.endsWith('B')?'review':'finish',c.id.endsWith('B')?'Vollständige Karte vergleichen':ui.next,{primary:true});
  } else {
    const card=bank.cards[level].find(card=>card.method===c.method);
    body=`<p class="paper">Infokarte „${esc(card.title)}“: Vergleiche die Felder 1 bis 4 mit der Musterkarte. Ergänze fehlende Wörter. Laufzettel „${esc(c.id)}“: Kreuze „${ui.cardReview}“ an.</p>${fullCard(card)}<p>Tippe auf „${ui.next}“.</p>${btn('finish',ui.next,{primary:true})}`;
  }
  return `<h1>${esc(title)}</h1>${body}`;
}
function render(focus=false) {
  document.querySelector('#level-name').textContent=level?name(level):'';
  document.querySelector('#overview').hidden=screen==='home';
  view.innerHTML=screen==='home'?home():screen==='picker'?picker():learning();
  if (focus) {view.focus({preventScroll:true});window.scrollTo(0,0);}
}
function check(q,a,code=false) {
  if(a.passed||a.transfer) return;
  if(code) {
    a.choice=q.options.findIndex(o=>o.code===a.raw.trim().toUpperCase());
    a.invalid=a.choice<0;
  }
  if(a.choice<0) return;
  a.checked=a.choice;
  if(!q.options[a.choice].correct){a.errors++;return;}
  if(a.maxDepth===5){a.transfer=true;return;}
  a.passed=true;
  a.outcome=status(a);
}
function clearChoice(a) {
  a.checked=-1;
  a.depth=0;
  a.invalid=false;
}
function startNew() {
  sessions.set(level,{id:null,progress:{},models:new Set()});
  selectChapter('PI');
}
document.querySelector('#close-sheet').onclick=()=>sheet.close();
document.addEventListener('input',event=>{
  if(event.target.id!=='code') return;
  const a=attempt();
  a.raw=event.target.value;
  a.choice=-1;
  clearChoice(a);
  a.passed=false; a.transfer=false; a.extraChoice=-1; a.extraChecked=-1;
  const replacement=document.createElement('div');
  replacement.innerHTML=paperCheck(currentQuestion(),a);
  document.querySelector('#code-result').replaceWith(replacement.querySelector('#code-result'));
  document.querySelector('[data-do=send]').disabled=true;
  document.querySelector('[data-do=code-check]').disabled=!a.raw.trim();
});
document.addEventListener('click',event=>{
  const el=event.target.closest('button[data-do]');
  if(!el||el.disabled) return;
  const what=el.dataset.do, value=el.dataset.value;
  const s=session();
  if(what==='material'){dialog(ui.read,material());return;}
  if(what==='references'){showReferences();return;}
  if(what==='reference'){
    s.models.add(value);
    const card=bank.cards[level].find(c=>c.method===value);
    dialog('Musterkarte · '+name(level),fullCard(card));return;
  }
  if(what==='new'&&s?.id){
    dialog(ui.start,`<p>Den Arbeitsstand für ${name(level)} in dieser Sitzung zurücksetzen?</p>${btn('reset','Ja, neu beginnen')}`);
    return;
  }
  let jump=true;
  switch(what){
    case 'level':
      level=value;
      if(!sessions.has(level)) sessions.set(level,{id:null,progress:{},models:new Set()});
      jump=false;break;
    case 'home': screen='home';break;
    case 'picker': screen='picker';break;
    case 'new': case 'reset': if(sheet.open) sheet.close();startNew();break;
    case 'resume': if(s?.id) screen='learn';break;
    case 'open': selectChapter(value);break;
    case 'begin': progress().step='question';break;
    case 'review': progress().step='review';break;
    case 'finish':
      if(chapter().paperCheck&&!attempt().sent) return;
      progress().finished=true;
      if(s.id==='2B'||s.id==='4B') break;
    // Other chapters continue directly after the paper return.
    case 'continue':
      if(chapter()?.nextChapter) selectChapter(chapter().nextChapter);
      else screen='picker';
      break;
    case 'advance':
      if(!attempt().passed) return;
      if(s.id==='PI'){progress().finished=true;selectChapter('1A');}
      else if(progress().index===0){progress().index=1;}
      else progress().step='paper';
      break;
    default: {
      const a=attempt(), q=currentQuestion();
      jump=false;
      if(what==='choice'&&!a.passed&&!a.transfer&&a.choice!==Number(value)){
        a.choice=Number(value);clearChoice(a);
      } else if(what==='check') check(q,a);
      else if(what==='code-check') check(q,a,true);
      else if(what==='hint'&&!a.passed&&!a.transfer){
        a.depth=Math.min(5,a.depth+1);a.maxDepth=Math.max(a.maxDepth,a.depth);
      } else if(what==='extra-choice'&&a.transfer&&!a.passed){
        a.extraChoice=Number(value);a.extraChecked=-1;
      } else if(what==='extra-check'&&a.transfer&&!a.passed&&a.extraChoice>=0){
        a.extraChecked=a.extraChoice;
        if(q.afterSolutionCheck.options[a.extraChecked].correct){a.passed=true;a.outcome=status(a);}
        else a.errors++;
      } else if(what==='send'&&a.passed&&!a.sent){a.sent=true;}
    }
  }
  render(jump);
  if(!jump){
    const same=[...view.querySelectorAll('button[data-do]')].find(b=>b.dataset.do===what&&b.dataset.value===value&&!b.disabled);
    (same||view.querySelector('#application button:not(:disabled),[data-do=advance],[data-do=send]:enabled,[data-do=finish],.answers button:enabled'))?.focus({preventScroll:true});
  }
});
render();
})();
