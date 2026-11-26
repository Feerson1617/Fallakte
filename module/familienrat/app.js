'use strict';
const bank = JSON.parse(document.getElementById('material').textContent);
const portraits = JSON.parse(document.getElementById('portraits').textContent);
const ui = bank.ui, names = Object.keys(bank.cases);
const root = document.getElementById('app'), dialog = document.getElementById('dialog');
const body = document.getElementById('dialog-body');
let port, screen = 'home', level = '', current, saved, opener;
let picker = {person:'Mutter', step:'0'};

const el = (parent, tag, text, cls) => {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (cls) node.className = cls;
  parent.append(node);
  return node;
};
function btn(parent, text, id, action, cls) {
  const button = el(parent,'button',text,cls);
  button.id=id; button.onclick=action;
  return button;
}
function paragraph(parent,text,cls) { return el(parent,'p',text,cls); }
function heading(parent,text) {
  const h=el(parent,'h1',text);h.tabIndex=-1;return h;
}
function select(parent,title,id,options,value,change) {
  const label=el(parent,'label',title), field=el(label,'select');field.id=id;
  for(const [key,text] of options){const option=el(field,'option',text);option.value=key;}
  field.value=value;field.onchange=()=>change(field.value);
  return field;
}
function resetPath() {
  saved={history:new Map(),records:{},complete:{},personal:{choice:'',part:0,step:'choice',feedback:'',notes:{},depth:0},last:null};
}
const advanced=t=>bank.levels.indexOf(t)>=2;
function go(type, fields={}) {
  if(!saved.history.size)remember('start','Laura',bank.opening);
  current={type,...fields};screen='work';saved.last=current;draw(true);
}
function record(key){
  return saved.records[key] ||= {depth:0,wrong:false,valid:false,text:'',feedback:'',compared:false};
}
function status(r){
  if(!r?.valid)return ui.unchecked;
  if(r.depth===5||r.solutionShown)return ui.used;
  if(r.depth)return ui.explain;
  return r.wrong?ui.corrected:ui.own;
}
function solutionUsed(person){
  const addition=saved.records[person+'/Ergänzung'];
  return addition?.depth===5 || addition?.solutionShown===true;
}
function hasApplication(person){
  return solutionUsed(person)||saved.records[person+'/Transfer']?.resumed;
}
function applicationStatus(person){
  const r=saved.records[person+'/Transfer'];
  if(!r?.valid)return r?.skipped?ui.skipped:ui.pending;
  if(r.depth===5)return ui.appliedSolution;
  return r.wrong||r.depth?ui.assisted:ui.applied;
}

