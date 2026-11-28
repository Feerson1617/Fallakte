// Eine erkannte Behauptung kann korrigiert werden. Alle anderen Freitexte bleiben ungeprüft.
const Entwurf = (() => {
  const methods=['K','P','Cu','H'];
  const sections=[
    ['material','wirkung','sti','alltag','schmerzen'],['wirkung','sti','alltag','eignung','schmerzen'],
    ['wirkung','sti','alltag','einlage','schmerzen'],['wirkung','sti','alltag','einlage','schmerzen']
  ];
  function fehler(text,weitere=[]) {
    const own=text.replace(/„[^“]*“|»[^«]*«|«[^»]*»|"[^"]*"/gu,' ');
    const normal=own.toLocaleLowerCase('de').normalize('NFC').replaceAll('ä','ae').replaceAll('ö','oe').replaceAll('ü','ue').replaceAll('ß','ss');
    // Zitate, berichtete Rede, Fragen und ausdrückliche Rücknahmen sind kein eindeutiges Eigenurteil.
    const clauses=Fachwissen.berichtigungen(normal,'').replace(/\bpillle\b/gu,'pille')
      .replace(/([^.!?;]+)\?/gu,' ').split(/[.!;]+(?=\s|$)/u);
    const issues=[];
    const verstanden=new Map();
    const kennung=m=>[m.code,m.name,m.ziel||''].join('/');
    const positive={
      sti:'Du hast den fehlenden Schutz vor Ansteckung richtig erklärt.',
      kupferhormone:'Du hast richtig erkannt, dass Kupfer ohne Hormone wirkt.',
      hormonabgabe:'Du hast die Hormonabgabe richtig erklärt.',
      einnahme:'Dein Hinweis zum Einnahmeplan stimmt.'
    };
    function collect(s){
      const match=Fachwissen.lesen(s,'');
      if(match && !match.falsch && positive[match.code])verstanden.set(kennung(match),positive[match.code]);
      if(match?.falsch){
        const fact=Fachwissen.katalog[match.code];
        return {kennung:kennung(match),ref:{method:methods[match.karte],section:sections[match.karte][match.abschnitt]},frage:fact.frage,info:fact.info};
      }
      return weitere.find(rule=>rule.satz.test(s));
    }
    for(const [index,clause] of clauses.entries()){
      const s=clause.trim().replace(/\s+/gu,' ');
      if(!s || /(?:weiss|wissen|glaube|glauben) nicht[, ]|sicher bin ich nicht/u.test(s) || /[:„“]|\b(?:behauptet|behaupten|fragt|meint|sagt|angeblich|vielleicht|ob)\b/u.test(s))continue;
      if(/^(?:das (?:stimmt nicht|ist falsch|war falsch)|nein, eine spaetere schwangerschaft bleibt moeglich)$/u.test(s)){
        const previous=issues.at(-1);
        if(previous && previous.index===index-1 &&
          (!s.startsWith('nein') || previous.issue.quelle==='Später schwanger werden'))issues.pop();
        continue;
      }
      // Getrennte Behauptungen nur bei zwei ausdrücklich genannten Subjekten.
      if(/(?:stimmt nicht|ist falsch|bezweifle|glaube nicht|nicht so),? dass |^es stimmt nicht/u.test(s))continue;
      const correction=s.match(/^(?:nein,|ich korrigiere mich,) (.+)$/u);
      if(correction){
        const fact=Fachwissen.lesen(correction[1],'');
        if(fact && !fact.falsch){
          const i=issues.findLastIndex(x=>x.issue.kennung===kennung(fact));
          if(i>=0)issues.splice(i,1);
        }
        continue;
      }
      const parts=s.split(/(?: und |, aber )(?=(?:die |eine |ein |das )(?:pille|kupferspirale|hormonspirale|kondom)\b)/u);

      for(const part of parts){
        const claim=part.replace(/^ich (?:empfehle|wähle|waehle|nehme) (die (?:pille|kupferspirale|hormonspirale)),? weil sie (?:auch )?vor hiv schuetzt$/u,'$1 schuetzt vor hiv').replace(/^ich (?:denke|glaube|finde),? (?:dass )?(die (?:pille|kupferspirale|hormonspirale)) (?:auch )?vor hiv schuetzt$/u,'$1 schuetzt vor hiv').replace(/^die pille ist meine wahl, weil sie (vor hiv) schuetzt$/u,'die pille schuetzt $1');
        const issue=collect(claim);
        if(issue)issues.push({issue,index});
      }
    }
    if(!issues.length)return null;
    const found=issues.map(row=>row.issue);
    for(const issue of found)verstanden.delete(issue.kennung);
    const correction=[...new Set(found.map(v=>v.info))].join(' ');
    const known=verstanden.values().next().value;
    return {...found[0],info:known?correction+' '+known:correction};
  }
  function hilfen(quelle,frage,fakt){
    const parts=fakt.match(/[^.!?]+[.!?]+|[^.!?]+$/gu) || [fakt];
    const detail=parts.find(line=>!line.includes('?'))?.trim() || fakt;
    return [frage+' ('+quelle+')','Achte auf den Unterschied: '+detail,'Prüfe diesen Satz: '+detail,fakt,'Vergleiche deinen Grund mit der Korrektur: '+fakt];
  }
  function bearbeiten(field){
    Arbeitsplatz.zeigen(field);field.focus({preventScroll:true});
  }
  return {fehler,hilfen,bearbeiten};
})();
