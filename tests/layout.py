"""Real iframe layout comparison, with the last reviewed PR as the immutable baseline."""
import hashlib
import io
import os
import shutil
import subprocess
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from zipfile import ZipFile

from playwright.sync_api import expect, sync_playwright

from acceptance import LOCAL, QA, ROOT, QuietHandler, pane, save

BASE = '307156287cd26c07982ea19c44c84982746c5d30'
SIZES = [(1366,768), (1180,820), (820,1180), (1024,600), (820,650), (390,844)]
GEOMETRY = (ROOT/'tests/geometry.js').read_text()
SHOTS = QA/'vergleich'


def operate(control, touch):
    if touch:
        control.tap()
    else:
        control.click()


def school_frame(page, url, version, size):
    page.goto(url+'/host.html')
    page.locator('iframe').evaluate("""(e,[src,w,h])=>{
      e.width=w; e.height=h; e.src=src;
    }""", [version+'/index.html', *size])
    frame = page.frame(name='lesson')
    frame.locator('[data-person=Laura]').wait_for()
    frame.evaluate('document.fonts.ready')
    return frame


def to_refusal(frame, touch):
    def press(control):
        operate(control, touch)
    press(frame.locator('#level-ESA'))
    press(frame.locator('[data-person=Laura]'))
    for method in ('K','H'):
        pane(frame,'write-answer')
        press(frame.locator('#method-'+method))
        press(frame.locator('#send'))
        press(frame.get_by_role('button',name='Vorschlag beibehalten'))
    pane(frame,'write-answer')
    press(frame.get_by_role('button',name='Weiter nach dem Gespräch'))


def unchanged_page(m, size):
    assert m['viewport'] == list(size), (size,m)
    assert m['document'] == list(size) and m['global'] == [0,0], (size,m)
    assert not m['touchOrTextIssues'], (size,m['touchOrTextIssues'])


def independent(frame):
    # Scroll both containers to both ends, checking the sibling after each movement.
    return frame.evaluate("""() => {
      const chat=document.querySelector('#history'), work=document.querySelector('#work');
      const result={};
      for (const [id,e,other] of [['chat',chat,work],['work',work,chat]]) {
        const start=e.scrollTop, sibling=other.scrollTop;
        e.scrollTop=0;
        e.scrollTop=e.scrollHeight;
        result[id]=e.scrollTop;
        if (other.scrollTop!==sibling || scrollY!==0) throw Error('Gekoppelte Scrollbereiche: '+id);
        e.scrollTop=start;
      }
      return result;
    }""")


def check_state(m, size, state):
    unchanged_page(m,size)
    chat, answer = m['chat'], m['answer']
    if size[0] > 680:
        assert chat['visibleHeight'] > size[1] - 65 and answer['visibleHeight'] == chat['visibleHeight'], m
        assert abs(chat['x']) < 1 and abs(chat['width']-answer['x']) < 1, m
        assert abs(answer['x']+answer['width']-size[0]) < 1, m
        if state!='Rueckmeldung':
            assert m['message']['visibleHeight'] >= 30, ('aktuelle Nachricht',m)
    else:
        active = chat if state=='Nachricht' else answer
        assert active['width'] == size[0] and active['visibleHeight'] > size[1]-125, m
    if state in ('Auswahl','Hilfen'):
        assert m['sendReachable'] and m['send']['visibleHeight'] >= m['send']['height']-1, m
    if state=='Hilfen':
        assert m['focus']=='hint-current' and m['hint']['visibleHeight'] >= 40, m


def exercise(browser, engine, version, size, url, images):
    new = version == 'nachher'
    w,h = size
    touch = w < 1300
    ctx = browser.new_context(viewport={'width':max(1200,w+30),'height':max(900,h+30)},
                              has_touch=touch,device_scale_factor=1)
    page = ctx.new_page()
    frame = school_frame(page,url,version,size)
    to_refusal(frame,touch)
    states = {}
    def record(state):
        m = frame.evaluate(GEOMETRY)
        states[state] = m
        if new:
            check_state(m,size,state)
        if engine=='chromium' and size==(820,650):
            shot = SHOTS/f'{version}-{state}.jpg'
            page.screenshot(path=shot,type='jpeg',quality=78,clip=page.locator('iframe').bounding_box())
            images[shot.name] = hashlib.sha256(shot.read_bytes()).hexdigest()
        return m

    record('Nachricht')
    pane(frame,'write-answer')
    operate(frame.locator('#method-P'),touch)
    selected = record('Auswahl')
    for _ in range(2):
        operate(frame.locator('#help'),touch)
        if new:
            m = frame.evaluate(GEOMETRY)
            assert (m['chat'],m['scrollHistory'])==(selected['chat'],selected['scrollHistory']), m
            unchanged_page(m,size)
    expect(frame.locator('.hint')).to_have_count(2)
    hints = record('Hilfen')
    extra = {}
    if new:
        extra['scrollRange'] = independent(frame)
        if size in ((820,650),(1024,600)):
            assert all(x>0 for x in extra['scrollRange'].values()), extra
        if w==390:
            log = frame.locator('#history').text_content()
            pane(frame,'read-chat')
            expect(frame.locator('#history')).to_be_visible()
            expect(frame.locator('#work')).to_be_hidden()
            frame.locator('#history').evaluate('(e)=>e.scrollTop=0')
            pane(frame,'write-answer')
            assert frame.evaluate(GEOMETRY)['scrollWork']==hints['scrollWork']
            expect(frame.locator('#method-P')).to_have_attribute('aria-pressed','true')
            expect(frame.locator('.hint')).to_have_count(2)
            assert frame.locator('#history').text_content()==log
            # Resize the live frame across the breakpoint, keeping both panes' contents.
            page.locator('iframe').evaluate('(e)=>{e.width=844;e.height=390}')
            expect(frame.locator('#history')).to_be_visible()
            expect(frame.locator('#send')).to_be_visible()
            assert frame.locator('#history').evaluate('e=>e.scrollTop')==0
            page.locator('iframe').evaluate('(e)=>{e.width=390;e.height=844}')
            expect(frame.locator('#history')).to_be_hidden()
            expect(frame.locator('.hint')).to_have_count(2)
        elif size==(820,650):
            extra['enlargedText'] = large_text(frame,size)
    operate(frame.locator('#send'),touch)
    record('Rueckmeldung')
    for label in ('Vorschlag beibehalten','Vorschlag ändern'):
        b = frame.get_by_role('button',name=label)
        if new:
            expect(b).to_be_in_viewport(ratio=.99)
    operate(frame.get_by_role('button',name='Vorschlag ändern'),touch)
    expect(frame.locator('#method-P')).to_have_attribute('aria-pressed','false')
    assert page.evaluate('[scrollX,scrollY]')==[0,0]
    ctx.close()
    return dict(version=version, size=size, states=states, **extra)


