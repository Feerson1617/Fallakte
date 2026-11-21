'use strict';

const paths = {
  chat:'M4 4h12a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H9l-5 4v-4H3a1 1 0 0 1-1-1V6a2 2 0 0 1 2-2z M20 9h1v11l-4-3h-3',
  folder:'M3 7V5a1 1 0 0 1 1-1h6l2 3h8a1 1 0 0 1 1 1v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z M3 9h18',
  book:'M12 6C8 4 5 4 2 5v14c3-1 6-1 10 1 4-2 7-2 10-1V5c-3-1-6-1-10 1z M12 6v14',
  group:'M15 20v-2a5 5 0 0 0-5-5H8a5 5 0 0 0-5 5v2 M9 10a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z M16 4a3 3 0 0 1 0 6 M18 14a5 5 0 0 1 3 5',
  layers:'m12 3 9 5-9 5-9-5 9-5z M3 12l9 5 9-5 M3 16l9 5 9-5',
  pencil:'m4 16 11-11 4 4L8 20l-5 1 1-5z M13 7l4 4 M16 4l1-1a2 2 0 0 1 3 0l1 1a2 2 0 0 1 0 3l-1 1',
  next:'M4 12h15m-6-6 6 6-6 6', back:'M20 12H5m6 6-6-6 6-6', down:'M12 4v16m-6-6 6 6 6-6',
  help:'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z M9.5 9a2.5 2.5 0 1 1 4 2c-1 .7-1.5 1.1-1.5 2.5 M12 17h.01',
  send:'m3 3 19 9-19 9 3-9-3-9z M6 12h13'
};
function icon(name) {
  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns,'svg');
  svg.setAttribute('viewBox','0 0 24 24');
  svg.setAttribute('aria-hidden','true');
  const path = document.createElementNS(ns,'path');
  path.setAttribute('d',paths[name]);
  svg.append(path);
  return svg;
}
function el(tag, cls, text) {
  const element = document.createElement(tag);
  if (cls) element.className = cls;
  if (text !== undefined) element.textContent = text;
  return element;
}
function button(label, action, cls, symbol) {
  const b = el('button', cls, label);
  b.type = 'button';
  if (symbol) b.append(icon(symbol));
  b.onclick = action;
  return b;
}
