"""Seiten der von Work benannten Originale mit den Aufträgen im gebauten SCO vergleichen."""
import argparse,re,subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from sprachpruefung import documents,bank
from auslieferung import OUT,QA,sha,json_text

def run(archiv):
    b=bank(documents((OUT/'Fallakte-08-12.html').read_bytes())['UB08'][0]);rows=[]
    with ZipFile(archiv) as z,TemporaryDirectory() as temp:
        for tier in ('Foerder','ESA'):
            name='Pflichtlernbogen_'+tier+'.pdf';raw=z.read(name);p=Path(temp)/name;p.write_bytes(raw)
            level='Förder' if tier=='Foerder' else tier
            for page,key in [(2,'MU'),(3,'FR'),(4,'LA')]:
                text=subprocess.check_output(['pdftotext','-layout','-f',str(page),'-l',str(page),str(p),'-'],text=True)
                flat=' '.join(text.split())
                keys=[key+'-erst',key+'-ergebnis'] if key!='LA' else ['LA-eigen','LA-abschluss']
                screens=[b['media']['steps'][k]['orders'][level]['screen'] for k in keys]
                if key!='LA':
                    assert 'Meine erste' in flat and 'Nach dem' in flat and 'rechts erneut ankreuzen. Erstes Kreuz bleibt' in flat
                    assert 'links an: Meine erste Antwort' in screens[0] and 'rechts an: Nach dem Prüfen. Dein erstes Kreuz bleibt.' in screens[1]
                    field=b['cases']['Mutter' if key=='MU' else 'Freundin']['field']
                    opt=b['media']['fields'][field+' / Meine erste Antwort']
                    labels=opt['foerder' if level=='Förder' else 'options']
                    positions=[flat.index(label) for label in labels]
                    assert positions==sorted(positions),labels
                else:
                    assert all(x in flat for x in ['Lauras Frage – Meine Antwort','Lauras Frage – Festhalten','digital geprüft','analog geprüft','noch offen'])
                    assert 'Lass deine erste Antwort stehen' in screens[1]
                    if tier=='Foerder':
                        assert all(x in flat for x in ['Schreibe M (Mutter) oder F (Freundin)','Beide, aus unterschiedlichen Gründen','erkläre beide'])
                        assert 'Trage M für Mutter oder F für Freundin' in screens[0] and 'erkläre beide' in screens[0]
                rows.append(dict(datei=name,sha256=sha(raw),seite=page,niveau=level,abschnitte=keys,auftraege=screens))
    (QA/'Pflichtbogenabgleich.json').write_text(json_text(dict(archiv_sha256=sha(archiv.read_bytes()),seiten=rows)))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('zip',type=Path);run(p.parse_args().zip)
