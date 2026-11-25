// Test-only observer. Read what a pupil sees after the application handled a click.
(() => {
  const fields=el=>[...el.querySelectorAll('.fields li')].map(li=>{
    const number=li.innerText.match(/^Feld (\d+)\b/);
    if (!number) throw Error('Feldnummer fehlt');
    return {number:Number(number[1]),answer:li.querySelector('b').innerText};
  });
  window.readPrintedCard=el=>({
    text:[...el.children].filter(n=>n.tagName!=='UL').map(n=>n.innerText).join(' '),
    fields:fields(el)
  });
  window.cardTrace={entries:{},review:{}};
  window.addEventListener('click',()=>{
    const title=document.querySelector('#view h1')?.innerText || '';
    const key=title.match(/^([1-4][AB]) /)?.[1];
    if (!key) return;
    const paper=document.querySelector('#view .paper .fields')?.parentElement;
    if (paper) window.cardTrace.entries[key]=fields(paper);
    const ref=document.querySelector('#view .reference');
    if (ref) window.cardTrace.review[key]=window.readPrintedCard(ref);
  });
})();
