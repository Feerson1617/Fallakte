// Arbeitsblatt im sichtbaren Fenster. Nur längere Ansichten bekommen Blättertasten.
window.Arbeitsplatz = (() => {
  const make = (tag, cls) => Object.assign(document.createElement(tag), {className:cls});
  function button(label, action) {
    const b=make('button',''); b.type='button'; b.textContent=label; b.onclick=action; return b;
  }
  const pages = new Map();
  function sheet(parent) {
    if(pages.has(parent) && parent.querySelector(':scope > .blatt-inhalt'))return;
    const content=make('div','blatt-inhalt'), controls=make('nav','blatt-wechsel');
    controls.setAttribute('aria-label','Teile dieser Ansicht');
    const status=make('span','');status.setAttribute('aria-live','polite');
    let index=0,count=1;
    const previous=button('‹ Zurück',()=>show(index-1,true));
    const next=button('Weiter ›',()=>show(index+1,true));
    function indicate(){
      previous.disabled=index===0;next.disabled=index>=count-1;
      status.textContent=(index+1)+' / '+count;
    }
    function show(i,focus){
      index=Math.max(0,Math.min(count-1,i));
      content.scrollLeft=index*content.getBoundingClientRect().width;indicate();
      if(focus)(index===count-1?previous:next).focus({preventScroll:true});
    }
    controls.append(previous,status,next);
    content.append(...parent.childNodes);parent.classList.add('blatt');parent.append(content,controls);
    pages.set(parent,()=>{
      const width=content.getBoundingClientRect().width;if(!width)return;
      controls.hidden=true;content.classList.remove('geteilt');
      if(content.scrollHeight<=content.clientHeight && content.scrollWidth<=width+1){index=0;count=1;return;}
      controls.hidden=false;content.classList.add('geteilt');
      count=Math.max(1,Math.ceil((content.scrollWidth-1)/width));
      if(count===1)controls.hidden=true;
      show(index,false);
    });
    content.addEventListener('scroll',()=>{
      if(!content.classList.contains('geteilt'))return;
      const i=Math.round(content.scrollLeft/content.getBoundingClientRect().width);
      if(i!==index){index=i;indicate();}
    });
    // Bei Touch muss der Seitenumfang schon zur geöffneten Quelle passen, bevor eine weitere Taste angetippt wird.
    content.addEventListener('click',event=>{
      const summary=event.target.closest('summary');
      if(!summary || event.defaultPrevented || summary.parentElement?.tagName!=='DETAILS')return;
      event.preventDefault();
      summary.parentElement.open=!summary.parentElement.open;
      refresh();
      zeigen(summary);
    });
    content.addEventListener('toggle',refresh,true);
  }
  function zeigen(node){
    const field=node?.closest('.blatt-inhalt.geteilt');
    if(!field || !field.clientWidth)return;
    const start=field.getBoundingClientRect().left;
    const left=node.getBoundingClientRect().left-start+field.scrollLeft;
    const width=field.getBoundingClientRect().width;field.scrollLeft=Math.floor((left+1)/width)*width;
  }
  let current;
  function refresh(){
    if(!current)return;
    const {room,chat}=current;
    const v=window.visualViewport;
    let end=Math.min(innerHeight,(v?.offsetTop||0)+(v?.height||innerHeight));
    let host=window,offset=0;
    try{
      while(host!==host.parent && host.frameElement){
        offset+=host.frameElement.getBoundingClientRect().top+host.frameElement.clientTop;
        host=host.parent;const pv=host.visualViewport;
        end=Math.min(end,(pv?.offsetTop||0)+(pv?.height||host.innerHeight)-offset);
      }
    }catch{}
    document.documentElement.style.setProperty('--sichtbare-hoehe',end+'px');
    room.style.height=Math.max(1,end-room.getBoundingClientRect().top-2)+'px';
    for(const [box,update] of pages){
      if(!box.isConnected){pages.delete(box);continue;}
      if(box.getClientRects().length)update();
    }
    if(chat && current.newMessage){chat.scrollTop=room.matches('#lernspur.lesephase')?0:chat.scrollHeight;current.newMessage=false;}
  }
  function setup(room,work,chat,heading,hint,orientation,auftrag){
    const split=chat?.parentElement;
    let bar=room.querySelector(':scope > .arbeitskopf');
    if(!bar){
      bar=make('header','arbeitskopf');
      if(heading)bar.append(heading);
      if(chat){
        const latest=chat.querySelector('.chat-entry:last-child > p,.chat-history .bubble:last-child > p,:scope > .bubble:last-child > p') ||
          chat.lastElementChild;
        const excerpt=latest?.textContent.trim();
        const preview=()=>{
          toggle.replaceChildren();
          const label=make('span','chat-lang');label.textContent='Gespräch lesen';toggle.append(label);
          const kurz=make('span','chat-kurz');kurz.textContent='Chat';toggle.append(kurz);
          toggle.setAttribute('aria-label','Gespräch lesen');
          if(excerpt){const text=make('span','vorschau');text.textContent=excerpt;toggle.append(text);}
        };
        const toggle=button('Gespräch lesen',()=>{
          const open=room.classList.toggle('gespraech-offen');
          if(open){toggle.textContent='Zur Aufgabe';toggle.setAttribute('aria-label','Zur Aufgabe');}else preview();
          toggle.setAttribute('aria-expanded',String(open));
          if(open)chat.scrollTop=chat.scrollHeight;
          refresh();
        });
        preview();toggle.className='gespraech-wechsel';toggle.setAttribute('aria-expanded','false');bar.append(toggle);
        split.classList.add('arbeitsfelder');chat.classList.add('gespraech');
      }
      if(work===room){
        work=make('section','');work.append(...room.childNodes);room.append(work);
      }
      const help=hint||button('Ich brauche Hilfe',()=>orientation(help));
      help.className='hilfezugang';help.textContent='Ich brauche Hilfe';
      if(!help.id)help.id='orientierungshilfe-'+room.id;
      bar.append(help);room.prepend(bar);room.classList.add('lernraum');
      const cue=make('section','aufgabenkasten');
      const tag=make('span','aufgabenmarke');tag.textContent='Aufgabe';cue.append(tag);
      const source=work.querySelector('[data-auftrag],.fachcheck label,#begruendungsfrage,legend,h2,h3');
      const wording=auftrag || work.dataset.auftrag || source?.childNodes[0]?.textContent || 'Wähle den nächsten Schritt.';
      const line=make('p','');line.textContent=wording;cue.append(line);
      if(source && source.textContent.trim()===wording.trim() && !source.querySelector('input,textarea,select'))source.classList.add('nur-vorlesen');
      sheet(work);
      work.classList.add('mit-auftrag');work.prepend(cue);
    }
    current={room,chat,newMessage:!!chat};
    refresh();
  }
  // Das Dialogblatt liegt über der Aufgabe. Der Gesprächsverlauf behält seinen Platz.
  function prepareDialog(d,body){
    const bar=current?.room.querySelector('.arbeitskopf');
    if(!bar)return;
    let help=d.querySelector(':scope > .dialoghilfe');
    if(!help){
      help=button('Ich brauche Hilfe',()=>{
        const currentHelp=current.room.querySelector('.arbeitskopf .hilfezugang');
        if(d.dataset.hilfe==='true')d.close();
        else {d.close();currentHelp?.click();}
      });
      help.className='hilfezugang dialoghilfe';d.append(help);
    }
    sheet(body);refresh();
  }
  window.addEventListener('resize',refresh);
  window.visualViewport?.addEventListener('resize',refresh);
  try{
    let w=window;
    while(w!==w.parent&&w.frameElement){w=w.parent;w.visualViewport?.addEventListener('resize',refresh);w.addEventListener('resize',refresh);}
  }catch{}
  document.fonts.ready.then(refresh);
  return {setup,refresh,prepareDialog,zeigen};
})();
