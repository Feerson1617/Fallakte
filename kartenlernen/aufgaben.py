"""Unterrichtsinhalte des eigenständigen Vorbereitungswegs. Feldreihenfolge wie im Druck."""
NIVEAUS = ('Foerder','ESA','MSA','AHR')
# Zwei kurze Bildseiten je Methode. Die Nummern binden jeden Lernbeleg an das Originalfeld.
# Sternchen markieren den fachlichen Kern, der im Browser hervorgehoben wird.
BILDER = [('huelle','kontakt'),('eisprung','einnahme'),('kupfer','kupferwahl'),('schleim','hormonwahl')]
TITEL = [('So wirkt das Kondom.','Schutz beim Sex.'),
         ('So wirkt die Kombinationspille.','Die Pille im Alltag.'),
         ('So wirkt die Kupferspirale.','Die Spirale im Alltag.'),
         ('So wirkt die Hormonspirale.','Die Spirale im Alltag.')]
# Diagnose, Rückmeldung und nächster Denkimpuls sind je Antwortalternative fest verbunden.
def wahl(abschnitt, ziel, frage, richtig, fehler, grund, impuls, starter):
    return dict(typ='wahl',abschnitt=abschnitt,ziel=ziel,frage=frage,passend=richtig,alternativen=[
        dict(text=text,muster=kategorie,erklaerung=antwort,impuls=hilfe) for text,kategorie,antwort,hilfe in fehler],
        grund=grund,impuls=impuls,starter=starter)

def frei(abschnitt,modell,frage,ziel):
    return dict(typ='text',abschnitt=abschnitt,modell=modell,frage=frage,ziel=ziel)

