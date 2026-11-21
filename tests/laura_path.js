// Measure the same visible path in both built versions, including an optional revision.
({tier, correctFirst=false, stages=5, stepLabel='Laura', returnToOverview=true}) => {
  const find = selector => document.querySelector(selector);
  const press = node => {
    if (!node || node.disabled || !node.getClientRects().length) throw Error('Missing control on Laura path');
    node.click();
  };
  const steps = [], words = [];
  let decisions = 0;
  const keep = () => [...document.querySelectorAll('#work .row button')].find(b=>b.textContent==='Vorschlag beibehalten');
  const wordCount = text => (text.match(/[\p{L}\p{N}]+(?:[-’'][\p{L}\p{N}]+)*/gu) || []).length;
  press(find('#level-'+tier));
  press(find('[data-person=Laura]'));
  for (let index=0; index<stages; index++) {
    const tab = find('#write-answer');
    if (tab.getClientRects().length && tab.getAttribute('aria-pressed')!=='true') press(tab);
    if (find('#step').textContent!==stepLabel+' '+(index+1)+' von '+stages) throw Error('Missing Laura stage '+index);
    const opening = [...document.querySelectorAll('.chat-step')].at(-1).nextElementSibling;
    const task = find('#work > p:not(.preview):not(.response)');
    words.push({
      fall:wordCount([...opening.querySelectorAll('p')].map(p=>p.textContent).join(' ')),
      auftrag:wordCount(task.textContent),
      kartenhinweis:wordCount(find('#card-cue')?.innerText || '')
    });
    const actions = [];
    const count = e => actions.push(e.target.closest('button').textContent);
    find('#room').addEventListener('click', count, true);
    try {
      if (!find('#work .methods, #change-prior')) press(find('#work .primary'));
      else {
        decisions++;
        if (!find('#change-prior')) {
          if (index===0 && correctFirst) {
            press(find('#method-P'));
            press(find('#send'));
            if (!find('#work .response').textContent.includes('Infektionen')) throw Error('Missing STI feedback');
            press([...document.querySelectorAll('#work .row button')].find(b=>b.textContent==='Vorschlag ändern'));
            decisions++;
          }
          press(find('#method-K'));
          press(find('#send'));
        } else if (!find('#work .preview').textContent.includes('Kondom') || !find('#work .response')) {
          throw Error('Missing prior method or response');
        }
        press(keep());
      }
    } finally { find('#room').removeEventListener('click', count, true); }
    steps.push(actions);
  }
  if (find('#task-title').textContent!=='Gespräch abgeschlossen') throw Error('Missing completion');
  if (returnToOverview) press(find('#home-nav'));
  return {steps, total:steps.flat().length, decisions, words};
}
