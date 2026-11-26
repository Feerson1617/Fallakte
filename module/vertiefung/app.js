'use strict';
const bank=JSON.parse(document.querySelector('#bank').textContent);
const desk=document.querySelector('#desk'),dialog=document.querySelector('dialog'),sessions=new Map();
let port,state,tier;
const lower=()=>tier==='Foerder' || tier==='ESA';
const readingTrail=[];
const stage=()=>bank.stages[state.index];
function add(parent,tag,text=''){const e=document.createElement(tag);e.textContent=text;parent.append(e);return e;}
function btn(parent,label,id,action){const b=add(parent,'button',label);b.id=id;b.onclick=action;return b;}
function fresh(index,history=[]){return {index,history,choice:'',code:'',result:'',valid:false,sent:false,asked:'',read:false,previous:''};}
function save(next){state=next;sessions.set(tier,next);}
function clearChoice(key){
  if(!key && state.choice)state.previous=state.choice;
  Object.assign(state,{choice:key,code:'',result:'',valid:false,asked:''});draw();
}
function resource(title,render){
  const heading=document.querySelector('#resource'),body=document.querySelector('#reading');
  if(dialog.open){
    if(heading.textContent===title)return;
    readingTrail.push({title:heading.textContent,nodes:[...body.childNodes],scroll:dialog.scrollTop});
  }
  heading.textContent=title;body.replaceChildren();render(body);dialog.scrollTop=0;
  if(!dialog.open)dialog.showModal();
}
function source(){
  const s=stage(),small=['Foerder','ESA'].includes(tier);
  if(!s.choices || !Object.keys(s.choices).length){
    state.read=true;
    resource('Forschungsmaterial',body=>{
      if(small)add(body,'p',s.shortSource);
      const article=bank.articles[tier];
      const more=add(body,'details');more.open=!small && state.index===1;add(more,'summary',article.title);
      article.paragraphs.forEach(p=>add(more,'p',p));
      for(const [word,meaning] of Object.entries(article.glossary))add(more,'p',word+' · '+meaning);
      for(const study of bank.studies){
        const d=add(body,'details');d.open=!small && state.index===2 && study===bank.studies[1];add(d,'summary',study.label);
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
  if(state.sent || state.valid || conflict() || needsSource())return;
  const check=currentCheck();const idx='ABC'.indexOf(code);
  if(code.length!==1 || idx<0){state.result='Gib einen Buchstaben von A bis C ein.';}
  else{
    state.result=check.feedback[idx];
    state.valid=code===check.code;
  }
  draw();
}
function conflict(){return state.choice && stage().conflicts?.[state.choice];}
function needsSource(){return !Object.keys(stage().choices).length && !lower() && !state.read;}
function choices(s){
  const entries=Object.entries(s.choices);
  const group=(parent,set)=>{const box=add(parent,'div');box.className='choices';
    for(const [k,v] of set)btn(box,v,'method-'+k,()=>clearChoice(k));
  };
  if(lower()){
    const first=[...new Set([state.previous,...s.primary[tier]].filter(Boolean))].slice(0,3);
    group(desk,entries.filter(([k])=>first.includes(k)));
    const extra=add(desk,'details');extra.id='more';add(extra,'summary','Weitere Vorschläge');
    group(extra,entries.filter(([k])=>!first.includes(k)));
  }else{
    for(const combo of [false,true]){
      add(desk,'h3',combo?'Kombinationen':'Einzelmethoden');
      group(desk,entries.filter(([k])=>k.includes('+')===combo));
    }
  }
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
      const next=fresh(state.index+1,state.history);next.previous=state.choice;save(next);draw();
    }).className='primary';return;
  }
  if(hasChoice && !state.choice){
    add(desk,'h2','Welchen Vorschlag machst du?');
    choices(s);
  }else{
    if(hasChoice){add(desk,'strong',s.choices[state.choice]).id='selected';btn(desk,'Auswahl ändern','edit',()=>clearChoice(''));}
    if(!hasChoice && lower()){add(desk,'strong','Aus der Quelle');add(desk,'blockquote',s.shortSource);}
    if(needsSource())add(desk,'p',state.index===1?'Lies den Artikel. Welche Aussage ist belegt?':'Lies Studie B. Was wurde tatsächlich untersucht?');
    if(!state.valid && !conflict() && !needsSource()){
      add(desk,'p',s.task[tier]);
      if(['MSA','AHR'].includes(tier)){
        const paper=s.paper[tier].replace(' '+s.task[tier],'');
        const celina=bank.person==='Celina';
        add(desk,'p',paper+(celina
          ? ' Lies A, B und C hier am iPad. Schreibe deine Begründung auf den Celina-Bogen. Kreise dort den Buchstaben der passenden Aussage ein.'
          : ' Schreibe deine Begründung auf. Kreise die richtige Aussage ein.'));
        const list=add(desk,celina?'div':'details');
        if(!celina)add(list,'summary','Zusatzbogen nicht zur Hand?');
        check.answers.forEach((answer,i)=>add(list,'p','ABC'[i]+' · '+answer));
        add(desk,'p',s.return);
        const input=add(add(desk,'label','Prüfcode '),'input');input.id='code';input.value=state.code;
        input.oninput=()=>{state.code=input.value;state.result='';document.querySelector('#feedback').textContent='';};
        btn(desk,'Code prüfen','check',()=>inspect(state.code.trim().toUpperCase()));
      }else{
        for(const k of tier==='Foerder'?check.short:'ABC')btn(desk,check.answers['ABC'.indexOf(k)],'answer-'+k,()=>inspect(k)).className='answer';
      }
    }
    add(desk,'p',conflict()?.[lower()?'short':'full'] || state.result).id='feedback';document.querySelector('#feedback').setAttribute('role','status');
    if(state.valid)btn(desk,'Nachricht senden','send',()=>{
      if(!state.valid || state.sent || conflict() || needsSource())return;state.sent=true;
      if(bank.person==='Tom' && state.index===bank.stages.length-1)port.postMessage({type:'completed',person:bank.person,tier});
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
function leaveReading(){
  const prior=readingTrail.pop();
  if(!prior){dialog.close();return;}
  document.querySelector('#resource').textContent=prior.title;
  document.querySelector('#reading').replaceChildren(...prior.nodes);dialog.scrollTop=prior.scroll;
}
document.querySelector('#back').onclick=leaveReading;
dialog.oncancel=e=>{e.preventDefault();leaveReading();};
dialog.onclose=()=>{readingTrail.length=0;if(document.querySelector('#source') && !state.sent && !Object.keys(stage().choices).length && state.read){draw();document.querySelector('#source')?.focus();}};
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
