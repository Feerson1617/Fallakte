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
CHAINS = {
    'Mutter': 'Die Info über Blutungen stimmt. Die Mutter sorgt sich um Lauras Gesundheit. Familie zählt für sie. Weil Familien einander helfen sollen, rät sie zum Fortsetzen. Die Blutung und ihr Hilfsangebot legen Lauras Wahl nicht fest.',
    'Freundin': 'Die Info zur Operation stimmt. Der Freundin ist die Ausbildung wichtig. Zukunftspläne sollen bei der Wahl zählen. Deshalb rät sie zum Abbruch. Auch ohne Operation gibt es Blutungen. Weder der Ablauf noch die Ausbildung legt Lauras Wahl fest.',
    'Großmutter': 'Der Embryo entwickelt sich in der Gebärmutter. Ungeborenes Leben ist ihr wichtig. Ihr Glaube fordert Schutz. Daher wünscht sie das Fortsetzen. Sie unterstützt Laura auch bei einer anderen Wahl.',
    'Vater': 'Die Stelle informiert. Dem Vater sind Wissen und freie Wahl wichtig. Die Beratungsregelung schreibt eine anerkannte Stelle und eine Frist vor. Er empfiehlt einen Termin. Laura kann danach selbst entscheiden.',
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
            ids.append(next(n for n in all_ids if n not in ids))
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
                feedback = f'Zeile {n}: {seen} Suche für „{name}“ in Zeile {line}.'
            options.append(dict(line=n, correct=correct, feedback=feedback))
        fields.append(dict(name=name, line=line, meaning=meaning, options=options))
    mapping = ', '.join(f"{field['name']} {field['line']}" for field in fields)
    prompt = 'Wähle zu jedem Feld die passende Zeile.'
    if person == 'Mutter':
        prompt += ' Beginne mit dem Fakt.'
    return dict(kind='map', heading='Argumenten-Check', prompt=prompt, fields=fields, lines=all_ids, wishes=[],
                hints=['Lies die Nachricht. Wähle für jedes Feld eine Zeile.',
                       'Ein Wert zeigt, was zählt. Eine Norm ist eine Regel. Ein Rat richtet sich hier an Laura.',
                       f'Lies die Zeilen {entries[1][0]} und {entries[2][0]}. Wo steht, was der Person wichtig ist?',
                       f'{entries[1][1]} Ihre Regel steht in Zeile {entries[2][0]}. Daraus entsteht der Rat in Zeile {entries[3][0]}.',
                       f'{mapping}. {CHAINS[person]} Wähle diese Zeilen. Tippe auf „Weiter“.'])


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
         'Die Mutter rät zum Fortsetzen, die Freundin zum Abbruch. Ihre Regeln erklären die Richtung. Laura bestimmt selbst, was für sie zählt.'),
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

# ESA retrieves a source passage. Older readers check an inference or an alternative interpretation.
EVIDENCE = {
    'Mutter': ('medizin', 3, 5, 'Welche Kartenstelle belegt die Blutung?'),
    'Freundin': ('medizin', 5, 4, 'Welche Kartenstelle belegt die Aussage der Freundin zur Operation?'),
    'Großmutter': ('entwicklung', 2, 1, 'Welche Kartenstelle erklärt, wo der Embryo nach der Einnistung wächst?'),
    'Vater': ('beratung', 3, 4, 'Welche Kartenstelle belegt die Frist?'),
}
DEEP = {
    'Mutter': ('Wie hängt die Familienregel mit dem Rat zusammen?', [3, 4, 5],
               'Die Regel erklärt ihr Hilfsangebot. Sie lässt auch Hilfe bei einer anderen Wahl zu.',
               'Wer Hilfe in der Familie wichtig findet, muss denselben Rat geben.',
               'Zeile 3 verlangt gegenseitige Hilfe. Zeile 5 ist der persönliche Rat der Mutter.'),
    'Freundin': ('Was wäre, wenn Laura ihre Ausbildung auch mit Kind fortsetzen könnte?', [2, 3, 4],
                 'Die Ausbildung bleibt wichtig. Dieselbe Regel lässt dann auch einen anderen Rat zu.',
                 'Dann wäre die medizinische Aussage der Freundin falsch.',
                 'Die Möglichkeiten in der Ausbildung ändern das Gewicht ihres Grundes. Der körperliche Ablauf bleibt gleich.'),
    'Großmutter': ('Folgt die Glaubensregel aus der Entwicklung des Embryos?', [1, 2, 3, 4],
                   'Die Entwicklung ist prüfbar. Die Regel erklärt sie mit ihrem Glauben.',
                   'Die biologische Aussage allein schreibt Laura die Entscheidung vor.',
                   'In Zeile 1 beschreibt sie den Körper. In Zeile 3 begründet sie die Regel mit ihrem Glauben.'),
    'Vater': ('Kann Zeile 3 zugleich eine prüfbare Aussage und eine Norm enthalten?', [3],
              'Ja. Man kann im Gesetz prüfen, welche Regel gilt.',
              'Nein. Was eine Regel nennt, kann man nie überprüfen.',
              'Der Gesetzestext lässt sich nachlesen. Sein Inhalt ist eine rechtliche Regel.'),
}

