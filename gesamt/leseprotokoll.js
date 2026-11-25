// Nur im Prüfbrowser. Exportiert sichtbaren Text, die aktuell erreichbaren Knöpfe
// und den Medienort nach einer tatsächlich ausgelösten Bedienhandlung.
(() => {
  let seen=new Set(),batch=[];
  function flush(){if(batch.length){window.protokoll(batch);batch=[];}}
  function read(event){
    const id=q=>document.querySelector(q);
    if(!document.body)return;
    const module=id('#auswahl')?'START':id('#materialvertrag')?'UB02':id('#bank')?id('#step')?.textContent.split(' ')[0]:id('#sheet')?'PREP':id('#portraits')?'UB08':null;
    if(!module)return;
    const work=id('dialog[open]')||document.body;
    const visible=el=>el.getClientRects().length && !el.closest('[hidden]') &&
      ![...function*(node){for(let p=node.parentElement;p;p=p.parentElement)yield p;}(el)].some(p=>p.tagName==='DETAILS'&&!p.open&&!p.querySelector('summary')?.contains(el));
    const text=work.innerText.trim();
    if(!text)return;
    const buttons=[...work.querySelectorAll('button,summary,select')].filter(visible).map(b=>[b.id||b.dataset.do||b.name||b.tagName,b.innerText.trim(),!b.disabled]);
    const stage=id('#beratung-stage')?.dataset.stage || id('main h1[data-section]')?.dataset.section || id('#step')?.textContent || id('#view h1')?.textContent || '';
    const tier=id('#beratung-tier')?.innerText || id('#level-name')?.innerText || id('#step + p')?.innerText.split(' · ').at(-1) || (module==='UB08'?parent.document.querySelector('#gespraechsstand')?.textContent.split(' · ').at(-1):'') || window.auditTier || '';
    const key=JSON.stringify([module,stage,tier,text,buttons]);
    if(seen.has(key))return;
    seen.add(key);
    batch.push({modul:module,abschnitt:stage,niveau:tier,aktion:event?.target?.id||event?.target?.dataset?.do||event?.type||'Öffnen',text,bedienung:buttons});
    if(batch.length>=24)flush();
  }
  for(const name of ['click','change','toggle'])window.addEventListener(name,read);
  window.addEventListener('DOMContentLoaded',read);
  window.addEventListener('pagehide',flush);
  window.auditRead=read;
  window.auditFlush=flush;
})();
