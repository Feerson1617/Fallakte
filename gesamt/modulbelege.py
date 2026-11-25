"""Übernimmt Detailprotokolle ausschließlich bei identischer Moduldatei und Navigationshülle."""
import argparse
import base64
import json
import shutil
from pathlib import Path
from lxml import etree,html
from auslieferung import OUT,QA,json_text,sha


def nachvollziehen(datei):
    doc=html.fromstring(datei.read_bytes())
    modules={}
    for node in doc.xpath('//script[@type="application/octet-stream"]'):
        modules[node.get('id').split('-')[-1]]=sha(base64.b64decode(node.text,validate=True))
        node.text='MODUL'
    revision=doc.xpath('//meta[@name="revision"]')[0]
    revision.set('content','REVISION')
    return sha(etree.tostring(doc)),modules


def uebernehmen(quelle,module):
    alt=quelle/'build/Gesamtpruefung'
    original=nachvollziehen(quelle/'dist/Gesamt/Fallakte-08-12.html')
    aktuell=nachvollziehen(OUT/'Fallakte-08-12.html')
    assert original[0]==aktuell[0], 'Die Navigation der Prüfaufbauten unterscheidet sich.'
    hashes={}
    files=[]
    for modul in module:
        assert original[1][modul]==aktuell[1][modul],modul
        hashes[modul]=aktuell[1][modul]
        namen={'vor':['PREP'],'02':['UB02','Zusatz'],'08':['UB08']}[modul]
        for name in namen:
            files.extend('Paarvergleich-'+name+ext for ext in ('.json','.ndjson.gz'))
        if modul=='02':files+=['Empfehlungen.json','Dialogansichten.jsonl.gz']
        if modul=='08':
            for art in ('tandem','verlauf'):
                for engine in ('chromium','webkit'):
                    files+=['Familienwege-'+art+'-'+engine+'.json','Familienansichten-'+art+'-'+engine+'.jsonl.gz']
    assert all((alt/name).is_file() for name in files)
    for name in files:shutil.copyfile(alt/name,QA/name)
    report=dict(quelle=json.loads((alt/'Bestandsvergleich.json').read_text())['commit'],
                ziel=json.loads((QA/'Bestandsvergleich.json').read_text())['commit'],
                navigation_sha256=aktuell[0],module=hashes,nachweise={n:sha((QA/n).read_bytes()) for n in files})
    (QA/'Pruefherkunft.json').write_text(json_text(report))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('quelle',type=Path)
    parser.add_argument('module',choices=('vor','02','08'),nargs='+')
    args=parser.parse_args()
    uebernehmen(args.quelle,args.module)
