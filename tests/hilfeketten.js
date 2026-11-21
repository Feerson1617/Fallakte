// Start each branch with the on-screen picker. Read all five hints before using the
// last one. A help action may focus an existing button or open a draft, never send.
({person,tier,label,index,stage,previous}) => {
  const one=s=>document.querySelector(s);
  const many=s=>[...document.querySelectorAll(s)];
  const assert=(ok,msg)=>{if (!ok) throw Error([person,tier,stage.id,msg].join(' / '));};
  const click=node=>{assert(node && !node.disabled && node.getClientRects().length,'control');node.click();};
  const named=(selector,text)=>many(selector).find(b=>b.textContent===text);
  const press=s=>click(one(s));
  const history=()=>one('#history').textContent;
  const defaultMethod=stage.id==='C1'?'Cu':'K';
  const names={K:'Kondom',P:'Kombinationspille',H:'Hormonspirale',Cu:'Kupferspirale'};
  const checks={};
  function start(at=index) {
    press('#home-nav');press('#open-recovery');
    click(named('#recovery-picker button',person));
    click(named('#recovery-picker button',label));
    click(many('#recovery-picker fieldset:last-child button')[at]);
  }
  function choose(key) {
    press('#method-'+key.split('+').pop());
    if (key.includes('+')) press('#combine');
  }
  function issue(key) {
    const method=key.split('+').pop();
    if (person==='Laura' && index>=2 && method==='P') return true;
    if (person==='Celina' && ['P','H'].includes(method)) return true;
    if (['L0','L4','C3'].includes(stage.id) && !key.includes('K')) return true;
    return stage.id==='T0' && key!=='K';
  }
  function chain(state,key='') {
    const before=history(),number=one('#step').textContent;
    const article=!!stage.options.DONE;
    let sourceKey=key || defaultMethod;
    if (state==='Antwort' && ['L0','C3','T0'].includes(stage.id) && !key.includes('K') &&
        !(stage.declined && stage.declined[key])) sourceKey='K';
    const method=sourceKey.split('+').pop();
    const bridge=state==='Eigener Beitrag';
    const locked=state==='Zweite Antwort';
    const withdrawn=locked && issue(key);
    const text=[];
    for (let depth=1;depth<=5;depth++) {
      press('#help');
      assert(many('.hint').length===depth && history()===before,state+' changed history');
      text.push(one('#hint-current p').textContent);
      assert(text.at(-1).length>5,state+' empty help');
      assert(!!one('#help-action')===(depth===5),'early or missing action');
    }
    assert(!/mit deinem Partner|mit deiner Partnerin|zu zweit|tauscht euch|besprecht miteinander/i.test(text.join(' ')),'partner required');
    const laterFacts={
      L0:/Laura (will keine Pille|hat Schmerzen)|Erfahrung der Freundin/,
      L1:/Laura (will keine Pille|hat Schmerzen)|Erfahrung der Freundin/,
      L3:/Lauras Regelschmerzen|Laura hat Schmerzen/,
      C0:/Celinas Sorge vor dem Einsetzen|Celinas feste Beziehung/
    };
    if (laterFacts[stage.id]) assert(!laterFacts[stage.id].test(text.join(' ')),'later case fact');
    assert(text[2].includes('…') && many('.hint small')[3].textContent==='Eine mögliche Begründung','scaffold');
    if (!article) {
      const hint=stage.hints[sourceKey];
      const fact=Array.isArray(hint)?hint[1]:hint.fact;
      assert(text[0].includes('Karte „'+names[method]+'“') && text[1]===fact,state+' source/fact '+sourceKey);
      const section=text[0].match(/Abschnitt „([^“]+)“/)[1];
      assert(many('#card-'+method+' dt').some(dt=>dt.textContent===section),'source heading');
      assert(named('#support-panel button','Karte „'+names[method]+'“ lesen'),'source button');
      if (withdrawn) assert(text[3].includes('ziehe meinen Rat zurück') && text[3].includes(fact) && text[4].includes('Vorschlag zurückziehen'),'withdrawal example');
      else if (locked && key!==defaultMethod) {
        assert(key.split('+').every(k=>text[3].includes(names[k])) && text[3].includes(fact),'actual revised recommendation');
      } else {
        assert(text[3].includes(names[defaultMethod]),'example method');
        if (sourceKey!==defaultMethod) {
          assert(text[3].includes(names[method]) || /Pille|Spirale|Hormone/.test(text[3]),'missing comparison');
          assert(text[3].startsWith(LERNHILFEN[stage.id].vergleich[sourceKey] ||
                                   LERNHILFEN[stage.id].vergleich[method]),'missing reason before alternative');
        }
      }
      assert(!one('#card-cue').hidden,'missing paper cue');
    } else assert(named('#support-panel button','Artikel nachlesen'),'article source');
    press('#help-action');
    assert(history()===before && one('#step').textContent===number,state+' advanced');
    if (article || locked || bridge || (['Prüfung','Antwort'].includes(state) && key===defaultMethod)) {
      const expected=(article || bridge)?one('#work .primary'):named('#work .row button',withdrawn?'Vorschlag zurückziehen':'Vorschlag beibehalten');
      assert(expected && document.activeElement===expected && text[4].includes(expected.textContent),'wrong target');
    } else {
      assert(one('#send') && !one('#send').disabled && one('#method-'+defaultMethod).getAttribute('aria-pressed')==='true','wrong draft');
      assert(!one('#combine')?.checked && !one('#additional')?.value,'stale combination');
      assert(text[4].includes(names[defaultMethod]) && text[4].includes('Nachricht senden'),'draft instruction');
    }
    checks[state]=(checks[state]||0)+1;
    return text;
  }
  start();
  const opening=chain('Ohne Auswahl');
  if (!stage.options.DONE) {
    choose(defaultMethod);press('#send');
    click(named('#work .row button','Vorschlag ändern'));
    chain('Revision ohne Auswahl');
    if (stage.reviewPrevious) {
      for (const prior of Object.keys(previous.options)) {
        start(index-1);choose(prior);press('#send');
        click(named('#work .row button','Vorschlag beibehalten'));
        assert(one('#change-prior'),'missing retained choice');
        chain('Prüfung',prior);
      }
    }
    if (stage.id==='T0') {
      start();choose('P');press('#send');click(named('#work .row button','Vorschlag beibehalten'));
      chain('Eigener Beitrag');
    }
    for (const key of Object.keys(stage.options)) {
      start();choose(key);chain('Auswahl',key);
      choose(key);press('#send');chain('Antwort',key);
      // The fifth help may already have opened the revised draft.
      if (!one('#work .methods')) click(named('#work .row button','Vorschlag ändern'));
      choose(key);chain('Revision',key);
      choose(key);press('#send');chain('Zweite Antwort',key);
    }
  }
  return {person,niveau:tier,abschnitt:index+1,gepruefte_ketten:checks,ohne_auswahl:opening};
}
