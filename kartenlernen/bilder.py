"""Behalte die geprüften anatomischen Grundformen. Beschriftungen skalieren im HTML."""
from abbildungen import anatomy, dot, iud, path, sperm


def make_graphics():
    # Anatomie und Lage der Spiralen kommen aus der geprüften Vorbereitung.
    uterus=anatomy(15,13,1.36)
    barrier=path('M45 22 L45 79 Q45 109 78 110 Q85 124 91 110 Q122 110 122 79 L122 22','#34755f',4,'#cee6d7')
    barrier+=path('M42 22 Q84 13 125 22 Q84 31 42 22 Z','#34755f',3,'#e5f1e9')
    grid=''.join(dot(10+10*x,9+10*y,4,'#a6492d' if y==0 and x<3 else '#a6bcb1') for x in range(10) for y in range(10))
    skin='<rect x="9" y="32" width="160" height="52" rx="14" fill="#edccba"/><path d="M10 57q13 -8 25 0t25 0t25 0t25 0t25 0t32 0" fill="none" stroke="#91665d" stroke-width="2"/><path d="M10 49h88v-9q0-10-10-10H22q-12 0-12 12z" fill="#86b59f" stroke="#345c4e" stroke-width="3"/>'
    skin+=path('M55 30V16 M138 54V16',width=2)
    eggs=anatomy(0,6,1)+anatomy(158,6,1)+dot(28,44,5,'#af5431')+path('M22 37 q7 -11 15 -9 m-5 -4 5 4 -6 3','#965030',2)
    cal=''.join(f'<rect x="{7+i*57}" y="25" width="49" height="53" rx="7" fill="#fffdf6" stroke="#487363" stroke-width="2"/>'+path(f'M{7+i*57} 40h49',width=1) for i in range(3))
    cal+=path('M18 57l7 7 14-15 M132 57l7 7 14-15',width=3)+path('M77 58h21','#9a5936',3)
    def complaints(up):
        drop='<path d="M53 17C46 32 32 46 32 62a21 21 0 0042 0c0-16-14-31-21-45z" fill="#c57d69" stroke="#875444" stroke-width="2"/>'
        return drop+path('M100 73L143 30m-19 0h19v19' if up else 'M100 30l43 43m0-19v19h-19',width=5)
    mucus=uterus+iud(False)+path('M105 147q10 -5 22 0 M106 151q9-4 20 0 M108 155q8-4 16 0','#377461',2)+sperm(117,174,-90)+path('M126 151l24-13',width=2)
    copper=uterus+iud(True)+''.join(dot(x,y,2.8,'#ae612d') for x,y in [(115,116),(127,113),(121,121),(111,124)])+sperm(117,147,-82)
    drawings=[
      ('index','0 0 110 110',grid,'100 Frauen · 1 Jahr','Drei von hundert Punkten sind markiert.'),
      ('huelle','20 6 130 118',barrier+sperm(77,53,20)+sperm(98,78,-45)+sperm(74,89,90),'Heile Hülle mit Spermien','Eine intakte Kondomhülle hält die dargestellten Spermien zurück.'),
      ('kontakt','0 8 180 84',skin,'Bedeckte und freie Haut','Links bedeckt die Hülle die Haut. Rechts bleibt die Haut frei.'),
      ('eisprung','0 18 310 116',eggs,'Eisprung / Eisprung gehemmt','Links tritt eine Eizelle aus dem Eierstock aus. Rechts wird keine Eizelle frei.'),
      ('einnahme','0 13 180 78',cal,'Einnahme · ein Tag fehlt','Drei Kalendertage. Am mittleren fehlt die Einnahme.'),
      ('kupfer','18 28 203 162',copper,'Kupfer und Spermien','Die Kupferspirale sitzt in der Gebärmutter. Kupfer beeinträchtigt Spermien.'),
      ('kupferwahl','19 8 139 85',complaints(True),'Blutung kann zunehmen','Ein Tropfen mit aufsteigendem Pfeil. Die Blutung kann zunehmen.'),
      ('schleim','18 28 203 162',mucus,'Zäher Schleim am Gebärmutterhals','Unter der Hormonspirale erschwert Schleim am Gebärmutterhals den Weg der Spermien.'),
      ('hormonwahl','19 8 139 85',complaints(False),'Blutung kann abnehmen','Ein Tropfen mit absteigendem Pfeil. Später kann die Blutung abnehmen.')]
    return {k:dict(svg=f'<svg viewBox="{view}" role="img" aria-label="{alt}">{art}</svg>',caption=cap) for k,view,art,cap,alt in drawings}
