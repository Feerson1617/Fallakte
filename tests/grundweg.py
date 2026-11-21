"""Observe the short teaching path through real controls without retries or hints."""
from collections import Counter
import re
from playwright.sync_api import expect

# Include content below the fold. Exclude closed disclosures, disabled hidden steps
# and unexpanded select menus. Count repeated passages once per screen and position.
VISIBLE = """main=>{
 const disclosed=e=>{
   for(let node=e;node;node=node.parentElement)
     if(node.matches('details:not([open])') && !node.querySelector(':scope > summary')?.contains(e)) return false;
   return true;
 };
 const words=[], walker=document.createTreeWalker(main,NodeFilter.SHOW_TEXT);
 while(walker.nextNode()){
   const n=walker.currentNode, e=n.parentElement;
   if (!e || e.closest('script,style,option,textarea,[hidden]') || !disclosed(e)) continue;
   const range=document.createRange();range.selectNodeContents(n);
   if (range.getBoundingClientRect().width && n.textContent.trim()) words.push(n.textContent.trim());
 }
 for(const s of main.querySelectorAll('select')) if(disclosed(s) && !s.closest('[hidden]') && s.getClientRects().length && s.offsetWidth)
   words.push(s.selectedOptions[0]?.textContent || '');
 return words;
}"""


def measure_route(browser,engine,dist,bank,first,second,shot):
    page=browser.new_page(viewport={'width':1180,'height':820},has_touch=True)
    page.goto((dist/'Fallakte.html').as_uri())
    page.locator('#zweiter-tag').tap()
    frame=page.frame_locator('iframe[title="Dienstag, 08.12.2026"]')
    article=frame.locator('article')
    actions=Counter(button=1)
    choices=0
    screens=['Tagesauswahl','Nachrichten']
    texts={}
    low,high=(first,second or first)
    def sample():
        if not article.count():return
        name=frame.locator('.eyebrow').inner_text()
        if screens[-1]!=name:screens.append(name)
        seen=Counter(frame.locator('main').evaluate(VISIBLE))
        texts[name]=texts.get(name,Counter()) | seen
    def click(loc,choice=False):
        nonlocal choices
        choices+=int(choice)
        expect(loc).to_be_visible()
        loc.tap()
        actions['button']+=1
        sample()
    def btn(label):
        return frame.get_by_role('button',name=label,exact=True)
    def select(loc,val,choice=False):
        nonlocal choices
        choices+=int(choice)
        loc.select_option(val);actions['auswahl']+=1;sample()
    if first!=bank['levels'][0]: click(btn(first))
    if second:
        click(frame.get_by_text('Zu zweit auf zwei Niveaus',exact=True))
        select(frame.get_by_label('Zweites Niveau',exact=True),second)
    click(btn(bank['cases']['Mutter']['sections'][0]))
    for person in ['Mutter','Freundin']:
        case=bank['cases'][person]
        steps=case['levels'][high]
        for field in case['levels'][low][0]['fields']:
            select(article.get_by_role('combobox',name=field['name'],exact=True),str(field['line']),choice=True)
        click(btn('Weiter'))
        for i in [1,2]:
            q=steps[i]
            for n,part in enumerate([q]+([q['depth']] if 'depth' in q else [])):
                target=next(k for k,o in enumerate(part['options']) if o['correct'])
                click(article.locator('.options').nth(n).get_by_role('button').nth(target),choice=True)
            if i==2 and person=='Freundin' and second and first=='Förder':
                shot(page,engine+'-Partner-Regeln')
            click(btn('Weiter'))
        q=steps[3]
        key,ids=q['card']
        expect(article.locator(':scope > p').first).to_have_text('Wähle eine Information. Wähle, was Laura möchte. Erkläre deinen Grund.')
        expect(article.locator('section.intro')).not_to_be_visible()
        if person=='Freundin' and second and first=='Förder':shot(page,engine+'-Partner-Grundauftrag')
        click(btn(bank['cards'][key]['lines'][ids[0]-1]),choice=True)
        click(btn(bank['laura'][q['goals'][0]-1]),choice=True)
        click(btn(q['options'][1]),choice=True)
        if 'extension' in q:
            extension=article.locator('section.intro')
            expect(extension.get_by_role('heading',name=high+' · Weiterdenken')).to_be_visible()
            expect(extension.get_by_text(q['extension']['prompt'],exact=True)).to_be_visible()
        expect(article.get_by_text(bank['verdictUI']['explain'],exact=True)).to_be_visible()
        click(btn(bank['verdictUI']['spoken']))
        if person=='Freundin' and second and first=='ESA':shot(page,engine+'-Partner-Begründung')
        click(btn(bank['verdictUI']['done']))
        expect(frame.get_by_role('heading',name=person+' · Abschnitt fertig')).to_be_visible()
        screens.append(person+' fertig')
        if person=='Mutter':click(btn('Weiter zur Freundin'))
    page.close()
    assert len(screens)==12 and len(texts)==8
    counts={screen:sum(len(re.findall(r"[^\W_]+(?:[’'-][^\W_]+)*",t))*n for t,n in fragments.items())
            for screen,fragments in texts.items()}
    return dict(browser=engine,niveaus=[first,second] if second else [first],aufgaben=len(texts),wechsel=len(screens)-1,
                ansichten=screens,fachliche_auswahlen=choices,bedienhandlungen=dict(actions),woerter_je_aufgabe=counts,wortvorkommen=sum(counts.values()))
