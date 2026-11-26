(() => {
  'use strict';
  const data=JSON.parse(document.querySelector('#material').textContent);
  const bar=document.querySelector('#bar'), page=document.querySelector('#page'), work=document.querySelector('#workspace');
  const names={Foerder:'Förder',ESA:'ESA',MSA:'MSA',AHR:'AHR'};
  const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
  const btn=(action,label,style='',value='')=>'<button type="button" data-action="'+action+'" data-value="'+esc(value)+'" class="'+style+'">'+esc(label)+'</button>';
  const go=(action,text)=>btn(action,text,'primary');
  const para=s=>'<p>'+esc(s)+'</p>';
  const title=s=>'<h1>'+esc(s)+'</h1>';
  const context=s=>'<p class="context">'+esc(s)+'</p>';
  const strong=s=>esc(s).replace(/\*([^*]+)\*/g,'<strong>$1</strong>');
  let screen='level',level='',chapter=0,step=0,qi=0,source='',cardpage=0,shortcut=false,fromTransition=false;
  const sessions=new Map();
  const lesson=()=>data.levels[level],session=()=>sessions.get(level);
  const number=()=>chapter+1,card=(i=chapter)=>lesson().cards[i],label=(i=chapter)=>(i+1)+' – '+card(i).titel;
  const q=()=>lesson().fragen[qi],r=()=>session().answers[qi],model=()=>data.modelle[q().modell];
  const section=()=>card(qi).texte[q().abschnitt];
  const info=()=>lesson().info[chapter][step];
  const key=()=>source==='info'?'info-'+chapter+'-'+step:source==='paper'?'paper-'+chapter:'frage-'+qi;
  function sess(){
    return {units:[0,0,0,0],done:new Set(),hints:{},position:0,answers:Array.from({length:4},()=>({
      text:'',choice:null,tries:0,last:null,repeat:false,used:0,revealed:false,closed:null,view:'question',attempts:[]
    }))};
  }
  const questionScreens=['question','feedback','compare'];
  function diagram(i){
    const side=i<2?'Vorderseite':'Rückseite',base=i<2?0:2;
    return '<div class="sheet" role="img" aria-label="'+side+', '+card(i).position+' · '+esc(label(i))+' markiert">'+[base,base+1].map(n=>'<span class="'+(i===n?'active':'')+'">'+esc(label(n))+'</span>').join('')+'</div>';
  }
  function graphic(k){const g=data.graphics[k];return '<figure>'+g.svg+'<figcaption>'+esc(g.caption)+'</figcaption></figure>';}
  function menu(lookup=false){
    const buttons=lesson().cards.map((c,i)=>btn(lookup?'fill':'open',label(i)+(session().done.has(i)&&!lookup?' ✓':''),'chapter',i)).join('');
    return title(lookup?'Welche Karte fehlt?':'Welche Karte brauchst du?')+
      para(lookup?'Wähle die Karte auf deinem Blatt.':'Blatt noch leer? Starte mit dem Kondom.')+
      '<div class="grid">'+buttons+'</div>'+(lookup?(fromTransition?btn('startq','Zu den Fragen'):''):'<div class="menulinks">'+btn('questions','Karten fertig? Zu den Fragen')+btn('lookup','Fehlende Wörter nachsehen')+'</div>');
  }
  function paperLocation(){
    if(chapter===2)return 'Suche auf der Rückseite oben '+label()+'.';
    return 'Suche '+card().position+' auf der '+card().seite+' '+label()+'.';
  }
  function rows(){
    return '<ol>'+card().felder.map(f=>'<li><span>Schreibe bei <b>'+f.nummer+'</b>:</span> <strong>'+esc(f.wort)+'</strong></li>').join('')+'</ol>';
  }
  function paper(){
    return '<section class="paper">'+title('Infokarte · '+card().titel)+
      '<div class="locator">'+diagram(chapter)+'<div>'+para(paperLocation())+'</div></div>'+
      rows()+para('Alle vier Wörter eingetragen?')+
      go('written',shortcut?'Zurück zur Kartenauswahl':'Ja, weiter')+'</section>';
  }
  const sourceTitle=()=>context('Frage '+(qi+1)+' von 4');
  function location(){
    return '<div class="locator">'+'<p>'+esc(card(qi).titel)+' · <strong>'+esc(section().titel)+'</strong></p></div>';
  }
  function resultView(){
    const rec=r(),st=rec.last.state;
    let heading=({passend:'Gut erklärt.',teilweise:'Ein Teil stimmt.',fehlvorstellung:'Schau noch einmal hin.',widerspruch:'Prüfe diese Stelle.',vertauscht:'Prüfe die Reihenfolge.',unsicher:'Vergleiche deine Erklärung.',leer:'Dein erster Gedanke'})[st];
    if(st==='passend' && q().typ==='wahl')heading='Das passt.';
    const [karte,stelle]=rec.last.quelle||[qi,q().abschnitt];
    const reference=st==='passend'?'':context(card(karte).titel+' · '+card(karte).texte[stelle].titel);
    const compare=q().typ==='text' && rec.text.trim() && st!=='leer';
    const recommended=st==='unsicher' && compare;
    const actions=st==='passend'?go('advance','Weiter'):recommended?
      go('compare','Mit Beispiel vergleichen')+btn('revise','Antwort bearbeiten'):
      go('revise',q().typ==='wahl'?'Antwort ändern':'Antwort bearbeiten')+(compare?btn('compare','Mit Beispiel vergleichen'):'');
    return sourceTitle()+title(heading)+reference+para(rueckmeldung(q(),model(),rec))+'<div class="actions">'+actions+'</div>';
  }
  function question(){
    return '<section class="question">'+sourceTitle()+location()+title(q().frage)+(q().typ==='wahl'?
      '<div class="answers">'+q().optionen.map((o,i)=>btn('pick',o,'answer',i)).join('')+'</div>':
      '<label for="entry">Stichwörter reichen.</label><textarea id="entry" rows="2" aria-label="'+esc(q().frage)+'" spellcheck="false">'+esc(r().text)+'</textarea><div class="editfoot"><div id="segments"></div>'+go('check','Antwort prüfen')+'</div>')+'</section>';
  }
  const orientierung={
    level:'Suche das Niveau oben auf deinem Blatt. Tippe auf denselben Namen.',
    menu:'Beginne mit der ersten Karte, die auf deinem Blatt noch fehlt.',
    lookup:'Suche den Namen der fehlenden Karte auf deinem Blatt. Tippe auf diesen Namen.',
    intro:'Vergleiche die vier Karten auf deinem Blatt. Fehlt ein Eintrag, öffne die passende Karte.',
    end:'Lege deine ausgefüllten Infokarten für die nächste Stunde weg.',
    reserve:'Suche unten auf zwei Karten den Pearl-Index. Vergleiche die Zahlen.'
  };
  function help(){
    if(orientierung[source])return title('Hilfe')+para(orientierung[source])+go('back','Zurück');
    const stage=session().hints[key()]||1,task=questionScreens.includes(source);
    const max=task?5:2;
    let body='';
    if(task){
      body=title(stage===5?'Beispiel zum Vergleichen':'Hilfe '+stage+' von 5')+para(fachhilfe(q(),model(),r(),card(qi),stage,lesson().cards))+
        (stage===5?para('Vergleiche mit deiner Antwort.'):'')+btn('reference','Infokarte öffnen');
    }else if(source==='paper'){
      body=title('Hier schreibst du.')+'<div class="locator">'+diagram(chapter)+para(paperLocation())+'</div>'+
        (stage===1?para('Suche die Lücken 1 bis 4.'):rows());
    }else{
      body=title('Hilfe zum Bild')+graphic(info().bild)+para(info().hilfe[stage-1]);
    }
    return body+'<div class="actions">'+(stage<max?btn('more','Mehr Hilfe'):'')+go('back','Zurück zur Aufgabe')+'</div>';
  }
  function hilfequelle(){
    return (model() && Lernfeedback.analyze(q().modell,r().text).quelle)||[qi,q().abschnitt];
  }
  function reference(){
    const [karte,stelle]=hilfequelle();
    const c=card(karte),sec=c.texte[cardpage];
    return context(c.titel)+title(sec?sec.titel:'Pearl-Index · '+c.pearl)+(sec && cardpage===stelle?'<p class="beleg">'+esc(sec.volltext)+'</p>':para(sec?sec.volltext:c.pearl_erklaerung))+
      '<div class="actions">'+(cardpage>0?btn('prev','Vorherige Stelle'):'')+(sec?btn('following','Nächste Stelle'):'')+go('helpback','Zur Hilfe')+'</div>';
  }
  function main(){
    switch(screen){
      case 'level':return title('Vier Methoden zur Verhütung')+para('Wähle dein Niveau wie auf dem Blatt.')+'<div class="grid">'+Object.entries(names).map(([k,v])=>btn('level',v,'chapter',k)).join('')+'</div>';
      case 'menu':return menu();case 'lookup':return menu(true);
      case 'info':return '<section class="learn">'+context('Kapitel '+number()+' von 4 · '+card().titel)+title(info().titel)+'<div class="lesson">'+graphic(info().bild)+'<div>'+info().text.map(s=>'<p>'+strong(s)+'</p>').join('')+'</div></div>'+go('readnext','Weiter')+'</section>';
      case 'paper':return paper();
      case 'intro':return title('Sind alle vier Infokarten ausgefüllt?')+para('Lege die Karten neben das iPad.')+'<div class="actions">'+go('startq',session().position?'Zu den Fragen':'Zur ersten Frage')+btn('lookup','Fehlende Infokarte ergänzen')+'</div>';
      case 'question':return question();case 'feedback':return resultView();
      case 'help':return help();case 'reference':return reference();
      case 'compare':return sourceTitle()+title('Vergleiche mit dem Beispiel.')+'<p><b>Deine Antwort</b></p>'+'<p id="draft"></p><div id="pieces"></div>'+(r().last?.state==='unsicher'?'<p class="selbstcheck">'+esc(model().vergleich)+'</p>':'')+'<p><b>Beispiel</b> · '+esc(vergleichstext(q(),model(),r(),r().last))+'</p>'+'<div class="actions">'+btn('revise','Antwort bearbeiten')+go('compared','Verglichen, weiter')+'</div>';
      case 'reserve':return title('Zwei Karten vergleichen')+para('Vergleiche die Pearl-Index-Angaben zweier Karten. Was sagen sie über Schwangerschaften? Was sagen sie über eine Ansteckung beim Sex?')+btn('end','Zurück');
      case 'end':return title('Du bist fertig.')+para('Hebe die Karten für den Unterricht auf. Schneide erst, wenn deine Lehrkraft es sagt. Schneide einmal in der Mitte.')+btn('reserve','Wenn du Zeit hast: Zwei Karten vergleichen')+btn('menu','Zur Kapitelauswahl');
    }
  }
  function nav(){
    const origin=(screen==='help'||screen==='reference')?source:screen;
    bar.innerHTML=(['level','menu'].includes(origin)?'<strong>Fallakte.</strong>':btn('menu','‹ Kapitel'))+
      (screen==='menu'?btn('levels','Niveau ändern'):'')+btn('help','Ich brauche Hilfe','help');
  }
  // Seite nur bei mehr Text als Platz. Der ganze Entwurf bleibt separat im RAM.
  let editorParts=[],editAt=0,compareAt=0;
  function portions(text,box,isEditor){
    const parts=[];let offset=0;
    const set=s=>{if(isEditor)box.value=s;else box.textContent=s;};
    while(offset<text.length){
      let low=1,high=Math.min(1024,text.length-offset);
      while(low<high){
        const mid=Math.ceil((low+high)/2);
        set(text.slice(offset,offset+mid));
        if(box.scrollHeight<=box.clientHeight+1)low=mid;else high=mid-1;
      }
      let cut=offset+low;
      if(cut<text.length){
        const end=text.slice(offset,cut).match(/\s+(?=\S*$)/g);
        const space=end?text.slice(offset,cut).search(/\s+\S*$/):-1;
        if(space>low/2)cut=offset+space+1;
      }
      parts.push(text.slice(offset,cut));offset=cut;
    }
    return parts.length?parts:[''];
  }
  function pager(area,index,total){
    area.replaceChildren();
    if(total<2)return;
    area.innerHTML=(index?btn('earlier','‹'):'')+ '<span>'+ (index+1)+'/'+total+'</span>'+(index+1<total?btn('later','›'):'');
    area.querySelector('[data-action=earlier]')?.setAttribute('aria-label','Vorheriger Textteil');
    area.querySelector('[data-action=later]')?.setAttribute('aria-label','Nächster Textteil');
  }
  function paginate(position){
    const box=document.querySelector('#entry'),display=document.querySelector('#draft');
    if(!box && !display)return;
    if(display){
      const parts=portions(r().text,display,false);
      compareAt=Math.max(0,Math.min(compareAt,parts.length-1));
      display.textContent=parts[compareAt];pager(document.querySelector('#pieces'),compareAt,parts.length);return;
    }
    const focus=box===document.activeElement, full=r().text;
    const before=editorParts.slice(0,editAt).join('').length;
    const caret=position??(before+(focus?box.selectionStart:0));
    const selectionEnd=position??(before+box.selectionEnd);
    const mirror=box.cloneNode(false);
    mirror.removeAttribute('id');mirror.removeAttribute('aria-label');mirror.tabIndex=-1;
    mirror.style.cssText='position:fixed;visibility:hidden;pointer-events:none;left:0;top:0';
    const metrics=getComputedStyle(box);
    for(const name of ['width','height','fontSize','lineHeight','padding','border','boxSizing'])mirror.style[name]=metrics[name];
    box.parentNode.append(mirror);
    editorParts=portions(full,mirror,true);mirror.remove();
    let start=0;editAt=0;
    while(editAt+1<editorParts.length && start+editorParts[editAt].length<=caret){
      start+=editorParts[editAt++].length;
    }
    if(box.value!==editorParts[editAt])box.value=editorParts[editAt];
    if(focus)box.setSelectionRange(Math.max(0,caret-start),Math.max(0,selectionEnd-start));
    pager(document.querySelector('#segments'),editAt,editorParts.length);
  }
  function visibleArea(){
    const viewport=window.visualViewport;
    let top=viewport?.offsetTop||0,bottom=top+Math.min(innerHeight,viewport?.height||innerHeight);
    let host=window,offset=0;
    // Ein zugänglicher LMS-Rahmen kann bei offener Tastatur größer als sein Ausschnitt bleiben.
    try{
      while(host!==host.parent && host.frameElement){
        const frame=host.frameElement;offset+=frame.getBoundingClientRect().top+frame.clientTop;
        host=host.parent;
        const v=host.visualViewport,y=v?.offsetTop||0;
        top=Math.max(top,y-offset);bottom=Math.min(bottom,y+Math.min(host.innerHeight,v?.height||host.innerHeight)-offset);
      }
    }catch{ /* Bei einem fremden Ursprung liefert der eigene Viewport die verfügbare Höhe. */ }
    return {top,height:Math.max(1,bottom-top)};
  }
  function resize(){
    const area=visibleArea();
    work.style.height=area.height+'px';work.style.top=area.top+'px';
    work.classList.toggle('editing',screen==='question' && q().typ==='text' && area.height<410);
    work.classList.remove('tight');
    if(page.scrollHeight>page.clientHeight||page.scrollWidth>page.clientWidth)work.classList.add('tight');
    paginate();
    if(!work.classList.contains('tight') && page.scrollHeight>page.clientHeight){work.classList.add('tight');paginate();}
  }
  function render(){
    editorParts=[];editAt=0;compareAt=0;nav();page.dataset.screen=screen;page.dataset.feedback=screen==='feedback'?r().last.state:'';page.innerHTML=main();resize();page.focus({preventScroll:true});
  }
  function openUnit(n){
    chapter=n;shortcut=false;const pos=session().units[n];step=pos<2?pos:1;screen=pos===2?'paper':'info';
    if(pos===3){step=0;session().units[n]=0;}
  }
  function startQ(){
    qi=session().position;
    screen=qi>=4?'end':r().view;
  }
  function record(d){
    const rec=r();rec.tries++;
    rec.repeat=!!rec.last&&d.state===rec.last.state && d.kind===rec.last.kind && d.error===rec.last.error && String(d.parts)===String(rec.last.parts);
    if(d.state==='passend')rec.outcome=rec.revealed||rec.used>=2||rec.tries>1?'unterstuetzt':'selbststaendig';
    rec.last=d;rec.attempts.push({...d});rec.view=screen='feedback';
  }
  function advance(compared){
    const rec=r();rec.closed=compared?'selbstvergleich':rec.outcome;
    session().position=qi+1;startQ();
  }
  document.addEventListener('click',e=>{
    const b=e.target.closest('button[data-action]');if(!b)return;
    const a=b.dataset.action,v=b.dataset.value;
    switch(a){
      case 'earlier':case 'later':{
        const delta=a==='later'?1:-1;
        if(screen==='compare'){compareAt+=delta;paginate();}
        else{const pos=editorParts.slice(0,editAt+delta).join('').length;document.querySelector('#entry').focus({preventScroll:true});paginate(pos);}
        return;
      }
      case 'reserve':if(session()?.position===4)screen='reserve';break;
      case 'end':screen='end';break;
      case 'levels':screen='level';break;
      case 'level':level=v;if(!sessions.has(v))sessions.set(v,sess());screen='menu';break;
      case 'menu':screen='menu';break;
      case 'open':openUnit(+v);break;
      case 'readnext':session().units[chapter]=step+1;if(step===0)step++;else screen='paper';break;
      case 'written':
        if(shortcut){screen='lookup';break;}
        session().done.add(chapter);session().units[chapter]=3;
        if(chapter===3)screen='intro';else openUnit(chapter+1);break;
      case 'lookup':fromTransition=screen==='intro';screen='lookup';break;
      case 'fill':chapter=+v;shortcut=true;screen='paper';break;
      case 'questions':case 'startq':startQ();break;
      case 'pick':r().choice=q().optionen[+v];record({state:r().choice===q().passend?'passend':'fehlvorstellung',parts:[],error:q().alternativen.find(x=>x.text===r().choice)?.muster||null});break;
      case 'check':record(Lernfeedback.analyze(q().modell,r().text));break;
      case 'help':
        if(screen==='help'||screen==='reference'){screen=source;break;}
        source=screen;screen='help';if(questionScreens.includes(source))r().used=Math.max(r().used,session().hints[key()]||1);break;
      case 'more':session().hints[key()]=(session().hints[key()]||1)+1;
        if(questionScreens.includes(source)){r().used=session().hints[key()];if(r().used===5)r().revealed=true;}break;
      case 'back':screen=source;break;
      case 'reference':cardpage=hilfequelle()[1];screen='reference';break;
      case 'prev':cardpage--;break;case 'following':cardpage++;break;case 'helpback':screen='help';break;
      case 'revise':r().view=screen='question';break;
      case 'compare':r().revealed=true;r().view=screen='compare';break;
      case 'advance':advance(false);break;case 'compared':advance(true);break;
      default:return;
    }
    render();
  });
  document.addEventListener('input',e=>{
    if(e.target.id!=='entry')return;
    const prefix=editorParts.slice(0,editAt).join('');
    r().text=prefix+e.target.value+editorParts.slice(editAt+1).join('');
    paginate(prefix.length+e.target.selectionStart);
  });
  document.addEventListener('focusin',e=>{if(e.target.id==='entry')requestAnimationFrame(resize);});
  window.addEventListener('resize',resize);
  window.visualViewport?.addEventListener('resize',resize);
  window.visualViewport?.addEventListener('scroll',resize);
  try{
    let host=window;
    while(host!==host.parent && host.frameElement){
      host=host.parent;host.addEventListener('resize',resize);host.addEventListener('scroll',resize);
      host.visualViewport?.addEventListener('resize',resize);host.visualViewport?.addEventListener('scroll',resize);
    }
  }catch{ /* Der eigene Viewport bleibt erreichbar. */ }
  document.fonts.ready.then(resize);render();
})();
