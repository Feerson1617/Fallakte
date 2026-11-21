"""Reload the delivered classroom HTML/SCO, then recover from the paper section number."""
import hashlib
import os
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from zipfile import ZipFile

from playwright.sync_api import expect, sync_playwright

from acceptance import DATA, LOCAL, OUT, QA, QuietHandler, save

CHECK=Path(__file__).with_suffix('.js').read_text()
LAURA_LABELS=['Infektionsschutz','Schutz im Alltag','Lauras Entscheidung','Schmerzen und Infektionsschutz','Mein letzter Rat']
SIZES=((820,1180),(1180,820))
# Collect attempted persistence across reloads outside the application. Web Storage state is
# also inspected to catch property assignment rather than a call to setItem.
AUDIT="""() => {
  for (const [type,methods] of [['Storage',['setItem','removeItem','clear']],['IDBFactory',['open','deleteDatabase']]]) {
    const proto=window[type]?.prototype;
    if (!proto) continue;
    for (const method of methods) {
      const original=proto[method];
      proto[method]=function(...args) { reportPersistence(type+'.'+method); return original.apply(this,args); };
    }
  }
  let owner=document;
  while (owner && !Object.getOwnPropertyDescriptor(owner,'cookie')) owner=Object.getPrototypeOf(owner);
  const cookie=Object.getOwnPropertyDescriptor(owner,'cookie');
  Object.defineProperty(document,'cookie',{get:()=>cookie.get.call(document),set:value=>{
    reportPersistence('cookie');cookie.set.call(document,value);
  }});
}"""
# Before real reloads at Laura 3 and 5, send a proposal in the regular conversation.
WORK_TO="""number=>{
  const find=s=>document.querySelector(s);
  find('[data-person=Laura]').click();
  for (let i=1;i<number;i++){
    if (!find('#change-prior')) { find('#method-K').click();find('#send').click(); }
    find('#work .row button').click();
  }
  find('#change-prior')?.click();
  find('#method-H').click();
  find('#send').click();
}"""


