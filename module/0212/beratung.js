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
      if (active && visibleRender===renderNumber && button.isConnected && !button.disabled) fn(button);
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
    active.editingChoice=false;
    active.historyOpen=false;
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
    active.chatScroll=document.getElementById('chat-meldungen')?.scrollTop ?? active.chatScroll;
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
    active.editingChoice=false;
    if (active.draft.strategy!==strategy) {
      active.revision++;
      active.draft=newDraft(strategy);
      active.draft.recheck=isPaper() && active.paperChecked;
      active.phase='choose';
    }
    render('aktueller-rat');
  }
  function editChoice() {
    active.editingChoice=true;
    render('strategie-'+active.draft.strategy);
  }
  function editReason() {
    active.draft.feedback=null;
    active.draft.grant=null;
    active.phase='choose';
    render('aktueller-rat');
  }
  function matchesEvidence() {
    const draft=active.draft;
    if (isPaper()) return draft.code.trim().toUpperCase()===stage().code;
    return info().options.some(option=>option.id===draft.optionId && option.correct);
  }
  function canSend() {
    if (!active || active.phase!=='checked' || active.editingChoice || !active.draft.strategy) return false;
    const draft=active.draft;
    return draft.grant===contextKey() && matchesEvidence() && !missingGoal() && info().status==='C';
  }
  function check(optionId) {
    if (active.phase==='sent' || active.editingChoice || !active.draft.strategy) return;
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
    appendMessage('send','Du',reason ? proposal+' '+reason : proposal);
    appendMessage('reaction','Laura',strategy.reply);
    if(!followingStage())window.dispatchEvent(new CustomEvent('beratung:abgeschlossen',{detail:active.tier}));
    active.chatScroll=null;
    render('beratung-reaktion',true);
  }
  function followingStage() {
    const stages=Object.values(bank().stages);
    const index=stages.findIndex(item=>item.id===active.stageId);
    return stages[index+1];
  }
  function next() {
    const following=followingStage();
    if (active.phase!=='sent' || !following?.playable) return;
    enter(following.id,false);
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
    const messages=element('div','chat-meldungen');
    messages.id='chat-meldungen';
    const latest=active.messages.length-1;
    const showPast=control('fruehere-nachrichten','Gesprächsverlauf',button=>{
      active.historyOpen=!active.historyOpen;
      for (const entry of messages.querySelectorAll('[data-past=true]')) entry.hidden=!active.historyOpen;
      button.setAttribute('aria-expanded',String(active.historyOpen));
      messages.scrollTop=0;
    });
    showPast.setAttribute('aria-controls',messages.id);
    showPast.setAttribute('aria-expanded',String(active.historyOpen));
    let hasPast=false;
    for (const [index,message] of active.messages.entries()) {
      const entry=element('div','chat-entry');
      entry.dataset.stage=message.stageId;
      entry.dataset.kind=message.kind;
      entry.dataset.speaker=message.speaker;
      entry.dataset.aboutStrategy=message.strategy;
      const currentStart=message.stageId===active.stageId && ['opening','recap'].includes(message.kind);
      const recentPair=index>=latest-1 && message.revision===active.revision;
      const visible=active.phase==='sent' ? recentPair : currentStart || recentPair;
      if (!visible) {
        hasPast=true;
        entry.dataset.past='true';
        entry.hidden=!active.historyOpen;
      }
      let sender=message.speaker;
      if (message.kind==='question' || message.kind==='answer') {
        const historical=message.revision!==active.revision || active.phase==='sent';
        entry.dataset.historical=String(historical);
        if (historical) {
          sender=message.kind==='question' ? 'Frühere Rückfrage' : 'Lauras frühere Antwort';
          if (message.strategy) {
            const previousTask=bank().stages[message.stageId].levels[active.tier];
            sender+=' · '+(previousTask.choiceLabels?.[message.strategy] || bank().strategies[message.strategy].label);
          }
        }
      }
      entry.append(element('strong','',sender),element('p','',message.text));
      if (message.kind==='reaction' && message.stageId===active.stageId) {
        entry.id='beratung-reaktion';
        entry.tabIndex=-1;
      }
      messages.append(entry);
    }
    if (hasPast) history.append(showPast);
    history.append(messages);
    return history;
  }
  function strategyButton(id) {
    const selected=active.draft.strategy===id;
    const label=task().choiceLabels?.[id] || bank().strategies[id].label;
    const b=control('strategie-'+id,label,()=>select(id),'strategie');
    b.dataset.strategy=id;
    b.setAttribute('aria-pressed',String(selected));
    return b;
  }
  function choices() {
    const field=element('fieldset','beratung-wahl');
    field.append(element('legend','','Wähle deinen vollständigen Rat für Laura.'));
    if (active.previous) {
      field.append(element('p','bisher','Dein bisheriger Rat: '+bank().strategies[active.previous].label+'.'));
    }
    // Keep the previous recommendation visible alongside the new alternatives.
    // Lower levels start with at most three buttons; the other choices stay available.
    const primary=[...task().primary];
    if (active.previous && !primary.includes(active.previous)) {
      if (!isPaper() && primary.length>=3) primary.pop();
      primary.push(active.previous);
    }
    function group(ids,title) {
      const row=element('div','strategie-grid');
      if (title) {
        field.append(element('p','strategie-gruppe',title));
        row.setAttribute('role','group');
        row.setAttribute('aria-label',title);
      }
      for (const id of ids) row.append(strategyButton(id));
      field.append(row);
    }
    if (isPaper()) {
      group(primary.filter(id=>bank().strategies[id].methods.length===1),'Einzelmethoden');
      group(primary.filter(id=>bank().strategies[id].methods.length===2),'Kombinationen');
    } else group(primary);
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
    details.id='papier-ersatz';
    details.open=draft.anchorsOpen;
    details.ontoggle=()=>{if (details.isConnected) draft.anchorsOpen=details.open;};
    if (draft.recheck) section.append(element('p','','Laufzettel · Seite '+Math.ceil(Number(stage().id.slice(1))/2)+' · „'+stage().title+'“: Lies deine Begründung. Passt sie zur neuen Empfehlung? Wenn dein neuer Rat einen anderen Grund hat, ergänze ihn. Gib den Buchstaben erneut ein.'));
    else section.append(element('p','',task().task),element('p','',task().paperPrompt));
    details.append(element('summary','',task().paperFallback),element('p','',task().task));
    for (const [letter,text] of Object.entries(stage().anchors)) details.append(element('p','',letter+' · '+text));
    details.append(element('p','',bank().paperFallbackInstruction));
    const form=element('form','code-form');
    const label=element('label','','Prüfcode vom Laufzettel');
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
      document.getElementById('strategie-neu-waehlen')?.remove();
      document.getElementById('kartenverweise').replaceWith(cardLinks());
      document.getElementById('nachricht-senden').disabled=true;
    };
    const verify=control('fachcheck-pruefen','Code prüfen',()=>check(null),'pruefen');
    form.onsubmit=event=>{event.preventDefault();verify.click();};
    form.append(label,input,verify);
    section.append(element('p','rueckkehr',task().returnPrompt),form,details);
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
  function cardLinks() {
    const links=element('div','kartenverweise');
    links.id='kartenverweise';
    const draft=active.draft;
    const source=draft.strategy ? info() : task().before;
    const references=[draft.feedback?.card || source.card];
    if (draft.strategy) {
      const methods=bank().strategies[draft.strategy].methods;
      for (const ref of [source.card,...source.extraCards]) {
        const listed=references.some(other=>other.method===ref.method && other.section===ref.section);
        if (methods.includes(ref.method) && !listed) references.push(ref);
      }
    }
    references.forEach((ref,index)=>{
      const id=index?'passende-karte-'+index:'passende-karte';
      const link=control(id,window.Material.cardLabel(ref),b=>window.Material.openCard(ref,b,active.tier));
      link.dataset.method=ref.method;
      link.dataset.section=ref.section;
      links.append(link);
    });
    return links;
  }
  function materialTools() {
    const tools=element('div','beratung-tools');
    const key=contextKey();
    const asked=active.asked.get(key) || new Set();
    const context={stageId:active.stageId,levelId:active.tier,strategy:active.draft.strategy,
      asked:new Set(asked),feedback:active.draft.feedback};
    if (active.draft.strategy || active.stageId==='L01') tools.append(cardLinks());
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
        appendMessage('question','Du',question.text);
        appendMessage('answer','Laura',question.answer);
        active.chatScroll=null;
        render('beratung-verlauf',true);
      };
      tools.append(control('ask','Rückfrage an Laura',b=>window.Material.questions(context,ask,b)));
    }
    return tools;
  }
  function currentStep() {
    if (active.phase==='sent') return 'antwort';
    if (!active.draft.strategy || active.editingChoice) return 'wahl';
    if (active.phase==='checked') return 'senden';
    return active.draft.feedback?.type==='B' ? 'korrektur' : 'grund';
  }
  function chosenStrategy(canEdit) {
    const rat=element('div','gewaehlter-rat');
    rat.id='aktueller-rat';
    rat.tabIndex=-1;
    rat.dataset.aboutStrategy=active.draft.strategy;
    const label=task().choiceLabels?.[active.draft.strategy] || bank().strategies[active.draft.strategy].label;
    rat.append(element('p','','Dein Rat · '+label));
    if (canEdit) rat.append(control('strategie-bearbeiten','Auswahl ändern',editChoice,'textaktion'));
    return rat;
  }
  function work() {
    const area=element('section','beratung-arbeit');
    const step=currentStep();
    area.id='beratung-arbeit';
    area.dataset.step=step;
    area.setAttribute('aria-label','Dein aktueller Arbeitsschritt');
    if (active.phase==='sent') {
      const following=followingStage();
      const end=!following?.playable;
      area.append(element('h2','',end?'Schlussrat gesendet':'Lies Lauras Antwort.'));
      if (end) area.append(element('p','','Laufzettel · Seite '+(isPaper()?3:1)+' · „Mein Schlussrat“: Lass deine Antwort für das Unterrichtsgespräch offen.'));
      area.append(end ? control('beratung-fertig','Zur Fallübersicht',()=>window.Runde1.home(),'senden') :
        control('beratung-weiter',following.title.split(' – ')[0]+' öffnen',next,'senden'));
      return area;
    }
    if (step==='wahl' || step==='grund') {
      const evidence=element('p','abschnittshinweis',step==='grund' ? info().evidence : task().evidence || stage().evidence);
      evidence.dataset.stage=active.stageId;
      evidence.dataset.aboutStrategy=step==='grund' ? active.draft.strategy : '';
      if (step==='wahl') {
        area.append(evidence,choices());
      } else {
        area.append(chosenStrategy(true),evidence,isPaper()?paperCheck():closedCheck());
        if (task().paperFieldId) {
          const guide=element('details','schlussrat-hilfe');
          guide.append(element('summary','','Schreibhilfe für „Mein Schlussrat“'),window.Material.finalAdvice(active.tier));
          area.append(guide);
        }
      }
    } else {
      const lowerCorrection=step==='korrektur' && !isPaper();
      area.append(chosenStrategy(step==='senden' || lowerCorrection));
    }
    const report=step==='wahl' ? null : active.draft.feedback;
    const feedback=element('p','fachmeldung',report?.text || '');
    feedback.id='fachmeldung';
    feedback.tabIndex=-1;
    feedback.dataset.type=report?.type || '';
    feedback.setAttribute('role','status');
    area.append(feedback);
    if (step==='korrektur') {
      const correction=info().correction;
      if (correction.target && !isPaper()) {
        area.append(control('strategie-ergaenzen',correction.label,()=>select(correction.target),'ergaenzen'));
      } else {
        area.append(control('strategie-neu-waehlen',correction.label,editChoice,'ergaenzen'));
      }
    }
    const submit=control('nachricht-senden','Nachricht senden',send,'senden');
    submit.disabled=!canSend();
    submit.hidden=submit.disabled;
    area.append(submit);
    if (step==='senden' || step==='korrektur') {
      area.append(control('grund-bearbeiten','Antwort erneut prüfen',editReason,'textaktion'));
    }
    area.append(materialTools());
    return area;
  }
  function render(focusId,showLatest=false,restore=false) {
    renderNumber++;
    const target=root();
    const lastHistory=target.querySelector('#beratung-verlauf');
    if (!showLatest && !restore && !target.hidden && lastHistory && lastHistory.dataset.level===active.tier) {
      active.chatScroll=lastHistory.querySelector('#chat-meldungen').scrollTop;
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
    const transcript=history.querySelector('#chat-meldungen');
    transcript.scrollTop=showLatest || active.chatScroll===null ? transcript.scrollHeight : active.chatScroll;
    const focus=document.getElementById(focusId);
    focus?.focus({preventScroll:true});
    if (!restore && focus && (focusId==='fachmeldung' || focusId==='aktueller-rat' || focusId==='beratung-reaktion')) {
      const rect=focus.getBoundingClientRect();
      if (rect.bottom<0 || rect.top>innerHeight) focus.scrollIntoView({block:'nearest'});
    }
    window.dispatchEvent(new Event('beratung:view'));
  }
  return Object.freeze({
    begin,has:tier=>sessions.has(tier),resume,pause,
    status:()=>active ? {tier:active.tier,stageId:active.stageId,phase:active.phase} : null
  });
})();