function notify(){
  port?.postMessage({type:'view',active:screen==='home'?'home':screen==='picker'?'recovery':'',
    status:screen==='work'? (current.person||ui.theme)+' · '+level:''});
}
function popup(title,content,from){
  if(!dialog.open)opener=from || document.activeElement;
  document.getElementById('dialog-title').textContent=title;
  body.replaceChildren();content(body);dialog.scrollTop=0;
  if(!dialog.open)dialog.showModal();
  dialog.dataset.hilfe=String(title==='Hilfe' || title.startsWith(ui.helpTitle+' '));
  Arbeitsplatz.prepareDialog(dialog,body);
}
document.getElementById('dismiss').textContent=ui.close;
document.getElementById('dismiss').onclick=()=>dialog.close();
dialog.onclose=()=>{if(opener?.isConnected)opener.focus({preventScroll:true});};
function cards(index){
  popup(ui.cards,box=>{
    bank.cards.forEach((c,i)=>{
      const details=el(box,'details');details.open=i===index;
      el(details,'summary',c.title);paragraph(details,(level==='Förder'||level==='ESA')?c.short:c.text);
      if(c.short!==c.text && !advanced(level)){const more=el(details,'details');el(more,'summary',ui.deeper);paragraph(more,c.text);}
    });
  });
}
// Ausschließlich explizite medizinische Behauptungen abgleichen. Lauras Entscheidung bleibt offen.
const medizinischeAussagen=[
  {satz:/^(?:nach einem (?:unkomplizierten )?(?:abbruch|schwangerschaftsabbruch) kann (?:man|eine frau) nie (?:mehr |wieder )?schwanger werden|ein (?:schwangerschafts)?abbruch macht (?:immer )?unfruchtbar)$/,quelle:'Später schwanger werden',frage:'Was ist nach einem Abbruch ohne Komplikationen möglich?',info:bank.cards[1].short},
  {satz:/^(?:nach einem (?:unkomplizierten )?(?:abbruch|schwangerschaftsabbruch) wird (?:man|eine frau) (?:garantiert|immer|sicher) (?:wieder )?schwanger)$/,quelle:'Später schwanger werden',frage:'Kann jemand eine spätere Schwangerschaft versprechen?',info:bank.cards[1].short},
  {satz:/^(?:ein medikamentoeser (?:schwangerschafts)?abbruch (?:ist immer schmerzfrei|verursacht nie (?:schmerzen|blutungen)))$/,quelle:'Blutungen und Schmerzen',frage:'Was kann im Bauch passieren?',info:bank.cards[0].short}
];
const medizin=text=>Entwurf.fehler(text||'',medizinischeAussagen);
function help(task,r){
  const tier=task.personalTier || level;
  function show(depth){
    if(!r.valid && r.step!=='done')r.depth=Math.max(r.depth,depth);
    else r.laterDepth=Math.max(r.laterDepth||0,depth);
    popup(ui.helpTitle+' '+depth+' / 5',box=>{
      const issue=medizin(r.text || (r.step==='reason'?r.reason:''));
      const wrong=!r.valid && (r.sourceError || (r.selected!==undefined || r.urteil==='falsch' ? r.feedback:''));
      const where=issue?.quelle || (issue?.ref?'Infokarte zur Verhütung':
        r.sourceError?'Originalnachricht':task.id && bank.definitions[task.id]?'Originalnachricht · '+task.id:
        bank.cards[names.indexOf(current?.person)]?.title || 'Fachinformation zum Anliegen');
      const hints=issue || wrong?Entwurf.hilfen(where,issue?.frage||
          (r.sourceError?'Welche Textstelle beantwortet die Frage?':task.prompt || 'Welche Fachinformation passt zum Anliegen?'),issue?.info||wrong):
          (task.helpByLevel?.[tier] || task.hints);
      if(issue?.ref)hints[0]='Prüfe die Aussage zur Verhütung in deinem eigenen Text.';
      paragraph(box,hints[depth-1]);
      const row=el(box,'div',undefined,'row');
      if(depth<5)btn(row,ui.more,'hint-next',()=>show(depth+1));
      if(depth<4)btn(row,ui.solution,'hint-last',()=>show(5));
    });
  }
  show(1);
}
function profile(box,name){
  const who=el(box,'div',undefined,'profile');
  const img=el(who,'img');img.src=portraits[name];img.alt='';
  el(who,'strong',name);
}
const sentences=text=>text.match(/[^.!?]+[.!?]+|[^.!?]+$/g)?.map(line=>line.trim()) || [text];
function remember(id,speaker,text) {
  saved.history.set(id,{speaker,text});
}
function transcript(panel,hiddenTask){
  const log=el(panel,'div',undefined,'chat-history');
  log.setAttribute('role','log');log.setAttribute('aria-label','Gesprächsverlauf');
  for(const [id,entry] of saved.history){
    if(hiddenTask && (id===hiddenTask || id===hiddenTask+'/entwurf'))continue;
    const item=el(log,'div',undefined,'bubble');
    item.dataset.own=String(id.includes('/'));
    el(item,'strong',entry.speaker);paragraph(item,entry.text);
    if(bank.cases[id]){
      const original=el(item,'details');el(original,'summary','Originalnachricht lesen');
      paragraph(original,bank.cases[id].original);
    }
  }
}
function message(box,name,text){
  profile(box,name);
  for(const line of sentences(text))paragraph(box,line);
}
function chooseLevel(box){
  const field=select(box,'Dein Niveau','level-0',[['',ui.choose],...bank.levels.map(t=>[t,t])],level,value=>{
    if(!value || value===level){field.value=level;return;}
    const change=()=>{level=value;resetPath();draw();};
    if(!saved.last){change();return;}
    field.value=level;
    popup('Niveau wechseln?',content=>{
      paragraph(content,'Beim Wechsel beginnst du neu. Deine Antworten am iPad werden gelöscht.');
      btn(content,'Niveau wechseln','confirm-level',()=>{dialog.close();change();});
    },field);
  });
}
function tools(box,task,r,card){
  let row=el(box,'div',undefined,'tools');
  if(matchMedia('(max-width:650px),(max-height:400px)').matches){
    row=el(row,'details');el(row,'summary','Fachkarte und Begriffe');
  }
  const guided=['Ergänzung','Reichweite','Transfer'].includes(task.id) && !advanced(level);
  btn(row,ui.help,'help',()=>help(task,r));
  btn(row,guided?bank.cards[card].title:ui.cards,'cards',()=>cards(guided?card:undefined));
  const word=bank.definitions[task.id]?task.id:
    ['Ergänzung','Transfer'].includes(task.id)?bank.cases[current.person].missing:
    task.id==='Reichweite'?'Fakt':null;
  if(word)btn(row,word+' erklären','terms',()=>popup(word,b=>paragraph(b,bank.definitions[word])));
  else btn(row,'Begriff erklären','terms',()=>popup('Welcher Begriff?',box=>{
    for(const [term,meaning] of Object.entries(bank.definitions))
      btn(box,term,'begriff-'+term,()=>popup(term,b=>paragraph(b,meaning)));
  }));
}
function showHome(){
  const layout=el(root,'div',undefined,'split'), aside=el(layout,'aside',undefined,'msg');
  message(aside,'Laura',bank.opening);
  const box=el(layout,'section',undefined,'card');
  heading(box,ui.openingTitle);chooseLevel(box);
  if(!level)return;
  if(saved.last)btn(box,ui.resume,'resume',()=>{current=saved.last;screen='work';draw(true);},'primary');
  btn(box,saved.last?ui.fresh:ui.start,'start',()=>{
    if(!saved.last){go('case',{person:'Mutter',at:0});return;}
    popup(ui.fresh,content=>{
      paragraph(content,ui.soloReplace);
      btn(content,ui.fresh,'confirm-start',()=>{
        dialog.close();resetPath();go('case',{person:'Mutter',at:0});
      });
    });
  },saved.last?'':'primary');
  if(saved.complete.Mutter)btn(box,bank.cases.Freundin.titles[0],'friend',()=>go('case',{person:'Freundin',at:0}));

  if(saved.completedReview)reserves(box);
}
function additionalCases(){
  return saved.finalCard && saved.completedReview && names.slice(0,2).every(name=>saved.complete[name]);
}
function reserves(box){
  if(!additionalCases())return;
  el(box,'h2',ui.reserve,'section');
  for(const n of names.slice(2))btn(box,n,'open-'+n,()=>go('case',{person:n,at:0}));
}
function openSection(id){
  for(const [person,c] of Object.entries(bank.cases)){
    const at=c.recovery.findIndex(section=>section.id===id);
    if(at>=0){go('case',{person,at});return;}
  }
  const at=bank.evaluationRecovery.findIndex(section=>section.id===id);
  if(at<0)throw new Error('Unbekannter Abschnitt '+id);
  go('laura',{at});
}
function thought(box,label,text,save,id,buttonText,submit){
  const input=el(el(box,'label',label),'textarea');input.value=text;
  // This is a form check, never a judgement about a pupil's argument or spelling.
  const usable=()=>{
    const letters=input.value.normalize('NFKC').toLowerCase().match(/\p{L}/gu)||[];
    const word=letters.join('');
    return new Set(letters).size>=2 && !/^(?:test|testtext|platzhalter|asdf|qwertz|qwerty|xyz|abc|bla|blabla|loremipsum)$/.test(word);
  };
  const note=paragraph(box,ui.thoughtHint,'small');note.id=id+'-hint';
  input.setAttribute('aria-describedby',note.id);
  const confirm=btn(box,buttonText,id,()=>{if(usable())submit();});
  confirm.disabled=!usable();
  input.oninput=()=>{save(input.value);confirm.disabled=!usable();};
}
function draft(box,task,r,c){
  if(r.valid)return;
  if(r.compared){
    paragraph(box,'Dein eigener Grund · fachlich ungeprüft: '+r.text);
    btn(box,'Erklärung bearbeiten','edit-draft',()=>{r.compared=false;r.feedback='';r.selected=undefined;draw();});
    return;
  }
  if(r.source!==undefined)paragraph(box,ui.sourceYes+' '+sentences(c.original)[r.source],'small');
  if(r.draftError)paragraph(box,r.draftError,'feedback falsch').id='draft-error';
  thought(box,ui.free,r.text,text=>{r.text=text;r.draftError='';box.querySelector('#draft-error')?.remove();},'compare',ui.compare,()=>{
    const issue=medizin(r.text);r.draftError=issue?.info || '';r.compared=!issue;draw(true);
  });
  if(!task.evidenceSentences)return;
  const d=el(box,'details');el(d,'summary',ui.sourceInstead);
  const feedback=paragraph(d,'','small');feedback.setAttribute('role','status');
  sentences(c.original).forEach((line,i)=>{
    btn(d,line,'source-'+i,()=>{
      if(task.evidenceSentences.includes(i)){r.source=i;r.sourceError='';draw();const field=root.querySelector('textarea');Arbeitsplatz.zeigen(field);field.focus({preventScroll:true});}
      else{r.wrong=true;r.sourceError=ui.sourceRetry;feedback.textContent=r.sourceError;}
    });
  });
}
function options(box,task,r,onDone,application=false){
  const retry=!r.valid && r.selected!==undefined && matchMedia('(max-height:400px),(max-width:475px)').matches;
  let choices=box;
  if(retry){
    choices=el(box,'details');el(choices,'summary','Aussage ändern');
  }
  const row=el(choices,'div',undefined,'answers');
  // Rotate in a stable order. A pupil may return to the same choice after opening a card.
  const shift=Array.from(task.prompt).reduce((sum,c)=>sum+c.charCodeAt(0),0)%task.answers.length;
  const arranged=task.answers.slice(shift).concat(task.answers.slice(0,shift));
  const compact=level==='Förder' && task.shortOptions;
  let extra;
  if(compact && arranged.length>2 && !r.valid && !retry){
    extra=el(box,'details');extra.id='more-options';el(extra,'summary',ui.moreOptions);
  }
  for(const o of arranged){
    const index=task.answers.indexOf(o);
    const deeper=application && advanced(level) && o.advancedText;
    const target=extra && !compact.includes(index)?extra:row;
    if(r.valid && r.selected!==index)continue;
    const b=btn(target,deeper?o.advancedText:o.text,'answer-'+index,()=>{
      if(r.text && medizin(r.text))return;
      r.sourceError='';r.feedback=deeper?o.advancedFeedback:o.feedback;r.valid=o.ok;r.selected=index;if(!o.ok)r.wrong=true;
      if(o.revealsSolution)r.solutionShown=true;
      if(o.ok && current.type==='case'){
        const key=current.person+'/'+task.id;
        if(r.text?.trim())remember(key+'/entwurf','Dein eigener Grund · fachlich ungeprüft',r.text);
        remember(key,'Du · '+current.person,deeper?o.advancedText:o.text);
      }
      if(application){r.finished=o.ok;r.skipped=false;}
      draw();
      const target=document.getElementById('response') || root.querySelector('#next');
      Arbeitsplatz.zeigen(target);
      target.tabIndex=-1;
      target.focus({preventScroll:true});
    });
    if(target===extra && r.selected===index)extra.open=true;
    if(r.selected===index)b.dataset.urteil=o.ok?'passend':'falsch';
    b.disabled=r.valid||r.finished===true;b.setAttribute('aria-pressed',String(r.selected===index));
  }
  if(r.feedback){const fb=paragraph(box,r.feedback,r.valid?'feedback':'feedback falsch');fb.id='response';fb.tabIndex=-1;fb.setAttribute('role','status');}
  if(r.valid && !application){
    paragraph(box,task.id==='Reichweite'?ui.limitChecked+' '+status(r):status(r),'tag');
    if(r.compared && r.text){
      const own=el(box,'details');el(own,'summary','Eigenen Grund vergleichen');
      paragraph(own,r.text);paragraph(own,ui.freeNote,'small');
    }
    btn(box,ui.next,'next',onDone,'primary');
  }
}
function originalPanel(layout,person,c,hideAddition){
  const panel=el(layout,'aside',undefined,'msg');
  remember(person,person,c.lesefassung);
  profile(panel,person);
  transcript(panel,hideAddition?person+'/Ergänzung':null);
  const r=saved.records[person+'/Ergänzung'];
  if(r?.valid && !hideAddition){el(panel,'h2',ui.addition);paragraph(panel,c.addition);paragraph(panel,c.connection,'small');}
  return panel;
}
function caseView(){
  const {person,at}=current,c=bank.cases[person],idx=names.indexOf(person);
  const paper=at===c.tasks.length+1, transfer=paper && hasApplication(person);
  const application=transfer?record(person+'/Transfer'):null;
  heading(root,at>0 && !paper?person+' · '+(c.tasks[at-1].id==='Ergänzung'?c.missing:c.tasks[at-1].id):c.recovery[at].section).dataset.section=c.recovery[at].id;
  const layout=el(root,'div',undefined,'split');
  const chat=originalPanel(layout,person,c,transfer && !application.finished);
  const box=el(layout,'section',undefined,'card');
  const advance=()=>go('case',{person,at:at+1});
  if(at===0){
    paragraph(box,bank.known);
    btn(box,ui.read,'next',advance,'primary');
  }else if(!paper){
    const task=c.tasks[at-1],r=record(person+'/'+task.id);
    const adding=task.id==='Ergänzung';
    const concept=adding?c.missing:task.id;
    if(bank.definitions[concept])paragraph(box,concept,'small');
    el(box,'h2',task.prompt);
    if(advanced(level) && !r.valid){

      if(adding)paragraph(box,bank.caseReflection[person]);
      draft(box,task,r,c);
    }
    if(!advanced(level)||r.compared)options(box,task,r,advance);
    tools(box,task,r,idx);
  }else{
    if(transfer){
      const task=c.transfer;box.dataset.application=task.sectionId;
      if(!application.finished){
        
        el(box,'h2',advanced(level) && task.advancedPrompt?task.advancedPrompt:task.prompt);
        options(box,task,application,null,true);
        tools(box,task,application,idx);
        btn(box,ui.switch,'jump',()=>{application.skipped=true;go('laura',{at:0});});
        return;
      }
      const checked=paragraph(chat,application.feedback,'feedback');
      checked.id='response';checked.tabIndex=-1;checked.setAttribute('role','status');
      paragraph(box,applicationStatus(person),'tag');
    }
    if(c.tasks.every(task=>saved.records[person+'/'+task.id]?.valid))saved.complete[person]=true;
    const next=idx===0?'Nachricht der Freundin':idx===1?'Zu Lauras Frage':'Zur Übersicht';
    el(box,'h2','Zur Nachricht');
    const result=saved.records[person+'/Ergänzung'];
    if(result?.valid)paragraph(box,c.addition);else paragraph(box,'Hier kannst du die Fachinformation noch prüfen.');
    btn(box,next,'next',()=>{if(idx===0)go('case',{person:names[1],at:0});else if(idx===1)go('laura',{at:0});else{screen='home';draw();}},'primary');
  }
}

