/* Supplementary views read the same bank as the working area. Only the caller can record an answer. */
(() => {
  'use strict';

  let dialog;
  let title;
  let body;
  let origin;
  let back;
  let views = [];

  function element(tag, text) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function button(label, action, id) {
    const node = element('button',label);
    node.type = 'button';
    if (id) node.id = id;
    node.addEventListener('click',() => {
      if (dialog.open && node.isConnected) action();
    });
    return node;
  }

  function rememberFocus(trigger) {
    const anchor = trigger instanceof HTMLElement ? trigger : document.activeElement;
    const scroll = [];
    for (let node=anchor; node && node !== document.documentElement; node=node.parentElement) {
      if (node.scrollHeight > node.clientHeight || node.scrollWidth > node.clientWidth) {
        scroll.push([node,node.scrollLeft,node.scrollTop]);
      }
    }
    return {anchor,scroll,x:window.scrollX,y:window.scrollY};
  }

  function restoreFocus(position) {
    const anchor = position.anchor;
    const target = anchor?.isConnected ? anchor : anchor?.id && document.getElementById(anchor.id);
    target?.focus({preventScroll:true});
    for (const [node,left,top] of position.scroll) {
      if (node.isConnected) node.scrollTo(left,top);
    }
    if (window.scrollX !== position.x || window.scrollY !== position.y) window.scrollTo(position.x,position.y);
  }

  function close(restore=true) {
    if (!dialog?.open) return;
    const position = origin;
    dialog.close();
    views = [];
    origin = null;
    if (restore && position) restoreFocus(position);
  }

  function previous() {
    if (views.length === 1) {
      close();
      return;
    }
    views.pop();
    draw();
  }

  function prepare() {
    if (dialog) return;
    dialog = element('dialog');
    dialog.id = 'material-dialog';
    dialog.setAttribute('aria-labelledby','material-titel');
    const head = element('header');
    head.className = 'material-kopf';
    title = element('h2');
    title.id = 'material-titel';
    title.tabIndex = -1;
    back = button('Zurück',previous,'material-zurueck');
    head.append(title,back);
    body = element('div');
    body.className = 'material-inhalt';
    dialog.append(head,body);
    document.body.append(dialog);
    dialog.addEventListener('cancel',event => {
      event.preventDefault();
      previous();
    });
  }

  function begin(view, trigger) {
    prepare();
    if (dialog.open) {
      // A command from the surrounding day picker can arrive while a source is open.
      if (view.type !== views.at(-1).type) child(view,document.activeElement);
      return;
    }
    origin = rememberFocus(trigger);
    views = [view];
    draw();
  }

  function child(view, trigger) {
    const parent = views.at(-1);
    parent.scrollTop = body.scrollTop;
    parent.focusId = trigger?.id;
    views.push(view);
    draw();
  }

  function viewData(context) {
    const task = window.LAURA.stages[context.stageId].levels[context.levelId];
    return context.strategy ? task.strategies[context.strategy] : task.before;
  }

  function cardView(view) {
    const {method,section} = view.ref;
    const card = window.LAURA.cards[method];
    title.textContent = card.title;
    dialog.dataset.method = method;
    if (section) dialog.dataset.section = section;
    let target = title;
    for (const [id,passage] of Object.entries(card.sections)) {
      const entry = element('section');
      entry.dataset.sectionId = id;
      const heading = element('h3',passage.title);
      entry.append(heading,element('p',passage.text));
      if (id === section) {
        entry.dataset.target = 'true';
        heading.tabIndex = -1;
        target = heading;
      }
      body.append(entry);
    }
    return target;
  }

  function cardsView() {
    title.textContent = 'Infokarten';
    const choices = element('div');
    choices.className = 'material-auswahl';
    for (const [id,card] of Object.entries(window.LAURA.cards)) {
      const pick = button(card.title,() => child({type:'card',ref:{method:id}},pick),'material-karte-'+id);
      choices.append(pick);
    }
    body.append(choices);
  }

  function helpView(view) {
    const {context,depth} = view;
    const data = viewData(context);
    title.textContent = 'Hilfe '+(depth+1)+' von '+data.hints.length;
    const hint = element('p',data.hints[depth]);
    hint.id = 'hilfe-text';
    hint.dataset.depth = String(depth+1);
    hint.setAttribute('aria-describedby','material-titel');
    hint.tabIndex = -1;
    body.append(hint);
    const controls = element('div');
    controls.className = 'material-schritte';
    function step(delta) {
      view.depth += delta;
      delete view.focusId;
      view.scrollTop = 0;
      draw();
    }
    if (depth > 0) controls.append(button('Vorherige Hilfe',() => step(-1),'hilfe-zurueck'));
    if (depth+1 < data.hints.length) controls.append(button('Nächste Hilfe',() => step(1),'hilfe-weiter'));
    for (const [i,ref] of [data.card,...(data.extraCards || [])].entries()) {
      const card = window.LAURA.cards[ref.method];
      const label = i ? 'Auch zur Karte „'+card.title+'“' : 'Passende Infokarte öffnen';
      const source = button(label,() => child({type:'card',ref},source),i ? 'hilfe-karte-'+i : 'hilfe-karte');
      source.dataset.method = ref.method;
      source.dataset.section = ref.section;
      controls.append(source);
    }
    body.append(controls);
    return hint;
  }

  function questionsView(view) {
    title.textContent = 'Rückfrage an Laura';
    const questions = viewData(view.context).questions;
    const choices = element('div');
    choices.className = 'material-auswahl';
    for (const item of questions) {
      if (view.context.asked.has(item.id)) continue;
      const ask = button(item.text,() => {
        if (view.context.asked.has(item.id)) return;
        close();
        view.onAsk(item.id);
      });
      ask.dataset.questionId = item.id;
      choices.append(ask);
    }
    if (choices.childElementCount) body.append(choices);
    else body.append(element('p',questions.length ? 'Diese Fragen hast du Laura schon gestellt.' :
      'Für diesen Schritt gibt es gerade keine weitere Rückfrage.'));
  }

  function summaryView() {
    const data = window.LAURA.consolidation;
    title.textContent = 'Gemeinsame Sicherung';
    const facts = element('ul');
    for (const fact of data.facts) facts.append(element('li',fact));
    body.append(facts,element('h3',data.paperField),element('p',data.prompt),element('p',data.compare));
  }

  function draw() {
    const view = views.at(-1);
    dialog.dataset.view = view.type;
    delete dialog.dataset.method;
    delete dialog.dataset.section;
    body.replaceChildren();
    const drawView = {cards:cardsView,card:cardView,help:helpView,questions:questionsView,summary:summaryView};
    if (view.context?.strategy) {
      const chosen = window.LAURA.strategies[view.context.strategy].label;
      const context = element('p','Dein Entwurf · '+chosen);
      context.className = 'material-bezug';
      body.append(context);
    }
    const first = drawView[view.type](view) || title;
    if (!dialog.open) dialog.showModal();
    body.scrollTop = view.scrollTop || 0;
    const focus = view.focusId && document.getElementById(view.focusId);
    (focus || first).focus({preventScroll:true});
    if (!focus && first.closest('[data-target="true"]')) {
      // Only scroll the source. The chat and the input behind the modal stay in place.
      const passage = first.parentElement;
      body.scrollTop += passage.getBoundingClientRect().top - body.getBoundingClientRect().top;
    }
  }

  window.Material = Object.freeze({
    openCards: trigger => begin({type:'cards'},trigger),
    openCard: (ref,trigger) => begin({type:'card',ref},trigger),
    help: (context,trigger) => begin({type:'help',context,depth:0},trigger),
    questions: (context,onAsk,trigger) => begin({type:'questions',context,onAsk},trigger),
    summary: trigger => begin({type:'summary'},trigger),
    close,
    get isOpen() { return Boolean(dialog?.open); }
  });
})();
