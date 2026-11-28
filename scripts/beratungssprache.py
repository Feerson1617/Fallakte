"""Die Frage am Eingabefeld und ihr biologischer Bezug je Empfehlung."""
METHODEN={'K':'das Kondom','P':'die Pille','Cu':'die Kupferspirale','H':'die Hormonspirale'}
AUSWAHL={
    'L01':'Laura verträgt kein Latex. Was rätst du ihr?',
    'L02':'Laura möchte sich auch vor Infektionen beim Sex schützen. Was rätst du ihr?',
    'L03':'Laura vergisst manchmal, was sie täglich tun muss. Was rätst du ihr?',
    'L04':'Laura hat starke Regelschmerzen. Was rätst du ihr?',
    'L05':'Was empfiehlst du Laura am Ende des Gesprächs?'}
KONTROLLFRAGE={
    'L01':'Kann ein Kondom auch ohne Latex Sperma zurückhalten?',
    'L02':'Welche Verhütung senkt das Risiko, sich beim Sex anzustecken?',
    'L03':'Was passiert mit dem Schutz, wenn Laura ihre Pille vergisst?',
    'L04':'Was können Spiralen an Lauras Regelschmerzen ändern?',
    'L05':'Was schützt Laura vor Schwangerschaft und was vor Ansteckung beim Sex?'}
FRAGEN={
    'L01':{'K':'Welches Kondom kann Laura trotz ihrer Latexallergie benutzen?',
           'P':'Wie verhindert die Pille eine Schwangerschaft?',
           'Cu':'Was macht das Kupfer der Kupferspirale mit den Spermien?',
           'H':'Wie erschwert die Hormonspirale den Spermien den Weg?',
           'K+P':'Was hält beim Kondom ohne Latex die Spermien zurück? Wie wirkt die Pille?',
           'K+Cu':'Wie wirken das Kondom ohne Latex und die Kupferspirale auf Spermien?',
           'K+H':'Wie halten das Kondom ohne Latex und die Hormonspirale Spermien auf?'},
    'L02':{'K':'Wie schützt das Kondom vor Schwangerschaft und vor einer Ansteckung?',
           'P':'Wovor schützt die Pille? Was braucht Laura zum Schutz vor HIV?',
           'Cu':'Wovor schützt die Kupferspirale? Was braucht Laura zum Schutz vor HIV?',
           'H':'Wovor schützt die Hormonspirale? Was braucht Laura zum Schutz vor HIV?'},
    'L03':{'K':'Wann braucht Laura ein neues Kondom?',
           'P':'Was kann passieren, wenn Laura die Pille vergisst?',
           'Cu':'Muss Laura mit der Kupferspirale täglich Tabletten nehmen?',
           'H':'Muss Laura mit der Hormonspirale täglich Tabletten nehmen?',
           'K+P':'Wann braucht Laura das Kondom und wann muss sie die Pille nehmen?'},
    'L04':{'K':'Was ändert ein Kondom an Regelschmerzen?',
           'P':'Wie kann die Pille Lauras Regelschmerzen verändern?',
           'Cu':'Wie kann die Kupferspirale Lauras Regelschmerzen verändern?',
           'H':'Wie kann die Hormonspirale Lauras Regelschmerzen verändern?',
           'K+P':'Was kann die Pille an Regelschmerzen ändern? Wofür braucht Laura das Kondom?'},
    'L05':{'K':'Warum rätst du Laura zum Kondom ohne Latex?',
           'P':'Was spricht für die Pille? Welcher Schutz fehlt Laura dann?',
           'Cu':'Was spricht für die Kupferspirale? Was bedeuten Lauras Schmerzen für deinen Rat?',
           'H':'Was spricht für die Hormonspirale? Was muss Laura vor dem Einsetzen entscheiden?'}}
VERTIEFUNG={
    'L01':'Warum muss Laura bei einer Latexallergie nicht auf jedes Kondom verzichten?',
    'L02':'Wo kann trotz Kondom Haut die Haut eines anderen Menschen berühren?',
    'L03':'Lauras Freundin hatte mit der Pille Beschwerden. Was weiß Laura damit über ihren eigenen Körper?',
    'L04':'Wer kann die Ursache der Schmerzen untersuchen? Wer entscheidet über eine Spirale?',
    'L05':'Welcher Wunsch von Laura zählt für dich am meisten? Wann würdest du ihr anders raten?'}
SATZSTART={
    'L01':'„Bei einer Latexallergie kann Laura …, weil …“',
    'L02':'„Vor Schwangerschaft schützt … Beim Schutz vor HIV …“',
    'L03':'„Wenn Laura die Pille vergisst, … Ein Kondom braucht sie …“',
    'L04':'„Bei starken Regelschmerzen … Vor dem Einsetzen …“',
    'L05':'„Ich rate Laura zu …, weil ihr … wichtig ist. Wenn …, würde ich …“'}
def empfehlung(stufe,key):
    if key in FRAGEN[stufe]:return FRAGEN[stufe][key]
    mittel=METHODEN[key.split('+')[1]]
    return {'L02':f'Wie schützen das Kondom und {mittel} vor Schwangerschaft und HIV?',
            'L03':f'Was muss Laura beim Kondom jedes Mal tun? Wie lange wirkt {mittel}?',
            'L04':f'Wie kann {mittel} die Regelschmerzen verändern? Wofür braucht Laura das Kondom?',
            'L05':f'Warum rätst du Laura zum Kondom und zusätzlich zur {mittel[4:].capitalize()}?'}[stufe]
def beschriften(bank):
    for stufe,stage in bank['stages'].items():
        for tier,task in stage['levels'].items():
            task['choiceQuestion']=AUSWAHL[stufe]
            task['controlQuestion']=KONTROLLFRAGE[stufe]
            for key,way in [('vorher',task['before']),*task['strategies'].items()]:
                card=bank['cards'][way['card']['method']]
                section=card['sections'][way['card']['section']]
                frage=AUSWAHL[stufe] if key=='vorher' else empfehlung(stufe,key)
                way['question']=frage
                # Beim Schreiben bleibt der jeweilige biologische Denkanspruch erhalten.
                way['writeQuestion']=frage
                if tier in ('MSA','AHR'):
                    if stufe=='L01' and key in ('P','Cu','H'):way['writeQuestion']+=' Welche Rolle spielt Latex dabei?'
                    elif stufe=='L03':way['writeQuestion']+=' Was sagen die Erfahrungen der Freundin über Laura aus?'
                    elif stufe=='L04':way['writeQuestion']+=' Wer klärt die Schmerzen ab?'+(' Wer entscheidet über das Einsetzen?' if 'H' in key or 'Cu' in key else '')
                    elif stufe=='L05':way['writeQuestion']+=' Wann würdest du ihr anders raten?'
                if key=='vorher':way['writeQuestion']=frage
                source=f'Lies auf der Karte „{card["title"]}“ den Abschnitt „{section["title"]}“.'
                example=(way['condition'] if key!='vorher' else section['levels'][tier])
                way['hints']=[source,frage,VERTIEFUNG[stufe],SATZSTART[stufe],example]
                way['evidence']=frage
    return bank
