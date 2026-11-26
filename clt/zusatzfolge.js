async path=>{
  const q=s=>document.querySelector(s);
  function click(s){
    const n=q(s);if(!n || n.disabled)throw Error('Zusatzfall '+s+' '+path);
    const d=n.closest('details:not([open])');if(d)d.querySelector('summary').click();n.click();
  }
  const bank=JSON.parse(q('#bank').textContent);
  for(const [i,key] of path.entries()){
    const stage=bank.stages[i],context=stage.checks?.[key]||stage;
    if(!q('#step').textContent.includes((i+1)+' von'))throw Error('Schritt '+i);
    if(key)click('[id="method-'+key+'"]');
    else{
      click('#source');click('#back');
      // WebKit kann das native close-Ereignis nach mehreren Animationsframes zustellen.
      const until=performance.now()+5000;
      while(!q('#erklaerung,[id^=answer-]')){
        if(performance.now()>until)throw Error('Quellenrückkehr ohne Eingabe in '+bank.person+' '+(i+1));
        await new Promise(resolve=>setTimeout(resolve,20));
      }
    }
    if(q('#erklaerung')){
      const t=q('#erklaerung');t.value='Ich berücksichtige die Bedingungen und die Wünsche der Person.';
      t.dispatchEvent(new Event('input'));click('#vergleichen');
    }
    click('#answer-'+context.code);click('#send');
    if(!q('.gespraech').textContent.includes(stage.replies[key||'DONE']))throw Error('Antwort fehlt '+i);
    click('#next');
  }
}
