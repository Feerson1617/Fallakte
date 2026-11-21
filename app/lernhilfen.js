// A module supplies its own source, feedback and ordered hints; the panel only handles disclosure.
function levelText(value, level) {
  return typeof value === 'string' || Array.isArray(value) ? value : value[level];
}

function renderHelp(panel, entry, steps, depth, changeDepth, source) {
  const labels=['Hilfe','Zweite Hilfe','Satzanfang zeigen'];
  if (depth < steps.length) {
    const next=button(labels[depth],()=>changeDepth(depth+1),'text-button','help');
    next.id='help';
    next.setAttribute('aria-controls',panel.id);
    next.setAttribute('aria-expanded',String(depth>0));
    entry.append(next);
  }
  if (!depth) return;
  panel.hidden=false;
  const notes=el('div','help-notes');
  for (let i=0;i<depth;i++) {
    const hint=el('div','hint');
    hint.append(el('small','',i===2?'Satzanfang':('Hilfe '+(i+1))),el('p','',steps[i]));
    if (i===depth-1) {hint.id='hint-current';hint.tabIndex=-1;}
    notes.append(hint);
  }
  notes.append(button(source.label,source.open,'text-button','book'));
  const close=button('Schließen',()=>changeDepth(0),'text-button');
  close.setAttribute('aria-label','Hilfe schließen');
  entry.append(close);
  panel.append(notes,entry);
}
