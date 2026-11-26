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
OLD="""tier=>{
 const b=JSON.parse(document.querySelector('#material').textContent),lesson=b.levels[tier];
 const click=(key,value)=>{const el=document.querySelector('[data-do="'+key+'"]'+(value===undefined?'':'[data-value="'+value+'"]'));
 if(!el||el.disabled)throw Error(key);el.click()};
 function solve(q){click('choice',q.options.findIndex(x=>x.correct));click('check');click('advance')}
 click('level',tier);click('new');click('begin');solve(lesson.intro.question);
 for(const c of lesson.chapters){
   click('begin');c.questions.forEach(solve);
   if(c.paperCheck){const input=document.querySelector('#code');input.value=c.paperCheck.options.find(o=>o.correct).code;
   input.dispatchEvent(new Event('input',{bubbles:true}));click('code-check');click('send');}
   if(c.id.endsWith('B'))click('review');
   click('finish');if(c.id==='2B')click('open','3A');
 }
 if(!document.querySelector('h1').textContent.includes('Abschluss'))throw Error('Abschluss fehlt');
 return 1+lesson.chapters.reduce((n,c)=>n+c.questions.length+Number(!!c.paperCheck),0);
}"""
def measure(ref):
    records=[]
    with sync_playwright() as pw,pw.chromium.launch() as browser:
        for tier in ['Foerder','ESA','MSA','AHR']:
            p=browser.new_page(viewport={'width':1024,'height':768})
            p.goto((ref/'Fallakte-Vorbereitung.html').as_uri());p.locator('#vorbereitung').click()
            f=p.frames[-1];f.locator('#view button').first.wait_for();f.evaluate(RECORDER,'#view')
            questions=f.evaluate(OLD,tier);old=f.evaluate(COUNTS);old['fragen']=questions
            p.goto((OUT/'Vorbereitung.html').as_uri());p.evaluate('document.fonts.ready');p.evaluate(RECORDER,'#page')
            result=p.evaluate((HERE/'sichttest.js').read_text(),dict(tier=tier,assist=False,models=False))
            assert not result['errors'];new=p.evaluate(COUNTS);new['fragen']=9
            records.append(dict(niveau=tier,alt=old,neu=new));p.close()
    return records
