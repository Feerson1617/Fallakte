"""Authoring source for the second lesson. Export the same resolved bank to HTML and Work."""
import json
from pathlib import Path

SOURCE = json.loads(Path(__file__).with_name('nachrichten.json').read_text())
LEVELS = ['Förder', 'ESA', 'MSA', 'AHR']
QUESTIONS = ['Stimmt das?', 'Was möchte Laura? Geht die Nachricht darauf ein?', 'Hilft die Nachricht Laura? Warum?']
CATEGORIES = {
    'Fakt': 'Was behauptet die Person? Können wir das prüfen?',
    'Wert': 'Was ist der Person wichtig?',
    'Norm': 'Welche Regel nennt die Person?',
    'Folgerung': 'Was soll Laura nach Meinung dieser Person tun?',
}
HELP = ['Was soll ich tun?', 'Was bedeutet die Frage?', 'Wo muss ich schauen?',
        'Wie hängen die Aussagen zusammen?', 'So geht es.']
SOURCES = {
    'BIÖG': 'https://www.familienplanung.de/schwangerschaftskonflikt/schwangerschaftsabbruch/der-medikamentoese-schwangerschaftsabbruch/',
    'IQWiG': 'https://www.gesundheitsinformation.de/medikamentoeser-schwangerschaftsabbruch.html',
    'StGB § 218a Abs. 1': 'https://www.gesetze-im-internet.de/stgb/__218a.html',
    'StGB § 219 Abs. 2': 'https://www.gesetze-im-internet.de/stgb/__219.html',
    'SchKG § 2 Abs. 2': 'https://www.gesetze-im-internet.de/beratungsg/__2.html',
    'SchKG § 5': 'https://www.gesetze-im-internet.de/beratungsg/__5.html',
    'SchKG § 7': 'https://www.gesetze-im-internet.de/beratungsg/__7.html',
    'SchKG § 9': 'https://www.gesetze-im-internet.de/beratungsg/__9.html',
}
CARDS = {
    'medizin': dict(title='Abbruch mit Medikamenten', lines=[
        'Ein Abbruch mit Medikamenten ist grundsätzlich ohne Operation möglich.',
        'Es kommt zu Blutungen. Schmerzen und Krämpfe sind möglich.',
        'Manchmal ist eine weitere Behandlung nötig.',
        'Eine Ärztin oder ein Arzt prüft, ob der Weg für die Person geeignet ist. Lauras Schwangerschaftswoche kennen wir nicht.'
    ], sources=['BIÖG', 'IQWiG']),
    'beratung': dict(title='Beratung und Gesetz', lines=[
        'Für einen Abbruch nach der Beratungsregelung gilt unter anderem: Die Beratung muss bei einer staatlich anerkannten Schwangerschaftskonfliktberatungsstelle stattfinden.',
        'Die Beratung muss mindestens drei Tage vor dem Abbruch liegen.',
        'Die Beratung ist ergebnisoffen. Ein Termin legt Lauras Entscheidung nicht fest.',
        'Laura kann dort nach Hilfe für ihre Ausbildung fragen.'
    ], sources=list(SOURCES)[2:]),
}

# Each check pairs the original line with evidence, one delimited question,
# a supported answer and a concrete route back from the other answer.
def choice(prompt, target, other, yes, no, place, bridge, *, lines=(), wishes=(), card=None, kind='check'):
    return dict(kind=kind, prompt=prompt, lines=list(lines), wishes=list(wishes), card=card,
                options=[dict(label=target, correct=True, feedback=yes),
                         dict(label=other, correct=False, feedback=no)],
                hints=['Lies die Stelle. Wähle eine Antwort.',
                       ('Vergleiche die Wörter auf der Karte mit dem Satz aus der Nachricht.' if card else
                        'Suche die Antwort in den Worten der Person.'), place, bridge,
                       f'Wähle „{target}“. Lies die Rückmeldung. Tippe auf „Weiter“.'])


def category(person, line, target, insight):
    # The four learned terms always occupy their original position.
    q = choice('Welches Feld passt zu dieser Stelle?', target, '', insight, '', f'Lies {person}, Zeile {line}.',
               insight, lines=[line], kind='category')
    q['hints'][1] = 'Achte darauf, was die Person hier tut. Nennt sie etwa eine Regel oder gibt sie einen Rat?'
    q['options'] = [dict(label=k, correct=k == target, feedback=insight if k == target else
                        f'{k}: {v} Lies Zeile {line} noch einmal. {insight}') for k, v in CATEGORIES.items()]
    return q


