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
                ctx['hints'][0]='Lies auf deiner Infokarte „'+card['title']+'“ unter „'+title+'“.'
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
    keys=('levels','opening','second','cards','cases','limits','evaluationHints','review','levelPrompts','caseReflection','evaluationHelpByLevel','crossReference','designFiles','commit')
    selected={k:bank[k] for k in keys}
    selected.update(ui=ui,definitions={'Fakt':'Was kann man prüfen?','Wert':'Was ist jemandem wichtig?','Norm':'Was sollte man tun?','Folgerung':'Welcher Rat folgt daraus?'},known='Lies die Nachricht.')
    selected['crossReference']=['Die Information über Beschwerden steht bei der Mutter. Wie hilft sie dir beim Rat der Freundin?', 'Die Information über spätere Schwangerschaften steht bei der Freundin. Wie hilft sie dir beim Rat der Mutter?']
    selected['evaluationSteps']=['Lauras Frage','Anliegen vergleichen','Nachrichten abwägen','Stundenabschluss']
    selected['evaluationRecovery']=[dict(id='LA-0'+str(i+1),section=t) for i,t in enumerate(selected['evaluationSteps'])]
    for name,c in selected['cases'].items():
        c.pop('field',None);c['recovery'][-1].update(section=name+' · Weiter',part='Weiter')
    return selected
