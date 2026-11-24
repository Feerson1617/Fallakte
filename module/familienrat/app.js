'use strict';
const bank = JSON.parse(document.getElementById('material').textContent);
const portraits = JSON.parse(document.getElementById('portraits').textContent);
const ui = bank.ui, names = Object.keys(bank.cases);
const root = document.getElementById('app'), dialog = document.getElementById('dialog');
const body = document.getElementById('dialog-body');
let port, screen = 'home', members = ['', ''], current, saved, opener;
let picker = {person:'Mutter', step:'0'};
const teams = new Map();
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
function activate(){
  const key=JSON.stringify(members);
  if(!teams.has(key)) teams.set(key,{records:{},complete:{},personal:[],last:null});
  saved=teams.get(key);
}
const levels=()=>members.filter(Boolean);
const low=()=>levels().slice().sort((a,b)=>bank.levels.indexOf(a)-bank.levels.indexOf(b))[0];
const high=()=>levels().slice().sort((a,b)=>bank.levels.indexOf(b)-bank.levels.indexOf(a))[0];
const advanced=t=>bank.levels.indexOf(t)>=2;
function go(type, fields={}) {
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
    status:screen==='work'? (current.person||ui.theme)+' · '+levels().join(' / '):''});
}
function popup(title,content,from){
  if(!dialog.open)opener=from || document.activeElement;
  document.getElementById('dialog-title').textContent=title;
  body.replaceChildren();content(body);dialog.scrollTop=0;
  if(!dialog.open)dialog.showModal();
}
document.getElementById('dismiss').textContent=ui.close;
document.getElementById('dismiss').onclick=()=>dialog.close();
dialog.onclose=()=>{if(opener?.isConnected)opener.focus({preventScroll:true});};
function cards(index){
  popup(ui.cards,box=>{
    bank.cards.forEach((c,i)=>{
      const details=el(box,'details');details.open=i===index;
      el(details,'summary',c.title);paragraph(details,(low()==='Förder'||low()==='ESA')?c.short:c.text);
      if(c.short!==c.text && !advanced(low())){const more=el(details,'details');el(more,'summary',ui.deeper);paragraph(more,c.text);}
    });
  });
}
function help(task,r){
  let tier=task.personalTier || low();
  function show(depth){
    if(!r.valid && r.step!=='done')r.depth=Math.max(r.depth,depth);
    else r.laterDepth=Math.max(r.laterDepth||0,depth);
    popup(ui.helpTitle+' '+depth+' / 5',box=>{
      if(!task.personalTier && levels().length===2 && low()!==high())
        select(box,ui.helpFor,'help-tier',Array.from(new Set(levels())).map(t=>[t,t]),tier,v=>{tier=v;show(depth);});
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
function message(box,name,text){
  profile(box,name);
  for(const line of sentences(text))paragraph(box,line);
}
function team(box){
  const row=el(box,'div',undefined,'row');
  const options=bank.levels.map(t=>[t,t]);
  members.forEach((member,i)=>select(row,i?ui.two:ui.one,'level-'+i,
    [['',i?ui.solo:ui.choose],...options],member,value=>{
      members[i]=value;activate();draw();document.getElementById('level-'+i).focus();
    }));
}
function tools(box,task,r,card){
  const row=el(box,'div',undefined,'tools');
  const guided=['Ergänzung','Reichweite','Transfer'].includes(task.id) && !advanced(low());
  btn(row,ui.help,'help',()=>help(task,r));
  btn(row,guided?bank.cards[card].title:ui.cards,'cards',()=>cards(guided?card:undefined));
  btn(row,ui.terms,'terms',()=>popup(ui.terms,b=>Object.entries(bank.definitions).forEach(([k,v])=>{el(b,'strong',k);paragraph(b,v);})));
}
function showHome(){
  const layout=el(root,'div',undefined,'split'), aside=el(layout,'aside',undefined,'msg');
  message(aside,'Laura',bank.opening);
  const box=el(layout,'section',undefined,'card');
  heading(box,ui.openingTitle);team(box);
  if(!members[0])return;
  if(saved.last)btn(box,ui.resume,'resume',()=>{current=saved.last;screen='work';draw(true);},'primary');
  btn(box,saved.last?ui.fresh:ui.start,'start',()=>{
    if(!saved.last){go('case',{person:'Mutter',at:0});return;}
    popup(ui.fresh,content=>{
      paragraph(content,ui.replaceTeam);
      btn(content,ui.fresh,'confirm-start',()=>{
        dialog.close();teams.delete(JSON.stringify(members));activate();go('case',{person:'Mutter',at:0});
      });
    });
  },saved.last?'':'primary');
  if(saved.complete.Mutter)btn(box,bank.cases.Freundin.titles[0],'friend',()=>go('case',{person:'Freundin',at:0}));
  btn(box,ui.switch,'jump',()=>go('laura',{at:0}));
  if(saved.completedReview)reserves(box);
}
function reserves(box){
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
  const orders=levels();
  orders.forEach((tier,i)=>{
    if(orders.length>1)el(panel,'strong',(i?ui.two:ui.one)+' · '+tier);
    const order=paragraph(panel,step.orders[tier].screen);
    order.className='paper-order';order.dataset.member=String(i);order.dataset.level=tier;
  });
  if(support)paragraph(panel,step.support);
  if(!button){
    const handoff=paragraph(panel,step.returnText,'small');
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
      if(task.evidenceSentences.includes(i)){r.source=i;draw();root.querySelector('textarea').focus();}
      else{r.wrong=true;feedback.textContent=ui.sourceRetry;}
    });
  });
}
function options(box,task,r,onDone,application=false){
  const row=el(box,'div',undefined,'answers');
  // Rotate in a stable order. A pupil may return to the same choice after opening a card.
  const shift=Array.from(task.prompt).reduce((sum,c)=>sum+c.charCodeAt(0),0)%task.answers.length;
  const arranged=task.answers.slice(shift).concat(task.answers.slice(0,shift));
  const compact=low()==='Förder' && task.shortOptions;
  let extra;
  if(compact && arranged.length>2){
    extra=el(box,'details');extra.id='more-options';el(extra,'summary',ui.moreOptions);
  }
  for(const o of arranged){
    const index=task.answers.indexOf(o);
    const deeper=application && advanced(low()) && o.advancedText;
    const target=extra && !compact.includes(index)?extra:row;
    const b=btn(target,deeper?o.advancedText:o.text,'answer-'+index,()=>{
      r.feedback=deeper?o.advancedFeedback:o.feedback;r.valid=o.ok;r.selected=index;if(!o.ok)r.wrong=true;
      if(o.revealsSolution)r.solutionShown=true;
      if(application){r.finished=o.ok;r.skipped=false;}
      draw();
      const fb=document.getElementById('response');fb.focus({preventScroll:true});fb.scrollIntoView({block:'nearest'});
    });
    if(target===extra && r.selected===index)extra.open=true;
    b.disabled=r.valid||r.finished===true;b.setAttribute('aria-pressed',String(r.selected===index));
  }
  if(r.feedback){const fb=paragraph(box,r.feedback,r.valid?'feedback':'feedback retry');fb.id='response';fb.tabIndex=-1;fb.setAttribute('role','status');}
  if(r.valid && !application){
    paragraph(box,task.id==='Reichweite'?ui.limitChecked+' '+status(r):status(r),'tag');
    btn(box,ui.next,'next',onDone,'primary');
  }
}
function originalPanel(layout,person,c,hideAddition){
  const panel=el(layout,'aside',undefined,'msg');message(panel,person,c.original);
  const r=saved.records[person+'/Ergänzung'];
  if(r?.valid && !hideAddition){el(panel,'h2',ui.addition);paragraph(panel,c.addition);paragraph(panel,c.connection,'small');}
  return panel;
}
function caseView(){
  const {person,at}=current,c=bank.cases[person],idx=names.indexOf(person);
  const paper=at===c.tasks.length+1, transfer=paper && hasApplication(person);
  const application=transfer?record(person+'/Transfer'):null;
  heading(root,c.recovery[at].section).dataset.section=c.recovery[at].id;
  const layout=el(root,'div',undefined,'split');originalPanel(layout,person,c,transfer && !application.finished);
  const box=el(layout,'section',undefined,'card');
  const advance=()=>go('case',{person,at:at+1});
  if(at===0){
    if(person==='Freundin' && levels().length===2)paragraph(box,ui.role);
    paragraph(box,bank.known);
    btn(box,ui.read,'next',advance,'primary');
  }else if(!paper){
    const task=c.tasks[at-1],r=record(person+'/'+task.id);
    const adding=task.id==='Ergänzung';
    if(adding && r.selected===undefined && !r.compared)paperOrder(box,c.recovery[0].id.split('-')[0]+'-erst');
    el(box,'h2',task.prompt);
    const phase=adding?'Ergänzung':'analyse';
    if(advanced(high())){
      paragraph(box,high()+' · '+bank.levelPrompts[high()][phase],'small');
      if(adding)paragraph(box,bank.caseReflection[person]);
      draft(box,task,r,c);
    }else if(adding)paragraph(box,bank.levelPrompts[low()][phase],'small');
    if(!advanced(high())||r.compared)options(box,task,r,advance);
    tools(box,task,r,idx);
  }else{
    if(transfer){
      const task=c.transfer;box.dataset.application=task.sectionId;
      if(!application.finished)paragraph(box,ui.helpBeforePaper,'small');
      el(box,'h2',advanced(low()) && task.advancedPrompt?task.advancedPrompt:task.prompt);
      if(!application.finished && advanced(high()) && !advanced(low()) && task.advancedPrompt)paragraph(box,high()+' · '+ui.mixedTransfer,'small');
      options(box,task,application,null,true);
      if(!application.finished){
        tools(box,task,application,idx);
        btn(box,ui.switch,'jump',()=>{application.skipped=true;go('laura',{at:0});});
        return;
      }
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
    btn(box,step.returnText,'next',()=>{
      if(saved.records[person+'/Ergänzung']?.valid)saved.complete[person]=true;
      openSection(step.nextId);
    },'primary').dataset.return=step.nextId;
    const matrix=el(box,'details');matrix.dataset.digital='matrix';
    el(matrix,'summary',ui.readMatrix);
    for(const [key,value] of Object.entries(c.matrix)){el(matrix,'strong',key);paragraph(matrix,value);}
  }
  if(idx<2){
    const bar=el(root,'div',undefined,'tools');btn(bar,ui.switch,'jump',()=>go('laura',{at:0}));
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
  btn(box,ui.help,'help',()=>help({hints:bank.evaluationHints,helpByLevel:bank.evaluationHelpByLevel,personalTier:current.at===2?members[current.individual||0]:null},r));
}
function personal(index){
  return saved.personal[index] ||= {choice:'',part:0,step:'choice',feedback:'',notes:{},depth:0};
}
const reviewText=i=>bank.review[i][1].split('“')[0];
function comparison(box,index){
  const p=personal(index);
  el(box,'h2',(index?ui.two:ui.one)+' · '+members[index]);
  const end=()=>{
    p.step='done';
    const missing=levels().findIndex((_,i)=>saved.personal[i]?.step!=='done');
    saved.completedReview=missing<0;
    if(saved.completedReview)go('laura',{at:3});
    else go('laura',{at:2,individual:missing});
  };
  if(p.choice){
    btn(box,ui.editWeight,'edit-weight',()=>{
      p.step='choice';saved.paperRecovery=false;p.choice='';p.part=0;p.notes={};p.reason='';p.alternate=false;p.other=false;p.feedback='';
      // Recheck the selection while keeping any support this person already received.
      for(const [key,r] of Object.entries(saved.records)){
        if(key.startsWith('Bewertung/'+index+'/'))Object.assign(r,{valid:false,selected:undefined,feedback:''});
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
        if(i!==p.concern)record('Bewertung/'+index+'/'+person+'/'+p.concern).wrong=true;
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
      const r=record('Bewertung/'+index+'/'+person+'/'+target),task=bank.limits[target];
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
      tools(box,{...task,personalTier:members[index]},r,target);return;
    }
    if(p.feedback){const msg=paragraph(box,p.feedback,'feedback retry');msg.setAttribute('role','status');}
  }
  evaluationHelp(box,p);
}
function lauraView(){
  const at=current.at;heading(root,bank.evaluationSteps[at]).dataset.section=bank.evaluationRecovery[at].id;
  const layout=el(root,'div',undefined,'split'),panel=el(layout,'aside',undefined,'msg');
  message(panel,'Laura',bank.second);facts(panel);
  const box=el(layout,'section',undefined,'card');
  if(at===0){
    paragraph(box,ui.before);btn(box,ui.openPersonal,'next',()=>go('laura',{at:1}),'primary');
  }else if(at===1){
    const step=paperOrder(box,'LA-eigen',{button:true});
    if(levels().includes('Förder')){
      const d=el(box,'details');el(d,'summary',ui.examples);
      for(const [field,line] of bank.stems){el(d,'strong',field);paragraph(d,line);}
    }
    paragraph(box,levels().length===2?ui.reviewEach:ui.reviewSolo);
    btn(box,step.returnText,'next',()=>openSection(step.nextId),'primary').dataset.return=step.nextId;
    evaluationHelp(box,record('Bewertung/Vorbereitung'));
  }else if(at===2)comparison(box,current.individual||0);
  else{
    el(box,'h2',ui.paper);
    levels().forEach((t,i)=>{
      const p=saved.personal[i];el(box,'strong',(i?ui.two:ui.one)+' · '+t);
      paragraph(box,p?.step==='done'?p.choice+' · '+ui.personal:ui.noPast);
      if(p?.notes)for(const [name,note] of Object.entries(p.notes)){
        paragraph(box,name+' · '+(note.concern?ui.questionB:ui.questionA));
        paragraph(box,ui.limitChecked+' '+note.outcome,'small');
        if(note.reason){
          paragraph(box,ui.other+' · '+note.reason);
        }
        paragraph(box,ui.reasonOpen,'small');
      }
      if(p?.depth===5||saved.records['Bewertung/Vorbereitung']?.depth===5)paragraph(box,ui.timeHint);
    });
    if(saved.completedReview || saved.paperRecovery)paperOrder(box,'LA-abschluss');
    if(saved.completedReview)reserves(box);
    else{
      paragraph(box,ui.endRecovery,'small');
      btn(box,bank.evaluationSteps[2],'open-review',()=>openSection(bank.evaluationRecovery[2].id),'primary');
      if(!saved.paperRecovery)btn(box,ui.paperReady,'paper-ready',()=>{saved.paperRecovery=true;draw(true);});
    }
  }
}
function pickerView(){
  heading(root,ui.where);team(root);if(!members[0])return;
  if(saved.last)paragraph(root,ui.inSession,'small');
  select(root,ui.home,'person',[...names,ui.theme].map(k=>[k,k]),picker.person,v=>{picker={person:v,step:'0'};draw();});
  const n=picker.person,c=bank.cases[n];
  const steps=c?c.recovery.map((r,i)=>[i,c.recovery.filter(s=>s.section===r.section).length>1?r.section+' · '+r.part:r.section]):bank.evaluationSteps.map((v,i)=>[i,v]);
  if(c){
    const prefix=c.recovery[0].id.split('-')[0];
    steps.push(['transfer',bank.media.steps[prefix+'-ergebnis'].restartApplication.label]);
  }
  select(root,ui.selectSection,'entry',steps,picker.step,v=>{picker.step=v;draw();});
  if(!c && Number(picker.step)===2 && members[1]){
    select(root,ui.apply,'member',levels().map((v,i)=>[i,(i?ui.two:ui.one)+' · '+v]),picker.individual||0,v=>picker.individual=Number(v));
  }
  btn(root,ui.resumeHere,'open-entry',()=>{
    if(c && picker.step==='transfer'){
      record(n+'/Transfer').resumed=true;
      go('case',{person:n,at:c.tasks.length+1});return;
    }
    const at=Number(picker.step);
    if(c)go('case',{person:n,at});else go('laura',{at,individual:members[1]?picker.individual||0:0});
  },'primary');
}
function draw(focus=false){
  root.replaceChildren();
  if(screen==='home')showHome();else if(screen==='picker')pickerView();else if(current.type==='case')caseView();else lauraView();
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
activate();draw();
