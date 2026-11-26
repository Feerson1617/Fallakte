(() => {
  'use strict';
  const bank = JSON.parse(document.getElementById('material').textContent);
  const bar = document.getElementById('bar');
  const page = document.getElementById('page');
  const workspace = document.getElementById('workspace');
  const names = {Foerder:'Förder', ESA:'ESA', MSA:'MSA', AHR:'AHR'};
  const topics = [['index','huelle','kontakt'],['eisprung','einnahme'],['kupfer','kupferwahl'],['schleim','hormonwahl']];
  const icons = {
    menu:'<path d="M3 5h3v3H3zM10 5h11M3 11h3v3H3zM10 11h11M3 17h3v3H3zM10 17h11"/>',
    paper:'<path d="M4 3h11l3 3v4M4 3v18h13v-4M7 8h6M7 12h3M12 17l1-4 6-6 3 3-6 6z"/>',
    help:'<circle cx="12" cy="12" r="9"/><path d="M9.4 9a2.8 2.8 0 115 1.6c-1.3 1.3-2.4 1.4-2.4 3.5M12 17h.01"/>',
    arrow:'<path d="M4 12h15m-6-6 6 6-6 6"/>',
    back:'<path d="M20 12H5m6-6-6 6 6 6"/>',
    book:'<path d="M3 5c4-1 6 0 9 2 3-2 5-3 9-2v13c-4-1-6 0-9 2-3-2-5-3-9-2zM12 7v13"/>'
  };
  const icon = key => '<svg viewBox="0 0 24 24" aria-hidden="true" class="icon">'+icons[key]+'</svg>';
  const esc = value => String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
  function button(action,label,style='',value='',symbol='') {
    return '<button type="button" data-action="'+action+'" data-value="'+esc(value)+'" class="'+style+'">'+(symbol?icon(symbol):'')+'<span>'+esc(label)+'</span></button>';
  }
  const sessions = new Map();
  let level='', screen='level', chapter=0, hint=0, modelSection=0, lookup=false;
  let shortStep='read', forceRead=false;
  const session=()=>sessions.get(level);
  const cards=()=>bank.levels[level].cards;
  const progress=()=>session().progress[chapter];
  const topic=()=>topics[chapter][progress().item];
  const task=()=>bank.levels[level].fragen[topic()];
  const header=()=>cards()[chapter].ueberschrift;
  function graphic(key) {
    const g=bank.graphics[key];
    return '<figure>'+g.svg+'<figcaption>'+esc(g.caption)+'</figcaption></figure>';
  }
  function chapterTitle(i) {return '<span class="number">'+(i+1)+'</span><span>'+esc(cards()[i].titel)+'</span>';}
  function selectChapter(index) {
    chapter=index;lookup=false;hint=0;shortStep='read';forceRead=false;
    const r=session().progress[index];
    if (!r || r.done) session().progress[index]={item:0,chosen:null,correct:false,done:false,paper:false};
    screen=progress().paper?'paper':'question';
  }
  function navigation() {
    const inTask=screen==='question'||screen==='help';
    const isPaper=screen==='paper';
    const logo='<strong class="brand">Fallakte<span>.</span></strong>';
    const home=button('menu','Kapitel','plain','','menu');
    const left=screen==='level'||screen==='menu'||screen==='end'||isPaper?logo:home;
    const levelLabel=level?'<span class="level">'+names[level]+'</span>':'';
    const right=inTask?button('help','Ich brauche Hilfe','help','','help'):
      screen==='menu'?button('levels','Niveau ändern','plain'):'';
    bar.innerHTML='<div class="navleft">'+left+levelLabel+'</div>'+right;
  }
  function levels() {
    return '<section class="landing"><div class="intro"><div class="book">'+icon('book')+'</div><h1>Vier Methoden zur Verhütung</h1><p>Lerne die Methoden am iPad kennen. Am Ende jedes Kapitels füllst du eine Infokarte aus.</p></div><div class="selectbox"><h2>Wähle dein Niveau.</h2><div class="levelgrid">'+Object.entries(names).map(([k,v])=>button('level',v,'choice',k)).join('')+'</div></div></section>';
  }
  function menu(models) {
    const heading=models?'Welche Musterkarte brauchst du?':'Welches Kapitel ist noch nicht fertig?';
    const intro=models?'Bei Zeitnot kannst du fehlende Wörter ergänzen. Die Aufgaben bleiben offen.':'Schau auf dein Kartenblatt. Du kannst jedes Kapitel auch wiederholen.';
    const items=cards().map((c,i)=>'<button type="button" class="chapter" data-action="'+(models?'model':'open')+'" data-value="'+i+'">'+chapterTitle(i)+icon('arrow')+'</button>').join('');
    return '<section class="menu"><h1>'+heading+'</h1><p>'+intro+'</p><div class="chaptergrid">'+items+'</div>'+
      (models?'':'<div class="menufoot">'+button('models','Bei Zeitnot: Musterkarten','plain','','paper')+'</div>')+'</section>';
  }
  function context() {
    return '<p class="context">'+(topic()==='index'?'Kapitel 1 · Pearl-Index':esc(header()))+'</p>';
  }
  function source() {
    return '<section class="source">'+graphic(topic())+'<p class="fact">'+esc(task().info)+'</p></section>';
  }
  function question() {
    const q=task(),p=progress();
    const choices=q.antworten.map((text,i)=>{
      const picked=p.chosen===i;
      return '<button class="answer'+(picked?(p.correct?' yes':' no'):'')+'" data-action="answer" data-value="'+i+'" aria-pressed="'+picked+'"'+(p.correct?' disabled':'')+'><span class="mark" aria-hidden="true">'+(picked?(p.correct?'✓':'×'):'')+'</span><span>'+esc(text)+'</span></button>';
    }).join('');
    const result=p.chosen===null?'':'<div class="feedback '+(p.correct?'good':'again')+'" role="status"><strong>'+(p.correct?'Richtig.':'Versuch es noch einmal.')+'</strong> '+esc(p.correct?q.rueckmeldung:q.fehler)+'</div>';
    const next=p.correct?button('next','Weiter','primary','','arrow'):'';
    return '<div class="work">'+context()+'<div class="panes">'+source()+'<section class="task"><h1>'+esc(q.frage)+'</h1><div class="answers">'+choices+'</div>'+result+next+'</section></div></div>';
  }
  function splitQuestion() {
    const q=task(),p=progress();
    if(forceRead || (shortStep==='read' && !p.correct))return '<div class="compactpage">'+context()+'<h1>Lies die Info zum Bild.</h1>'+source()+button('toanswers','Antwort wählen','primary','','arrow')+'</div>';
    if((shortStep==='feedback' || p.correct) && p.chosen!==null)return '<div class="compactpage">'+context()+'<h1>'+(p.correct?'Richtig.':'Versuch es noch einmal.')+'</h1><p class="remember">'+esc(q.antworten[p.chosen])+'</p><p>'+esc(p.correct?q.rueckmeldung:q.fehler)+'</p>'+button(p.correct?'next':'toanswers',p.correct?'Weiter':'Antwort ändern','primary','','arrow')+'</div>';
    return '<div class="compactpage">'+context()+'<h1>'+esc(q.frage)+'</h1>'+
      q.antworten.map((text,i)=>button('answer',text,'answer'+(p.chosen===i?' no':''),i)).join('')+
      button('read','Bild und Info ansehen','plain','','book')+'</div>';
  }
  function helpPage(){
    return '<section class="assist">'+context()+'<div class="hintbody">'+graphic(topic())+'<div><h1>Hilfe '+hint+' von 5</h1><p>'+esc(task().hilfen[hint-1])+'</p></div></div><div class="actions">'+
      (hint<5?button('more','Mehr Hilfe','secondary','','help'):'')+button('back','Zurück zur Aufgabe','primary','','back')+'</div></section>';
  }
  function paper() {
    const c=cards()[chapter];
    const fields=c.felder.map(f=>'<li><span class="number">'+f.nummer+'</span><div><span class="fieldname">'+esc(f.titel)+'</span><strong>'+esc(f.wort)+'</strong></div></li>').join('');
    return '<section class="paper"><div class="paperhead">'+icon('paper')+'<h1>Jetzt brauchst du deine Infokarte!</h1></div><h2>'+esc(c.ueberschrift)+'</h2>'+
     '<p>'+(chapter===2?'Wende dein Kartenblatt. Suche oben.':'Suche '+(chapter<2?'vorne':'hinten')+' '+c.position+'.')+' Fülle Lücken. Verbessere Fehler.</p>'+
     '<ol>'+fields+'</ol>'+button('finish','Karte fertig – weiter','primary','','arrow')+'</section>';
  }
  function model() {
    const c=cards()[chapter], section=c.texte[modelSection];
    const text=section?section.volltext:c.pearl_erklaerung+' Kein Maß für den Schutz vor sexuell übertragbaren Infektionen (STI).';
    return '<section class="model"><p class="context">Musterkarte · '+esc(header())+'</p><h1>'+esc(section?section.titel:'Pearl-Index: '+c.pearl+' · Richtwert nach pro familia')+'</h1><p>'+esc(text)+'</p><div class="actions">'+
      (modelSection?button('prevsection','Zurück','plain','','back'):'')+(modelSection<c.texte.length?button('section','Weiterlesen','secondary','','book'):'')+
      button('fill','Fehlende Wörter ergänzen','primary','','paper')+'</div></section>';
  }
  function completion() {
    const done=session().completed.size;
    const count=done===4?'Du hast alle vier Kapitel in dieser Sitzung bearbeitet.':done===1?'Du hast ein Kapitel in dieser Sitzung bearbeitet.':'In dieser Sitzung bearbeitete Kapitel: '+done+'.';
    return '<section class="end"><div class="book">'+icon('book')+'</div><h1>Deine Karten für die Beratung</h1><p>'+count+'</p><p>Sind alle vier Karten vollständig? Schneide das Blatt einmal an der Mittellinie durch. Bewahre beide Karten für den 2. Dezember auf.</p>'+button('menu','Kapitel auswählen','primary','','menu')+'</section>';
  }
  function fits() {
    return page.scrollHeight<=page.clientHeight+1 && page.scrollWidth<=page.clientWidth+1;
  }
  function render(focus=false) {
    navigation();
    workspace.classList.remove('tight','split');
    page.innerHTML=screen==='level'?levels():screen==='menu'||screen==='models'?menu(screen==='models'):
      screen==='question'?question():screen==='help'?helpPage():screen==='paper'?paper():screen==='model'?model():completion();
    if(!fits())workspace.classList.add('tight');
    if(screen==='question' && (!fits()||forceRead)){
      workspace.classList.add('split');page.innerHTML=splitQuestion();
    }
    page.dataset.screen=screen;
    if(focus)page.focus({preventScroll:true});
  }
  document.addEventListener('click',event=>{
    const b=event.target.closest('button[data-action]');if(!b||b.disabled)return;
    const action=b.dataset.action,value=b.dataset.value;
    switch(action){
      case 'level':level=value;if(!sessions.has(level))sessions.set(level,{progress:[],completed:new Set()});screen='menu';break;
      case 'levels':screen='level';break;
      case 'menu':screen='menu';hint=0;break;
      case 'models':screen='models';break;
      case 'open':selectChapter(Number(value));break;
      case 'model':chapter=Number(value);modelSection=0;lookup=true;screen='model';break;
      case 'section':modelSection++;break;
      case 'prevsection':modelSection--;break;
      case 'fill':screen='paper';break;
      case 'read':forceRead=true;shortStep='read';break;
      case 'toanswers':forceRead=false;shortStep='answers';break;
      case 'help':if(screen==='help'){screen='question';}else{hint=1;screen='help';}break;
      case 'more':hint=Math.min(hint+1,5);break;
      case 'back':screen='question';break;
      case 'answer':{
        const p=progress();if(p.correct)return;
        p.chosen=Number(value);p.correct=p.chosen===task().richtig;shortStep='feedback';break;
      }
      case 'next':{
        const p=progress();if(!p.correct)return;
        if(p.item+1===topics[chapter].length){p.paper=true;screen='paper';}
        else{p.item++;p.chosen=null;p.correct=false;shortStep='read';forceRead=false;}
        break;
      }
      case 'finish':{
        if(!lookup){
          progress().done=true;progress().paper=false;
          session().completed.add(chapter);
        }
        const next=cards().findIndex((c,i)=>i>chapter && !session().completed.has(i));
        if(next>=0)selectChapter(next);else screen='end';
        break;
      }
    }
    render(true);
  });
  const observer=new ResizeObserver(()=>render());
  observer.observe(workspace);
  observer.observe(document.getElementById('type-measure'));
  document.fonts.ready.then(()=>render());
  render();
})();