def medical(line, medline, prompt, target, other, yes, no):
    return choice(prompt, target, other, yes, no,
                  f'Lies die Fachkarte „Abbruch mit Medikamenten“, Zeile {medline}.', yes,
                  lines=[line], card=['medizin', [medline]])


MOTHER = medical(1, 2, 'Was zeigt die Fachkarte?', 'Blutungen treten auf. Schmerzen sind möglich.',
                 'Schmerzen treten immer auf.', 'Die Karte bestätigt die Mutter. Schmerzen sind möglich.',
                 'Lies Zeile 2 der Karte. „Möglich“ heißt: Schmerzen können auftreten.')
FRIEND_OP = medical(2, 1, 'Ist für diesen Weg immer eine Operation nötig?', 'Nein. Es geht grundsätzlich ohne Operation.',
                    'Ja. Eine Operation gehört immer dazu.', 'Die Karte bestätigt Zeile 2 der Freundin.',
                    'Vergleiche Zeile 1 der Karte. Dort steht „grundsätzlich ohne Operation“.')
FRIEND_VIDEO = medical(3, 2, 'Stimmt der Satz aus dem Video?', 'Nein. Es kommt zu Blutungen. Schmerzen sind möglich.',
                       'Ja. Ohne Operation gibt es keine Blutungen.', 'Ohne Operation heißt nicht ohne Blutungen oder Schmerzen.',
                       'Lies Zeile 2 der Karte. Prüfe diesen Satz aus dem Video an der Fachinformation.')
GRAND = choice('Was steht in der Nachricht?', 'Sie nennt ihren Glauben und wünscht sich, dass Laura das Kind bekommt.',
               'Sie erklärt, wie ein Abbruch mit Medikamenten abläuft.',
               'Zeilen 2 und 3 nennen ihren Glauben und ihren Wunsch.', 'Lies Zeilen 2 und 3. Dort steht ihr Wunsch. Ein Ablauf fehlt.',
               'Lies Großmutter, Zeilen 2 und 3.', '„Zu meinem persönlichen Glauben“ zeigt, wessen Regel sie nennt.',
               lines=[2, 3])
FATHER = choice('Was gilt bei der Beratungsregelung?', 'Anerkannte Stelle und mindestens drei Tage Abstand.',
                'Ein Termin an einer beliebigen Stelle reicht.', 'Der Vater nennt zwei Vorgaben. Beide stehen auf der Karte.',
                'Lies Zeilen 1 und 2 der Karte. Die Stelle und der Abstand sind vorgeschrieben.',
                'Lies „Beratung und Gesetz“, Zeilen 1 und 2.', 'Die Stelle braucht eine staatliche Anerkennung. Achte auch auf die Frist.',
                lines=[2], card=['beratung', [1, 2]])