def large_text(frame,size):
    before=frame.locator('.bubble').first.evaluate("e=>parseFloat(getComputedStyle(e).fontSize)")
    frame.evaluate("document.documentElement.style.fontSize='200%'")
    after=frame.locator('.bubble').first.evaluate("e=>parseFloat(getComputedStyle(e).fontSize)")
    assert after >= 2*before
    current=frame.evaluate(GEOMETRY)
    unchanged_page(current,size)
    assert current['sendReachable']
    frame.locator('#hint-current').scroll_into_view_if_needed()
    assert frame.evaluate(GEOMETRY)['hint']['visibleHeight'] > 40
    frame.evaluate("document.documentElement.style.removeProperty('font-size')")
    return dict(normal=before,doubled=after)


def accessibility(browser,engine,url):
    # 200% desktop page zoom halves the CSS viewport available for reflow.
    ctx=browser.new_context(viewport={'width':410,'height':325},has_touch=True,is_mobile=True,
                            reduced_motion='reduce')
    page=ctx.new_page()
    page.goto(url+'/nachher/index.html')
    page.locator('[data-person=Laura]').tap()
    pane(page,'write-answer')
    page.locator('#method-P').tap()
    page.locator('#help').tap()
    page.locator('#help').tap()
    measures=page.evaluate(GEOMETRY)
    unchanged_page(measures,(410,325))
    assert measures['sendReachable'] and measures['hint']['visibleHeight']>30
    motion=page.locator('#room .hint').first.evaluate("""e=>({
      preference:matchMedia('(prefers-reduced-motion: reduce)').matches,
      animations:e.getAnimations().length, scroll:getComputedStyle(e).scrollBehavior})""")
    assert motion==dict(preference=True,animations=0,scroll='auto')
    result=dict(reflow=measures,motion=motion)
    if engine=='chromium':
        cdp=ctx.new_cdp_session(page)
        cdp.send('Emulation.setPageScaleFactor',{'pageScaleFactor':2})
        zoom=page.evaluate('({scale:visualViewport.scale, width:visualViewport.width})')
        assert zoom['scale']>=1.99 and zoom['width'] <= 206, zoom
        result['pinch']=zoom
    ctx.close()
    return result


def run():
    SHOTS.mkdir(exist_ok=True)
    (QA/'layout.json').unlink(missing_ok=True)
    images, runs = {}, []
    with TemporaryDirectory() as temp:
        site = Path(temp)
        archive = subprocess.check_output(['git','archive','--format=zip',BASE,'index.html','assets','app','data'],cwd=ROOT)
        with ZipFile(io.BytesIO(archive)) as zipped:
            zipped.extractall(site/'vorher')
        (site/'nachher').mkdir()
        shutil.copyfile(LOCAL,site/'nachher/index.html')
        (site/'host.html').write_text('<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><style>*{margin:0}iframe{display:block;border:0}</style><iframe name="lesson" title="Unterricht"></iframe>')
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=temp))
        Thread(target=server.serve_forever,daemon=True).start()
        url='http://127.0.0.1:'+str(server.server_port)
        try:
            with sync_playwright() as p:
                for engine in ('chromium','webkit'):
                    exe=os.environ.get(engine.upper()+'_EXECUTABLE')
                    browser=getattr(p,engine).launch(**({'executable_path':exe} if exe else {}))
                    frames=[]
                    for size in SIZES:
                        for version in ('vorher','nachher'):
                            frames.append(exercise(browser,engine,version,size,url,images))
                        print(engine,size,'vier Zustände vor und nach der Optimierung geprüft',flush=True)
                    runs.append(dict(engine=engine,browser=browser.version,frames=frames,
                                     accessibility=accessibility(browser,engine,url)))
                    browser.close()
        finally:
            server.shutdown()
            server.server_close()
    save('layout',dict(baseline=BASE,runs=runs,screenshots=images))


if __name__=='__main__':
    run()
