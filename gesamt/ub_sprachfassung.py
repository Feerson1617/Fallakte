"""Zwei Unterrichtstage getrennt von der eigenständig ausgelieferten Vorbereitung bauen."""
import argparse
import base64
from pathlib import Path
import re
import sys
from auslieferung import ROOT, OUT, JOINT, PAYLOAD, manifest, pack, rebuild, sha, single_replace
sys.path.insert(0,str(ROOT/'scripts'))
from modul_0212 import build as laura, commit
from familienrat_build import module_document

def bauen(joint):
    shell=(joint/'Fallakte.html').read_bytes()
    assert sha(shell)=='254e5d06cb9190250bacc63fa9eea6c118846b45ce2b305ffa640d766f44a820'
    shell=shell.decode()
    assert len(re.findall(PAYLOAD,shell))==2
    shell=re.sub(PAYLOAD,'',shell)
    shell=single_replace(shell,'id="zweiter-tag"','id="zweiter-tag" data-modulnavigation')
    shell=single_replace(shell,'</head>',f'<meta name="revision" content="{commit()}"></head>')
    days={'02':laura().read_bytes(),'08':module_document()[1].encode()}
    OUT.mkdir(parents=True,exist_ok=True)
    for version,allowed in [('02-12',['02']),('08-12',['02','08'])]:
        page=shell
        if '08' not in allowed:page=single_replace(page,'data-entry="modul-08"','disabled')
        embeds=''.join(f'<script id="modul-{day}" type="application/octet-stream">{base64.b64encode(days[day]).decode()}</script>' for day in allowed)
        raw=single_replace(page,'</body>',embeds+'</body>').encode()
        name='Fallakte-'+version
        (OUT/(name+'.html')).write_bytes(raw)
        schema={p.name:p.read_bytes() for p in (ROOT/'scorm').glob('*.xsd')}
        pack(OUT/(name+'-SCORM12.zip'),dict(schema,**{'index.html':raw,'imsmanifest.xml':manifest('FALLAKTE-'+version)}))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--unterricht',type=Path)
    args=parser.parse_args()
    bauen(args.unterricht or rebuild(JOINT,'scripts/familienrat_build.py','Familienrat'))
