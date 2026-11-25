"""Bildschirmtexte der Vorbereitung. Das mitgelieferte Druck- und Kartenmaterial bleibt die Referenz."""
import json
from pathlib import Path


# Vier Denkanstöße je Themenpaar. Die fünfte Hilfe enthält weiterhin die geprüfte
# Lösung der konkreten Niveaufrage und schaltet deren zusätzliche Anwendung frei.
IMPULSE = {
    'PI': ('Was wird beim Pearl-Index gezählt?', 'Vergleiche zwei Zahlen. Bei welcher gab es weniger Schwangerschaften?', 'Achte darauf, über welchen Zeitraum die Angaben gelten.'),
    '1A': [('Was verrät die Packung über das Material?', 'Vergleiche die beiden Hüllen im Bild.', 'Welche Angabe brauchst du zusätzlich, um die Eignung zur Verhütung zu beurteilen?'),
           ('Welchen Weg müssten Spermien zur Eizelle nehmen?', 'Verfolge den Weg bis zur Hülle.', 'Was würde ein Riss in der Hülle ändern?')],
    '1B': [('Welche Hautstellen zeigt das Bild?', 'Vergleiche bedeckte und freie Haut.', 'Kann die Hülle an beiden Stellen gleich gut schützen?'),
           ('Wann beginnt der Kontakt der Körper?', 'Überlege, wann eine Hülle wirken kann.', 'Welchen Unterschied machen Sitz und Zeitpunkt der Anwendung?')],
    '2A': [('Suche Eierstock und Eizelle im Bild.', 'Vergleiche die beiden Wege der Eizelle.', 'Was müsste geschehen, bevor ein Spermium eine Eizelle befruchten kann?'),
           ('Wo im Körper wirken die Hormone?', 'Was müsste eine Methode beim Sex tun, um Erreger zurückzuhalten?', 'Vergleiche den Wirkungsort der Pille mit dem einer Kondomhülle.')],
    '2B': [('Vergleiche die beiden Einnahmepläne im Bild.', 'An welcher Stelle unterscheiden sich die Pläne?', 'Was könnte eine Lücke im Plan für den Schutz bedeuten?'),
           ('Wer hat die beschriebene Erfahrung gemacht?', 'Welche Veränderungen sind möglich?', 'Was weißt du damit über eine andere Person?')],
    '3A': [('Welche Zellen zeigt das Bild?', 'Verfolge ihren Weg zur Eizelle.', 'Wie hängt dieser Weg mit einer möglichen Befruchtung zusammen?'),
           ('Welche Wirkung auf Spermien beschreibt die Karte?', 'Vergleiche Spermien mit den Erregern einer Infektion.', 'Welche zusätzliche Information bräuchtest du für eine Aussage über STI?')],
    '3B': [('Vergleiche den Tag des Einsetzens mit den Tagen danach.', 'Wer setzt die Spirale ein?', 'Was muss die Person vor dem Einsetzen entscheiden?'),
           ('Welche Veränderungen beschreibt die Karte?', 'Welche Wörter beschreiben eine Möglichkeit?', 'Was muss bei starken Schmerzen geklärt werden?')],
    '4A': [('Suche den Gebärmutterhals im Bild.', 'Welchen Weg nehmen die Spermien durch den Schleim?', 'Was würde auf diesem Weg ein zäherer Schleim ändern?'),
           ('Welche Zellen zeigt das Bild im Schleim?', 'Was müsste untersucht werden, um etwas über Infektionen zu erfahren?', 'Was lässt sich allein am Weg der Spermien erkennen?')],
    '4B': [('Suche im Bild den Ort der Hormonabgabe.', 'Vergleiche die Hormonabgabe mit der Einnahme einer Tablette.', 'Welche Vorbereitung braucht die Anwendung der Spirale?'),
           ('Welche Veränderungen der Blutung beschreibt die Karte?', 'Welche davon können auftreten?', 'Was ist vor einer persönlichen Entscheidung noch zu klären?')]
}

def frage(q, titel, impulse):
    text='Tippe auf „Informationen nachlesen“. Lies '+titel+'.'
    q['hintsBeforeChoice'][:4]=[text,*impulse]
    for opt in q['options']:
        if 'hints' in opt:
            opt['hints'][:4]=[text,impulse[0],impulse[1],impulse[2]]
            # Dieser Weg erscheint erst nach der Prüfung genau dieser Aussage.
            if not opt['correct']:
                opt['hints'][1]='Du hast „'+opt['text'].strip('„“')+'“ gewählt. '+impulse[0]
    for task in [q,q['afterSolutionCheck']]:
        right=next(o for o in task['options'] if o['correct'])
        for opt in task['options']:
            if opt['correct']:continue
            feedback=opt['feedback']
            if feedback.startswith(('Du ','Das Schutzziel ist falsch','Das folgt nicht aus dem Mechanismus','Die Aussage ist nicht','Das ist fachlich')):
                opt['feedback']=right['feedback'].removeprefix('Die markierte biologische Aussage passt. ')
            elif feedback.startswith('Diese Aussage ist durch die Wirkweise gedeckt.'):
                opt['feedback']='Die Hormone der Kombinationspille hemmen vor allem den Eisprung. Gesucht ist eine Aussage, die der Wirkweise widerspricht.'

