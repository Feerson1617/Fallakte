"""Ausgelieferten Familienrat über Pflicht-, Wahl-, Fehler-, Hilfe- und persönliche Prüfwege bedienen."""
import argparse,os,sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from auslieferung import ROOT,QA,OUT,json_text
from leseprotokoll import Aufzeichnung
os.environ['FALLAKTE_FAMILIEN_HTML']=str(OUT/'Fallakte-08-12.html')
sys.path.insert(0,str(ROOT/'tests'))
import familienrat_qa as qa
import familienrat_zustaende as z
from tagesauswahl import HOST,host

def run(engine,typ):
    qa.QA.mkdir(exist_ok=True,parents=True);z.OUT.mkdir(exist_ok=True,parents=True)
    with Aufzeichnung('Familienansichten-'+typ+'-'+engine):
        if typ=='tandem':
            r=z.check(engine)
        else:
            with TemporaryDirectory() as temp:
                site=Path(temp)
                with ZipFile(OUT/'Fallakte-08-12-SCORM12.zip') as archive:archive.extractall(site)
                (site/'host.html').write_text(HOST)
                with host(site) as url:r=qa.engine_run(engine,url,OUT/'Fallakte-02-12.html')
            assert {k for weg in r['wege'] for k in weg['alle_uebergaben']}==set(qa.BANK['media']['steps'])
    (QA/('Familienwege-'+typ+'-'+engine+'.json')).write_text(json_text(r))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('engine',choices=['chromium','webkit'])
    p.add_argument('typ',choices=['verlauf','tandem'])
    a=p.parse_args();run(a.engine,a.typ)
