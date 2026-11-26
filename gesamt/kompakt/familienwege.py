from concurrent.futures import ProcessPoolExecutor
from itertools import product
from pathlib import Path
from tempfile import TemporaryDirectory
import gzip,json,hashlib
from zipfile import ZipFile
from familien_scan import qa,Aufzeichnung,QA,OUT,HOST,host,json_text

def weg(args):
    engine,i=args
    name='Familienroute-'+engine+'-'+str(i)
    chk=QA/(name+'.json')
    build=hashlib.sha256((OUT/'Fallakte-08-12.html').read_bytes()).hexdigest()
    if chk.exists():
        cached=json.loads(chk.read_text())
        if cached.get('html_sha256')==build:return cached
    with TemporaryDirectory() as tmp:
        site=Path(tmp)
        with ZipFile(OUT/'Fallakte-08-12-SCORM12.zip') as z:z.extractall(site)
        (site/'host.html').write_text(HOST)
        with Aufzeichnung(name),host(site) as url:r=qa.engine_run(engine,url,OUT/'Fallakte-02-12.html',[i])
    r['html_sha256']=build
    chk.write_text(json_text(r))
    return r
if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=3) as pool:list(pool.map(weg,[(engine,i) for i in [7,0,1,2,3,4,5,6] for engine in ['chromium','webkit']]))
    for engine in ['chromium','webkit']:
        rr=[json.loads((QA/('Familienroute-'+engine+'-'+str(i)+'.json')).read_text()) for i in range(8)]
        result=dict(wege=[r['wege'][0] for r in rr],pixelvergleich=rr[0]['pixelvergleich'])
        assert len({r['pixelvergleich'] for r in rr})==1
        assert {k for r in result['wege'] for k in r['alle_uebergaben']}==set(qa.BANK['media']['steps'])
        (QA/('Familienwege-verlauf-'+engine+'.json')).write_text(json_text(result))
