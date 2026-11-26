"""Unterrichtsinhalte des eigenständigen Vorbereitungswegs. Feldreihenfolge wie im Druck."""
NIVEAUS = ('Foerder','ESA','MSA','AHR')
# Zwei kurze Bildseiten je Methode. Die Nummern binden jeden Lernbeleg an das Originalfeld.
# Sternchen markieren den fachlichen Kern, der im Browser hervorgehoben wird.
BILDER = [('huelle','kontakt'),('eisprung','einnahme'),('kupfer','kupferwahl'),('schleim','hormonwahl')]
TITEL = [('Wie hält das Kondom Sperma zurück?','Wann schützt das Kondom?'),
         ('Was bewirkt die Kombinationspille?','Was ist bei der Pille wichtig?'),
         ('Was macht das Kupfer?','Was kann sich bei der Regel ändern?'),
         ('Was verändert die Hormonspirale?','Was kann sich bei der Regel ändern?')]
INFO = {
'Foerder': [
 ('Bei Latexallergie gibt es geeignete Kondome *ohne Latex*.','Die heile Hülle fängt Sperma auf. Sie hält *Spermien* zurück.','Das *Risiko* für viele Infektionen beim Sex sinkt. Haut bleibt frei.','Benutze bei jedem Sex *von Anfang an* ein neues Kondom.'),
 ('Die Hormone verhindern meist den *Eisprung*. Dann wird keine Eizelle frei.','Die Pille bietet *keinen* Schutz vor Infektionen beim Sex.','Nimm die Pille *regelmäßig* nach Plan.','Menschen vertragen die Pille *unterschiedlich*. Manche bekommen Übelkeit.'),
 ('Kupfer stört *Spermien*. Sie bewegen sich schlechter und können die Eizelle schwerer befruchten.','Kupfer bietet *keinen* Schutz vor Infektionen beim Sex.','Die Spirale wirkt lange. *Tägliche Tabletten* sind nicht nötig.','Blutung und Regelschmerzen können *stärker* werden.'),
 ('Ein Hormon macht den Schleim am Gebärmutterhals *zäher*. Spermien kommen schwerer durch.','Der Schleim schützt *nicht* vor Infektionen beim Sex.','Die Spirale wirkt lange. *Tägliche Tabletten* sind nicht nötig.','Später können Blutung und Schmerzen *schwächer* werden.')],
'ESA': [
 ('Bei Latexallergie gibt es geeignete Kondome *ohne Latex* aus Kunststoff.','Eine heile Hülle hält *Spermien* zurück.','Bei sexuell übertragbaren Infektionen (STI) bleibt ein *Restrisiko*. Nicht alle Haut ist bedeckt.','Ein neues Kondom muss bei jedem Sex *von Anfang an* sitzen.'),
 ('Die Hormone hemmen meist den *Eisprung*. Ohne freie Eizelle gibt es keine Befruchtung.','Die Pille hält keine Erreger zurück. Sie bietet *keinen STI-Schutz*.','Die Pille *regelmäßig* nach Plan nehmen. Vergessen kann den Schutz mindern.','Menschen vertragen sie *unterschiedlich*. Eigene Beschwerden ärztlich klären.'),
 ('Kupfer stört die Bewegung und die *Befruchtungsfähigkeit* der Spermien.','Es entsteht *kein STI-Schutz*. Kupfer hält keine Erreger zurück.','Die Spirale wirkt lange ohne *tägliche Einnahme*.','Blutung und Regelschmerzen können *stärker* werden.'),
 ('Ein Hormon macht den Schleim am Gebärmutterhals *zäher*. Spermien kommen schwerer durch.','Das bietet *keinen STI-Schutz*.','Die Spirale wirkt lange ohne *tägliche Einnahme*.','Nach anfangs unregelmäßiger Blutung können Blutung und Schmerzen *schwächer* werden.')],
'MSA': [
 ('Geeignete Kondome *ohne Latex* sind bei Latexallergie eine Alternative.','Die intakte Hülle bildet eine *Barriere*. Sie hält Sperma zurück.','Bei sexuell übertragbaren Infektionen (STI) bleibt durch freie Haut ein *Restrisiko*.','Ein neues Kondom muss bei jedem Sex *von Anfang an* sitzen.'),
 ('Die Hormone hemmen vor allem den *Eisprung*. Ohne freie Eizelle ist keine Befruchtung möglich.','Für Erreger entsteht keine *Barriere*.','Vergessene Tabletten können den Schwangerschaftsschutz *verringern*.','Die Verträglichkeit ist *individuell*. Die Erfahrung einer Freundin gilt für ihren Körper.'),
 ('Kupfer beeinträchtigt Bewegung und *Befruchtungsfähigkeit* der Spermien.','Die Spirale bildet keine *Barriere* gegen Erreger.','Die lange Wirkung erspart die *tägliche Einnahme*.','Blutung und Regelschmerzen können *stärker* werden.'),
 ('Ein Gestagen macht den Schleim am Gebärmutterhals zäher. *Spermien* kommen schwerer hindurch.','Der zähe Schleim bietet *keinen STI-Schutz*.','Die Spirale wirkt lange ohne *tägliche Einnahme*.','Blutung und Schmerzen können später *schwächer* werden.')],
'AHR': [
 ('Bei Latexallergie kommen geeignete *synthetische* Kondome infrage.','Eine intakte Hülle bildet eine mechanische *Barriere* für Sperma.','Beim Schutz vor sexuell übertragbaren Infektionen (STI) ist Naturmembran *nicht gleichwertig*. Auch bei geeigneten Kondomen bleiben Hautstellen frei. Erreger können dort übertragen werden.','Ein neues Kondom bei jedem Sex *von Anfang an* richtig anwenden.'),
 ('Östrogen und Gestagen hemmen vor allem den *Eisprung*. Ohne freie Eizelle ist keine Befruchtung möglich.','Die Wirkung auf den Zyklus bildet keine *Barriere* gegen Erreger.','Vergessene Tabletten können den Schwangerschaftsschutz *mindern*.','Die Verträglichkeit ist *individuell*. Gleiche Einnahme belegt keine gleiche Reaktion.'),
 ('Kupfer stört die Bewegung und *Befruchtungsfähigkeit* der Spermien. Der Eisprung kann stattfinden.','Die Wirkung auf Spermien bedeutet *keinen STI-Schutz*.','Die Spirale wirkt langfristig ohne *tägliche Einnahme*.','Blutung und Regelschmerzen können *stärker* werden. Hormonfrei heißt nicht beschwerdefrei.'),
 ('Ein Gestagen macht den Schleim am Gebärmutterhals für Spermien *schwer durchlässig*.','Veränderter Schleim bietet *keinen STI-Schutz*.','Die Spirale wirkt langfristig ohne *tägliche Einnahme*.','Anfangs kann die Blutung unregelmäßig sein. Später können Blutung und Schmerzen *abnehmen*.')]
}
# Diagnose, Rückmeldung und nächster Denkimpuls sind je Antwortalternative fest verbunden.
def wahl(abschnitt, ziel, frage, richtig, fehler, grund, impuls, starter):
    return dict(typ='wahl',abschnitt=abschnitt,ziel=ziel,frage=frage,passend=richtig,alternativen=[
        dict(text=text,muster=kategorie,erklaerung=antwort,impuls=hilfe) for text,kategorie,antwort,hilfe in fehler],
        grund=grund,impuls=impuls,starter=starter)