def redigieren(bank):
    feedback=json.loads(Path(__file__).with_name('rueckmeldungen.json').read_text())
    applied=set()
    def erkläre_fehler(q):
        for option in q['options']:
            if option['correct']:
                continue
            key=option['id'] if 'id' in option else q['id']+'-'+option['code']
            option['feedback']=feedback[key]
            applied.add(key)
    bank['ui']['reference']='Musterkarten bei Zeitnot oder Ausfall'
    for lesson in bank['levels'].values():
        intro=lesson['intro']
        frage(intro['question'],'die Erklärung zum Pearl-Index',IMPULSE['PI'])
        erkläre_fehler(intro['question'])
        for c in lesson['chapters']:
            code=c['id']
            method=c['title'].split(' – ')[-1].split(':')[0]
            fields=c['cardEntries']
            nums=' und '.join(str(e['number']) for e in fields)
            c['paperPrompt']=f'Infokarte „{method}“: Trage die Wörter unten in die Felder {nums} ein.'
            c['backToChat']='Tippe auf „Vollständige Karte vergleichen“.' if code.endswith('B') else ('Beantworte jetzt die Frage auf dem Laufzettel.' if c.get('paperCheck') else 'Tippe auf „Weiter im Chat“.')
            for i,q in enumerate(c['questions']):
                if q['id'] in ('3A-Q2-MSA','3A-Q2-AHR'):
                    application=q['afterSolutionCheck']
                    application['prompt']='Die Untersuchung zeigt, dass Kupfer die Beweglichkeit von Spermien vermindert. Welche Schutzwirkung wurde dabei nicht untersucht?'
                titles=[section['title'] for section in c['information'] if section['sectionId'] in q['informationSections']]
                assert titles,(code,q['id'])
                frage(q,'unter „'+'“ und „'.join(titles)+'“',IMPULSE[code][i])
                if q['id'] in ('3A-Q2-ESA','4B-Q2-ESA'):
                    right=next(o for o in q['options'] if o['correct'])
                    text={'3A-Q2-ESA':'Wenn Spermien eine Eizelle schlechter befruchten können, schützt das nicht vor Krankheitserregern.',
                          '4B-Q2-ESA':'Auch wenn Schmerzen schwächer werden können, sollte eine Ärztin oder ein Arzt die Ursache starker, ungeklärter Schmerzen untersuchen.'}[q['id']]
                    old=q['solutionExplanation']
                    right['feedback']=q['solutionExplanation']=text
                    for hints in [q['hintsBeforeChoice'],*(o['hints'] for o in q['options'] if 'hints' in o)]:
                        hints[4]=hints[4].replace(old,text)
                if q['id']=='2A-Q2-AHR':
                    for hints in [q['hintsBeforeChoice'],*(o['hints'] for o in q['options'] if 'hints' in o)]:
                        hints[4]=hints[4].replace('Passende Aussage:', 'Diese Behauptung kannst du widerlegen:')
                erkläre_fehler(q)
            if c.get('paperCheck'):
                q=c['paperCheck']
                q['screen']=f'Laufzettel „{code}“: Kreise A, B oder C ein. Schreibe unter die Aussagen in wenigen Stichworten, warum die gewählte Aussage stimmt.'
                q['return']='Gib den Buchstaben am iPad ein. Tippe auf „Code prüfen“. Nach der richtigen Auswahl kannst du „Nachricht senden“ antippen.'
                frage(q,'unter „'+c['information'][0]['title']+'“',IMPULSE[code][0])
                erkläre_fehler(q)
    assert applied==feedback.keys()
    # Die Druckvorlage ist verbindlich. Diese Bearbeitung betrifft nur die
    # Lesetexte und die digitalen Aufgaben, nie die Karten oder ihre Einträge.
    for lesson in bank['levels'].values():
        klartext(lesson['intro'])
        for chapter in lesson['chapters']:
            for key in ('questions','paperCheck','observationPrompt','information'):
                if chapter.get(key):
                    chapter[key]=klartext(chapter[key])
            number=int(chapter['id'][0])
            chapter['paperPrompt']=f'Kartenblatt · Seite {1 if number<=2 else 2} · '+chapter['paperPrompt']
            if chapter.get('paperCheck'):
                q=chapter['paperCheck']
                q['screen']=f'Laufzettel · Seite {3 if number<=2 else 4} · '+q['screen'].replace('unter die Aussagen','in das Feld „Begründung“')


