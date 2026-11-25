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
    bank['ui']['reference']='Musterkarten bei Zeitnot oder Ausfall'
    for lesson in bank['levels'].values():
        intro=lesson['intro']
        frage(intro['question'],'die Erklärung zum Pearl-Index',IMPULSE['PI'])
        for c in lesson['chapters']:
            code=c['id']
            method=c['title'].split(' – ')[-1].split(':')[0]
            fields=c['cardEntries']
            nums=' und '.join(str(e['number']) for e in fields)
            c['paperPrompt']=f'Infokarte „{method}“: Trage die Wörter unten in die Felder {nums} ein.'
            c['backToChat']='Tippe auf „Vollständige Karte vergleichen“.' if code.endswith('B') else ('Beantworte jetzt die Frage auf dem Laufzettel.' if c.get('paperCheck') else 'Tippe auf „Weiter im Chat“.')
            for i,q in enumerate(c['questions']):
                titles=[section['title'] for section in c['information'] if section['sectionId'] in q['informationSections']]
                assert titles,(code,q['id'])
                frage(q,'unter „'+'“ und „'.join(titles)+'“',IMPULSE[code][i])
                for option in q['options']:
                    if not option['correct']:
                        option['feedback']=feedback[option['id']]
                        applied.add(option['id'])
            if c.get('paperCheck'):
                q=c['paperCheck']
                q['screen']=f'Laufzettel „{code}“: Kreise A, B oder C ein. Schreibe unter die Aussagen in wenigen Stichworten, warum die gewählte Aussage stimmt.'
                q['return']='Gib den Buchstaben am iPad ein. Tippe auf „Code prüfen“. Nach der richtigen Auswahl kannst du „Nachricht senden“ antippen.'
                frage(q,'unter „'+c['information'][0]['title']+'“',IMPULSE[code][0])
    assert applied==feedback.keys()
