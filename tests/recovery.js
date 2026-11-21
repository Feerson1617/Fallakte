// Exercise the new session via its visible controls, starting with no earlier recommendation.
({person, tier, index, stages}) => {
  const find=s=>document.querySelector(s);
  const all=s=>[...document.querySelectorAll(s)];
  function assert(ok, message) {
    if (!ok) throw Error(person+' '+(index+1)+' '+tier+': '+message);
  }
  function press(node) {
    assert(node && !node.disabled && node.getClientRects().length,'missing control');
    node.click();
  }
  const click=s=>press(find(s));
  const stage=stages[index];
  const content=value=>typeof value==='object' && !Array.isArray(value)?value[tier]:value;
  const progress=()=>find('#step').textContent;
  const marker=person+' '+(index+1)+' von '+stages.length;
  assert(progress()===marker,'wrong section');
  assert(find('#room-level').textContent===({Foerder:'Förder'}[tier] || tier),'wrong level');
  const chat=find('#history');
  const steps=all('#history .chat-step');
  assert(steps.length===1 && steps[0].textContent===stage.title,'invented earlier chat');
  assert(JSON.stringify(all('#history .person p').map(e=>e.textContent))===JSON.stringify(content(stage.message)),'wrong message');
  assert(!find('#history .team,#draft-preview,#send,#work .response,#change-prior,.hint'),'previous response');
  const facts=all('.recap li').map(e=>e.textContent);
  assert(JSON.stringify(facts)===JSON.stringify(stages.slice(0,index).map(s=>s.recap)),'recap out of order');
  const disclosed=chat.innerText;
  const boundaries={
    Laura:[[],[/schwanger/i],[/Freundin|Einsetzen|Pille/i],[/Schmerzen|Regel\b/i],[]],
    Celina:[[],[/länger|täglich|später/i],[/Einsetzen|Periode/i],[/festen Beziehung|Infektion|\bSTI\b/i],[]],
    Tom:[[],[/Artikel|Forschung/i],[]]
  };
  for (const later of boundaries[person].slice(index+1).flat()) assert(!later.test(disclosed),'early fact '+later);
  assert(all('#history .article').length===Number(person==='Tom' && index>=1),'wrong article availability');
  const snapshot=chat.innerText;
  click('#cards-nav');click('#resources .return');
  click('#home-nav');click('[data-person="'+person+'"]');
  assert(progress()===marker && chat.innerText===snapshot,'navigation lost position');
  if (person==='Tom' && index===2) {
    click('.recap button');
    assert(document.activeElement.matches('.article'),'article inaccessible');
  }
  for (let depth=1;depth<=5;depth++) {
    click('#help');
    assert(all('.hint').length===depth && chat.innerText===snapshot,'help changed conversation');
    if (depth===1 && stage.options.DONE) {
      press(all('#support-panel button').find(b=>b.textContent==='Artikel nachlesen'));
      assert(document.activeElement.matches('.article'),'missing article for help');
    }
  }
  click('#help-action');
  assert(chat.innerText===snapshot && progress()===marker,'help advanced conversation');
  if (stage.options.DONE) {
    click('#work .primary');
    assert(index===stages.length-1?find('#task-title').textContent==='Gespräch abgeschlossen':
      progress()===person+' '+(index+2)+' von '+stages.length,'discussion could not continue');
  } else {
    const cue=find('#card-cue');
    assert(!cue.hidden && cue.textContent.includes('Infokarte auf Papier'),'paper card missing');
    click('#method-P');
    assert(index!==0 || person!=='Laura' || !find('#combine,#additional'),'combination too soon');
    if (index>=1 && person==='Laura') click('#combine');
    const first=person==='Laura' && index>=1?'K+P':'P';
    click('#send');
    assert(find('#work .response').textContent===content(stage.replies[first]),'unexpected feedback');
    if (person==='Laura' && index>=2) assert(/nicht|abgelehnt/.test(find('#work .response').textContent),'pill refusal lost');
    press(all('#work .row button').find(b=>b.textContent==='Vorschlag ändern'));
    click('#method-K');
    const draft=find('#draft-preview').textContent;
    click('#cards-nav');click('#resources .return');
    assert(find('#draft-preview').textContent===draft,'lost revised draft');
    click('#send');
    assert(find('#work .response').textContent===content(stage.replies.K),'revision feedback');
    press(all('#work .row button').find(b=>b.textContent==='Vorschlag beibehalten'));
    if (index===stages.length-1) assert(find('#task-title').textContent==='Gespräch abgeschlossen','final blocked');
    else {
      assert(progress()===person+' '+(index+2)+' von '+stages.length,'progress blocked');
      if (stages[index+1].reviewPrevious) {
        assert(find('#change-prior') && find('#work .preview').textContent.includes('Kondom'),'new choice lost');
      }
    }
  }
  return {person,niveau:tier,abschnitt:index+1,vorherige_fakten:facts.length,
          hilfestufen:5,revision:!stage.options.DONE};
}
