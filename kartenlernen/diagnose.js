// Eine Aussage muss als ganze Teilaussage passen. Unbekannte Zusätze dürfen
// eine richtige Teilbeobachtung erhalten, aber keine sichere Freigabe erzeugen.
const Lernfeedback = (() => {
  const sperm='(?:spermien|samenzellen)', egg='(?:ei|eizelle)', mucus='(?:schleim|zervixschleim)';
  const slow='(?:schwerer|schlechter|langsamer|kaum|nicht so leicht)', dense='(?:zaeher|dicker|dichter|zaehfluessiger|zaeh)';
  const pass='(?:hindurch|durch|durch den schleim|zur eizelle|voran|weiter|zum ei)';
  const move='(?:kommen|gelangen|schwimmen)', germs='(?:(?:manche|einige) )?(?:krankheitserreger|erreger|keime|viren)';
  const skin='(?:hautstellen|ein teil der haut|manche hautstellen|teile der haut)';
  const bound = {
    pille:{
      a:['(?:die )?(?:pille|hormone|hormone der pille) (?:hemmt|hemmen|verhindert|verhindern|unterdrueckt) (?:meist )?(?:den )?eisprung',
        '(?:der )?eisprung (?:bleibt aus|wird (?:meist )?(?:gehemmt|verhindert|unterdrueckt)|findet nicht statt|entfaellt)','(?:kein|ohne|gehemmter) eisprung'],
      b:['(?:es )?(?:wird|ist) keine (?:befruchtbare )?eizelle (?:frei|da|vorhanden)','keine (?:freie |befruchtbare )?eizelle(?: (?:wird frei|frei|zur befruchtung|kann befruchtet werden))?',
        '(?:die )?eizelle (?:wird nicht frei|fehlt|kann nicht befruchtet werden)','(?:es )?fehlt (?:eine|die) (?:freie |befruchtbare )?eizelle',
        'steht keine (?:befruchtbare )?eizelle zur verfuegung','(?:es )?gibt (?:es )?keine (?:freie |befruchtbare )?eizelle','wird kein ei frei','wird keine eizelle zur befruchtung frei','ist keine befruchtbare eizelle da'],
      negatives:{zyklus:['(?:die pille )?(?:foerdert|verstaerkt) den eisprung','(?:der )?eisprung (?:findet statt|wird nicht gehemmt|bleibt nicht aus)'],eizelle:['(?:die |eine )?eizelle wird (?:trotzdem )?frei','(?:es )?wird eine eizelle frei'],spermien:['die pille (?:bremst|toetet|stoppt) (?:die )?spermien']}
    },
    schleim:{
      a:['(?:der )?'+mucus+'(?: am gebaermutterhals)? (?:wird|ist) '+dense,'(?:das hormon|die spirale|gestagen) macht (?:den )?schleim '+dense,'(?:zaeher|dicker|dichter|zaehfluessiger) '+mucus,'(?:wird|ist) der schleim '+dense],
      b:['(?:die )?'+sperm+' '+move+' '+slow+' '+pass,move+' (?:die )?'+sperm+' '+slow+' '+pass,'(?:die )?'+sperm+' koennen '+slow+' (?:hindurch|durchkommen|hindurchgelangen|durch den schleim gelangen|zur eizelle gelangen)',
        '(?:sie|die samenzellen|die spermien) kommen nicht so gut durch','(?:die )?'+sperm+' werden (?:gebremst|aufgehalten)','(?:sie|spermien) kommen kaum hindurch','der weg (?:der|fuer die) spermien wird erschwert'],
      negatives:{dichte:['(?:der )?schleim (?:wird|ist) (?:nicht '+dense+'|duenner|fluessiger|durchlaessiger)'],weg:['(?:die )?'+sperm+' '+move+' (?:deshalb )?(?:leichter|schneller|besser) '+pass,move+' (?:die )?'+sperm+' (?:leichter|schneller|besser) '+pass],zyklus:['(?:die )?(?:hormonspirale|spirale) (?:hemmt|verhindert|stoppt) (?:immer |vor allem )?(?:den )?eisprung']}
    },
    haut:{
      a:[skin+' (?:bleibt|bleiben|ist|sind) (?:frei|unbedeckt|nicht bedeckt)','(?:das )?kondom (?:bedeckt|schuetzt) (?:nicht die ganze haut|nur einen teil der haut|nicht alle hautstellen)','(?:unbedeckte|freie) haut(?:stellen)?','nicht (?:die )?ganze haut (?:ist )?bedeckt','(?:es )?bleiben hautstellen frei'],
      b:[germs+' (?:koennen )?(?:bei|durch|ueber) (?:direkten )?(?:hautkontakt|freie haut|unbedeckte haut) (?:uebertragen werden|uebergehen|weitergegeben werden)','(?:bei|durch) hautkontakt (?:koennen |werden )?'+germs+' (?:uebertragen werden|uebertragen|weitergegeben werden|uebergehen)','(?:bei )?hautkontakt (?:kann )?'+germs+' uebertragen','(?:koennen )?'+germs+' bei hautkontakt uebertragen werden','uebertragung (?:von erregern )?durch hautkontakt'],
      negatives:{flaeche:['(?:das )?kondom (?:bedeckt|schuetzt) (?:die ganze haut|alle hautstellen)','(?:die )?ganze haut ist bedeckt'],kontakt:['(?:bei|durch) hautkontakt werden keine erreger uebertragen','erreger koennen durch hautkontakt nicht uebertragen werden'],sperma:['erreger werden nur (?:durch|mit) sperma uebertragen']}
    },
    kupfer:{
      a:['kupfer bremst (?:die )?'+sperm,'kupfer (?:stoert|hemmt|bremst) (?:die )?(?:bewegung|beweglichkeit) (?:der |von )?'+sperm,'(?:die )?'+sperm+' (?:bewegen sich|schwimmen) '+slow,'(?:die )?'+sperm+' sind weniger beweglich','(?:langsame|gebremste) spermien','(?:die )?beweglichkeit der spermien (?:nimmt ab|sinkt)'],
      b:['(?:sie|(?:die )?'+sperm+') (?:erreichen|befruchten) (?:die |eine |das )?'+egg+' '+slow,'(?:sie|(?:die )?'+sperm+') koennen (?:die |eine |das )?'+egg+' '+slow+' befruchten','(?:eine |die )?befruchtung (?:ist|wird) (?:erschwert|schwieriger|schwerer)','(?:die )?befruchtungsfaehigkeit (?:nimmt ab|sinkt)','(?:erreichen|befruchten) (?:sie|die spermien) (?:die eizelle|das ei) '+slow,'(?:sie|spermien) erreichen und befruchten die eizelle schwerer','erschwerte befruchtung','erreichen und befruchten sie die eizelle schwerer'],
      negatives:{bewegung:['(?:die )?spermien (?:schwimmen|bewegen sich) (?:schneller|besser)','kupfer macht spermien beweglicher'],befruchtung:['(?:die )?befruchtung wird (?:leichter|erleichtert)','sie befruchten die eizelle leichter'],zyklus:['kupfer (?:verhindert|hemmt|stoppt) (?:den )?eisprung','(?:der )?eisprung bleibt aus'],schleim:['kupfer macht den schleim zaeher','der schleim wird dicker']}
    }
  };
  function matches(list, clause){return list.some(re=>re.test(clause));}
  const compile=list=>list.map(s=>new RegExp('^(?:'+s+')$'));
  for(const m of Object.values(bound)){
    m.a=compile(m.a);m.b=compile(m.b);
    for(const key of Object.keys(m.negatives))m.negatives[key]=compile(m.negatives[key]);
  }
  function clean(s){
    return s.replace(/\n/g,';').toLowerCase().replaceAll('ä','ae').replaceAll('ö','oe').replaceAll('ü','ue').replaceAll('ß','ss')
      .replace(/\b(spermjen|spermein|spermin|spermiem)\b/g,'spermien').replace(/\bschleim[m]?\b/g,'schleim')
      .replace(/\b(eisprug|eissprung)\b/g,'eisprung').replace(/\b(?:eizzele|eizele)\b/g,'eizelle')
      .replace(/\bzaher\b/g,'zaeher').replace(/\bhautkontak\b/g,'hautkontakt').replace(/\bkupffer\b/g,'kupfer')
      .replace(/\s+/g,' ').trim();
  }
  function analyze(id,text){
    const s=clean(text), model=bound[id], parts=new Set(),errors=new Set();
    function result(state){return {state,parts:[...parts],error:[...errors][0]||null};}
    if(!/[a-z0-9]/.test(s))return result('leer');
    if(/\?|\b(?:vielleicht|angeblich|weiss nicht|oder|nicht sicher|wenn|falls)\b/.test(s))return result('unsicher');
    // Split relation words separately so reversal of a causal arrow cannot earn approval.
    const ordered=s.replace(/,\s*(aber|und) /g,' $1 ').replace(/((?:die )?(?:samenzellen|spermien)) (kommen|gelangen|schwimmen) (deshalb|dadurch|daher) /g,'$3 $2 $1 ');
    const chunks=ordered.replace(/[.,;:]?\s*\b(weil|denn|dadurch|deshalb|daher|darum|sodass|also|deswegen)\b\s*/g,'|$1|')
      .split(/(\|[a-z]+\||\s+aber\s+|\s+und\s+(?!(?:befruchten sie|befruchten die eizelle))|\s*(?:->|→)\s*|[.,;:\n]+)/);
    let unknown=false,reversed=false,link='',last='';
    for(let i=0;i<chunks.length;i++){
      if(i%2){if(chunks[i].trim())link=chunks[i].trim();continue;}
      let c=chunks[i].trim().replace(/ (?:und|aber)$/,'');if(!c || c==='aber' || c==='und')continue;
      // Normalize common verb-final clauses after "weil" and cause-first inversion.
      c=c.replace(/^(der schleim) (zaeher|dicker|dichter) wird$/,'$1 wird $2')
        .replace(/^(die pille) den eisprung (hemmt|verhindert)$/,'$1 $2 den eisprung')
        .replace(/^kupfer (?:die )?spermien bremst$/,'kupfer bremst spermien')
        .replace(/^(ein teil der haut) (frei|unbedeckt) bleibt$/,'$1 bleibt $2')
        .replace(/^dort (koennen|werden) /,'$1 ').replace(/^bei hautkontakt koennen sie /,'bei hautkontakt koennen erreger ');
      let tag=matches(model.a,c)?'a':matches(model.b,c)?'b':'';
      if(tag){
        if(last && last!==tag && ((/weil|denn/.test(link) && tag==='b') || (/dadurch|deshalb|daher|darum|sodass|also|deswegen|→|->/.test(link) && tag==='a')))reversed=true;
        parts.add(tag);last=tag;
      }else{
        const err=Object.keys(model.negatives).find(k=>matches(model.negatives[k],c));
        if(err)errors.add(err);else unknown=true;
      }
      link='';
    }
    if(unknown && errors.size)return result('unsicher');
    if(errors.size)return result(parts.size?'widerspruch':'fehlvorstellung');
    if(reversed||unknown)return result('unsicher');
    if(parts.size===2)return result('passend');
    return result(parts.size?'teilweise':'unsicher');
  }
  return {analyze};
})();
if(typeof module!=='undefined' && module.exports)module.exports=Lernfeedback;
