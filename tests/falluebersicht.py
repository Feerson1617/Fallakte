"""Compare the delivered overview to the previous release in an equally sized SCO."""
from playwright.sync_api import expect

VIEWS = [
    ('iPad-hoch',820,1180,100), ('iPad-quer',1180,820,100),
    ('Einbettung',820,520,100), ('Grosse-Schrift',820,650,200),
    ('Zoom-Reflow',410,325,100)
]

GEOMETRY = """() => {
  const box = el => {
    const {x,y,width,height,right,bottom} = el.getBoundingClientRect();
    return {x,y,width,height,right,bottom};
  };
  const get = s => box(document.querySelector(s));
  const controls = [...document.querySelectorAll('header button,header a,#home button')]
    .filter(e => e.getClientRects().length);
  const issues = [];
  for (const [i,e] of controls.entries()) {
    const r = box(e);
    if (r.x < -1 || r.right > innerWidth+1 || e.scrollWidth > e.clientWidth+2 ||
        (e.matches('button') && Math.min(r.width,r.height)<43.9)) issues.push(e.textContent);
    for (const other of controls.slice(i+1)) {
      const s = box(other);
      if (Math.min(r.right,s.right)-Math.max(r.x,s.x)>1 &&
          Math.min(r.bottom,s.bottom)-Math.max(r.y,s.y)>1) issues.push([e.textContent,other.textContent]);
    }
  }
  return {breite:innerWidth, seitenbreite:document.documentElement.scrollWidth,
    scrollweg:document.documentElement.scrollHeight-innerHeight, laura:get('.case-card.laura'),
    celina:get('.case-card.celina'), tom:get('.case-card.tom'), level:get('#levels'),
    auftrag:document.querySelector('.assignment') ? get('.assignment') : null,
    einstieg:get('[data-person=Laura]'), neustart:get('#open-recovery'),
    gesperrt:[...document.querySelectorAll('[data-person]:disabled')].map(b=>b.dataset.person),
    ueberlappungen_oder_ueberlauf:issues};
}"""


def compare_overviews(browser, engine, address, photograph):
    records = []
    for name,width,height,fontsize in VIEWS:
        row = dict(browser=engine, ansicht=name, viewport=[width,height], schrift_prozent=fontsize)
        page = browser.new_page(viewport=dict(width=width,height=height),has_touch=True)
        for state,site in [('vorher','gemeinsam/dist/Version-A'),('nachher','A')]:
            page.goto(f'{address}/{site}/host.html')
            shell = page.frame(name='sco')
            shell.locator('#erster-tag').tap()
            host = shell.locator('iframe')
            expect(host.content_frame.locator('[data-person=Tom]')).to_be_visible()
            frame = host.element_handle().content_frame()
            shell.evaluate('size => document.documentElement.style.fontSize=size+"%"',fontsize)
            frame.evaluate('size => document.documentElement.style.fontSize=size+"%"',fontsize)
            frame.evaluate('document.fonts.ready')
            m = frame.evaluate(GEOMETRY)
            row[state] = m
            if state=='vorher':
                assert m['gesperrt']==['Celina','Tom']
            else:
                assert m['gesperrt']==[] and m['seitenbreite']==width, (name,m)
                assert not m['ueberlappungen_oder_ueberlauf'], (name,m)
                laura, extras, task = m['laura'], m['celina'], m['auftrag']
                assert m['level']['bottom']<=laura['y'] and task['bottom']<=extras['y']
                if width>=800 and fontsize==100:
                    assert laura['right']<=task['x'] and extras['right']<=m['tom']['x']
                    assert laura['height']>1.25*extras['height']
                    assert laura['y']<row['vorher']['laura']['y']
                    assert m['einstieg']['bottom']<row['vorher']['einstieg']['bottom']
                else:
                    assert laura['bottom']<=task['y']+1
                expect(frame.locator('#case-order')).to_have_text('Beginne mit Laura. Celina und Tom sind Zusatzfälle.')
                restart = shell.locator('[data-action=recovery]')
                expect(restart).to_be_in_viewport(ratio=.99)
                m['neustart'] = restart.evaluate('el=>el.getBoundingClientRect().toJSON()')
                m['neustart_im_rahmen'] = True
                expect(frame.locator('header.top')).to_be_hidden()
                expect(frame.locator('#open-recovery')).to_have_count(1)
                expect(frame.locator('footer,.intro,.subject')).to_have_count(0)
                expect(frame.locator('.laura .role')).to_have_text('Hauptfall')
            if ((engine=='chromium' and (state=='nachher' or name in ('iPad-hoch','Einbettung'))) or
                (engine=='webkit' and name=='iPad-quer')):
                photograph(page,f'Uebersicht-{state}-{name}-{engine}')
        if name=='Einbettung':
            shell.locator('[data-action=recovery]').tap()
            frame.locator('#recovery').get_by_role('button',name='ESA',exact=True).tap()
            if engine=='webkit':
                photograph(page,'Wiedereinstieg-kleines-Fenster')
            frame.get_by_role('button',name='Laura 3 – Lauras Entscheidung').tap()
            expect(frame.locator('#step')).to_have_text('Laura 3 von 5')
            expect(frame.locator('#open-recovery')).to_be_hidden()
            expect(frame.locator('#card-cue')).to_be_in_viewport(ratio=.99)
            expect(frame.locator('#help')).to_be_in_viewport(ratio=.99)
        if name=='Grosse-Schrift':
            frame.locator('[data-person=Laura]').tap()
            frame.locator('#help').tap()
            expect(frame.locator('#hint-current')).to_be_in_viewport()
            expect(frame.locator('#card-cue')).to_be_in_viewport(ratio=.99)
            if engine=='webkit':
                photograph(page,'Laura-Hilfe-grosse-Schrift')
        if name=='Zoom-Reflow' and engine=='chromium':
            cdp = page.context.new_cdp_session(page)
            cdp.send('Emulation.setPageScaleFactor',{'pageScaleFactor':2})
            row['pinch_zoom'] = page.evaluate('visualViewport.scale')
            assert row['pinch_zoom']>=1.99
            photograph(page,'Uebersicht-Pinchzoom-200')
        page.close()
        records.append(row)
    return records