function facts(box){
  const d=el(box,'details');el(d,'summary','Schon geprüft');
  let count=0;
  for(const name of names.slice(0,2)){
    const c=bank.cases[name];
    for(const t of c.tasks){
      const r=saved.records[name+'/'+t.id];
      if(!r?.valid)continue;
      el(d,'strong',name+' · '+(t.id==='Ergänzung'?c.missing:t.id));
      paragraph(d,t.id==='Ergänzung'?c.addition:t.answers[r.selected].text);count++;
    }
  }
  if(!count)paragraph(d,'In dieser Sitzung hast du noch keine Nachricht geprüft.');
}
function evaluationHelp(box,r){
  btn(box,ui.help,'help',()=>help({hints:bank.evaluationHints,helpByLevel:bank.evaluationHelpByLevel,personalTier:level},r));
}
const reviewText=i=>bank.review[i][1].split('“')[0];
function comparison(box){
  const p=saved.personal;
  el(box,'h2',level);
  const end=()=>{
    p.step='done';saved.completedReview=true;go('laura',{at:3});
  };
  if(p.choice){
    paragraph(box,'Deine Einschätzung · '+p.choice);
    btn(box,ui.editWeight,'edit-weight',()=>{
      if(!window.confirm('Gewichtung ändern? Die bisherige Prüfung dieser Gewichtung beginnt neu.'))return;
      p.step='choice';p.choice='';p.part=0;p.notes={};p.reason='';p.alternate=false;p.other=false;p.feedback='';
      // Recheck the selection while keeping any support this person already received.
      for(const [key,r] of Object.entries(saved.records)){
        if(key.startsWith('Bewertung/'))Object.assign(r,{valid:false,selected:undefined,feedback:''});
      }
      saved.completedReview=false;draw(true);
    });
  }
  if(p.step==='done'){
    paragraph(box,ui.personal);btn(box,ui.next,'next',end,'primary');return;
  }
  if(p.step==='choice'){
    paragraph(box,'Welche Nachricht hilft Laura besonders?');
    for(const [i,name] of [...names.slice(0,2),ui.both,'Ich bin noch unsicher'].entries())
      btn(box,name,'weight-'+i,()=>{p.choice=name;p.part=0;p.step='concern';p.feedback='';draw(true);});
  }else{
    const person=(p.choice===ui.both || p.choice==='Ich bin noch unsicher')?names[p.part]:p.choice,num=names.indexOf(person);
    el(box,'strong',person);
    if(p.step==='concern'){
      paragraph(box,ui.priority);
      [ui.questionA,ui.questionB].forEach((v,i)=>btn(box,v,'concern-'+i,()=>{
        p.concern=i;p.reason='';p.alternate=false;p.other=false;p.step='fact';p.feedback='';draw(true);
      }));
    }else if(p.step==='fact'){
      paragraph(box,p.concern?ui.questionB:ui.questionA);paragraph(box,ui.evidence);
      const values=[bank.cases.Mutter.addition,bank.cases.Freundin.addition,ui.guarantee,ui.forced];
      values.forEach((v,i)=>btn(box,v,'fact-'+i,()=>{
        p.alternate=false;
        if(i!==p.concern)record('Bewertung/'+person+'/'+p.concern).wrong=true;
        p.urteil=i>=2?'falsch':i===p.concern?'persoenlich':'impuls';
        if(i>=2)p.feedback=reviewText(i===2?6:7);
        else if(i!==p.concern)p.feedback=reviewText(p.concern===0?4:5);
        else if(i!==num){p.feedback=bank.crossReference[i];p.alternate=true;}
        else{p.step='limit';p.feedback='';}
        draw();
      }));
      if(p.alternate)btn(box,ui.other,'other',()=>{p.other=true;p.step='reason';p.feedback='';draw(true);});
      btn(box,ui.again,'rechoose',()=>{p.step='concern';p.feedback='';p.alternate=false;draw();});
    }else if(p.step==='reason'){
      paragraph(box,ui.otherNote);
      paragraph(box,bank.crossReference[p.concern]);
      thought(box,ui.openReason,p.reason||'',text=>{p.reason=text;p.feedback='';box.querySelector('.retry')?.remove();},'check-reason',ui.continueReason,()=>{
        const issue=medizin(p.reason);if(issue){p.feedback=issue.info;p.urteil='falsch';draw(true);return;}
        p.feedback='';p.step='limit';draw(true);
      });
      btn(box,ui.again,'rechoose',()=>{p.step='concern';p.other=false;draw(true);});
    }else{
      const target=p.concern;
      const r=record('Bewertung/'+person+'/'+target),task=bank.limits[target];
      paragraph(box,p.other?ui.checkLimit:ui.evidenceOK);
      if(p.other){
        paragraph(box,p.reason);
        btn(box,ui.editReason,'edit-reason',()=>{p.step='reason';draw(true);});
      }
      paragraph(box,p.concern?ui.reasonB:ui.reasonA);
      el(box,'h3',task.prompt);
      options(box,task,r,()=>{
        p.notes[person]={concern:target,reason:p.other?p.reason:'',outcome:status(r)};
        if((p.choice===ui.both || p.choice==='Ich bin noch unsicher')&&p.part===0){p.part++;p.step='concern';p.other=false;p.alternate=false;draw(true);}
        else end();
      });
      tools(box,{...task,personalTier:level},r,target);return;
    }
    if(p.feedback){const msg=paragraph(box,p.feedback,'feedback retry '+p.urteil);msg.setAttribute('role','status');}
  }
  evaluationHelp(box,p);
}
function lauraView(){
  const at=current.at;heading(root,bank.evaluationSteps[at]).dataset.section=bank.evaluationRecovery[at].id;
  const layout=el(root,'div',undefined,'split'),panel=el(layout,'aside',undefined,'msg');
  remember('frage','Laura',bank.second);profile(panel,'Laura');transcript(panel);
  const box=el(layout,'section',undefined,'card');
  facts(box);
  if(at===0){
    paragraph(box,'Welche Frage ist Laura wichtig?');
    btn(box,'Nachrichten abwägen','next',()=>go('laura',{at:2}),'primary');
  }else if(at===1 || at===2)comparison(box);
  else{
    if(saved.personal.choice)paragraph(box,'Deine Einschätzung · '+saved.personal.choice);
    paragraph(box,'Deine Lehrkraft gibt die Abschlusskarte aus. Begründe dort deine eigene Einschätzung.');
    if(saved.completedReview && !saved.finalCard)btn(box,'Meine Begründung steht auf der Abschlusskarte','abschlusskarte',()=>{saved.finalCard=true;draw();});
    if(saved.finalCard)reserves(box);
    if(!saved.completedReview)btn(box,'Zur Abwägung','open-review',()=>go('laura',{at:2}));
  }
}