# A short source-based check of both the support and the limit of each message.
WISHES = {
    'Mutter': ([4, 6], [4, 5], 'Sie bietet Hilfe an und fragt Laura. Erklärt sie auch beide Wege?',
               'Sie fragt Laura. Beide Wege erklärt sie noch nicht.', 'Sie erklärt Laura beide Wege.',
               'Ihr Angebot kann helfen. Laura sucht auch einen Überblick über ihre Möglichkeiten.'),
    'Freundin': ([1, 5], [2, 4, 5], 'Was greift die Freundin auf? Was braucht Laura noch?',
                'Die Ausbildung ist ihr wichtig. Laura braucht noch richtige Informationen.',
                'Der Rat zur Ausbildung klärt schon alle Fragen.', 'Sie sieht Lauras Ausbildung. Der falsche Satz hilft Laura beim eigenen Entscheiden nicht.'),
    'Großmutter': ([4, 5], [4, 5], 'Was lässt sie Laura selbst tun?',
                  'Laura darf selbst entscheiden. Die Großmutter bleibt bei ihr.', 'Laura soll den Glauben der Großmutter übernehmen.',
                  'Sie lässt Laura frei und bietet Nähe an. Die Möglichkeiten erklärt sie nicht.'),
    'Vater': ([3, 4, 5], [2, 4, 5], 'Was ermöglicht der Termin?',
              'Laura kann nach Hilfe fragen und selbst entscheiden.', 'Mit dem Termin hat Laura sich schon für den Abbruch entschieden.',
              'Der Vater zeigt einen Weg zu Informationen und Hilfe für die Ausbildung. Die Entscheidung bleibt offen.'),
}
EVIDENCE = {
    'Mutter': ('medizin', 2, 'Welche Kartenstelle stützt die Mutter?', 1, 'Zeile 2 nennt Blutungen und mögliche Schmerzen.'),
    'Freundin': ('medizin', 2, 'Welche Kartenstelle widerspricht dem Video?', 1, 'Zeile 2 nennt Blutungen. Zeile 1 erklärt nur, dass es ohne Operation geht.'),
    'Großmutter': (None, 5, 'Welche Stelle zeigt ihr Angebot?', 3, 'Zeile 5 bietet Nähe an. Zeile 3 nennt ihren Wunsch.'),
    'Vater': ('beratung', 3, 'Welche Kartenstelle lässt die Entscheidung offen?', 2, 'Zeile 3 erklärt: Ein Termin legt nichts fest.'),
}

DEEP = {
    'Mutter': ('Darf die Mutter trotz der offenen Fragen einen Rat geben?', 'Ja. Laura kann zuhören und anders entscheiden.',
               'Nein. Schon ein persönlicher Rat nimmt Laura die Wahl.', 'Sie fragt in Zeile 6 nach Lauras Meinung. Ein Rat ist kein Zwang.', [5, 6]),
    'Freundin': ('Stell dir vor: Die Freundin verbessert den Satz aus dem Video. Steht Lauras Entscheidung dann fest?',
                 'Nein. Richtige Informationen helfen. Laura entscheidet selbst.', 'Ja. Der verbesserte Satz legt den Abbruch nahe.',
                 'Der Fehler lässt sich berichtigen. Was zu Laura passt, folgt daraus noch nicht.', [2, 3, 5]),
    'Großmutter': ('Macht die fehlende Fachinformation ihr Angebot wertlos?', 'Nein. Sie kann Laura trotzdem begleiten.',
                  'Ja. Nur medizinische Aussagen helfen.', 'Nähe und Fachwissen helfen auf verschiedene Weise. Laura kann beides brauchen.', [4, 5]),
    'Vater': ('Die Aussage über das Gesetz ist prüfbar. Kann sie auch eine Regel nennen?', 'Ja. Man kann nachlesen, was vorgeschrieben ist.',
              'Nein. Eine Regel kann man nie prüfen.', 'Im Gesetz steht eine Regel. Ob der Vater sie richtig wiedergibt, ist prüfbar.', [2]),
}