KLARTEXT={
    'Welche Zahl spricht unter vergleichbaren Bedingungen für weniger Schwangerschaften trotz Verhütung?':
        'Zwei Gruppen verhüten gleich lange. Beide wenden ihre Methode wie vorgesehen an. Welcher Pearl-Index bedeutet weniger Schwangerschaften?',
    'Unter vergleichbaren Bedingungen steht der kleinere Wert für einen zuverlässigeren Schwangerschaftsschutz.':
        'Wenn die Methoden ähnlich angewendet und untersucht wurden, spricht der kleinere Wert für weniger Schwangerschaften.',
    'unter vergleichbaren Bedingungen':'bei ähnlicher Anwendung und Untersuchung',
    'Vergleiche den hauptsächlichen Wirkmechanismus mit dem der Pille und die Modellgrenze.':
        'Vergleiche die Wirkung der Hormonspirale mit der Wirkung der Pille. Welche Wirkung zeigt das Bild? Welche zeigt es nicht?',
    'Die Richtung ist vertauscht. Vergleiche die kleinere mit der größeren Zahl.':'Beim Pearl-Index zählen Schwangerschaften trotz Verhütung. Wo wurden weniger gezählt?',
    'Das ist keine Kondomwirkung. Lies die Stelle zum Infektionsschutz.':'Das Kondom bedeckt einen Teil der Haut. Über welche Hautstellen können Erreger trotzdem übertragen werden?',
    'Der Sitz ist verändert. Denke an die Voraussetzung für die Barriere.':'Wenn das Kondom abrutscht, kann Sperma an der Hülle vorbeigelangen.',
    'Die regelmäßige Einnahme schafft keine Erregerbarriere.':'Auch bei regelmäßiger Einnahme hält die Pille Krankheitserreger beim Sex nicht zurück.',
    'Die Pille wirkt auf den Zyklus und bildet keine Erregerbarriere.':'Die Pille wirkt auf den Zyklus. Sie hält Krankheitserreger beim Sex nicht zurück.',
    'Die Kupferwirkung betrifft Spermien und beweist keine Erregerbarriere.':'Kupfer wirkt auf Spermien. Das sagt nichts darüber aus, ob Krankheitserreger übertragen werden.',
    'Hemmung des Eisprungs verhindert eine Befruchtung; keine Erregerbarriere.':'Ohne Eisprung wird keine Eizelle frei. Krankheitserreger können beim Sex trotzdem übertragen werden.',
    'Es wird keine Eizelle zur Befruchtung freigesetzt; eine Erregerbarriere entsteht nicht.':'Es wird keine Eizelle frei. Krankheitserreger können trotzdem übertragen werden.',
    'Keine STI-Risikominderung durch die Pille; eine Erregerbarriere fehlt.':'Die Pille schützt nicht vor Infektionen beim Sex. Sie hält keine Krankheitserreger zurück.',
    'Kupfer wirkt auf Spermien; es gibt keine Erregerbarriere beim Sex.':'Kupfer wirkt auf Spermien. Die Kupferspirale hält beim Sex keine Krankheitserreger zurück.',
    'Ein hoher Schwangerschaftsschutz beweist eine Erregerbarriere.':'Ein hoher Schutz vor Schwangerschaft beweist, dass die Methode auch Krankheitserreger zurückhält.',
    'Spermienwirkung ist keine Erregerbarriere':'Eine Wirkung auf Spermien schützt nicht vor Krankheitserregern',
    'Erregerübertragung ist ein anderer Vorgang. Trenne die beiden Ziele.':'Eine Befruchtung braucht Spermien. Eine Infektion entsteht durch Krankheitserreger. Worauf wirkt Kupfer?',
    'Ungeklärte starke Schmerzen sollten nicht ignoriert werden. Lies den Hinweis am Kartenende.':'Bei starken Schmerzen ohne bekannte Ursache sollte eine Ärztin oder ein Arzt die Ursache klären.',
    'Diese möglichen Veränderungen sind individuell.':'Bei manchen Menschen wird die Blutung schwächer. Sie verändert sich nicht bei allen gleich.',
    'Das ist keine tägliche Anwendung. Schau auf das Bild der liegenden Spirale.':'Die Kupferspirale liegt in der Gebärmutter. Wer darf sie dort einsetzen?',
    'Die Spirale ist keine tägliche äußerliche Methode. Sieh dir das Modell an.':'Suche auf dem Bild die Gebärmutter. Wo liegt die Spirale?',
    'Eine mögliche Linderung ist keine Garantie.':'Schmerzen können nachlassen. Das passiert nicht bei jeder Person.',
    'Spermienwirkung und Infektionsschutz sind verschieden.':'Der Schleim erschwert Spermien den Weg. Beim Sex können trotzdem Krankheitserreger übertragen werden.'
}

def klartext(value):
    if isinstance(value,dict):
        for key,text in value.items():
            value[key]=klartext(text)
    elif isinstance(value,list):
        return [klartext(text) for text in value]
    elif isinstance(value,str):
        for old,new in KLARTEXT.items():
            value=value.replace(old,new)
    return value
