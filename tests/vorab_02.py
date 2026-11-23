"""Operate the first day in the packaged candidate and exercise real day changes."""
import hashlib,json,os,sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from lxml import etree
from playwright.sync_api import expect,sync_playwright
from runde1_bestand import switch_days, documents
from tagesauswahl import HOST,host
from runde1_orakel import correct_reason
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'dist/Vorabkandidat'
QA=ROOT/'build/Kandidat-02'

def main():
    QA.mkdir(parents=True,exist_ok=True)
    app=(TARGET/'Fallakte.html').read_bytes()
    modules=documents(app)
    assert modules['modul-02']==(ROOT/'dist/Runde-1/Fallakte.html').read_bytes() and len(app)<10_000_000
    log=[]
    with TemporaryDirectory() as td,sync_playwright() as pw:
        site=Path(td)
        with ZipFile(TARGET/'Fallakte-SCORM12.zip') as z:
            assert z.testzip() is None and z.read('index.html')==app
            z.extractall(site)
        etree.XMLSchema(etree.parse(str(site/'adlcp_rootv1p2.xsd'))).assertValid(etree.parse(str(site/'imsmanifest.xml')))
        (site/'host.html').write_text(HOST)
        with host(site) as base:
            for engine in ('chromium','webkit'):
                b=getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE'))
                for lms,size in ((False,(820,1180)),(True,(1180,820))):
                    url=base+'/host.html' if lms else (TARGET/'Fallakte.html').as_uri()
                    log.append(switch_days(b,engine,url,lms,size))
                for i,tier in enumerate(('Foerder','ESA','MSA','AHR')):
                    p=b.new_page(has_touch=True,viewport={'width':820 if i%2==0 else 1180,'height':1180 if i%2==0 else 820})
                    p.goto(base+'/host.html')
                    shell=p.frame(name='sco');shell.locator('#erster-tag').tap()
                    f=shell.frame_locator('iframe[title^=Mittwoch]')
                    f.locator('#level-'+tier).tap();f.locator('#neu').tap()
                    for j,(m,code) in enumerate(zip(('K','K+Cu','K+P','K+H','K'),'BCABC')):
                        sid='L0'+str(j+1);expect(f.locator('#beratung-stage')).to_have_attribute('data-stage',sid)
                        choice=f.locator('[data-strategy="'+m+'"]')
                        if not choice.is_visible():f.locator('#weitere-strategien summary').tap()
                        choice.tap()
                        if i<2:
                            options=f.locator('#begruendungen button');options.nth(correct_reason(tier,sid,m,options.all_text_contents())).tap()
                        else:f.locator('#pruefcode').fill(code);f.locator('#fachcheck-pruefen').tap()
                        f.locator('#nachricht-senden').tap()
                        f.locator('#beratung-fertig' if j==4 else '#beratung-weiter').tap()
                    expect(f.locator('[data-optional]').first).to_have_text('Tom')
                    expect(f.locator('[data-optional=Tom]')).to_be_enabled()
                    expect(f.locator('[data-optional=Celina]')).to_be_disabled()
                    f.locator('[data-optional=Tom]').tap()
                    tom=f.frame_locator('#rahmen-reserve-Tom')
                    for j,code in enumerate('BCA'):
                        if j==0:tom.locator('#method-K').tap()
                        if i<2:tom.locator('#answer-'+code).tap()
                        else:
                            if j:tom.locator('#source').tap();tom.locator('#back').tap()
                            tom.locator('#code').fill(code);tom.locator('#check').tap()
                        tom.locator('#send').tap();tom.locator('#next').tap()
                    expect(f.locator('[data-optional=Celina]')).to_be_enabled()
                    if i==1:p.screenshot(path=QA/f'{engine}-Falluebersicht.jpg')
                    p.reload();shell=p.frame(name='sco');shell.locator('#erster-tag').tap()
                    f=shell.frame_locator('iframe[title^=Mittwoch]');shell.locator('[data-action=recovery]').tap()
                    f.locator('#wieder-level-'+tier).tap();f.locator('#abschnitte button').nth(2).tap()
                    expect(f.locator('#beratung-stage')).to_have_attribute('data-stage','L03')
                    expect(f.locator('#beratung-verlauf [data-kind=send]')).to_have_count(0)
                    log.append({'browser':engine,'niveau':tier,'gesendet':5,'neustart':'Laura 3'});p.close()
                b.close()
    (QA/'Abnahme.json').write_text(json.dumps({'wege':log,'html_sha256':hashlib.sha256(app).hexdigest()},indent=2))
if __name__=='__main__':main()
