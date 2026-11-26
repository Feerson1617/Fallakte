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
    const clauses=Fachwissen.berichtigungen(normal,'').split(/[.!;]+(?:\s|$)/u);
    for(const clause of clauses){
      const s=clause.trim().replace(/\s+/gu,' ');
      const match=Fachwissen.lesen(s,'');
      if(match?.falsch){
        const fact=Fachwissen.katalog[match.code];
        return {ref:{method:methods[match.karte],section:sections[match.karte][match.abschnitt]},frage:fact.frage,info:fact.info};
      }
      const other=weitere.find(rule=>rule.satz.test(s));
      if(other)return other;
    }
    return null;
  }
  function hilfen(quelle,frage,fakt){
    const parts=fakt.match(/[^.!?]+[.!?]+|[^.!?]+$/gu) || [fakt];
    const detail=parts.find(line=>!line.includes('?'))?.trim() || fakt;
    return ['Lies: '+quelle+'.',frage,'Prüfe diesen Satz: '+detail,fakt,'Vergleiche deinen Grund mit der Korrektur: '+fakt];
  }
  return {fehler,hilfen};
})();
