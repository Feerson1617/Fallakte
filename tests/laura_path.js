// Complete the simple case using visible controls. Count content actions after opening Laura.
({tier, correctFirst=false}) => {
  const find = selector => document.querySelector(selector);
  const press = node => {
    if (!node || node.disabled || !node.getClientRects().length) throw Error('Missing control on Laura path');
    node.click();
  };
  const counts = [];
  const keep = () => [...document.querySelectorAll('#work .row button')].find(b=>b.textContent==='Vorschlag beibehalten');
  press(find('#level-'+tier));
  press(find('[data-person=Laura]'));
  for (let index=0; index<7; index++) {
    const tab = find('#write-answer');
    if (tab.getClientRects().length && tab.getAttribute('aria-pressed')!=='true') press(tab);
    if (find('#step').textContent!=='Schritt '+(index+1)+' von 7') throw Error('Missing Laura stage '+index);
    const actions = [];
    const count = e => actions.push(e.target.closest('button').textContent);
    find('#room').addEventListener('click', count, true);
    try {
      if (index===2) press(find('#work .primary'));
      else {
        if (!find('#change-prior')) {
          if (index===0 && correctFirst) {
            press(find('#method-P'));
            press(find('#send'));
            if (!find('#work .response').textContent.includes('Infektionen')) throw Error('Missing STI feedback');
            press([...document.querySelectorAll('#work .row button')].find(b=>b.textContent==='Vorschlag ändern'));
          }
          press(find('#method-K'));
          press(find('#send'));
        } else if (!find('#work .preview').textContent.includes('Kondom') || !find('#work .response')) {
          throw Error('Missing prior method or response');
        }
        press(keep());
      }
    } finally { find('#room').removeEventListener('click', count, true); }
    counts.push(actions);
  }
  if (find('#task-title').textContent!=='Gespräch abgeschlossen') throw Error('Missing completion');
  press(find('#home-nav'));
  return {steps:counts, total:counts.flat().length};
}
