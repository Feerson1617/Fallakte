"""Vergleicht die tatsächlich eingebetteten Verträge einschließlich der zwei Unterdokumente."""
import argparse
import base64
import csv
import gzip
import io
import json
import re
from collections import Counter
from pathlib import Path
from lxml import html
from auslieferung import ROOT,OUT,QA,SRC,sha,json_text,revision,rebuild

BASE='f5fa5db2cd6fe076c7c435b39b8b6485837aa2a2'
BASE_HASH={'PREP':'7e5b13d76a4b448e7d64a6a55be0d3a9e0f23a927ed1f04a380ed305bafa2d4b','UB02':'6f969460d00005fefd27fed985b6c95b7f1203bee0a9e4d72fcaaf9aea605cb2',
           'UB08':'0606de0b43bcbe4ef28b9fb0b036ee6ae1a8179d855b6af47baa5246438f1d2f','Tom':'c258f25999b179571ced66bbcc6586a71f7d901dae3e6b985e8ed48e49aa54b2','Celina':'52baa3cf356b1d472373449d0151bcde9f10bc1d099a2f074370ce33e2eb3e88'}
def documents(raw):
    docs={}
    def read(key,data):
        dom=html.fromstring(data);docs[key]=(dom,sha(data))
        for el in dom.xpath('//script[@type="application/octet-stream"]'):
            k=el.get('id').split('-')[-1]
            read({'vor':'PREP','02':'UB02','08':'UB08'}.get(k,k),base64.b64decode(el.text,validate=True))
    read('START',raw)
    return docs
def bank(dom):
    nodes=dom.xpath('//script[@id="bank" or @id="materialvertrag" or @id="material"]')
    return json.loads(nodes[0].text) if nodes else {}
def leaves(obj,path=''):
    if isinstance(obj,(dict,list)):
        for k,v in (obj.items() if isinstance(obj,dict) else enumerate(obj)):
            yield from leaves(v,(path+'/' if path else '')+str(k))
    else:yield path,obj

# Only presentation values may differ. Answer text, order, numeric/boolean flags,
# method restrictions, source data, question IDs and all graded keys are separate.
ALLOWED={
 'PREP':r'ui/reference|levels/[^/]+/(?:intro/question|chapters/\d+/(?:questions/\d+|paperCheck))/(?:options/\d+/(?:hints/\d|feedback)|hintsBeforeChoice/\d|afterSolutionCheck/options/\d+/feedback|screen|return)|levels/[^/]+/chapters/\d+/(?:paperPrompt|backToChat|observationPrompt)',
 'UB02':r'buildCommit|paperFallbackInstruction|consolidation/finalAdvice/levels/[^/]+/focus|stages/L0\d/(?:evidence|levels/[^/]+/(?:task|evidence|paperPrompt|returnPrompt|before/hints/\d|strategies/[^/]+/(?:hints/\d|evidence|feedback|options/\d+/feedback|correction/label)))',
 'Tom':r'buildCommit|stages/\d+/(?:task/[^/]+|return|paper/[^/]+|questions/\d+/0)',
 'Celina':r'buildCommit|stages/\d+/(?:task/[^/]+|return|paper/[^/]+|(?:checks/[^/]+/)?feedback/\d+)',
 'UB08':r'commit|time|cases/[^/]+/tasks/\d+/(?:helpByLevel/[^/]+|hints)/[0-3]|definitions/[^/]+|ui/[^/]+|evaluationHelpByLevel/[^/]+/\d|evaluation(?:Hints)?/[^/]+|stems/\d+/[01]|media/(?:fields/[^/]+ / Nach dem Prüfen/support|fields/Lauras Frage – Meine Antwort/parts/\d+|steps/[^/]+/(?:support|returnText|restartApplication/label|buttonText|orders/[^/]+/(?:action|screen)))'}
def pruefen(reference):
    old=documents(reference.read_bytes());new=documents((OUT/'Fallakte-Gesamt.html').read_bytes())
    assert {k:v[1] for k,v in old.items() if k!='START'}==BASE_HASH
    changes=[];proof={}
    for k,pattern in ALLOWED.items():
        a=dict(leaves(bank(old[k][0])));b=dict(leaves(bank(new[k][0])))
        assert a.keys()<=b.keys()
        for path in sorted(a.keys()|b.keys()):
            if path in a and a[path]==b[path]:continue
            specific=k=='PREP' and re.fullmatch(r'levels/(MSA|AHR)/chapters/4/questions/1/afterSolutionCheck/prompt',path)
            esa=k=='PREP' and re.fullmatch(r'levels/ESA/chapters/(4|7)/questions/1/solutionExplanation',path)
            assert specific or esa or re.fullmatch(pattern,path),(k,path)
            assert isinstance(b[path],str) or (path.endswith('/buttonText') and b[path] is None),(k,path)
            changes.append({'modul':k,'stelle':path,'alt':a.get(path),'neu':b[path]})
        proof[k]=dict(referenz=old[k][1],kandidat=new[k][1],werte=len(a),geaendert=sum(x['modul']==k for x in changes))
    (QA/'Bestandsvergleich.json').write_text(json_text(dict(basis=BASE,commit=revision(),module=proof,differenzen=changes)))
    (QA/'Referenzkarten.json').write_text(json_text(bank(old['PREP'][0])['cards']))
    return old,new,changes

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--referenz',type=Path)
    args=parser.parse_args()
    pruefen(args.referenz or rebuild(BASE,'gesamt/auslieferung.py','Gesamt')/'Fallakte-Gesamt.html')
