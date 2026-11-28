// Textmodelle prüfen Aussagen nur im Kontext der gerade geöffneten Aufgabe.
const Diagnose=(()=>{
  const norm=text=>String(text||'').normalize('NFC').toLocaleLowerCase('de').trim()
    .replaceAll('ß','ss').replace(/\s+/gu,' ').replace(/[.! ]+$/u,'');
  const muster={
    'Mutter/Wert':/^(?:(?:ihr|mama|der mutter) ist (?:die )?(?:gesundheit (?:von|ihrer tochter) laura|lauras (?:körperliche )?gesundheit|gesundheit) wichtig|(?:lauras |ihre |die )?(?:körperliche )?gesun(?:d|t)heit(?: von laura)?|(?:sie will,? |sie möchte,? |mama will,? )?(?:dass )?laura gesund (?:bleibt|ist)|(?:sie|mama) (?:möchte|will) nicht,? dass laura krank wird|(?:dass )?es laura (?:körperlich )?gut geht|laura soll gesund bleiben)$/u,
    'Mutter/Norm':/^(?:man (?:soll|sollte|muss) (?:gut )?auf (?:seinen|den|seinen eigenen) körper (?:achten|aufpassen)|(?:man sollte )?(?:mögliche )?beschwerden ernst nehmen)$/u,
    'Mutter/Folgerung':/^(?:(?:laura|sie) soll (?:das kind|ihr baby) (?:bekommen|behalten)|(?:das kind|ihr baby|das baby) (?:bekommen|behalten)|(?:die )?schwangerschaft (?:fortsetzen|austragen))$/u,
    'Freundin/Wert':/^(?:lauras (?:eigene )?zukunftsplanung|(?:erst )?(?:die |ihre )?ausbildung (?:abschließen|beenden|fertig machen)(?: und (?:die |ihre )?zukunft (?:selbst )?planen)?|(?:dass )?laura (?:ihre |die )?zukunft selbst (?:plant|planen kann))$/u,
    'Freundin/Norm':/^(?:man sollte (?:erst )?kinder (?:bekommen|kriegen),? wenn man (?:selbst |dafür )?bereit (?:dafür )?ist|kinder (?:bekommen|kriegen),? wenn es (?:zu den eigenen plänen|ins leben) passt)$/u,
    'Freundin/Folgerung':/^(?:(?:die )?schwangerschaft (?:mit medikamenten |medikamentös )?abbrechen|(?:ein(?:en)? )?(?:medikamentöser?|medikamentösen) abbruch|laura soll (?:die schwangerschaft )?(?:mit medikamenten )?abbrechen)$/u,
    'Großmutter/Norm':/^(?:man (?:sollte|soll|muss) ungeborenes (?:menschliches )?leben schützen|ungeborenes leben (?:soll|sollte) geschützt werden)$/u,
    'Großmutter/Ergänzung':/^(?:das )?ungeborene (?:menschliche )?leben(?: ist ihr wichtig)?$/u,
    'Vater/Wert':/^(?:gut informiert selbst entscheiden|(?:dass )?laura (?:gut )?informiert selbst entscheiden kann|lauras (?:informierte )?selbstbestimmung)$/u,
    'Vater/Folgerung':/^(?:in der (?:praxis|arztpraxis) nach (?:den |ihren )?möglichkeiten fragen|sich in der arztpraxis beraten lassen)$/u,
    'Vater/Ergänzung':/^(?:man sollte sich vor (?:einer )?(?:wichtigen )?medizinischen entscheidung (?:gut|verlässlich) informieren|vor einer medizinischen entscheidung verlässliche informationen einholen)$/u,
    'Mutter/Ergänzung':/^(?:es (?:gibt|kommt zu) blutungen|blutungen (?:treten auf|kommen vor))(?:[.,;] ?| und )(?:schmerzen(?: und krämpfe)? (?:können auftreten|sind möglich)|es kann wehtun)$/u,
    'Freundin/Ergänzung':/^(?:ja,? )?(?:(?:danach|später) (?:kann (?:sie|laura|man) (?:wieder )?schwanger werden|ist eine schwangerschaft (?:weiterhin )?möglich)|eine spätere schwangerschaft (?:ist|bleibt) möglich|sie kann (?:später )?wieder schwanger werden)$/u
  };
  muster['Großmutter/Folgerung']=muster['Mutter/Folgerung'];
  const eizelle=/^(?:(?:weil |da )?keine eizelle (?:frei ?(?:kommt|wird)|freigesetzt wird)|es (?:wird|kommt) keine eizelle frei)$/u;
  const eisprung=/^(?:(?:die |eine )?(?:kombinations)?pille (?:hemmt|verhindert|unterdrückt) (?:meist |meistens )?(?:den )?eisprung|(?:weil |da )(?:die )?pille (?:den )?eisprung (?:hemmt|verhindert|unterdrückt))$/u;
  // Nur vollständige, in sich abgegrenzte Satzmuster. Ein unbekannter Nachsatz bleibt offen.
  const sinngleich={
    'Mutter/Wert':[
      /^(?:(?:der |ihrer )?mutter|mama) (?:liegt|liegt vor allem) (?:lauras gesundheit|die gesundheit ihrer tochter) am herzen$/u,
      /^(?:sie|mama|die mutter) (?:macht sich sorgen um|sorgt sich um) (?:lauras (?:körperliches wohl|gesundheit)|die gesundheit ihrer tochter)$/u,
      /^(?:ihre tochter|laura) (?:soll|muss) gesund bleiben$/u,
      /^gesund bleiben ist (?:der mama|ihr|der mutter) (?:wichtig|am wichtigsten)$/u
    ],
    'Mutter/Norm':[/^(?:beschwerden|schmerzen) (?:sollte|muss|soll) man ernst nehmen$/u,
      /^man (?:sollte|muss|soll) auf (?:den|seinen) körper achten$/u],
    'Mutter/Folgerung':[/^(?:ihr rat ist,? dass|die mutter will,? dass|sie rät,? dass) laura (?:das kind|das baby) (?:bekommt|behält)$/u],
    'Freundin/Wert':[/^laura (?:soll|will|möchte) (?:erst |zuerst )?(?:ihre |die )?ausbildung (?:abschließen|beenden)(?: und ihre zukunft selbst planen)?$/u],
    'Freundin/Norm':[/^man sollte (?:erst )?kinder bekommen,? wenn man (?:selbst )?bereit dazu ist$/u],
    'Freundin/Folgerung':[/^(?:sie|die freundin) rät (?:laura )?(?:zu einem|zum) abbruch mit medikamenten$/u],
    'Mutter/Ergänzung':[/^es blutet und (?:es kann im bauch (?:wehtun|weh tun)|der bauch kann (?:wehtun|weh tun))$/u],
    'Freundin/Ergänzung':[/^wenn es keine komplikationen gibt,? (?:ist (?:eine schwangerschaft|das) später (?:noch |wieder )?möglich|kann (?:sie|laura) später wieder schwanger werden)$/u]
  };
  function trifft(text,key,beispiel){
    if(text===norm(beispiel)||muster[key]?.test(text)||sinngleich[key]?.some(re=>re.test(text)))return true;
    if(!key.endsWith('/Leerstelle'))return false;
    const category=norm(beispiel);
    if(category==='fakt')return /^(?:(?:es fehlt |es fehlt noch )?(?:ein biologischer fakt|eine biologische (?:information|begründung))(?: (?:als grund )?für (?:den|ihren) rat)?|(?:der|ein) (?:biologische[r]? )?fakt fehlt)$/u.test(text);
    if(category==='norm')return /^(?:(?:die|eine) (?:allgemeine regel|norm) fehlt|es fehlt eine (?:regel|norm))$/u.test(text);
    if(category==='wert')return /^(?:der wert fehlt|es fehlt (?:ein|der) wert)$/u.test(text);
    return false;
  }
  function analyse(text,model,medizin=Entwurf.fehler){
    const raw=norm(text).replace(/^das (laura gesund bleibt)$/u,'dass $1');
    const {key='',frage,beispiel='',persoenlich=false,alternativen=[],fachlich=[]}=model;
    const imp='Vergleiche deinen Gedanken: '+(frage||'Welche Information passt zu deinem Grund?');
    function result(status,feedback,focus=imp,sample=beispiel){
      const next=status==='vollständig'?'Lies deinen Text noch einmal. Du kannst jetzt weitergehen.':
        status==='teil'?'Diesen Teil hast du schon erklärt. '+focus:status==='verwechslung'?'Prüfe, welche Art von Aussage die Frage sucht.':
        status==='unsicher'?'Dein Gedanke bleibt erhalten. Lege ihn neben das Beispiel.':frage||focus;
      return {status,feedback,focus,hints:[focus,feedback,next,
        sample?'Ein Beispiel: '+sample:focus,'Vergleiche deinen Text: '+(sample||focus)]};
    }
    if(!raw)return result('leer','Hier ist Platz für deinen Gedanken.',frage);
    const error=medizin(text);
    if(error){
      const contradict=/(?:^|[.!;] )die pille schützt (?:auch )?nicht vor hiv\b/u.test(raw)&&/(?:^|[.!;] )die pille schützt vor hiv\b/u.test(raw);
      return {...result(contradict?'widerspruch':'fehlvorstellung',error.info,error.frage,error.info),error};
    }
    if(!persoenlich){
      const value=fachlich.find(x=>norm(x)===raw);
      if(value||trifft(raw,key,beispiel))return result('vollständig',
        key==='Mutter/Wert'?'Genau! Mama ist Lauras Gesundheit wichtig.':'Deine Erklärung trifft diesen Fachgedanken.',frage);
      const person=key.split('/')[0];
      for(const cat of ['Norm','Folgerung','Wert']){
        if(!key.startsWith(person+'/')||key===person+'/'+cat||!muster[person+'/'+cat]?.test(raw))continue;
        const fb=cat==='Norm'?'Du hast eine Regel gefunden. Das ist eine Norm.':cat==='Folgerung'?'Das ist der Rat.':'Du hast einen Wert gefunden.';
        return result('verwechslung',person==='Mutter'&&cat==='Folgerung'?'Das ist Mamas Rat.':fb,
          key==='Mutter/Wert'&&cat==='Folgerung'?'Warum gibt Mama Laura diesen Rat?':frage);
      }
      if(alternativen.some(x=>norm(x.text)===raw && !x.ok))return result('verwechslung','Diese Aussage beantwortet eine andere Frage.',frage);
      if(key==='Mutter/Ergänzung' && /^(blutungen|es kommt zu blutungen|es blutet)$/u.test(raw))return result('teil','Die Blutungen hast du erkannt.','Was kann Laura außerdem im Bauch spüren?');
      if(key==='Freundin/Wert' && /^(?:die |ihre |lauras )?ausbildung$/u.test(raw))return result('teil','Du hast Lauras Ausbildung erkannt.','Wer soll über Lauras Zukunft entscheiden?');
    }
    if(model.pille){
      if(eizelle.test(raw))return result('teil','Richtig! Keine Eizelle wird frei.','Was verhindert die Pille?','Die Pille hemmt meist den Eisprung. Dann wird keine Eizelle frei.');
      if(eisprung.test(raw))return result('teil','Du hast die Hemmung des Eisprungs erklärt.','Was geschieht dann mit der Eizelle?');
      if(/^(?:eisprung|(?:die )?eizelle)$/u.test(raw))return result('ansatz','Du nennst einen Teil des Vorgangs.','Was passiert bei der Einnahme der Pille mit dem Eisprung?');
      if(/^(?:(?:die )?pille[, ]+)?eisprung (?:und |[,;] ?)(?:die )?eizelle$/u.test(raw))return result('zusammenhang','Eisprung und Eizelle gehören zusammen.','Wie hängt der Eisprung mit dem Freiwerden der Eizelle zusammen?');
    }
    return result('unsicher',persoenlich?'Das ist dein eigener Grund. Vergleiche ihn mit der Fachinformation.':'Dein Wortlaut bleibt stehen. Vergleiche deinen Gedanken mit dem Beispiel.',frage);
  }
  function modell(key,frage,beispiel,options={}){
    return {key,frage,beispiel,...options};
  }
  return {analyse,modell};
})();
