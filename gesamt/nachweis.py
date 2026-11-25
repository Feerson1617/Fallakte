"""Fetch attestations for the three newly requested runs of the original release workflows."""
import json
import os
import time
import urllib.request
from urllib.error import HTTPError
from auslieferung import PREP,JOINT,FIRST,QA,json_text
RUNS={45634918917:(PREP,'vorbereitung.yml'),45634912263:(FIRST,'unterricht.yml'),45634906500:(JOINT,'familienrat.yml')}

def request(path):
    headers={'Accept':'application/vnd.github+json','User-Agent':'Fallakte-Integrationspruefung'}
    token=os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if token:headers['Authorization']='Bearer '+token
    url='https://api.github.com/repos/Feerson1617/Fallakte/actions/'+path
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=35) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code<500 or attempt==3:raise
            time.sleep(5)

def collect():
    results=[]
    for id_,(expected,workflow) in RUNS.items():
        while True:
            run=request(f'runs/{id_}')
            assert run['head_sha']==expected and run['path'].endswith('/'+workflow) and run['event']=='workflow_dispatch'
            if run['status']=='completed':break
            print('Lauf',id_,run['status'],flush=True);time.sleep(25)
        assert run['conclusion']=='success',(run['html_url'],run['conclusion'])
        jobs=request(f'runs/{id_}/attempts/{run["run_attempt"]}/jobs')['jobs']
        assert jobs and all(j['conclusion']=='success' for j in jobs),[(j['name'],j['conclusion']) for j in jobs]
        results.append(dict(lauf=id_,commit=expected,url=run['html_url'],versuch=run['run_attempt'],
                            beginn=run['run_started_at'],ergebnis=run['conclusion'],jobs=[j['name'] for j in jobs]))
    QA.mkdir(exist_ok=True,parents=True)
    (QA/'Referenzlaeufe.json').write_text(json_text(results))
if __name__=='__main__':collect()
