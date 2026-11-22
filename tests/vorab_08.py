"""Apply the unmodified reference assertions and its browser exercises to the candidate."""
import json,os,sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from vorabkandidat import TARGET, REF
sys.path.insert(0,str(REF/'tests'))
import nachrichten as reference

def main():
    reference.QA=ROOT/'build/Kandidat-08';reference.QA.mkdir(parents=True,exist_ok=True)
    reference.check_content()
    record={'einzelwege':[],'gemischt':[],'wiederaufnahme':[],'ansichten':[]}
    with TemporaryDirectory() as td:
        temp=Path(td)
        # The comparator also checks the frozen historical version A, in its own build tree.
        reference.protect(temp)
        reference.B=TARGET
        with ZipFile(TARGET/'Fallakte-SCORM12.zip') as z:
            assert z.testzip() is None and z.read('index.html')==(TARGET/'Fallakte.html').read_bytes()
            z.extractall(temp/'sco')
        (temp/'sco/host.html').write_text(reference.HOST)
        with reference.host(temp/'sco') as url,sync_playwright() as pw:
            for engine in ('chromium','webkit'):
                b=getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE'))
                views,figures=reference.inspect_views(b,engine,temp/'ref/dist/Version-B',TARGET,reference.BANK,reference.shot)
                record['ansichten'].append([views,figures,reference.standalone_zoom(b,engine)])
                for i,person in enumerate(reference.BANK['cases']):
                    for j,level in enumerate(reference.BANK['levels']):
                        record['einzelwege'].append(reference.exercise(b,engine,person,level,4*i+j,url))
                    print(engine,person,flush=True)
                for low,high in [(l,'') for l in reference.BANK['levels']]+[('Förder','AHR'),('ESA','MSA')]:
                    record['gemischt'].append(reference.measure_route(b,engine,TARGET,reference.BANK,low,high,reference.shot))
                for i,(low,high) in enumerate([('Förder','AHR'),('ESA','MSA')]):
                    record['wiederaufnahme'].append(reference.pair_recovery(b,engine,url,low,high,bool(i)==(engine=='webkit')))
                b.close()
    record['html_sha256']=reference.digest((TARGET/'Fallakte.html').read_bytes())
    (reference.QA/'Abnahme.json').write_text(json.dumps(record,ensure_ascii=False,indent=1))
if __name__=='__main__':main()
