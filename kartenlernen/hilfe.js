// Hinweise werden aus dem aktuellen Entwurf berechnet, Rückmeldungen aus dem geprüften Versuch.
function fehlenderTeil(d){
  if(d.parts.length!==1)return null;
  return d.parts[0]==='a'?1:0;
}
function fachhilfe(q,m,r,card,step){
  const where='Lies auf deiner Infokarte '+card.nummer+' – '+card.titel+' unter der Überschrift „'+card.texte[q.abschnitt].titel+'“.';
  if(step===1)return where;
  if(step===5)return m?m.beispiel:q.grund;
  if(!m){
    if(r.choice===q.passend)return 'Deine Auswahl passt. Du kannst weitergehen.';
    const wrong=q.alternativen.find(a=>a.text===r.choice);
    if(wrong && r.repeat)return [wrong.impuls,q.starter,wrong.erklaerung+' Vergleiche mit der Karte.'][step-2];
    return [wrong?.impuls||q.impuls,q.starter,wrong?.erklaerung||q.grund][step-2];
  }
  const d=Lernfeedback.analyze(q.modell,r.text),missing=fehlenderTeil(d);
  if(d.state==='passend')return 'Du hast beide Schritte verbunden. Du kannst deine Antwort prüfen.';
  if(d.error && r.repeat && r.last?.error===d.error){
    return [m.fragen[d.error]+' '+m.fehler[d.error],m.starter,m.fehler[d.error]+' Vergleiche mit der markierten Kartenstelle.'][step-2];
  }
  if(d.error)return [m.fragen[d.error],m.fehler[d.error]+' '+m.fragen[d.error],m.fehler[d.error]][step-2];
  if(d.kind==='zusatz')return ['Beide Schritte sind da. Welcher Satz kommt noch dazu?',
    'Vergleiche nur den Zusatz mit der Kartenstelle.','Du kannst deinen Zusatz auch mit dem Beispiel vergleichen.'][step-2];
  if(d.kind==='beziehung')return [m.verknuepfen,'Was geschieht zuerst? Beginne den zweiten Teil mit „Dadurch …“.',m.beziehung][step-2];
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
  if(d.state==='leer')return 'Beginne mit einem Stichwort. '+m.impulse[0];
  if(d.state==='unsicher'){
    const context=d.kind==='zusatz'?'Beide Schritte sind da. Prüfe deinen Zusatz. ':
      d.kind==='beziehung'?(d.relation==='umgekehrt'?'Prüfe die Reihenfolge. ':'Du hast die Begriffe genannt. ')+m.verknuepfen+' ':
      known?'Das erkenne ich: '+known+' ':'';
    return context+'Deine Antwort kann richtig sein. Vergleiche sie mit diesem Beispiel.';
  }
  if(d.error){
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
