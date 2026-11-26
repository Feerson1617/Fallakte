// Die Anzeige und der maschinenlesbare Scaffoldingvertrag benutzen denselben Auskunftsweg.
function fachhilfe(q,m,r,card,step) {
  const heading=card.texte[q.abschnitt].titel;
  const where='Infokarte '+card.nummer+' – '+card.titel+' · '+heading;
  const d=q.typ==='text'?Lernfeedback.analyze(q.modell,r.text):null;
  const wrong=q.typ==='wahl'?q.alternativen.find(a=>a.text===r.choice):null;
  const missing=d?.parts.includes('a')?1:d?.parts.includes('b')?0:null;
  const think=wrong?.impuls || (d?.error?m.fehler[d.error]+' '+m.impulse[missing??0]:
    (m?m.impulse[missing??0]:q.impuls));
  const specific=wrong?.erklaerung || (m?(d?.error?m.fehler[d.error]:m.teile[missing??1]):q.grund);
  return [where,think,m?(missing!==null?m.impulse[missing]+' '+(missing===1?'Dadurch …':'Das liegt daran, dass …'):m.starter):q.starter,
    specific,m?m.beispiel:q.grund][step-1];
}
function rueckmeldung(q,m,r){
  const d=r.last;
  if(q.typ==='wahl'){
    if(d.state==='passend')return (r.tries>1?'Jetzt passt die Erklärung. ':'')+q.grund;
    const a=q.alternativen.find(x=>x.text===r.choice);
    return r.repeat?'Schau auf die markierte Kartenstelle. '+a.impuls:a.erklaerung+' '+a.impuls;
  }
  const known=d.parts.length?m.teile[d.parts[0]==='a'?0:1]:'';
  const missing=d.parts.includes('a')?1:0;
  if(d.state==='passend')return (r.tries>1?'Jetzt hast du den Zusammenhang erklärt. ':'')+m.beispiel;
  if(d.state==='leer')return 'Beginne mit einem Stichwort. '+m.impulse[0];
  if(d.state==='unsicher')return (known?'Diesen Teil erkenne ich: '+known+' ':'')+'Ich kann die Erklärung noch nicht sicher prüfen. Vergleiche sie mit dem Beispiel.';
  if(d.state==='widerspruch')return r.repeat?
    'Vergleiche deine beiden Aussagen. '+m.fehler[d.error]+' '+m.impulse[missing]:
    'Das stimmt: '+known+' Prüfe den anderen Teil: '+m.fehler[d.error];
  if(d.state==='teilweise'){
    const previous=r.attempts?.at(-2);
    if(previous?.parts.includes(missing===1?'b':'a'))return 'Jetzt erklärst du: '+known+' Verbinde das mit deiner vorherigen Aussage.';
    return 'Das stimmt: '+known+' '+(r.repeat?m.starter:m.impulse[missing]);
  }
  return r.repeat?m.fehler[d.error]+' '+m.starter:m.fehler[d.error]+' '+m.impulse[0];
}
if(typeof module!=='undefined' && module.exports)module.exports={fachhilfe,rueckmeldung};
