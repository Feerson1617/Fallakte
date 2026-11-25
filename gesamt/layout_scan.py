"""Stichprobe an den neuen Arbeitsaufträgen mit vergrößerter Schrift in beiden iPad-Lagen."""
import os,json
from playwright.sync_api import sync_playwright
from auslieferung import OUT,QA,json_text
from pruefen import enter,button
SAMPLE="""() => {
  const issues=[];
  const rgb=s=>s.match(/[.\\d]+/g)?.map(Number);
  const lum=c=>c.slice(0,3).map(x=>x/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4).reduce((n,x,i)=>n+x*[.2126,.7152,.0722][i],0);
  for(const el of document.querySelectorAll('button,p,label,summary,h1,h2,h3')){
    if(!el.checkVisibility() || !el.innerText.trim())continue;
    const box=el.getBoundingClientRect(),s=getComputedStyle(el);
    if(!box.width||!box.height)continue;
    if(el.tagName==='BUTTON'&&!el.disabled&&(box.height<43.8||box.width<43.8))issues.push(['Touchfläche',el.innerText,Math.round(box.width),Math.round(box.height)]);
    if(el.scrollWidth>el.clientWidth+1 && ['hidden','clip'].includes(s.overflowX))issues.push(['Text abgeschnitten',el.innerText]);
    if(el.disabled)continue;
    let bg=null;
    for(let p=el;p;p=p.parentElement){const st=getComputedStyle(p);if(st.backgroundImage!=='none')break;const c=rgb(st.backgroundColor);if(c?.length===3||c?.[3]===1){bg=c;break;}}
    const fg=rgb(s.color);
    if(bg&&fg){const [a,b]=[lum(fg),lum(bg)].sort((a,b)=>b-a);const ratio=(a+.05)/(b+.05);
      const large=parseFloat(s.fontSize)>=(parseInt(s.fontWeight)>=700?18.67:24);
      if(ratio+.01<(large?3:4.5))issues.push(['Kontrast',el.innerText,ratio.toFixed(2)]);}
  }
  if(document.documentElement.scrollWidth>innerWidth+1)issues.push(['Dokument zu breit',innerWidth,document.documentElement.scrollWidth]);
  return issues;
}"""
def run():
    rows=[]
    with sync_playwright() as pw:
        for engine in ('chromium','webkit'):
            with getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as b:
                for w,h in [(820,1180),(1180,820),(390,560)]:
                    p=b.new_page(viewport={'width':w,'height':h},has_touch=True);p.goto((OUT/'Fallakte-Gesamt.html').as_uri())
                    for module in ('START','vor','02','08'):
                        f=p if module=='START' else enter(p,module)
                        f.locator('html').evaluate("e=>e.style.fontSize='150%'")
                        def check(step):
                            rows.append(dict(browser=engine,fenster=[w,h],schrift='150%',modul=module,zustand=step,befunde=f.evaluate(SAMPLE)))
                        check('Übersicht')
                        if module=='vor':
                            button(f,'level','Foerder');button(f,'picker');button(f,'open','1A');button(f,'begin');button(f,'hint');check('Fachfrage mit Hilfe')
                        if module=='02':
                            f.locator('#level-MSA').click();f.locator('#neu').click();f.locator('[data-strategy=K]').click();check('L01 Papier und Code')
                        if module=='08':
                            f.locator('#level-0').select_option('Förder');f.locator('#level-1').select_option('AHR');f.locator('#jump').click();f.locator('#next').click();check('LA-02 im gemischten Tandem')
                        if module!='START':p.locator('#zurueck').click()
                    p.close()
    (QA/'Layoutstichprobe.json').write_text(json_text(rows))
if __name__=='__main__':run()
