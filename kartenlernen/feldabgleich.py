"""Fachliche Gegenprobe für die 64 sichtbaren Lernbelege vor den Papieraufträgen."""
def pruefe(belege,karten):
    for i,karte in enumerate(karten):
        for j,feld in enumerate(karte['felder']):
            b=belege[i*4+j]
            assert (b['kapitel'],b['feld'],b['wort'])==(i+1,j+1,feld['wort'])
            assert feld['wort'] in b['text'],b
            b['kartenstelle']=next(s['volltext'] for s in karte['texte'] if s['titel']==feld['titel'])
            assert b['text'] in b['kartenstelle'],b