# Two independent evidence anchors. Choosing a weight is never scored.
ANCHORS = {
    'Mutter': ['Die Mutter bietet Hilfe an und fragt nach Lauras Meinung.', 'Sie erklärt Laura nicht beide Möglichkeiten.'],
    'Freundin': ['Die Freundin denkt an Lauras Ausbildung.', 'Der Satz aus dem Video verspricht fälschlich, dass es keine Blutungen gibt.'],
    'Großmutter': ['Die Großmutter bleibt an Lauras Seite und lässt ihr die Wahl.', 'Laura erfährt wenig über ihre Möglichkeiten.'],
    'Vater': ['Die Beratung gibt Laura Raum für Fragen zur Ausbildung und zu ihren Möglichkeiten.',
              'Der Termin lässt die Entscheidung offen. Die Nachricht erklärt die Wege selbst noch nicht.'],
}
WEIGHTS = {
    'Mutter': ['So weiß Laura, wer ihr helfen möchte.', 'So fehlen Laura noch Informationen für ihre Wahl.'],
    'Freundin': ['Das hilft Laura, ihren Plan im Blick zu behalten.', 'So kann Laura Folgen falsch einschätzen.'],
    'Großmutter': ['So kann Laura sich auch bei einer anderen Wahl auf sie verlassen.', 'So braucht Laura eine zweite Quelle.'],
    'Vater': ['So kann Laura passende Hilfe finden.', 'So kann Laura in Ruhe weiterfragen.'],
}
COUNTER = {
    'Mutter': 'Wie wäre es, wenn die Mutter auch beide Wege erklären würde?',
    'Freundin': 'Wie wäre es, wenn die Freundin den Satz aus dem Video verbessern würde?',
    'Großmutter': 'Wie wäre es, wenn Laura gerade vor allem jemanden zum Reden bräuchte?',
    'Vater': 'Wie wäre es, wenn Laura schon gut informiert wäre und gerade Begleitung suchte?',
}
COUNTER_EXAMPLE = {
    'Mutter': 'Mit einem Überblick über beide Wege würde die Nachricht auch Lauras Fragen beantworten.',
    'Freundin': 'Ohne den Fehler wäre der Rat besser begründet. Laura müsste sich trotzdem selbst entscheiden.',
    'Großmutter': 'Wenn Laura vor allem Nähe sucht, kann das Angebot besonders wichtig werden.',
    'Vater': 'Wenn Laura vor allem Begleitung sucht, könnte das Angebot eines gemeinsamen Besuchs mehr helfen.',
}
CATS = {'Mutter': (3, 'Norm', '„Sollen“ nennt eine Regel der Familie.'),
        'Freundin': (3, 'Fakt', 'Den Satz aus dem Video kann man prüfen. Auch eine falsche Behauptung ist prüfbar.'),
        'Großmutter': (1, 'Wert', 'Sie sagt, was ihr wichtig ist.'),
        'Vater': (3, 'Folgerung', '„Deshalb rate ich dir“ zeigt seinen Rat.')}
FACTS = {'Mutter': [MOTHER], 'Freundin': [FRIEND_OP, FRIEND_VIDEO], 'Großmutter': [GRAND], 'Vater': [FATHER]}
FACT_RESULTS = {'Mutter': 'Blutungen treten auf. Schmerzen sind möglich.',
                'Freundin': 'Eine Operation ist dafür meist nicht nötig. Es kommt zu Blutungen. Schmerzen sind möglich.',
                'Großmutter': 'Sie nennt ihren Glauben und ihren Wunsch. Über einen medizinischen Ablauf sagt sie nichts.',
                'Vater': 'Für die Beratungsregelung stimmen beide Angaben zu Stelle und Frist.'}
JUDGMENTS = ['Sie hilft viel.', 'Sie hilft zum Teil.', 'Sie hilft wenig.']


def evidence_task(person):
    card, right, prompt, other, why = EVIDENCE[person]
    lines = CARDS[card]['lines'] if card else SOURCE['nachrichten'][person]
    reference = 'der Fachkarte' if card else 'der Nachricht'
    return choice(prompt, lines[right-1], lines[other-1], why, f'Vergleiche Zeile {right} in {reference}. {why}',
                  f'Lies Zeile {right} in {reference}.', why, lines=[] if card else [other, right],
                  card=[card, sorted([right, other])] if card else None)


VERDICT_UI = {
    'rating': 'Wie gut hilft sie?',
    'evidence': 'Welcher Beleg wiegt für dich mehr?',
    'simpleEvidence': 'Wähle eine Stelle.',
    'reason': 'Warum ist das für Laura wichtig?',
    'own': 'Eigenen Grund sagen oder schreiben',
    'reconnect': 'Dein Baustein erklärt die andere Stelle. Wähle ihn dort. Oder erkläre deine Verbindung mit eigenen Worten.',
    'write': 'Dein Grund', 'oral': 'Du kannst deinen Grund auch laut sagen.',
    'spoken': 'Ich habe meinen Grund gesagt.',
    'done': 'Abschnitt beenden',
    'reflect': 'Vergleiche deinen Grund mit dem Beleg. Was sagt er über die Hilfe für Laura?',
}


