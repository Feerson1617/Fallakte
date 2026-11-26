"""Inhaltliche Mindestbelege je nummeriertem Feld vor der jeweiligen Papierphase.

Geprüft werden nur tatsächlich gelesene Pflichtansichten mit Info oder richtiger
Rückmeldung. Eine Übereinstimmung allein auf der Musterkarte reicht nicht aus.
"""

# Die vier Gruppen entsprechen den vier Karten, die Zeilen den Feldern 1 bis 4.
# Die Spalten sind die im Browser geprüften Niveaus Förder, ESA, MSA und AHR.
BELEGE = (
    (
        ('Kunststoff ohne Latex', 'ohne Latex aus Kunststoff', 'ohne Latex, etwa aus Kunststoff', 'synthetische Kondome'),
        ('Spermien bleiben in der heilen Hülle', 'Hindernis für Spermien', 'hält Sperma zurück. Diese Barriere', 'heile Hülle hält Sperma zurück'),
        ('senkt das Risiko. Ein Teil der Haut bleibt frei', 'senkt das Risiko vieler STI. Haut bleibt frei', 'senkt das Risiko vieler STI. Ein Teil der Haut bleibt frei', 'Naturmembran bietet keinen gleichwertigen STI-Schutz'),
        ('von Anfang an ein neues Kondom', 'von Anfang an richtig sitzen', 'von Anfang an ein neues', 'von Anfang an eine Barriere'),
    ), (
        ('verhindern meist den Eisprung', 'hemmen meist den Eisprung', 'hemmt vor allem den Eisprung', 'hemmen vor allem den Eisprung'),
        ('Vor Infektionen beim Sex schützt die Pille nicht', 'schützen nicht vor STI', 'keine Barriere gegen Krankheitserreger', 'keine Barriere gegen Erreger'),
        ('regelmäßig nach Plan', 'regelmäßig nach Plan', 'Vergessene Tabletten können den Schutz verringern', 'Vergessene Tabletten können den Schutz mindern'),
        ('Verträglichkeit ist unterschiedlich', 'von Person zu Person verschieden', 'Verträglichkeit ist individuell', 'Verträglichkeit ist individuell'),
    ), (
        ('Spermien bewegen sich schlechter', 'können eine Eizelle schwerer befruchten', 'stört Bewegung und Befruchtungsfähigkeit', 'beeinträchtigt Bewegung und Befruchtungsfähigkeit'),
        ('Vor Infektionen schützt es nicht', 'keinen STI-Schutz', 'keine Barriere gegen Erreger', 'schützt nicht vor STI'),
        ('Tägliche Tabletten entfallen', 'ohne tägliche Einnahme', 'ohne tägliche Einnahme', 'braucht keine tägliche Einnahme'),
        ('Regelschmerzen können stärker werden', 'Blutung und Schmerzen können stärker werden', 'Stärkere Blutungen und Schmerzen sind möglich', 'Blutung und Schmerzen können stärker werden'),
    ), (
        ('Schleim am Gebärmutterhals zäher', 'Schleim am Gebärmutterhals wird zäher', 'Spermien kommen schwerer hindurch', 'für Spermien schwer durchlässig'),
        ('Vor Infektionen schützt sie nicht', 'Das schützt nicht vor STI', 'kein STI-Schutz', 'bietet keinen STI-Schutz'),
        ('Tägliche Tabletten entfallen', 'ohne tägliche Einnahme', 'ohne tägliche Einnahme', 'Ohne tägliche Einnahme'),
        ('Blutung und Schmerzen schwächer werden', 'Blutung und Schmerzen schwächer werden', 'Blutung und Schmerzen schwächer werden', 'Blutung und Schmerzen können abnehmen'),
    )
)

def abgleich(niveau, karten, gelesen):
    spalte = ('Foerder', 'ESA', 'MSA', 'AHR').index(niveau)
    protokoll = []
    assert len(gelesen) == len(karten) == len(BELEGE) == 4
    for karte, quellen, gruppe in zip(karten, gelesen, BELEGE):
        assert len(karte['felder']) == len(gruppe) == 4
        for feld, zeile in zip(karte['felder'], gruppe):
            beleg = zeile[spalte]
            quelle = next((quelle for quelle in quellen if beleg in quelle['text']), None)
            assert quelle, (niveau, karte['titel'], feld['nummer'], beleg)
            protokoll.append(dict(niveau=niveau, kapitel=karte['nummer'], feld=feld['nummer'],
                                  loesung=feld['wort'], lernbeleg=beleg, **quelle))
    return protokoll
