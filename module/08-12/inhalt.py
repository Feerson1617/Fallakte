"""Authoring source for the second lesson. Export the same resolved bank to HTML and Work."""
import json
from pathlib import Path

SOURCE = json.loads(Path(__file__).with_name('nachrichten.json').read_text())
LEVELS = ['Förder', 'ESA', 'MSA', 'AHR']
QUESTIONS = ['Stimmt das?', 'Was möchte Laura? Geht die Nachricht darauf ein?', 'Hilft die Nachricht Laura? Warum?']
CATEGORIES = {
    'Fakt': 'Welche Aussage kannst du prüfen?',
    'Wert': 'Was ist der Person wichtig?',
    'Norm': 'Welche Regel nennt die Person?',
    'Folgerung': 'Was rät die Person Laura?',
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
    'evidence': 'Fachkarte', 'goal': 'Lauras Worte', 'rating': 'Wie gut hilft die Nachricht Laura?',
    'reason': 'Das kann dir beim Erklären helfen', 'own': 'Am iPad schreiben',
    'explain': 'Zeige die zwei Stellen.\nErkläre: Warum passt deine Antwort?',
    'solo': 'Nutze deinen Lernbogen. Schreibe dort deinen Grund oder sage ihn laut.',
    'write': 'Dein Grund', 'paper': 'Mein Grund steht auf dem Lernbogen.',
    'spoken': 'Ich habe meinen Grund gesagt.', 'done': 'Abschnitt beenden',
    'missing': 'Sage oder schreibe deinen Grund. Bestätige ihn oder gib ihn hier ein.',
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
    'Fakt': 'Ein Fakt ist eine Aussage, die du prüfen kannst.',
    'Wert': 'Ein Wert zeigt, was jemand wichtig findet.',
    'Norm': 'Eine Norm ist eine allgemeine Regel.',
    'Folgerung': 'Eine Folgerung ist hier der Rat an Laura.',
}
FIELD_LINKS = {
    'Mutter': ['Was im Körper passiert, kannst du auf der Fachkarte prüfen.', 'Die Sorge der Mutter zeigt, was ihr wichtig ist.', 'Die Regel gilt für die ganze Familie. Ihr Rat gilt für Laura.', 'Die Mutter bietet Hilfe an. Welchen Weg rät sie Laura deshalb?'],
    'Freundin': ['Ob eine Operation nötig ist, kannst du auf der Fachkarte prüfen.', 'Die Freundin denkt an das, was Laura nach der Schule vorhat.', 'Die Regel über Zukunftspläne gilt auch für andere Menschen.', 'Die Freundin denkt an die Ausbildung. Was rät sie Laura deshalb?'],
    'Großmutter': ['Wo der Embryo wächst, kannst du auf der Fachkarte prüfen.', 'Was liegt der Großmutter besonders am Herzen?', 'Die Regel kommt aus ihrem Glauben und gilt für sie allgemein.', 'Die Großmutter nennt ihre Glaubensregel. Was wünscht sie sich deshalb für Laura?'],
    'Vater': ['Was eine Beratungsstelle anbietet, kannst du auf der Fachkarte prüfen.', 'Der Vater möchte, dass Laura Bescheid weiß und selbst wählt.', 'Das Gesetz gilt für alle, die diese Beratungsregelung nutzen.', 'Das Gesetz nennt eine Pflicht. Was schlägt der Vater Laura als ersten Schritt vor?'],
}
FIELD_PLACES = {
    'Mutter': ['Lies den Anfang über den Abbruch.', 'Lies die Stelle über ihre Sorge.', 'Lies die Stellen über Familie und Hilfe.', 'Lies den Schluss nach dem Hilfsangebot.'],
    'Freundin': ['Lies den Anfang über Medikamente.', 'Lies die Stelle über Lauras Ausbildung.', 'Suche die allgemeine Regel über Zukunftspläne.', 'Lies ihren letzten Satz.'],
    'Großmutter': ['Suche die Stelle über den Embryo.', 'Was sagt sie über ungeborenes Leben?', 'Lies die Stelle über ihren Glauben.', 'Wo nennt sie einen Wunsch für Laura?'],
    'Vater': ['Suche die Auskunft über die Beratungsstelle.', 'Was sagt er über Wissen und Entscheiden?', 'Suche die Aussage über das Gesetz.', 'Was rät er Laura als ersten Schritt?'],
}
EXTRA_LINES = {'Mutter': 'Hier bietet sie Laura persönlich Hilfe an.',
               'Großmutter': 'Hier verspricht sie Laura Hilfe bei jeder Wahl.',
               'Vater': 'Hier sagt er: Laura entscheidet selbst.'}


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
        target = SOURCE['nachrichten'][person][line-1]
        hints = [f'Wähle für {name} eine Zeile.', FIELD_HELP[name], FIELD_PLACES[person][i], FIELD_LINKS[person][i],
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
    'Mutter': check('Wie kommt es zur Blutung?', [1], [
        ('Die Gebärmutter zieht sich zusammen. Gewebe wird ausgestoßen.', 'Die Kartenzeilen 2 und 3 beschreiben, wie sich die Gebärmutter zusammenzieht. Beim Ausstoßen von Gewebe kommt es zur Blutung.'),
        ('Die Blutung entsteht erst bei einer Operation.', 'Lies die Kartenzeilen 2 und 3. Das Medikament bewirkt, dass die Gebärmutter sich zusammenzieht und Gewebe ausstößt. Dabei blutet es.')
    ], card=['medizin', [2, 3, 4]], look='Lies Fachkarte „Abbruch mit Medikamenten“, Zeilen 2 bis 4.',
        clue='Das Medikament löst das Zusammenziehen aus. Gewebe verlässt die Gebärmutter.',
        meaning='Eine Blutung heißt: Blut tritt aus dem Körper aus.'),
    'Freundin': check('Wie passen die Aussagen über Blutungen und Operationen zusammen?', [1], [
        ('Ein Abbruch mit Medikamenten ist meist ohne Operation möglich. Beim Ausstoßen von Gewebe blutet es.', 'Kartenzeile 3 erklärt die Blutung beim Ausstoßen von Gewebe. Laut Kartenzeile 5 ist dieser Abbruch grundsätzlich ohne Operation möglich.'),
        ('Die Mutter beschreibt eine Operation. Die Freundin beschreibt einen anderen Weg.', 'Lies die Kartenzeilen 3 und 5. Beide Nachrichten beschreiben denselben Abbruch mit Medikamenten. Dabei blutet es. Meist ist keine Operation nötig.'),
        ('Blutungen zeigen, dass eine Operation nötig war.', 'Laut Kartenzeile 3 blutet es, wenn die Gebärmutter Gewebe ausstößt. Laut Kartenzeile 5 geht das grundsätzlich ohne Operation.')
    ], card=['medizin', [2, 3, 4, 5]], mother=[1], look='Vergleiche beide ersten Zeilen mit den Kartenzeilen 2 bis 5.',
        clue='Das Medikament bringt die Gebärmutter zum Zusammenziehen. Dafür ist grundsätzlich keine Operation nötig.',
        meaning='Bei einer Operation arbeiten Ärztinnen oder Ärzte mit Instrumenten im Körper.'),
    'Großmutter': check('Welche Aussage kannst du mit der Fachkarte prüfen?', [1, 3], [
        ('Nach der Einnistung wächst der Embryo in der Gebärmutter weiter.', 'Kartenzeile 2 beschreibt, wie sich der Embryo nach der Einnistung in der Gebärmutter weiterentwickelt.'),
        ('Die Entwicklung des Embryos beweist die Glaubensregel.', 'Kartenzeile 2 beschreibt, wo der Embryo wächst. Die Großmutter erklärt ihre Regel mit ihrem Glauben.')
    ], card=['entwicklung', [1, 2]], look='Lies auf der Karte „Am Anfang der Schwangerschaft“ die zweite Zeile.',
        clue='Die Karte erklärt, wo der Embryo wächst. Die Großmutter sagt selbst, woher ihre Regel kommt.',
        meaning='Bei der Einnistung verbindet sich der frühe Embryo mit der Schleimhaut der Gebärmutter.'),
    'Vater': check('Was stimmt über die Beratungsstelle?', [1, 3], [
        ('Sie informiert. Für die Beratungsregelung gilt: Die Stelle muss anerkannt sein. Bis zum Abbruch müssen mindestens drei Tage vergehen.',
         'Kartenzeile 1 nennt das Beratungsangebot. Nach den Kartenzeilen 2 und 3 muss die Stelle staatlich anerkannt sein. Die Beratung muss mindestens drei Tage vor dem Abbruch liegen.'),
        ('Jede Stelle reicht aus, wenn der Termin drei Tage vor dem Abbruch liegt.',
         'Lies Kartenzeile 2. Für die Beratungsregelung muss die Beratungsstelle staatlich anerkannt sein.')
    ], card=['beratung', [1, 2, 3]], look='Lies „Beratung und Gesetz“, Zeilen 1 bis 3.',
        clue='Unterscheide das Angebot der Stelle und die Vorgaben für die Beratungsregelung.',
        meaning='Anerkannt heißt hier: Der Staat hat die Stelle für diese Beratung zugelassen.'),
}

