"""Eine Textquelle für Bildschirm, Schreibfelder, Druck und Work. *…* ist ein Schreibfeld."""
NAMEN = ('Kondom', 'Kombinationspille', 'Kupferspirale', 'Hormonspirale')
BEZUG = ('zu Kondomen', 'zur Kombinationspille', 'zur Kupferspirale', 'zur Hormonspirale')
TITEL = (
    ('Kondome ohne Latex', 'Die Hülle hält Sperma zurück', 'Ansteckung über die Haut', 'Ein neues Kondom für jeden Sex', 'Die Regel bleibt gleich'),
    ('Die Pille bremst den Eisprung', 'Kein Schutz vor Ansteckung', 'Die Pille nach Plan nehmen', 'Jeder Körper reagiert anders', 'Regelschmerzen können nachlassen'),
    ('Kupfer bremst Spermien', 'Kein Schutz vor Ansteckung', 'Schutz ohne tägliche Tablette', 'Du entscheidest über die Spirale', 'Regelschmerzen können zunehmen'),
    ('Schleim bremst Spermien', 'Kein Schutz vor Ansteckung', 'Schutz ohne tägliche Tablette', 'Du entscheidest über die Spirale', 'Regelschmerzen können nachlassen'),
)
ARZTPRAXIS = 'Starke Schmerzen ohne klare Ursache? Lass sie in der Arztpraxis prüfen.'
EINSETZEN = 'Die Arztpraxis prüft, ob die Spirale zu dir passt. Du entscheidest. Nur mit deinem Ja setzt sie die Spirale in die Gebärmutter ein. Das kann wehtun.'
PEARL = 'So viele von 100 Frauen werden schwanger, wenn sie ein Jahr so verhüten. Kleine Zahl → seltener schwanger. Der Wert sagt nichts über Ansteckung beim Sex.'
POSITION = ((0,1,2,3),(0,1,2,3),(0,1,2,4),(0,1,2,4))


def karte(niveau, index, vorlage):
    einfach = niveau == 'Foerder'
    vertieft = niveau in ('MSA','AHR')
    # Der kurze Kernsatz erscheint vor dem Schreiben. Auf der Karte folgen die nötigen Einzelheiten.
    if index == 0:
        kern = ['Allergie gegen Latex? Es gibt Kondome aus *Kunststoff*.',
                'Die heile Hülle hält *Spermien* zurück. Das sind Samenzellen im Sperma.',
                'Manche Erreger gehen beim Sex über *freie Haut* von Mensch zu Mensch.',
                'Bei jedem Sex ein *neues Kondom* benutzen. Gleich von Anfang an.']
        zusatz = ['Latex ist ein Material aus Gummi. Auf der Packung steht, ob das Kondom geeignet ist.',
                  'Das Kondom muss gut sitzen. Es wirkt ohne Hormone.',
                  'Ein geeignetes Kondom senkt das Risiko für viele Infektionen beim Sex. Kondome aus Tierdarm schützen davor nicht zuverlässig.',
                  'Es kann reißen oder abrutschen. Dann schützt es schlechter.']
        if not einfach: zusatz[0] += ' Ein Beispiel für Kunststoff ist Polyurethan.'
        if vertieft: zusatz[0] += ' Ein anderer Kunststoff ist Polyisopren.'
        if vertieft: zusatz[1] = 'Diese Hülle ist eine Barriere. Sitzt sie richtig, kommt kein Sperma in die Scheide. Ohne Hormone.'
        extra = 'Das Kondom verändert die Regel nicht. '+ARZTPRAXIS
    elif index == 1:
        kern = ['Die Pille verhindert meist den *Eisprung*. Dann wird keine Eizelle frei.',
                'Die Pille bietet *keinen Schutz* vor Ansteckung beim Sex.',
                'Die Pille *nach Plan* nehmen. Eine Pille vergessen → der Schutz vor Schwangerschaft kann sinken.',
                'Jeder Körper reagiert *anders*. Manchen wird von der Pille übel.']
        zusatz = ['Ohne freie Eizelle gibt es keine Befruchtung. Die Pille enthält zwei Hormone.',
                  'Die Hormone halten keine Krankheitserreger auf.', '',
                  'Eine Freundin verträgt sie gut? In der Arztpraxis klärst du, ob sie auch zu dir passt.']
        if not einfach: zusatz[0] += ' Sie heißen Östrogen und Gestagen.'
        if vertieft: zusatz[3] += ' Selten bildet sich ein Blutgerinnsel. Dabei verklumpt Blut in einem Gefäß.'
        extra = 'Blutung und Schmerzen können schwächer werden. '+ARZTPRAXIS
    elif index == 2:
        kern = ['Kupfer bremst *Spermien*. Diese Samenzellen erreichen und befruchten die Eizelle schwerer.',
                'Kupfer bietet *keinen Schutz* vor Ansteckung beim Sex.',
                'Die Spirale schützt lange vor Schwangerschaft. Du brauchst *keine Tablette*.',
                'Blutung und Regelschmerzen können *stärker* werden.']
        zusatz = ['Die Kupferspirale wirkt ohne Hormone.', 'Kupfer hält Krankheitserreger nicht auf.',
                  'Der Schutz ist sehr zuverlässig. Die Arztpraxis prüft, ob die Spirale richtig sitzt.', ARZTPRAXIS]
        if vertieft: zusatz[0] += ' Der Eisprung kann weiter stattfinden.'
        if not einfach: zusatz[2] += ' Wie lange sie wirkt, hängt vom Modell ab.'
        extra = EINSETZEN
    else:
        kern = ['Der Schleim unten an der Gebärmutter wird *zäher*. Spermien kommen schwerer durch.',
                'Der Schleim bietet *keinen Schutz* vor Ansteckung beim Sex.',
                'Die Spirale schützt lange vor Schwangerschaft. Du brauchst *keine Tablette*.',
                'Später können Blutung und Regelschmerzen *schwächer* werden.']
        zusatz = ['Dort ist der Gebärmutterhals. Ein Hormon aus der Spirale macht den Schleim dickflüssig.',
                  'Erreger können beim Sex weitergegeben werden.',
                  'Der Schutz ist sehr zuverlässig. Die Arztpraxis prüft, ob die Spirale richtig sitzt.',
                  'Am Anfang kann die Blutung unregelmäßig sein. '+ARZTPRAXIS]
        if not einfach: zusatz[0] += ' Das Hormon heißt Gestagen.'
        if vertieft: zusatz[0] += ' Die Pille hemmt vor allem den Eisprung.'
        extra = EINSETZEN
    sections, fields = [], []
    for s, heading in enumerate(TITEL[index]):
        if s in POSITION[index]:
            j = POSITION[index].index(s)
            left, word, right = kern[j].split('*')
            rest = (' '+zusatz[j]) if zusatz[j] else ''
            template = left+'{'+str(j+1)+'}'+right+rest
            text = left+word+right+rest
            fields.append(dict(nummer=j+1,wort=word,titel=heading))
        else:
            template = text = extra
        sections.append(dict(titel=heading,lueckentext=template,volltext=text))
    return dict(titel=NAMEN[index],bezug=BEZUG[index],nummer=index+1,seite='Vorderseite' if index<2 else 'Rückseite',
                position='oben' if index%2==0 else 'unten',ueberschrift=f'{index+1} – {NAMEN[index]}',felder=fields,
                texte=sections,pearl=vorlage['pearlIndex'],pearl_erklaerung=PEARL),kern
