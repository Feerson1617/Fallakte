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
function help(task,r){
  const tier=task.personalTier || level;
  function show(depth){
    if(!r.valid && r.step!=='done')r.depth=Math.max(r.depth,depth);
    else r.laterDepth=Math.max(r.laterDepth||0,depth);
    popup(ui.helpTitle+' '+depth+' / 5',box=>{
      paragraph(box,(task.helpByLevel?.[tier] || task.hints)[depth-1]);
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
  const row=el(box,'div',undefined,'tools');
  const guided=['Ergänzung','Reichweite','Transfer'].includes(task.id) && !advanced(level);
  btn(row,ui.help,'help',()=>help(task,r));
  btn(row,guided?bank.cards[card].title:ui.cards,'cards',()=>cards(guided?card:undefined));
  btn(row,ui.terms,'terms',()=>popup(ui.terms,b=>Object.entries(bank.definitions).forEach(([k,v])=>{el(b,'strong',k);paragraph(b,v);})));
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
  btn(box,ui.switch,'jump',()=>go('laura',{at:0}));
  if(saved.completedReview)reserves(box);
}
function additionalCases(){
  return saved.completedReview && names.slice(0,2).every(name=>saved.complete[name]);
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
function paperOrder(box,key,{button=false,support=false}={}){
  const step=bank.media.steps[key];
  const panel=el(box,'div',undefined,'note');
  panel.dataset.handoff=step.id;
  const order=paragraph(panel,step.orders[level].screen,'paper-order');
  order.dataset.level=level;
  if(support)paragraph(panel,step.support);
  if(!button){
    let instruction=step.returnText;
    if(step.nextId===step.sectionId && advanced(level))instruction='Schreibe deine Erklärung am iPad. Tippe auf „'+ui.compare+'“.';
    const handoff=paragraph(panel,instruction,'small');
    if(step.nextId)handoff.dataset.return=step.nextId;
    else handoff.dataset.terminal='paper';
  }
  if(step.after)paragraph(panel,step.after,'small');
  return step;
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
    paragraph(box,r.text);
    paragraph(box,ui.freeNote,'small');
    return;
  }
  if(r.source!==undefined)paragraph(box,ui.sourceYes+' '+sentences(c.original)[r.source],'small');
  thought(box,ui.free,r.text,text=>r.text=text,'compare',ui.compare,()=>{r.compared=true;draw(true);});
  if(!task.evidenceSentences)return;
  const d=el(box,'details');el(d,'summary',ui.sourceInstead);
  const feedback=paragraph(d,'','small');feedback.setAttribute('role','status');
  sentences(c.original).forEach((line,i)=>{
    btn(d,line,'source-'+i,()=>{
      if(task.evidenceSentences.includes(i)){r.source=i;draw();const field=root.querySelector('textarea');Arbeitsplatz.zeigen(field);field.focus({preventScroll:true});}
      else{r.wrong=true;feedback.textContent=ui.sourceRetry;}
    });
  });
}
function options(box,task,r,onDone,application=false){
  const row=el(box,'div',undefined,'answers');
  // Rotate in a stable order. A pupil may return to the same choice after opening a card.
  const shift=Array.from(task.prompt).reduce((sum,c)=>sum+c.charCodeAt(0),0)%task.answers.length;
  const arranged=task.answers.slice(shift).concat(task.answers.slice(0,shift));
  const compact=level==='Förder' && task.shortOptions;
  let extra;
  if(compact && arranged.length>2 && !r.valid){
    extra=el(box,'details');extra.id='more-options';el(extra,'summary',ui.moreOptions);
  }
  for(const o of arranged){
    const index=task.answers.indexOf(o);
    const deeper=application && advanced(level) && o.advancedText;
    const target=extra && !compact.includes(index)?extra:row;
    if(r.valid && r.selected!==index)continue;
    const b=btn(target,deeper?o.advancedText:o.text,'answer-'+index,()=>{
      r.feedback=deeper?o.advancedFeedback:o.feedback;r.valid=o.ok;r.selected=index;if(!o.ok)r.wrong=true;
      if(o.revealsSolution)r.solutionShown=true;
      if(o.ok && current.type==='case'){
        const key=current.person+'/'+task.id;
        if(r.text?.trim())remember(key+'/entwurf','Deine Erklärung',r.text);
        remember(key,'Du · '+current.person,deeper?o.advancedText:o.text);
      }
      if(application){r.finished=o.ok;r.skipped=false;}
      draw();
      const target=application && o.ok?root.querySelector('[data-handoff]'):document.getElementById('response');
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
    if(r.compared && r.text)paragraph(box,ui.freeNote,'small');
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
  heading(root,c.recovery[at].section).dataset.section=c.recovery[at].id;
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
    if(adding && !r.valid && r.selected===undefined && !r.compared)paperOrder(box,c.recovery[0].id.split('-')[0]+'-erst');
    el(box,'h2',task.prompt);
    const phase=adding?'Ergänzung':'analyse';
    if(advanced(level) && !r.valid){
      paragraph(box,level+' · '+bank.levelPrompts[level][phase],'small');
      if(adding)paragraph(box,bank.caseReflection[person]);
      draft(box,task,r,c);
    }else if(adding && !r.valid)paragraph(box,bank.levelPrompts[level][phase],'small');
    if(!advanced(level)||r.compared)options(box,task,r,advance);
    tools(box,task,r,idx);
  }else{
    if(transfer){
      const task=c.transfer;box.dataset.application=task.sectionId;
      if(!application.finished){
        paragraph(box,ui.helpBeforePaper,'small');
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
    const prefix=c.recovery[0].id.split('-')[0];
    const key=prefix+(idx>=2 && !saved.completedReview?'-einstieg':'-ergebnis');
    const result=saved.records[person+'/Ergänzung'];
    if(result?.valid)paragraph(box,status(result),'tag');
    else{
      paragraph(box,ui.supported+' · '+ui.noPast,'small');
      paragraph(box,c.addition);
    }
    el(box,'h2',ui.paper);
    const step=paperOrder(box,key,{button:true,support:solutionUsed(person)});
    btn(box,step.buttonText,'next',()=>{
      if(c.tasks.every(task=>saved.records[person+'/'+task.id]?.valid))saved.complete[person]=true;
      openSection(step.nextId);
    },'primary').dataset.return=step.nextId;
    const matrix=el(box,'details');matrix.dataset.digital='matrix';
    el(matrix,'summary',ui.readMatrix);
    for(const [key,value] of Object.entries(c.matrix)){el(matrix,'strong',key);paragraph(matrix,value);}
  }
  if(idx<2){
    const bar=el(box,'div',undefined,'tools');btn(bar,ui.switch,'jump',()=>go('laura',{at:0}));
  }
}
function facts(box){
  const d=el(box,'details');el(d,'summary',ui.facts);
  for(const n of names.slice(0,2)){
    el(d,'strong',n+' · '+(saved.records[n+'/Ergänzung']?.valid?ui.confirmed:ui.supported));
    if(hasApplication(n))paragraph(d,applicationStatus(n),'small');
    const original=el(d,'details');el(original,'summary',ui.family);paragraph(original,bank.cases[n].original);
    el(d,'strong',ui.addition);paragraph(d,bank.cases[n].addition);paragraph(d,bank.cases[n].connection,'small');
  }
  for(const n of names.slice(2)){
    const r=saved.records[n+'/Transfer'];
    if(r?.skipped || r?.valid)paragraph(d,n+' · '+applicationStatus(n),'small');
  }
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
    const field=bank.media.steps['LA-eigen'].field;
    paragraph(box,'„'+field+'“ · '+ui.digitalCheck).dataset.fieldref=field;
    paragraph(box,ui.choice);
    for(const [i,name] of [...names.slice(0,2),ui.both].entries())
      btn(box,name,'weight-'+i,()=>{p.choice=name;p.part=0;p.step='concern';p.feedback='';draw(true);});
  }else{
    const person=p.choice===ui.both?names[p.part]:p.choice,num=names.indexOf(person);
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
      thought(box,ui.openReason,p.reason||'',text=>p.reason=text,'check-reason',ui.continueReason,()=>{
        p.step='limit';draw(true);
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
        if(p.choice===ui.both&&p.part===0){p.part++;p.step='concern';p.other=false;p.alternate=false;draw(true);}
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
  if(at===2)facts(box);else facts(panel);
  if(at===0){
    paragraph(box,ui.before);btn(box,ui.openPersonal,'next',()=>go('laura',{at:1}),'primary');
  }else if(at===1){
    const step=paperOrder(box,'LA-eigen',{button:true});
    if(level==='Förder'){
      const d=el(box,'details');el(d,'summary',ui.examples);
      for(const [field,line] of bank.stems){el(d,'strong',field);paragraph(d,line);}
    }
    paragraph(box,ui.reviewSolo);
    btn(box,step.buttonText,'next',()=>openSection(step.nextId),'primary').dataset.return=step.nextId;
    evaluationHelp(box,record('Bewertung/Vorbereitung'));
  }else if(at===2)comparison(box);
  else{
    el(box,'h2',ui.paper);
    const p=saved.personal;
    el(box,'strong',level);
      paragraph(box,p?.step==='done'?p.choice+' · '+ui.personal:ui.noPast);
      if(p?.notes)for(const [name,note] of Object.entries(p.notes)){
        paragraph(box,name+' · '+(note.concern?ui.questionB:ui.questionA));
        paragraph(box,ui.limitChecked+' '+note.outcome,'small');
        if(note.reason){
          paragraph(box,ui.other+' · '+note.reason);
        }
        paragraph(box,ui.reasonOpen,'small');
      }
      if(p?.depth===5)paragraph(box,ui.timeHint);
    if(saved.records['Bewertung/Vorbereitung']?.depth===5)paragraph(box,ui.timeHint);
    if(saved.completedReview)paperOrder(box,'LA-abschluss');
    if(saved.completedReview)reserves(box);
    else{
      paragraph(box,ui.endRecovery,'small');
      btn(box,bank.evaluationSteps[2],'open-review',()=>openSection(bank.evaluationRecovery[2].id),'primary');
    }
  }
}
function pickerView(){
  heading(root,ui.where);chooseLevel(root);if(!level)return;
  if(saved.last)paragraph(root,ui.soloSession,'small');
  if(!additionalCases() && !saved.paperRecovery)
    btn(root,'Mein Pflichtteil ist auf Papier abgeschlossen','papierstand',()=>{saved.paperRecovery=true;draw();});
  const available=additionalCases()||saved.paperRecovery?names:names.slice(0,2);
  if(![...available,ui.theme].includes(picker.person))picker={person:'Mutter',step:'0'};
  select(root,ui.home,'person',[...available,ui.theme].map(k=>[k,k]),picker.person,v=>{picker={person:v,step:'0'};draw();});
  const n=picker.person,c=bank.cases[n];
  const steps=c?c.recovery.map((r,i)=>[i,c.recovery.filter(s=>s.section===r.section).length>1?r.section+' · '+r.part:r.section]):bank.evaluationSteps.map((v,i)=>[i,v]);
  if(c){
    const prefix=c.recovery[0].id.split('-')[0];
    steps.push(['transfer',bank.media.steps[prefix+'-ergebnis'].restartApplication.label]);
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
  const hint=screen==='picker'?'Suche den Abschnitt auf deinem Laufzettel und wähle ihn aus.':
    screen==='home'?'Wähle dein Niveau auf dem Laufzettel. Öffne dann die erste Nachricht.':
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
    if(data==='resources'){cards();return;}
    if(data==='home'||data==='recovery'){screen=data==='home'?'home':'picker';draw(true);}
  };
  port.postMessage({type:'ready',actions:[{id:'home',label:ui.home,icon:'folder'},{id:'resources',label:ui.cards,icon:'book'},{id:'recovery',label:ui.recovery,icon:'restart'}]});notify();
});
resetPath();draw();
