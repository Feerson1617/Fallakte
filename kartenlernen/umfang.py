"""Vergleiche die sichtbaren Arbeitswege ab der Niveauwahl bis zum Abschluss."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
from erstellen import ROOT,OUT,HERE

RECORDER=r"""selector=>{
  window.spur={woerter:new Set(),ansichten:[],handlungen:[]};
  function read(){
    const text=document.querySelector(selector).innerText.trim();
    if(text!==spur.ansichten.at(-1))spur.ansichten.push(text);
    for(const line of text.split(/\n+/)){
      const l=line.trim();if(l)spur.woerter.add(l);
    }
  }
  read();
  for(const type of ['click','input'])window.addEventListener(type,e=>{
    const b=e.target.closest('button,input');if(!b)return;
    spur.handlungen.push(b.dataset.do||b.dataset.action||'Buchstabe eingeben');read();
  });
}"""
COUNTS=r"""()=>({bedienhandlungen:spur.handlungen.length,bildschirmwechsel:spur.ansichten.length-1,
  lesewoerter:[...spur.woerter].join(' ').match(/[\p{L}\p{N}]+(?:[-–][\p{L}\p{N}]+)*/gu).length,
  handlungen:spur.handlungen})"""
def measure(ref):
    import subprocess
    from erstellen import START
    oldtest=subprocess.check_output(['git','show',START+':kartenlernen/sichttest.js'],cwd=ROOT,text=True)
    records=[]
    with sync_playwright() as pw,pw.chromium.launch() as browser:
        for tier in ['Foerder','ESA','MSA','AHR']:
            result={'niveau':tier}
            for title,path,script in [('alt',ref/'Vorbereitung.html',oldtest),('neu',OUT/'Vorbereitung.html',(HERE/'sichttest.js').read_text())]:
                p=browser.new_page(viewport={'width':1024,'height':768})
                p.goto(path.as_uri());p.evaluate('document.fonts.ready');p.evaluate(RECORDER,'#page')
                row=p.evaluate(script,dict(tier=tier,assist=False,models=False))
                assert not row['errors']
                result[title]=dict(klicks=row['taps'],papierphasen=row['papers'],woerter=p.evaluate(COUNTS)['lesewoerter'],
                                   pflichtfragen=9 if title=='alt' else 4,freitext=2 if title=='neu' and tier in ('MSA','AHR') else 0)
                p.close()
            records.append(result)
    return records
