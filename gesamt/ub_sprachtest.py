"""Sicht-, Quellen- und Verlaufsprüfung der beiden ausgelieferten Unterrichtstage."""
import base64,json,os
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from lxml import etree,html
from playwright.sync_api import sync_playwright,expect
from auslieferung import OUT,QA,sha

def module(page,day):
    page.locator('#'+('erster-tag' if day=='02' else 'zweiter-tag')).click()
    frame=page.locator('#arbeitsplatz iframe:visible').element_handle().content_frame()
    frame.locator('main').first.wait_for()
    return frame

def spalten(frame,left,right,width):
    a=frame.locator(left).bounding_box();b=frame.locator(right).bounding_box()
    assert a and b and frame.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
    if width>=650:assert a['x']+a['width']<=b['x']+1,(a,b)
    else:assert a['y']+a['height']<=b['y']+1,(a,b)

def run():
    folder=QA/'Sprachansichten';folder.mkdir(parents=True,exist_ok=True)
    proof={};rows=[]
    for name,allowed in [('02-12',['02']),('08-12',['02','08'])]:
        path=OUT/('Fallakte-'+name+'.html')
        with ZipFile(path.with_name(path.stem+'-SCORM12.zip')) as z:
            assert z.testzip() is None and z.read('index.html')==path.read_bytes()
            schema=etree.XMLSchema(etree.parse(str(Path(__file__).resolve().parents[1]/'scorm/adlcp_rootv1p2.xsd')))
            manifest=etree.parse(BytesIO(z.read('imsmanifest.xml')));schema.assertValid(manifest)
            assert manifest.xpath('string(//*[local-name()="schemaversion"])')=='1.2'
        doc=html.fromstring(path.read_bytes())
        mods={s.attrib['id'][-2:]:sha(base64.b64decode(s.text)) for s in doc.xpath('//script[@type="application/octet-stream"]')}
        assert list(mods)==allowed
        if name=='08-12':assert mods['02']==proof['02-12']['02']
        proof[name]=mods
    with sync_playwright() as pw:
        for engine in ('chromium','webkit'):
            with getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as browser:
                for i,level in enumerate(('Förder','ESA','MSA','AHR')):
                    for width,height in [(820,1180),(1180,820),(390,740)]:
                        page=browser.new_page(viewport=dict(width=width,height=height),has_touch=True)
                        issues=[];page.on('pageerror',lambda e:issues.append(str(e)))
                        page.goto((OUT/'Fallakte-08-12.html').as_uri())
                        f=module(page,'02');f.locator('#level-'+level.replace('Förder','Foerder')).click();f.locator('#neu').click()
                        spalten(f,'#beratung-verlauf','#beratung-arbeit',width)
                        if width==820:page.screenshot(path=folder/f'{engine}-{i}-02.jpg',quality=68)
                        f.locator('[data-strategy=K]').click()
                        if i<2:
                            method=f.evaluate("t=>window.LAURA.stages.L01.levels[t].strategies.K.options.find(o=>o.correct).id",level.replace('Förder','Foerder'))
                            f.locator('[data-option="'+method+'"]').click()
                        else:
                            f.locator('#pruefcode').fill(f.evaluate('window.LAURA.stages.L01.code'));f.locator('#fachcheck-pruefen').click()
                        f.locator('#nachricht-senden').click();f.locator('#beratung-weiter').click()
                        assert not f.locator('.fachmeldung').inner_text().strip()
                        f.locator('#fruehere-nachrichten').click()
                        expect(f.locator('[data-stage=L01][data-kind=send]')).to_be_visible()
                        page.locator('#zurueck').click();f=module(page,'08')
                        f.locator('#level-0').select_option(level);f.locator('#start').click()
                        spalten(f,'.msg','section.card',width)
                        f.get_by_text('Originalnachricht lesen',exact=True).click()
                        expect(f.locator('.msg')).to_contain_text('deine körperliche Gesundheit')
                        f.locator('#next').click()
                        if i>=2:f.locator('textarea').fill('Ihr ist Lauras Gesundheit wichtig.');f.locator('#compare').click()
                        f.locator('#answer-2').click();expect(f.locator('.retry')).to_be_visible()
                        f.locator('#answer-0').click()
                        assert not f.locator('.retry,#answer-2').count()
                        f.locator('#next').click()
                        f.get_by_text('Frühere Nachrichten',exact=True).click()
                        assert 'Du · Mutter' in f.locator('.chat-history').inner_text()
                        if i>=2:assert 'Ihr ist Lauras Gesundheit wichtig.' in f.locator('.chat-history').inner_text()
                        f.get_by_text('Frühere Nachrichten',exact=True).click()
                        if width==820:page.screenshot(path=folder/f'{engine}-{i}-08.jpg',quality=68)
                        assert not issues,issues
                        rows.append(dict(browser=engine,niveau=level,breite=width,hoehe=height))
                        page.close()
    (QA/'Sprachansichten.json').write_text(json.dumps(dict(module=proof,wege=rows),ensure_ascii=False,indent=2))
if __name__=='__main__':run()