def frei(abschnitt,modell,frage,ziel):
    return dict(typ='text',abschnitt=abschnitt,modell=modell,frage=frage,ziel=ziel)

FRAGEN={
'Foerder':[
 wahl(1,'Barriere erkennen','Was hält ein heiles Kondom zurück?','Spermien',[('Den Eisprung','zyklus','Die Hülle liegt außerhalb des Eierstocks.','Was bleibt in der Hülle?')],'Die Hülle fängt Sperma mit Spermien auf.','Was fängt die Hülle auf?','In der Hülle bleiben …'),
 wahl(0,'Ausbleibenden Eisprung verstehen','Was wird ohne Eisprung nicht frei?','Eine Eizelle',[('Spermien','zellen','Spermien entstehen nicht im Eierstock.','Welche Zelle verlässt sonst den Eierstock?')],'Beim Eisprung wird eine Eizelle frei. Bleibt er aus, fehlt sie.','Was verlässt beim Eisprung den Eierstock?','Ohne Eisprung fehlt …'),
 wahl(0,'Wirkort des Kupfers erkennen','Was bewegt sich durch Kupfer schlechter?','Spermien',[('Die Eizelle','zellen','Kupfer stört vor allem die Spermien.','Wer bewegt sich zur Eizelle?')],'Spermien kommen schlechter zur Eizelle.','Wer muss zur Eizelle gelangen?','Das Kupfer stört …'),
 wahl(4,'Mögliche Veränderung von Schmerzen erkennen','Wie können sich Regelschmerzen mit der Hormonspirale verändern?','Sie können schwächer werden.',[('Sie hören sicher auf.','garantie','Die Schmerzen lassen nur bei manchen nach.','Ist eine Besserung sicher?')],'Schwächere Schmerzen sind möglich.','Suche das Wort „können“.','Später können die Schmerzen …')],
'ESA':[
 wahl(2,'Ein verbleibendes Infektionsrisiko erklären','Warum bleibt mit Kondom ein Risiko für Infektionen?','Ein Teil der Haut bleibt frei.',[('Die Hülle bedeckt die gesamte Haut.','haut','Das Kondom bedeckt nur einen Teil der Haut.','Wo kann es noch Hautkontakt geben?')],'Über freie Haut können manche Erreger übertragen werden.','Welche Haut berührt sich noch?','Ein Risiko bleibt, weil …'),
 wahl(3,'Persönliche Verträglichkeit unterscheiden','Eine Freundin verträgt die Pille gut. Was gilt für eine andere Person?','Ihr Körper kann anders reagieren.',[('Bei gleicher Pille verträgt sie sie genauso gut.','erfahrung','Die Erfahrung betrifft die Freundin.','Wessen Körper wurde beobachtet?')],'Die Verträglichkeit ist von Person zu Person verschieden.','Für wen gilt die Erfahrung?','Für eine andere Person …'),
 wahl(4,'Hormonfreiheit und Beschwerden unterscheiden','Die Kupferspirale ist hormonfrei. Was gilt für Regelschmerzen?','Sie können stärker werden.',[('Ohne Hormone bleiben die Schmerzen gleich.','hormonfrei','Auch bei einer hormonfreien Spirale können Schmerzen zunehmen.','Was steht bei Regelschmerzen?')],'Hormonfreiheit schützt nicht vor stärkeren Regelschmerzen.','Kann eine hormonfreie Spirale Beschwerden verändern?','Unter Kupfer können …'),
 wahl(0,'Folge des zähen Schleims verstehen','Was bewirkt zäher Schleim am Gebärmutterhals?','Spermien kommen schwerer hindurch.',[('Die Eizelle verlässt den Eierstock nicht.','zyklus','Hier verändert sich der Schleim am Gebärmutterhals.','Welche Zellen müssen dort hindurch?')],'Der zähere Schleim erschwert Spermien den Weg.','Wer muss durch den Schleim?','Der Schleim erschwert …')],
'MSA':[
 wahl(2,'Grenze der Barriere erklären','Warum bleibt trotz intaktem Kondom ein STI-Risiko?','Erreger können über unbedeckte Haut übertragen werden.',[('Erreger müssen mit Sperma durch die Hülle gelangen.','haut','Manche Erreger werden auch bei Hautkontakt übertragen.','Welche Haut bleibt außerhalb der Hülle?')],'Die Barriere bedeckt nur einen Teil der Haut.','Welche Übertragung braucht kein Sperma?','Ein Restrisiko bleibt, weil …'),
 frei(0,'pille','Wie verhindert die Pille durch ihre Wirkung auf den Eisprung eine Befruchtung?','Ausbleibenden Eisprung mit fehlender befruchtbarer Eizelle verbinden.'),
 wahl(4,'Hormonfreiheit und individuelle Wirkung trennen','Was bedeutet „hormonfrei“ bei der Kupferspirale für Regelschmerzen?','Sie können trotzdem stärker werden.',[('Ohne Hormone können Schmerzen nicht zunehmen.','hormonfrei','Hormonfreiheit schließt stärkere Blutungen und Schmerzen nicht aus.','Welche Veränderung beschreibt die Karte?')],'Auch eine hormonfreie Methode kann Regelschmerzen verstärken.','Was ist trotz Hormonfreiheit möglich?','Hormonfrei bedeutet hier …'),
 frei(0,'schleim','Warum kommen Spermien mit der Hormonspirale schwerer zur Eizelle?','Veränderte Schleimbeschaffenheit mit erschwertem Durchtritt verbinden.')],
'AHR':[
 frei(2,'haut','Warum können manche Erreger trotz intaktem Kondom übertragen werden?','Grenzen der bedeckten Fläche mit Übertragung bei Hautkontakt verbinden.'),
 wahl(3,'Grenzen einer Einzelerfahrung begründen','Eine Freundin verträgt die Pille gut. Was folgt für eine andere Person?','Die Erfahrung lässt ihre persönliche Verträglichkeit offen.',[('Gleiche Einnahme bedeutet gleiche Verträglichkeit.','erfahrung','Die Dosis allein bestimmt die persönliche Reaktion nicht.','Welche Person wurde tatsächlich beobachtet?')],'Eigene Beschwerden und Risiken müssen individuell geklärt werden.','Worüber gibt eine einzelne Erfahrung Auskunft?','Die Erfahrung zeigt … Offen bleibt …'),
 frei(0,'kupfer','Wie erschwert Kupfer die Befruchtung, obwohl ein Eisprung stattfinden kann?','Eingeschränkte Spermienbewegung mit erschwerter Befruchtung verbinden.'),
 wahl(4,'Grenzen einer Vorhersage prüfen','Die Blutung ist anfangs unregelmäßig. Was folgt für spätere Regelschmerzen?','Die Schmerzen können nachlassen. Ihr Verlauf bleibt offen.',[('Die unregelmäßige Blutung zeigt schon, dass die Schmerzen nachlassen.','garantie','Die anfängliche Blutung erlaubt keine sichere Vorhersage.','Welche spätere Veränderung ist nur möglich?')],'Ein möglicher Verlauf ist keine individuelle Garantie.','Welche Beobachtung betrifft nur den Anfang?','Später ist möglich …')]
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
