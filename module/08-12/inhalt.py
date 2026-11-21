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
HELP = ['Was soll ich tun?', 'Was bedeutet die Frage?', 'Wo finde ich die passende Stelle?',
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
VERDICT_UI = {
    'evidence': 'Welche Stelle passt zu deiner Antwort?',
    'goal': 'Welche Aussage von Laura ist für deine Antwort wichtig?',
    'rating': 'Wie gut hilft die Nachricht Laura?',
    'reason': 'Warum hilft diese Info Laura? Was bleibt offen?',
    'own': 'Einen eigenen Grund sagen oder schreiben',
    'write': 'Dein Grund', 'oral': 'Du kannst deinen Grund auch laut sagen.',
    'spoken': 'Ich habe meinen Grund gesagt.', 'done': 'Abschnitt beenden',
    'reflect': 'Prüfe auf deinem Lernbogen: Erklärt dein Grund, wie die Fachinformation Laura hilft?',
}


SOURCES['BIÖG · Frühe Schwangerschaft'] = 'https://www.familienplanung.de/schwangerschaft/schwangerschaftswochen/1-bis-4-schwangerschaftswoche/'
CARDS = {
    'medizin': dict(title='Abbruch mit Medikamenten', lines=[
        'Medikamente beenden die Schwangerschaft.',
        'Ein Medikament bewirkt, dass sich die Gebärmutter zusammenzieht.',
        'Dabei wird Schwangerschaftsgewebe ausgestoßen. Es kommt zu Blutungen.',
        'Schmerzen und Krämpfe können auftreten.',
        'Ein Abbruch mit Medikamenten ist grundsätzlich ohne Operation möglich.',
        'Manchmal ist eine weitere Behandlung nötig.',
        'Auch ohne Operation kommt es zu Blutungen. Schmerzen sind möglich.',
        'Eine Ärztin oder ein Arzt prüft, ob die Methode für die Person infrage kommt.'
    ], parts={'Was passiert im Körper?': [1, 2, 3, 4], 'Ist eine Operation nötig?': [5, 6], 'Wichtig': [7, 8]},
        sources=['BIÖG', 'IQWiG']),
    'entwicklung': dict(title='Am Anfang der Schwangerschaft', lines=[
        'Die befruchtete Eizelle teilt sich auf dem Weg zur Gebärmutter.',
        'Nach der Einnistung in der Gebärmutter entwickelt sich dort der Embryo weiter.'
    ], sources=['BIÖG · Frühe Schwangerschaft']),
    'beratung': dict(title='Beratung und Gesetz', lines=[
        'Eine anerkannte Beratungsstelle informiert über Möglichkeiten und Hilfen.',
        'Für einen Abbruch nach der Beratungsregelung gilt unter anderem: Die Beratung muss bei einer staatlich anerkannten Schwangerschaftskonfliktberatungsstelle stattfinden.',
        'Die Beratung muss mindestens drei Tage vor dem Abbruch liegen.',
        'Die Beratung ist ergebnisoffen. Ein Termin legt Lauras Entscheidung nicht fest.',
        'Laura kann dort auch nach Hilfe für ihre Ausbildung fragen.'
    ], sources=[s for s in SOURCES if s.startswith(('StGB', 'SchKG'))]),
}

# These are interpretations of numbered source passages, never annotations in the messages.
READING = {
    'Mutter': [
        (1, 'Blutungen treten auf. Schmerzen sind möglich.'),
        (2, 'Gesundheit und Familie sind ihr wichtig.'),
        (3, 'Familienmitglieder sollen einander helfen.'),
        (5, 'Sie rät Laura, die Schwangerschaft fortzusetzen.')
    ],
    'Freundin': [
        (1, 'Ein Abbruch mit Medikamenten ist grundsätzlich ohne Operation möglich.'),
        (2, 'Lauras Ausbildung und Zukunft sind ihr wichtig.'),
        (3, 'Man sollte bei wichtigen Entscheidungen auf seine Zukunftspläne achten.'),
        (4, 'Sie rät Laura zu einem Schwangerschaftsabbruch.')
    ],
    'Großmutter': [
        (1, 'Am Anfang der Schwangerschaft entwickelt sich ein Embryo in der Gebärmutter.'),
        (2, 'Ungeborenes Leben ist ihr wichtig.'),
        (3, 'Nach ihrem Glauben soll ungeborenes Leben geschützt werden.'),
        (4, 'Sie wünscht sich, dass Laura die Schwangerschaft fortsetzt.')
    ],
    'Vater': [
        (1, 'Eine anerkannte Beratungsstelle informiert über die Möglichkeiten.'),
        (2, 'Gute Informationen und Lauras freie Entscheidung sind ihm wichtig.'),
        (3, 'Für die Beratungsregelung sind die anerkannte Stelle und die Frist vorgeschrieben.'),
        (4, 'Er rät Laura, zuerst eine Beratungsstelle aufzusuchen.')
    ],
}
FIELD_HELP = {
    'Fakt': ('Einen Fakt kannst du an einer Quelle prüfen.',
             'Diese Aussage kannst du mit einer Fachkarte vergleichen.'),
    'Wert': ('Ein Wert zeigt, was jemand wichtig findet.',
             'Ein Wert nennt, was zählt. Eine Regel sagt, wie man handeln soll.'),
    'Norm': ('Eine Norm ist eine allgemeine Regel.',
             'Die Regel gilt auch für andere Menschen. Der konkrete Rat richtet sich an Laura.'),
    'Folgerung': ('Eine Folgerung ist hier der Rat an Laura.',
                  'Überlege, was Laura aus Sicht der Person jetzt tun soll.'),
}
FIELD_PLACES = {
    'Mutter': ['Lies den Anfang über den Abbruch.', 'Lies die Stelle über ihre Sorge.', 'Lies die Stellen über Familie und Hilfe.', 'Lies den Schluss nach dem Hilfsangebot.'],
    'Freundin': ['Lies den Anfang über Medikamente.', 'Lies die Stelle über Lauras Ausbildung.', 'Suche die allgemeine Regel über Zukunftspläne.', 'Lies ihren letzten Satz.'],
    'Großmutter': ['Suche die Stelle über den Embryo.', 'Was sagt sie über ungeborenes Leben?', 'Lies die Stelle über ihren Glauben.', 'Wo nennt sie einen Wunsch für Laura?'],
    'Vater': ['Suche die Auskunft über die Beratungsstelle.', 'Was sagt er über Wissen und Entscheiden?', 'Suche die Aussage über das Gesetz.', 'Was rät er Laura als ersten Schritt?'],
}
EXTRA_LINES = {'Mutter': 'Hier bietet sie Laura persönlich Hilfe an.',
               'Großmutter': 'Hier verspricht sie Laura Unterstützung bei jeder Entscheidung.',
               'Vater': 'Hier lässt er die Entscheidung ausdrücklich bei Laura.'}


def argument_map(person, level):
    entries = READING[person]
    all_ids = list(range(1, len(SOURCE['nachrichten'][person]) + 1))
    fields = []
    roles = {line: meaning for line, meaning in entries}
    for i, (name, (line, meaning)) in enumerate(zip(CATEGORIES, entries, strict=True)):
        # Similar passages make meaningful alternatives: value/rule and rule/advice.
        near = entries[[1, 2, 3, 2][i]][0]
        ids = [line, near]
        if level == 'ESA' or (person == 'Freundin' and level == 'Förder'):
            # Keep the legal fact/norm overlap for the independent, upper-level check.
            extra = 4 if person == 'Vater' and name == 'Fakt' else next(n for n in all_ids if n not in ids)
            ids.append(extra)
        if level in LEVELS[2:]:
            ids = all_ids
        options = []
        for n in sorted(ids):
            dual = person == 'Vater' and name == 'Fakt' and n == 3
            correct = n == line or dual
            if dual:
                feedback = 'Auch das passt. Man kann die Vorschrift im Gesetz nachlesen. Zeile 1 nennt das Angebot der Stelle.'
            elif correct:
                feedback = meaning
            else:
                seen = roles[n] if n in roles else EXTRA_LINES[person]
                feedback = f'{seen} {CATEGORIES[name]}'
            options.append(dict(line=n, correct=correct, feedback=feedback))
        define, relation = FIELD_HELP[name]
        target = SOURCE['nachrichten'][person][line-1]
        hints = [f'Wähle für {name} eine Zeile.', define, FIELD_PLACES[person][i], relation,
                 f'{meaning} Wähle bei {name} Zeile {line}.']
        if name == 'Norm' and person == 'Mutter':
            hints[-1] = f'„{target}“ Wähle bei Norm Zeile {line}.'
        fields.append(dict(name=name, line=line, meaning=meaning, options=options, hints=hints))
    return dict(kind='map', heading='Argumenten-Check', prompt='Wähle für jedes Feld eine Zeile.',
                fields=fields, lines=all_ids, wishes=[])


def check(prompt, lines, choices, *, look, clue, meaning, card=None, wishes=(), mother=()):
    """First option is the evidence-based answer. Display order varies in bank()."""
    return dict(kind='check', prompt=prompt, lines=lines, wishes=list(wishes), card=card, mother=list(mother),
                options=[dict(label=label, correct=i == 0, feedback=feedback)
                         for i, (label, feedback) in enumerate(choices)],
                hints=['Lies die Stelle. Wähle die passende Antwort.', meaning, look, clue,
                       f'Wähle „{choices[0][0]}“. Tippe auf „Weiter“.'])


FACTS = {
    'Mutter': check('Wie kommt es bei diesem Abbruch zur Blutung?', [1], [
        ('Die Gebärmutter zieht sich zusammen. Gewebe wird ausgestoßen.', 'Das Medikament wirkt auf die Gebärmutter. Dabei blutet es. Schmerzen sind möglich.'),
        ('Die Blutung entsteht erst bei einer Operation.', 'Lies auf der Fachkarte Zeilen 2 und 3. Dort wirkt das Medikament.')
    ], card=['medizin', [2, 3, 4]], look='Lies Fachkarte „Abbruch mit Medikamenten“, Zeilen 2 bis 4.',
        clue='Das Medikament löst das Zusammenziehen aus. Gewebe verlässt die Gebärmutter.',
        meaning='Suche im Körper den Grund für die Blutung.'),
    'Freundin': check('Wie passen die beiden medizinischen Aussagen zusammen?', [1], [
        ('Medikamente wirken ohne Operation. Beim Ausstoßen von Gewebe blutet es.', 'Beide beschreiben denselben Weg. Die Freundin nennt die Art des Abbruchs. Die Mutter nennt eine körperliche Folge.'),
        ('Die Mutter beschreibt eine Operation. Die Freundin beschreibt einen anderen Weg.', 'Lies die erste Zeile beider Nachrichten. Beide sprechen von Medikamenten.'),
        ('Blutungen zeigen, dass eine Operation nötig war.', 'Lies Zeile 3 der Karte. Die Blutung entsteht beim Ausstoßen des Gewebes.')
    ], card=['medizin', [2, 3, 4, 5]], mother=[1], look='Vergleiche beide ersten Zeilen mit den Kartenzeilen 2 bis 5.',
        clue='Das Medikament bringt die Gebärmutter zum Zusammenziehen. Dafür ist grundsätzlich keine Operation nötig.',
        meaning='Können diese Dinge beim selben Abbruch passieren?'),
    'Großmutter': check('Welche Aussage kannst du mit der Fachkarte prüfen?', [1, 3], [
        ('Nach der Einnistung wächst der Embryo in der Gebärmutter weiter.', 'Die Entwicklung im Körper ist biologisch überprüfbar.'),
        ('Die Entwicklung des Embryos beweist die Glaubensregel.', 'Lies Zeile 1 und Zeile 3 getrennt. Die Karte erklärt einen Vorgang im Körper. Die Regel stammt aus ihrem Glauben.')
    ], card=['entwicklung', [1, 2]], look='Lies auf der Karte „Am Anfang der Schwangerschaft“ die zweite Zeile.',
        clue='Die Karte erklärt, wo der Embryo wächst. Die Großmutter sagt selbst, woher ihre Regel kommt.',
        meaning='Suche die Aussage über den Körper.'),
    'Vater': check('Was stimmt über die Beratungsstelle?', [1, 3], [
        ('Sie informiert. Für die Beratungsregelung sind eine anerkannte Stelle und mindestens drei Tage Abstand vorgeschrieben.',
         'Das Angebot in Zeile 1 und die beiden gesetzlichen Vorgaben in Zeile 3 stimmen.'),
        ('Jede Stelle reicht aus, wenn der Termin drei Tage vor dem Abbruch liegt.',
         'Lies die Kartenzeilen 2 und 3. Für diese Regelung ist auch die staatliche Anerkennung vorgeschrieben.')
    ], card=['beratung', [1, 2, 3]], look='Lies „Beratung und Gesetz“, Zeilen 1 bis 3.',
        clue='Unterscheide das Angebot der Stelle und die Vorgaben für die Beratungsregelung.',
        meaning='Prüfe, was die Stelle anbietet und was für diese Regelung gilt.'),
}

WISHES = {
    'Mutter': check('Was bietet die Mutter Laura? Was ist noch offen?', [2, 3, 4, 5], [
        ('Sie bietet Hilfe mit dem Kind an. Laura möchte erst beide Wege kennen.', 'Ihre Familienregel erklärt das Angebot. Laura darf trotzdem anders wählen.'),
        ('Das Hilfsangebot beantwortet schon, welcher Weg zu Laura passt.', 'Lies Lauras Worte. Ihr fehlen Informationen zu ihren Möglichkeiten.')
    ], wishes=[4, 5], look='Vergleiche die Zeilen 3 bis 5 der Mutter mit Lauras Worten.',
        clue='Mit einem Kind will die Mutter helfen. Laura hat noch keine Entscheidung getroffen.',
        meaning='Was würde Laura durch die Nachricht bekommen? Was sucht sie noch?'),
    'Freundin': check('Warum raten sie Laura zu verschiedenen Wegen?', [2, 3, 4], [
        ('Die Mutter setzt auf Familienhilfe und rät zum Fortsetzen. Die Freundin denkt an die Zukunft und rät zum Abbruch.',
         'Die dritte Zeile beider Nachrichten erklärt, warum die Ratschläge verschieden sind.'),
        ('Eine der beiden muss sich beim Ablauf mit Medikamenten irren.',
         'Vergleiche die Regeln in Zeile 3 beider Nachrichten. Die medizinischen Aussagen passen zusammen.'),
        ('Der Ausbildungswunsch legt schon fest, was Laura tun soll.',
         'Lies Lauras Worte. Sie möchte die Ausbildung abschließen und selbst entscheiden.')
    ], wishes=[2, 5], mother=[2, 3, 5], look='Lies bei beiden die dritte Zeile und den Rat danach.',
        clue='Die Mutter nennt eine Familienregel. Die Freundin nennt eine Regel für Zukunftspläne.',
        meaning='Suche, was bei jeder Person den Ausschlag gibt.'),
    'Großmutter': check('Was bietet sie Laura bei einer anderen Wahl an?', [3, 4, 5], [
        ('Sie bleibt bei Laura. Laura kann selbst entscheiden.', 'Ihr Wunsch und ihr Angebot stehen nebeneinander. Laura muss den Glauben nicht teilen.'),
        ('Ihre Unterstützung hängt davon ab, dass Laura ihren Glauben teilt.', 'Lies Zeile 5. Dort verspricht sie Hilfe bei jeder Wahl.')
    ], wishes=[4, 5], look='Vergleiche den Wunsch in Zeile 4 mit dem Versprechen in Zeile 5.',
        clue='Achte auf „egal wie du dich entscheidest“.', meaning='Was gilt, auch wenn Laura anders denkt?'),
    'Vater': check('Was bringt der Termin Laura?', [2, 4, 5], [
        ('Sie kann sich informieren und danach selbst entscheiden.', 'Verlässliche Informationen und die freie Wahl sind auch dem Vater wichtig.'),
        ('Mit dem Termin entscheidet sie sich für einen Abbruch.', 'Lies Zeile 5 des Vaters und Kartenzeile 4. Das Ergebnis ist offen.')
    ], wishes=[4, 5], card=['beratung', [4, 5]], look='Lies seine letzte Zeile und Kartenzeile 4.',
        clue='Ein Rat zum Gespräch lässt die spätere Wahl offen.', meaning='Ein Termin und eine Schwangerschaftsentscheidung sind zwei Schritte.'),
}

# Only the second question carries a deeper check. All four routes have the same positions.
CITATIONS = {
    'Mutter': ['2–3', '5'], 'Freundin': ['3 und 5', '5', '3'],
    'Großmutter': ['2','2'], 'Vater': ['1–3','3'],
}
DEPTH = {
    'Mutter': ('Welche Hilfe passt noch zur Regel der Mutter?', [3, 4, 5],
               'Sie könnte Laura auch zu einer Beratung begleiten. Das wäre ebenfalls Familienhilfe.',
               'Die Zusage in Zeile 4 gilt für ein Kind. Damit gilt auch die Familienregel nur für diesen Weg.',
               'Die Zusage nennt einen bestimmten Fall. Die Regel über gegenseitige Hilfe ist weiter gefasst.'),
    'Freundin': ('Was folgt aus der Regel über Zukunftspläne?', [2, 3, 4],
                 'Laura kann für beide Wege prüfen, wie sie die Ausbildung beenden könnte.',
                 'Laura will ihre Ausbildung beenden. Damit steht schon fest, welcher Weg besser zu ihrem Plan passt.',
                 'Die Regel nennt ein Ziel. Wie Laura es auf jedem Weg erreichen könnte, ist noch offen.'),
    'Großmutter': ('Welche Stelle erklärt den Wunsch der Großmutter?', [1, 3, 4],
                   'Die Entwicklung ist prüfbar. Warum sie zum Fortsetzen rät, erklärt ihre Glaubensregel.',
                   'Die Entwicklung des Embryos reicht als Grund für ihren Rat. Die Glaubensregel sagt dasselbe.',
                   'Die erste Stelle beschreibt den Körper. Die dritte sagt, was aus ihrer Sicht geschützt werden soll.'),
    'Vater': ('Kann die Stelle über das Gesetz Fakt und Norm sein?', [3],
              'Ja. Der Wortlaut ist prüfbar. Er sagt zugleich, was gesetzlich gilt.',
              'Da der Vater das Gesetz nur wiedergibt, enthält seine Nachricht hier ausschließlich einen Fakt.',
              'Auch eine zitierte Vorschrift beschreibt eine Regel. Ihr Wortlaut lässt sich prüfen.'),
}
AHR_FRIEND = ('Können beide Regeln zugleich gelten? Müssen beide dann dasselbe raten?', [2, 3, 4],
              'Beides kann zählen. Je nachdem, was Laura braucht, können die Regeln verschiedene Wege stützen.',
              'Beides kann zählen. Wenn beide dieselben Regeln annehmen, müssen sie auch zum selben Weg raten.',
              'Familienhilfe und Zukunftspläne schließen sich nicht aus. Ihr Gewicht und Lauras Möglichkeiten können verschieden sein.')
JUDGMENTS = ['Sie hilft viel.', 'Sie hilft zum Teil.', 'Sie hilft wenig.']

# Each approved factual excerpt comes verbatim from the common card. An assessment
# requires an explicit excerpt, a Laura quote, a rating and a learner-made connection.
PROOF = {
    'Mutter': ('medizin', [3, 4], [4, 5]),
    'Freundin': ('medizin', [5, 7], [2, 5]),
    'Großmutter': ('entwicklung', [1, 2], [4, 5]),
    'Vater': ('beratung', [1, 4], [4, 5]),
}
LINKS = {
    'Mutter': ['Laura kennt jetzt eine mögliche körperliche Belastung.', 'Für den Vergleich braucht Laura auch Informationen zum anderen Weg.'],
    'Freundin': ['Laura kann den Ablauf mit ihren Plänen vergleichen.', 'Wie Laura die Ausbildung weiterführt, bleibt offen.'],
    'Großmutter': ['Laura weiß mehr über die Entwicklung im Körper.', 'Laura sucht auch Informationen über ihre Möglichkeiten.'],
    'Vater': ['Laura weiß jetzt, wo sie Informationen bekommt.', 'Laura kann fragen und ihre Wahl offenlassen.'],
}
COUNTERS = {
    'Mutter': ('Wie wäre es, wenn Laura schon gut informiert wäre und jetzt Hilfe im Alltag suchte?', 'Dann könnte das Hilfsangebot für sie mehr zählen.'),
    'Freundin': ('Wie wäre es, wenn der Betrieb Laura auch mit Kind einen Ausbildungsplatz zusichert?', 'Dann könnte sie die Ausbildung auf beiden Wegen fortsetzen.'),
    'Großmutter': ('Wie wäre es, wenn Laura gerade vor allem jemanden zum Reden bräuchte?', 'Dann könnte die zugesagte Nähe für sie mehr zählen.'),
    'Vater': ('Wie wäre es, wenn Laura bereits eine Beratung besucht hätte?', 'Dann könnte ein weiteres Gespräch weniger dringlich sein.'),
}
EXAMPLES = {
    'Mutter': 'Für mich hilft sie zum Teil. Beim Ausstoßen von Gewebe kommt es zu Blutungen. Laura sucht richtige Infos. Jetzt kennt sie eine körperliche Folge. Für ihren Vergleich fehlt noch der andere Weg.',
    'Freundin': 'Für mich hilft sie zum Teil. Der Abbruch ist grundsätzlich ohne Operation möglich. Laura will die Ausbildung abschließen. Die Info erklärt den Ablauf. Wie die Ausbildung weitergeht, muss sie für beide Wege klären.',
    'Großmutter': 'Für mich hilft sie wenig bei Lauras Suche nach Möglichkeiten. Laura erfährt, wo sich der Embryo entwickelt. Was die beiden Wege für sie bedeuten, bleibt offen. Das Angebot, bei ihr zu bleiben, kann trotzdem helfen.',
    'Vater': 'Für mich hilft sie viel. Die Stelle informiert über beide Wege. Laura möchte richtige Infos und selbst entscheiden. Beim Termin kann sie Fragen klären und ihre Wahl offenlassen.',
}
SELF_CHECK = {
    'Mutter': 'Welche körperliche Folge nennst du? Was will Laura wissen? Warum reicht die Nachricht für sie aus oder nur zum Teil?',
    'Freundin': 'Was weiß Laura über den Abbruch? Was möchte sie für ihre Ausbildung? Wie passt dein Grund zu deiner Einschätzung?',
    'Großmutter': 'Was zeigt die Fachkarte zum Embryo? Welche Frage bleibt für Laura offen? Was bringt ihr das Angebot der Großmutter?',
    'Vater': 'Was kann eine Beratungsstelle tun? Was möchte Laura? Wie hilft ihr der Rat zum Termin?',
}


def judgment(person, level):
    key, facts, goals = PROOF[person]
    prompts = {'Förder': 'Wähle zuerst eine Fachinformation.',
               'ESA': 'Verbinde eine Kartenstelle mit Lauras Wunsch. Erkläre deinen Grund kurz.',
               'MSA': 'Was hilft Laura? Was fehlt ihr noch? Verbinde die Fachinformation mit Lauras Wunsch.',
               'AHR': 'Verbinde die Fachinformation mit Lauras Wunsch. Prüfe, wann du anders urteilen würdest.'}
    sample = EXAMPLES[person]
    if level == 'AHR':
        sample += ' ' + COUNTERS[person][1]
    return dict(kind='judgment', heading=QUESTIONS[2], prompt=prompts[level], options=JUDGMENTS,
                card=[key,facts], goals=goals, links=LINKS[person], selfCheck=SELF_CHECK[person],
                counter=COUNTERS[person][0] if level=='AHR' else '',
                hints=['Wähle eine Kartenstelle. Wähle dann Lauras Worte.',
                       'Überlege: Was kann Laura mit dieser Info anfangen?',
                       f'Lies „{CARDS[key]["title"]}“, Zeile {facts[-1]}. Vergleiche Lauras Worte darunter.',
                       'Die Info zeigt … Laura möchte … Deshalb hilft die Nachricht aus meiner Sicht …',
                       sample+' Wähle Kartenstelle, Lauras Worte und Einschätzung. Gib deinen Grund an. Tippe auf „Abschnitt beenden“.'])


def bank():
    cases = {}
    for pi, (person, message) in enumerate(SOURCE['nachrichten'].items()):
        by_level = {}
        for level in LEVELS:
            fact = dict(FACTS[person], heading=QUESTIONS[0])
            fact['prompt'] += ' Wähle die Antwort mit dem passenden Kartenbeleg.'
            fact['options'] = [dict(o, citation=n) for o,n in zip(fact['options'],CITATIONS[person],strict=True)]
            wishes = dict(WISHES[person], heading=QUESTIONS[1])
            if level in LEVELS[2:]:
                special = person=='Freundin' and level=='AHR'
                prompt, ids, target, other, why = AHR_FRIEND if special else DEPTH[person]
                q = check(prompt, ids, [(target, why), (other, 'Prüfe die Regel und den konkreten Rat noch einmal. '+why)],
                          look=f'Lies {person}, Zeile {ids[0]} bis {ids[-1]}.' if len(ids)>1 else f'Lies {person}, Zeile {ids[0]}.',
                          clue=why, meaning='Prüfe, ob die Regel auch einen anderen Weg zulässt.' if person!='Vater' else 'Eine Aussage kann zwei Aufgaben erfüllen.')
                if special:
                    q['mother']=[3,5]
                    q['hints'][2]='Vergleiche Zeile 3 der Mutter mit Zeile 3 der Freundin.'
                if pi%2==0: q['options']=list(reversed(q['options']))
                q['hints'][-1]=f'Wähle „{target}“. Tippe auf „Weiter“.'
                wishes['depth']=q
                base=next(o['label'] for o in wishes['options'] if o['correct'])
                wishes['hints']=[*wishes['hints'][:4], f'Wähle „{base}“. Lies dann die Frage unter „Weiterdenken“.']
            for index, task in enumerate((fact,wishes),1):
                shift=(pi+index)%len(task['options'])
                task['options']=task['options'][shift:]+task['options'][:shift]
            by_level[level]=[argument_map(person,level),fact,wishes,judgment(person,level)]
        cases[person]=dict(message=message,sections=[person+' 1 – Argumenten-Check',person+' 2 – Nachricht prüfen'],levels=by_level)
    return dict(lead='Wie gut helfen die Nachrichten Laura?',context='Laura ist 19 Jahre alt und macht eine Ausbildung.',
                laura=SOURCE['laura'],levels=LEVELS,categories=CATEGORIES,questions=QUESTIONS,helps=HELP,
                sources=SOURCES,cards=CARDS,verdictUI=VERDICT_UI,cases=cases)
