'use strict';
window.Reserve0212 = (() => {
  let frame, port, ready=false, pending, active, pendingCards=false;
  const progress=new Map();
  const slot=()=>document.getElementById('reserve-platz');
  const key=(person,tier)=>person+'/'+tier;
  const announce=detail=>window.dispatchEvent(new CustomEvent('reserve0212:status',{detail}));

  function send() {
    if (!ready || !pending) return;
    port.postMessage(pending);
    pending=null;
    if (pendingCards) {port.postMessage({type:'cards'});pendingCards=false;}
  }
  function connect() {
    ready=false;
    port?.close();
    const channel=new MessageChannel();
    port=channel.port1;
    port.onmessage=({data})=>{
      if (data.type==='ready') {ready=true;send();return;}
      if (data.type==='home') {if (!slot().hidden) {hide();Runde1.home();}return;}
      if (data.type==='status') {
        progress.set(key(data.person,data.tier),data.abschnitt);
        if (!slot().hidden && active===key(data.person,data.tier)) announce(data);
      }
    };
    frame.contentWindow.postMessage('reserve0212:verbinden','*',[channel.port2]);
  }
  function open(person,tier,abschnitt) {
    if (!['Tom','Celina'].includes(person) || !['Foerder','ESA','MSA','AHR'].includes(tier)) return;
    if (abschnitt!==undefined && (!Number.isInteger(abschnitt) || abschnitt<1 || abschnitt>(person==='Tom'?3:5))) return;
    active=key(person,tier);
    pending={type:'open',person,tier,abschnitt};
    pendingCards=false;
    slot().hidden=false;
    const payload=document.getElementById('reserve-'+person) || document.getElementById('reserve');
    const frameId='rahmen-'+payload.id;
    frame=document.getElementById(frameId);
    for (const child of slot().querySelectorAll('iframe')) child.hidden=child!==frame;
    if (!frame) {
      frame=document.createElement('iframe');
      const created=frame;
      frame.id=frameId;frame.title='Freiwillige Vertiefung · '+person;
      frame.addEventListener('load',()=>{created.dataset.loaded='true';if(frame===created)connect();});
      const bytes=Uint8Array.from(atob(payload.textContent),c=>c.charCodeAt(0));
      frame.srcdoc=new TextDecoder().decode(bytes);
      slot().append(frame);
      ready=false;
    } else if(frame.dataset.loaded)connect();
    const status={person,tier,abschnitt:abschnitt??progress.get(active)??1,view:'room'};
    announce(status);
    send();
    return status;
  }
  function cards() {
    if (slot().hidden) return;
    if (!ready) pendingCards=true;
    else port.postMessage({type:'cards'});
  }
  function hide() {slot().hidden=true;active=undefined;}
  return {open,hide,cards};
})();
