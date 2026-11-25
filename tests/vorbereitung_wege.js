(function ({lesson,cards,ui,level,assisted,embedded=false}) {
  const logs=[],screens=[],home=()=>click('home');
  let clicks=0,where=level;
  const one=sel=>document.querySelector(sel);
  const all=sel=>[...document.querySelectorAll(sel)];
  const element=(action,value)=>one(`[data-do="${action}"]${value===undefined?'':`[data-value="${value}"]`}`);
  function ok(value,msg){if(!value)throw new Error(`${where}: ${msg}`);}
  function click(action,value){
    const b=element(action,value);ok(b&&!b.disabled&&b.getClientRects().length,`Bedienung ${action}/${value}`);
    b.click();clicks++;
  }
  function visible(text,root='#view'){ok(one(root).innerText.includes(text),'Text: '+text);}
  function save(part){if(!assisted)screens.push({Niveau:level,Abschnitt:where,Schritt:part,Bildschirm:one('#view').innerText});}
  function code(value){
    const input=one('#code');ok(input,'Codefeld fehlt');
    input.value=value;input.dispatchEvent(new Event('input',{bubbles:true}));clicks++;
  }
  function enter(q,i,paper){
    if(paper)code(' '+q.options[i].code.toLowerCase()+' ');
    else click('choice',i);
  }
  function hints(list){
    for(const [i,text] of list.entries()){
      click('hint');visible('Hilfe '+(i+1)+' von 5');visible(text,'.tip');
    }
    ok(!element('hint'),'Mehr als fünf Hilfen');
  }
  function solve(q,paper=false){
    where=q.id;
    const check=paper?'code-check':'check';
    const idx=q.options.findIndex(o=>o.correct);
    ok(element(check).disabled,'Prüfung ohne Auswahl');
    if(paper){
      ok(element('send').disabled,'Vorzeitige Sendefreigabe');
      const fallback=one('#view details');
      ok(!fallback.open && fallback.querySelector('summary').textContent.includes('Ausfallhilfe'),'Papiercheck muss auf Papier beginnen');
      fallback.querySelector('summary').click();
      ok(JSON.stringify([...fallback.querySelectorAll('li')].map(li=>li.textContent))===JSON.stringify(q.options.map(o=>o.text)),'Digitale Ausfallhilfe in Druckreihenfolge');
      fallback.querySelector('summary').click();
      ok(!fallback.open && element('send').disabled,'Ausfallhilfe schaltete Senden frei');
    }
    else{
      ok(!one('[data-field]'),'Zu früh freigegebene Karte');
      ok(JSON.stringify(all('.answers button').map(b=>b.textContent))===JSON.stringify(q.options.map(o=>o.text)),'Antwortreihenfolge');
      if(assisted){click('material');ok(one('#sheet').open,'Nachlesen');one('#close-sheet').click();}
    }
    save('Auftrag');
    if(assisted){
      hints(q.hintsBeforeChoice);
      for(const [i,o] of q.options.entries()){
        if(o.correct)continue;
        enter(q,i,paper);ok(!one('.feedback')&&!one('.help .tip'),'Veraltete Rückmeldung');
        click(check);visible(o.feedback,'.feedback');
        ok(!element('advance')&&!element('finish'),'Fehlantwort gibt Kapitel frei');
        if(paper)ok(element('send').disabled,'Falscher Code schaltete Senden frei');
        click('material');one('#close-sheet').click();visible(o.feedback,'.feedback');
        hints(o.hints);
      }
    }
    enter(q,idx,paper);click(check);visible(q.options[idx].feedback);
    if(assisted){
      const ext=q.afterSolutionCheck;
      visible(ext.prompt,'#application');
      ok(!element('advance')&&(!paper||element('send').disabled),'Anwendung umgangen');
      for(const [i,o] of ext.options.entries()){
        if(o.correct)continue;
        click('extra-choice',i);click('extra-check');visible(o.feedback,'#application');
        ok(!element('advance')&&(!paper||element('send').disabled),'Falsche Anwendung akzeptiert');
      }
      const correct=ext.options.findIndex(o=>o.correct);
      click('extra-choice',correct);click('extra-check');visible(ext.options[correct].feedback,'#application');
      visible('Mit Lösungshilfe und eigener Anwendung gelöst.');
    }else{
      ok(!one('#application'),'Unerbetene Zusatzfrage');visible('Selbstständig gelöst.');
    }
    save('Rückmeldung');
    if(paper){
      const send=element('send');click('send');send.click();
      ok(!element('send')&&one('#view').innerText.split('Nachricht gesendet').length===2,'Doppelversand');
      save('Nachricht gesendet');click('finish');
    }else click('advance');
    logs.push({Frage:q.id,Fehlantworten:assisted?q.options.filter(o=>!o.correct).length:0,Anwendung:assisted});
  }
  click('level',level);click('new');visible(lesson.intro.information);
  save('Pearl-Index');click('begin');solve(lesson.intro.question);
  const counts={};
  for(const ch of lesson.chapters){
    where=ch.id;const start=clicks;
    visible(ch.title);visible(ch.id+' auf deinem Laufzettel.','p.paper');
    for(const info of ch.information)visible(info.text,'.material');
    if(ch.supportingInfo)visible(ch.supportingInfo);
    ok(one('figure svg')&&!one('[data-field]'),'Orientierung und Grafik');
    save('Orientierung und Information');
    click('begin');
    for(const q of ch.questions)solve(q);
    where=ch.id;
    visible(ch.paperPrompt);
    const exact=all('.fields li').map(li=>[li.dataset.field,li.querySelector('b').textContent]);
    ok(JSON.stringify(exact)===JSON.stringify(ch.cardEntries.map(e=>[e.fieldId,e.exactEntry])),'Karteneinträge');
    save('Papierauftrag und Rückkehr');
    if(ch.paperCheck){solve(ch.paperCheck,true);}
    else{
      ok(!one('#code'),'Unerwarteter Code');
      if(ch.id.endsWith('B')){
        ok(element('review').textContent==='Vollständige Karte vergleichen','Rückweg zur Vollkarte');
        click('review');const card=cards.find(k=>k.method===ch.method);
        for(const section of card.sections)visible(section.completedText,'.reference');
        ok(all('.fields [data-field]').length===4,'Vollkarte');
        visible('Karte kontrolliert');ok(element('finish').textContent==='Weiter im Chat','Rückweg nach Kartenkontrolle');save('Kartenkontrolle');
      }
      click('finish');
    }
    counts[ch.id]=clicks-start;
    if(ch.id==='2B'){
      visible('Ende der ersten Vorbereitungsstunde','h1');
      visible('Du hast Kondom und Kombinationspille bearbeitet.');
      ok(one('#checked-chapters').innerText==='1A, 1B, 2A, 2B','Fachchecks der ersten Stunde');
      save('Zwischenansicht nach 2B');click('open','3A');
    }
    if(ch.id==='4B'){
      visible('Abschluss der Vorbereitung','h1');
      ok(one('#checked-chapters').innerText===lesson.chapters.map(c=>c.id).join(', '),'Fachchecks beider Stunden');
      ok(all('#view [data-do="reference"]').length===4,'Vier Musterkarten am Ende');
      save('Abschlussansicht nach 4B');click('picker');
    }
  }
  visible(ui.picker);ok(all('.chapters small').filter(s=>s.textContent==='In dieser Sitzung bearbeitet').length===8,'Abschlussstatus');
  // In der Tagesauswahl bedient der Browser-Test die gemeinsame Übersicht.
  if(!embedded) home();
  return {Niveau:level,Loesungshilfe:assisted,Fragen:logs,Interaktionen:counts,Auftraege:screens};
})
