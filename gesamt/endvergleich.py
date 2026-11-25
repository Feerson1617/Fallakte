"""Vergleiche den vollständigen Datenvertrag des Builds mit der ausgelieferten Sprachfassung."""
import argparse
import json
from pathlib import Path
from auslieferung import OUT,QA,sha,json_text,rebuild
from sprachpruefung import documents,bank,leaves

REFERENZ='3565a45d8688ce002b29dcb2dd04b54750e187f0'
# Hash über exakte Quelladresse UND beide Wortlaute. Jede weitere Textänderung
# oder Änderung eines Codes, Antwortschlüssels, Bildes oder einer Kartenzeile fällt auf.
FREIGEGEBENE_DIFFERENZEN={
    'PREP':'b95f8862d2b3235447b06f5d6889b7f684509cc652863950c91ee50f544172a5',
    'UB02':'8b75b85cec0b271ceba687e2d2ad2751215de162bc29e0c57ae7fc8926eb7b06',
    'Tom':'a26218dd4f3e278c5c81c93fadd7cc51fead0e63fb019542c7e64a2a182d976c',
    'Celina':'e4f85b73e0a8a7d2480cefdfca8fe852e4ba02f467203abe56e9b3e0cc3c807d',
    'UB08':'49019af56a9fd9db03d576e96abbee98e5d713cbc7d6f42552a8259e13ac34b9',
}
def basis():
    return rebuild(REFERENZ,'gesamt/auslieferung.py','Gesamt')/'Fallakte-Gesamt.html'

def vergleich(ref):
    old=documents(ref.read_bytes());new=documents((OUT/'Fallakte-Gesamt.html').read_bytes())
    assert old['START'][0].xpath('string(//meta[@name="revision"]/@content)')==REFERENZ
    assert old.keys()==new.keys()
    proof={}
    for m,digest in FREIGEGEBENE_DIFFERENZEN.items():
        a=dict(leaves(bank(old[m][0])));b=dict(leaves(bank(new[m][0])))
        delta={k:(a.get(k),b.get(k)) for k in a.keys()|b.keys() if a.get(k)!=b.get(k) and k not in ('commit','buildCommit')}
        assert sha(json.dumps(delta,sort_keys=True,ensure_ascii=False).encode())==digest,m
        for key,(before,after) in delta.items():
            assert all(v is None or isinstance(v,str) for v in (before,after))
            assert key.rsplit('/',1)[-1] not in ('ok','correct','code','id','sectionId','nextId','revealsSolution')
        if m=='PREP':
            assert bank(old[m][0])['cards']==bank(new[m][0])['cards']
        proof[m]=dict(datenfelder=len(b),unterschiede=delta,sha256_alt=old[m][1],sha256_neu=new[m][1])
    family=bank(new['UB08'][0])
    for case in family['cases'].values():
        for task in [*case['tasks'],case['transfer']]:
            assert sum(answer['ok'] for answer in task['answers'])==1
            assert all(len(task['helpByLevel'][level])==5 for level in family['levels'])
    sections={r['id']:r['section'] for case in family['cases'].values() for r in case['recovery']}
    sections.update({r['id']:r['section'] for r in family['evaluationRecovery']})
    media=family['media']
    assert set(media['fields'])==set(family['paperFields'])=={r['field'] for r in media['steps'].values()}
    for key,r in media['steps'].items():
        assert r['id']==key and r['section']==sections[r['sectionId']]
        assert r['restart'].endswith(sections[r['restartId']])
        if r['mode']=='Abschnittswechsel':
            assert r['returnText']=='Öffne „'+sections[r['nextId']]+'“.'
        elif r['mode']=='Sicherung':
            assert key=='LA-abschluss' and r['nextId'] is None
        else:
            assert r['sectionId']==r['nextId']
        assert set(r['orders'])==set(family['levels'])
        assert all(order['action'] in order['screen'] and r['field'] in order['screen'] for order in r['orders'].values())
    (QA/'Referenzkarten.json').write_text(json_text(bank(old['PREP'][0])['cards']))
    (QA/'Endvergleich.json').write_text(json_text(proof))
    return old,new
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--referenz',type=Path);args=parser.parse_args()
    vergleich(args.referenz or basis())