def judgment(person, level):
    a, b = ANCHORS[person]
    acts = {
        'Förder': 'Wähle dein Urteil. Verbinde eine Stelle mit einem Grund.',
        'ESA': 'Wähle dein Urteil und einen Beleg. Erkläre ihn in einem Satz.',
        'MSA': 'Wähle dein Urteil. Erkläre, wie beide Stellen dazu passen.',
        'AHR': 'Wähle dein Urteil. Was wiegt für dich mehr? Prüfe auch die andere Sicht.',
    }
    examples = {
        'Mutter': ('Für mich hilft sie zum Teil. Die Mutter bietet Hilfe an. Laura fehlen aber Infos zu beiden Wegen.',
                   'Für mich zählt hier mehr, dass Laura erst beide Wege kennen möchte.'),
        'Freundin': ('Für mich hilft sie wenig. Sie denkt an die Ausbildung. Der falsche Satz kann Laura aber täuschen.',
                     'Mir ist hier wichtiger, dass Laura sich auf die Infos verlassen kann.'),
        'Großmutter': ('Für mich hilft sie viel. Sie bleibt bei Laura, auch wenn Laura anders entscheidet.',
                       'Fachwissen fehlt. Laura kann es woanders bekommen. Für mich zählt hier die Nähe mehr.'),
        'Vater': ('Für mich hilft sie viel. Laura kann bei der Beratung Fragen stellen. Die Wahl bleibt bei ihr.',
                  'Der Vater erklärt die Wege noch nicht. Für mich zählt mehr, dass Laura weiß, wo sie Hilfe bekommt.'),
    }
    sample, weighting = examples[person]
    if level in LEVELS[2:]:
        sample += ' ' + weighting
    if level == 'AHR':
        sample += ' ' + COUNTER_EXAMPLE[person]
    return dict(kind='judgment', prompt=acts[level], options=JUDGMENTS, anchors=[a, b], links=WEIGHTS[person],
                matchingLinks=[[0, 1], [0, 1]] if person == 'Vater' else [[0], [1]],
                counter=COUNTER[person] if level == 'AHR' else '', results=[FACT_RESULTS[person], WISHES[person][-1]],
                hints=['Wähle zuerst, wie gut die Nachricht hilft.', 'Dein Grund zählt. Was bringt die Stelle Laura?',
                       f'Lies oben „Geprüft“. Achte hierauf: {a}', f'{a} {WEIGHTS[person][0]} Überlege, wie wichtig das für Laura ist.',
                       sample + ' Wähle dein Urteil. Gib deinen Grund an. Tippe auf „Abschnitt beenden“.'])


def bank():
    lessons = {}
    for person, message in SOURCE['nachrichten'].items():
        lines, wishes, prompt, target, other, reason = WISHES[person]
        wish = choice(prompt, target, other, reason, f'Lies {person}, Zeile {lines[-1]}. {reason}',
                      f'Lies Lauras Worte und {person}, Zeilen {", ".join(map(str,lines))}.', reason, lines=lines, wishes=wishes)
        wish['hints'][1] = 'Suche einen Wunsch von Laura. Was sagt die Person dazu?'
        by_level = {}
        for i, level in enumerate(LEVELS):
            tasks = [dict(category(person, *CATS[person]), heading='Argumenten-Check')]
            checks = list(FACTS[person])
            if level == 'ESA':
                checks.append(evidence_task(person))
            tasks.extend(dict(item, heading=QUESTIONS[0]) for item in checks)
            tasks.append(dict(wish, heading=QUESTIONS[1]))
            if i >= 2:
                p, t, o, why, ls = DEEP[person]
                tasks.append(dict(choice(p, t, o, why, f'Lies Zeile {ls[-1]}. {why}', f'Lies {person}, Zeile {ls[-1]}.', why, lines=ls,
                                         card=['beratung', [1, 2]] if person == 'Vater' else None),
                                  heading=QUESTIONS[1]))
            tasks.append(dict(judgment(person, level), heading=QUESTIONS[2]))
            # Vary the correct position; preserve category order.
            for n, task in enumerate(tasks):
                if task['kind']=='check' and (n+i+list(WISHES).index(person)) % 2:
                    task['options'] = list(reversed(task['options']))
            by_level[level] = tasks
        lessons[person] = dict(message=message, sections=[person+' 1 – Argumenten-Check', person+' 2 – Nachricht prüfen'], levels=by_level)
    return dict(lead='Wie gut helfen die Nachrichten Laura?', context='Laura ist 19 Jahre alt und macht eine Ausbildung.',
                laura=SOURCE['laura'], levels=LEVELS, categories=CATEGORIES, questions=QUESTIONS, helps=HELP,
                sources=SOURCES, cards=CARDS, verdictUI=VERDICT_UI, cases=lessons)