function pickerView(){
  heading(root,ui.where);chooseLevel(root);if(!level)return;
  if(saved.last)paragraph(root,ui.soloSession,'small');
  if(!additionalCases() && !saved.paperRecovery)
    btn(root,'Meine Begründung steht auf der Abschlusskarte','papierstand',()=>{saved.paperRecovery=true;draw();});
  const available=additionalCases()||saved.paperRecovery?names:names.slice(0,2);
  if(![...available,ui.theme].includes(picker.person))picker={person:'Mutter',step:'0'};
  select(root,ui.home,'person',[...available,ui.theme].map(k=>[k,k]),picker.person,v=>{picker={person:v,step:'0'};draw();});
  const n=picker.person,c=bank.cases[n];
  const steps=c?c.recovery.map((r,i)=>[i,c.recovery.filter(s=>s.section===r.section).length>1?r.section+' · '+r.part:r.section]):bank.evaluationSteps.map((v,i)=>[i,v]);
  if(c){
    steps.push(['transfer','Fachinformation anwenden']);
  }
  select(root,ui.selectSection,'entry',steps,picker.step,v=>{picker.step=v;draw();});
  btn(root,ui.resumeHere,'open-entry',()=>{
    if(c && picker.step==='transfer'){
      record(n+'/Transfer').resumed=true;
      go('case',{person:n,at:c.tasks.length+1});return;
    }
    const at=Number(picker.step);
    if(c)go('case',{person:n,at});else go('laura',{at});
  },'primary');
}
function draw(focus=false){
  root.replaceChildren();root.classList.remove('gespraech-offen');
  if(screen==='home')showHome();else if(screen==='picker')pickerView();else if(current.type==='case')caseView();else lauraView();
  const work=root.querySelector('.split>.card')||root;
  const title=root.querySelector(':scope>h1')||work.querySelector('h1');
  const hint=screen==='picker'?'Wähle die Person und den Abschnitt, bei dem du weiterarbeiten willst.':
    screen==='home'?'Wähle dein Niveau. Öffne dann die erste Nachricht.':
    'Lies die aktuelle Nachricht. Der Arbeitsauftrag nennt den nächsten Schritt.';
  Arbeitsplatz.setup(root,work,root.querySelector('.split>.msg'),title,root.querySelector('#help'),b=>popup('Hilfe',box=>paragraph(box,hint),b));
  notify();
  if(focus){window.scrollTo(0,0);root.querySelector('h1')?.focus({preventScroll:true});}
}
window.addEventListener('message',e=>{
  if(e.source!==parent||e.data!=='fallakte:navigation'||!e.ports[0])return;
  port?.close();port=e.ports[0];
  port.onmessage=({data})=>{
    if(dialog.open)dialog.close();
    if(data==='abschluss'){popup('Stundenabschluss',box=>{
      facts(box);paragraph(box,'Deine Lehrkraft gibt dir die Abschlusskarte. Begründe darauf, welche Nachricht dir bei Lauras Frage hilft. Auch Unsicherheit kannst du begründen.');
    });return;}
    if(data==='resources'){cards();return;}
    if(data==='home'||data==='recovery'){screen=data==='home'?'home':'picker';draw(true);}
  };
  port.postMessage({type:'ready',actions:[{id:'home',label:ui.home,icon:'folder'},{id:'resources',label:ui.cards,icon:'book'},{id:'recovery',label:'Wiedereinstieg',icon:'restart'},{id:'abschluss',label:'Stundenabschluss'}]});notify();
});
resetPath();draw();
