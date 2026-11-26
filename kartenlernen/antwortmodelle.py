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
