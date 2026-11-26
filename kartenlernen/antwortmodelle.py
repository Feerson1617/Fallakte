"""Semantische Teilziele und Schülertexte für alle lokalen Freitextmodelle."""
def modell(teile,impulse,starter,beispiel,fehler):
    return dict(teile=teile,impulse=impulse,starter=starter,beispiel=beispiel,fehler=fehler)

MODELLE={
'pille':modell(['Die Pille hemmt den Eisprung.','Es fehlt eine freie, befruchtbare Eizelle.'],
 ['Was passiert mit dem Eisprung?','Welche Zelle fehlt dann für die Befruchtung?'],
 'Die Pille hemmt … Dadurch fehlt …','Die Pille hemmt den Eisprung. Dadurch wird keine Eizelle zur Befruchtung frei.',
 {'zyklus':'Unter der Pille bleibt der Eisprung meist aus.','eizelle':'Ohne Eisprung wird keine befruchtbare Eizelle frei.','spermien':'Die Pille wirkt vor allem auf den Eisprung.'}),
'schleim':modell(['Der Schleim am Gebärmutterhals wird zäher.','Spermien kommen schwerer durch den Schleim.'],
 ['Was verändert sich am Schleim?','Was bedeutet zäherer Schleim für die Spermien?'],
 'Der Schleim wird … Dadurch können Spermien …','Der Schleim wird zäher. Dadurch kommen Spermien schwerer hindurch.',
 {'dichte':'Der Schleim wird zäher und damit schwerer durchlässig.','weg':'Durch zähen Schleim gelangen Spermien schwerer hindurch.','zyklus':'Entscheidend ist der Schleim am Gebärmutterhals.'}),
'haut':modell(['Ein Teil der Haut bleibt unbedeckt.','Erreger können bei Hautkontakt übertragen werden.'],
 ['Welche Haut bedeckt das Kondom?','Wie können sich Erreger an diesen Stellen übertragen?'],
 'Das Kondom bedeckt … Bei Hautkontakt können …','Ein Teil der Haut bleibt frei. Dort können Erreger bei Hautkontakt übertragen werden.',
 {'flaeche':'Das Kondom bedeckt nur einen Teil der Haut.','kontakt':'Manche Erreger können durch Hautkontakt übertragen werden.','sperma':'Nicht alle Erreger brauchen Sperma zur Übertragung.'}),
'kupfer':modell(['Kupfer stört die Bewegung der Spermien.','Die Spermien erreichen oder befruchten die Eizelle schwerer.'],
 ['Was verändert Kupfer an den Spermien?','Was bedeutet ihre geringere Beweglichkeit für die Befruchtung?'],
 'Die Spermien bewegen sich … Dadurch können sie die Eizelle …','Kupfer bremst Spermien. Dadurch erreichen und befruchten sie die Eizelle schwerer.',
 {'bewegung':'Kupfer beeinträchtigt die Beweglichkeit der Spermien.','befruchtung':'Die Befruchtung wird dadurch erschwert.','zyklus':'Kupfer wirkt auf Spermien. Der Eisprung kann stattfinden.','schleim':'Der zähere Schleim gehört zur Hormonspirale.'})
}

