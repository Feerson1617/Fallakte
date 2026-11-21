(() => {
  const menu = document.getElementById('auswahl');
  const workspace = document.getElementById('arbeitsplatz');
  const returnNav = workspace.querySelector('nav');
  const first = document.getElementById('erster-tag');
  const frames = new Map();
  let current;

  function createFrame(card) {
    const frame = document.createElement('iframe');
    frame.title = card.querySelector('.beschriftung').textContent.trim();
    const payload = document.getElementById(card.dataset.entry);
    if (payload) {
      const bytes = Uint8Array.from(atob(payload.textContent), char => char.charCodeAt(0));
      frame.srcdoc = new TextDecoder().decode(bytes);
    } else {
      frame.src = card.dataset.entry;
    }
    if (card === first) {
      frame.addEventListener('load', () => {
        // Offer the return at the existing overview only; the work area gets the full viewport.
        const overview = frame.contentDocument?.getElementById('home');
        if (!overview) return;
        const sync = () => { if (current === card) returnNav.hidden = overview.hidden; };
        new MutationObserver(sync).observe(overview, {attributes: true, attributeFilter: ['hidden']});
        sync();
      });
    }
    workspace.append(frame);
    frames.set(card, frame);
    return frame;
  }

  for (const card of menu.querySelectorAll('button[data-entry]')) {
    card.addEventListener('click', () => {
      if (card.disabled) return;
      current = card;
      menu.hidden = true;
      workspace.hidden = false;
      returnNav.hidden = false;
      const frame = frames.get(card) || createFrame(card);
      frame.hidden = false;
      frame.focus();
    });
  }
  document.getElementById('zurueck').addEventListener('click', () => {
    frames.get(current).hidden = true;
    workspace.hidden = true;
    menu.hidden = false;
    current.focus();
    current = null;
  });
})();
