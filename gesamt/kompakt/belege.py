"""Prüfe die separat vorliegenden Druckfassungen, alle Feldstatus und die CI-Artefakte."""
import argparse
from html import escape
import csv
import io
import json
import subprocess
from pathlib import Path
from zipfile import ZipFile
from abnahme import SOURCE,flat
from auslieferung import OUT,QA,ROOT,sha,pack
from sprachpruefung import documents,bank


def run(materialroot,ci,reference):
    docs=documents((OUT/'Fallakte-Gesamt.html').read_bytes())
    records=[]
    with ZipFile(SOURCE/'Work.zip') as z:
        rows=csv.reader(io.StringIO(z.read('Druckreferenzen_SHA256.tsv').decode('utf-8-sig')),delimiter='\t')
        next(rows)
        for h,name in rows:
            path=name.removeprefix('Druckreferenzen/')
            raw=(materialroot/path).read_bytes()
            assert raw==z.read(name) and h==sha(raw)
            records.append(dict(pdf=path,sha256=h))
    assert len(records)==18
    guide=materialroot/'02-12/04_Lehrkraft/Unterricht_Druck_und_Erwartungshorizont.pdf'
    pages=subprocess.check_output(['pdftotext','-layout',guide,'-']).decode().split('\f')
    keys=json.loads((QA/'Papierfachchecks.json').read_text())
    for p,begin in [('Laura','Laura 1–5:'),('Celina','MSA/AHR in Abschnittsfolge:'),('Tom','MSA/AHR in Abschnittsfolge:')]:
        code=' · '.join(x['code'] for x in keys if '/'+p+'_' in x['pdf'] and x['pdf'].endswith('_MSA.pdf'))
        assert code
        page=next(i for i,text in enumerate(pages,1) if begin+' '+code+'.' in flat(text))
        records.append(dict(lehrkraft=guide.name,seite=page,fall=p,schluessel=code,sha256=sha(guide.read_bytes())))
    (QA/'Druckabgleich.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
    physical=json.loads((QA/'Work-Gegenprobe.json').read_text())
    for engine in ['chromium','webkit']:
        for tier in ['Förder','ESA','MSA','AHR']:
            by_key={r['zustand']:r['bildschirm'] for r in physical if r['browser']==engine and r['niveau']==tier}
            assert len(by_key)==14
            end=by_key['LA-offen']
            for phrase in ['„digital geprüft“ oder „analog geprüft“ angekreuzt','nur in „Festhalten“','Deine erste Antwort bleibt stehen.','Fehlt das Kreuz oder ist „noch offen“ angekreuzt?','Die früheren Fragen sind am iPad noch nicht als bearbeitet markiert.']:
                assert phrase in end
            assert by_key['LA-abschluss']!=end and 'Fehlt das Kreuz' not in by_key['LA-abschluss']
            if tier=='Förder':
                assert 'Warum hilft die Nachricht Laura bei ihrer Frage? Nutze den biologischen Fakt.' in by_key['LA-eigen']
                assert 'Die Nachricht hilft Laura, weil …' in by_key['LA-eigen']
    md=ROOT/'dist/Runde-1'
    hefte={}
    for m,file in [('UB02','Materialvertrag'),('Tom','Tom-Material'),('Celina','Celina-Material')]:
        packed=bank(docs[m][0])
        exported=json.loads((md/(file+'.json')).read_text())
        assert exported==packed,m
        hefte[file+'.json']=json.dumps(packed,ensure_ascii=False,indent=2)
        hefte[file+'.md']=(md/(file+'.md')).read_bytes()
    family=bank(docs['UB08'][0])
    hefte['Familienrat-Material.json']=json.dumps(family,ensure_ascii=False,indent=2)
    from familienrat_build import markdown
    hefte['Familienrat-Material.md']='# Familienrat · aus dem ausgelieferten Modul\n\n'+markdown(family)
    hefte['Letzte_Materialkorrekturen_Work.md']=(QA/'Letzte_Materialkorrekturen_Work.md').read_bytes()
    for name in ['Celina_Ausfall_Aussagen.tsv','Celina_Ausfall_Rueckmeldungen_Lehrkraft.tsv']:
        hefte[name]=(QA/name).read_bytes()
    variants=csv.DictReader(io.StringIO(hefte['Celina_Ausfall_Aussagen.tsv'].decode()),delimiter='\t')
    parts=['<!doctype html><html lang="de"><meta charset="utf-8"><title>Celina · Aussagen bei Geräteausfall</title><style>@page{size:A4;margin:14mm}body{font:12pt/1.4 sans-serif;color:#172420}h1{font-size:19pt}h2{font-size:16pt;break-after:avoid}h3{margin:8pt 0 3pt}ol{margin:0;padding-left:22pt}article{break-inside:avoid}</style><h1>Celina · Aussagen bei Geräteausfall</h1><p>Suche deinen Abschnitt und deinen Vorschlag. Lies A, B und C. Schreibe deine Begründung auf den Celina-Bogen. Kreise dort deinen Buchstaben ein.</p>']
    previous=''
    for v in variants:
        if previous!=v['Abschnitt']:
            parts.append('<h2>'+escape(v['Abschnitt'])+'</h2>');previous=v['Abschnitt']
        parts.append('<article><h3>'+escape(v['Vorschlag'])+'</h3><ol type="A">'+''.join('<li>'+escape(v[l])+'</li>' for l in 'ABC')+'</ol></article>')
    hefte['Celina_Ersatzblatt_zum_Drucken.html']=''.join(parts)+'</html>'
    pack(QA/'Work-Materialexport.zip',hefte)
    # CI produced these independently on a fresh GitHub-hosted runner.
    artifacts={}
    for file in OUT.glob('Fallakte-*'):
        if file.suffix not in ('.html','.zip'):continue
        raw=file.read_bytes()
        assert (ci/'dist/Gesamt'/file.name).read_bytes()==raw
        artifacts[file.name]=dict(sha256=sha(raw),bytes=len(raw))
    assert len(artifacts)==8
    for name in ('Celina-Varianten','Lehrkraftstopp','Papierfachchecks'):
        a=json.loads((QA/(name+'.json')).read_bytes());b=json.loads((ci/'build/Gesamtpruefung'/(name+'.json')).read_bytes());assert a==b,name
    proof='Rueckfall-Vorbereitung.zip';raw=(reference/proof).read_bytes()
    assert sha(raw)=='562d27c68e0884a86c3f86494b9a7a1a8753b34282011626b0a98ced12df2563'
    with ZipFile(io.BytesIO(raw)) as z:
        assert z.testzip() is None
        for row in z.read('SHA256SUMS').decode().splitlines():
            h,p=row.split('  ');assert sha(z.read(p))==h
    (QA/'CI-Abgleich.json').write_text(json.dumps(dict(artefakte=artifacts,rueckfall=sha(raw),ci_lauf=45768593839),indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser()
    for arg in ('materialroot','ci','referenz'):p.add_argument(arg,type=Path)
    a=p.parse_args();run(a.materialroot,a.ci,a.referenz)
