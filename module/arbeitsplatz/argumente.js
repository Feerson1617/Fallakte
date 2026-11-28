// Ein vollständiger Satz oder eine sinngleiche Kurzantwort im jeweiligen Textkontext.
// Die Art des Arguments und die persönliche Zustimmung dazu sind voneinander unabhängig.
const Argumente=(()=>{
 const rolle={
 'Mutter/Wert':[/^(?:ihr ist wichtig,? dass (?:laura|ihre tochter) gesund bleibt|(?:sie möchte,? |sie will,? )?dass es (?:ihrer tochter|laura) körperlich gut geht|(?:dass )?(?:mama|die mutter) sich um die gesundheit ihrer tochter sorgt)$/u],
 'Mutter/Norm':[/^(?:(?:beschwerden|schmerzen) (?:sollte|darf) man nicht (?:ignorieren|übergehen)|man (?:muss|sollte) (?:auf seine gesundheit aufpassen|die signale (?:des|seines) körpers beachten))$/u],
 'Mutter/Folgerung':[/^(?:(?:sie (?:rät ihr dazu|empfiehlt laura),? )?schwanger (?:zu )?bleiben|(?:dass laura|laura soll) das kind zur welt (?:bringt|bringen)|nicht abtreiben|sie soll die schwangerschaft austragen|(?:sie|laura) soll die schwangerschaft nicht abbrechen|kind bekommen)$/u],
 'Mutter/Leerstelle':[/^(?:(?:der medizinische grund|eine überprüfbare aussage zum körper) fehlt|welche folgen ein abbruch für den körper hat|ein beleg über die körperlichen folgen|es fehlt eine überprüfbare biologische aussage)$/u],
 'Mutter/Ergänzung':[/^(?:(?:man blutet|es blutet) und der bauch kann weh ?tun|es kann zu krämpfen kommen und man bekommt blutungen|blutungen und mögliche schmerzen|blutung(?:en)? und bauchkrämpfe können auftreten)$/u],
 'Freundin/Wert':[/^(?:(?:die freundin möchte,? )?dass laura (?:ihre eigenen pläne umsetzen|ihre ausbildung fertig machen und selbst planen) kann|ihr ist lauras berufliche zukunft wichtig|selbst über (?:die|ihre) zukunft entscheiden)$/u],
 'Freundin/Norm':[/^(?:kinder erst dann,? wenn man selbst bereit dafür ist|man sollte erst (?:ein kind|kinder) (?:kriegen|bekommen),? wenn man sich (?:dazu )?bereit fühlt|man soll selbst entscheiden,? wann ein kind ins eigene leben passt)$/u],
 'Freundin/Folgerung':[/^(?:sie rät ihr,? die schwangerschaft zu beenden|abtreibung mit tabletten|laura soll die schwangerschaft abbrechen lassen|sie soll einen medikamentösen schwangerschaftsabbruch machen lassen)$/u],
 'Freundin/Leerstelle':[/^(?:ob laura später noch kinder kriegen kann|ein biologischer beleg zum späteren kinderwunsch|es fehlt eine medizinische information|eine überprüfbare aussage zum körper fehlt)$/u],
 'Freundin/Ergänzung':[/^(?:wenn (?:alles|der abbruch) ohne komplikationen verläuft,? kann (?:laura|sie|man) später (?:noch |wieder )?kinder (?:bekommen|kriegen)|ein komplikationsloser abbruch bedeutet nicht,? dass man unfruchtbar wird|später kinder (?:kriegen|bekommen) ist danach weiterhin möglich|ja,? wenn es keine komplikationen gibt)$/u],
 'Großmutter/Norm':[/^(?:man soll(?:te)? das leben (?:eines embryos|vor der geburt) schützen|(?:das ungeborene leben|ungeborene kinder) sollte man schützen)$/u],
 'Großmutter/Leerstelle':[/^(?:was ihr persönlich wichtig ist|der persönliche wert ist nicht ausdrücklich genannt|sie sagt nicht direkt,? was ihr wichtig ist)$/u],
 'Großmutter/Ergänzung':[/^(?:ihr ist das leben vor der geburt wichtig|dass ungeborenes leben geschützt wird|das leben des embryos|ihr liegt das ungeborene leben am herzen)$/u],
 'Vater/Wert':[/^(?:dass laura nach guten informationen ihre eigene entscheidung trifft|die entscheidung soll laura selbst treffen und sich vorher informieren|ihm ist ihre selbstbestimmung wichtig|lauras selbstbestimmung und gute informationen)$/u],
 'Vater/Folgerung':[/^(?:laura soll sich beim arzt über ihre möglichkeiten informieren|sie soll in der praxis fragen,? was möglich ist|er rät ihr,? sich ärztlich beraten zu lassen|zum arzt gehen und nachfragen)$/u],
 'Vater/Leerstelle':[/^(?:es fehlt eine allgemeine regel|er nennt keine allgemeine handlungsregel|eine regel für solche entscheidungen fehlt|die norm ist nicht ausdrücklich genannt)$/u],
 'Vater/Ergänzung':[/^(?:vor einer medizinischen entscheidung sollte man sich gut beraten lassen|man sollte vorher verlässliche informationen sammeln|man muss sich vor wichtigen entscheidungen gut informieren|erst informieren,? dann selbst entscheiden)$/u]
 };
 rolle['Großmutter/Folgerung']=rolle['Mutter/Folgerung'];
 return {passt:(key,text)=>rolle[key]?.some(re=>re.test(text))};
})();
