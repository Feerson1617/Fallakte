"""Measure the pupil-facing offline HTML. --vorpruefung requires exactly two playable stages."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess

from playwright.sync_api import expect, sync_playwright

from runde1_orakel import correct_reason

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'dist/Runde-1/Fallakte.html'
LEVELS = ('Foerder', 'ESA', 'MSA', 'AHR')
VIEWS = {'hoch': (820, 1180), 'quer': (1180, 820), 'schmal': (390, 844)}
TASKS = {'L01': ('K','B'), 'L02': ('K+Cu','C'), 'L03': ('K+P','A'),
         'L04': ('K+H','B'), 'L05': ('K','C')}
ENGINES = ('chromium','webkit')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def context(browser, view):
    width, height = VIEWS[view]
    return browser.new_context(viewport={'width':width, 'height':height},has_touch=True,
                               device_scale_factor=1,locale='de-DE',reduced_motion='reduce')


def capture(page, directory, files, name):
    file = directory / ('bedienung-'+name+'.jpg')
    page.screenshot(path=file, type='jpeg', quality=59, animations='disabled')
    files[file.name] = digest(file)


# Word rectangles distinguish actually visible text from text rendered below the fold
# or clipped by a scroll container. Voluntary tools, older chat entries, navigation,
# and the folded paper substitute are outside the pupil's mandatory task.
MEASURE = r"""
() => {
  const work=document.querySelector('#beratung-arbeit'), chat=document.querySelector('#beratung-verlauf');
  const phase=work.dataset.step, stage=document.querySelector('#beratung-stage').dataset.stage;
  const current=chat.querySelector('[data-stage="'+stage+'"][data-kind="'+(phase==='antwort'?'reaction':'opening')+'"] > p');
  const skip='.beratung-tools,#kartenverweise,#papier-ersatz,#strategie-bearbeiten,#grund-bearbeiten,'+
             '#fruehere-nachrichten,.weiterlesen';
  const inView=(node,rect)=>{
    const x=rect.left+rect.width/2, y=rect.top+rect.height/2;
    if(x<0 || x>=innerWidth || y<0 || y>=innerHeight)return false;
    for(let n=node.parentElement;n && n!==document.body;n=n.parentElement){
      const style=getComputedStyle(n),box=n.getBoundingClientRect();
      if(/hidden|clip|auto|scroll/.test(style.overflowY) && (y<box.top || y>=box.bottom))return false;
      if(/hidden|clip|auto|scroll/.test(style.overflowX) && (x<box.left || x>=box.right))return false;
    }
    return true;
  };
  let present=0, onscreen=0;
  for(const root of [current,work].filter(Boolean)){
    const tree=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
    for(let node;node=tree.nextNode();){
      if(node.parentElement.closest(skip))continue;
      const closed=node.parentElement.closest('details:not([open])');
      if(closed && !closed.querySelector('summary').contains(node))continue;
      for(const m of node.textContent.matchAll(/[\p{L}\p{N}]+(?:[-’'][\p{L}\p{N}]+)*/gu)){
        const range=document.createRange();
        range.setStart(node,m.index);range.setEnd(node,m.index+m[0].length);
        const rects=[...range.getClientRects()].filter(r=>r.width>0 && r.height>0);
        if(!rects.length)continue;
        present++;
        if(rects.some(r=>inView(node,r)))onscreen++;
      }
    }
  }
  const labels=[...work.querySelectorAll('button,input')].filter(e=>e.getBoundingClientRect().height);
  const overflowing=labels.filter(e=>e.scrollWidth>e.clientWidth+2).map(e=>e.id);
  const visible=labels.filter(e=>inView(e,e.getBoundingClientRect())).map(e=>e.id);
  return {schritt:phase,pflichtwoerter_im_blick:onscreen,pflichtwoerter_aufgeklappt:present,
    bedienung_im_blick:visible,scroll_y:Math.round(scrollY),umbruchfehler:overflowing,
    dokumentbreite:document.documentElement.scrollWidth,fensterbreite:innerWidth};
}
"""


def sample(page, stage, phase, check_action=True):
    work=page.locator('#beratung-arbeit')
    expect(work).to_have_attribute('data-step',phase)
    expect(page.locator('#beratung-stage')).to_have_attribute('data-stage',stage)
    state=page.evaluate(MEASURE)
    assert state['dokumentbreite']<=state['fensterbreite']+1 and not state['umbruchfehler'],(stage,state)
    assert state['pflichtwoerter_im_blick']>0, (stage,state)
    primary={'wahl':('strategie-',),'grund':('grund-','pruefcode'), 'senden':('nachricht-senden',),
             'antwort':('beratung-weiter','beratung-fertig')}
    state['naechste_handlung_im_blick']=any(i.startswith(primary[phase]) for i in state['bedienung_im_blick'])
    if check_action:
        assert state['naechste_handlung_im_blick'],(stage,phase,state)
    return state


def select(page,strategy):
    choice=page.locator('[data-strategy="'+strategy+'"]')
    if not choice.is_visible(): page.locator('#weitere-strategien summary').tap()
    choice.tap()
    expect(page.locator('#aktueller-rat')).to_have_attribute('data-about-strategy',strategy)
    expect(page.locator('button[data-strategy]:visible')).to_have_count(0)


def reason(page,tier,stage,strategy,correct):
    options=page.locator('#begruendungen [data-option]')
    labels=options.all_inner_texts()
    answer=correct_reason(tier,stage,strategy,labels)
    options.nth(answer if correct else (answer+1)%len(labels)).tap()


def open_start(page,tier):
    page.goto(HTML.as_uri())
    expect(page.locator('#start [aria-pressed=true]')).to_have_count(0)
    page.locator('#level-'+tier).tap()
    page.locator('#neu').tap()


def measure_route(browser,engine,tier,view,stages,directory,files):
    with context(browser,view) as ctx:
        page=ctx.new_page()
        page.set_default_timeout(5500)
        errors=[]
        page.on('pageerror',lambda exc: errors.append(str(exc)))
        open_start(page,tier)
        actions=['Niveau wählen','Neu beginnen']
        entries=[]
        media=0
        codes=0
        paper=tier in ('MSA','AHR')
        for idx,stage in enumerate(stages):
            strategy,code=TASKS[stage]
            observations=[sample(page,stage,'wahl')]
            expect(page.locator('[data-strategy][aria-pressed=true]')).to_have_count(0)
            expect(page.locator('#pruefcode:visible,#begruendungen:visible')).to_have_count(0)
            chosen=page.locator('[data-strategy="'+strategy+'"]')
            if not chosen.is_visible():
                page.locator('#weitere-strategien summary').tap()
                actions.append(stage+' weitere Strategien')
            select(page,strategy)
            actions.append(stage+' vollständigen Rat wählen')
            observations.append(sample(page,stage,'grund'))
            if stage==('L01' if len(stages)==2 else {'hoch':'L03','quer':'L04','schmal':'L05'}[view]):
                # Across both engines every level and layout is represented without duplicate pictures.
                view_index=list(VIEWS).index(view)
                selected_engine=ENGINES[(view_index+LEVELS.index(tier))%2]
                if engine==selected_engine:
                    capture(page,directory,files,'-'.join([engine,tier,view,'grund']))
            if paper:
                expect(page.locator('#pruefcode')).to_be_visible()
                label=page.locator('.fachcheck').inner_text()
                assert 'Laufzettel' in label and 'Laura '+str(idx+1) in label,label
                page.locator('#pruefcode').tap()
                actions.append(stage+' Codefeld antippen')
                page.locator('#pruefcode').fill(code)
                page.locator('#fachcheck-pruefen').tap()
                actions.append(stage+' Code prüfen')
                codes+=1
                media+=1
            else:
                expect(page.locator('#pruefcode')).to_have_count(0)
                reason(page,tier,stage,strategy,True)
                actions.append(stage+' biologischen Grund wählen')
                if stage=='L05': media+=1
            observations.append(sample(page,stage,'senden'))
            send=page.locator('#nachricht-senden')
            expect(send).to_be_enabled()
            send.tap()
            actions.append(stage+' Nachricht senden')
            observations.append(sample(page,stage,'antwort'))
            expect(page.locator(f'.chat-entry[data-stage="{stage}"][data-kind=send]')).to_have_count(1)
            expect(page.locator(f'.chat-entry[data-stage="{stage}"][data-kind=reaction]')).to_have_count(1)
            history=page.locator('#fruehere-nachrichten')
            if history.is_visible() and idx==len(stages)-1:
                history.tap()
                expect(history).to_have_attribute('aria-expanded','true')
                expect(page.locator('.chat-entry[data-stage=L01][data-kind=opening]')).to_be_visible()
                history.tap()
            entries.append({'abschnitt':stage,'strategie':strategy,'zustaende':observations})
            if idx+1<len(stages):
                page.locator('#beratung-weiter').tap()
                actions.append(stage+' zum nächsten Abschnitt')
        expect(page.locator('#beratung-fertig')).to_be_visible()
        assert not errors,errors
        return {'browser':engine,'ansicht':view,'viewport':VIEWS[view],'niveau':tier,'entscheidungen':len(stages),
                'codeeingaben':codes,'papierphasen':media,'medienwechsel':2*media,
                'tipps':len(actions),'handlungen':actions,'abschnitte':entries,'skriptfehler':errors}


def follow_help(page,tier,stage,chosen):
    draft=page.locator('#aktueller-rat')
    history=page.locator('#beratung-verlauf').text_content()
    page.locator('#hilfe').tap()
    modal=page.locator('#material-dialog[open]')
    for i in range(1,6):
        hint=modal.locator('#hilfe-text')
        expect(hint).to_have_attribute('data-depth',str(i))
        assert hint.inner_text().strip() and modal.locator('#hilfe-text:visible').count()==1
        if i<5: modal.locator('#hilfe-weiter').tap()
    modal.locator('#material-zurueck').tap()
    expect(draft).to_have_attribute('data-about-strategy',chosen)
    assert page.locator('#beratung-verlauf').text_content()==history


def challenge(browser,engine,tier,directory,files):
    """Interrupt a real draft and change the advice after a successful biological check."""
    with context(browser,'hoch') as ctx:
        page=ctx.new_page()
        page.set_default_timeout(5500)
        open_start(page,tier)
        select(page,'Cu')
        page.locator('#passende-karte').tap()
        modal=page.locator('#material-dialog[open]')
        target=modal.locator('[data-section-id]:visible')
        expect(modal).to_have_attribute('data-method','Cu')
        expect(target).to_have_count(1)
        expect(target.locator('h3')).to_have_text('Kupfer bremst Spermien')
        expect(modal.locator('#material-ganze-karte')).to_be_visible()
        short=target.inner_text()
        if tier=='Foerder':
            capture(page,directory,files,engine+'-Foerder-quelle')
        modal.locator('#material-ganze-karte').tap()
        n=modal.locator('[data-section-id]:visible').count()
        assert n>=5,(tier,n)
        modal.locator('#material-zurueck').tap()
        expect(modal.locator('[data-section-id]:visible')).to_have_count(1)
        modal.locator('#material-zurueck').tap()
        expect(page.locator('#aktueller-rat')).to_have_attribute('data-about-strategy','Cu')
        paper=tier in ('MSA','AHR')
        if paper:
            page.locator('#pruefcode').fill('A')
            page.locator('#fachcheck-pruefen').tap()
        else: reason(page,tier,'L01','Cu',False)
        expect(page.locator('#fachmeldung')).to_have_attribute('data-type','A')
        assert page.locator('#fachmeldung').inner_text().strip()
        follow_help(page,tier,'L01','Cu')
        if paper:
            page.locator('#pruefcode').fill('B')
            page.locator('#fachcheck-pruefen').tap()
        else: reason(page,tier,'L01','Cu',True)
        expect(page.locator('#nachricht-senden')).to_be_enabled()
        page.locator('#strategie-bearbeiten').tap()
        select(page,'H')
        disabled=page.locator('#nachricht-senden')
        assert not disabled.is_visible() or disabled.is_disabled()
        expect(page.locator('.chat-entry[data-kind=send]')).to_have_count(0)
        return {'browser':engine,'niveau':tier,'gezielte_kartenstelle':short,
                'ganze_karte_abschnitte':n,'hilfe_stufen':5,'fachfehler_korrigierbar':True,
                'alte_freigabe_nach_neuwahl_entwertet':True}


def enlarged(browser,engine,tier,directory,files):
    with context(browser,'schmal') as ctx:
        page=ctx.new_page()
        open_start(page,tier)
        page.add_style_tag(content='html{font-size:150% !important}')
        initial=sample(page,'L01','wahl',check_action=False)
        select(page,'K')
        proof={'browser':engine,'niveau':tier,'schrift_prozent':150,
               'normal':initial,'fachcheck':sample(page,'L01','grund',check_action=False)}
        if tier in ('MSA','AHR'):
            # Reducing the visual work area reproduces space competition, not a physical iPad keyboard.
            page.set_viewport_size({'width':390,'height':460})
            code=page.locator('#pruefcode')
            code.tap()
            for button in [code,page.locator('#fachcheck-pruefen')]:
                button.scroll_into_view_if_needed()
                assert button.evaluate("""e=>{const b=e.getBoundingClientRect(),x=b.left+b.width/2,y=b.top+b.height/2;
                    return e.contains(document.elementFromPoint(x,y))}""")
            code.fill('B')
            page.locator('#fachcheck-pruefen').tap()
            expect(page.locator('#nachricht-senden')).to_be_enabled()
            proof['tastatur_flaeche']=[390,460]
            proof['senden']=sample(page,'L01','senden',check_action=False)
        if tier=='AHR': capture(page,directory,files,engine+'-AHR-gross-kleinfenster')
        return proof


def run_engine(engine, stages, dest):
    files={}
    routes=[]
    checks=[]
    sizes=[]
    with sync_playwright() as pw:
        browser=getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE'))
        for tier in LEVELS:
            for view in VIEWS:routes.append(measure_route(browser,engine,tier,view,stages,dest,files))
            checks.append(challenge(browser,engine,tier,dest,files))
            sizes.append(enlarged(browser,engine,tier,dest,files))
            print(engine,tier,'geprüft',flush=True)
        browser.close()
    return routes,checks,sizes,files


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vorpruefung',action='store_true')
    early=parser.parse_args().vorpruefung
    dest=ROOT/('docs/pruefnachweise/2a-vorpruefung' if early else 'build/runde1/qa')
    dest.mkdir(parents=True,exist_ok=True)
    bank=json.loads(HTML.with_name('Materialvertrag.json').read_text())
    stages=[sid for sid,s in bank['stages'].items() if s['playable']]
    assert stages==list(TASKS)[:2 if early else 5],stages
    before=digest(HTML)
    routes,checks,sizes,files=[],[],[],{}
    with ThreadPoolExecutor(max_workers=len(ENGINES)) as pool:
        futures=[pool.submit(run_engine,e,stages,dest) for e in ENGINES]
        for f in futures:
            r,c,s,b=f.result()
            routes.extend(r);checks.extend(c);sizes.extend(s);files.update(b)
    levels={}
    for tier in LEVELS:
        rows=[r for r in routes if r['niveau']==tier]
        keys=['entscheidungen','tipps','codeeingaben','papierphasen','medienwechsel']
        metrics={k:rows[0][k] for k in keys}
        assert all(all(r[k]==metrics[k] for k in keys) for r in rows)
        samples=[s for r in rows for entry in r['abschnitte'] for s in entry['zustaende']]
        metrics['pflichtwoerter_im_blick_max']=max(s['pflichtwoerter_im_blick'] for s in samples)
        metrics['pflichtwoerter_aufgeklappt_max']=max(s['pflichtwoerter_aufgeklappt'] for s in samples)
        levels[tier]=metrics
    assert before==digest(HTML), 'Prüfung nach zwischenzeitlichem Neubau wiederholen.'
    result={'commit':bank['buildCommit'],'html_sha256':before,'bankversion':bank['version'],
            'geprueft_utc':datetime.now(timezone.utc).isoformat(),'erprobte_abschnitte':stages,
            'vorpruefung_arbeitskopie':early,'niveaus':levels,'bilder':files,'durchlaeufe':routes,
            'bedienproben':{'hilfen_und_korrektur':checks,'gross_schmal_tastatur':sizes},
            'messweise':'Regulärer Beispielweg ohne freiwillige Hilfen. Tipps zählen Niveauwahl und Start, Wahl, Fachcheck und Senden sowie Übergänge bis zur letzten Antwort. Ein Antippen des Codefelds zählt als Tipp, die Texteingabe separat. Papierphasen folgen den Pflichtaufträgen; pro Phase zählen Hin- und Rückweg. Ab Laura 5 zählt das gemeinsame Schlussratfeld einmal, mit dem Codeauftrag auf demselben Bogen. Analoger Unterrichtseinstieg und anschließende Projektion liegen außerhalb der Messung. Textmessung zählt Wörter der aktuellen Laura-Nachricht und des sichtbaren Arbeitsbereichs einschließlich Auswahl- und Schaltflächenbeschriftungen. Optionale Hilfe, Kartenlinks, Ersatzaufgabe, Verlauf und Navigation sind ausgenommen. Wortmittelpunkte innerhalb des Viewports und seiner Scrollcontainer zählen als im Blick. Größere Schrift ist eine 150%-Emulation; die kleinere Arbeitshöhe ersetzt nur den Platzbedarf einer Tastatur. Keine Messung von Schülerarbeitszeit, Lesen oder Schreibqualität.'}
    if early: result['referenz_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    (dest/'bedienung.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(dest/'bedienung.json',flush=True)


if __name__=='__main__':main()
