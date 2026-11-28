// Satzmodelle gelten jeweils für einen konkreten Gesprächsanlass. Ein Treffer
// bestätigt nur die benannte Aussage, auch wenn der übrige Entwurf offen bleibt.
const Aussagen=(()=>{
  const norm=s=>s.toLocaleLowerCase('de').replaceAll('ß','ss').replace(/\s+/gu,' ').trim();
  const saetze=s=>norm(s).split(/[.!?;]+/u).map(s=>s.trim()).filter(Boolean);
  const vergleich={
    latex:['Auch ein passendes latexfreies Kondom hält Sperma zurück.',/^(?:auch )?(?:ohne latex|bei einer latexallergie) kann (?:ein |das )?kondom (?:sperma|spermien|samenzellen) (?:zurückhalten|auffangen)$/u],
    infektionen:['Ein Kondom senkt das Risiko vieler Infektionen.',/^(?:geeignete |passende )?kondome (?:senken|verringern|mindern) (?:die gefahr|das risiko) (?:von |für )(?:ansteckungen|viele infektionen|infektionen beim sex)$/u],
    vergessen:['Eine vergessene Pille kann den Schwangerschaftsschutz mindern.',/^wenn (?:laura|sie|man) (?:die |eine )?pille vergisst,? (?:kann (?:sie|laura|man) schwanger werden|kann der schutz (?:nachlassen|sinken))$/u],
    langzeit:['Eine Spirale braucht keine tägliche Einnahme.',/^(?:eine |die )?(?:kupfer|hormon)?spirale (?:muss|braucht) man nicht (?:jeden tag|täglich) (?:zu )?(?:nehmen|einzunehmen|einnehmen)$/u],
    kupferschmerz:['Bei einer Kupferspirale können Regelschmerzen stärker werden.',/^(?:mit kupfer|mit (?:einer|der) kupferspirale) können (?:die |ihre )?(?:regel)?schmerzen (?:stärker|schlimmer) werden$/u],
    hormonschmerz:['Eine Hormonspirale kann Regelschmerzen lindern.',/^(?:die |eine )?hormonspirale kann (?:die )?(?:regel)?schmerzen (?:lindern|mindern)$/u],
    abklaeren:['Die Ursache starker Schmerzen sollte ärztlich abgeklärt werden.',/^(?:die ärztin|der arzt) soll (?:vorher )?(?:schauen|prüfen|klären),? woher die schmerzen kommen$/u],
    doppelschutz:['Das Kondom hält Spermien zurück und senkt das Risiko vieler Infektionen.',/^kondome halten (?:sperma|spermien|samenzellen) zurück und schützen (?:auch )?vor vielen (?:infektionen|sti)$/u],
    eisprung:['Die Pille hemmt meist den Eisprung.',/^(?:die |eine )?(?:kombinations)?pille (?:hemmt|unterdrückt|verhindert) (?:meist |meistens )?(?:den )?eisprung$/u],
    kupfer:['Kupfer hemmt die Beweglichkeit von Spermien.',/^(?:kupfer|kupferionen) (?:hemmt|hemmen|mindert|mindern) die beweglichkeit (?:der |von )(?:spermien|samenzellen)$/u],
    schleim:['Die Hormonspirale macht den Schleim am Gebärmutterhals zäher.',/^die hormonspirale (?:macht den schleim am gebärmutterhals zäher|verdickt den schleim am gebärmutterhals)$/u],
    barriere:['Das Kondom hält Spermien zurück.',/^(?:ein |das )?kondom hält (?:das |die )?(?:sperma|spermien|samenzellen) zurück$/u]
  };
  // Dieselbe Teilinformation kann mit der Ursache oder mit der Wirkung beginnen.
  const varianten={
    latex:[/^(?:ein |das )?(?:passendes |geeignetes )?latexfreies kondom (?:fängt|hält) (?:das |die )?(?:sperma|spermien|samenzellen) (?:auf|zurück)$/u],
    eisprung:[/^(?:weil|da) die (?:kombinations)?pille den eisprung (?:hemmt|unterdrückt),? (?:wird keine eizelle frei|kann keine eizelle befruchtet werden)$/u],
    vergessen:[/^(?:der schutz (?:sinkt|kann sinken)|eine schwangerschaft ist möglich),? wenn (?:laura|sie) (?:ihre|die) pille vergisst$/u],
    langzeit:[/^(?:bei|mit) (?:einer|der) (?:kupfer|hormon)?spirale (?:entfällt die tägliche einnahme|muss laura nicht täglich an die einnahme denken)$/u],
    infektionen:[/^(?:ein |das )?kondom (?:senkt|verringert) (?:das risiko|die gefahr),? sich (?:beim sex )?anzustecken$/u],
    kupfer:[/^(?:die )?(?:spermien|samenzellen) (?:bewegen sich|schwimmen) durch (?:das )?kupfer (?:schlechter|langsamer)$/u],
    schleim:[/^durch (?:das hormon|die hormone) (?:der hormonspirale )?wird der schleim am gebärmutterhals (?:dicker|zäher)$/u],
  };
  const ohneBarriere=['Pille und Spiralen bilden keine Barriere gegen sexuell übertragbare Erreger.',
    /^(?:die |eine )?(?:pille|kupferspirale|hormonspirale|spirale) (?:schützt nicht vor (?:hiv|sti|ansteckung)|bietet keinen (?:sti-schutz|schutz vor hiv))$/u];
  vergleich.ohneBarriere=ohneBarriere;
  const anlass={L01:['latex'],L02:['infektionen','doppelschutz'],L03:['vergessen','langzeit'],L04:['kupferschmerz','hormonschmerz','abklaeren'],L05:['doppelschutz','infektionen','langzeit','abklaeren']};
  const methode={K:'barriere',P:'eisprung',Cu:'kupfer',H:'schleim'};
  const gewicht={
    L01:'Was ändert die Latexallergie an der Anwendung deiner gewählten Methode?',
    L02:'Welche der beiden Schutzwirkungen hat deine gewählte Methode? Wo bleibt ein Risiko?',
    L03:'Wann muss Laura im Alltag an deine Methode denken?',
    L04:'Was möchte Laura vor einer Entscheidung wegen ihrer Schmerzen klären?',
    L05:'Welches Anliegen wiegt für dich stärker? Welche Grenze bleibt?'
  };
  const satzstart={L01:'Wegen der Latexallergie …',L02:'Beim Schutz vor Ansteckung … Beim Schutz vor Schwangerschaft …',
    L03:'In Lauras Alltag …',L04:'Wegen der Regelschmerzen … Über eine Einlage …',L05:'Für Laura wiegt … schwerer, weil …'};
  function beratung(stage,methods,way,frage){
    return {frage,key:stage+'/'+methods.join('+'),persoenlich:true,pille:methods.includes('P'),
      beispiel:way.options.find(o=>o.correct).text,quelle:way.condition,bezug:way.evidence,
      gewicht:gewicht[stage],anfang:satzstart[stage],hilfen:way.hints,merkmale:[...anlass[stage],...methods.map(m=>methode[m]),...(stage!=='L01' && methods.some(m=>m!=='K')?['ohneBarriere']:[])]};
  }
  function treffer(text,m){
    if(!m.bezug)return '';
    // Eine zitierte, bezweifelte oder zurückgenommene Aussage ist kein eigener Beleg.
    if(/[„“»«"?]|(?:stimmt nicht|ist falsch|behauptet|bezweifle|weiß nicht|angeblich)/iu.test(text))return '';
    const known=saetze(m.beispiel||''),parts=saetze(text);
    const hits=new Set();
    for(const part of parts){
      const i=known.indexOf(part);
      if(i>=0 && part.length>12 && !/^(?:sie|dies|diese|dann) /u.test(part)){
        hits.add(m.beispiel.match(/[^.!?;]+/gu)[i].trim().replace(/[.,]$/u,'')+'.');
      }else{
        const key=m.merkmale?.find(k=>vergleich[k][1].test(part)||varianten[k]?.some(pattern=>pattern.test(part)));
        if(key)hits.add(vergleich[key][0]);
      }
    }
    return [...hits].join(' ');
  }
  return {beratung,treffer};
})();
