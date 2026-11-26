"""Fachliche Gegenprobe für die 64 sichtbaren Lernbelege vor den Papieraufträgen."""
STAMM = (
    (('latex','synthetisch'), ('hülle','barriere'), ('risiko','gleichwertig'), ('von anfang an',)),
    (('eisprung',), ('keinen schutz','kein sti-schutz','keinen sti-schutz','keine barriere'), ('regelmäßig','vergessene'), ('unterschiedlich','individuell')),
    (('spermien',), ('keinen schutz','kein sti-schutz','keine barriere','keinen sti-schutz'), ('tägliche',), ('stärker',)),
    (('schleim',), ('nicht vor infektionen','keinen sti-schutz','kein sti-schutz'), ('tägliche',), ('schwächer','abnehmen'))
)

def pruefe(belege,karten):
    for i,karte in enumerate(karten):
        for j,feld in enumerate(karte['felder']):
            b=belege[i*4+j]
            assert (b['kapitel'],b['feld'],b['wort'])==(i+1,j+1,feld['wort'])
            assert any(w in b['text'].lower() for w in STAMM[i][j]),b
            b['kartenstelle']=next(s['volltext'] for s in karte['texte'] if s['titel']==feld['titel'])
