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
    const sources=trigger?.closest?.('.quellenwahl[open]');
    if(sources){
      sources.open=false;
      Arbeitsplatz.refresh();
      origin=rememberFocus(sources.querySelector('summary'));
    }else origin=rememberFocus(trigger);
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

  function cardLabel(ref) {
    const card=window.LAURA.cards[ref.method];
    return card.title+' · '+card.sections[ref.section].title;
  }

  function cardView(view) {
    const {method,section} = view.ref;
    const card = window.LAURA.cards[method];
    title.textContent = card.title;
    dialog.dataset.method = method;
    if (section) dialog.dataset.section = section;
    let target = title;
    const passages = section ? [[section,card.sections[section]]] : Object.entries(card.sections);
    const short = section && (view.levelId === 'Foerder' || view.levelId === 'ESA');
    for (const [id,passage] of passages) {
      const entry = element('section');
      entry.dataset.sectionId = id;
      const heading = element('h3',passage.title);
      entry.append(heading,element('p',passage.levels?.[view.levelId] || (short && passage.shortText ? passage.shortText : passage.text)));
      if (id === section) {
        entry.dataset.target = 'true';
        const image=window.LAURA.kartenbilder[method]?.[id];
        if(image){
          const figure=element('figure');
          figure.className='kartenbild';
          const graphic=new DOMParser().parseFromString(image.svg.replace('<svg ','<svg xmlns="http://www.w3.org/2000/svg" '),'image/svg+xml').documentElement;
          figure.append(document.importNode(graphic,true),element('figcaption',image.caption));
          entry.append(figure);
        }
        heading.tabIndex = -1;
        target = heading;
      }
      body.append(entry);
    }
    if (section) {
      const more = button('Ganze Karte lesen',() => child({type:'card',ref:{method},levelId:view.levelId},more),'material-ganze-karte');
      body.append(more);
    }
    return target;
  }

  function cardsView(view) {
    title.textContent = 'Infokarten';
    const choices = element('div');
    choices.className = 'material-auswahl';
    for (const [id,card] of Object.entries(window.LAURA.cards)) {
      const pick = button(card.title,() => child({type:'card',ref:{method:id},levelId:view.levelId},pick),'material-karte-'+id);
      choices.append(pick);
    }
    body.append(choices);
  }

  function helpView(view) {
    const {context,depth} = view;
    const data = viewData(context);
    title.textContent = 'Hilfe '+(depth+1)+' von '+data.hints.length;
    const issue=context.error, feedback=context.feedback;
    const focusCard=issue?.ref || feedback?.card || data.card;
    const targeted=issue || ['A','B'].includes(feedback?.type);
    const hints=targeted?Entwurf.hilfen(cardLabel(focusCard),issue?.frage ||
      (feedback.type==='B'?'Welches Anliegen bleibt bei deinem Rat offen?':'Welche Aussage auf der Karte passt zu deiner Wahl?'),
      issue?.info||feedback.text,issue):context.diagnose?.hints||data.hints;
    const hint = element('p',hints[depth]);
    hint.id = 'hilfe-text';
    hint.dataset.depth = String(depth+1);
    hint.setAttribute('aria-describedby','material-titel');
    hint.tabIndex = -1;
    body.append(hint);
    const passage=window.LAURA.cards[focusCard?.method]?.sections[focusCard?.section];
    const source=issue?.info||passage?.levels?.[context.levelId]||passage?.shortText||passage?.text;
    if(source && !hint.textContent.includes(source)){
      const excerpt=element('p',source);excerpt.className='hilfsquelle';body.append(excerpt);
    }
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
    if (data.freeCards && !targeted) {
      const browse = button('Infokarte auswählen',() => child({type:'cards',levelId:context.levelId},browse),'hilfe-kartenauswahl');
      controls.append(browse);
    } else {
      for (const [i,ref] of (targeted?[focusCard]:[data.card,...(data.extraCards || [])]).entries()) {
        const source = button(cardLabel(ref),() => child({type:'card',ref,levelId:context.levelId},source),i ? 'hilfe-karte-'+i : 'hilfe-karte');
        source.dataset.method = ref.method;
        source.dataset.section = ref.section;
        controls.append(source);
      }
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

  function finalAdvice(levelId) {
    const {finalAdvice:advice,prompt,compare} = window.LAURA.consolidation;
    const instructions = element('div');
    instructions.className = 'schlussrat-impulse';
    if (!advice) {
      instructions.append(element('p',prompt),element('p',compare));
      return instructions;
    }
    const level = advice.levels[levelId];
    const stems = element('ul');
    for (const stem of level?.stems || advice.stems) stems.append(element('li',stem));
    instructions.append(stems);
    if (level) instructions.append(element('p',level.focus));
    instructions.append(element('p',advice.compare));
    return instructions;
  }

  function summaryView(view) {
    const data = window.LAURA.consolidation;
    title.textContent = 'Gemeinsame Sicherung';
    const facts = element('ul');
    for (const fact of data.facts) facts.append(element('li',fact));
    body.append(facts,element('h3',data.paperField));
    const level=view.levelId || 'Foerder';
    body.append(element('p',window.LAURA.stages.L05.levels[level].task),finalAdvice(level));
  }

  function draw() {
    const view = views.at(-1);
    dialog.dataset.view = view.type;
    delete dialog.dataset.method;
    delete dialog.dataset.section;
    body.replaceChildren();
    const drawView = {orientation:v=>{
      title.textContent=v.steps?'Hilfe '+(v.depth+1)+' von '+v.steps.length:'Hilfe';
      body.append(element('p',v.steps?v.steps[v.depth]:v.text));
      if(v.steps && v.depth<v.steps.length-1)body.append(button('Nächste Hilfe',()=>{v.depth++;draw();},'spur-mehr'));
    },cards:cardsView,card:cardView,help:helpView,questions:questionsView,summary:summaryView};
    if (view.context?.strategy) {
      const task = window.LAURA.stages[view.context.stageId].levels[view.context.levelId];
      const chosen = task.choiceLabels?.[view.context.strategy] || window.LAURA.strategies[view.context.strategy].label;
      const context = element('p','Dein Entwurf · '+chosen);
      context.className = 'material-bezug';
      body.append(context);
    }
    const first = drawView[view.type](view) || title;
    if (!dialog.open) dialog.showModal();
    dialog.dataset.hilfe=String(['help','orientation'].includes(view.type));
    Arbeitsplatz.prepareDialog(dialog,body);
    body.scrollTop = view.scrollTop || 0;
    const focus = view.focusId && document.getElementById(view.focusId);
    (focus || first).focus({preventScroll:true});
  }

  window.Material = Object.freeze({
    impuls:(text,steps)=>begin({type:'orientation',text,steps,depth:0},document.getElementById('spur-hilfe')),
    orient:(text,trigger)=>begin({type:'orientation',text},trigger),
    cardLabel,
    finalAdvice,
    openCards: (trigger,levelId) => begin({type:'cards',levelId},trigger),
    openCard: (ref,trigger,levelId) => begin({type:'card',ref,levelId},trigger),
    help: (context,trigger) => begin({type:'help',context,depth:0},trigger),
    questions: (context,onAsk,trigger) => begin({type:'questions',context,onAsk},trigger),
    summary: (trigger,levelId) => begin({type:'summary',levelId},trigger),
    close,
    get isOpen() { return Boolean(dialog?.open); }
  });
})();
