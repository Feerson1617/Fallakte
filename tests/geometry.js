// Measurements in the SCO's own CSS pixels, clipped to the frame and scroll panes.
() => {
  const root = document.documentElement;
  const visible = e => e && e.getClientRects().length && getComputedStyle(e).visibility === 'visible';
  function box(e, clip) {
    if (!e) return null;
    const r = e.getBoundingClientRect();
    const top = Math.max(0, r.top, clip?.top ?? 0);
    const bottom = Math.min(innerHeight, r.bottom, clip?.bottom ?? innerHeight);
    return {x:r.x, y:r.y, width:r.width, height:r.height,
      visibleHeight:visible(e) ? Math.max(0, bottom-top) : 0};
  }
  const history = document.querySelector('#history');
  const work = document.querySelector('#work');
  const steps = history.querySelectorAll('.chat-step');
  const latestMessage = steps[steps.length-1].nextElementSibling;
  const send = document.querySelector('#send');
  const rect = send?.getBoundingClientRect();
  const touchOrTextIssues = [];
  for (const e of document.querySelectorAll('nav button,#room button,#room label,#room select,#room p,.bubble,.hint,.room-meta,#work,#history')) {
    if (!visible(e)) continue;
    const r = e.getBoundingClientRect();
    const small = e.matches('button,label,select') && (r.width < 43.9 || r.height < 43.9);
    if (small || e.scrollWidth > e.clientWidth + 2) touchOrTextIssues.push(e.id || e.textContent.slice(0,60));
  }
  return {
    viewport:[innerWidth,innerHeight], document:[root.scrollWidth,root.scrollHeight], global:[scrollX,scrollY],
    chat:box(history), answer:box(work.parentElement), work:box(work),
    message:box(latestMessage,history.getBoundingClientRect()), hint:box(document.querySelector('#hint-current'),work.getBoundingClientRect()),
    send:box(send), sendReachable:!!rect && send.contains(document.elementFromPoint(rect.x+rect.width/2,rect.y+rect.height/2)),
    scrollHistory:history.scrollTop, scrollWork:work.scrollTop, focus:document.activeElement.id, touchOrTextIssues
  };
}
