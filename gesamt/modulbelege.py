"""Übernimmt ausschließlich Nachweise zu byteidentischen integrierten Unterrichtsmodulen."""
import argparse
import json
import shutil
from pathlib import Path
from auslieferung import OUT,QA,json_text,sha
from sprachpruefung import documents


def uebernehmen(quelle):
    alt = quelle / 'build/Gesamtpruefung'
    hashes = json.loads((QA / 'Module.json').read_text())
    alt_hashes = json.loads((alt / 'Module.json').read_text())
    for folder in (quelle / 'dist/Gesamt', OUT):
        inhalt = documents((folder / 'Fallakte-08-12.html').read_bytes())
        for tag in ('02','08'):
            assert hashes[tag] == alt_hashes[tag] == inhalt['UB'+tag][1]
    files = ['Empfehlungen.json','Dialogansichten.jsonl.gz']
    for name in ('UB02','UB08','Zusatz'):
        files += ['Paarvergleich-'+name+ext for ext in ('.json','.ndjson.gz')]
    for art in ('tandem','verlauf'):
        for engine in ('chromium','webkit'):
            files += ['Familienwege-'+art+'-'+engine+'.json','Familienansichten-'+art+'-'+engine+'.jsonl.gz']
    for name in files:
        shutil.copyfile(alt/name,QA/name)
    report = dict(quelle=json.loads((alt/'Bestandsvergleich.json').read_text())['commit'],
                  ziel=json.loads((QA/'Bestandsvergleich.json').read_text())['commit'],
                  module={k:hashes[k] for k in ('02','08')},nachweise={n:sha((QA/n).read_bytes()) for n in files})
    (QA/'Pruefherkunft.json').write_text(json_text(report))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('quelle',type=Path)
    uebernehmen(parser.parse_args().quelle)