WISHES = {
    'Mutter': check('Was bietet die Mutter Laura? Was ist noch offen?', [2, 3, 4, 5], [
        ('Sie bietet Hilfe mit dem Kind an. Laura möchte erst beide Wege kennen.', 'Ihre Familienregel erklärt das Angebot. Laura darf trotzdem anders wählen.'),
        ('Das Hilfsangebot beantwortet schon, welcher Weg zu Laura passt.', 'Lies Lauras Worte. Ihr fehlen Informationen zu ihren Möglichkeiten.')
    ], wishes=[4, 5], look='Vergleiche die Zeilen 3 bis 5 der Mutter mit Lauras Worten.',
        clue='Mit einem Kind will die Mutter helfen. Laura hat noch keine Entscheidung getroffen.',
        meaning='Ein Angebot sagt, welche Hilfe Laura bekommen kann.'),
    'Freundin': check('Warum raten sie Laura zu verschiedenen Wegen?', [2, 3, 4], [
        ('Die Mutter rät zum Fortsetzen und bietet Hilfe an. Die Freundin rät wegen der Ausbildung zum Abbruch.',
         'Beide nennen in Zeile 3 ihre Regel.'),
        ('Eine der beiden muss sich beim Ablauf mit Medikamenten irren.',
         'Vergleiche die Regeln in Zeile 3 beider Nachrichten. Die medizinischen Aussagen passen zusammen.'),
        ('Der Ausbildungswunsch legt schon fest, was Laura tun soll.',
         'Lies Lauras Worte. Sie möchte die Ausbildung abschließen und selbst entscheiden.')
    ], wishes=[2, 5], mother=[2, 3, 5], look='Lies bei beiden die dritte Zeile und den Rat danach.',
        clue='Die Mutter nennt eine Familienregel. Die Freundin nennt eine Regel für Zukunftspläne.',
        meaning='Ein Rat sagt Laura, was sie aus Sicht der Person tun soll.'),
    'Großmutter': check('Was bietet sie Laura bei einer anderen Wahl an?', [3, 4, 5], [
        ('Sie bleibt bei Laura. Laura kann selbst entscheiden.', 'Ihr Wunsch und ihr Angebot stehen nebeneinander. Laura muss den Glauben nicht teilen.'),
        ('Ihre Unterstützung hängt davon ab, dass Laura ihren Glauben teilt.', 'Lies Zeile 5. Dort verspricht sie Hilfe bei jeder Wahl.')
    ], wishes=[4, 5], look='Vergleiche den Wunsch in Zeile 4 mit dem Versprechen in Zeile 5.',
        clue='Achte auf „egal wie du dich entscheidest“.', meaning='Hilfe kann auch heißen: Jemand bleibt bei dir und hört zu.'),
    'Vater': check('Was bringt der Termin Laura?', [2, 4, 5], [
        ('Sie kann sich informieren und danach selbst entscheiden.', 'Der Vater will, dass Laura gut informiert selbst entscheidet.'),
        ('Mit dem Termin entscheidet sie sich für einen Abbruch.', 'Lies Zeile 5 des Vaters und Kartenzeile 4. Das Ergebnis ist offen.')
    ], wishes=[4, 5], card=['beratung', [4, 5]], look='Lies seine letzte Zeile und Kartenzeile 4.',
        clue='Ein Rat zum Gespräch lässt die spätere Wahl offen.', meaning='Ergebnisoffen heißt: Laura kann nach dem Gespräch selbst wählen.'),
}