JUDGMENTS = ['Sie hilft viel.', 'Sie hilft zum Teil.', 'Sie hilft wenig.']
ANCHORS = {
    'Mutter': ['Die Mutter bietet Hilfe an, wenn Laura das Kind bekommt.', 'Sie erklärt den Weg mit Medikamenten nur zum Teil.'],
    'Freundin': ['Die Freundin denkt an Lauras Ausbildung.', 'Sie rät zum Abbruch. Wege für die Ausbildung mit Kind nennt sie nicht.'],
    'Großmutter': ['Sie bleibt bei Laura, wie auch immer Laura entscheidet.', 'Sie erklärt den Embryo. Über Lauras Möglichkeiten sagt sie wenig.'],
    'Vater': ['Er zeigt Laura eine Stelle für ihre Fragen.', 'Er lässt die Entscheidung ausdrücklich bei Laura.'],
}
WEIGHTS = {
    'Mutter': ['So kennt Laura ein konkretes Hilfsangebot.', 'Laura braucht noch Informationen zum Vergleichen.'],
    'Freundin': ['So bleibt Lauras Zukunftsplan im Blick.', 'Laura braucht für ihren Vergleich auch diese Möglichkeit.'],
    'Großmutter': ['So kann Laura auf ihre Unterstützung zählen.', 'Für ihre Wahl braucht Laura noch andere Informationen.'],
    'Vater': ['So findet Laura verlässliche Informationen.', 'So kann Laura ihren eigenen Weg wählen.'],
}
RESULTS = {
    'Mutter': ['Beim Ausstoßen des Gewebes blutet es. Schmerzen sind möglich.', 'Familie zählt für die Mutter. Sie bietet Hilfe an, falls Laura das Kind bekommt.'],
    'Freundin': ['Medikamente können ohne Operation wirken. Beim Ausstoßen von Gewebe kommt es zu Blutungen.',
                 'Die Mutter setzt auf Hilfe in der Familie. Die Freundin denkt an die Ausbildung. Sie geben entgegengesetzte Ratschläge.'],
    'Großmutter': ['Nach der Einnistung wächst der Embryo in der Gebärmutter.', 'Ihre Regel kommt aus ihrem Glauben. Laura darf anders wählen.'],
    'Vater': ['Die Stelle informiert. Die Beratungsregelung nennt Stelle und Frist.', 'Der Vater legt Wert auf Wissen und freie Wahl. Der Termin lässt die Entscheidung offen.'],
}
COUNTERS = {
    'Mutter': ('Was wäre, wenn Laura gerade vor allem praktische Hilfe sucht?', 'Dann könnte das Hilfsangebot für Laura mehr wiegen.'),
    'Freundin': ('Was wäre, wenn Laura ihre Ausbildung mit Kind fortsetzen könnte?', 'Dann wäre der Ausbildungswunsch auch mit einem Kind vereinbar.'),
    'Großmutter': ('Was wäre, wenn Laura sich gerade vor allem Begleitung wünscht?', 'Dann könnte die zugesagte Nähe für Laura besonders wichtig sein.'),
    'Vater': ('Was wäre, wenn Laura schon über beide Wege gut informiert wäre?', 'Dann könnte ihr persönliche Begleitung mehr helfen als ein weiterer Hinweis auf Beratung.'),
}
SELF_CHECK = {
    'Mutter': 'Nennst du die Blutung und das Hilfsangebot? Erklärst du, was Laura trotzdem noch entscheiden muss?',
    'Freundin': 'Erklärst du, wie Blutungen auch ohne Operation entstehen? Zeigst du, warum die beiden Regeln zu anderem Rat führen?',
    'Großmutter': 'Trennst du die Entwicklung des Embryos von ihrer Glaubensregel? Was bedeutet ihr Angebot für Lauras eigene Wahl?',
    'Vater': 'Unterscheidest du die gesetzliche Vorgabe vom persönlichen Rat? Was kann Laura nach dem Termin noch entscheiden?',
}
EXAMPLES = {
    'Mutter': 'Für mich hilft die Nachricht zum Teil. Laura kennt jetzt ein Hilfsangebot. Über ihre Möglichkeiten möchte sie noch mehr wissen.',
    'Freundin': 'Für mich hilft sie zum Teil. Die Ausbildung ist Laura wichtig. Ich würde noch fragen, wie sie die Ausbildung mit Kind fortsetzen könnte.',
    'Großmutter': 'Für mich hilft sie viel. Laura kann mit ihr reden und auch anders wählen. Für medizinische Fragen braucht sie noch eine andere Quelle.',
    'Vater': 'Für mich hilft sie viel. Laura findet eine Anlaufstelle. Dort kann sie nach beiden Wegen fragen.',
}


