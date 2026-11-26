"""A4-Duplex mit zwei Kartenhälften wie in der Druckvorlage vom 27.11."""
import io
import re
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def druck(cards, niveau, muster, fontpath):
    pdfmetrics.registerFont(TTFont('Karte',str(fontpath)))
    stream=io.BytesIO()
    c=Canvas(stream,pagesize=A4,invariant=True)
    c.setTitle(('Musterkarten' if muster else 'Infokarten')+' · '+niveau)
    width,height=A4
    left,right=30,width-30
    for i,card in enumerate(cards):
        top=height-(i%2)*height/2
        c.setFillColor(HexColor('#21483c'));c.setFont('Karte',22)
        c.drawString(left,top-33,card['ueberschrift'])
        c.setFont('Karte',12);c.drawRightString(right,top-30,('Förder' if niveau=='Foerder' else niveau)+(' · Muster' if muster else ''))
        y=top-54
        def absatz(text,size,leading):
            nonlocal y
            c.setFont('Karte',size);x=left
            for token in text.split():
                match=re.fullmatch(r'\{([1-4])\}([.,?!]?)',token)
                if match:
                    wort=card['felder'][int(match[1])-1]['wort']
                    w=max(115,pdfmetrics.stringWidth(wort,'Karte',size)+25)
                else: w=pdfmetrics.stringWidth(token,'Karte',size)
                if (match and x>left) or x+w>right:
                    y-=leading;x=left
                if match:
                    c.setStrokeColor(HexColor('#557769'));c.roundRect(x,y-3,w-5,leading-1,3)
                    c.drawString(x+4,y,match[1])
                    if muster:c.drawString(x+18,y,wort)
                    c.drawString(x+w-3,y,match[2])
                else:c.drawString(x,y,token)
                x+=w+pdfmetrics.stringWidth(' ','Karte',size)
            y-=leading
        for s in card['texte']:
            c.setFillColor(HexColor('#205641'));absatz(s['titel'],14,17)
            c.setFillColor(HexColor('#15251f'));absatz(s['lueckentext'],12,16)
            y-=3
        c.setFillColor(HexColor('#344c41'))
        absatz('Pearl-Index '+card['pearl']+' (pro familia). '+card['pearl_erklaerung'],10,12)
        assert y>=top-height/2+2,(niveau,card['titel'],y-top+height/2)
        if i%2==0:
            c.setDash(4,4);c.line(0,height/2,width,height/2);c.setDash()
        else:c.showPage()
    c.save()
    return stream.getvalue()