FRAGEN={
'Foerder':[
 wahl(1,'Barriere erkennen','Was hält ein heiles Kondom zurück?','Spermien',[('Den Eisprung','zyklus','Ein Kondom verändert den Eisprung nicht.','Was bleibt in der Hülle?')],'Die Hülle fängt Sperma mit Spermien auf.','Was fängt die Hülle auf?','In der Hülle bleiben …'),
 wahl(0,'Ausbleibenden Eisprung verstehen','Welche Zelle wird ohne Eisprung nicht frei?','Eine Eizelle',[('Spermien','zellen','Spermien entstehen nicht im Eierstock.','Welche Zelle verlässt sonst den Eierstock?')],'Beim Eisprung wird eine Eizelle frei. Ohne Eisprung wird sie nicht frei.','Was verlässt beim Eisprung den Eierstock?','Ohne Eisprung wird keine …'),
 wahl(0,'Wirkort des Kupfers erkennen','Was bewegt sich durch Kupfer schlechter?','Spermien',[('Die Eizelle','zellen','Kupfer stört vor allem die Spermien.','Wer bewegt sich zur Eizelle?')],'Spermien kommen schlechter zur Eizelle.','Wer muss zur Eizelle gelangen?','Das Kupfer stört …'),
 wahl(4,'Mögliche Veränderung von Schmerzen erkennen','Hormonspirale: Was kann mit den Regelschmerzen passieren?','Sie können schwächer werden.',[('Sie hören sicher auf.','garantie','Nur bei manchen werden die Schmerzen schwächer.','Ist eine Besserung sicher?')],'Bei manchen tut die Regel weniger weh.','Suche das Wort „können“.','Später können die Schmerzen …')],
'ESA':[
 wahl(2,'Ein verbleibendes Infektionsrisiko erklären','Warum kann man sich auch mit Kondom beim Sex anstecken?','Ein Teil der Haut bleibt frei.',[('Die Hülle bedeckt die gesamte Haut.','haut','Das Kondom bedeckt nur einen Teil der Haut.','Wo kann es noch Hautkontakt geben?')],'Über freie Haut können manche Erreger von Mensch zu Mensch kommen.','Welche Haut berührt sich noch?','Ein Risiko bleibt, weil …'),
 wahl(3,'Persönliche Verträglichkeit unterscheiden','Eine Person verträgt die Pille gut. Wie können andere Menschen reagieren?','Andere Menschen können anders reagieren.',[('Alle vertragen die gleiche Pille gleich gut.','erfahrung','Die Erfahrung gilt für diese eine Person.','Wer hat die Pille genommen?')],'Jeder Körper reagiert anders.','Für wen gilt die Erfahrung?','Für eine andere Person …'),
 wahl(4,'Hormonfreiheit und Beschwerden unterscheiden','Kupferspirale ohne Hormone: Was kann mit Regelschmerzen passieren?','Sie können stärker werden.',[('Ohne Hormone bleiben die Schmerzen gleich.','hormonfrei','Auch bei einer hormonfreien Spirale können Schmerzen zunehmen.','Können die Schmerzen stärker werden?')],'Auch ohne Hormone kann die Regel mehr wehtun.','Kann eine hormonfreie Spirale Beschwerden verändern?','Unter Kupfer können …'),
 wahl(0,'Folge des zähen Schleims verstehen','Was bewirkt zäher Schleim am Gebärmutterhals?','Spermien kommen schwerer hindurch.',[('Die Eizelle verlässt den Eierstock nicht.','zyklus','Hier verändert sich der Schleim am Gebärmutterhals.','Welche Zellen müssen dort hindurch?')],'Der zähere Schleim erschwert Spermien den Weg.','Wer muss durch den Schleim?','Der Schleim erschwert …')],
'MSA':[
 wahl(2,'Grenze der Barriere erklären','Warum kann man sich trotz heilem Kondom beim Sex anstecken?','Manche Erreger gelangen über freie Haut zum anderen Menschen.',[('Erreger müssen mit Sperma durch die Hülle gelangen.','haut','Manche Erreger werden auch bei Hautkontakt übertragen.','Welche Haut bleibt außerhalb der Hülle?')],'Die Barriere bedeckt nur einen Teil der Haut.','Welche Übertragung braucht kein Sperma?','Ein Restrisiko bleibt, weil …'),
 frei(0,'pille','Wie verhindert die Pille eine Befruchtung? Erkläre mit Eisprung und Eizelle.','Ausbleibenden Eisprung mit fehlender befruchtbarer Eizelle verbinden.'),
 wahl(4,'Hormonfreiheit und individuelle Wirkung trennen','Die Kupferspirale enthält keine Hormone. Was bedeutet das für Regelschmerzen?','Sie können trotzdem stärker werden.',[('Ohne Hormone können Schmerzen nicht zunehmen.','hormonfrei','Auch ohne Hormone können Blutung und Schmerzen stärker werden.','Welche Veränderung beschreibt die Karte?')],'Auch eine hormonfreie Methode kann Regelschmerzen verstärken.','Was ist trotz Hormonfreiheit möglich?','Hormonfrei bedeutet hier …'),
 frei(0,'schleim','Warum kommen Spermien mit der Hormonspirale schwerer zur Eizelle?','Veränderte Schleimbeschaffenheit mit erschwertem Durchtritt verbinden.')],
'AHR':[
 frei(2,'haut','Wie gelangen manche Erreger trotz heilem Kondom zum anderen Menschen?','Grenzen der bedeckten Fläche mit Übertragung bei Hautkontakt verbinden.'),
 wahl(3,'Grenzen einer Einzelerfahrung begründen','Eine Person verträgt die Pille gut. Was lässt sich daraus für andere Menschen schließen?','Andere können auf die gleiche Pille anders reagieren.',[('Alle Menschen vertragen die gleiche Pille genauso gut.','erfahrung','Zwei Körper können auf die gleiche Pille anders reagieren.','Welche Person wurde tatsächlich beobachtet?')],'Die Arztpraxis berät zur persönlichen Verträglichkeit.','Worüber gibt eine einzelne Erfahrung Auskunft?','Die Erfahrung zeigt … Offen bleibt …'),
 frei(0,'kupfer','Der Eisprung findet statt. Wie erschwert die Kupferspirale trotzdem die Befruchtung?','Eingeschränkte Spermienbewegung mit erschwerter Befruchtung verbinden.'),
 wahl(4,'Grenzen einer Vorhersage prüfen','Mit der Hormonspirale kommt die Blutung anfangs unregelmäßig. Was sagt das über spätere Schmerzen?','Die Schmerzen können nachlassen. Sicher ist das noch nicht.',[('Die unregelmäßige Blutung zeigt schon, dass die Schmerzen nachlassen.','garantie','Die erste Blutung sagt wenig über spätere Schmerzen.','Welche spätere Veränderung ist nur möglich?')],'Bei manchen lassen die Schmerzen nach. Bei anderen bleiben sie.','Welche Beobachtung betrifft nur den Anfang?','Später ist möglich …')]
}

