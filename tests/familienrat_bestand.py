"""Run the original day-02 suites on the protected build, then exercise it in the new shell."""
from concurrent.futures import ThreadPoolExecutor
import base64
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from familienrat_build import ROOT, REF, OUT, BASE, DAY02, sha, git, payload
import release_abnahme

def run(suite):
    subprocess.run([sys.executable,'tests/'+suite+'.py'],cwd=REF,check=True)

def main():
    # These suites share generated files. Only the independent groups run concurrently.
    def group(suites):
        for suite in suites:run(suite)
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(group,[['runde1_vertrag','runde1_browser','runde1_karten'],
                             ['uebung','vertiefungen','runde2a_bedienung','runde1_bestand']]))
    release_abnahme.APP=OUT
    release_abnahme.PRACTICE=OUT
    release_abnahme.QA=ROOT/'build/Familienrat-Schutz'
    release_abnahme.main()
    reference=(REF/'dist/Vorabkandidat/Fallakte.html').read_bytes()
    delivered=(OUT/'Fallakte.html').read_bytes()
    assert reference.replace(payload(reference,b'08'),b'')==delivered.replace(payload(delivered,b'08'),b'')
    assert base64.b64decode(payload(delivered,b'02'))==base64.b64decode(payload(reference,b'02'))
    # Compare every path already in the frozen release. README is the shared branch landing page.
    tree=[]
    for line in git('ls-tree','-r','-z',BASE).split(b'\0'):
        if not line:continue
        metadata,raw_path=line.split(b'\t',1)
        path=raw_path.decode()
        current=git('ls-tree','HEAD','--',path).split(b'\t')[0]
        equal=metadata==current
        if path!='README.md':assert equal and (ROOT/path).read_bytes()==git('show',BASE+':'+path),path
        tree.append(dict(datei=path,referenz=metadata.decode(),kandidat=current.decode(),gleich=equal,
                         schutz='Branch-Liesmich' if path=='README.md' else 'geschützt'))
    (release_abnahme.QA/'Dateivergleich.json').write_text(json.dumps(dict(referenz=BASE,commit=git('rev-parse','HEAD').decode().strip(),
        rahmen_ohne_zweitmodul_bytegleich=True,html02=DAY02,dateien=tree),ensure_ascii=False,indent=2))
    files=['build/runde1/qa/browser.json','build/runde1/qa/material.json','build/runde1/qa/karten.json',
           'build/runde1/qa/bedienung.json','build/runde1/bestand.json']
    logs={}
    for f in files:
        data=json.loads((REF/f).read_text())
        assert data['commit']==BASE and data['html_sha256']==DAY02
        logs[Path(f).stem]=sha((REF/f).read_bytes())
    extra=json.loads((REF/'build/vertiefungen/Vertiefungspruefung.json').read_text())
    practice=json.loads((REF/'dist/Uebungsakte/Browserpruefung.json').read_text())
    assert len(extra)==8 and len(practice['wege'])==8
    laura=json.loads((REF/files[0]).read_text())
    result=dict(referenz=BASE,html_02=DAY02,pruefprotokolle=logs,wege_laura=sum(len(x['paths']) for x in laura['browsers']),
                vertiefungen=extra,uebung=practice)
    (release_abnahme.QA/'Referenz.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
