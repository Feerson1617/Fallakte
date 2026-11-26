// Hinweise werden aus dem aktuellen Entwurf berechnet, Rückmeldungen aus dem geprüften Versuch.
function fehlenderTeil(d){
  if(d.state!=='teilweise'||d.parts.length!==1)return null;
  return d.parts[0]==='a'?1:0;
}
function vergleichstext(q,m,r,d){
  const beispiel=m?m.beispiel:q.grund;
  if(d?.state==='vertauscht')return 'Achte auf die Reihenfolge. '+beispiel;
  let korrektur;
  if(!m)korrektur=q.alternativen.find(a=>a.text===r.choice)?.erklaerung;
  else if(d.error)korrektur=d.quelle?Lernfeedback.gesundheit[d.error].info:m.fehler[d.error];
  return korrektur && !beispiel.includes(korrektur)?beispiel+' '+korrektur:beispiel;
}
function fachhilfe(q,m,r,card,step,karten){
  const d=m?Lernfeedback.analyze(q.modell,r.text):null;
  const ziel=d?.quelle?karten[d.quelle[0]]:card;
  const abschnitt=d?.quelle?.[1]??q.abschnitt;
  const where='Lies auf deiner Infokarte '+ziel.nummer+' – '+ziel.titel+' unter der Überschrift „'+ziel.texte[abschnitt].titel+'“.';
  if(step===1)return where;
  if(step===5)return vergleichstext(q,m,r,d);
  if(!m){
    if(r.choice===q.passend)return 'Deine Auswahl passt. Du kannst weitergehen.';
    const wrong=q.alternativen.find(a=>a.text===r.choice);
    if(wrong && r.repeat)return [wrong.impuls,q.starter,wrong.erklaerung+' Vergleiche mit der Karte.'][step-2];
    return [wrong?.impuls||q.impuls,q.starter,wrong?.erklaerung||q.grund][step-2];
  }
  const missing=fehlenderTeil(d);
  if(d.state==='passend')return 'Du hast beide Schritte verbunden. Du kannst deine Antwort prüfen.';
  if(d.error){
    const fach=d.quelle?Lernfeedback.gesundheit[d.error]:null;
    const frage=fach?.frage||m.fragen[d.error],info=fach?.info||m.fehler[d.error];
    const wieder=r.repeat && r.last?.error===d.error;
    return wieder?[info+' '+frage,'Vergleiche diesen Satz mit der Infokarte.',info][step-2]:
      [frage,info+' '+frage,info][step-2];
  }
  if(d.state==='vertauscht')return [m.zuerst,'Beginne mit der Ursache. Schreibe dann „Dadurch …“.',m.beziehung][step-2];
  if(d.kind==='ergebnis')return [m.impulse[0],m.starter,m.beziehung][step-2];
  if(d.kind==='zusatz')return ['Beide Schritte sind da. Welcher Satz kommt noch dazu?',
    'Vergleiche nur den Zusatz mit der Kartenstelle.','Du kannst deinen Zusatz auch mit dem Beispiel vergleichen.'][step-2];
  if(d.kind==='beziehung')return [m.verknuepfen,'Was geschieht zuerst? Beginne den zweiten Teil mit „Dadurch …“.',m.beziehung][step-2];
  if(d.state==='unsicher')return ['Vergleiche deine Erklärung mit dem Beispiel.',m.vergleich,'Lies deine Antwort noch einmal neben dem Beispiel.'][step-2];
  if(missing!==null)return [m.impulse[missing],(missing===1?'Dadurch … ':'Das liegt daran, dass … ')+m.impulse[missing],m.teile[missing]][step-2];
  return [m.impulse[0],m.starter,m.teile[0]+' '+m.impulse[1]][step-2];
}
function rueckmeldung(q,m,r){
  const d=r.last;
  if(!m){
    if(d.state==='passend')return (r.tries>1?'Jetzt passt deine Wahl. ':'')+q.grund;
    const a=q.alternativen.find(x=>x.text===r.choice);
    return r.repeat?(r.tries>=3?'Vergleiche mit dem Beispiel in Hilfe 5. ':q.starter+' ')+a.impuls:a.erklaerung+' '+a.impuls;
  }
  const known=d.parts.length===1?m.teile[d.parts[0]==='a'?0:1]:'';
  const missing=fehlenderTeil(d);
  if(d.state==='passend'){
    const prev=r.attempts?.at(-2);
    if(prev?.error)return 'Jetzt stimmt der Zusammenhang. '+m.beziehung;
    const added=prev && fehlenderTeil(prev);
    return added===0||added===1?'Jetzt hast du auch das erklärt: '+m.teile[added]:m.beispiel;
  }
  if(d.kind==='ergebnis')return 'Du nennst das Ergebnis. Was passiert vorher mit dem Eisprung und der Eizelle?';
  if(d.state==='leer')return 'Beginne mit einem Stichwort. '+m.impulse[0];
  if(d.state==='vertauscht')return 'Du hast beide Vorgänge genannt. '+m.zuerst;
  if(d.state==='unsicher'){
    const context=d.kind==='zusatz'?'Beide Schritte sind da. Prüfe deinen Zusatz. ':
      d.kind==='beziehung'?'Du hast die Begriffe genannt. ':
      known?'Das erkenne ich: '+known+' ':'';
    return context+'Deine Antwort kann richtig sein. Vergleiche sie mit diesem Beispiel.';
  }
  if(d.error){
    if(d.quelle){
      const fach=Lernfeedback.gesundheit[d.error];
      const teil=known?'Das stimmt: '+known+' ':d.parts.length===2?'Die Erklärung zur Aufgabe passt. ':'';
      return teil+(r.repeat?'Schau auf die genannte Infokarte. ':fach.info+' ')+fach.frage;
    }
    const lead=known?'Das stimmt: '+known+' ':d.parts.length===2?'Beide Schritte sind da. Prüfe deinen Zusatz. ':'';
    if(r.repeat)return lead+(r.tries>=3?'Vergleiche mit dem Beispiel. ':m.fehler[d.error]+' ')+m.fragen[d.error];
    return lead+(known?'Prüfe den anderen Teil. ':m.fehler[d.error]+' ')+m.fragen[d.error];
  }
  if(missing!==null){
    if(r.attempts?.at(-2)?.parts.includes(missing===1?'b':'a'))return 'Jetzt erklärst du: '+known+' Verbinde das mit deiner vorherigen Aussage.';
    return 'Das stimmt: '+known+' '+(r.repeat?(missing===1?'Setze fort: „Dadurch …“':'Setze fort: „Das liegt daran, dass …“'):m.impulse[missing]);
  }
  return 'Vergleiche deine Erklärung mit dem Beispiel.';
}
if(typeof module!=='undefined' && module.exports)module.exports={fachhilfe,rueckmeldung};
