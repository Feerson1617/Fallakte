// Only the enclosing Fallakte can take over the standalone preparation header.
window.addEventListener('message', event => {
  if (event.source !== parent || event.data !== 'fallakte:navigation' || !event.ports[0]) return;
  const port = event.ports[0];
  const overview = document.querySelector('#overview');
  const level = document.querySelector('#level-name');
  document.querySelector('body > header').hidden = true;
  let homeAvailable, shownLevel;
  function publish() {
    const available = !overview.hidden;
    if (available !== homeAvailable) {
      const actions = available ? [{id:'home', label:'Übersicht', icon:'folder'}] : [];
      port.postMessage({type:'ready', actions});
      homeAvailable = available;
    }
    if (shownLevel !== level.textContent) {
      shownLevel = level.textContent;
      port.postMessage({type:'view', active:'', status:shownLevel});
    }
  }
  port.onmessage = ({data}) => {
    if (data === 'home' && !overview.hidden) overview.click();
  };
  const observer = new MutationObserver(publish);
  observer.observe(overview, {attributes:true, attributeFilter:['hidden']});
  observer.observe(level, {childList:true, characterData:true, subtree:true});
  publish();
});
