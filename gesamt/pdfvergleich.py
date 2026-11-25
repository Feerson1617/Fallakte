"""Seiten der von Work benannten Originale mit den Aufträgen im gebauten SCO vergleichen."""
import argparse,re,subprocess
from lxml import etree
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
                layout=None
                if key!='LA':
                    bbox=subprocess.check_output(['pdftotext','-bbox-layout','-f',str(page),'-l',str(page),str(p),'-'])
                    doc=etree.fromstring(bbox)
                    lines={ ' '.join(line.xpath('./*[local-name()="word"]/text()')):line for line in doc.xpath('//*[local-name()="line"]') }
                    left,right=lines['Meine erste'],lines['Nach dem']
                    assert float(left.get('xMax'))<float(right.get('xMin'))
                    assert abs(float(left.get('yMin'))-float(right.get('yMin')))<1
                    layout=dict(erste_antwort_x=float(left.get('xMin')),nach_dem_pruefen_x=float(right.get('xMin')),kopfzeile_y=float(left.get('yMin')),einheit='PDF-Punkt')
                    assert 'Meine erste' in flat and 'Nach dem' in flat and 'rechts erneut ankreuzen. Erstes Kreuz bleibt' in flat
                    assert 'links in „Meine erste Antwort“' in screens[0] and 'rechts in „Nach dem Prüfen“. Dein erstes Kreuz bleibt.' in screens[1]
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
                bild='Druckvergleich-'+tier+'-'+str(page)
                subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-singlefile','-scale-to','1000','-jpeg','-jpegopt','quality=67',str(p),str(QA/bild)],check=True)
                rows.append(dict(datei=name,bild=bild+'.jpg',spalten=layout,sha256=sha(raw),seite=page,niveau=level,abschnitte=keys,auftraege=screens))
    (QA/'Pflichtbogenabgleich.json').write_text(json_text(dict(archiv_sha256=sha(archiv.read_bytes()),seiten=rows)))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('zip',type=Path);run(p.parse_args().zip)
