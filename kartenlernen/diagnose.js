// Eine Aussage muss als ganze Teilaussage passen. Unbekannte Zusätze dürfen
// eine richtige Teilbeobachtung erhalten, aber keine sichere Freigabe erzeugen.
const Lernfeedback = (() => {
  const gesund=typeof Fachwissen==='undefined'?require('./gesundheit.js'):Fachwissen;
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
        '(?:die )?eizelle (?:wird nicht frei|fehlt)','(?:es )?fehlt (?:eine|die) (?:freie |befruchtbare )?eizelle',
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
      negatives:{flaeche:['(?:das )?kondom (?:bedeckt|schuetzt) (?:die ganze haut|alle hautstellen)','(?:die )?ganze haut ist bedeckt','haut bleibt nicht frei'],kontakt:['(?:bei|durch) hautkontakt werden keine erreger uebertragen','erreger koennen durch hautkontakt nicht uebertragen werden'],sperma:['erreger werden nur (?:durch|mit) sperma uebertragen']}
    },
    kupfer:{
      a:['kupfer bremst (?:die )?'+sperm,'kupfer (?:stoert|hemmt|bremst) (?:die )?(?:bewegung|beweglichkeit) (?:der |von )?'+sperm,'(?:die )?'+sperm+' (?:bewegen sich|schwimmen) '+slow,'(?:die )?'+sperm+' sind weniger beweglich','(?:langsame|gebremste) spermien','(?:die )?beweglichkeit der spermien (?:nimmt ab|sinkt)'],
      b:['(?:sie|(?:die )?'+sperm+') (?:erreichen|befruchten) (?:die |eine |das )?'+egg+' '+slow,'(?:sie|(?:die )?'+sperm+') koennen (?:die |eine |das )?'+egg+' '+slow+' befruchten','(?:eine |die )?befruchtung (?:ist|wird) (?:erschwert|schwieriger|schwerer)','(?:die )?befruchtungsfaehigkeit (?:nimmt ab|sinkt)','(?:erreichen|befruchten) (?:sie|die spermien) (?:die eizelle|das ei) '+slow,'(?:sie|spermien) erreichen und befruchten die eizelle schwerer','erschwerte befruchtung','erreichen und befruchten sie die eizelle schwerer'],
      negatives:{bewegung:['(?:die )?spermien (?:schwimmen|bewegen sich) (?:schneller|besser)','kupfer macht spermien beweglicher'],befruchtung:['(?:die )?befruchtung wird (?:leichter|erleichtert)','sie befruchten die eizelle leichter'],zyklus:['kupfer (?:verhindert|hemmt|stoppt) (?:den )?eisprung','(?:der )?eisprung bleibt aus'],schleim:['kupfer macht den schleim zaeher','der schleim wird dicker']}
    }
  };
  // Jede Ergänzung bindet ein Subjekt an ein Prädikat und ein bestimmtes Objekt.
  // Derselbe Rahmen gilt für Hauptsatz, Inversion und Verbendstellung.
  const word = alternatives => '(?:'+alternatives+')';
  function frame(s,v,o){
    const S=word(s),V=word(v),O=word(o);
    return [S+' '+V+' '+O,S+' '+O+' '+V,V+' '+S+' '+O];
  }
  const pill='(?:die )?(?:kombinationspille|pille|hormone(?: der pille)?)';
  const ov='(?:den |der )?eisprung', ovVerb='hemmt|hemmen|verhindert|verhindern|unterdrueckt|unterdruecken|stoppt|blockiert';
  const negOv='(?:den )?eisprung nicht';
  const cell='(?:eine |die )?eizelle|(?:ein |das )?ei';
  const noCell='kein(?:e)? (?:freie |befruchtbare )?(?:eizelle|ei)';
  const sauce='(?:der |den )?(?:zervixschleim|schleim|schleimpfropf)(?: am (?:gebaermutterhals|muttermund))?';
  const thick='dickfluessiger|zaehfluessiger|dicker|zaeher|dichter|zaeh|dickfluessig';
  const fluid='duenner|fluessiger|durchlaessiger';
  const hormonal='(?:die |das )?(?:hormonspirale|spirale|hormone?|gestagen)(?: der spirale)?';
  const swimmers='(?:die )?(?:samenzellen|spermien|samenfaeden)';
  const refer=swimmers+'|sie|diese';
  const hard='schwerer|schlechter|langsamer|seltener|kaum(?: noch)?|weniger gut|nicht (?:mehr )?so (?:gut|leicht)|nur schwer';
  const path='hindurch|durch(?: den (?:zaehen )?schleim)?|voran|weiter|zur eizelle|zum ei';
  const copper='(?:das |die )?(?:kupfer(?:ionen)?|kupferspirale)';
  const motion='(?:die )?(?:beweglichkeit|bewegung|bewegungsfaehigkeit) (?:der |von )?'+swimmers;
  const condom='(?:das |ein |die )?kondom(?:e)?';
  const outside='(?:einige |manche |andere )?(?:hautstellen|stellen)|(?:ein )?teil der haut|haut';
  const bare='frei|unbedeckt|ungeschuetzt|nicht bedeckt';
  const partialCover='nicht (?:die )?(?:ganze|gesamte) haut|nicht alle (?:hautstellen|stellen)|nur (?:die bedeckte stelle|einen teil der haut|einen teil)';
  const route='(?:bei|durch|ueber) (?:direkten )?(?:hautkontakt|kontakt|(?:die )?(?:uebrige|freie|unbedeckte) haut)';
  const transfer='uebertragen|weitergegeben|uebertragen werden|weitergegeben werden|uebergehen|weiterwandern';
  const reduced=word(hard);
  const gram={
    pille:{
      a:[...frame(pill,ovVerb,'(?:meist(?:ens)? |normalerweise )?'+ov),
        ...frame(pill,ovVerb,'(?:den )?eisprung nicht immer'),
        ...frame('(?:der )?eisprung','wird','(?:meist |normalerweise )?(?:gehemmt|verhindert|unterdrueckt)'),
        '(?:der )?eisprung (?:ausbleibt|ausfaellt|nicht stattfindet)','es (?:gibt keinen eisprung|kommt (?:meist )?nicht zum eisprung)'],
      b:[...frame(noCell,'wird|ist','(?:zur befruchtung )?(?:frei|freigesetzt|vorhanden|da)'),
        ...frame(noCell,'kann','befruchtet werden'),...frame(cell,'wird','nicht (?:frei|freigesetzt)'),
        '(?:eine |die )?(?:freie |befruchtbare )?eizelle fehlt',word(cell)+' fehlt','kein(?:e)? (?:eizelle|ei) (?:zum befruchten|zum befruchten da|zur befruchtung frei)',
        '(?:es )?(?:ist|wird) '+noCell+' (?:frei|freigesetzt|zur befruchtung frei|zum befruchten frei)',
        '(?:es )?gibt (?:es )?'+noCell+'(?: zum befruchten| zur befruchtung)?','fehlt eine befruchtbare eizelle',
        'keine eizelle zur befruchtung (?:frei )?wird'],
      ab:['ohne eisprung (?:gibt es|wird|ist) '+noCell+'(?: frei| freigesetzt| da| zur befruchtung)?(?:,? (?:die|das) befruchtet werden (?:kann|koennte))?',
        'ohne eisprung kann '+noCell+' befruchtet werden'],
      extra:['(?:die )?pille enthaelt hormone','die pille schuetzt nicht vor sti'],
      negatives:{zyklus:[...frame(pill,ovVerb,negOv),...frame(pill,'hemmt nicht|verhindert nicht|unterdrueckt nicht',ov),'(?:der )?eisprung wird nicht (?:unterdrueckt|verhindert)'],spermien:[...frame(pill,ovVerb,'(?:vor allem )?'+motion)]}
    },
    schleim:{
      a:[...frame(sauce,'wird|ist',thick),...frame(hormonal,'verdickt|verdicken',sauce),'(?:durch (?:die hormonspirale|das gestagen|die hormone) )?(?:verdickt sich (?:der )?schleim|wird der schleim '+word(thick)+')',
        ...frame(hormonal,'macht|machen',sauce+' '+word(thick)),sauce+' (?:verdickt sich|wird verdickt|'+word(thick)+')',
        'der pfropf am hals der gebaermutter ist '+word(thick),'der schleim verdickt sich'],
      b:[...frame(refer,'kommen|gelangen|schwimmen',reduced+' '+word(path)),
        ...frame(refer,'kommen|gelangen',word(path)+' '+reduced),
        ...frame(refer,'koennen',reduced+' (?:passieren|durchkommen|hindurchkommen|hindurchgelangen|durchschwimmen|durch den schleim gelangen)'),
        ...frame(refer,'schaffen','(?:die passage|den weg) '+reduced),
        word(refer)+' '+reduced+' (?:durchkommen|hindurchkommen|passieren)(?: koennen)?',
        '(?:der |den )?spermien (?:faellt|wird) der weg zur eizelle schwerer'],
      ab:['(?:der |durch den |durch |im )?(?:verdickte[nr]?|zaehere[nr]?|dickere[nr]?|zaehe[nr]?|dichte[nr]?) schleim(?: am gebaermutterhals)? (?:erschwert (?:den )?(?:spermien|samenzellen) (?:den weg|den durchtritt|das durchkommen)(?: zur eizelle)?|bremst (?:die )?(?:spermien|samenzellen)|kommen (?:die )?(?:spermien|samenzellen) '+reduced+' (?:durch|hindurch))'],
      extra:['die hormonspirale gibt (?:ein hormon|gestagen) ab','(?:der )?eisprung kann (?:weiter )?stattfinden'],
      negatives:{dichte:[...frame(sauce,'wird|ist','nicht '+word(thick)+'|'+fluid),sauce+' verdickt sich nicht'],
        weg:[...frame(refer,'kommen|gelangen|schwimmen',word('leichter|schneller|besser')+' '+word(path)),...frame(refer,'koennen','(?:leichter|schneller|besser) passieren')],
        zyklus:[...frame(hormonal,ovVerb,'(?:immer |vor allem )?'+ov)]}
    },
    haut:{
      a:[...frame(condom,'schuetzt|schuetzen|bedeckt|bedecken',partialCover),...frame(condom,'deckt|decken',word(partialCover)+' ab'),
        ...frame(outside,'bleibt|bleiben|ist|sind',bare),'neben dem kondom (?:gibt es|bleiben) (?:immer noch |noch )?freie hautflaechen','(?:das )?kondom laesst (?:einen teil der haut|hautstellen) frei','nicht alle (?:hautstellen|stellen) (?:vom kondom )?(?:bedeckt sind|sind bedeckt)',
        '(?:die )?(?:ganze|gesamte) haut (?:ist nicht|wird nicht) (?:abgedeckt|bedeckt)','(?:das )?kondom (?:liegt|sitzt) nur (?:auf|an) einer stelle'],
      b:[...frame(germs,'koennen|werden',route+' '+word(transfer)),route+' (?:koennen|werden) '+germs+' '+word(transfer),
        route+' (?:kann man sich|koennen wir uns) (?:anstecken|infizieren)','(?:man kann sich|kann man sich) '+route+' (?:anstecken|infizieren)',
        '(?:bei hautkontakt|dort|an diesen stellen) ist (?:eine )?ansteckung(?: durch hautkontakt)? moeglich',
        '(?:ist )?(?:dort|hier) (?:eine )?ansteckung moeglich','(?:dort|hier) koennen erreger uebertragen werden',
        'hautkontakt kann '+germs+' (?:uebertragen|weitergeben)'],
      ab:['an (?:den )?(?:unbedeckten|freien|ungeschuetzten) hautstellen koennen '+germs+' (?:durch kontakt |bei hautkontakt )?(?:uebertragen|weitergegeben) werden'],
      extra:['(?:das )?kondom (?:ist heil|ist intakt|haelt sperma zurueck)'],
      negatives:{flaeche:[...frame(condom,'deckt|decken','(?:die )?(?:gesamte|ganze) haut ab'),...frame(condom,'bedeckt|schuetzt','die gesamte haut')],
        kontakt:['(?:eine )?ansteckung '+route+' ist nicht moeglich','hautkontakt kann keine erreger uebertragen'],
        sperma:['erreger brauchen (?:immer |nur )?sperma zur uebertragung']}
    },
    kupfer:{
      a:[...frame(copper,'hemmt|hemmen|beeintraechtigt|beeintraechtigen|stoert|stoeren|bremst|bremsen',motion),
        ...frame(copper,'bremst|bremsen|beeintraechtigt|beeintraechtigen',swimmers),
        ...frame(swimmers,'koennen','sich '+reduced+' bewegen'),...frame(swimmers,'sind','(?:nicht mehr so|weniger|kaum noch) beweglich'),...frame(swimmers,'bewegen','sich '+reduced),
        'sich '+swimmers+' '+reduced+' bewegen (?:koennen|muessen)',...frame(swimmers,'schwimmen',hard),...frame(swimmers,'kommen|schwimmen',reduced+' voran'),
        'die beweglichkeit der spermien (?:wird eingeschraenkt|wird gehemmt|ist vermindert)'],
      b:[...frame(refer,'erreichen|befruchten',word(cell)+' '+reduced),...frame(refer,'erreichen|befruchten',reduced+' '+word(cell)),
        ...frame(refer,'koennen',word(cell)+' '+reduced+' (?:erreichen|befruchten)'),...frame(refer,'schaffen','es seltener bis zur eizelle'),
        '(?:eine |die )?befruchtung (?:ist|wird) (?:weniger wahrscheinlich|unwahrscheinlicher)', '(?:sie|diese|die spermien|die samenzellen) kommen '+reduced+' (?:an die eizelle|bis zur eizelle|ans ei)','(?:ist|wird) (?:eine |die )?befruchtung (?:erschwert|schwieriger|weniger wahrscheinlich|unwahrscheinlicher)',
        '(?:sie|diese) schaffen es seltener(?:,)? (?:die eizelle|das ei) zu befruchten'],
      ab:['(?:langsamere|gebremste|weniger bewegliche) '+swimmers+' (?:erreichen|befruchten) '+word(cell)+' '+reduced],
      extra:['(?:der |ein )?eisprung (?:kann (?:trotzdem |weiter )?stattfinden|ist weiterhin moeglich)','kupfer (?:hemmt|verhindert) (?:den eisprung nicht|nicht den eisprung)'],
      negatives:{bewegung:[...frame(copper,'macht|machen',swimmers+' (?:beweglicher|schneller)'),...frame(copper,'beeintraechtigt|hemmt',motion+' nicht')],
        zyklus:[...frame(copper,ovVerb,ov)],befruchtung:[...frame(refer,'erreichen|befruchten',word(cell)+' (?:besser|leichter)')]}
    }
  };
  // Häufige fachliche Alternativen mit ausdrücklicher Orts- oder Wirkungsangabe.
  gram.pille.a.push('(?:mit|durch) (?:die )?pille (?:bleibt der eisprung aus|wird der eisprung (?:meist )?gehemmt)',
    '(?:die )?pille sorgt dafuer dass der eisprung ausbleibt','(?:es )?kommt nicht zu einem eisprung');
  gram.pille.b.push('(?:zur befruchtung )?steht keine (?:freie |befruchtbare )?eizelle (?:mehr )?zur verfuegung',
    'keine (?:freie |befruchtbare )?eizelle steht zur verfuegung','(?:es )?ist kein ei (?:zum befruchten|mehr frei)',
    'spermien (?:finden|haben) keine (?:freie |befruchtbare )?eizelle(?: zum befruchten)?');
  gram.pille.ab.push('ohne eisprung (?:steht keine eizelle zur verfuegung|fehlt (?:die |eine )?(?:freie |befruchtbare )?eizelle)(?: zur befruchtung)?',
    'bleibt der eisprung aus wird keine eizelle frei');
  gram.schleim.a.push('(?:der )?schleim (?:am gebaermutterhals )?(?:verdickt sich|wird dickfluessig)',
    '(?:durch (?:das hormon|die hormonspirale) )?wird (?:der )?schleim am gebaermutterhals '+word(thick));
  gram.schleim.b.push(...frame(refer,'kommen|gelangen','(?:da |dort |nun )?'+reduced+' (?:durch|hindurch)'),
    ...frame(refer,'koennen','(?:den schleim |ihn )?'+reduced+' (?:durchdringen|passieren|durchqueren)'),
    '(?:der weg|die passage) (?:fuer|von) (?:die )?spermien (?:ist|wird) (?:erschwert|schwieriger)');
  gram.schleim.ab.push('(?:der |ein )?(?:zaehe[rn]?|dicke[rn]?|verdickte[rn]?) schleim (?:laesst|lassen) (?:die )?spermien '+reduced+' (?:durch|hindurch)',
    'spermien (?:kommen|gelangen) durch (?:den )?(?:zaehen|dicken|verdickten) schleim '+reduced+' (?:hindurch|zur eizelle)');
  gram.haut.a.push('(?:ein |das )?kondom (?:deckt|bedeckt) nur (?:eine stelle|einen bereich|einen teil)(?: ab)?',
    '(?:manche |einige )?stellen bleiben (?:frei|ungeschuetzt)','ausserhalb (?:des kondoms|der huelle) bleibt haut frei',
    'nicht alle (?:hautstellen|stellen) (?:werden|sind) (?:vom kondom )?(?:abgedeckt|bedeckt)');
  gram.haut.b.push('(?:ueber|durch|bei) (?:die )?(?:haut|hautkontakt|freien stellen) (?:ist|bleibt) (?:eine )?ansteckung moeglich',
    '(?:dort|hier|bei hautkontakt) kann man sich (?:noch |trotzdem )?(?:anstecken|infizieren)',
    '(?:auch )?hautkontakt (?:genuegt|reicht) (?:fuer eine ansteckung|zur uebertragung)',
    germs+' (?:werden|koennen) (?:auch )?'+route+' '+word(transfer));
  gram.haut.ab.push('an (?:freien|unbedeckten|ungeschuetzten) hautstellen (?:kann man sich (?:durch hautkontakt )?anstecken|ist eine ansteckung moeglich)');
  gram.kupfer.a.push(...frame(copper,'stoert|stoeren|behindert|behindern','die bewegung (?:von |der )?'+swimmers),
    ...frame(swimmers,'sind','(?:durch (?:das )?kupfer )?(?:langsamer|langsamer beweglich|weniger beweglich)'),
    'durch (?:das )?kupfer (?:bewegen sich|schwimmen) '+swimmers+' '+reduced);
  gram.kupfer.b.push(...frame(refer,'schaffen','es '+reduced+' (?:bis )?(?:zur eizelle|zum ei)'),
    word(refer)+' (?:die eizelle|das ei) '+reduced+' (?:erreichen|befruchten) koennen',
    'koennen '+word(refer)+' (?:die eizelle|das ei) '+reduced+' (?:erreichen|befruchten)',
    '(?:die |eine )?eizelle (?:wird|kann) '+reduced+' befruchtet (?:werden)?');
  gram.pille.a.push('(?:mit der pille|unter der pille|durch die pille) (?:bleibt der eisprung aus|faellt der eisprung (?:aus|weg))',
    '(?:normalerweise |meist )?faellt (?:mit|unter) der pille der eisprung (?:aus|weg)');
  gram.pille.b.push('fehlt (?:die |eine )?(?:freie |befruchtbare )?eizelle','(?:dann )?(?:es )?gibt (?:es )?(?:auch )?nichts (?:zum befruchten|zur befruchtung)',
    '(?:dann )?gibt es (?:auch )?nichts,? was die spermien befruchten koennten','spermien koennen (?:somit )?kein ei befruchten',
    'es gibt keine eizelle mehr die befruchtet werden kann');
  gram.schleim.ab.push('(?:der |ein )?(?:dickfluessige[rn]?|zaehe[rn]?|dichte[rn]?) (?:schleim|schleimpfropf) (?:versperrt|erschwert) den (?:spermien|samenzellen) (?:fast |weitgehend )?(?:den weg|die passage)');
  gram.schleim.b.push(word(refer)+' '+reduced+' (?:vorankommen|durchkommen|weiterkommen)',
    'durch den schleim '+word(move)+' '+word(refer)+' '+reduced);
  gram.haut.a.push('(?:die )?haut (?:neben|ausserhalb) (?:dem kondom|des kondoms) kann (?:andere )?haut beruehren',
    'neben (?:dem kondom|der huelle) (?:bleibt|ist) (?:noch )?haut (?:ungeschuetzt|frei|unbedeckt)');
  gram.haut.b.push('(?:dabei|dort|so) koennen '+germs+' (?:wechseln|uebergehen|weitergegeben werden|uebertragen werden)',
    'uebertragung von (?:erregern|keimen|viren) durch hautkontakt');
  gram.kupfer.a.push('fuer (?:die )?(?:spermien|samenzellen) ist es (?:durch kupfer )?(?:schwieriger|muehsamer) zu schwimmen',
    'weil sich (?:die )?spermien schlechter bewegen');
  gram.kupfer.b.push('(?:die |eine )?eizelle wird '+reduced+' befruchtet','so schaffen weniger (?:spermien |samenzellen )?die befruchtung',
    '(?:die |sie |diese )?'+reduced+' (?:zum ei|zur eizelle) (?:kommen|gelangen)');
  gram.kupfer.negatives.bewegung.push(...frame(swimmers,'schwimmen|werden','schneller|beweglicher'));
  gram.pille.a.push('(?:der )?eisprung faellt aus','(?:meistens |meist )?springt kein ei aus dem eierstock','(?:unter|mit) der pille der eisprung ausbleibt');
  gram.pille.b.push(noCell+' (?:steht bereit|zur befruchtung|zum befruchten)','(?:dann )?ist fuer (?:die )?spermien kein ei da',
    '(?:die )?spermien (?:finden|haben) '+noCell+'(?: zum befruchten)?');
  gram.schleim.b.push('(?:so )?ist der weg fuer (?:die )?spermien schwer zu schaffen');
  gram.haut.a.push('haut ist noch frei','(?:auch )?ein (?:heiles|intaktes) kondom laesst hautstellen frei');
  gram.haut.b.push('an (?:diesen|den) (?:stellen|hautstellen) ohne schutz kann man sich (?:anstecken|infizieren)',
    'dort koennen '+germs+' (?:weitergegeben|uebertragen) werden',
    'auf (?:dieser|der) freien haut koennen '+germs+' von einem menschen zum anderen (?:kommen|gelangen)');
  gram.haut.negatives.flaeche.push(...frame(condom,'bedeckt|bedecken|schuetzt|schuetzen','die (?:ganze|gesamte) haut'));
  gram.kupfer.a.push(...frame(swimmers,'verlieren','(?:an )?tempo'));
  gram.kupfer.b.push('(?:so )?haben sie es schwerer bis zum ei');
  gram.kupfer.negatives.befruchtung.push(...frame('(?:die |eine )?befruchtung','wird','leichter|erleichtert'));
  // Rollen der Anatomie, nicht die bloße Nennung der Befruchtung.
  const herkunft='(?:aus dem |vom )?eierstock', nichtsFrei=noCell+' (?:mehr )?';
  gram.pille.b.push(nichtsFrei+herkunft+' (?:freikommt|freiwird|freigesetzt wird|abgegeben wird|austritt|springt)',
    '(?:kommt|tritt) '+noCell+' (?:aus dem eierstock )?(?:frei|aus)',
    '(?:aus dem eierstock )?wird '+noCell+' (?:aus dem eierstock )?(?:freigesetzt|abgegeben)',
    'der eierstock (?:gibt '+noCell+' (?:mehr )?frei|setzt '+noCell+' (?:mehr )?frei)');
  const ergebnisOhneZelle=new RegExp('^(?:'+['(?:die |eine )?befruchtung (?:ist (?:dann )?nicht moeglich|findet nicht statt|bleibt aus)',
    '(?:(?:es )?kommt (?:es )?nicht (?:zu einer|zur) befruchtung)', '(?:die )?eizelle kann nicht befruchtet werden'].join('|')+')$');
  const durchtritt='(?:den durchtritt|die passage|den durchgang|das durchkommen) (?:der |von )?'+swimmers;
  const hindert='erschwert|behindert|hemmt';
  gram.schleim.b.push(...frame(sauce,hindert,durchtritt),'(?:der durchtritt|die passage) (?:der |von )?'+swimmers+' (?:wird|ist) (?:erschwert|schwieriger)');
  gram.schleim.ab.push('(?:der |ein )?(?:verdickte[rn]?|zaehere[rn]?|dickere[rn]?) (?:schleim|schleimpfropf|zervixschleim) '+word(hindert)+' '+durchtritt);
  const flaeche='(?:auf|an) (?:der )?(?:unbedeckter|freier|ungeschuetzter|unbedeckten|freien|ungeschuetzten) (?:haut|hautstellen)';
  const beruehrung='(?:durch beruehrung|bei beruehrung|durch direkten hautkontakt|bei hautkontakt|durch hautkontakt)';
  gram.haut.ab.push(flaeche+' (?:koennen|werden) '+germs+' (?:'+beruehrung+' )?(?:uebertragen|weitergegeben)(?: werden)?',
    germs+' koennen '+flaeche+' (?:'+beruehrung+' )?(?:uebertragen|weitergegeben) werden',
    flaeche+' kann man sich (?:'+beruehrung+' )?(?:anstecken|infizieren)');
  gram.haut.a.push('(?:unbedeckte|freie) hautstellen bleiben (?:frei|unbedeckt)');
  const beeintraechtigt='stoert|stoeren|beeintraechtigt|beeintraechtigen|hemmt|hemmen|mindert|mindern|verringert|verringern';
  const mobil='(?:beweglichkeit|bewegung|bewegungsfaehigkeit)',fruchtbar='befruchtungsfaehigkeit';
  const eigenschaft='(?:die )?(?:'+mobil+'|'+fruchtbar+')';
  const traeger=' (?:der |von )?'+swimmers;
  gram.kupfer.b.push(...frame(copper,beeintraechtigt,'(?:die )?'+fruchtbar+traeger));
  gram.kupfer.a.push(...frame(copper,beeintraechtigt,'(?:die )?'+mobil+traeger),
    copper+' (?:schraenkt|schraenken) (?:die )?'+mobil+traeger+' ein',
    copper+' (?:die )?'+mobil+traeger+' (?:einschraenkt|einschraenken)');
  // Ein gemeinsames Subjekt/Objekt nur innerhalb eines vollständigen Satzrahmens verteilen.
  const paar=new RegExp('^('+copper+') ('+beeintraechtigt+') ('+eigenschaft+') und ('+eigenschaft+')('+traeger+')$');
  const schleimpaar=new RegExp('^('+sauce+') (wird (?:verdickt|'+thick+')|verdickt sich) und ('+hindert+') ('+durchtritt+')$');
  function koordinieren(s,id){
    return s.split(/([.!?;])/).map(teil=>{
      const c=teil.trim();
      if(id==='kupfer')return c.replace(paar,'$1 $2 $3$5 und $1 $2 $4$5');
      if(id==='schleim')return c.replace(schleimpaar,'$1 $2 und $1 $3 $4');
      return c;
    }).join(' ');
  }
  for(const [id,g] of Object.entries(gram)){
    for(const tag of ['a','b','ab','extra'])bound[id][tag]=[...(bound[id][tag]||[]),...g[tag]];
    for(const [e,patterns] of Object.entries(g.negatives))bound[id].negatives[e].push(...patterns);
  }
  function matches(list, clause){return list.some(re=>re.test(clause));}
  const compile=list=>list.map(s=>new RegExp('^(?:'+s+')$'));
  for(const m of Object.values(bound)){
    for(const tag of ['a','b','ab','extra'])m[tag]=compile(m[tag]);
    for(const key of Object.keys(m.negatives))m.negatives[key]=compile(m.negatives[key]);
  }
  function clean(s){
    return s.replace(/\n/g,';').toLowerCase().replaceAll('ä','ae').replaceAll('ö','oe').replaceAll('ü','ue').replaceAll('ß','ss')
      .replace(/\b(spermjen|spermein|spermin|spermiem)\b/g,'spermien').replace(/\bschleim[m]?\b/g,'schleim')
      .replace(/\b(eisprug|eissprung)\b/g,'eisprung').replace(/\b(?:eizzele|eizele)\b/g,'eizelle')
      .replace(/\bzaher\b/g,'zaeher').replace(/\bhautkontak\b/g,'hautkontakt').replace(/\bkupffer\b/g,'kupfer')
      .replace(/\s+/g,' ').trim();
  }
  const correctedNouns={
    eisprung:['eisprng','eisprngg','eisprun','eisprumg'],eizelle:['eizellee','eizäle','eizele','eizellle'],
    spermien:['spermine','spermiern','sperminen','spermiien'],samenzellen:['samenzelen','samenzelln'],
    schleim:['schleimm','schleihm','schleimn'],erregern:['eregern','errregern'],hautkontakt:['hautkontackt','hautkontkt'],
    kupferionen:['kupferjonen','kupferionnen'],kondom:['kondomm','kondon'],
    gebaermutterhals:['gebaermuterhals','gebarmutterhals'],befruchtung:['befruchtug','befruchtunng'],
    beweglichkeit:['beweglichket','beweglichkiet'],erreger:['ereger','erregr']
  };
  const spellings=new Map(Object.entries(correctedNouns).flatMap(([word,forms])=>forms.map(f=>[f,word])));
  function normalize(text){
    return clean(text).replace(/[–—]/g,';').replace(/[a-z]+/g,w=>spellings.get(w)||w)
      .replace(/\bnich\b/g,'nicht').replace(/\bnich(t)? mehr so einfach\b/g,'nicht mehr so leicht')
      .replace(/\bnur noch schwer\b/g,'nur schwer').replace(/\bso dass\b/g,'sodass')
      .replace(/\b(?:in der regel|in den meisten faellen)\b/g,'meist')
      .replace(/\b(?:samenfaeden|spermienzellen)\b/g,'samenzellen')
      .replace(/\b(?:gehemmt|unterdrueckt) wird\b/g,'wird gehemmt')
      .replace(/\b(?:kein ei|keine eizelle) aus dem eierstock entlassen\b/g,'keine eizelle freigesetzt')
      .replace(/\bnicht mehr so gut bewegen\b/g,'schlechter bewegen')
      .replace(/\bin der gebaermutterhalsregion\b/g,'am gebaermutterhals')
      .replace(/\bueberhaupt nicht\b/g,'nicht')
      .replace(/\b(?:menschliche )?eizelle zur befruchtung frei wird\b/g,'eizelle wird zur befruchtung frei')
      .replace(/,? (?:die|das) befruchtet werden (?:kann|koennte)\b/g,' zur befruchtung')
      .replace(/,? was die spermien befruchten koennten\b/g,' zum befruchten')
      .replace(/,\s*(?:die|welche) (?:darum|deshalb|dadurch) /g,', sodass diese ')
      .replace(/\bdeshalb dann\b/g,'deshalb')
      .replace(/\bnicht (mehr )?so einfach\b/g,'nicht $1so leicht').replace(/ +/g,' ');
  }
  // Nur diese vollständig erfassten Berichtigungen haben eine eindeutige Reichweite.
  const repairs={
    pille:[[/\b((?:die )?pille) haelt nicht (?:die )?spermien auf,? sondern (hemmt|verhindert|unterdrueckt) (?:den )?eisprung\b/g,'$1 $2 den eisprung']],
    schleim:[[/\b((?:die )?(?:hormonspirale|spirale)) macht den schleim nicht duenner,? sondern (zaeher|dicker)\b/g,'$1 macht den schleim $2'],
      [/\bder schleim wird nicht duenner,? sondern (zaeher|dicker)\b/g,'der schleim wird $1']],
    kupfer:[[/\bkupfer verhindert nicht den eisprung,? sondern (beeintraechtigt|bremst) (?:die )?spermien\b/g,'kupfer $1 spermien']],
    haut:[[/\bnicht die (?:gesamte|ganze) haut,? sondern nur ein teil (?:ist|wird) bedeckt\b/g,'ein teil der haut bleibt frei']]
  };
  const confusions={pille:['spermien'],schleim:['zyklus'],haut:['sperma'],kupfer:['zyklus','schleim']};
  const vocabulary={pille:['eisprung','eizelle'],schleim:['schleim','spermien|samenzellen'],haut:['haut(?:kontakt)?','erreger'],kupfer:['spermien|samenzellen','befruchtung']};
  function recognition(model,clause){
    for(const [error,patterns] of Object.entries(model.negatives))if(matches(patterns,clause))return {error};
    for(const tag of ['ab','a','b','extra'])if(matches(model[tag],clause))return {tag};
    return null;
  }
  // Unterscheide die benannte Nominalgruppe vom Rest des Prädikats. Nur ganze
  // Formen desselben Satzes werden umgestellt; kein Objekt oder Negator entfällt.
  const subject=/^(?:(?:die |der |das |ein |eine |kein |keine )?(?:freie |befruchtbare |manche |andere |einige )?(?:kombinationspille|pille|eisprung|eizelle|ei|samenzellen|spermien|kupferionen|kupfer|kupferspirale|hormonspirale|zervixschleim|schleim|kondome?|hautstellen|haut|befruchtungsfaehigkeit|befruchtung|erreger|keime|viren|hormone?)|(?:ein teil|teile) der haut|diese|sie)\b/;
  const finite=/^(?:wird|werden|ist|sind|bleibt|bleiben|faellt|kommen|gelangen|schwimmen|erreichen|befruchten|fehlt|fehlen|kann|koennen|finden|haben|sinkt|hemmt|hemmen|unterdrueckt|verhindert|bremst|bremsen|bedeckt|macht|machen|verdickt|verdicken)$/;
  function orderedReading(model,c){
    const direct=recognition(model,c);
    if(direct)return direct;
    const words=c.split(' ');
    if(words.length<3)return null;
    const first=words[0],last=words.at(-1);
    if(finite.test(first)){
      const rest=c.slice(first.length+1),subj=rest.match(subject)?.[0];
      if(subj){const hit=recognition(model,subj+' '+first+rest.slice(subj.length));if(hit)return hit;}
    }
    if(finite.test(last)){
      const subj=c.match(subject)?.[0];
      if(subj)return recognition(model,subj+' '+last+c.slice(subj.length,-last.length-1));
    }
    return null;
  }
  function readClause(model,clause){
    const read=orderedReading(model,clause);
    if(read)return [read];
    // Zwei vollständige Satzglieder ohne Satzzeichen. Restwörter werden nicht verworfen.
    if(clause.length<=220){
      for(const space of clause.matchAll(/ /g)){
        const left=recognition(model,clause.slice(0,space.index));
        if(!left)continue;
        const right=orderedReading(model,clause.slice(space.index+1));
        if(right)return [left,right];
      }
    }
    return [{unknown:true}];
  }
  const causes=/^(?:weil|denn|da)$/;
  const effects=/^(?:darum|daher|deshalb|dadurch|also|deswegen|sodass|somit|folglich|->|→)$/;
  function analyze(id,text){
    const model=bound[id],parts=new Set(),errors=new Set();
    let unknown=false,reversed=false,beleg=null,ergebnis=false;
    function result(state,kind=state){
      return {state,kind,ergebnis,parts:[...parts],error:beleg?.code||[...errors][0]||null,quelle:beleg?[beleg.karte,beleg.abschnitt]:null,relation:reversed?'umgekehrt':parts.size===2?'verbunden':'offen',zusatz:unknown};
    }
    let s=gesund.berichtigungen(normalize(text),id).trim();
    if(id==='haut')s=s.replace(/^auch wenn (?:das |ein )?kondom (?:heil|intakt) ist, */,'');
    if(!/[a-z0-9]/.test(s))return result('leer');
    // Keine Behauptung aus einer Frage, einem Zitat oder einer hypothetischen Verneinung ableiten.
    if(s.length>2400 || /[„“"]/.test(s))return result('unsicher');
    const vorsicht=/[?]|\b(?:vielleicht|angeblich|weiss nicht|oder|nicht sicher|wenn|falls|glaube nicht|behauptet|falsch ist|es stimmt nicht|es waere falsch|es ist falsch)\b/;
    if(vorsicht.test(s)){
      // In einem unklaren Satz keine Diagnose raten. Gesondert behauptete Risiken bleiben sichtbar.
      const satz=s.match(/[^.!?;]+[?]?/g)||[];
      for(const teil of satz){
        if(vorsicht.test(teil))continue;
        const befund=gesund.lesen(teil.trim(),id);
        if(befund?.falsch){beleg=befund;return result('fehlvorstellung');}
      }
      return result('unsicher');
    }
    s=koordinieren(s,id);
    for(const [from,to] of repairs[id])s=s.replace(from,to);
    // Eine vollständig erklärte Gegenwirkung bleibt erhalten, auch bei geteilter Subjektgruppe.
    s=s.replace(/(samenzellen|spermien) (kommen|schwimmen) (kaum noch|langsamer|schlechter) voran und (erreichen|befruchten) (das ei|die eizelle) deshalb /g,'$1 $2 $3 voran, deshalb $4 sie $5 ')
      .replace(/\bund (deshalb|dadurch|daher) (die eizelle|das ei) (schwerer|schlechter) (erreichen|befruchten)\b/g,', $1 koennen sie $2 $3 $4')
      .replace(/\bund (deshalb|dadurch|daher)\b/g,', $1')
      .replace(/\b((?:die )?(?:samenzellen|spermien)) (kommen|gelangen|schwimmen) (deshalb|dadurch|daher) /g,'$3 $2 $1 ')
      .replace(/\bdas ist (?:darum|deshalb) so,? weil /g,'weil ')
      .replace(/\b(bleibt) aber nicht aus\b/g,'$1 nicht aus').replace(/,\s*(aber|und) /g,' $1 ');
    if(id==='kupfer')s=s.replace(/(samenzellen|spermien) (schwimmen|kommen) (schlechter|langsamer)( voran)? und (erreichen|befruchten) /g,'$1 $2 $3$4 und sie $5 ');
    s=s.replace(/\bso dass\b/g,'sodass');
    const leading=s.match(/^(weil|da)\s+/);
    if(leading)s=s.slice(leading[0].length);
    const chunks=s.split(/(\s*[,.;:]?\s*\b(?:weil|da|denn|dadurch|deshalb|daher|darum|sodass|also|deswegen|somit|folglich)\b\s*|\s+aber\s+|\s+und\s+(?!(?:befruchten sie|befruchten die eizelle))|\s*(?:->|→)\s*|[!.,;:\n]+)/);
    let last='',link='',first=true;
    for(let i=0;i<chunks.length;i++){
      if(i%2){const token=chunks[i].trim().replace(/^[,.;:]\s*/, '');if(token||!link)link=token;continue;}
      let c=chunks[i].trim().replace(/ (?:und|aber)$/,'');
      if(!c||c==='aber'||c==='und')continue;
      c=c.replace(/^dort (koennen|werden) ((?:manche |einige )?(?:erreger|keime|viren)) (weitergegeben|uebertragen) werden$/,'$2 koennen bei hautkontakt $3 werden')
        .replace(/^(der schleim) (zaeher|dicker|dichter) wird$/,'$1 wird $2')
        .replace(/^(die pille) den eisprung (hemmt|verhindert)$/,'$1 $2 den eisprung')
        .replace(/^kupfer (?:die )?spermien bremst$/,'kupfer bremst spermien')
        .replace(/^(ein teil der haut) (frei|unbedeckt) bleibt$/,'$1 bleibt $2')
        .replace(/^dort (koennen|werden) /,'$1 ').replace(/^bei hautkontakt koennen sie /,'bei hautkontakt koennen erreger ');
      // „Ihre Beweglichkeit“ bezieht sich nur auf zuvor ausdrücklich genannte Samenzellen.
      if(id==='kupfer' && last==='b' && /\b(spermien|samenzellen)\b/.test(chunks[i-2]||'')){
        c=c.replace(/\bihre (beweglichkeit|bewegung|bewegungsfaehigkeit)\b/,'die $1 der spermien');
      }
      if(c==='korrigierter zusatz'){unknown=true;continue;}
      if(id==='pille' && ergebnisOhneZelle.test(c)){ergebnis=true;continue;}
      const medizin=gesund.lesen(c,id);
      if(medizin){
        if(medizin.falsch){beleg??=medizin;errors.add(medizin.code);}
        continue;
      }
      for(const item of readClause(model,c)){
        if(item.error){errors.add(item.error);continue;}
        if(item.unknown){unknown=true;continue;}
        if(item.tag==='extra')continue;
        for(const tag of item.tag){
          if((first && leading && tag==='b') || (last && last!==tag &&
            ((causes.test(link)&&tag==='b')||(effects.test(link)&&tag==='a'))))reversed=true;
          parts.add(tag);last=tag;first=false;link='';
        }
      }
      link='';
    }
    if(errors.size){
      if(parts.size)return result('widerspruch');
      return result('fehlvorstellung',confusions[id].includes([...errors][0])?'verwechslung':'fehlvorstellung');
    }
    if(parts.size===2 && /nicht immer/.test(s))return result('unsicher','beziehung');
    if(reversed && parts.size===2)return result('vertauscht','beziehung');
    if(reversed)return result('unsicher','beziehung');
    if(unknown){
      if(parts.size===2)return result('unsicher','zusatz');
      const terms=vocabulary[id];
      const keywords=new RegExp('^(?:'+terms.join('|')+'|die|der|das|und|pille|hormone|kupfer|kondom)$');
      if(!parts.size && s.split(/\s+/).length<=6 && terms.every(t=>new RegExp('\\b(?:'+t+')\\b').test(s)) &&
        s.split(/[ ,.;:]+/).filter(Boolean).every(w=>keywords.test(w)))return result('unsicher','beziehung');
      return result('unsicher');
    }
    if(ergebnis && !parts.size)return result('teilweise','ergebnis');
    return result(parts.size===2?'passend':parts.size?'teilweise':'unsicher');
  }
  return {analyze,gesundheit:gesund.katalog};
})();
if(typeof module!=='undefined' && module.exports)module.exports=Lernfeedback;
