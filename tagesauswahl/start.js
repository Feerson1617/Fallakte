(() => {
  const menu = document.getElementById('auswahl');
  const workspace = document.getElementById('arbeitsplatz');
  const actions = document.getElementById('modulaktionen');
  const status = document.getElementById('gespraechsstand');
  const entries = new Map();
  let current;

  const icons = {
    folder: 'M3 7V5h6l2 2h10v13H3z M3 10h18',
    book: 'M12 6Q7 3 2 5v14q5-2 10 1 5-3 10-1V5q-5-2-10 1z M12 6v14',
    restart: 'M4 10a8 8 0 1 1 1 8 M4 4v6h6'
  };
  function symbol(key) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg','svg');
    const path = document.createElementNS(svg.namespaceURI,'path');
    svg.setAttribute('aria-hidden','true');
    svg.setAttribute('viewBox','0 0 24 24');
    path.setAttribute('d',icons[key]);
    svg.append(path);
    return svg;
  }

  function showState(entry) {
    for (const button of actions.children) {
      if (button.dataset.action === entry.active) button.setAttribute('aria-current','page');
      else button.removeAttribute('aria-current');
    }
    if (status.textContent !== entry.status) status.textContent = entry.status;
    status.hidden = !entry.status;
  }

  function showActions(entry) {
    actions.replaceChildren();
    for (const {id,label,icon} of entry.actions) {
      const button = document.createElement('button');
      button.type = 'button';
      button.dataset.action = id;
      if (Object.hasOwn(icons,icon)) button.append(symbol(icon));
      button.append(label);
      button.onclick = () => entry.port.postMessage(id);
      actions.append(button);
    }
    showState(entry);
  }

  function connect(entry) {
    entry.port?.close();
    entry.actions = [];
    entry.active = '';
    entry.status = '';
    if (entry === current) showActions(entry);
    const channel = new MessageChannel();
    entry.port = channel.port1;
    entry.port.onmessage = ({data}) => {
      if (data.type === 'ready') {
        entry.frame.style.visibility = '';
        entry.actions = data.actions;
        if (entry === current) showActions(entry);
      } else if (data.type === 'view') {
        entry.active = data.active;
        entry.status = data.status;
        if (entry === current) showState(entry);
      }
    };
    // The target is our specific frame. Local files can have an opaque origin.
    entry.frame.contentWindow.postMessage('fallakte:navigation','*',[channel.port2]);
  }

  function createEntry(card) {
    const frame = document.createElement('iframe');
    const entry = {card, frame, actions:[], active:'', status:''};
    // Show modules with their own fallback header only after they have handed
    // navigation over. This avoids painting two bars during the first load.
    if (card.hasAttribute('data-modulnavigation')) frame.style.visibility = 'hidden';
    frame.title = card.querySelector('.beschriftung').textContent.trim();
    frame.addEventListener('load', () => connect(entry));
    const payload = document.getElementById(card.dataset.entry);
    if (payload) {
      const bytes = Uint8Array.from(atob(payload.textContent), char => char.charCodeAt(0));
      frame.srcdoc = new TextDecoder().decode(bytes);
    } else {
      frame.src = card.dataset.entry;
    }
    entries.set(card,entry);
    workspace.append(frame);
    return entry;
  }

  for (const card of menu.querySelectorAll('button[data-entry]')) {
    card.addEventListener('click', () => {
      if (card.disabled) return;
      menu.hidden = true;
      workspace.hidden = false;
      current = entries.get(card) || createEntry(card);
      current.frame.hidden = false;
      showActions(current);
      current.frame.focus();
    });
  }
  document.getElementById('zurueck').addEventListener('click', () => {
    current.frame.hidden = true;
    workspace.hidden = true;
    menu.hidden = false;
    current.card.focus();
    current = null;
  });
})();
