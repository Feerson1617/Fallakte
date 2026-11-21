"""Exercise the current standalone application inside real school-sized frames."""
import hashlib
import os
import shutil
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread

from playwright.sync_api import expect, sync_playwright

from acceptance import LOCAL, QA, ROOT, QuietHandler, pane, save

SIZES = [(1366,768), (1180,820), (820,1180), (1024,600), (820,650), (390,844)]
GEOMETRY = (ROOT/'tests/geometry.js').read_text()
SHOTS = QA/'rahmen'


def operate(control, touch):
    if touch:
        control.tap()
    else:
        control.click()


def school_frame(page, url, size):
    page.goto(url+'/host.html')
    page.locator('iframe').evaluate("""(e,[src,w,h])=>{
      e.width=w; e.height=h; e.src=src;
    }""", ['index.html', *size])
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


def exercise(browser, engine, size, url, images):
    w,h = size
    touch = w < 1300
    ctx = browser.new_context(viewport={'width':max(1200,w+30),'height':max(900,h+30)},
                              has_touch=touch,device_scale_factor=1)
    page = ctx.new_page()
    frame = school_frame(page,url,size)
    to_refusal(frame,touch)
    states = {}
    def record(state):
        m = frame.evaluate(GEOMETRY)
        states[state] = m
        check_state(m,size,state)
        if engine=='chromium' and size==(820,650):
            shot = SHOTS/f'{state}.jpg'
            page.screenshot(path=shot,type='jpeg',quality=78,clip=page.locator('iframe').bounding_box())
            images[shot.name] = hashlib.sha256(shot.read_bytes()).hexdigest()
        return m

    record('Nachricht')
    pane(frame,'write-answer')
    operate(frame.locator('#method-P'),touch)
    selected = record('Auswahl')
    labels = measure_labels(frame)
    if w >= 820:
        assert len({label['row'] for label in labels}) == 2, (size,labels)
    for _ in range(2):
        operate(frame.locator('#help'),touch)
        m = frame.evaluate(GEOMETRY)
        assert (m['chat'],m['scrollHistory'])==(selected['chat'],selected['scrollHistory']), m
        unchanged_page(m,size)
    expect(frame.locator('.hint')).to_have_count(2)
    hints = record('Hilfen')
    extra = {}
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
        expect(b).to_be_in_viewport(ratio=.99)
    operate(frame.get_by_role('button',name='Vorschlag ändern'),touch)
    expect(frame.locator('#method-P')).to_have_attribute('aria-pressed','false')
    assert page.evaluate('[scrollX,scrollY]')==[0,0]
    ctx.close()
    return dict(size=size, states=states, **extra)


def large_text(frame,size):
    before=frame.locator('.bubble').first.evaluate("e=>parseFloat(getComputedStyle(e).fontSize)")
    frame.evaluate("document.documentElement.style.fontSize='200%'")
    after=frame.locator('.bubble').first.evaluate("e=>parseFloat(getComputedStyle(e).fontSize)")
    assert after >= 2*before
    current=frame.evaluate(GEOMETRY)
    unchanged_page(current,size)
    assert current['sendReachable']
    for control in frame.locator('#help-dock button').all():
        expect(control).to_be_in_viewport(ratio=.99)
    frame.locator('#hint-current').scroll_into_view_if_needed()
    hint_height=frame.evaluate(GEOMETRY)['hint']['visibleHeight']
    assert hint_height > 40, hint_height
    frame.evaluate("document.documentElement.style.removeProperty('font-size')")
    return dict(normal=before,doubled=after,hint_visible_px=hint_height)


def measure_labels(view):
    labels = view.locator('.methods .method').evaluate_all("""buttons => buttons.map(b => {
      const range = document.createRange();
      range.selectNodeContents(b);
      const lines = [...range.getClientRects()];
      const box = b.getBoundingClientRect();
      return {name:b.textContent, lines:lines.length, row:box.top, font:getComputedStyle(b).fontSize,
              fits:lines.every(r => r.left >= box.left && r.right <= box.right &&
                                    r.top >= box.top && r.bottom <= box.bottom)};
    })""")
    assert len(labels) == 4 and all(m['lines']==1 and m['fits'] for m in labels), labels
    return labels


def phone_labels(browser,engine,url):
    folder = QA/'methoden'
    folder.mkdir(exist_ok=True)
    results = []
    for width in (360,390,420):
        page = browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True)
        page.goto(url+'/index.html')
        page.locator('[data-person=Laura]').tap()
        page.locator('#write-answer').tap()
        page.locator('#method-P').tap()
        page.evaluate('document.fonts.ready')
        sizes = {}
        for percent in (100,105,110):
            page.evaluate("n=>document.documentElement.style.fontSize=n+'%'",percent)
            sizes[percent] = measure_labels(page)
            if percent == 100:
                distinct_rows = {label['row'] for label in sizes[percent]}
                assert len(distinct_rows) == (4 if width<=390 else 2), (width,distinct_rows)
                shot = folder/f'{engine}-{width}.jpg'
                page.locator('.methods').screenshot(path=shot,type='jpeg',quality=85)
        results.append(dict(width=width, sizes=sizes, screenshot=shot.name,
                            sha256=hashlib.sha256(shot.read_bytes()).hexdigest()))
        page.close()
    return results


def accessibility(browser,engine,url):
    # 200% desktop page zoom halves the CSS viewport available for reflow.
    ctx=browser.new_context(viewport={'width':410,'height':325},has_touch=True,is_mobile=True,
                            reduced_motion='reduce')
    page=ctx.new_page()
    page.goto(url+'/index.html')
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
        shutil.copyfile(LOCAL,site/'index.html')
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
                        frames.append(exercise(browser,engine,size,url,images))
                        print(engine,size,'vier Gesprächszustände geprüft',flush=True)
                    runs.append(dict(engine=engine,browser=browser.version,frames=frames,
                                     accessibility=accessibility(browser,engine,url),
                                     phone_labels=phone_labels(browser,engine,url)))
                    browser.close()
        finally:
            server.shutdown()
            server.server_close()
    save('layout',dict(runs=runs,screenshots=images))


if __name__=='__main__':
    run()
