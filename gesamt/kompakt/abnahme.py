"""Prüfe die gedruckten Fachanker und die tatsächlich zugänglichen Antworten im SCO."""
import csv,io,json,os,re,subprocess,tempfile
from pathlib import Path
from zipfile import ZipFile
from playwright.sync_api import sync_playwright,expect
from auslieferung import OUT,QA,SRC,sha,json_text
from sprachpruefung import documents,bank
from pruefen import enter
from karten import LEVELS

SOURCE=SRC/'kompakt'
def flat(s):return ' '.join(s.split())
def documents_pdf():
    pages={}
    with ZipFile(SOURCE/'Work.zip') as z:
        manifest=csv.reader(io.StringIO(z.read('Druckreferenzen_SHA256.tsv').decode('utf-8-sig')),delimiter='\t')
        next(manifest)
        for digest,name in manifest:
            raw=z.read(name);assert sha(raw)==digest
            text=subprocess.check_output(['pdftotext','-layout','-','-'],input=raw).decode()
            pages[name.removeprefix('Druckreferenzen/')]=text.rstrip('\f').split('\f')
    assert len(pages)==18
    return pages

def paper(banks,pages):
    rows=[]
    for person in ('Laura','Tom','Celina'):
        stages=banks['UB02']['stages'].values() if person=='Laura' else banks[person]['stages']
        for i,s in enumerate(stages,1):
            for tier in ('MSA','AHR'):
                laura=person=='Laura'
                page=(i+1)//2 if laura else 1+int(person=='Celina' and i>3)
                pdf='02-12/'+('01_Pflicht/' if laura else '02_Freiwillig/')+person+'_'+tier+'.pdf'
                text=flat(pages[pdf][page-1])
                prompt=s['levels'][tier]['task'] if laura else s['task'][tier]
                questions=prompt.splitlines()[1:] if laura and i==5 else [prompt]
                for question in questions:assert flat(question) in text,(pdf,i,question)
                answers=list(s['anchors'].values()) if laura else s['answers']
                # The original printed Celina variant is K. All other variants are checked at the iPad.
                start=0
                for letter,answer in zip('ABC',answers):
                    needle=letter+' '+flat(answer)
                    start=text.index(needle,start)+len(needle)
                printed_code={'Laura':'BCABC','Tom':'BCA','Celina':'BACBC'}[person][i-1]
                assert printed_code==s['code']
                rows.append(dict(pdf=pdf,seite=page,abschnitt=i,frage=prompt,aussagen=answers,code=s['code'],
                    papierstand='Kondomfassung im Druck; am Gerät auswahlabhängig' if person=='Celina' else 'wortgleich'))
    assert len(rows)==26
    return rows

def browser(banks):
    rows=[];stops=[]
    with tempfile.TemporaryDirectory() as td, sync_playwright() as pw:
        with ZipFile(OUT/'Fallakte-02-12-SCORM12.zip') as z:z.extractall(td)
        for engine in ('chromium','webkit'):
            path=Path(td)/'index.html' if engine=='webkit' else OUT/'Fallakte-02-12.html'
            with getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as b:
                page=b.new_page(viewport={'width':820,'height':1180},has_touch=True)
                page.goto(path.as_uri());f=enter(page,'02')
                for tier in LEVELS:
                    for i,s in enumerate(banks['UB02']['stages'].values(),1):
                        page.locator('[data-action=recovery]').click()
                        f.locator('#wieder-level-'+tier).click()
                        f.locator('[data-stage="'+s['id']+'"]').click()
                        f.locator('#lehrkraft summary').evaluate("s=>{if(!s.parentElement.open)s.click()}")
                        f.locator('#sicherung-oeffnen').click()
                        dlg=f.locator('#material-dialog')
                        expect(dlg).to_be_visible()
                        assert not dlg.locator('input').count()
                        words=dlg.inner_text()
                        assert 'Seite '+str(1 if tier in ('Foerder','ESA') else 3)+' · „Mein Schlussrat“' in words
                        for fact in banks['UB02']['consolidation']['facts']:assert fact in words
                        stops.append(dict(browser=engine,niveau=tier,abschnitt=i,wortlaut=words))
                        dlg.get_by_role('button',name='Schließen').click()
                for tier in ('MSA','AHR'):
                    for i,s in enumerate(banks['Celina']['stages'],1):
                        page.locator('[data-action=recovery]').click();f.locator('#wieder-level-'+tier).click()
                        f.locator('#wiederfall').get_by_role('button',name='Celina',exact=True).click()
                        f.locator('#abschnitte button').nth(i-1).click()
                        room=f.locator('#rahmen-reserve-Celina').element_handle().content_frame()
                        expect(room.locator('#step')).to_contain_text('Celina '+str(i)+' von')
                        for method in s['choices']:
                            room.locator('[id="method-'+method+'"]').click()
                            body=room.locator('#desk').inner_text();allowed=method in s['allowed']
                            if allowed:
                                check=s['checks'][method]
                                labels=room.locator('#desk p').all_inner_texts()
                                actual=[l for l in labels if re.match('^[ABC] · ',l)]
                                assert actual==[letter+' · '+v for letter,v in zip('ABC',check['answers'])]
                                assert 'Lies A, B und C hier am iPad' in body and 'Zusatzbogen nicht zur Hand?' not in body
                                assert f'Zusatzbogen Celina · Seite {1 if i<=3 else 2}' in body
                                if tier=='MSA' and i==4 and method=='K+Cu':
                                    page.screenshot(path=QA/(engine+'-Celina-4-Kupfer.jpg'),quality=65)
                                for code in [*[c for c in 'ABC' if c!=check['code']],check['code']]:
                                    room.locator('#code').fill(code);room.locator('#check').click()
                                    expect(room.locator('#feedback')).to_have_text(check['feedback']['ABC'.index(code)])
                                    assert room.locator('#send').is_visible()==(code==check['code'])
                            else:
                                assert not room.locator('#code,#send').count() and s['conflicts'][method]['full'] in body
                            rows.append(dict(browser=engine,niveau=tier,abschnitt=i,wahl=method,zulaessig=allowed,
                                             antworten=s['checks'][method]['answers'] if allowed else [],code=s['code'] if allowed else '',bildschirm=body))
                            room.locator('#edit').click()
                page.close()
    assert len(stops)==40 and len(rows)==140
    return rows,stops

def run():
    banks={m:bank(d) for m,(d,_) in documents((OUT/'Fallakte-Gesamt.html').read_bytes()).items()}
    rows=paper(banks,documents_pdf());(QA/'Papierfachchecks.json').write_text(json_text(rows))
    variants,stops=browser(banks)
    (QA/'Celina-Varianten.json').write_text(json_text(variants))
    (QA/'Lehrkraftstopp.json').write_text(json_text(stops))
if __name__=='__main__':run()
