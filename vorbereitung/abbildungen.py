"""Offline-Lehrgrafiken. Identische anatomische Grundform für beide Spiralen."""
from html import escape


def label(x, y, value, size=17, middle=False):
    anchor = 'middle' if middle else 'start'
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{escape(value)}</text>'


def path(d, color='#28695d', width=3, fill='none'):
    return f'<path d="{d}" stroke="{color}" stroke-width="{width}" fill="{fill}" stroke-linecap="round" stroke-linejoin="round"/>'


def dot(x, y, r, color):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>'


def box(x,y,w,h,fill='#fffdf6'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="#99b4a9"/>'


def sperm(x,y,angle):
    return f'<g transform="translate({x} {y}) rotate({angle})"><ellipse rx="5" ry="3" fill="#295546"/>{path("M-5 0 q-5 -4 -9 0 t-9 0",width=1.6)}</g>'


def anatomy(x,y,scale):
    body=path('M48 46 Q76 31 104 46 Q105 63 93 79 Q81 92 83 110 L83 122 L69 122 L69 110 Q71 95 59 80 Q45 64 48 46 Z','#996d67',3,'#f0c7b8')
    body+=path('M55 49 Q76 39 97 49 Q97 62 86 76 Q78 88 76 108 Q75 90 66 78 Q56 64 55 49 Z','#c79585',1.5,'#fff5e5')
    body+=path('M50 48 Q33 42 32 30 Q29 14 14 23 L9 32 M102 48 Q119 42 120 30 Q123 14 138 23 L143 32','#996d67',4)
    body+='<g fill="#edc79c" stroke="#9c704c" stroke-width="2"><ellipse cx="17" cy="40" rx="11" ry="7"/><ellipse cx="135" cy="40" rx="11" ry="7"/></g>'
    return f'<g transform="translate({x} {y}) scale({scale})">{body}</g>'


def iud(copper):
    bar=path('M103 80 q15 -5 30 0 M118 78 v38','#36655f',4)
    if copper:
        bar+=''.join(path(f'M115 {y} l6 -2','#ae612d',2) for y in range(90,112,4))
    else:
        bar+=path('M118 90 v19','#617988',7)
    return bar+path('M118 116 q3 12 -1 22','#5a7770',1.4)


def figures():
    figures={}
    v=box(12,32,137,48)+label(24,62,'Latex')+box(12,87,137,61)+label(24,112,'Synthetisch,')+label(24,134,'latexfrei')
    v+=label(12,20,'Material')+label(12,174,'Zur Verhütung')+label(12,196,'geeignet')
    v+=path('M197 52 L197 131 Q198 165 236 167 Q241 182 248 167 Q285 164 285 131 L285 52','#377461',4,'#dcece3')
    v+=path('M193 52 Q240 44 289 52 Q240 60 193 52','#377461',3,'#e5f1e9')
    v+=sperm(230,94,-23)+sperm(260,116,63)+sperm(233,136,150)
    v+=label(194,24,'Intakte Hülle')+path('M262 118 l24 29 h24',width=1.5)+label(276,171,'Spermien',15)
    figures['1A']=v
    v=box(16,18,318,48,'#efe5d5')+box(16,18,164,48,'#c8e0d4')+label(42,49,'bedeckt')+label(201,49,'unbedeckt')
    v+=label(17,98,'Beginn')+label(207,98,'weiterer Kontakt')+path('M17 107 H330 l-7 -4 m7 4 l-7 4',width=1.5)
    v+=label(17,138,'Von Anfang an')+path('M17 150 H330',width=7)
    v+=label(17,181,'Später Beginn')+path('M17 194 h131','#ad8154',2)+path('M148 194 H330',width=7)
    figures['1B']=v
    v=label(84,20,'Eisprung',18,True)+label(264,20,'Eisprung gehemmt',17,True)
    v+=anatomy(0,37,1.03)+anatomy(182,37,1.03)
    v+=dot(24,68,4,'#a75530')+path('M24 64 q0 -7 6 -8 m-3 -2 l3 2 -1 3','#99542c',2)
    v+=path('M24 68 L53 50 h15','#945636',1)+label(66,50,'Eizelle',13)
    v+=label(8,181,'Eierstock',15)+path('M20 82 L13 160',width=1)+label(184,181,'Eileiter',15)+path('M220 79 l-11 81',width=1)
    v+=label(176,207,'Modell der hauptsächlichen Wirkung',15,True)
    figures['2A']=v
    v=label(16,31,'Einnahme')+''.join(label(x,30,'Tag '+str(i+1),15) for i,x in enumerate((160,223,282)))
    for y,name,lapse in [(69,'nach Plan',False),(119,'vergessen',True)]:
        v+=label(16,y+5,name)
        for i,x in enumerate((178,238,298)):
            v+=box(x-20,y-19,40,36)
            v+=path(f'M{x-7} {y} l5 5 10 -12',width=3) if not (lapse and i==1) else path(f'M{x-7} {y} h14','#a16630',3)
    v+=label(15,161,'Mögliche persönliche Reaktionen',16)+box(14,173,158,37)+label(24,197,'z. B. Übelkeit',15)+box(179,173,162,37)+label(187,197,'gut vertragen',15)
    figures['2B']=v
    for code,copper in [('3A',True),('4A',False)]:
        v=anatomy(15,13,1.36)+iud(copper)
        v+=label(11,22,'Gebärmutter',15)+path('M68 27 L84 76',width=1)
        v+=label(8,202,'Gebärmutterhals',15)+path('M104 187 l11 -22',width=1)
        if copper:
            for x,y in [(113,116),(127,113),(121,121),(111,124)]:
                v+=dot(x,y,2,'#ad6036')
            v+=label(216,43,'Kupferspirale')+path('M213 46 L131 79',width=1)
            v+=path('M113 110 l-6 5 m1 -3 -1 3 3 -1 M122 115 l6 4 m-1 -3 1 3 -3 -1','#a56138',1.2)
            v+=label(205,97,'Kupfer')+path('M196 97 L128 114',width=1)
            v+=sperm(118,148,-82)+sperm(124,139,-97)+label(185,147,'Spermien')+label(181,171,'in ihrer Bewegung',15)+label(181,190,'beeinträchtigt',15)
        else:
            v+=label(180,22,'Hormonspirale',17)+path('M184 27 L130 80',width=1)
            v+=label(202,51,'Gestagen',15)+path('M198 52 L124 103',width=1)
            v+=path('M123 161 l58 -61',width=1)
            for x,dense in [(178,False),(264,True)]:
                v+=box(x,76,73,66,'#e5efe7')
                for y in (range(83,136,8) if dense else [90,117]):
                    v+=path(f'M{x+5} {y} q14 -6 30 1 t32 0','#719487',1.5)
                v+=sperm(x+37,122,-84)
            v+=label(179,163,'Schleim',15)+label(264,162,'dichter',15)+label(189,193,'Weg der Spermien',15)
        figures[code]=v
    for code,copper in [('3B',True),('4B',False)]:
        v=''
        for y,t in [(17,'Eignung und freiwillige Zustimmung'),(65,'Ärztliches Einsetzen'),(113,'Längere Wirkung und Lagekontrolle' if copper else 'Längere Gestagenabgabe · Lagekontrolle')]:
            v+=box(12,y,326,33,'#e3eee6')+label(24,y+22,t,15 if len(t)>36 else 16)
            if y<113:v+=path(f'M175 {y+34} v10 m-4 -4 l4 4 4 -4',width=2)
        v+=label(18,171,'Mögliche Veränderungen',17)
        v+=label(18,194,'Blutung oder Schmerzen können',15)+label(18,213,'stärker werden.',15) if copper else label(18,193,'Anfangs unregelmäßige Blutung. Später',15)+label(18,212,'können Blutung und Schmerzen nachlassen.',15)
        figures[code]=v
    return figures


def render_visuals(briefs):
    return {code:f'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{escape(briefs[code]["alt"],quote=True)}" viewBox="0 0 350 224"><title>{escape(briefs[code]["title"])}</title>{drawing}</svg>' for code,drawing in figures().items()}
