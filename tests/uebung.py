"""Test the built drill in isolation and its actual SCO in an instrumented LMS."""
import json, os
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from lxml import etree
from playwright.sync_api import sync_playwright, expect
from tagesauswahl import HOST, host

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist/Uebungsakte'
EXPECTED=[('B','K','sti'),('A','P','alltag'),('C','Cu','wirkung'),('B','H','wirkung')]

def run():
    bank=json.loads((OUT/'Uebungsakte-Material.json').read_text())
    work=(OUT/'Uebungsakte-Material.md').read_text()
    log=[]
    with TemporaryDirectory() as tmp, sync_playwright() as pw:
        site=Path(tmp)
        with ZipFile(OUT/'Uebungsakte-SCORM12.zip') as z:
            assert z.testzip() is None and z.read('index.html')==(OUT/'Uebungsakte.html').read_bytes()
            z.extractall(site)
        schema=etree.XMLSchema(etree.parse(str(site/'adlcp_rootv1p2.xsd')))
        manifest=etree.parse(str(site/'imsmanifest.xml'));schema.assertValid(manifest)
        assert manifest.find('.//{*}resource').get('href')=='index.html'
        (site/'host.html').write_text(HOST)
        with host(site) as url:
            for name in ('chromium','webkit'):
                b=getattr(pw,name).launch(executable_path=os.getenv(name.upper()+'_EXECUTABLE'))
                for i,tier in enumerate(bank['levels']):
                    p=b.new_page(has_touch=True,viewport=dict(width=820 if i%2==0 else 1180,height=1180 if i%2==0 else 820))
                    p.goto((OUT/'Uebungsakte.html').as_uri());assert p.locator('#bank').evaluate('e=>JSON.parse(e.textContent)')==bank
                    p.locator('#tier-'+tier).tap();p.locator('#start').tap()
                    for j,(key,method,section) in enumerate(EXPECTED):
                        stage=bank['stages'][j]
                        assert stage['claim'] in work
                        p.locator('#source').tap()
                        card=bank['cards'][method];part=card['sections'][section]
                        expect(p.locator('#cardTitle')).to_have_text(card['title']+' · '+part['title'])
                        expect(p.locator('#passage')).to_have_text(part['shortText' if i<2 else 'text'])
                        p.locator('#back').tap()
                        wrong=next(k for k in stage['short'] if k!=key)
                        for answer in (wrong,key):
                            if i<2 or j!=2:
                                expect(p.locator('#code')).to_have_count(0);p.locator('#answer-'+answer).tap()
                            else:
                                p.locator('#code').fill(answer);p.locator('#check').tap()
                            if answer==wrong:
                                expect(p.locator('#feedback')).to_have_text(stage['feedback']['ABC'.index(answer)])
                                expect(p.locator('#next')).to_have_count(0)
                                p.locator('#home').tap();p.locator('#resume').tap()
                                expect(p.locator('#feedback')).to_have_text(stage['feedback']['ABC'.index(answer)])
                        expect(p.locator('#next')).to_have_count(0)
                        p.locator('#source').tap();p.locator('#back').tap()
                        expect(p.locator('#send')).to_be_visible()
                        if j==0:
                            p.locator('#edit').tap();expect(p.locator('#send')).to_have_count(0)
                            p.locator('#answer-'+key).tap()
                        if j==0 and i==0:p.screenshot(path=OUT/f'{name}-Entwurf.jpg')
                        p.locator('#send').tap()
                        expect(p.get_by_role('status')).to_have_text(stage['reply'])
                        if j==1 and i in (0,3):p.screenshot(path=OUT/f'{name}-{tier}.jpg')
                        p.locator('#next').tap()
                    p.reload();p.locator('#tier-'+tier).tap();p.locator('summary').tap();p.locator('#entry-U3').tap()
                    expect(p.locator('h1')).to_contain_text('U3');expect(p.locator('#next')).to_have_count(0)
                    assert p.evaluate('[localStorage.length,sessionStorage.length]')==[0,0]
                    log.append([name,tier,4,'U3']);p.close()
                p=b.new_page();p.goto(url+'/host.html')
                f=p.frame_locator('iframe');f.locator('#tier-ESA').click();f.locator('#start').click();f.locator('#source').click()
                f.locator('#back').click();f.locator('#answer-B').click();f.locator('#send').click();f.locator('#next').click()
                p.locator('iframe').evaluate("f=>f.src='about:blank'")
                p.wait_for_function("calls.some(c=>c[0]==='LMSFinish')")
                assert p.evaluate('calls')==[['LMSInitialize',''],['LMSFinish','']]
                b.close()
    (OUT/'Browserpruefung.json').write_text(json.dumps({'commit':bank['buildCommit'],'wege':log,'scorm':'Initialize/Finish'},indent=2))
    print('Übung: acht vollständige Wege, zwei echte SCO-Starts und technische Beendigungen bestanden.')
if __name__=='__main__':run()
