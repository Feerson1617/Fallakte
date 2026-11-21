// The SCO owns a single LMS session from the date screen to page exit.
(() => {
  function findLms(start) {
    let frame = start;
    for (let depth = 0; frame && depth < 32; depth++) {
      try {
        if (typeof frame.API?.LMSInitialize === 'function') return frame.API;
        if (frame.parent === frame) break;
        frame = frame.parent;
      } catch { break; }
    }
    return null;
  }
  const direct = window.API;
  let active = null;
  function begin() {
    if (active) return;
    try {
      const lms = direct || (parent !== window && findLms(parent)) || findLms(window.opener);
      if (lms && String(lms.LMSInitialize('')) === 'true') active = lms;
    } catch { /* The offline file works without an LMS. */ }
  }
  // The frozen module looks up API in its parent. Its lifecycle belongs to this SCO.
  window.API = {
    LMSInitialize: () => { begin(); return String(Boolean(active)); },
    LMSFinish: () => 'true'
  };
  begin();
  window.addEventListener('pageshow', begin);
  window.addEventListener('pagehide', () => {
    try { active?.LMSFinish(''); } catch { /* An LMS host may already be closed. */ }
    active = null;
  });
})();