# Only the second question carries a deeper check. All four routes have the same positions.
DEPTH = {
    'Mutter': ('Welche Hilfe passt noch zur Regel der Mutter?', [3, 4, 5],
               'Sie könnte Laura auch zu einer Beratung begleiten. Das wäre ebenfalls Familienhilfe.',
               'Die Zusage in Zeile 4 gilt für ein Kind. Damit gilt auch die Familienregel nur für diesen Weg.',
               'Die Mutter bietet Hilfe mit dem Kind an. Ihre Regel lässt auch andere Hilfe zu.'),
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
              'Der Vater berichtet von einer Vorschrift. Darum ist die Stelle nur ein Fakt.',
              'Auch eine zitierte Vorschrift beschreibt eine Regel. Ihr Wortlaut lässt sich prüfen.'),
}
AHR_FRIEND = ('Können beide Regeln zugleich gelten? Müssen beide dann dasselbe raten?', [2, 3, 4],
              'Beides kann zählen. Je nachdem, was Laura braucht, können die Regeln verschiedene Wege stützen.',
              'Beides kann zählen. Wenn beide dieselben Regeln annehmen, müssen sie auch zum selben Weg raten.',
              'Beide Regeln können gelten. Wie wichtig jede Regel ist, hängt von Lauras Lage ab.')
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
# The fifth hint names real choices. The optional paragraph for the upper level
# reflects on the same reason, without putting another task in the shared prompt.
EXAMPLES = {
    'Mutter': ('Blutungen', 'richtige Informationen', 1, 'Laura kennt eine Folge. Ihr fehlen Infos zum anderen Weg.'),
    'Freundin': ('grundsätzlich ohne Operation', 'Ausbildung', 1, 'Laura kennt den Ablauf. Was er für ihre Ausbildung bedeutet, bleibt offen.'),
    'Großmutter': ('Einnistung', 'richtige Informationen', 2, 'Laura weiß, wo der Embryo wächst. Ihre Frage nach beiden Wegen bleibt offen.'),
    'Vater': ('Möglichkeiten und Hilfen', 'selbst entscheiden', 0, 'Laura kann Fragen stellen und danach selbst wählen.'),
}
# A changed information need, rather than a new planning exercise.
COUNTERS = {
    'Mutter': ('Laura kennt die Blutungen schon. Was hilft ihr an der Nachricht dann noch?', 'Die Blutung ist für sie nichts Neues. Das Hilfsangebot kann weiter zählen.'),
    'Freundin': ('Laura weiß schon, dass meist keine Operation nötig ist. Wie hilfreich ist der Rat dann?', 'Der Ablauf ist für sie nichts Neues. Sie braucht noch Infos zum anderen Weg.'),
    'Großmutter': ('Laura weiß schon, wo der Embryo wächst. Was hilft ihr an der Nachricht dann noch?', 'Die Entwicklung kennt sie schon. Das Angebot, bei ihr zu bleiben, kann helfen.'),
    'Vater': ('Laura kennt beide Wege schon. Was bringt ihr der Rat zur Beratung dann noch?', 'Die Wege kennt sie schon. Sie kann dort eigene Fragen stellen.'),
}
SELF_CHECK = {
    'Mutter': 'Was steht auf deiner Fachkarte? Was will Laura? Passt dein Grund zu deiner Einschätzung?',
    'Freundin': 'Was erfährt Laura über den Abbruch? Welche ihrer Aussagen hast du gewählt? Warum passt dein Grund?',
    'Großmutter': 'Was zeigt die Fachkarte zum Embryo? Welche Frage bleibt für Laura offen? Was bringt ihr das Angebot der Großmutter?',
    'Vater': 'Was kann eine Beratungsstelle tun? Was möchte Laura? Wie hilft ihr der Rat zum Termin?',
}


