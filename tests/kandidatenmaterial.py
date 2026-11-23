"""Cross-check the archives people download against the payloads their browser reads."""
import base64
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
from lxml.html import fromstring

ROOT=Path(__file__).resolve().parents[1]
def load(document,element):
    return fromstring(document).get_element_by_id(element).text
def child(document,element):
    return base64.b64decode(load(document,element),validate=True)
def verify(folder):
    app=(folder/'Fallakte.html').read_bytes()
    meta=json.loads((folder/'Buildnachweis.json').read_text())
    assert hashlib.sha256(app).hexdigest()==meta['html_sha256'] and len(app)==meta['bytes']<10_000_000
    for name,expected in meta['auslieferungs_sha256'].items():
        assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==expected,name
    first=child(app,'modul-02');second=child(app,'modul-08')
    assert hashlib.sha256(first).hexdigest()==meta['tag02_sha256']
    assert hashlib.sha256(second).hexdigest()==meta['tag08_sha256']
    for basename in ('Fallakte','Uebungsakte'):
        with ZipFile(folder/(basename+'-SCORM12.zip')) as z:
            assert z.testzip() is None and z.read('index.html')==(folder/(basename+'.html')).read_bytes()
            assert 'imsmanifest.xml' in z.namelist()
    with ZipFile(folder/'Work-Material.zip') as z:
        assert z.testzip() is None
        checks={'02-12/Materialvertrag':load(first,'materialvertrag'),
                '08-12/Aufgabenbank':load(second,'material'),
                'Uebung/Uebungsakte-Material':load((folder/'Uebungsakte.html').read_bytes(),'bank')}
        for person in ('Tom','Celina'):
            checks['02-12/'+person+'-Material']=load(child(first,'reserve-'+person),'bank')
        for key,value in checks.items():
            bank=json.loads(value)
            assert bank==json.loads(z.read(key+'.json')),key
            if key.startswith('08-12/'):continue
            assert bank['buildCommit']==meta['commit']
            md=z.read(key+'.md').decode()
            assert meta['commit'] in md
            if key.endswith(('Tom-Material','Celina-Material')):
                for stage in bank['stages']:
                    assert stage['return'] in md
                    for key,task in stage.get('checks',{'all':stage}).items():
                        conflict=stage.get('conflicts',{}).get(key)
                        if conflict:
                            assert all(v in md for v in conflict.values())
                            continue
                        assert all(a in md for a in task['answers']+task['feedback'])
    with ZipFile(folder/'Fallakte-Sichtpruefung.zip') as z:
        assert z.testzip() is None
        shots=[n for n in z.namelist() if n.endswith('.jpg')]
        for n in shots:assert z.read(n).startswith(b'\xff\xd8\xff')
        assert all(any(engine in n for n in shots) for engine in ('chromium','webkit'))
        for name in ('Kandidat-02/Abnahme.json','Kandidat-08/Abnahme.json'):
            assert json.loads(z.read(name))['html_sha256']==meta['html_sha256']
    print('Fünf identische Inhaltsbanken, beide SCORM-Starts und',len(shots),'echte Screenshots im Download.')
if __name__=='__main__':verify(ROOT/'dist/Vorabkandidat')
