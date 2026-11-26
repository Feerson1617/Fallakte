"""Compile paper handoffs against the real recovery sections of the December 8 module."""

def compile_media(bank):
    actions=bank['mediaActions']
    levels=bank['levels']
    cases=bank['cases']
    laura=bank['evaluationRecovery']
    fields={}
    steps={}
    def add(key,source,target,field,kind,by_level,help_text,when,after='',support=''):
        orders={}
        for level in levels:
            action=by_level[level]
            prefix=key.split('-')[0]
            page=2 if prefix=='LA' else 1
            sheet='Vertiefungsbogen' if prefix in ('GM','VA') else 'Pflichtlernbogen'
            if prefix!='LA':
                topic={'MU':'mögliche Blutungen und Schmerzen beim Abbruch mit Medikamenten',
                       'FR':'eine spätere Schwangerschaft nach einem Abbruch ohne Komplikationen',
                       'GM':'das, was der Großmutter wichtig ist',
                       'VA':'die allgemeine Regel, an der sich der Vater orientiert'}[prefix]
                first=key.endswith('-erst')
                question={'MU':'Welche Beschwerden sind beim Abbruch mit Medikamenten möglich?',
                          'FR':'Kann eine Frau nach einem Abbruch ohne Komplikationen später schwanger werden?',
                          'GM':'Was ist der Großmutter wichtig?', 'VA':'Welche Regel meint der Vater?'}[prefix]
                if level in ('Förder','ESA'):
                    action=(question+' '+
                            ('Kreuze links an: „Meine erste Antwort“.' if first else
                             'Kreuze rechts an: „Nach dem Prüfen“. Dein erstes Kreuz bleibt.'))
                    if not first:
                        action+=' '+{'MU':'Was weißt du über die Beschwerden? Wer entscheidet?',
                                    'FR':'Was weißt du über spätere Kinder? Wer entscheidet?',
                                    'GM':'Wie hängt dieser Wert mit dem Rat der Großmutter zusammen?',
                                    'VA':'Wie wendet der Vater diese Regel auf Lauras Situation an?'}[prefix]
                elif prefix in ('GM','VA'):
                    focus='den Wert der Großmutter' if prefix=='GM' else 'die allgemeine Regel des Vaters'
                    if first:
                        action=question+' Schreibe '+focus+' in „Meine erste Antwort“.'
                    else:
                        action=('Schreibe '+focus+' in „Nach dem Prüfen“. Lass deine erste Antwort stehen. '+
                                ('Wie passt diese Aussage zum Rat in der Nachricht?' if level=='MSA' else
                                 'Was erklärt diese Aussage über den Rat? Was entscheidet Laura selbst?'))
                else:
                    action=('Schreibe in „Meine erste Antwort“, welche Aussage über '+topic+' deiner Meinung nach fehlt.' if first else
                            'Schreibe in „Nach dem Prüfen“ die geprüfte Aussage über '+topic+'. Lass deine erste Antwort stehen. '+
                            ('Warum passt die Aussage zu dieser Nachricht?' if level=='MSA' else 'Was erklärt diese Aussage? Was entscheidet Laura selbst?'))
            orders[level]={'action':action,'screen':f'{sheet} · Seite {page} · {field}\n{action}'}
        person=next((name for name,c in cases.items() if target in c['recovery']),bank['ui']['theme'])
        terminal=target is None
        staying=source==target
        destination='Sicherung' if terminal else target['section']
        resume=source if terminal else target
        steps[key]=dict(id=key,sectionId=source['id'],section=source['section'],levels=levels,
                        field=field,kind=kind,orders=orders,condition=when,help=help_text,
                        returnText=(actions['finish'] if terminal else bank['ui']['sameStep'] if staying else 'Öffne „'+destination+'“.'),
                        buttonText=None if terminal or staying else ('Meine Antwort prüfen' if key=='LA-eigen' else 'Weiter im Chat'),
                        nextId=None if terminal else target['id'],mode='Sicherung' if terminal else 'gleicher Abschnitt' if staying else 'Abschnittswechsel',
                        restartId=resume['id'],
                        restart='Nach Neustart → Niveau wählen → '+person+' → '+resume['section'],
                        after=after,support=support)
    for name,c in cases.items():
        first,paper=c['recovery'][-2:]
        prefix=first['id'].split('-')[0]
        initial=c['field']+' / '+actions['firstLabel']
        result=c['field']+' / '+actions['checkedLabel']
        task=c['tasks'][-1]
        options=[a['text'] for a in task['answers']]
        shift=sum(map(ord,task['prompt'])) % len(options)
        alternatives=options[shift:]+options[:shift]
        short=[text for text in alternatives if options.index(text) in task['shortOptions']]
        fields[initial]=dict(group=c['field'],options=alternatives,foerder=short,design='Förder/ESA: Auswahl zum Ankreuzen. MSA/AHR: Raum für eigene Stichworte.')
        fields[result]=dict(group=c['field'],options=alternatives,foerder=short,design='Getrennt vom Erstfeld. Förder/ESA markieren. MSA/AHR erhalten Platz für eine kurze Begründung.',support=actions['supportLabel'])
        add(prefix+'-erst',first,first,initial,'Erstgedanke',actions['first'],
            'Hilfe 1 bis 5 und Fachkarten am Gerät.', 'Vor der ersten digitalen Prüfung der Ergänzung.')
        dest=cases['Freundin']['recovery'][0] if name=='Mutter' else laura[0] if name=='Freundin' else laura[-1]
        def checked(key,target,condition):
            add(key,paper,target,result,'überprüftes Ergebnis',actions['checked'],
                'Nach einer gezeigten Lösung zur Ergänzung zuerst die passende kurze Anwendung im Abschnitt Festhalten. Nach einem Neustart kann sie dort direkt ausgewählt werden.',
                condition,support=actions['displaySupport'])
            steps[key]['restartApplication']=dict(id=c['transfer']['sectionId'],
                label=paper['section']+' · '+bank['ui']['transfer'],
                person=name)
        checked(prefix+'-ergebnis',dest,'Nach der digitalen Ergänzung oder der Anwendung.' if name in ('Mutter','Freundin') else 'Nach abgeschlossener persönlicher Bewertung.')
        if name in ('Großmutter','Vater'):
            checked(prefix+'-einstieg',laura[0],'Direkteinstieg in die Vertiefung bei noch offener persönlicher Bewertung.')
    personal=laura[1]['section']
    fields[personal]=dict(group=personal,design=actions['layout'],parts=[x[0] for x in bank['stems']])
    add('LA-eigen',laura[1],laura[2],personal,'eigene Begründung',
        bank['evaluation'],
        'Fünf Hilfen. Auf Förder zusätzlich die aufklappbaren Satzteile.',
        'Vor der digitalen Prüfung der persönlichen Antwort.')
    add('LA-abschluss',laura[3],None,'Festhalten','eigene Begründung',actions['final'],
        'Die persönlichen Belege und die beiden Ergänzungen lassen sich im selben Abschnitt vergleichen.',
        'Nach der in dieser Sitzung abgeschlossenen persönlichen Prüfung.')
    fields['Festhalten']=dict(group=laura[3]['section'],design='Platz für eine Ergänzung zur weiterhin lesbaren ersten Antwort auf Seite 2.')
    del bank['mediaActions']
    return dict(layout=actions['layout'],digitalOnly=actions['digitalOnly'],fields=fields,steps=steps)


