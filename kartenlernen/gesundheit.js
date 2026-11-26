// Aussagen gelten nur mit ausdrücklich benannter Methode, passendem Prädikat und Objekt.
const Fachwissen = (() => {
  const pille='(?:die |eine )?(?:kombinationspille|pille)';
  const spirale='(?:die |eine )?(?:kupfer|hormon)?spirale[n]?';
  const kondom='(?:ein |das |die )?kondome?';
  const kupfer='(?:(?:die |eine )?kupferspirale[n]?)';
  const hormon='(?:(?:die |eine )?hormonspirale[n]?)';
  const erreger='(?:hiv(?: (?:oder|und|beziehungsweise) (?:anderen )?sti[s]?)?|sti[s]?|geschlechtskrankheiten|sexuell uebertragbaren (?:krankheiten|infektionen)|chlamydien|anderen sti[s]?)';
  const vor='(?:vor|gegen) (?:eine[r]? (?:ansteckung|infektion) mit )?(?:allen |saemtlichen |vielen )?'+erreger;
  const alle='vor (?:allen|saemtlichen|jeder art von) (?:sti[s]?|geschlechtskrankheiten|sexuell uebertragbaren infektionen)';
  const aktiv='(?:schuetzt|schuetzen)';
  const schutz='(?:auch |ausserdem |immer |zuverlaessig |sicher |vollstaendig )*';
  const mittel='(?:(?:eine |die )?hormonfreie methode|hormonfreie methoden|hormonfrei)';
  const regel='(?:die |eine )?regelmaessige einnahme (?:der |von der )?pille';
  const einnehmen='(?:regelmaessig|nach plan|taeglich) (?:einnehmen|nehmen|eingenommen werden|genommen werden)';
  const hormonwort='(?:hormone|ein hormon|gestagen)';
  function eintrag(karte,abschnitt,info,frage,falsch,richtig){
    const compile=list=>list.map(s=>new RegExp('^(?:'+s+')$'));
    return {karte,abschnitt,info,frage,falsch:compile(falsch),richtig:compile(richtig)};
  }
  const einzelne='(?:'+pille+'|'+spirale+')';
  const methoden=einzelne+'(?: (?:oder|und) '+einzelne+')?';
  const katalog={
    sti:eintrag(1,1,'Pille und Spiralen schützen nicht vor HIV. Auch andere Erreger können beim Sex übertragen werden.','Hält diese Methode Krankheitserreger zurück?',
      [methoden+' '+aktiv+' '+schutz+vor,vor+' '+aktiv+' '+methoden,methoden+' (?:bietet|bieten) (?:auch )?schutz '+vor,
       'mit (?:der |einer )?(?:(?:hormon|kupfer)?spirale|(?:kombinations)?pille) kann man kein hiv bekommen',
       methoden+' (?:verhindert|verhindern) (?:eine ansteckung mit )?(?:hiv|sti[s]?)'],
      [methoden+' '+aktiv+' (?:auch )?nicht '+vor,methoden+' '+aktiv+' '+vor+' nicht',methoden+' '+aktiv+' nicht gegen '+erreger,methoden+' (?:bietet|bieten) keinen (?:sti-schutz|schutz '+vor+')']),
    kondomschutz:eintrag(0,2,'Kondome senken das Risiko, sich beim Sex anzustecken. Manche Erreger gelangen über freie Haut zum anderen Menschen.','Welche Haut bleibt frei?',
      [kondom+' '+aktiv+' '+schutz+alle+'(?: immer| sicher| vollstaendig)?',kondom+' (?:bietet|bieten) (?:hundertprozentigen|absoluten|sicheren) schutz '+alle,
       kondom+' '+aktiv+' zu (?:hundert|100) prozent vor jeder infektion beim sex'],
      [kondom+' '+aktiv+' nicht (?:sicher |vollstaendig )?'+alle,kondom+' '+aktiv+' '+alle+' nicht sicher',kondom+' (?:senkt|senken) das (?:risiko vieler sti|sti-risiko)']),
    kupferhormone:eintrag(2,0,'Die Kupferspirale wirkt ohne Hormone.','Was gibt die Kupferspirale ab?',
      [kupfer+' (?:enthaelt|enthalten) '+hormonwort,kupfer+' (?:gibt|geben) '+hormonwort+' ab',kupfer+' (?:ist|sind) hormonhaltig'],
      [kupfer+' (?:enthaelt|enthalten) keine hormone',kupfer+' (?:ist|sind|wirkt|wirken) (?:hormonfrei|ohne hormone)',kupfer+' (?:gibt|geben) keine hormone ab']),
    hormonabgabe:eintrag(3,0,'Die Hormonspirale gibt ein Hormon ab. Es macht den Schleim am Gebärmutterhals zäher.','Welches Mittel verändert den Schleim?',
      [hormon+' (?:gibt|geben) (?:keine hormone|kein hormon|kein gestagen) ab',hormon+' (?:ist|sind|wirkt|wirken) (?:hormonfrei|ohne hormone)',hormon+' (?:enthaelt|enthalten) keine hormone'],
      [hormon+' (?:gibt|geben) (?:ein hormon|gestagen|hormone) ab',hormon+' (?:ist|sind) nicht hormonfrei']),
    spermien:eintrag(1,0,'Die Pille hemmt meist den Eisprung. Sie tötet keine Spermien.','Was geschieht bei der Pille mit dem Eisprung?',
      [pille+' (?:toetet|vernichtet) (?:die |alle )?(?:spermien|samenzellen)(?: ab)?',pille+' toetet (?:die )?(?:spermien|samenzellen) ab'],
      [pille+' toetet (?:die )?(?:spermien|samenzellen) nicht',pille+' toetet keine (?:spermien|samenzellen)']),
    einnahme:eintrag(1,2,'Nimm die Pille nach Plan. Vergisst du sie, kann der Schutz sinken.','Was steht im Einnahmeplan?',
      [regel+' ist (?:grundsaetzlich |generell )?(?:unnoetig|egal|unwichtig|nicht (?:noetig|notwendig|wichtig))',
       pille+' muss nicht jeden tag (?:genommen|eingenommen) werden',pille+' (?:muss|braucht) (?:man )?nicht '+einnehmen,'man muss '+pille+' nicht '+einnehmen],
      [regel+' ist (?:noetig|notwendig|wichtig|nicht unnoetig)',pille+' muss (?:man )?'+einnehmen,'man muss '+pille+' '+einnehmen]),
    beschwerden:eintrag(2,4,'Auch ohne Hormone sind Beschwerden möglich. Bei der Kupferspirale kann die Blutung stärker werden.','Wie kann sich die Blutung bei der Kupferspirale ändern?',
      [mittel+' (?:ist|sind|bedeutet) (?:immer |grundsaetzlich |garantiert )?(?:beschwerdefrei|nebenwirkungsfrei|frei von nebenwirkungen|keine beschwerden)',
       mittel+' (?:macht|machen|verursacht|verursachen) (?:nie (?:beschwerden|nebenwirkungen)|keine (?:beschwerden|nebenwirkungen))'],
      [mittel+' (?:bedeutet|heisst) nicht,? dass man keine beschwerden (?:hat|bekommt)',mittel+' (?:ist|sind|bedeutet) nicht (?:immer |automatisch |grundsaetzlich )?(?:beschwerdefrei|nebenwirkungsfrei)',mittel+' (?:kann|koennen) (?:auch )?beschwerden (?:machen|verursachen)'])
  };
  function lesen(text,modell){
    for(const [code,e] of Object.entries(katalog)){
      const falsch=e.falsch.some(re=>re.test(text));
      if(!falsch && !e.richtig.some(re=>re.test(text)))continue;
      const name=text.match(/(?:kombinationspille|pille|(?:hormon|kupfer)?spiralen?|kondome?)/)?.[0]||'methode';
      let karte=e.karte;
      if(code==='sti' && name.includes('spirale'))karte=name.includes('hormon')||name==='spirale'&&modell==='schleim'?3:2;
      const ziel=code==='sti'?text.match(/\b(hiv|sti[s]?|geschlechtskrankheiten|chlamydien|infektionen)\b/)?.[0]:null;
      return {code,name,ziel,karte,abschnitt:e.abschnitt,falsch};
    }
    return null;
  }
  // Nur die ausdrücklich zurückgenommene Aussage mit derselben Methode und demselben Thema auflösen.
  function berichtigungen(s,modell){
    // Einheitliches zusammengesetztes Subjekt; beide Methoden bieten keinen STI-Schutz.
    s=s.replace(/\b(?:die |eine )?(?:kombinationspille|pille) (?:oder|und) (?:die |eine )?(?:kupfer|hormon)?spirale schuetzen (?=(?:(?:nicht|auch|sicher) )?vor )/g,'die pille schuetzt ');
    s=s.replace(/([^.!?;]+?)[.!;]\s*(?:das stimmt nicht|das ist falsch|das war falsch)(?=[.!;]|$)/g,(original,satz)=>
      lesen(satz.trim(),modell)?.falsch?' korrigierter zusatz':original);
    return s.replace(/([^.!?;]+?)[.,;!]\s*(?:nein|korrektur|ich korrigiere mich)[,:]?\s*([^.!?;]+)/g,(original,vor,nach)=>{
      const a=lesen(vor.trim(),modell);
      if(!a?.falsch)return original;
      const explizit=nach.trim().replace(/^sie /,'die '+a.name+' ');
      const b=lesen(explizit,modell);
      return b && !b.falsch && b.code===a.code && b.name===a.name && b.ziel===a.ziel?' '+explizit:original;
    });
  }
  return {lesen,berichtigungen,katalog};
})();
if(typeof module!=='undefined' && module.exports)module.exports=Fachwissen;
