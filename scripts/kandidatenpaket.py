"""Package the tested candidate, local teaching material, and selected visual evidence."""
import json
from pathlib import Path
from shutil import copy2
from zipfile import ZIP_DEFLATED,ZipFile
from vorabkandidat import ROOT,REF,TARGET,OUT,digest

def package():
    sha=digest((TARGET/'Fallakte.html').read_bytes())
    report02=ROOT/'build/Kandidat-02/Abnahme.json';report08=ROOT/'build/Kandidat-08/Abnahme.json'
    for p in (report02,report08):assert json.loads(p.read_text())['html_sha256']==sha
    for p in (ROOT/'dist/Uebungsakte').glob('Uebungsakte*'):
        if p.suffix in ('.zip','.html'):copy2(p,TARGET/p.name)
    with ZipFile(TARGET/'Work-Material.zip','w',ZIP_DEFLATED) as z:
        for p in sorted(OUT.glob('*Material*')):z.write(p,'02-12/'+p.name)
        for p in sorted((ROOT/'dist/Uebungsakte').glob('*Material*')):z.write(p,'Uebung/'+p.name)
        for name in ('Aufgabenbank.json','Materialbank.md'):z.write(REF/'build/08-12'/name,'08-12/'+name)
    with ZipFile(TARGET/'Fallakte-Sichtpruefung.zip','w',ZIP_DEFLATED) as z:
        z.write(TARGET/'Buildnachweis.json','Buildnachweis.json')
        for folder in (report02.parent,report08.parent,ROOT/'build/vertiefungen',ROOT/'dist/Uebungsakte'):
            for p in sorted(folder.glob('*.json')):
                if p.name not in ('Uebungsakte-Material.json',):z.write(p,f'{folder.name}/{p.name}')
            shots=sorted(folder.glob('*.jpg'))
            assert shots,folder
            for engine in ('chromium','webkit'):
                selected=[p for p in shots if p.name.startswith(engine)]
                assert selected,(folder,engine)
                for p in selected[:2]:z.write(p,f'{folder.name}/{p.name}')
    for p in TARGET.glob('*.zip'):
        with ZipFile(p) as z:assert z.testzip() is None
if __name__=='__main__':package()