# Lehrkraftvertrag und Oberfläche verwenden dieselben Teilziele und Denkimpulse.
# Ein Kern kann in einem Satz, als geordnete Stichworte oder durch zwei Sätze belegt sein.
DETAILS={
 'pille':dict(beziehung='Eisprung bleibt aus → keine befruchtbare Eizelle verfügbar.',
    alternativ='Auch die ausbleibende Freisetzung aus dem Eierstock kann den Zusammenhang erklären.',
    vereinfachung='Ei für Eizelle, zwei kurze Stichworte mit Richtungspfeil.',
    zusatz='Hormonnamen und Angaben zum Einnahmeplan sind entbehrlich.',
    einschraenkung='Die Pille hemmt den Eisprung meist. „Nicht immer“ ist keine Verneinung der üblichen Wirkung.',
    bild='eisprung',verknuepfen='Was fehlt für die Befruchtung, wenn der Eisprung ausbleibt?',
    fragen={'zyklus':'Wird der Eisprung meist gehemmt oder ausgelöst?', 'eizelle':'Welche Eizelle könnte ohne Eisprung befruchtet werden?', 'spermien':'Wo wirkt die Pille: am Eisprung oder an den Spermien?'}),
 'schleim':dict(beziehung='Zäherer Schleim am Gebärmutterhals → erschwerter Weg der Spermien.',
    alternativ='Eine Erklärung als erschwerter Durchtritt durch den verdickten Schleim genügt.',
    vereinfachung='„Dicker“ für zäher, „schlechter durchkommen“ für erschwerten Durchtritt.',
    zusatz='Der Name Gestagen ist entbehrlich.',einschraenkung='Erschwerter Durchtritt bedeutet keine absolute Undurchlässigkeit.',
    bild='schleim',verknuepfen='Warum kommen Spermien durch zäheren Schleim schwerer hindurch?',
    fragen={'dichte':'Wird der Schleim zäher oder dünner?', 'weg':'Kommen Spermien durch zähen Schleim leichter oder schwerer?', 'zyklus':'Was verändert die Hormonspirale am Gebärmutterhals?'}),
 'haut':dict(beziehung='Die Hülle bedeckt nur einen Teil der Haut → Erreger können bei Kontakt an freien Stellen übertragen werden.',
    alternativ='Ansteckung an unbedeckten Hautstellen kann beide Teilziele in einem Satz ausdrücken.',
    vereinfachung='„Keime“ und „sich anstecken“ sind zulässig.',
    zusatz='Das Material der Hülle ist für diese Erklärung entbehrlich.',
    einschraenkung='Das gilt für manche Erreger. Die Hülle kann zugleich intakt sein.',
    bild='kontakt',verknuepfen='Wie können Erreger an den freien Hautstellen übertragen werden?',
    fragen={'flaeche':'Welche Haut bleibt neben dem Kondom frei?', 'kontakt':'Was kann passieren, wenn sich freie Hautstellen berühren?', 'sperma':'Welche Übertragung braucht kein Sperma?'}),
 'kupfer':dict(beziehung='Kupfer beeinträchtigt Spermien → das Erreichen oder Befruchten der Eizelle ist erschwert.',
    alternativ='Die verminderte Befruchtungsfähigkeit oder der erschwerte Weg zum Ei können als Folge dienen.',
    vereinfachung='„Langsamer schwimmen“ für geringere Beweglichkeit.',
    zusatz='Der Begriff Kupferionen und eine Erklärung des Eisprungs sind entbehrlich.',
    einschraenkung='Der Eisprung kann stattfinden. Die Wirkung auf Spermien erschwert die Befruchtung.',
    bild='kupfer',verknuepfen='Wie wirkt sich die geringere Beweglichkeit auf die Befruchtung aus?',
    fragen={'bewegung':'Schwimmen Spermien unter dem Einfluss von Kupfer besser oder schlechter?', 'befruchtung':'Erreichen gebremste Spermien die Eizelle leichter oder schwerer?', 'zyklus':'Auf welche Zellen wirkt Kupfer?', 'schleim':'Was beeinflusst Kupfer an den Spermien?'})
}
for name,details in DETAILS.items():
    MODELLE[name].update(details)

# Zwei kurze Vergleichsfragen für den freiwilligen Abgleich mit dem eigenen Entwurf.
for name,(vergleich,zuerst) in {
    'pille':('Bleibt der Eisprung aus? Fehlt dadurch die Eizelle?', 'Was passiert zuerst mit dem Eisprung?'),
    'schleim':('Wird der Schleim zäher? Kommen Spermien schwerer hindurch?', 'Was ändert sich zuerst am Schleim?'),
    'haut':('Bleibt Haut frei? Können sich dort Erreger übertragen?', 'Welche Haut bleibt beim Kondom frei?'),
    'kupfer':('Bewegen sich Spermien schlechter? Erreichen oder befruchten sie das Ei schwerer?', 'Was passiert zuerst mit den Spermien?')
}.items():
    MODELLE[name].update(vergleich=vergleich,zuerst=zuerst)
