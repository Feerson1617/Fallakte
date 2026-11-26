// Öffentliche Bedienelemente betätigen. Prüft Textrechtecke und die Trefferfläche jedes sichtbaren Knopfs.
({tier,assist,models=true})=>{
 const $=s=>document.querySelector(s), all=s=>Array.from(document.querySelectorAll(s));
 const material=JSON.parse($('#material').textContent),cs=material.levels[tier].cards;
 const errors=[],words=new Set();
 let state='',count=0,taps=0,papers=0,segments=0,helpPos=null;
 const key=a=>document.querySelector('[data-action="'+a+'"]');
 const ok=(v,m)=>{if(!v)throw Error(tier+' / '+state+' / '+m);};
 const problem=m=>{errors.push({state,message:m});};
 function inspect(label){
   state=label;count++;
   const root=document.documentElement, vp=window.visualViewport;
   const W=Math.min(innerWidth,vp?.width||innerWidth), H=Math.min(innerHeight,vp?.height||innerHeight);
   if(scrollX||scrollY||root.scrollWidth>W+1||root.scrollHeight>H+1)problem('Seitenmaß '+[W,H,root.scrollWidth,root.scrollHeight,scrollY]);
   const box=r=>r.left>=-1 && r.top>=-1 && r.right<=W+1.1 && r.bottom<=H+1.1;
   const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
   for(let node;node=walker.nextNode();){
     if(!node.textContent.trim()||node.parentElement.closest('script,style,svg')||!node.parentElement.getClientRects().length)continue;
     const range=new Range();range.selectNodeContents(node);
     for(const r of range.getClientRects()){
       if(r.width && !box(r))problem('Text außerhalb: '+node.textContent.slice(0,48));
     }
     if(parseFloat(getComputedStyle(node.parentElement).fontSize)<15.95)problem('Schrift zu klein');
   }
   for(const b of all('button')){
     const r=b.getBoundingClientRect();if(!box(r)||r.height<43.9||r.width<43.9)problem('Taste: '+b.textContent);
     if(!b.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2)))problem('Taste verdeckt: '+b.textContent);
   }
   if($('#page').dataset.screen==='question'){
     const h=key('help');ok(h?.textContent==='Ich brauche Hilfe','Hilfezugang');
     const r=h.getBoundingClientRect();if(!helpPos)helpPos=[r.right,r.top];
     if(Math.abs(r.right-helpPos[0])>1 || Math.abs(r.top-helpPos[1])>1)problem('Hilfe verschoben');
   }
   for(const g of all('figure svg')){const r=g.getBoundingClientRect();if(!box(r)||r.height<44||r.width<44)problem('Abbildung außerhalb');}
   for(const s of all('#page h1,#page h2,#page p,#page figcaption,#page button,#page li,#page .feedback')){
     if(s.innerText.trim())words.add(s.innerText.trim());
   }
 }
 function tap(a,v){const b=$('[data-action="'+a+'"]'+(v===undefined?'':'[data-value="'+v+'"]'));ok(b&&!b.disabled,a+' '+v);b.click();taps++;}
 function showAnswers(){if(key('toanswers')){tap('toanswers');segments++;inspect(state+' · Auswahl');}}
 function help(label,start,end,q){
   const previous=$('#page').innerText;tap('help');
   for(let h=start;h<=end;h++){
     inspect(label+' · Hilfe '+h);
     ok($('#page h1').textContent==='Hilfe '+h+' von 5','gespeicherte Hilfestufe '+h);
     ok($('#page').innerText.includes(q.hilfen[h-1]),'Hilfe der aktuellen Frage');
     if(h<end)tap('more');
   }
   tap('back');ok($('#page').innerText===previous,'Arbeitsstand nach Hilfe');inspect(label+' · zurück');
 }
 inspect('Einstieg');tap('level',tier);inspect('Kapitelauswahl');
 ok($('#page').innerText.includes('STI bedeutet „sexuell übertragbare Infektionen“'),'STI beim ersten Auftreten erklärt');
 ok(!$('.chapter .done'),'unbearbeitete Sitzung');tap('open',0);
 const seen=[];
 for(let i=0;i<4;i++){
   const sources=[];seen.push(sources);
   const ts=[['index','huelle','kontakt'],['eisprung','einnahme'],['kupfer','kupferwahl'],['schleim','hormonwahl']][i];
   for(const topic of ts){
     const q=material.levels[tier].fragen[topic];inspect(topic);ok($('#page').innerText.includes(q.frage)||key('toanswers'),'Frage oder Leseansicht');
     const counter='Kapitel '+(i+1)+'/4';
     ok($('.context').innerText.includes(counter) && $('.context').innerText.includes('Frage '+(ts.indexOf(topic)+1)+'/'+ts.length),'Zähler der Aufgabe');
     ok($('.fact')?.innerText===q.info,'sichtbarer Lerntext vor Auswahl');sources.push({thema:topic,ansicht:'Lerntext',text:$('.fact').innerText});
     if(assist){help(topic,1,2,q);help(topic+' · erneut',2,3,q);}
     showAnswers();ok($('#page').innerText.includes(q.frage),'Frage in Auswahl');ok(all('[data-action=answer]').length===2,'beide Antworten');
     if(assist){
       tap('answer',1-q.richtig);inspect(topic+' · Fehler');ok($('#page').innerText.includes(q.fehler),'Fehlerhinweis');
       help(topic+' · nach Fehler',3,5,q);showAnswers();
     }
     tap('answer',q.richtig);inspect(topic+' · richtig');ok($('#page').innerText.includes(q.rueckmeldung),'Erklärung');
     sources.push({thema:topic,ansicht:'Rückmeldung',text:q.rueckmeldung});
     if(assist)help(topic+' · nach Lösung',5,5,q);
     tap('next');
   }
   inspect('Papier '+(i+1));ok($('#page h1').innerText==='Jetzt brauchst du deine Infokarte!','Papierüberschrift');
   ok(all('button').length===1&&key('finish').textContent==='Karte fertig – weiter','ein Rückweg');
   ok(JSON.stringify(all('li strong').map(n=>n.innerText))===JSON.stringify(cs[i].felder.map(f=>f.wort)),'vier Lösungen');
   if(i===2)ok($('#page').innerText.includes('Wende dein Kartenblatt'),'Blatt wenden');
   ok($('#page').innerText.includes(cs[i].seite+' '+cs[i].position) && $('#page h2').innerText===cs[i].ueberschrift,'Papierposition und Kapitel');
   ok($('.paperinstruction').innerText.includes('fett gedruckten Wörter in die gleich nummerierten Lücken. Richtige Wörter bleiben stehen.'),'Papierauftrag');
   ok(all('li .number').map(n=>n.innerText).join('')==='1234','Feldreihenfolge');
   papers++;tap('finish');
 }
 inspect('Abschluss');ok($('#page').textContent.includes('alle vier Kapitel'),'Sitzungsabschluss');
 const mandatoryTaps=taps, mandatoryWords=new Set(words);
 if(models){
   tap('menu');inspect('Vier Kapitel bearbeitet');ok(all('.chapter .done').length===4,'Sitzungsmarkierungen');tap('models');inspect('Musterkarten wählen');
   for(let i=0;i<4;i++){
     tap('model',i);
     for(const s of cs[i].texte){inspect('Muster '+(i+1)+' · '+s.titel);ok($('#page').innerText.includes(s.volltext),'Volltext');tap('section');}
     inspect('Muster '+(i+1)+' · Pearl-Index');tap('fill');inspect('Muster · Papier '+(i+1));tap('finish');ok($('#page').dataset.screen==='models' && all('[data-action=model]').length===4,'zurück zur Kartenauswahl');
   }
 }
 return {tier,assist,quellen:seen,count,taps:mandatoryTaps,papers,segments,lesewoerter:[...mandatoryWords].join(' ').match(/[\p{L}\p{N}]+(?:[-–][\p{L}\p{N}]+)*/gu)?.length,errors};
}