def media_markdown(media,commit):
    lines=['# Medienwechsel und Papierfelder · 08.12.2026','',f'Fertigungsstand `{commit}`',
           '',media['layout'],'',media['digitalOnly'],'','## Papierfelder','']
    for field,details in media['fields'].items():
        lines.extend(['### '+field,'',details['design'],''])
        if 'support' in details:lines.extend(['Kennzeichnung im selben Feld · '+details['support'],''])
        for option in details.get('options',details.get('parts',[])):lines.append('- '+option)
        if 'foerder' in details:lines.extend(['','Förder · zuerst angebotene Auswahl','',*['- '+o for o in details['foerder']]])
        lines.append('')
    for row in media['steps'].values():
        lines.extend(['## '+row['id']+' · '+row['section'],'',row['condition'],'',
                      f"Papierfeld **{row['field']}** · {row['kind']}",''])
        for level,order in row['orders'].items():
            lines.extend(['**'+level+'**','',order['screen'].replace('\n','  \n'),''])
        lines.extend(x for x in [row['support'],row['after']] if x)
        if 'restartApplication' in row:
            resume=row['restartApplication']
            lines.extend(['','Kurze Anwendung nach Neustart → '+resume['person']+' → '+resume['label']+' ('+resume['id']+')'])
        lines.extend(['','**'+row['returnText']+'**',(f"Digitaler Schritt `{row['nextId']}`" if row['nextId'] else 'Abschluss auf Papier mit der Lehrkraft.'),'',row['restart'],'',row['help'],''])
    return '\n'.join(lines)+'\n'
