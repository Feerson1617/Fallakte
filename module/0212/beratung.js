'use strict';

// One RAM session per level. The two playable stages have separate drafts and facts.
window.Beratung = (() => {
  const sessions=new Map();
  let active=null;
  let renderNumber=0;
  const root=()=>document.getElementById('beratung');
  const bank=()=>window.LAURA;
  const stage=()=>bank().stages[active.stageId];
  const task=()=>stage().levels[active.tier];
  const info=()=>task().strategies[active.draft.strategy];
  const isPaper=()=>['MSA','AHR'].includes(active.tier);

  function element(tag,cls,text) {
    const node=document.createElement(tag);
    if (cls) node.className=cls;
    if (text!==undefined) node.textContent=text;
    return node;
  }
  function control(id,label,fn,cls) {
    const visibleRender=renderNumber;
    const button=element('button',cls,label);
    button.id=id;
    button.type='button';
    button.onclick=()=>{
      if (active && visibleRender===renderNumber && !button.disabled) fn(button);
    };
    return button;
  }
  function contextKey() {
    return JSON.stringify([bank().version,bank().caseId,active.tier,active.stageId,
      active.draft.strategy,stage().knownFacts]);
  }
  function missingGoal() {
    const methods=bank().strategies[active.draft.strategy].methods;
    return bank().goalRules.some(rule=>stage().knownFacts.includes(rule.fact) &&
      !rule.requiresAny.some(method=>methods.includes(method)));
  }
  function appendMessage(kind,speaker,text) {
    active.messages.push({kind,speaker,text,stageId:active.stageId,
      strategy:active.draft.strategy,revision:active.revision});
  }
  function newDraft(strategy='') {
    return {strategy,recheck:false,code:'',optionId:null,grant:null,feedback:null,anchorsOpen:false};
  }
  function enter(id,direct) {
    active.stageId=id;
    active.revision++;
    active.phase='choose';
    active.moreOpen=false;
    active.paperChecked=false;
    active.draft=newDraft();
    if (direct && id!=='L01') appendMessage('recap','Bisher im Fall',stage().recovery);
    appendMessage('opening','Laura',task().message);
    active.chatScroll=null;
    active.pageScroll=0;
    active.focusId='beratung-stage';
  }
  function begin(tier,id='L01') {
    if (!Object.hasOwn(bank().levels,tier) || !bank().stages[id]?.playable) return false;
    pause();
    active={tier,revision:0,asked:new Map(),messages:[],previous:'',focusId:'',pageScroll:0,chatScroll:null};
    sessions.set(tier,active);
    enter(id,true);
    render('beratung-stage',true);
    return true;
  }
  function pause() {
    if (!active) return;
    active.pageScroll=window.scrollY;
    active.chatScroll=document.getElementById('beratung-verlauf')?.scrollTop ?? active.chatScroll;
    if (root().contains(document.activeElement)) active.focusId=document.activeElement.id;
    window.Material.close(false);
    active=null;
    renderNumber++;
  }
  function resume(tier) {
    if (!sessions.has(tier)) return false;
    if (active && active.tier!==tier) pause();
    active=sessions.get(tier);
    render(active.focusId || 'beratung-stage',false,true);
    window.scrollTo(0,active.pageScroll);
    return true;
  }
  function select(strategy) {
    if (active.phase==='sent' || !Object.hasOwn(task().strategies,strategy)) return;
    if (active.draft.strategy===strategy) return;
    active.revision++;
    active.draft=newDraft(strategy);
    active.draft.recheck=isPaper() && active.paperChecked;
    active.phase='choose';
    render('strategie-'+strategy);
  }
  function matchesEvidence() {
    const draft=active.draft;
    if (isPaper()) return draft.code.trim().toUpperCase()===stage().code;
    return info().options.some(option=>option.id===draft.optionId && option.correct);
  }
  function canSend() {
    if (!active || active.phase!=='checked' || !active.draft.strategy) return false;
    const draft=active.draft;
    return draft.grant===contextKey() && matchesEvidence() && !missingGoal() && info().status==='C';
  }
  function check(optionId) {
    if (active.phase==='sent' || !active.draft.strategy) return;
    const draft=active.draft;
    draft.grant=null;
    draft.optionId=optionId;
    active.phase='choose';
    const option=info().options.find(o=>o.id===optionId);
    if (!matchesEvidence()) {
      const anchor=isPaper() ? stage().anchorFeedback[draft.code.trim().toUpperCase()] : null;
      const inputHint=draft.code.trim() ? 'Wähle einen der Buchstaben A, B oder C von deinem Laufzettel.' : 'Gib den Buchstaben der passenden Aussage ein.';
      draft.feedback={type:'A',text:option?.feedback || anchor?.text || inputHint,
        card:option?.card || anchor?.card || info().card};
    } else {
      if (isPaper()) active.paperChecked=true;
      if (missingGoal() || info().status==='B') {
        draft.feedback={type:'B',text:info().feedback,card:info().goalCard || info().card};
      } else if (info().status==='C') {
        draft.grant=contextKey();
        active.phase='checked';
        draft.feedback={type:'C',text:info().condition+' '+info().feedback,card:info().card};
      }
    }
    render('fachmeldung');
  }
  function send() {
    // A disabled control is a cue. This guard also covers stale events and repeat taps.
    if (!canSend()) return;
    const draft=active.draft, strategy=info();
    const reason=strategy.options.find(o=>o.id===draft.optionId)?.text;
    active.phase='sent';
    draft.grant=null;
    active.previous=draft.strategy;
    const proposal='Mein Rat: '+bank().strategies[draft.strategy].label+'.';
    appendMessage('send','Team',reason ? proposal+' '+reason : proposal);
    appendMessage('reaction','Laura',strategy.reply);
    active.chatScroll=null;
    render('beratung-reaktion',true);
  }
  function next() {
    if (active.phase!=='sent' || active.stageId!=='L01' || !bank().stages.L02.playable) return;
    enter('L02',false);
    render('beratung-stage',true);
    root().scrollIntoView({block:'start'});
  }
  function chat() {
    const history=element('div','beratung-verlauf');
    history.id='beratung-verlauf';
    history.tabIndex=0;
    history.setAttribute('role','log');
    history.setAttribute('aria-live','off');
    history.setAttribute('aria-label','Gespräch mit Laura');
    let previousId='';
    for (const message of active.messages) {
      if (message.stageId!==previousId) {
        history.append(element('p','abschnittsmarke',bank().stages[message.stageId].title));
        previousId=message.stageId;
      }
      const entry=element('div','chat-entry');
      entry.dataset.stage=message.stageId;
      entry.dataset.kind=message.kind;
      entry.dataset.speaker=message.speaker;
      entry.dataset.aboutStrategy=message.strategy;
      let sender=message.speaker==='Team' ? 'Dein Beratungsteam' : message.speaker;
      if (message.kind==='question' || message.kind==='answer') {
        const historical=message.revision!==active.revision || active.phase==='sent';
        entry.dataset.historical=String(historical);
        if (historical) {
          sender=message.kind==='question' ? 'Frühere Rückfrage' : 'Lauras frühere Antwort';
          if (message.strategy) sender+=' · '+bank().strategies[message.strategy].label;
        }
      }
      entry.append(element('strong','',sender),element('p','',message.text));
      if (message.kind==='reaction' && message.stageId===active.stageId) {
        entry.id='beratung-reaktion';
        entry.tabIndex=-1;
      }
      history.append(entry);
    }
    return history;
  }
  function strategyButton(id) {
    const selected=active.draft.strategy===id;
    const b=control('strategie-'+id,bank().strategies[id].label,()=>select(id),'strategie');
    b.dataset.strategy=id;
    b.setAttribute('aria-pressed',String(selected));
    return b;
  }
  function choices() {
    const field=element('fieldset','beratung-wahl');
    field.append(element('legend','','Du wählst jetzt deinen vollständigen Rat für Laura.'));
    if (active.previous && active.stageId==='L02') {
      field.append(element('p','bisher','Dein bisheriger Rat: '+bank().strategies[active.previous].label+'.'));
    }
    // Keep the previous recommendation visible alongside the new alternatives.
    // Lower levels start with at most three buttons; the other choices stay available.
    const primary=[...task().primary];
    if (active.previous && !primary.includes(active.previous)) {
      if (!isPaper() && primary.length>=3) primary.pop();
      primary.push(active.previous);
    }
    const row=element('div','strategie-grid');
    for (const id of primary) row.append(strategyButton(id));
    field.append(row);
    const other=Object.keys(task().strategies).filter(id=>!primary.includes(id));
    if (other.length) {
      const more=element('details','weitere-strategien');
      more.id='weitere-strategien';
      more.open=active.moreOpen || other.includes(active.draft.strategy);
      const token=renderNumber;
      more.ontoggle=()=>{if (active && renderNumber===token) active.moreOpen=more.open;};
      more.append(element('summary','','Weitere Strategien'));
      const list=element('div','strategie-grid');
      for (const id of other) list.append(strategyButton(id));
      more.append(list);
      field.append(more);
    }
    return field;
  }
  function paperCheck() {
    const section=element('section','fachcheck');
    const draft=active.draft;
    const details=element('details');
    details.open=draft.anchorsOpen;
    details.ontoggle=()=>{if (details.isConnected) draft.anchorsOpen=details.open;};
    section.append(element('h3','',draft.recheck?'Dein geänderter Rat':'Auf dem Laufzettel'));
    details.append(element('summary','',draft.recheck?'Auftrag und Aussagen vom Laufzettel ansehen':'Aussagen vom Laufzettel ansehen'));
    if (draft.recheck) section.append(element('p','','Passt dein notierter Grund noch zu deinem neuen Rat? Prüfe das und gib den passenden Buchstaben erneut ein.'));
    const instructions=draft.recheck?details:section;
    instructions.append(element('p','',task().paperPrompt),element('p','',task().task));
    for (const [letter,text] of Object.entries(stage().anchors)) details.append(element('p','',letter+' · '+text));
    details.append(element('p','rueckkehr',task().returnPrompt));
    section.append(details);
    const form=element('form','code-form');
    const label=element('label','','Prüfcode');
    label.htmlFor='pruefcode';
    const input=element('input');
    input.id='pruefcode';
    input.type='text';
    input.autocomplete='off';
    input.autocapitalize='characters';
    input.spellcheck=false;
    input.enterKeyHint='done';
    input.value=active.draft.code;
    input.oninput=()=>{
      if (active?.draft!==draft || active.phase==='sent') return;
      draft.code=input.value;
      draft.grant=null;
      active.phase='choose';
      draft.feedback=null;
      const message=document.getElementById('fachmeldung');
      message.textContent='';
      message.dataset.type='';
      document.getElementById('strategie-ergaenzen')?.remove();
      document.getElementById('nachricht-senden').disabled=true;
    };
    const verify=control('fachcheck-pruefen','Code prüfen',()=>check(null),'pruefen');
    form.onsubmit=event=>{event.preventDefault();verify.click();};
    form.append(label,input,verify);
    section.append(form);
    return section;
  }
  function closedCheck() {
    const field=element('fieldset','fachcheck');
    field.id='begruendungen';
    field.append(element('legend','',task().task));
    for (const option of info().options) {
      const b=control('grund-'+option.id,option.text,()=>check(option.id),'grund');
      b.dataset.option=option.id;
      b.setAttribute('aria-pressed',String(active.draft.optionId===option.id));
      field.append(b);
    }
    return field;
  }
  function materialTools() {
    const tools=element('div','beratung-tools');
    const key=contextKey();
    const asked=active.asked.get(key) || new Set();
    const context={stageId:active.stageId,levelId:active.tier,strategy:active.draft.strategy,
      asked:new Set(asked),feedback:active.draft.feedback};
    if (active.draft.strategy) {
      tools.append(control('passende-karte','Passende Infokarte öffnen',b=>
        window.Material.openCard(active.draft.feedback?.card || info().card,b)));
    }
    tools.append(control('hilfe','Hilfe',b=>window.Material.help(context,b)));
    const questions=active.draft.strategy ? info().questions : (task().before?.questions || []);
    if (questions.some(q=>!asked.has(q.id))) {
      const sourceSession=active, sourceDraft=active.draft;
      const ask=id=>{
        if (active!==sourceSession || active.draft!==sourceDraft || contextKey()!==key ||
            active.asked.get(key)?.has(id)) return;
        const question=questions.find(q=>q.id===id);
        if (!question) return;
        asked.add(id);
        active.asked.set(key,asked);
        appendMessage('question','Team',question.text);
        appendMessage('answer','Laura',question.answer);
        active.chatScroll=null;
        render('beratung-verlauf',true);
      };
      tools.append(control('ask','Rückfrage an Laura',b=>window.Material.questions(context,ask,b)));
    }
    return tools;
  }
  function work() {
    const area=element('div','beratung-arbeit');
    if (active.phase==='sent') {
      const end=active.stageId==='L02';
      area.append(element('h2','',end?'Laura 2 bearbeitet':'Rat gesendet'));
      if (end) area.append(element('p','','Hier endet der digitale Prototyp. Deinen Schlussrat formulierst du in der gemeinsamen Sicherung.'));
      area.append(end ? control('beratung-fertig','Zur Fallübersicht',()=>window.Runde1.home(),'senden') :
        control('beratung-weiter','Weiter zu Laura 2',next,'senden'));
      return area;
    }
    const evidence=element('p','abschnittshinweis',task().evidence || stage().evidence);
    area.append(evidence,choices());
    if (!active.draft.strategy) {
      const submit=control('nachricht-senden','Nachricht senden',send,'senden');
      submit.disabled=true;
      area.append(submit,materialTools());
      return area;
    }
    area.append(isPaper()?paperCheck():closedCheck());
    const feedback=element('p','fachmeldung',active.draft.feedback?.text || '');
    feedback.id='fachmeldung';
    feedback.tabIndex=-1;
    feedback.dataset.type=active.draft.feedback?.type || '';
    feedback.setAttribute('role','status');
    area.append(feedback);
    if (active.draft.feedback?.type==='B') {
      const addition='K+'+active.draft.strategy;
      if (Object.hasOwn(task().strategies,addition)) {
        const b=control('strategie-ergaenzen','Ein passendes latexfreies Kondom ergänzen',()=>select(addition),'ergaenzen');
        area.append(b);
      }
    }
    const submit=control('nachricht-senden','Nachricht senden',send,'senden');
    submit.disabled=!canSend();
    area.append(submit,materialTools());
    return area;
  }
  function render(focusId,showLatest=false,restore=false) {
    renderNumber++;
    const target=root();
    const lastHistory=target.querySelector('#beratung-verlauf');
    if (!showLatest && !restore && !target.hidden && lastHistory && lastHistory.dataset.level===active.tier) {
      active.chatScroll=lastHistory.scrollTop;
    }
    const header=element('header','beratung-kopf');
    const title=element('h1','',stage().title);
    title.id='beratung-stage';
    title.dataset.stage=active.stageId;
    title.tabIndex=-1;
    const tier=element('span','',bank().levels[active.tier]);
    tier.id='beratung-tier';
    header.append(title,tier);
    const layout=element('div','beratung-spalten');
    const history=chat();
    history.dataset.level=active.tier;
    layout.append(history,work());
    target.replaceChildren(header,layout);
    if (showLatest || active.chatScroll===null) {
      const last=history.lastElementChild;
      if (last) history.scrollTop+=last.getBoundingClientRect().top-history.getBoundingClientRect().top-6;
    } else history.scrollTop=active.chatScroll;
    const focus=document.getElementById(focusId);
    focus?.focus({preventScroll:true});
    if (focusId==='fachmeldung' && focus.getBoundingClientRect().bottom>innerHeight)
      focus.scrollIntoView({block:'nearest'});
    window.dispatchEvent(new Event('beratung:view'));
  }
  return Object.freeze({
    begin,has:tier=>sessions.has(tier),resume,pause,
    status:()=>active ? {tier:active.tier,stageId:active.stageId,phase:active.phase} : null
  });
})();