INFOHILFE = [[['Was hält die heile Hülle zurück?', 'Die Hülle fängt Sperma auf. Es gibt geeignete Hüllen ohne Latex.'],
  ['Suche die freie Haut im Bild.',
   'Manche Erreger gehen bei Hautkontakt über. Das Kondom muss von Anfang an sitzen.']],
 [['Was fehlt rechts im Bild?', 'Ohne Eisprung wird keine Eizelle frei. Erreger können trotzdem übertragen werden.'],
  ['Was zeigt die Lücke im Kalender?',
   'Eine vergessene Tablette kann den Schutz mindern. Nicht alle vertragen die Pille gleich.']],
 [['Suche die Spermien nahe am Kupfer.', 'Kupfer stört Spermien. Gegen Erreger entsteht keine Barriere.'],
  ['Was bedeutet der Pfeil nach oben?',
   'Ohne tägliche Tablette wirkt die Spirale lange. Regelschmerzen können zunehmen.']],
 [['Suche den Schleim am Ausgang der Gebärmutter.',
   'Zäher Schleim erschwert Spermien den Weg. Vor Infektionen schützt er nicht.'],
  ['Was bedeutet der Pfeil nach unten?', 'Die Spirale wirkt lange. Später können Blutung und Schmerzen nachlassen.']]]

# Zweite Hilfe zur Erklärung des Bildes. Alle Niveaus erreichen sie mit derselben Taste.
BILDDETAIL={
 'ESA':(('Auch eine geeignete Hülle ohne Latex hält Sperma zurück.','Neben der bedeckten Fläche bleibt Haut frei. Dort können Erreger übertragen werden.'),
        ('Auf der rechten Seite wird keine Eizelle frei.','Der Kalender zeigt die Einnahme. Ob jemand Übelkeit bekommt, zeigt er nicht.'),
        ('Bewegen sich Spermien schlechter, erreichen sie die Eizelle schwerer.','Der Pfeil zeigt eine Möglichkeit. Nicht bei allen wird die Blutung stärker.'),
        ('Der Schleim liegt auf dem Weg der Spermien zur Eizelle.','Blutungen können am Anfang unregelmäßig sein und später nachlassen.')),
 'MSA':(('Barriere bedeutet hier, dass die heile Hülle Sperma zurückhält.','Außerhalb der Hülle können sich Hautstellen berühren.'),
        ('Vergleiche die Eierstöcke. Nur links wird eine Eizelle frei.','Ein Tag fehlt. Dann kann der Schutz sinken. Übelkeit zeigt der Kalender nicht.'),
        ('Kupfer beeinträchtigt die Spermien. Erreger werden dadurch nicht aufgehalten.','Der Pfeil betrifft die Blutung. Auch Regelschmerzen können zunehmen.'),
        ('Suche die enge Stelle am Gebärmutterhals. Dort wird der Schleim zäher.','Eine schwächere Blutung ist möglich. Der Pfeil zeigt, was passieren kann.')),
 'AHR':(('Eine Hülle kann Sperma zurückhalten. Beim Schutz vor Ansteckung zählt auch das Material.','Das Modell zeigt freie Haut neben der Hülle. Manche Erreger brauchen kein Sperma.'),
        ('Ohne freie Eizelle kann keine Befruchtung stattfinden. Eine Barriere entsteht dabei nicht.','Gleiche Einnahme bedeutet nicht, dass zwei Körper gleich reagieren.'),
        ('Der Eisprung kann stattfinden. Die Bewegung der Spermien ist beeinträchtigt.','Auch ohne Hormone können Blutung und Schmerzen stärker werden.'),
        ('Das Modell zeigt den Weg der Spermien durch den Schleim. Es zeigt keine Erregersperre.','Der Pfeil steht für eine mögliche Abnahme, nicht für eine sichere Linderung.'))
}