def judgment(person, level):
    prompts = {'Förder': 'Wähle dein Urteil. Verbinde eine Stelle mit einem Grund.',
               'ESA': 'Wähle einen Beleg und den passenden Grund. Erkläre dein Urteil kurz.',
               'MSA': 'Wäge ab: Was hilft Laura? Was fehlt ihr? Begründe dein Urteil.',
               'AHR': 'Was zählt für Laura mehr? Begründe dein Urteil. Prüfe auch eine andere Sicht.'}
    sample = EXAMPLES[person]
    if level == 'AHR':
        sample += ' ' + COUNTERS[person][1]
    return dict(kind='judgment', selfCheck=SELF_CHECK[person], heading=QUESTIONS[2], prompt=prompts[level],
                options=JUDGMENTS, anchors=ANCHORS[person], links=WEIGHTS[person],
                matchingLinks=[[0, 1], [0, 1]] if person == 'Vater' else [[0], [1]],
                counter=COUNTERS[person][0] if level == 'AHR' else '', results=RESULTS[person],
                hints=['Wähle zuerst, wie gut die Nachricht hilft.', 'Was hilft Laura gerade? Was fehlt ihr noch?',
                       'Lies „Geprüft“. Vergleiche das mit Lauras Wunsch, selbst zu entscheiden.',
                       ANCHORS[person][0]+' '+WEIGHTS[person][0]+' Wie wichtig ist dieser Grund für dein Urteil?',
                       CHAINS[person]+' '+sample+' Wähle dein Urteil und einen Beleg. Gib deinen Grund an. Tippe auf „Abschnitt beenden“.'])


def bank():
    cases = {}
    for pi, (person, message) in enumerate(SOURCE['nachrichten'].items()):
        by_level = {}
        for li, level in enumerate(LEVELS):
            tasks = [argument_map(person, level), dict(FACTS[person], heading=QUESTIONS[0])]
            if level == 'ESA':
                key, right, other, prompt = EVIDENCE[person]
                card = CARDS[key]
                target, distractor = (card['lines'][n-1] for n in [right, other])
                q = check(prompt, [3] if person == 'Vater' else [1], [(target, f'Zeile {right} belegt genau diese Aussage.'),
                                         (distractor, f'Lies Zeile {right} der Fachkarte. Vergleiche sie mit der Frage.')],
                          card=[key, sorted([right, other])], look=f'Lies „{card["title"]}“, Zeile {right}.',
                          clue=target, meaning='Wähle den Satz, der genau den gesuchten Punkt belegt.')
                tasks.append(dict(q, heading=QUESTIONS[0]))
            tasks.append(dict(WISHES[person], heading=QUESTIONS[1]))
            if li >= 2:
                prompt, ids, target, other, why = DEEP[person]
                q = check(prompt, ids, [(target, why), (other, f'Lies Zeile {ids[-1]} noch einmal. {why}')],
                          wishes=[5], card=['beratung', [2, 3]] if person=='Vater' else None,
                          look=f'Lies {person}, Zeilen {", ".join(map(str, ids))}.',
                          clue=why, meaning='Unterscheide, was die Stelle sagt und was man daraus schließen kann.')
                tasks.append(dict(q, heading=QUESTIONS[1]))
            tasks.append(judgment(person, level))
            for i, task in enumerate(tasks):
                if task['kind'] == 'check':
                    task['hints'] = [*task['hints'][:-1], CHAINS[person]+' '+task['hints'][-1]]
                    # Keep the key from occupying the same place across a teaching path.
                    shift = (pi + li + i) % len(task['options'])
                    task['options'] = task['options'][shift:] + task['options'][:shift]
            by_level[level] = tasks
        cases[person] = dict(message=message, sections=[person+' 1 – Argumenten-Check', person+' 2 – Nachricht prüfen'],
                             levels=by_level)
    return dict(lead='Wie gut helfen die Nachrichten Laura?', context='Laura ist 19 Jahre alt und macht eine Ausbildung.',
                laura=SOURCE['laura'], levels=LEVELS, categories=CATEGORIES, questions=QUESTIONS, helps=HELP,
                sources=SOURCES, cards=CARDS, verdictUI=VERDICT_UI, cases=cases)
