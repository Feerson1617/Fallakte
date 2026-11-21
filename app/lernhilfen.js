// Modules supply ordered hints, a source and an optional action for the last step.
function levelText(value, level) {
  return typeof value === 'string' || Array.isArray(value) ? value : value[level];
}

function renderHelp(panel, entry, steps, depth, changeDepth, source, action) {
  const openLabels=['Du kommst nicht weiter? – Hilfe anzeigen','Zweite Hilfe','Satzanfang zeigen','Beispiel zeigen','Nächsten Schritt zeigen'];
  const titles=['Hilfe 1 · Nachschlagen','Hilfe 2 · Fachinformation','Satzanfang','Eine mögliche Begründung','So kannst du weiterarbeiten'];
  entry.hidden=false;
  if (depth>1) {
    const previous=button('Zurück',()=>changeDepth(depth-1),'text-button');
    previous.setAttribute('aria-label','Vorherige Hilfe');
    entry.append(previous);
  }
  if (depth < steps.length) {
    const next=button(openLabels[depth],()=>changeDepth(depth+1),'help-trigger','help');
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
    hint.append(el('small','',titles[i]),el('p','',steps[i]));
    if (i===depth-1) {hint.id='hint-current';hint.tabIndex=-1;}
    notes.append(hint);
  }
  if (depth===steps.length && action) {
    const apply=button(action.label,action.run,'outline');
    apply.id='help-action';
    notes.append(apply);
  }
  notes.append(button(source.label,source.open,'text-button','book'));
  const close=button('Schließen',()=>changeDepth(0),'text-button');
  close.setAttribute('aria-label','Hilfe schließen');
  entry.append(close);
  panel.append(notes);
}
