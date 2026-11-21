"""Measure what learners see in the real outer and inner browser documents."""
from playwright.sync_api import expect


def shared_bar(shell, module, screen, label):
    nav = shell.locator('#tagesnavigation')
    expect(nav).to_be_visible()
    expect(shell.locator('nav:visible')).to_have_count(1)
    expect(module.locator('header.top, header.top nav').first).to_be_hidden()
    expect(module.locator('nav:visible')).to_have_count(0)
    expect(nav.locator('button')).to_have_text(['← Tagesauswahl','Fallakten','Infokarten','Nach Neustart'])
    status = nav.locator('#gespraechsstand')
    if screen=='room':
        expect(status).to_be_visible()
        expect(status).to_have_text(label)
    else:
        expect(status).to_be_hidden()
        expect(nav.locator('[aria-current="page"]')).to_have_attribute('data-action','home')
    # The actual text ranges include wrapped lines. Check those as well as touch
    # rectangles and centre-point hit targets at the user's chosen font size.
    metrics = nav.evaluate("""nav => {
      const issues = [];
      const controls = [...nav.querySelectorAll('button,.wortmarke,#gespraechsstand')].filter(e=>e.getClientRects().length);
      const area = nav.getBoundingClientRect();
      for (const [i,el] of controls.entries()) {
        const r = el.getBoundingClientRect();
        if (r.left < -.5 || r.right > innerWidth+.5 || r.top < area.top-.5 || r.bottom > area.bottom+.5) issues.push(el.textContent);
        const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) {
          if (!walker.currentNode.textContent.trim()) continue;
          const range = document.createRange();
          range.selectNodeContents(walker.currentNode);
          for (const t of range.getClientRects()) {
            if (t.left < r.left-1 || t.right > r.right+1 || t.top < r.top-1 || t.bottom > r.bottom+1)
              issues.push('Beschriftung '+el.textContent);
          }
        }
        if (el.matches('button') && (Math.min(r.width,r.height)<43.9 ||
          !el.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2)))) issues.push('Touch '+el.textContent);
        for (const other of controls.slice(i+1)) {
          const s = other.getBoundingClientRect();
          if (Math.min(r.right,s.right)-Math.max(r.x,s.x)>1 && Math.min(r.bottom,s.bottom)-Math.max(r.y,s.y)>1)
            issues.push('Überlappung '+el.textContent);
        }
      }
      const frame = document.querySelector('iframe:not([hidden])').getBoundingClientRect();
      return {hoehe:area.height, inhalt_ab:frame.top, inhalt_bis:frame.bottom, viewport:innerHeight,
              fehler:issues, schrift:parseFloat(getComputedStyle(nav.querySelector('button')).fontSize)};
    }""")
    assert not metrics['fehler'], metrics
    assert abs(metrics['inhalt_ab']-metrics['hoehe'])<=1
    assert abs(metrics['inhalt_bis']-metrics['viewport'])<=1
    return metrics


def compare_navigation(browser, engine, address, photograph):
    rows = []
    for w,h,scale in [(820,1180,100),(1180,820,100),(820,1180,200),(1180,820,200),(390,650,100)]:
        page = browser.new_page(viewport={'width':w,'height':h},has_touch=True)
        row = dict(browser=engine, viewport=[w,h], schrift_prozent=scale)
        for build, folder in [('vorher','vor-navigation/dist/Version-A'),('nachher','A')]:
            page.goto(f'{address}/{folder}/host.html')
            shell = page.frame(name='sco')
            shell.locator('#erster-tag').tap()
            host = shell.locator('iframe')
            expect(host.content_frame.locator('[data-person=Laura]')).to_be_visible()
            module = host.element_handle().content_frame()
            for f in (shell,module):
                f.evaluate('p=>document.documentElement.style.fontSize=p+"%"',scale)
                f.evaluate('document.fonts.ready')
            photo = ((scale==100 and ((engine=='chromium' and w==820) or (engine=='webkit' and w==1180))) or
                     (scale==200 and engine=='webkit' and w==820 and build=='nachher'))
            record = {}
            for screen in ('home','room'):
                if screen=='room':
                    module.locator('[data-person=Laura]').tap()
                    expect(module.locator('#step')).to_have_text('Laura 1 von 5')
                if build=='vorher':
                    outer = shell.locator('nav')
                    inner = module.locator('header.top')
                    expect(inner).to_be_visible()
                    if screen=='home':
                        expect(outer).to_be_visible()
                    else:
                        expect(outer).to_be_hidden()
                    record[screen] = dict(hoehe=inner.bounding_box()['height']+(outer.bounding_box() or {'height':0})['height'])
                else:
                    expect(shell.locator('[data-action=recovery]')).to_be_visible()
                    record[screen] = shared_bar(shell,module,screen,'Laura 1 von 5 · ESA')
                    if scale==100 and w>=820:
                        assert record[screen]['hoehe'] < row['vorher'][screen]['hoehe']
                    if scale==200:
                        expect(shell.locator('.wortmarke')).to_be_hidden()
                        assert record[screen]['schrift']>=27
                if photo:
                    photograph(page,f'Navigation-{build}-{screen}-{w}-{scale}-{engine}')
            row[build] = record
        page.close()
        rows.append(row)
    return rows
