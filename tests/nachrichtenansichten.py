"""Compare actual old and new screens, and check the portraits in their three contexts."""
import base64
from pathlib import Path
from playwright.sync_api import expect

ROOT=Path(__file__).resolve().parents[1]
PEOPLE={
    'Mutter':('mutter',42,39,390), 'Freundin':('freundin',671,448,327),
    'Großmutter':('grossmutter',1,461,332), 'Vater':('vater',565,17,395),
}


def src(path):
    return 'data:image/webp;base64,'+base64.b64encode(path.read_bytes()).decode()


def inspect_figures(page,frame,bank):
    group=page.locator('#zweiter-tag img').get_attribute('src')
    expect(frame.locator('.letter img')).to_have_attribute('src',src(ROOT/'assets/laura.webp'))
    expect(frame.locator('.letter .message-text p')).to_have_text([
        ' '.join(bank['laura'][n-1] for n in ids) for ids in bank['lauraAbsaetze']])
    expect(frame.locator('.letter ol,.letter details')).to_have_count(0)
    distances={}
    for person,(key,x,y,size) in PEOPLE.items():
        img=frame.locator(f'.person-card img[data-person="{person}"]')
        expect(img).to_have_attribute('src',src(ROOT/'module/08-12/assets'/f'{key}.webp'))
        # Compare downsampled decoded pixels with the corresponding group rectangle.
        error=img.evaluate("""async (face,[url,x,y,size])=>{
          const group=new Image(); group.src=url; await Promise.all([group.decode(),face.decode()]);
          const pixels=(image,sx,sy,w)=>{
            const cv=document.createElement('canvas'); cv.width=cv.height=32;
            const ctx=cv.getContext('2d'); ctx.imageSmoothingQuality='high';
            ctx.drawImage(image,sx,sy,w,w,0,0,32,32); return ctx.getImageData(0,0,32,32).data;
          };
          const a=pixels(group,x,y,size),b=pixels(face,0,0,face.naturalWidth);
          let total=0; for(let i=0;i<a.length;i++) if(i%4!==3) total+=Math.abs(a[i]-b[i]);
          return total/(32*32*3);
        }""",[group,x,y,size])
        assert error<12,(person,error)
        distances[person]=round(error,2)
    return distances


def check_names(frame):
    wrapped=frame.locator('.person-card h3,.restart-people button').evaluate_all("""els=>els.filter(el=>{
        const text=[...el.childNodes].find(n=>n.nodeType===Node.TEXT_NODE);
        const range=document.createRange();range.selectNodeContents(text);
        return range.getClientRects().length!==1 || el.scrollWidth>el.clientWidth+1;
    }).map(el=>el.textContent)""")
    assert not wrapped,('Umgebrochener Personenname',wrapped)


def scroll_metrics(target):
    return target.evaluate("""el=>{
      const doc=document.documentElement;
      return {seite:Math.max(0,doc.scrollHeight-innerHeight),
        bis_zum_ziel:Math.round(Math.max(0,el.getBoundingClientRect().bottom+scrollY-innerHeight))};
    }""")


def inspect_views(browser,engine,previous,current,bank,shot):
    records=[]
    for width,height in ((390,650),(820,1180),(1180,820)):
        versions={}
        for tag,folder in [('vorher',previous),('aktuell',current)]:
            page=browser.new_page(viewport={'width':width,'height':height},has_touch=True,is_mobile=True)
            page.goto((folder/'Fallakte.html').as_uri())
            if tag=='aktuell' and width==1180:shot(page,engine+'-Tagesauswahl')
            page.locator('#zweiter-tag').tap()
            f=page.frame_locator('iframe')
            f.get_by_role('heading',name=bank['lead']).wait_for()
            f.locator('body').evaluate('async()=>{await document.fonts.ready}')
            def button(name):return f.get_by_role('button',name=name,exact=True)
            results={'Übersicht':scroll_metrics(button(bank['cases']['Mutter']['sections'][0]))}
            if tag=='aktuell':
                check_names(f)
                expect(f.locator('.inbox').first.get_by_role('heading',level=3)).to_have_text(['Mutter','Freundin'])
                expect(f.locator('.inbox').last.get_by_role('heading',level=3)).to_have_text(['Großmutter','Vater'])
                if width==390:shot(page,engine+'-Übersicht-390')
                if width==820:
                    distances=inspect_figures(page,f,bank)
                    shot(page,engine+'-Posteingang-iPad')
                    shot(f.locator('.person-card').first,engine+'-Pflichtkarte')
            for person,case in bank['cases'].items():
                for section in case['sections']:
                    button(section).tap()
                    results[section]=scroll_metrics(button('Hilfe'))
                    if tag=='aktuell':
                        filename=PEOPLE[person][0]+'.webp'
                        expect(f.locator('aside .sender img').first).to_have_attribute('src',src(ROOT/'module/08-12/assets'/filename))
                        if section==case['sections'][0]:
                            expect(f.locator('aside > ol li')).to_have_count(len(case['message']))
                            if width==1180 and person=='Freundin':shot(page,engine+'-Absender')
                    page.locator('[data-action="overview"]').tap()
                for number in (2,3):
                    page.locator('[data-action="recovery"]').tap()
                    button(person).tap()
                    button(case['sections'][1]).tap()
                    question=button(f"{number}. "+bank['questions'][number-1])
                    if person=='Freundin' and number==3:results['Wiederaufnahme']=scroll_metrics(question)
                    question.tap()
                    results[f'{person} · Frage {number}']=scroll_metrics(button('Hilfe'))
                    if tag=='aktuell' and number==3:
                        f.get_by_text('Ganze Nachricht lesen',exact=True).tap()
                        expect(f.locator('aside details[open] ol')).to_have_count(0)
                        expect(f.locator('aside details[open] .message-text p')).to_have_text(case['message'])
                page.locator('[data-action="overview"]').tap()
            if tag=='aktuell':
                page.locator('[data-action="recovery"]').tap()
                expect(f.get_by_role('heading',name='Hier kannst du weiterarbeiten.')).to_be_visible()
                check_names(f)
                for person,(key,*_) in PEOPLE.items():
                    expect(button(person).locator('img')).to_have_attribute('src',src(ROOT/'module/08-12/assets'/f'{key}.webp'))
                page.locator('[data-action="resources"]').tap()
                for summary in f.locator('details summary').all():summary.tap()
                expect(f.locator('main ol')).to_have_count(0)
                expect(f.get_by_text(bank['cards']['medizin']['lines'][4],exact=True)).to_be_visible()
            versions[tag]=results
            page.close()
        for view,now in versions['aktuell'].items():
            before=versions['vorher'][view]
            assert all(now[k]<=before[k]+1 for k in now),(engine,width,view,before,now)
        records.append(dict(browser=engine,viewport=[width,height],**versions))
    return records,distances
