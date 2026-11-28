"""Sichtbare Satzbezüge und fachliche Hilfen im Familienrat."""

PERSON = {'Mutter': 'Mama', 'Freundin': 'die Freundin', 'Großmutter': 'die Großmutter', 'Vater': 'der Vater'}
MEDIZIN = {
    'Mutter': ['Was macht die Gebärmutter beim Abbruch mit Medikamenten?',
               'Die Gebärmutter ist ein Muskel. Sie zieht sich zusammen.',
               'Beim Abbruch kommt es zu Blutungen. Wie kann sich das Zusammenziehen anfühlen?',
               '„Es kommt zu Blutungen. Im Bauch kann …“',
               'Es kommt zu Blutungen. Schmerzen und Krämpfe sind möglich.'],
    'Freundin': ['Was passiert nach einem Abbruch ohne Komplikationen mit der Fruchtbarkeit?',
                 'Laura kann später wieder schwanger werden.',
                 'Kann man Laura deshalb ein späteres Kind versprechen?',
                 '„Nach einem Abbruch ohne Komplikationen ist eine Schwangerschaft später …“',
                 'Eine spätere Schwangerschaft bleibt möglich. Garantieren kann sie niemand.']}
TRANSFER = {
    'Mutter':'Ein Abbruch mit Medikamenten braucht keine Operation. Kann der Bauch trotzdem krampfen? Beweist das, was Laura weniger belastet?',
    'Freundin':'Kann Laura nach einem Abbruch sicher ein Kind bekommen? Wer entscheidet, was zu ihrer Ausbildung passt?'}
GEWICHT = ['Welche Frage beschäftigt Laura: Schmerzen beim Abbruch oder später Kinder bekommen?',
           'Beim Abbruch kann der Bauch wehtun. Nach einem Abbruch ohne Komplikationen sind später Kinder möglich.',
           'Kann jemand Laura versprechen, wie stark es wehtut oder ob sie später ein Kind bekommt?',
           '„Für Laura zählt für mich … besonders, weil …“',
           'Blutungen und mögliche Schmerzen betreffen Laura beim Abbruch. Die Fruchtbarkeit betrifft ihren Wunsch nach späteren Kindern. Laura entscheidet selbst.']
RUECKMELDUNGEN = {
    ('Großmutter','Folgerung'): 'Die Großmutter schreibt: „Deshalb rate ich dir, die Schwangerschaft fortzusetzen.“',
    ('Vater','Folgerung'): 'Der Vater schreibt: „Deshalb rate ich dir, in der Arztpraxis nach deinen Möglichkeiten zu fragen.“'}
def familie_beschriften(bank,quellen):
    for name,c in bank['cases'].items():
        for task in c['tasks']:
            key=task['id']
            if key=='Ergänzung' and name in MEDIZIN:
                task['hints']=MEDIZIN[name].copy()
            elif key in quellen[name]:
                quote='„'+quellen[name][key][-1]+'“'
                tail=next(a['text'] for a in task['answers'] if a['ok'])
                label=PERSON[name]
                lens={'Wert':f'Was ist {label} wichtig?' if name=='Mutter' else task['prompt'],
                      'Norm':'Gilt die Regel auch für andere Menschen?',
                      'Folgerung':'Was soll Laura nach dem Rat tun?'}[key]
                starters={'Wert':'„Wichtig ist …“','Norm':'„Man sollte …“','Folgerung':'„Laura soll …“'}
                task['hints']=[f'Nachricht · {name}: '+quote,lens,
                         {'Wert':'Welchen Wunsch hörst du in dem Satz?', 'Norm':'Die Norm sagt, was man tun sollte.',
                          'Folgerung':'Die Folgerung ist der Rat an Laura.'}[key],starters[key],tail]
            elif key=='Leerstelle':
                category='Norm' if name=='Großmutter' else 'Folgerung'
                quote='„'+quellen[name][category][-1]+'“'
                missing=c['missing']
                finish={'Fakt':'Eine biologische Erklärung für den Rat fehlt.',
                        'Wert':'Der Schutz ungeborenen Lebens ist der Großmutter wichtig. Sie nennt diesen Wert nicht ausdrücklich.',
                        'Norm':'Der Vater rät zur Arztpraxis. Die allgemeine Regel hinter dem Rat spricht er nicht aus.'}[missing]
                task['hints']=['Nachricht · '+name+': '+quote,'Was sagt '+PERSON[name]+' ausdrücklich?',
                               {'Fakt':'Wo steht, was im Körper geschieht?', 'Wert':'Steht dort auch ausdrücklich, was ihr wichtig ist?',
                                'Norm':'Nennt der Vater auch eine Regel für andere Menschen?'}[missing],
                               '„Nicht ausdrücklich genannt ist …“',finish]
            else:
                quote='„'+quellen[name]['Norm' if name=='Großmutter' else 'Folgerung'][-1]+'“'
                task['hints']=['Nachricht · '+name+': '+quote,task['prompt'],
                    'Was will die Großmutter schützen?' if name=='Großmutter' else 'Was soll man vor einer wichtigen medizinischen Entscheidung tun?',
                    '„Mir ist … wichtig.“' if name=='Großmutter' else '„Vor einer Entscheidung sollte man …“',c['addition']]
            task['helpByLevel']={level:list(task['hints']) for level in bank['levels']}
            for level in ('MSA','AHR'):
                if key in quellen[name]:
                    task['helpByLevel'][level][2]={'Wert':'Was ist wichtig? Welcher Satz zeigt den Unterschied zum Rat?',
                        'Norm':'Gilt die Regel nur für Laura? Welche Wörter zeigen, für wen sie gilt?',
                        'Folgerung':'Woran erkennst du, dass der Rat an Laura gerichtet ist?'}[key]
            if (name,key) in RUECKMELDUNGEN:
                for a in task['answers']:
                    if not a['ok']:a['feedback']=RUECKMELDUNGEN[name,key]
        if name in TRANSFER:c['transfer']['advancedPrompt']=TRANSFER[name]
    bank['evaluationHints']=GEWICHT.copy()
    bank['evaluationHelpByLevel']={level:GEWICHT.copy() for level in bank['levels']}
    bank['review'][4][1]='Das beschreibt spätere Schwangerschaften. Laura fragt gerade nach Blutungen und Schmerzen beim Abbruch.'
    bank['review'][5][1]='Das beschreibt Blutungen und Krämpfe. Laura fragt gerade, ob sie später schwanger werden kann.'
    bank['review'][6][1]='Laura kann später schwanger werden. Ein späteres Kind kann ihr niemand versprechen.'
    bank['review'][7][1]='Mögliche Schmerzen und spätere Fruchtbarkeit legen nicht fest, ob Laura die Schwangerschaft fortsetzt. Das entscheidet Laura.'
    return bank

