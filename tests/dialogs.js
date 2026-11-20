// Browser-run path matrix. Drive rendered controls only, compare actual messages with the content file.
({person, tier, strategy, data}) => {
  function click(selector) {
    const node = document.querySelector(selector);
    if (!node || !node.getClientRects().length) throw Error('Missing control ' + selector);
    node.click();
  }
  function assert(ok, description) { if (!ok) throw Error(description); }
  function pair(value) {return Array.isArray(value) || typeof value==='string' ? value : value[tier];}
  function checkHints(expected) {
    expected.forEach((text,index)=>{
      click('#help');
      assert(document.querySelector('#hint-current p').textContent===text,'Hint '+index);
    });
  }
  click('#level-'+tier);
  click('[data-person="'+person+'"]');
  let methods=0, questions=0, helps=0;
  for (const stage of data.cases[person]) {
    assert([...document.querySelectorAll('.chat-step')].at(-1).textContent===stage.title,'Wrong step');
    const history=document.querySelector('#history');
    for(const line of stage.message[tier]) assert(history.textContent.includes(line),'Missing case information');
    const index=data.cases[person].indexOf(stage);
    for (const future of data.cases[person].slice(index+1)) assert(![...history.querySelectorAll('.chat-step')].some(x=>x.textContent===future.title),'Premature disclosure');
    for (const [question,answer] of stage.questions) {
      click('#ask');
      const b=[...document.querySelectorAll('.question')].find(b=>b.textContent===question);
      assert(b,'Missing question');b.click();questions++;
      assert(history.lastChild.textContent.endsWith(answer),'Unexpected answer');
    }
    assert(!document.querySelector('#ask'),'Repeatable question');
    const key=stage.options.DONE?'DONE':strategy;
    if (key!=='DONE') {
      const method=key.split('+').pop();
      click('#method-'+method);
      if(key.includes('+'))click('#combine');
      if(key.includes('+')){
        click('#method-K');
        const menu=document.querySelector('#additional');
        menu.value=method;
        menu.dispatchEvent(new Event('change'));
      }
      assert([...document.querySelectorAll('#work .preview p')].at(-1).textContent===stage.options[key],'Preview');
    }
    checkHints(pair(stage.hints[key]));helps+=2;
    for (const element of document.querySelectorAll('#work, #work button, #work p, #history .bubble, .article')) {
      assert(element.scrollWidth<=element.clientWidth+2,'Text overflow: '+stage.id+' '+element.className);
    }
    if(key==='DONE') {
      click('#work .primary');
    } else {
      click('#send');methods++;
      assert(history.lastChild.textContent.endsWith(pair(stage.replies[key])),'Selected response');
      assert(history.lastChild.previousSibling.textContent.endsWith(stage.options[key]),'Sent text');
      click('#work .primary');
    }
  }
  assert(document.querySelector('#task-title').textContent==='Gespräch abgeschlossen','Case incomplete');
  return {person,tier,strategy,methods,questions,helps,stages:data.cases[person].length};
}
