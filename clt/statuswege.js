({name,depth,mask})=>{
  const b=JSON.parse(document.querySelector('#material').textContent),u=b.ui,c=b.cases[name],checks=[];
  const q=s=>document.querySelector(s);
  function click(s){
    const n=q(s);if(!n||n.disabled)throw Error('Fehlendes Bedienelement '+s);
    const d=n.closest('details:not([open])');if(d)d.querySelector('summary').click();n.click();
  }
  const help=n=>{click('#help');for(let j=1;j<n;j++)click('#hint-next');click('#dismiss');};
  click('#next');
  for(const task of c.tasks){
    if(q('textarea')){
      if(task.evidenceSentences)click('#source-'+task.evidenceSentences[0]);
      const t=q('textarea');t.value='Ich beziehe mich auf die Nachricht von '+name+'.';t.dispatchEvent(new Event('input'));click('#compare');
    }
    click('#cards');click('#dismiss');
    if(depth)help(depth);
    const wrong=task.answers.map((answer,i)=>({answer,i})).filter(v=>!v.answer.ok);
    const chosen=wrong.filter((_,i)=>mask&(1<<i));
    for(const v of chosen)click('#answer-'+v.i);
    if(chosen.length)click('#answer-'+chosen[0].i);
    click('#answer-'+task.answers.findIndex(a=>a.ok));
    const expected=depth===5||chosen.some(v=>v.answer.revealsSolution)?u.used:depth?u.explain:chosen.length?u.corrected:u.own;
    if(q('.tag').textContent!==expected)throw Error([name,task.id,mask,depth,expected,q('.tag').textContent]);
    help(5);
    if(q('.tag').textContent!==expected)throw Error('Rückwirkende Umwertung');
    checks.push([name,task.id,depth,chosen.map(v=>v.i),expected]);
    click('#next');
  }
  return checks;
}
