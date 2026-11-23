'use strict';
const bank=JSON.parse(document.querySelector('#bank').textContent);
const view=document.querySelector('#view'), card=document.querySelector('#card');
const sessions=new Map();
let level='', step, session;
function add(parent,tag,text) {
  const node=document.createElement(tag);node.textContent=text;parent.append(node);return node;
}
function button(parent,label,id,fn) {
  const b=add(parent,'button',label);b.id=id;b.onclick=fn;return b;
}
function heading(label) {
  view.replaceChildren();const h=add(view,'h1',label);h.tabIndex=-1;h.focus();
}
function overview(){
  heading(bank.title);
  add(view,'p','Wähle dein Niveau.');
  for(const tier of Object.keys(bank.levels)){
    const label=tier==='Foerder'?'Förder':tier;
    button(view,label,'tier-'+tier,()=>{level=tier;overview();}).setAttribute('aria-pressed',String(level===tier));
  }
  if(!level)return;
  if(sessions.has(level))button(view,'Weiterarbeiten','resume',()=>{session=sessions.get(level);draw();});
  button(view,'Neu beginnen','start',()=>begin(0));
  const picker=add(view,'details','');add(picker,'summary','Abschnitt auswählen');
  bank.stages.forEach((s,i)=>button(picker,s.id+' · '+s.title,'entry-'+s.id,()=>begin(i)));
}
function begin(index){
  session={index,history:[],read:false,code:'',draft:'',message:'',sent:false};
  sessions.set(level,session);draw();
}
function openCard(){
  const [method,part]=step.ref,c=bank.cards[method],passage=c.sections[part];
  document.querySelector('#cardTitle').textContent=c.title+' · '+passage.title;
  document.querySelector('#passage').textContent=['Foerder','ESA'].includes(level)?passage.shortText:passage.text;
  card.showModal();
}
function submit(code){
  if(session.sent || session.draft || !session.read)return;
  const i='ABC'.indexOf(code);
  if(code.length!==1 || i<0){session.message='Trage einen Buchstaben von A bis C ein.';draw();return;}
  session.message=step.feedback[i];
  if(code===step.code)session.draft=code;
  draw();
}
function draw(){
  step=bank.stages[session.index];
  heading(step.id+' · '+step.title+' · '+(level==='Foerder'?'Förder':level));
  if(session.history.length){
    const h=add(view,'details','');add(h,'summary','Gesprächsverlauf');
    for(const record of session.history)for(const text of record)add(h,'p',text);
  }
  const chat=add(view,'blockquote','');add(chat,'strong','Nachricht im Übungschat');add(chat,'p',step.claim);
  if(session.sent){
    add(view,'strong','Deine Nachricht');add(view,'p',step.answers['ABC'.indexOf(session.draft)]);
    add(view,'blockquote',step.reply).setAttribute('role','status');
    const last=session.index===bank.stages.length-1;
    button(view,last?'Übung abschließen':'Weiter im Chat','next',()=>{
      if(last){sessions.delete(level);overview();return;}
      Object.assign(session,{index:session.index+1,read:false,code:'',draft:'',message:'',sent:false});draw();
    });return;
  }
  if(!session.read)add(view,'p','Was vermutest du? Prüfe deinen Gedanken mit der Karte.');
  button(view,step.cardPrompt,'source',openCard);
  if(!session.read)return;
  if(session.draft){
    add(view,'strong','Deine Antwort');add(view,'p',step.answers['ABC'.indexOf(session.draft)]);
    button(view,'Auswahl ändern','edit',()=>{session.draft='';session.message='';draw();});
    button(view,'Nachricht senden','send',()=>{
      if(session.sent || !session.draft)return;
      session.sent=true;
      session.history.push([step.claim,step.answers['ABC'.indexOf(session.draft)],step.reply]);
      draw();
    }).className='primary';return;
  }
  add(view,'p',step.paper?.[level] || bank.levels[level]);
  const answers=add(view,'div','');answers.className='answers';
  const paper=Boolean(step.paper?.[level]);
  if(paper){
    const details=add(view,'details','');add(details,'summary','Laufzettel nicht zur Hand?');
    step.answers.forEach((answer,i)=>add(details,'p','ABC'[i]+' · '+answer));
    add(view,'p',bank.return);
    const label=add(view,'label','Prüfcode '),input=add(label,'input','');input.id='code';input.value=session.code;
    input.oninput=()=>{session.code=input.value;session.message='';document.querySelector('#feedback').textContent='';};
    button(view,'Code prüfen','check',()=>submit(session.code.trim().toUpperCase()));
  }else{
    for(const key of level==='Foerder'?step.short:'ABC'){
      button(answers,step.answers['ABC'.indexOf(key)],'answer-'+key,()=>submit(key));
    }
  }
  const feedback=add(view,'p',session.message);feedback.id='feedback';feedback.setAttribute('role','status');
}
document.querySelector('#home').onclick=overview;
document.querySelector('#back').onclick=()=>card.close();
card.onclose=()=>{session.read=true;draw();document.querySelector('#source')?.focus();};
overview();