def judgment(person, level):
    key, facts, goals = PROOF[person]
    fact, wish, rating, reason = EXAMPLES[person]
    sample = (f'Beispiel: Wähle „{fact}“ und Lauras Wunsch „{wish}“.\n'
              f'„{JUDGMENTS[rating]}“ {reason}\n'
              'Sage den Grund. Tippe auf „Ich habe meinen Grund gesagt.“ und „Abschnitt beenden“.')
    task = dict(kind='judgment', heading=QUESTIONS[2],
                prompt='Wähle eine Information.\nWähle, was Laura möchte.\nErkläre deinen Grund.',
                options=JUDGMENTS, card=[key,facts], goals=goals, links=LINKS[person], selfCheck=SELF_CHECK[person],
                hints=['Wähle eine Stelle auf der Fachkarte. Wähle dann Lauras Worte.',
                       'Dein Grund erklärt, warum die Nachricht Laura viel, zum Teil oder wenig hilft.',
                       f'Lies auf der Fachkarte Zeile {facts[1] if person=="Großmutter" else facts[0]}. Lies dann Lauras Worte.',
                       'Die Fachkarte sagt … Laura möchte … Darum hilft ihr die Nachricht …',
                       sample])
    if level in ('MSA','AHR'):
        prompt, example = COUNTERS[person] if level=='AHR' else (
            'Was hilft Laura? Was fehlt ihr noch?',
            'Laura kennt das Angebot. Ihre Fragen sind damit noch offen.' if person=='Vater' else reason)
        task['extension'] = dict(prompt=prompt, hints=[
            'Ergänze deinen Grund um einen Satz.',
            'Was Laura schon weiß, kann ändern, wie hilfreich eine Nachricht ist.' if level=='AHR'
            else 'Eine Grenze heißt hier: Diese Frage bleibt für Laura offen.',
            f'Lies deine Kartenstelle und Lauras Worte noch einmal. Achte auf den Rat von {person}.',
            'Wenn Laura das schon weiß, hilft ihr noch …' if level=='AHR'
            else 'Sie erfährt … Aber sie weiß noch nicht …',
            f'Ein möglicher Zusatz: {example} Sage oder schreibe den Satz zu deinem Grund.'])
    return task


