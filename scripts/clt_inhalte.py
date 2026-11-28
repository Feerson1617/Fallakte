"""Digitale Aufgaben aus den bestehenden fachlichen Entscheidungen und Karten ableiten."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
METHODS=('K','P','Cu','H')
STEPS={
'L01':'Wie verändert die Latexallergie deinen Rat?',
'L02':'Wie schützt dein Vorschlag vor Schwangerschaft und vor Ansteckung beim Sex?',
'L03':'Was bedeutet Lauras unregelmäßiger Alltag für deinen Rat?',
'L04':'Wie passen Regelschmerzen und Lauras Sorge vor dem Einsetzen zu deinem Rat?',
'L05':'Welches Anliegen ist für deinen Rat besonders wichtig? Warum?'}

def klar(text):
    paare=(
       ('Anwendung und individuelle Verträglichkeit sind getrennte Fragen.', 'Kann Laura die Pille nach Plan nehmen? Wie ihr Körper darauf reagiert, ist eine andere Frage.'),
       ('Auch hormonfrei ist Verhütung möglich. Ein geeignetes synthetisches Kondom besteht nicht aus Latex.',
        'Eine Möglichkeit ohne Hormone ist ein Kondom aus Kunststoff ohne Latex.'),
       ('Naturmembranprodukte sind zur STI-Risikominderung nicht gleichwertig. Prüfe, ob das synthetische latexfreie Kondom dafür geeignet ist.',
        'Kondome aus Naturmembran bieten diesen Infektionsschutz nicht. Bei Kondomen aus Kunststoff: Achte auf den Hinweis zum Infektionsschutz auf der Packung.'),
       ('Für STI-Risikominderung kommt ein dafür geeignetes synthetisches latexfreies Kondom infrage. Naturmembranen sind nicht gleichwertig.',
        'Ein dafür geeignetes Kondom aus Kunststoff ohne Latex senkt das Risiko einer Ansteckung. Kondome aus Naturmembran bieten diesen Schutz nicht.'),
       ('Geeignetes synthetisches latexfreies Kondom richtig benutzen. Ob die Pille zusätzlich passt, hängt auch von Eignung, Einnahme und Lauras Entscheidung ab.',
        'Das Kondom aus Kunststoff ohne Latex richtig benutzen. Möchte Laura zusätzlich die Pille? Passt die Pille zu ihrer Gesundheit? Kann Laura sie nach Plan nehmen?'),
       ('Geeignete synthetische latexfreie Kondome sind selbst Barrieren. Die Pille hat eine andere Wirkung.',
        'Kondome aus Kunststoff ohne Latex halten Spermien zurück. Die Pille wirkt anders.'),
       ('Ein geeignetes synthetisches latexfreies Kondom hält Spermien zurück und senkt bei richtiger Anwendung das Risiko vieler STI. Ein Risiko bleibt.',
        'Ein passendes Kondom aus Kunststoff ohne Latex hält Spermien zurück. Richtig benutzt senkt es das Risiko vieler Infektionen beim Sex. Ein Risiko bleibt.'),
       ('geeignetes synthetisches latexfreies Kondom','passendes Kondom aus Kunststoff ohne Latex'),
       ('geeignete synthetische latexfreie Kondome','passende Kondome aus Kunststoff ohne Latex'),
       ('Das geeignete synthetische Kondom','Das Kondom aus Kunststoff ohne Latex'),
       ('Das synthetische Kondom','Das Kondom aus Kunststoff ohne Latex'),
       ('Synthetisches Kondom ohne Latex ergänzen','Kondom aus Kunststoff ohne Latex ergänzen'),
       ('Persönliche Fragen zu Hormonen und medizinische Eignung klären.', 'Laura kann in der Arztpraxis fragen: Passt die Pille zu mir?'),
       ('Regelmäßige Einnahme nach Plan nötig.', 'Die Pille muss sie nach Plan nehmen.'),
       ('Lauras wechselnden Alltag berücksichtigen.', 'Lauras Alltag wechselt.'),
       ('Die Erfahrung der Freundin sagt ihre Verträglichkeit nicht voraus.', 'Ihre Freundin hatte Beschwerden. Bei Laura kann es anders sein.'),
       ('Die starken ungeklärten Schmerzen sollten ärztlich abgeklärt werden.', 'Die Arztpraxis sollte prüfen, warum Laura starke Schmerzen hat.'),
       ('geeignetes synthetisches Kondom ohne Latex','latexfreies Kondom aus Kunststoff'),
       ('geeignetes synthetisches Kondom','Kondom aus Kunststoff ohne Latex'),
       ('Geeignete synthetische latexfreie Kondome bilden eine Barriere für Spermien.', 'Latexfreie Kondome aus Kunststoff halten Spermien zurück.'),
       ('geeignete synthetische Kondome','Kondome aus Kunststoff'))
    for alt,neu in paare:text=text.replace(alt,neu)
    return text

def einfache_sprache(ctx):
    for k in ('feedback','condition','evidence'):
        if k in ctx:ctx[k]=klar(ctx[k])
    ctx['hints']=list(map(klar,ctx['hints']))
    if ctx.get('correction',{}).get('label'):ctx['correction']['label']=klar(ctx['correction']['label'])
    for op in ctx.get('options',[]):
        for k in ('feedback','text'):op[k]=klar(op[k])

def karten(bank):
    work=json.loads((ROOT/'clt/Infokarten.json').read_text())
    for i,key in enumerate(METHODS):
        for section in bank['cards'][key]['sections'].values():
            lookup={t:next(p['volltext'] for p in cs[i]['texte'] if p['titel']==section['title']) for t,cs in work.items()}
            section.update(levels=lookup,shortText=lookup['Foerder'],text=lookup['AHR'])

def laura(bank):
    karten(bank)
    bank["kartenbilder"]=json.loads((ROOT/"clt/Kartenbilder.json").read_text())
    # Die Schlussübersicht enthält Lauras Anliegen. Methodeneigenschaften stehen auf den Infokarten.
    bank['concernsShort']={
        'ausgang':'Laura ist 19. Sie möchte sicheren Schutz vor einer Schwangerschaft.',
        'latex':'Laura verträgt kein Latex.',
        'hormonfrage':'Laura weiß wenig über Hormone. Sie ist unsicher.',
        'sti':'Sie möchte sich beim Sex auch vor Infektionen schützen.',
        'routine':'Ihr Alltag wechselt. Tägliche Dinge vergisst sie manchmal.',
        'freundin':'Eine Freundin hatte Probleme mit der Pille. Laura weiß nicht, wie sie selbst die Pille verträgt.',
        'schmerzen':'Laura hat starke Regelschmerzen. Die Ursache ist noch nicht ärztlich geklärt.',
        'einlage':'Das Einsetzen einer Spirale macht ihr Sorgen. Sie hat sich noch nicht entschieden.'}
    for stage in bank['stages'].values():
        if stage['id']=='L05':stage['evidence']='Welche Wünsche und Sorgen von Laura sind für deinen Rat wichtig?'
        for tier,task in stage['levels'].items():
            advanced=tier in ('MSA','AHR')
            for name in ('paperPrompt','returnPrompt','paperFallback','paperFieldId'):task.pop(name,None)
            task['task']=STEPS[stage['id']] if advanced or stage['id']=='L05' else task['task']
            if stage['id']=='L05':task['evidence']='Denke an Lauras Wünsche und Sorgen.'
            for ctx in [task['before'],*task['strategies'].values()]:
                card=bank['cards'][ctx['card']['method']]
                title=card['sections'][ctx['card']['section']]['title']
                ctx['hints'][0]=STEPS[stage['id']]+' ('+card['title']+' · '+title+')'
                ctx['hints']=[line.split(' Laufzettel')[0] for line in ctx['hints']]
            if advanced:
                for way in task['strategies'].values():
                    way['options']=[dict(id='aussage-'+str(i+1),text=text,correct=key==stage['code'],feedback=stage['anchorFeedback'][key]['text'],card=stage['anchorFeedback'][key]['card']) for i,(key,text) in enumerate(stage['anchors'].items())]
            for ctx in [task['before'],*task['strategies'].values()]:einfache_sprache(ctx)
        for k in ('anchors','code','anchorFeedback'):stage.pop(k)
    for k in ('normalization','paperFallbackInstruction'):bank.pop(k,None)
    return bank

def familie(bank):
    # Nur Schlüssel mit einem Schüler-Einstieg gelangen ins digitale Modul.
    app=(ROOT/'module/familienrat/app.js').read_text()
    import re
    ui={k:bank['ui'][k] for k in sorted(set(re.findall(r'\bui\.(\w+)',app)))}
    ui['soloReplace']='Das Gespräch beginnt neu. Deine erste und deine abschließende Antwort bleiben auf diesem Gerät, bis du die Seite schließt.'
    keys=('levels','opening','second','cards','cases','limits','evaluationHints','review','levelPrompts','caseReflection','evaluationHelpByLevel','crossReference','designFiles','commit')
    selected={k:bank[k] for k in keys}
    selected.update(ui=ui,definitions={'Fakt':'Welche Aussage kann man prüfen?','Wert':'Was ist jemandem wichtig?','Norm':'Was sollte man tun?','Folgerung':'Welcher Rat folgt daraus?'},known='Lies die Nachricht.')
    selected['crossReference']=['Die Information über Beschwerden steht bei der Mutter. Wie hilft sie dir beim Rat der Freundin?', 'Die Information über spätere Schwangerschaften steht bei der Freundin. Wie hilft sie dir beim Rat der Mutter?']
    selected['evaluationSteps']=['Lauras Frage','Anliegen vergleichen','Nachrichten abwägen','Stundenabschluss']
    selected['evaluationRecovery']=[dict(id='LA-0'+str(i+1),section=t) for i,t in enumerate(selected['evaluationSteps'])]
    for name,c in selected['cases'].items():
        # Eine einzige Quelle für Chat, Quellenwahl und die erste Einschätzung.
        text=c['lesefassung']
        if name in NACHRICHTEN:text=' '.join(NACHRICHTEN[name])
        c['original']=c['lesefassung']=text
        c.pop('field',None);c['recovery'][-1].update(section=name+' · Weiter',part='Weiter')
    # Gegen die sichtbaren Satztexte auflösen, nicht gegen Indizes der früheren Originalnachricht.
    import re
    for name,parts in QUELLEN.items():
        c=selected['cases'][name]
        lines=[line.strip() for line in re.findall(r'[^.!?]+[.!?]+|[^.!?]+$',c['original'])]
        for t in c['tasks']:
            if 'evidenceSentences' in t:t['evidenceSentences']=[lines.index(line) for line in parts[t['id']]]
    def hinweis(text):
        return text.replace('Öffne „Fakt · Wert · Norm · Folgerung“. Lies die vier Fragen.',
                            'Tippe auf „Begriff erklären“. Wähle ein Wort.')
    for c in selected['cases'].values():
        for t in c['tasks']:
            t['hints']=list(map(hinweis,t['hints']))
            for k,h in t.get('helpByLevel',{}).items():t['helpByLevel'][k]=list(map(hinweis,h))
    for name in NACHRICHTEN:
        c=selected['cases'][name]
        who='Mama' if name=='Mutter' else 'deiner Freundin'
        for task in c['tasks']:
            key=task['id']
            if key=='Leerstelle':
                task['prompt']='Welche biologische Information fehlt als Grund für diesen Rat?'
                for a in task['answers']:
                    if a['ok']:a['feedback']='Ja. Für diesen Rat fehlt noch eine biologische Information.'
            if key in QUELLEN[name]:
                source=QUELLEN[name][key][-1]
                prompts={'Wert':'Was ist '+who+' wichtig?', 'Norm':'Welche Regel nennt '+('Mama' if name=='Mutter' else 'deine Freundin')+'?',
                         'Folgerung':'Was rät '+('Mama' if name=='Mutter' else 'deine Freundin')+' Laura?'}
                task['prompt']=prompts[key]
                hints={'Wert':['Welches Anliegen hörst du heraus?', 'Worüber macht sich Mama Sorgen?' if name=='Mutter' else 'Was hat Laura für später vor?', 'Achte auf „Gesundheit“.' if name=='Mutter' else 'Achte auf „Zukunft“.'],
                       'Norm':['Suche eine Regel, die auch für andere gilt.', 'Was sollte man aus Sicht der Person tun?', 'Achte auf „man sollte“.'],
                       'Folgerung':['Suche den persönlichen Rat.', 'Wozu rät sie Laura?', 'Achte auf „ich würde dir raten“.' if name=='Mutter' else 'Achte auf „raten“.']}[key]
                task['hints']=[*hints, 'Lies diesen Satz: „'+source+'“', 'Vergleiche: '+next(a['text'] for a in task['answers'] if a['ok'])]
                task['helpByLevel']={t:list(task['hints']) for t in bank['levels']}
    return selected


QUELLEN={
    'Mutter':{'Wert':['Ich mache mir Sorgen um deine Gesundheit.'],
              'Norm':['Ich finde, man sollte gut auf seinen Körper achten und Beschwerden ernst nehmen.'],
              'Folgerung':['Ganz ehrlich, ich würde dir raten, das Kind zu bekommen.']},
    'Freundin':{'Wert':['Du wolltest doch erst deine Ausbildung fertig machen.', 'Mir ist wichtig, dass du deine Zukunft selbst planen kannst.'],
                'Norm':['Ich finde, man sollte Kinder bekommen, wenn man selbst bereit dafür ist.'],
                'Folgerung':['Ganz ehrlich, ich würde dir zu einem Abbruch mit Medikamenten raten.']},
    'Großmutter':{'Norm':['Ich finde, man sollte ungeborenes menschliches Leben schützen.'],
                  'Folgerung':['Deshalb rate ich dir, die Schwangerschaft fortzusetzen.']},
    'Vater':{'Wert':['Laura, mir ist wichtig, dass du gut informiert selbst entscheidest.'],
             'Folgerung':['Deshalb rate ich dir, in der Arztpraxis nach deinen Möglichkeiten zu fragen.']}
}

NACHRICHTEN={
    'Mutter':['Hey mein Schatz ❤️!', *QUELLEN['Mutter']['Wert'], *QUELLEN['Mutter']['Norm'], *QUELLEN['Mutter']['Folgerung'], 'Ich bin für dich da.'],
    'Freundin':['Hey du ❤️!', QUELLEN['Freundin']['Wert'][0], 'Vielleicht möchtest du später Kinder.', QUELLEN['Freundin']['Wert'][1], *QUELLEN['Freundin']['Norm'], *QUELLEN['Freundin']['Folgerung'], 'Frag doch mal in der Arztpraxis nach.', 'Wenn du magst, komme ich mit.']
}
