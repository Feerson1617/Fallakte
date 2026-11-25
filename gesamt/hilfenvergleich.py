"""Testet wörtliche Lösungsübernahmen in den ersten vier Hilfen der gebauten Anwendung."""
from auslieferung import OUT, QA, json_text
from sprachpruefung import documents,bank


def run():
    docs=documents((OUT/'Fallakte-Gesamt.html').read_bytes())
    rows=[]
    def pruefe(modul,frage,zustand,richtig,hilfen):
        assert len(hilfen)==5,(modul,frage,zustand)
        needle=richtig.strip('.?! ,„“').casefold()
        # Einzelwörter wie „Fakt“ kommen auch als Kategoriename vor; dafür ist ein reiner Vergleich ungeeignet.
        if len(needle)<7:return
        for i,h in enumerate(hilfen[:4],1):
            assert needle not in h.casefold(),(modul,frage,zustand,i,richtig,h)
        rows.append(dict(modul=modul,frage=frage,zustand=zustand,stufen=[1,2,3,4]))
    for tier,l in bank(docs['PREP'][0])['levels'].items():
        questions=[l['intro']['question']]
        for c in l['chapters']:
            questions.extend(c['questions'])
            if c.get('paperCheck'):questions.append(c['paperCheck'])
        for q in questions:
            truth=next(o['text'] for o in q['options'] if o['correct'])
            pruefe('PREP',q['id'],'vor der Wahl',truth,q['hintsBeforeChoice'])
            for o in q['options']:
                if 'hints' in o:pruefe('PREP',q['id'],'nach Wahl '+str(o.get('id') or o['code']),truth,o['hints'])
    for key,s in bank(docs['UB02'][0])['stages'].items():
        for tier,l in s['levels'].items():
            for m,way in l['strategies'].items():
                for o in way['options']:
                    if o['correct']:pruefe('UB02',key+' '+tier,m,o['text'],way['hints'])
    for name,c in bank(docs['UB08'][0])['cases'].items():
        for t in [*c['tasks'],c['transfer']]:
            truth=next(o['text'] for o in t['answers'] if o['ok'])
            for tier,seq in t['helpByLevel'].items():
                pruefe('UB08',name+' '+t['id'],tier,truth,seq)
    (QA/'Hilfenvergleich.json').write_text(json_text({'kriterium':'Wörtliche Übernahme der längeren korrekten Antwort in Hilfen 1 bis 4', 'wege':rows}))
if __name__=='__main__':run()
