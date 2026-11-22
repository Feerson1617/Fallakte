'use strict';
const bank=JSON.parse(document.querySelector('#bank').textContent);
const desk=document.querySelector('#desk'),dialog=document.querySelector('dialog'),sessions=new Map();
let port,state,tier;
const stage=()=>bank.stages[state.index];
function add(parent,tag,text=''){const e=document.createElement(tag);e.textContent=text;parent.append(e);return e;}
function btn(parent,label,id,action){const b=add(parent,'button',label);b.id=id;b.onclick=action;return b;}
function fresh(index,history=[]){return {index,history,choice:'',code:'',result:'',valid:false,sent:false,asked:'',help:0};}
function save(next){state=next;sessions.set(tier,next);}
function clearChoice(key){Object.assign(state,{choice:key,code:'',result:'',valid:false,asked:'',help:0});draw();}
function resource(title,render){
  document.querySelector('#resource').textContent=title;
  const body=document.querySelector('#reading');body.replaceChildren();render(body);
  if(!dialog.open)dialog.showModal();
}
function source(){
  const s=stage(),small=['Foerder','ESA'].includes(tier);
  if(!s.choices || !Object.keys(s.choices).length){
    resource('Forschungsmaterial',body=>{
      if(small)add(body,'p',s.shortSource);
      const article=bank.articles[tier];
      const more=add(body,'details');more.open=!small;add(more,'summary',article.title);
      article.paragraphs.forEach(p=>add(more,'p',p));
      for(const [word,meaning] of Object.entries(article.glossary))add(more,'p',word+' · '+meaning);
      for(const study of bank.studies){
        const d=add(body,'details');add(d,'summary',study.label);
        for(const text of [study.body,study.meaning,study.source])add(d,'p',text);
      }
    });return;
  }
  const [m,key]=currentCheck().ref,c=bank.cards[m],section=c.sections[key];
  resource(c.title+' · '+section.title,body=>{
    add(body,'p',section[small?'shortText':'text']);const full=add(body,'details');add(full,'summary','Ganze Karte lesen');
    for(const part of Object.values(c.sections)){add(full,'h2',part.title);add(full,'p',part.text);}
  });
}
function currentCheck(){return stage().checks?.[state.choice] || stage();}
function inspect(code){
  if(state.sent || state.valid)return;
  const check=currentCheck();const idx='ABC'.indexOf(code);
  if(code.length!==1 || idx<0){state.result='Gib einen Buchstaben von A bis C ein.';}
  else{
    state.result=check.feedback[idx];
    if(code===check.code){
      const rejected=Object.keys(stage().choices).length && !stage().allowed.includes(state.choice);
      if(rejected)state.result+=' '+stage().replies[state.choice]+' Wähle deinen Vorschlag neu.';
      else state.valid=true;
    }
  }
  draw();
}
function draw(){
  const s=stage(),check=currentCheck(),hasChoice=Object.keys(s.choices).length>0;
  desk.replaceChildren();const h=add(desk,'h1',bank.person+' '+(state.index+1)+' von '+bank.stages.length);h.id='step';
  add(desk,'p',s.title+' · '+bank.levels[tier]);
  if(state.history.length){const old=add(desk,'details');add(old,'summary','Gesprächsverlauf');state.history.forEach(x=>add(old,'p',x));}
  if(state.direct && s.previousFacts.length){const facts=add(desk,'details');add(facts,'summary','Bisher im Fall');s.previousFacts.forEach(text=>add(facts,'p',text));}
  add(desk,'blockquote',s.message[tier].join(' '));
  if(state.sent){
    add(desk,'p',state.reply);
    btn(desk,state.index+1===bank.stages.length?'Zur Fallübersicht':'Weiter im Gespräch','next',()=>{
      if(state.index+1===bank.stages.length){sessions.delete(tier);port.postMessage({type:'home'});return;}
      save(fresh(state.index+1,state.history));draw();
    }).className='primary';return;
  }
  if(hasChoice && !state.choice){
    add(desk,'h2','Welchen Vorschlag machst du?');
    const box=add(desk,'div');box.className='choices';
    for(const [key,label] of Object.entries(s.choices))btn(box,label,'method-'+key,()=>clearChoice(key));
  }else{
    if(hasChoice){add(desk,'strong',s.choices[state.choice]).id='selected';btn(desk,'Auswahl ändern','edit',()=>clearChoice(''));}
    if(!state.valid){
      add(desk,'p',s.task[tier]);
      if(['MSA','AHR'].includes(tier)){
        add(desk,'p',s.paper[tier].replace(' '+s.task[tier],''));
        const d=add(desk,'details');add(d,'summary','Laufzettel nicht zur Hand?');
        check.answers.forEach((a,i)=>add(d,'p','ABC'[i]+' · '+a));add(d,'p',s.return);
        const input=add(add(desk,'label','Prüfcode '),'input');input.id='code';input.value=state.code;
        input.oninput=()=>{state.code=input.value;state.result='';document.querySelector('#feedback').textContent='';};
        btn(desk,'Code prüfen','check',()=>inspect(state.code.trim().toUpperCase()));
      }else{
        for(const k of tier==='Foerder'?check.short:'ABC')btn(desk,check.answers['ABC'.indexOf(k)],'answer-'+k,()=>inspect(k)).className='answer';
      }
    }
    add(desk,'p',state.result).id='feedback';document.querySelector('#feedback').setAttribute('role','status');
    if(state.valid)btn(desk,'Nachricht senden','send',()=>{
      if(!state.valid || state.sent)return;state.sent=true;
      state.reply=s.replies[state.choice || 'DONE'];
      state.history.push(s.message[tier].join(' '),(s.choices[state.choice]||'')+' '+check.answers['ABC'.indexOf(check.code)],state.reply);draw();
    }).className='primary';
  }
  btn(desk,hasChoice?'Infokarte öffnen':'Artikel und Studien öffnen','source',source);
  const hints=state.choice?s.hints[state.choice]:s.helpBefore;
  btn(desk,'Hilfe','help',()=>resource('Hilfe',body=>{for(const hint of hints)add(body,'p',hint);}));
  const qs=check.questions || s.questions;
  if(qs.length)btn(desk,'Rückfrage an '+bank.person,'ask',()=>resource('Rückfrage',body=>{
    for(const [q,a] of qs)btn(body,q,'q'+body.childElementCount,()=>{state.asked=q+' '+a;dialog.close();draw();});
  }));
  if(state.asked)add(desk,'p',state.asked);
  port?.postMessage({type:'status',person:bank.person,tier,abschnitt:state.index+1,view:'room'});
}
document.querySelector('#back').onclick=()=>dialog.close();
addEventListener('message',e=>{
  if(e.source!==parent || e.data!=='reserve0212:verbinden' || !e.ports[0])return;
  port?.close();port=e.ports[0];
  port.onmessage=({data})=>{
    if(data.type==='cards' && state){source();return;}
    if(data.type!=='open'||data.person!==bank.person||!Object.hasOwn(bank.levels,data.tier))return;
    tier=data.tier;
    const previous=sessions.get(tier);
    const returning=data.abschnitt===undefined && previous;
    if(dialog.open && (!returning || state!==previous))dialog.close();
    save(returning?previous:fresh((data.abschnitt||1)-1));
    if(data.abschnitt!==undefined)state.direct=true;
    draw();
  };
  port.postMessage({type:'ready'});
});
