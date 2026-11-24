"""Vergleicht beide Planungsverträge, Original-PDFs und tatsächlich gebaute HTML-Daten."""
import json
import re
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from lxml import etree, html

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vorbereitung'))
from bauen import ROOT, OUT, PLAN, QA, contracts, digest, json_text, revision
from vorbereitung_bestand import verify


def compact(text):
    return re.sub(r'\s+','', text)


def run():
    s,c=contracts()
    ub=json.loads(subprocess.check_output(['git','show',s['protectedUB']+':data/laura-0212.json'],cwd=ROOT))['cards']
    built=(OUT/'Vorbereitung.html').read_bytes()
    page=html.fromstring(built)
    assert page.xpath('//meta[@name="revision"]/@content')==[revision()]
    material=page.get_element_by_id('material').text
    fingerprint=digest(material.encode())
    # Datenblock aus der geprüften Offline-Auslieferung d89e667, Actions 45441105166.
    assert fingerprint=='0b108ea97dab994cb9d7bd2f5df1bd443f3b25816f60dc22edd2e986fab51ee7'
    bank=json.loads(material)
    for k in ('levels','ui','visualBriefs','title','pearlNote'):
        assert bank[k]==s[k]
    assert set(bank['graphics'])==set(s['sequence'])
    for k,g in bank['graphics'].items():
        svg=etree.fromstring(g.encode())
        assert svg.get('aria-label')==s['visualBriefs'][k]['alt']
    assert not page.xpath('//*[@src or @href]'), 'Externe HTML-Ressource'
    with ZipFile(OUT/'Vorbereitung-SCORM12.zip') as z, TemporaryDirectory() as folder:
        assert z.testzip() is None and z.read('index.html')==built
        z.extractall(folder)
        doc=etree.parse(str(Path(folder)/'imsmanifest.xml'))
        wrapper=Path(folder)/'pruefschema.xsd'
        wrapper.write_text('<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">'
            '<xs:import namespace="http://www.adlnet.org/xsd/adlcp_rootv1p2" schemaLocation="adlcp_rootv1p2.xsd"/>'
            '<xs:import namespace="http://www.imsproject.org/xsd/imscp_rootv1p1p2" schemaLocation="imscp_rootv1p1p2.xsd"/>'
            '</xs:schema>')
        schema=etree.XMLSchema(etree.parse(str(wrapper)))
        schema.assertValid(doc)
        assert doc.xpath('string(//*[local-name()="schemaversion"])')=='1.2'
        sco=doc.xpath('//*[local-name()="resource"]')[0]
        assert sco.attrib['{http://www.adlnet.org/xsd/adlcp_rootv1p2}scormtype']=='sco' and sco.get('href')=='index.html'
    nums={'Kapitel':0,'Felder':0,'UB_Abschnitte':0,'Papierchecks':0,'Hauptfragen_mit_Einstieg':0,'Fehlantworten':0}
    measurements=[]
    with ZipFile(PLAN) as z, TemporaryDirectory() as folder:
        pdfs={}
        for item in z.namelist():
            if item.endswith('.pdf'):
                p=Path(folder)/Path(item).name
                p.write_bytes(z.read(item))
                pdfs[p.stem]=compact(subprocess.check_output(['pdftotext','-layout',str(p),'-']).decode())
        refs=pdfs['Infokarten_Proberunde_Referenz']
        for level,lesson in s['levels'].items():
            cards=c['levels'][level]
            student=pdfs['Infokarten_'+level]
            low=level in ('Foerder','ESA')
            assert [ch['id'] for ch in lesson['chapters']]==s['sequence']
            qs=[lesson['intro']['question']]
            for ch in lesson['chapters']:
                key=ch['id']
                card=cards[int(key[0])-1]
                assert ch['title']==next(i['title'] for i in card['chapters'] if i['id']==key)
                assert len(ch['questions'])==len(ch['cardEntries'])==2
                for e in ch['cardEntries']:
                    f=next(f for f in card['fields'] if f['id']==e['fieldId'])
                    assert (f['answer'],f['number'],f['section'])==(e['exactEntry'],e['number'],e['sectionId'])
                    nums['Felder']+=1
                sections=[row for row in card['sections'] if row['phase']==key[-1]]
                assert ch['information']==[dict(sectionId=i['id'],title=i['title'],text=i['completedText']) for i in sections]
                for i in sections:
                    original=ub[card['method']]['sections'][i['id']]
                    assert (original['title'],original['shortText' if low else 'text'])==(i['title'],i['sourceText'])
                    assert compact(i['completedText']) in refs, (level,key,i['id'],'Referenzdruck')
                    template=compact(i['template'])
                    parts=re.split(r'\{(\d+)\}',template)
                    pattern=''.join(re.escape(fragment) if j%2==0 else fragment+r'_+' for j,fragment in enumerate(parts))
                    assert re.search(pattern,student),(level,key,i['id'],'Schülerdruck')
                    nums['UB_Abschnitte']+=1
                qs.extend(ch['questions'])
                nums['Kapitel']+=1
                pc=ch['paperCheck']
                if pc:
                    assert not low and key.endswith('A')
                    assert pc['code']=='BACB'[int(key[0])-1]
                    assert all(pc[k]==v for k,v in card['paperCheck'].items())
                    assert [o['code'] for o in pc['options']]==list('ABC')
                    abc=compact(pc['prompt'])+''.join(o['code']+compact(o['text']) for o in pc['options'])
                    assert abc in student,(level,key,'Papierauswahl')
                    nums['Papierchecks']+=1
                words=sum(len(i['text'].split()) for i in ch['information'])+len(ch['supportingInfo'].split())
                measurements.append(dict(Niveau=level,Kapitel=key,Woerter_Information=words,
                    Woerter_Hauptfragen_mit_Auswahl=sum(len(q['prompt'].split())+sum(len(o['text'].split()) for o in q['options']) for q in ch['questions']),
                    Woerter_Abschrift=sum(len(e['exactEntry'].split()) for e in ch['cardEntries'])))
            nums['Hauptfragen_mit_Einstieg']+=len(qs)
            checks=qs+[ch['paperCheck'] for ch in lesson['chapters'] if ch['paperCheck']]
            for q in checks:
                assert len(q['hintsBeforeChoice'])==5
                for item in (q,q['afterSolutionCheck']):
                    assert sum(o['correct'] for o in item['options'])==1
                assert len(q['options'])==(2 if level=='Foerder' else 3)
                for o in q['options']:
                    if not o['correct']:
                        assert o['feedback'] and len(o['hints'])==5
                        nums['Fehlantworten']+=1
    return dict(commit=revision(),Vertrag=nums,Umfang=measurements,Material_SHA256_wie_d89e667=fingerprint,
                Bestand=verify(Path(sys.argv[1]).resolve()))


if __name__=='__main__':
    QA.mkdir(exist_ok=True,parents=True)
    result=run()
    (QA/'Vertragspruefung.json').write_text(json_text(result))
    print(result['Vertrag'])
