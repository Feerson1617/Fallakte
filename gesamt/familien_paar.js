({kind,person,withHelp,number=0,joint=false})=>{
  const doc=document,by=id=>doc.getElementById(id),bank=JSON.parse(by('material').textContent);
  const click=el=>{
    if(typeof el==='string')el=by(el);
    if(!el||el.disabled)throw Error('Fehlende Aktion '+person+'/'+kind);
    const closed=el.closest('details:not([open])');if(closed&&el!==closed.querySelector('summary'))closed.querySelector('summary').click();
    if(!el.getClientRects().length)throw Error('Unsichtbare Aktion '+el.id);
    el.click();
  };
  function allHints(){click('help');for(let i=1;i<5;i++)click('hint-next');click('dismiss');}
  function choose(task){
    for(const [i,o] of task.answers.entries())if(!o.ok)click('answer-'+i);
    click('answer-'+task.answers.findIndex(o=>o.ok));
  }
  if(kind==='Person'){
    const c=bank.cases[person];click('next');
    for(const t of c.tasks){
      if(withHelp)allHints();
      click('terms');click('dismiss');click('cards');
      for(const d of [...doc.querySelectorAll('#dialog-body details')]){
        if(d.open || !d.parentElement.getClientRects().length)continue;
        if(!d.querySelector('summary').getClientRects().length)continue;
        d.querySelector('summary').click();
      }
      click('dismiss');
      const input=doc.querySelector('textarea');
      if(input){
        if(t.evidenceSentences){
          const first=t.evidenceSentences[0],wrong=[...doc.querySelectorAll('[id^=source-]')].find(e=>!t.evidenceSentences.includes(Number(e.id.split('-').at(-1))));
          if(wrong)click(wrong);click('source-'+first);
        }
        const field=doc.querySelector('textarea');field.value='Ich erkläre meine Lesart der Nachricht in eigenen Worten.';field.dispatchEvent(new Event('input',{bubbles:true}));
        click('compare');
      }
      choose(t);click('next');
    }
    if(doc.querySelector('[data-application]')){if(withHelp)allHints();choose(c.transfer);}
    const matrix=doc.querySelector('details[data-digital] summary');if(matrix)click(matrix);
    click('next');
  }else if(kind==='Laura'){
    const more=doc.querySelector('aside > details > summary');if(more)click(more);
    click('next');if(withHelp)allHints();
    const support=doc.querySelector('section.card details summary');if(support)click(support);
    click('next');
    for(let member=0;member<(joint?2:1);member++){
      const selection=(number+member)%3;click('weight-'+selection);
      for(const n of selection===2?[0,1]:[selection]){
        click('concern-'+n);click('fact-'+(1-n));click('fact-2');click('fact-3');click('fact-'+n);
        if(withHelp)allHints();
        choose(bank.limits[n]);click('next');
      }
    }
  }
}
