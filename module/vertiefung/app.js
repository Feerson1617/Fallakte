'use strict';
const bank=JSON.parse(document.querySelector('#bank').textContent);
const desk=document.querySelector('#desk'),dialog=document.querySelector('dialog'),sessions=new Map();
let port,state,tier;
const lower=()=>tier==='Foerder' || tier==='ESA';
const readingTrail=[];
const stage=()=>bank.stages[state.index];
function add(parent,tag,text=''){const e=document.createElement(tag);e.textContent=text;parent.append(e);return e;}
function btn(parent,label,id,action){const b=add(parent,'button',label);b.id=id;b.onclick=action;return b;}
function fresh(index,history=[]){return {index,history,choice:'',reason:'',drafts:{},compared:false,result:'',valid:false,sent:false,asked:'',read:false,previous:''};}
function save(next){state=next;sessions.set(tier,next);}
function clearChoice(key){
  if(!key && state.choice)state.previous=state.choice;
  if(state.choice)state.drafts[state.choice]=state.reason;
  Object.assign(state,{choice:key,reason:state.drafts[key]||'',compared:false,result:'',valid:false,asked:''});draw();
}
function resource(title,render){
  const heading=document.querySelector('#resource'),body=document.querySelector('#reading');
  if(dialog.open){
    if(heading.textContent===title)return;
    if(!(title.startsWith('Hilfe') && heading.textContent.startsWith('Hilfe')))readingTrail.push({title:heading.textContent,nodes:[...body.childNodes],scroll:dialog.scrollTop});
  }
  heading.textContent=title;body.replaceChildren();render(body);dialog.scrollTop=0;
  if(!dialog.open)dialog.showModal();dialog.dataset.hilfe=String(title.startsWith('Hilfe'));Arbeitsplatz.prepareDialog(dialog,body);
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
  if(!state.choice){
    resource('Infokarten',box=>{
      for(const [m,c] of Object.entries(bank.cards))btn(box,c.title,'karte-'+m,()=>resource(c.title,b=>{
        for(const part of Object.values(c.sections)){add(b,'h2',part.title);add(b,'p',part.levels[tier]);}
      }));
    });return;
  }
  const [m,key]=currentCheck().ref,c=bank.cards[m],section=c.sections[key];
  resource(c.title,body=>{
    add(body,'h3',section.title);
    add(body,'p',section.levels?.[tier] || section[small?'shortText':'text']);const full=add(body,'details');add(full,'summary','Ganze Karte lesen');
    for(const part of Object.values(c.sections)){add(full,'h2',part.title);add(full,'p',part.levels?.[tier]||part.text);}
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
function choices(s,work){
  const entries=Object.entries(s.choices);
  const group=(parent,set)=>{const box=add(parent,'div');box.className='choices';
    for(const [k,v] of set)btn(box,v,'method-'+k,()=>clearChoice(k));
  };
  if(lower()){
    const first=[...new Set([state.previous,...s.primary[tier]].filter(Boolean))].slice(0,3);
    group(work,entries.filter(([k])=>first.includes(k)));
    const extra=add(work,'details');extra.id='more';add(extra,'summary','Weitere Vorschläge');
    group(extra,entries.filter(([k])=>!first.includes(k)));
  }else{
    for(const combo of [false,true]){
      add(work,'h3',combo?'Kombinationen':'Einzelmethoden');
      group(work,entries.filter(([k])=>k.includes('+')===combo));
    }
  }
}
function draw(){
  const s=stage(),check=currentCheck(),hasChoice=Object.keys(s.choices).length>0;
  desk.replaceChildren();const h=add(desk,'h1',bank.person+' '+(state.index+1)+' von '+bank.stages.length);h.id='step';
  add(desk,'p',s.title+' · '+bank.levels[tier]);
  const layout=add(desk,'div');layout.className='split';
  const chat=add(layout,'aside'),work=add(layout,'section');
  chat.setAttribute('aria-label','Gespräch mit '+bank.person);
  work.setAttribute('aria-label','Deine Aufgabe');
  const past=state.sent?state.history.slice(0,-3):state.history;
  function note(i){if(state.notes?.[i]){const d=add(chat,'details');add(d,'summary','Dein eigener Grund · fachlich ungeprüft');add(d,'p',state.notes[i]);}}
  for(const [i,text] of past.entries()){note(i);add(chat,'strong',i%3===1?'Du':bank.person);add(chat,'p',text);}
  if(state.direct && s.previousFacts.length){const facts=add(chat,'details');add(facts,'summary','Bisher im Fall');s.previousFacts.forEach(text=>add(facts,'p',text));}
  add(chat,'strong',bank.person);add(chat,'blockquote',s.message[tier].join(' '));
  const room=()=>Arbeitsplatz.setup(desk,work,chat,h,work.querySelector('#help'),b=>resource('Hilfe',box=>add(box,'p','Lies die Antwort. Tippe dann auf Weiter.')));
  if(state.sent){
    note(state.history.length-2);add(chat,'strong','Du');add(chat,'p',state.history.at(-2));
    add(chat,'strong',bank.person);add(chat,'p',state.reply);
    btn(work,state.index+1===bank.stages.length?'Zur Fallübersicht':'Weiter im Gespräch','next',()=>{
      if(state.index+1===bank.stages.length){sessions.delete(tier);port.postMessage({type:'home'});return;}
      const next=fresh(state.index+1,state.history);next.notes=state.notes;next.previous=state.choice;save(next);draw();
    }).className='primary';room();return;
  }
  if(hasChoice && !state.choice){
    add(work,'h2','Welchen Vorschlag machst du?');
    choices(s,work);
  }else{
    if(hasChoice){add(work,'strong',s.choices[state.choice]).id='selected';btn(work,'Auswahl ändern','edit',()=>clearChoice(''));}
    if(!hasChoice && lower()){add(work,'strong','Aus der Quelle');add(work,'blockquote',s.shortSource);}
    if(needsSource())add(work,'p',state.index===1?'Lies den Artikel. Welche Aussage ist belegt?':'Lies Studie B. Was wurde tatsächlich untersucht?');
    if(!state.valid && !conflict() && !needsSource()){
      add(work,'p',s.task[tier]);
      if(!lower() && !state.compared){
        const field=add(add(work,'label','Deine Erklärung'),'textarea');field.id='erklaerung';field.value=state.reason;
        const compare=btn(work,'Mit den Aussagen vergleichen','vergleichen',()=>{const issue=Entwurf.fehler(state.reason);state.compared=!issue;state.result=issue?.info||'';draw();});
        compare.disabled=!field.value.trim();
        field.oninput=()=>{state.reason=field.value;state.result='';work.querySelector('#feedback').textContent='';compare.disabled=!state.reason.trim();};
      }else{
        if(!lower()){
          add(work,'p','Dein eigener Grund · fachlich ungeprüft: '+state.reason);
          btn(work,'Grund bearbeiten','grund-aendern',()=>{state.compared=false;state.result='';draw();});
        }
        for(const k of tier==='Foerder'?check.short:'ABC')btn(work,check.answers['ABC'.indexOf(k)],'answer-'+k,()=>inspect(k)).className='answer';
      }
    }
    add(work,'p',conflict()?.[lower()?'short':'full'] || state.result).id='feedback';document.querySelector('#feedback').setAttribute('role','status');
    if(state.valid && !lower()){
      add(work,'p','Vergleiche deinen Grund mit der geprüften Aussage: '+check.answers['ABC'.indexOf(check.code)]);
      const own=add(work,'details');add(own,'summary','Eigenen Grund ansehen');add(own,'p',state.reason);
      btn(own,'Grund bearbeiten','grund-aendern',()=>{state.compared=false;state.valid=false;state.result='';draw();});
    }
    if(state.valid)btn(work,'Nachricht senden','send',()=>{
      if(!state.valid || state.sent || conflict() || needsSource() || Entwurf.fehler(state.reason))return;state.sent=true;
      if(bank.person==='Tom' && state.index===bank.stages.length-1)port.postMessage({type:'completed',person:bank.person,tier});
      state.reply=s.replies[state.choice || 'DONE'];
      state.notes ||= {}; if(!lower())state.notes[state.history.length+1]=state.reason;
      state.history.push(s.message[tier].join(' '),[s.choices[state.choice],check.answers['ABC'.indexOf(check.code)]].filter(Boolean).join(' '),state.reply);draw();
    }).className='primary';
  }
  btn(work,hasChoice?'Infokarte öffnen':'Artikel und Studien öffnen','source',source);
  function hint(index){
    const prior=state.choice?s.hints[state.choice]:s.helpBefore;
    const issue=Entwurf.fehler(state.reason);
    const reason=issue?.info || conflict()?.[lower()?'short':'full'] || (!state.valid && state.result);
    const ref=issue?.ref || (check.ref && {method:check.ref[0],section:check.ref[1]});
    const card=ref && bank.cards[ref.method];
    const where=card?card.title+' · '+card.sections[ref.section].title:hasChoice?'Nachricht von '+bank.person:'Artikel und Studien';
    const answer=check.answers?.['ABC'.indexOf(check.code)];
    const hints=reason?Entwurf.hilfen(where,issue?.frage || (conflict()?'Welcher Wunsch bleibt offen?':s.task[tier]),reason):
      [prior[0],s.task[tier],prior[1],prior[2] || (card?card.sections[ref.section].levels[tier]:prior.at(-1)),
        prior[3] || answer || prior.at(-1)];
    resource('Hilfe '+(index+1)+' von '+hints.length,body=>{
      add(body,'p',hints[index]);
      if(index+1<hints.length)btn(body,'Mehr Hilfe','mehr-hilfe',()=>hint(index+1));
    });
  }
  btn(work,'Hilfe','help',()=>hint(0));
  const qs=check.questions || s.questions;
  if(qs.length)btn(work,'Rückfrage an '+bank.person,'ask',()=>resource('Rückfrage',body=>{
    for(const [q,a] of qs)btn(body,q,'q'+body.childElementCount,()=>{state.asked=q+' '+a;dialog.close();draw();});
  }));
  if(state.asked && !state.valid)add(chat,'p',state.asked);
  if(state.result||conflict())work.querySelector('#feedback').className=state.valid?'fachlich-passend':'fachlich-falsch';
  room();
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
    const returning=previous && (data.abschnitt===undefined || !window.confirm('Diesen Abschnitt neu beginnen? Dein bisheriges Gespräch in diesem Zusatzfall wird ersetzt.'));
    if(dialog.open && (!returning || state!==previous))dialog.close();
    save(returning?previous:fresh((data.abschnitt||1)-1));
    if(data.abschnitt!==undefined)state.direct=true;
    draw();
  };
  port.postMessage({type:'ready'});
});