def bank():
    cases = {}
    for pi, (person, message) in enumerate(SOURCE['nachrichten'].items()):
        by_level = {}
        for level in LEVELS:
            fact = dict(FACTS[person], heading=QUESTIONS[0])
            key, lines = fact['card']
            fact['prompt'] = (f'Lies in der Fachkarte „{CARDS[key]["title"]}“ die Zeilen {lines[0]} bis {lines[-1]}. '
                              + fact['prompt'])
            wishes = dict(WISHES[person], heading=QUESTIONS[1])
            if level in LEVELS[2:]:
                special = person=='Freundin' and level=='AHR'
                prompt, ids, target, other, why = AHR_FRIEND if special else DEPTH[person]
                q = check(prompt, ids, [(target, why), (other, 'Lies die Stelle noch einmal. Welche Regel gilt hier?')],
                          look=f'Lies {person}, Zeile {ids[0]} bis {ids[-1]}.' if len(ids)>1 else f'Lies {person}, Zeile {ids[0]}.',
                          clue=why, meaning='Eine Regel sagt, was allgemein gelten soll. Ein Rat gilt hier für Laura.' if person!='Vater' else 'Ein Fakt ist prüfbar. Eine Norm sagt, was gelten soll.')
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
                laura=SOURCE['laura'],lauraAbsaetze=SOURCE['lauraAbsaetze'],levels=LEVELS,categories=CATEGORIES,questions=QUESTIONS,helps=HELP,
                sources=SOURCES,cards=CARDS,verdictUI=VERDICT_UI,cases=cases)
