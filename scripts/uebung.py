"""Build the separate four-scene SCO and its paper handoff."""
import json
from zipfile import ZipFile, ZIP_DEFLATED
from modul_0212 import ROOT, commit, reference
from build import manifest

OUT=ROOT/'dist/Uebungsakte'

def build():
    OUT.mkdir(parents=True,exist_ok=True)
    bank=json.loads((ROOT/'data/uebung.json').read_text())
    bank.update(buildCommit=commit(),cards=json.loads((ROOT/'data/laura-0212.json').read_text())['cards'])
    md=['# Übungsakte · Material für Work',bank['buildCommit']]
    for step in bank['stages']:
        method,part=step['ref']
        label=reference(dict(method=method,section=part),bank)
        step['cardPrompt']='Infokarte öffnen · '+label
        md+=['## '+step['id']+' – '+step['title'],step['claim'],step['cardPrompt'],bank['cards'][method]['sections'][part]['text']]
        for level,instruction in bank['levels'].items():
            keys=step['short'] if level=='Foerder' else 'ABC'
            md+=['### '+level,instruction,*[k+' · '+step['answers']['ABC'.index(k)] for k in keys]]
            if level in ('MSA','AHR'):md.append(bank['return'])
        md+=['Lösung '+step['code'],*step['feedback']]
    data=json.dumps(bank,ensure_ascii=False,indent=2)
    (OUT/'Uebungsakte-Material.json').write_text(data)
    (OUT/'Uebungsakte-Material.md').write_text('\n\n'.join(md)+'\n')
    page=(ROOT/'module/uebung/index.html').read_text().replace('APP_JS',(ROOT/'module/uebung/app.js').read_text()).replace('SCORM_JS',(ROOT/'tagesauswahl/sitzung.js').read_text()).replace('BANK_JSON',data.replace('<','\\u003c'))
    (OUT/'Uebungsakte.html').write_text(page)
    with ZipFile(OUT/'Uebungsakte-SCORM12.zip','w',ZIP_DEFLATED) as z:
        z.writestr('index.html',page)
        z.writestr('imsmanifest.xml',manifest('Uebungsakte').replace(b'Fallakte.</',b'Fallakte - Uebungsakte</'))
        for schema in sorted((ROOT/'scorm').glob('*.xsd')):z.write(schema,schema.name)

if __name__=='__main__':build()
