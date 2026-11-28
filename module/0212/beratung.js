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
  const advanced=()=>['MSA','AHR'].includes(active.tier);

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
  function knownConcerns(tier) {
    const session=sessions.get(tier);
    if(!session)return [];
    const short=bank().concernsShort;
    const text=tier==='Foerder'||tier==='ESA'?short:bank().facts;
    return bank().stages[session.stageId].knownFacts.filter(key=>Object.hasOwn(short,key)).map(key=>text[key]);
  }
  function newDraft(strategy='') {
    return {strategy,reason:'',compared:false,optionId:null,grant:null,feedback:null,anchorsOpen:false};
  }
  function enter(id,direct) {
    active.stageId=id;
    active.reading=!direct;
    active.revision++;
    active.phase='choose';
    active.editingChoice=false;
    active.historyOpen=false;
    active.moreOpen=false;

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
    active={tier,revision:0,asked:new Map(),reasons:new Map(),messages:[],previous:'',focusId:'',pageScroll:0,chatScroll:null};
    sessions.set(tier,active);
    const first=Lernspur.state(tier).erst;
    if(first){
      active.messages.push({kind:'erster-rat',speaker:'Du',text:'Mein erster Rat: '+first.choice,stageId:'Einstieg'},
        {kind:'entwurf',speaker:'Dein erster Grund · fachlich ungeprüft',text:first.reason,stageId:'Einstieg'});
    }
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
    active.editingChoice=false;
    if (active.draft.strategy!==strategy) {
      active.revision++;
      active.reasons.set(active.stageId+'/'+active.draft.strategy,active.draft.reason);
      active.draft=newDraft(strategy);active.draft.reason=active.reasons.get(active.stageId+'/'+strategy)||'';

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
  function draftIssue(){
    const draft=active.draft;
    const medical=Entwurf.fehler(draft.reason);
    if(medical || !advanced() || !draft.strategy)return medical;
    // Nur überprüfbare Kontrollaussagen dieser konkreten Aufgabe. Die Gewichtung von Lauras Sorgen ist persönlich.
    const canonical=s=>s.trim().toLocaleLowerCase('de').replace(/[.!]+$/u,'').replace(/\s+/gu,' ');
    const option=info().options.find(o=>!o.correct && canonical(o.text)===canonical(draft.reason) &&
        !(active.stageId==='L04' && o.text.includes('Lauras Sorge')));
    return option?{frage:task().task,info:option.feedback,ref:option.card}:null;
  }
  function entwurfsdiagnose(){
    const model=Aussagen.beratung(active.stageId,bank().strategies[active.draft.strategy].methods,info(),task().task);
    return Diagnose.analyse(active.draft.reason,model);
  }
  function matchesEvidence() {
    const draft=active.draft;
    if(advanced() && (!draft.compared || draftIssue()))return false;
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
      if(!option)return;
      draft.feedback={type:'A',text:option.feedback,card:option.card};
    } else {

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
    if(advanced())appendMessage('entwurf','Dein eigener Grund · fachlich ungeprüft',draft.reason);
    appendMessage('send','Du',advanced()?proposal:proposal+' '+reason);
    appendMessage('reaction','Laura',strategy.reply);
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
    for (const message of active.messages) {
      const entry=element('div','chat-entry');
      entry.dataset.stage=message.stageId;
      entry.dataset.kind=message.kind;
      entry.dataset.speaker=message.speaker;
      entry.dataset.aboutStrategy=message.strategy;
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
      if(message.kind==='entwurf'){
        const own=element('details');own.append(element('summary','','Dein Grund'),element('strong','',sender),element('p','',message.text));entry.append(own);
      }else entry.append(element('strong','',sender),element('p','',message.text));
      if (message.kind==='reaction' && message.stageId===active.stageId) {
        entry.id='beratung-reaktion';
        entry.tabIndex=-1;
      }
      messages.append(entry);
    }

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
    field.append(element('legend','','Was rätst du Laura?'));
    if (active.previous) {
      field.append(element('p','bisher','Dein bisheriger Rat: '+bank().strategies[active.previous].label+'.'));
    }
    // Keep the previous recommendation visible alongside the new alternatives.
    // Lower levels start with at most three buttons; the other choices stay available.
    const primary=task().primary.filter(id=>!advanced() || bank().strategies[id].methods.length===1);
    if (active.previous && !primary.includes(active.previous)) {
      if (!advanced() && primary.length>=3) primary.pop();
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
    if (advanced()) {
      group(primary.filter(id=>bank().strategies[id].methods.length===1),'Einzelmethoden');
      const combined=primary.filter(id=>bank().strategies[id].methods.length===2);if(combined.length)group(combined,'Bisheriger Vorschlag');
    } else group(primary);
    const other=Object.keys(task().strategies).filter(id=>!primary.includes(id));
    if (other.length) {
      const more=element('details','weitere-strategien');
      more.id='weitere-strategien';
      more.open=active.moreOpen || other.includes(active.draft.strategy);
      const token=renderNumber;
      more.ontoggle=()=>{if (active && renderNumber===token) active.moreOpen=more.open;};
      more.append(element('summary','','Weitere Vorschläge'));
      const list=element('div','strategie-grid');
      for (const id of other) list.append(strategyButton(id));
      more.append(list);
      field.append(more);
    }
    return field;
  }
  function explanation(){
    const box=element('section','fachcheck');
    const label=element('label','',task().task);label.htmlFor='erklaerung';
    const field=element('textarea');field.id='erklaerung';field.rows=2;field.value=active.draft.reason;
    const next=control('vergleichen','Mit den Aussagen vergleichen',()=>{
      const d=active.draft, error=draftIssue();
      d.feedback=error?{type:'A',text:error.info,card:error.ref}:null;
      d.compared=!error;
      render(error?'fachmeldung':'begruendungen');
    },'senden');
    next.disabled=!field.value.trim();next.hidden=!!active.draft.feedback;
    field.oninput=()=>{active.draft.reason=field.value;active.draft.feedback=null;
      next.hidden=false;document.getElementById('entwurf-bearbeiten')?.remove();
      const msg=document.getElementById('fachmeldung');if(msg){msg.textContent='';msg.dataset.type='';}
      next.disabled=!field.value.trim();};
    box.append(label,field,next);return box;
  }
  const compact=()=>matchMedia('(max-height:400px),(max-width:475px)').matches;
  const kurzfrage={L01:'Was bedeutet die Latexallergie für deinen Rat?',L02:'Wie schützt dein Rat vor Schwangerschaft und Infektionen?',L03:'Passt dein Rat zu Lauras wechselndem Alltag?',L04:'Wie passt dein Rat zu ihren Schmerzen und Sorgen?',L05:'Was spricht für deinen Schlussrat?'};
  function closedCheck() {
    const field=element('section','fachcheck');
    field.id='begruendungen';
    const question=element('h2','',advanced()?'Welche Aussage stimmt?':compact()?kurzfrage[active.stageId]:task().task);
    question.id='begruendungsfrage';field.setAttribute('aria-labelledby',question.id);field.append(question);
    if(advanced()){
      const analysis=entwurfsdiagnose();
      const msg=element('p','denkhinweis',analysis.feedback+(analysis.status==='unsicher'?'':' '+analysis.focus));
      msg.dataset.diagnose=analysis.status;field.append(msg);
      const draft=element('details','eigener-text');draft.append(element('summary','','Eigener Grund'),
          element('p','','Fachlich ungeprüft: '+active.draft.reason),control('erklaerung-aendern','Erklärung ändern',()=>{active.draft.compared=false;editReason();}));
      field.append(draft);
    }
    for (const option of info().options) {
      const b=control('grund-'+option.id,option.text,()=>check(option.id),'grund');
      b.dataset.option=option.id;
      if(active.draft.optionId===option.id && active.draft.feedback?.type==='A')b.dataset.urteil='falsch';
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
    tools.append(control('hilfe','Hilfe',b=>window.Material.help({...context,feedback:active.draft.feedback,error:draftIssue(),diagnose:advanced() && active.draft.strategy && active.draft.reason.trim()?entwurfsdiagnose():null},b)));
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
    if(matchMedia('(max-width:650px),(max-height:400px)').matches){
      const more=element('details','quellenwahl');more.append(element('summary','','Karte und Rückfragen'));
      if(active.draft.strategy && !advanced())more.append(element('p','',task().task));
      for(const item of [...tools.children])if(item.id!=='hilfe')more.append(item);
      tools.append(more);
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
    if(compact() && canEdit){
      const short={K:'Kondom ohne Latex',P:'Pille',Cu:'Kupferspirale',H:'Hormonspirale'};
      const caption=bank().strategies[active.draft.strategy].methods.map(id=>short[id]).join(' + ');
      const edit=control('strategie-bearbeiten','Rat ändern · '+caption,editChoice,'textaktion');
      edit.setAttribute('aria-label','Rat ändern · '+label);rat.append(edit);
    }else{
      rat.append(element('p','','Dein Rat · '+label));
      if(canEdit)rat.append(control('strategie-bearbeiten','Auswahl ändern',editChoice,'textaktion'));
    }
    return rat;
  }
  function work() {
    const area=element('section','beratung-arbeit');
    const step=currentStep();
    area.id='beratung-arbeit';
    area.dataset.step=step;
    area.dataset.auftrag={wahl:'Was rätst du Laura?',grund:advanced() && active.draft.compared?'Vergleiche deinen Grund. Welche Aussage stimmt?':
      compact() && !advanced()?kurzfrage[active.stageId]:task().task,senden:'Vergleiche deinen Grund. Sende dann deinen Rat.',korrektur:'Ändere deinen Rat für Laura.',
      antwort:'Lies Lauras Antwort im Chat.'}[step];
    area.setAttribute('aria-label','Dein aktueller Arbeitsschritt');
    if(active.reading){
      area.dataset.auftrag='Lies Lauras neue Nachricht. →';
      area.append(control('beratung-lesen','Weiter',()=>{active.reading=false;render('beratung-stage');},'senden'));
      return area;
    }
    if (active.phase==='sent') {
      const following=followingStage();
      const end=!following?.playable;
      area.append(element('h2','',end?'Dein persönlicher Schlussrat':'Lies Lauras Antwort.'));
      if(end){
        const facts=element('details','fallwissen');facts.append(element('summary','','Was ist Laura wichtig?'));
        const list=element('ul');for(const text of knownConcerns(active.tier))list.append(element('li','',text));facts.append(list);area.append(facts);
        area.append(control('beratung-fertig','Schlussrat festhalten',()=>window.Runde1.final(),'senden'));
      }else area.append(control('beratung-weiter',following.title.split(' – ')[0]+' öffnen',next,'senden'));
      return area;
    }
    if (step==='wahl' || step==='grund') {
      const evidence=element('p','abschnittshinweis',step==='grund' ? info().evidence : task().evidence || stage().evidence);
      evidence.dataset.stage=active.stageId;
      evidence.dataset.aboutStrategy=step==='grund' ? active.draft.strategy : '';
      if (step==='wahl') {
        area.append(evidence,choices());
      } else {
        area.append(chosenStrategy(true));
        if(advanced() && !active.draft.compared)area.append(explanation());
        else area.append(closedCheck());

      }
    } else {
      const lowerCorrection=step==='korrektur' && !advanced();
      area.append(chosenStrategy(step==='senden' || lowerCorrection));
    }
    const report=step==='wahl' ? null : active.draft.feedback;
    const feedback=element('p','fachmeldung',report?.text || '');
    feedback.id='fachmeldung';
    feedback.tabIndex=-1;
    feedback.dataset.type=report?.type || '';
    feedback.setAttribute('role','status');
    const retry=compact() && report?.type==='A' && area.querySelector('#begruendungen');
    if(retry){
      const choices=element('details','neuer-grund');
      choices.append(element('summary','','Aussage ändern'));
      retry.replaceWith(choices);choices.append(retry);
      area.insertBefore(feedback,choices);
      area.dataset.auftrag='Lies den Hinweis. Ändere deine Aussage.';
    }else area.append(feedback);
    if(step==='grund' && advanced() && !active.draft.compared && report?.type==='A'){
      area.append(control('entwurf-bearbeiten','Grund bearbeiten',()=>{
        active.draft.feedback=null;render('erklaerung');Entwurf.bearbeiten(document.getElementById('erklaerung'));
      },'senden'));
    }
    if (step==='korrektur') {
      const correction=info().correction;
      if (correction.target && !advanced()) {
        area.append(control('strategie-ergaenzen',correction.label,()=>select(correction.target),'ergaenzen'));
      } else {
        area.append(control('strategie-neu-waehlen',correction.label,editChoice,'ergaenzen'));
      }
    }
    if(advanced() && step==='senden'){
      const statement=info().options.find(o=>o.id===active.draft.optionId);
      area.append(element('p','','Vergleiche deinen Grund mit der geprüften Aussage: '+statement.text));
      const own=element('details','entwurfsvergleich');own.append(element('summary','','Eigenen Grund ansehen'),element('p','',active.draft.reason));area.append(own);
    }
    const submit=control('nachricht-senden','Nachricht senden',send,'senden');
    submit.disabled=!canSend();
    submit.hidden=submit.disabled;
    area.append(submit);
    if (step==='senden' || step==='korrektur') {
      area.append(control('grund-bearbeiten','Antwort erneut prüfen',editReason,'textaktion'));
    }
    area.append(materialTools());
    if (active.stageId!=='L01') {
      const facts=element('details','fallwissen');
      facts.append(element('summary','','Was ist Laura wichtig?'));
      const list=element('ul');
      for(const text of knownConcerns(active.tier))list.append(element('li','',text));
      facts.append(list);area.append(facts);
    }
    return area;
  }
  function render(focusId,showLatest=false,restore=false) {
    renderNumber++;
    const target=root();
    target.classList.toggle("lesephase",active.reading);
    const lastHistory=target.querySelector('#beratung-verlauf');
    if (!showLatest && !restore && !target.hidden && lastHistory && lastHistory.dataset.level===active.tier) {
      active.chatScroll=lastHistory.scrollTop;
    }
    const header=element('header','beratung-kopf');
    const title=element('h1');
    title.append(element('span','titel-lang',stage().title),element('span','titel-kurz',stage().title.split(' – ')[0]));
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
    Arbeitsplatz.setup(target,layout.lastElementChild,history,header,layout.querySelector('#hilfe'),
      b=>window.Material.orient('Lies Lauras Antwort. Die Taste in der Aufgabe führt weiter.',b));
    const transcript=history;
    transcript.scrollTop=showLatest || active.chatScroll===null ? transcript.scrollHeight : active.chatScroll;
    const focus=document.getElementById(focusId);
    if(focusId==='fachmeldung')Arbeitsplatz.zeigen(focus);
    focus?.focus({preventScroll:true});

    window.dispatchEvent(new Event('beratung:view'));
  }
  return Object.freeze({
    known:knownConcerns,
    letzterRat:tier=>{
      const session=sessions.get(tier);
      if(session?.stageId!=='L05' || session.phase!=='sent')return null;
      const text=session.messages.findLast(m=>m.kind==='entwurf' && m.stageId==='L05' && m.strategy===session.previous)?.text;
      return {choice:bank().strategies[session.previous].label,reason:text||''};
    },
    begin,has:tier=>sessions.has(tier),resume,pause,
    status:()=>active ? {tier:active.tier,stageId:active.stageId,phase:active.phase} : null
  });
})();
