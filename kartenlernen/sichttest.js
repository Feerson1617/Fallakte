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
   if(['info','paper','question','feedback','help','reference','compare'].includes($('#page').dataset.screen)){
     const h=key('help');ok(h?.textContent.includes('Ich brauche Hilfe'),'Hilfezugang');
     const r=h.getBoundingClientRect();if(!helpPos)helpPos=[r.right,r.top];
     if(Math.abs(r.right-helpPos[0])>1 || Math.abs(r.top-helpPos[1])>1)problem('Hilfe verschoben');
   }
   if($('#page').dataset.screen==='feedback' && !key('advance'))ok($('.context:nth-of-type(2)')?.innerText.includes('Infokarte')||all('.context').some(n=>n.innerText.includes('Infokarte')&&n.innerText.includes(' · ')),'Kartenstelle in der Rückmeldung');
   for(const g of all('figure svg')){const r=g.getBoundingClientRect();if(!box(r)||r.height<44||r.width<44)problem('Abbildung außerhalb');}
   for(const s of all('#page h1,#page h2,#page p,#page figcaption,#page button,#page li,#page .feedback')){
     if(s.innerText.trim())words.add(s.innerText.trim());
   }
 }
 function tap(a,v){const b=$('[data-action="'+a+'"]'+(v===undefined?'':'[data-value="'+v+'"]'));ok(b&&!b.disabled,a+' '+v);b.click();taps++;}
 const chapter=material.levels[tier],quellen=[];
 function enter(text){
   const el=$('#entry');
   // Im kleinen Editor können weitere Textteile folgen. Beim Ersetzen alle Teile löschen.
   while(key('earlier'))tap('earlier');
   while(el.value){el.value='';el.dispatchEvent(new Event('input',{bubbles:true}));}
   el.value=text;el.dispatchEvent(new Event('input',{bubbles:true}));
 }
 function visitHelp(n,kind){
   const old=$('#page').innerText,value=$('#entry')?.value;
   tap('help');inspect(kind+' Hilfe 1');
   for(let h=2;h<=n;h++){tap('more');inspect(kind+' Hilfe '+h);}
   const saved=$('#page').innerText;tap('back');ok(old===$('#page').innerText,'Rückkehr aus Hilfe');tap('help');
   ok(saved===$('#page').innerText,'letzte Hilfestufe');tap('back');
   if(value!==undefined)ok($('#entry').value===value,'Entwurf erhalten');
 }
 inspect('Einstieg');tap('level',tier);inspect('Wiederaufnahme');tap('open',0);
 for(let i=0;i<4;i++){
   for(let part=0;part<2;part++){
     inspect('Info '+(i+1)+'/'+(part+1));
     ok(!key('pick')&&!$('#entry')&&!$('#page h1').innerText.endsWith('?'),'Informationstitel ohne Frage');
     const texts=all('.lesson p').map(el=>el.innerText);
     ok(texts.length===2,'zwei Lernbelege');
     texts.forEach((text,index)=>{
       const field=part*2+index;
       ok(text===chapter.info[i][part].text[index].replaceAll('*',''),'Lerntext tatsächlich sichtbar');
       quellen.push({niveau:tier,kapitel:i+1,feld:field+1,wort:cs[i].felder[field].wort,text});
     });
     if(assist)visitHelp(2,'Information');tap('readnext');
   }
   inspect('Papier '+(i+1));ok($('#page h1').innerText==='Schreibe auf deine Infokarte.','Schreibauftrag');
   const f=all('li strong').map(n=>n.innerText);
   ok(JSON.stringify(f)===JSON.stringify(cs[i].felder.map(f=>f.wort)),'Originalwörter');
   ok($('.sheet .active').innerText===(i+1)+' – '+cs[i].titel,'richtige Blatthälfte');
   ok($('#page').innerText.includes('Stehen alle vier Wörter bei 1, 2, 3 und 4'),'Selbstkontrolle');
   ok(all('.sheet span').map(n=>n.innerText).join('|')===cs.slice(i<2?0:2,i<2?2:4).map(c=>c.nummer+' – '+c.titel).join('|'),'Methodennamen auf beiden Blatthälften');
   if(assist)visitHelp(2,'Papier');papers++;tap('written');
 }
 inspect('Übergang');ok($('#page h1').innerText==='Sind alle vier Infokarten ausgefüllt?' && key('lookup'),'Selbstkontrolle mit Kartenrückweg');tap('startq');
 for(let i=0;i<4;i++){
   const q=chapter.fragen[i],m=material.modelle[q.modell];
   inspect('Frage '+(i+1));ok($('.locator').innerText.includes(cs[i].texte[q.abschnitt].titel),'Überschrift wie auf Papier');
   if(assist){
     tap('help');inspect('Kartenorientierung');ok($('#page').innerText.includes('Lies auf deiner Infokarte')&&$('#page').innerText.includes('unter der Überschrift'),'konkreter Suchauftrag');tap('reference');inspect('Ersatzkarte');
     for(let n=q.abschnitt;n>0;n--)tap('prev');
     for(const t of cs[i].texte){inspect('Ersatzkarte '+t.titel);ok($('#page').innerText.includes(t.volltext),'Originaltext');tap('following');}
     inspect('Ersatzkarte Pearl-Index');tap('helpback');tap('back');
     if(q.typ==='wahl'){
       const wrong=q.alternativen[0];
       for(let k=0;k<2;k++){
         tap('pick',q.optionen.indexOf(wrong.text));inspect('Fehlwahl');
         ok($('#page').innerText.includes(wrong.impuls),'spezifischer Denkimpuls');
         if(k===0)visitHelp(5,'Fehlwahl');
         tap('revise');
       }
     }else{
       tap('check');inspect('Leer');ok(!key('compare'),'leere Abgabe ohne Abschluss');tap('revise');
       const part=m.teile[0];
       const samples={schleim:['Der Schleim wird zäher.','Der Schleim wird zäher. Spermien kommen leichter durch.'],pille:['Kein Eisprung.','Kein Eisprung. Die Eizelle wird trotzdem frei.'],haut:['Freie Haut.','Freie Haut. Erreger werden nur mit Sperma übertragen.'],kupfer:['Kupfer bremst Spermien.','Kupfer bremst Spermien. Die Befruchtung wird leichter.']}[q.modell];
       enter(samples[0]);tap('check');inspect('Teilantwort');ok($('#page').innerText.includes(part),'richtige Teilaussage');
       tap('help');tap('more');inspect('Adaptiver Impuls');ok($('#page').innerText.includes(m.impulse[1]),'fehlende Folge');tap('back');tap('revise');
       enter(samples[1]);tap('help');inspect('Überarbeiteter Entwurf in Hilfe 2');
       ok(Object.values(m.fragen).some(text=>$('#page').innerText.includes(text)), 'Hilfe reagiert vor erneutem Prüfen');
       tap('back');tap('check');inspect('Widerspruch');ok($('#page').innerText.includes('Prüfe den anderen Teil'),'Widerspruch');
       tap('help');tap('more');inspect('Satzstarter');tap('more');inspect('Fachhilfe');tap('more');inspect('Beispiel');tap('back');tap('revise');
       enter(m.beispiel+' Das ist eine weitere Sache.');tap('check');inspect('Unklarer Zusatz');
       ok($('#page').innerText.includes('Beide Schritte sind da.'),'vorhandene Aussagen bestätigt');
       tap('help');tap('back');tap('revise');enter('Ich meine einen anderen Zusammenhang.');tap('check');inspect('Unsicher');
       ok(key('compare').classList.contains('primary')&&!key('revise').classList.contains('primary') && $('#page').innerText.includes('Deine Antwort kann richtig sein. Vergleiche sie mit diesem Beispiel.'),'passende primäre Handlung');tap('compare');inspect('Selbstvergleich');
       ok($('#page').innerText.includes(m.beispiel),'Beispiel zum Vergleich');
       if(i>=2){tap('compared');continue;}tap('revise');
     }
   }
   if(q.typ==='wahl')tap('pick',q.optionen.indexOf(q.passend));else{enter(m.beispiel);tap('check');}
   inspect('Passend');ok(key('advance'),'Weg zum Abschluss');tap('advance');
 }
 inspect('Abschluss');ok($('#page h1').innerText==='Du bist fertig.','Abschluss');
 const regularTaps=taps,read=[...words].join(' ').match(/[\p{L}\p{N}]+/gu).length;
 if(models){
   tap('menu');inspect('Sitzungsmarken');ok(all('.chapter').every(b=>b.innerText.endsWith('✓')),'vier Sitzungsmarken');
   tap('lookup');inspect('Zeitnotweg');for(let i=0;i<4;i++){tap('fill',i);inspect('Zeitnot Papier');ok(key('written').innerText==='Zurück zur Kartenauswahl','Beschriftung');tap('written');ok(key('fill'),'Kartenauswahl');}
 }
 return {tier,assist,count,taps:regularTaps,papers,lesewoerter:read,errors,quellen};
}