def exercise(browser,engine,size,host,photos):
    scorm=host is not None
    ctx=browser.new_context(viewport=dict(zip(('width','height'),size)),has_touch=True)
    errors,storage=[],[]
    ctx.expose_function('reportPersistence',lambda operation:storage.append(operation))
    ctx.add_init_script('('+AUDIT+')()')
    page=ctx.new_page()
    page.on('pageerror',lambda err:errors.append(str(err)))
    page.goto(host or LOCAL.as_uri())
    view=page.frame(name='sco') if scorm else page

    def reload_app():
        if scorm:
            with page.expect_event('framenavigated',predicate=lambda f:f.name=='sco'):
                view.evaluate('location.reload()')
        else:
            page.reload()
        expect(view.locator('#open-recovery')).to_be_visible()

    # Changing the person after the level replaces the section choices. Visiting cards
    # or cancelling the picker must not start a case or unlock the other home cards.
    view.locator('#open-recovery').tap()
    picker=view.locator('#recovery')
    expect(picker.locator('fieldset').last).to_be_hidden()
    picker.get_by_role('button',name='ESA',exact=True).tap()
    picker.get_by_role('button',name='Tom',exact=True).tap()
    view.locator('#cards-nav').tap()
    view.locator('#resources .return').tap()
    expect(picker.locator('fieldset').last.get_by_role('button')).to_have_count(3)
    view.locator('#leave-recovery').tap()
    expect(view.locator('[data-person=Tom]')).to_be_disabled()

    records=[]
    for person,stages in DATA['cases'].items():
        for tier,label in DATA['meta']['levels'].items():
            for index,stage in enumerate(stages):
                reload_app()
                expect(view.locator('[data-person=Tom]')).to_be_disabled()
                if person=='Laura' and index in (2,4):
                    view.locator('#level-'+tier).tap()
                    view.evaluate(WORK_TO,index+1)
                    expect(view.locator('#step')).to_have_text(f'Laura {index+1} von 5')
                    expect(view.locator('#history .team').last).to_contain_text('Hormonspirale')
                    reload_app()
                    expect(view.locator('#history .team')).to_have_count(0)
                entry=view.get_by_role('button',name='Nach Neustart weitermachen',exact=True)
                expect(entry).to_be_in_viewport(ratio=.99)
                entry.tap()
                panel=view.locator('#recovery')
                if person!='Laura':panel.get_by_role('button',name=person,exact=True).tap()
                panel.get_by_role('button',name=label,exact=True).tap()
                titles=LAURA_LABELS if person=='Laura' else [step['title'] for step in stages]
                names=[f'{person} {i} – {title}' for i,title in enumerate(titles,1)]
                buttons=panel.locator('fieldset').last.get_by_role('button')
                expect(buttons).to_have_text(names)
                assert buttons.evaluate_all("bs=>bs.every(b=>b.getBoundingClientRect().height>=44 && b.scrollWidth<=b.clientWidth+1)")
                photograph=(tier=='Foerder' and person=='Laura' and index==2 and
                            ((engine=='chromium' and not scorm and size==SIZES[0]) or
                             (engine=='webkit' and scorm and size==SIZES[1])))
                if photograph:
                    expect(buttons.last).to_be_in_viewport(ratio=.99)
                    name=f'Wiederaufnahme-{engine}.jpg'
                    page.screenshot(path=QA/name,type='jpeg',quality=78)
                    photos[name]=hashlib.sha256((QA/name).read_bytes()).hexdigest()
                buttons.nth(index).tap()
                if photograph and not scorm:
                    name='Wiederaufnahme-Laura-3.jpg'
                    page.screenshot(path=QA/name,type='jpeg',quality=78)
                    photos[name]=hashlib.sha256((QA/name).read_bytes()).hexdigest()
                records.append(view.evaluate(CHECK,dict(person=person,tier=tier,index=index,stages=stages)))
                assert view.evaluate('[localStorage.length,sessionStorage.length,document.cookie]')==[0,0,'']
    calls=[]
    if scorm:
        with page.expect_event('framenavigated',predicate=lambda f:f.name=='sco'):
            page.locator('iframe').evaluate("e=>e.src='about:blank'")
        calls=page.evaluate('calls')
        assert calls and calls==[['LMSInitialize',''],['LMSFinish','']]*(len(calls)//2), calls
    assert not errors and not storage and not ctx.cookies(), (errors,storage)
    ctx.close()
    return dict(engine=engine,format='SCORM' if scorm else 'HTML',viewport=size,wege=records,
                neuladen_bei_laura=[3,5],storage=storage,js_errors=errors,scorm_aufrufe=calls)


if __name__=='__main__':
    photos,runs={},[]
    with TemporaryDirectory() as tmp:
        root=Path(tmp)
        with ZipFile(OUT/'Fallakte-SCORM12.zip') as z:z.extractall(root)
        (root/'host.html').write_text("""<!doctype html><style>*{margin:0}
        iframe{display:block;border:0;width:100vw;height:100vh}</style><script>
        window.calls=[];window.API=new Proxy({},{get:(_,k)=>(...a)=>{calls.push([k,...a]);return 'true'}});
        </script><iframe name="sco" src="index.html"></iframe>""")
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=tmp))
        Thread(target=server.serve_forever,daemon=True).start()
        url='http://127.0.0.1:'+str(server.server_port)+'/host.html'
        try:
            with sync_playwright() as p:
                for engine in ('chromium','webkit'):
                    exe=os.environ.get(engine.upper()+'_EXECUTABLE')
                    browser=getattr(p,engine).launch(**({'executable_path':exe} if exe else {}))
                    for i,size in enumerate(SIZES):
                        host=url if i==1 else None
                        runs.append(exercise(browser,engine,size,host,photos))
                        print(engine,size,runs[-1]['format'],'52 Abschnittseinstiege bestanden.',flush=True)
                    browser.close()
        finally:
            server.shutdown()
            server.server_close()
    save('wiederaufnahme',dict(runs=runs,screenshots=photos))
