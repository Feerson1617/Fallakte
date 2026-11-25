// Prüfbrowser: Lese den Modultext und die sichtbare Navigation seiner Elternrahmen.
() => {
  const text = [];
  let frame = window;
  while (true) {
    const doc = frame.document;
    const area = doc.querySelector('dialog[open]') || doc.body;
    const words = area.innerText.trim();
    if (words) text.unshift(words);
    if (doc.getElementById('auswahl') || frame === frame.parent) break;
    frame = frame.parent;
  }
  return text.join('\n\n');
}
