"""Antworten und ursprüngliche Sollwerte aus der externen Prüfung vom 28.11."""
import json
import os
import sys
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from pathlib import Path
from playwright.sync_api import sync_playwright
from pruefen import OUT, HERE, QA, sha

DIAGNOSE = """([day, rows])=>{
 const result=[];
 const click=id=>{const b=document.getElementById(id);if(!b||b.disabled)throw Error(id);b.click()};
 const first=day==='02';
 for(const row of rows){
   if(first){Beratung.begin(row.tier,row.stage);click('strategie-'+row.key)}
   else{const [person,id]=row.key.split('/');level=row.tier;resetPath();
     go('case',{person,at:bank.cases[person].tasks.findIndex(t=>t.id===id)+1})}
   const t=document.querySelector(first?'#erklaerung':'#app textarea');
   t.value=row.text;t.dispatchEvent(new Event('input',{bubbles:true}));click(first?'vergleichen':'compare');
   const msg=document.querySelector('[data-diagnose]');
   const actual=msg.dataset.diagnose,feedback=msg.textContent;
   click(first?'hilfe':'help');const hints=[],references=[];
   for(let k=0;k<5;k++){
     hints.push(document.querySelector(first?'#hilfe-text':'#dialog-body p').textContent);
     references.push(document.querySelector('dialog[open] .hilfsquelle')?.textContent||'');
     if(k<4)click(first?'hilfe-weiter':'hint-next');
   }
   click(first?'material-zurueck':'dismiss');
   result.push({...row,actual,feedback,hints,references});
 }
 return result;
}"""
def run(engine):
    corpus=json.loads((HERE/'Gegenbestand-f5ebc56.json').read_text())
    dest=QA/'Freigabestufen'
    dest.mkdir(parents=True,exist_ok=True)
    results={}
    with TemporaryDirectory() as temp, sync_playwright() as pw,getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as browser:
        for day in ('02','08'):
            html=OUT/f'Fallakte-{day}-12.html'
            with ZipFile(html.with_name(html.stem+'-SCORM12.zip')) as package:
                entry=package.read('index.html')
            assert entry==html.read_bytes()
            sco=Path(temp)/'index.html'
            sco.write_bytes(entry)
            page=browser.new_page(viewport={'width':1024,'height':768})
            page.goto(sco.as_uri())
            page.locator(f'[data-entry="modul-{day}"]').click()
            frame=page.locator('#arbeitsplatz iframe').element_handle().content_frame()
            frame.locator('#level-MSA' if day=='02' else '#level-0').wait_for()
            rows=frame.evaluate(DIAGNOSE,[day,corpus[day]['antworten']])
            for row in rows:
                expected=row.get('expected','teil')
                if row['text']=='Es fehlt ihre Wertvorstellung.':
                    assert row['actual']=='teil' and 'ausdrücklich' in row['feedback'],row
                else:
                    assert row['actual']==expected,row
                assert all(row['hints']) and len(set(row['hints']))>=4,row
                if day=='02':
                    assert 'Fachlich richtig:' in row['feedback'] and any(row['references']),row
                if row['key'].endswith('/Leerstelle'):
                    person=row['key'].split('/')[0]
                    quote={'Mutter':'ich würde dir raten, das Kind zu bekommen',
                           'Freundin':'ich würde dir zu einem Abbruch mit Medikamenten raten',
                           'Großmutter':'man sollte ungeborenes menschliches Leben schützen',
                           'Vater':'in der Arztpraxis nach deinen Möglichkeiten zu fragen'}[person]
                    assert all(quote in hint+source for hint,source in zip(row['hints'],row['references'])),row
                if row['text']=='Es kommt zu Blutungen.':
                    assert 'Blutungen hast du erkannt' in row['feedback'] and 'Bauch' in row['hints'][0],row
            function='Entwurf.fehler' if day=='02' else 'medizin'
            medical=frame.evaluate(f'rows=>rows.map(r=>({{...r,issue:{function}(r.text)}}))',corpus[day]['medizin'])
            assert all(bool(r['issue'])==(r['expected']=='falsch') for r in medical),medical
            results[day]={'html_sha256':sha(entry),'texte':rows,'medizin':medical}
            if day=='02':
                page.reload();page.locator('[data-entry="modul-02"]').click()
                frame=page.locator('#arbeitsplatz iframe').element_handle().content_frame()
                frame.locator('#level-MSA').wait_for()
                carry=frame.evaluate('''()=>{
                  const c=id=>document.getElementById(id).click();
                  const reason='Mein eigener Schlussgedanke zur Grenze des Kondoms.';
                  c('level-MSA');c('neu');c('spur-lesen');
                  const pick=document.querySelector('#spur-wahl');pick.selectedIndex=1;pick.dispatchEvent(new Event('change'));
                  const fill=(id,text)=>{const f=document.getElementById(id);f.value=text;f.dispatchEvent(new Event('input'))};
                  fill('spur-grund','Mein erster Gedanke.');c('spur-speichern');c('spur-chat');
                  Beratung.begin('MSA','L01');c('strategie-K');
                  fill('erklaerung','Auch ohne Latex kann ein Kondom Sperma zurückhalten. Die Pille schützt vor HIV.');c('vergleichen');
                  const correction=document.querySelector('#fachmeldung').textContent;
                  if(!correction.includes('Sperma zurück')||!correction.includes('nicht vor HIV')||!document.querySelector('#nachricht-senden').disabled)throw Error(correction);
                  Beratung.begin('MSA','L05');c('strategie-K');fill('erklaerung',reason);c('vergleichen');
                  const way=LAURA.stages.L05.levels.MSA.strategies.K;
                  c('grund-'+way.options.find(o=>o.correct).id);c('nachricht-senden');Runde1.final();
                  const final=document.querySelector('#spur-wahl'),carried=document.querySelector('#spur-grund').value;
                  if(!final||carried!==reason||final.value!==LAURA.strategies.K.label)throw Error('Schlussrat fehlt');
                  final.selectedIndex=2;final.dispatchEvent(new Event('change'));
                  if(document.querySelector('#spur-grund').value!==reason)throw Error('Text bei Methodenwechsel verloren');
                  fill('spur-grund','Mein geänderter eigener Gedanke.');c('spur-speichern');
                  return [...document.querySelectorAll('.spur-zitat')].map(e=>e.textContent);
                }''')
                assert carry==['Mein erster Gedanke.','Mein geänderter eigener Gedanke.'],carry
                results[day]['eigener_Abschluss']=carry
            page.close()
        page=browser.new_page(viewport={'width':1024,'height':768})
        page.goto((OUT/'Fallakte-08-12.html').as_uri());page.locator('[data-entry="modul-08"]').click()
        frame=page.locator('#arbeitsplatz iframe').element_handle().content_frame()
        frame.locator('#level-0').select_option('MSA');frame.locator('#start').click()
        question=frame.locator('.nachrichten-einstieg>.bubble:last-child')
        question.wait_for()
        rect=question.bounding_box();assert rect['y']>=0 and rect['y']+rect['height']<=768,rect
        assert question.evaluate('e=>e.getBoundingClientRect().bottom<=e.parentElement.getBoundingClientRect().bottom')
        assert frame.locator('.nachrichten-liste').evaluate('e=>e.scrollHeight<=e.clientHeight+1')
        page.screenshot(path=dest/f'Nachrichten-1024-{engine}.jpg',quality=80)
        results['sichtbare_Frage']=rect
        page.set_viewport_size({'width':740,'height':340})
        frame.wait_for_function("innerWidth===740 && innerHeight<=340")
        frame.evaluate("async()=>{document.documentElement.style.fontSize='150%';await document.fonts.ready;await new Promise(requestAnimationFrame);Arbeitsplatz.refresh();await new Promise(requestAnimationFrame)}")
        reach=frame.evaluate('''()=>{
          const chat=document.querySelector('.nachrichten-einstieg'),inbox=chat.querySelector('.nachrichten-liste');
          const question=chat.lastElementChild, end=inbox.lastElementChild.lastElementChild;
          const bounds=e=>e.getBoundingClientRect();
          chat.scrollTop=0;
          const questionVisible=bounds(question).top>=bounds(chat).top && bounds(question).bottom<=bounds(chat).bottom;
          chat.scrollTop=chat.scrollHeight;
          const endVisible=bounds(end).bottom<=bounds(chat).bottom+1 && bounds(end).bottom>bounds(chat).top;
          return {questionVisible,endVisible,readingHeight:inbox.clientHeight};
        }''')
        assert reach['questionVisible'] and reach['endVisible'] and reach['readingHeight']>0,reach
        results['Leseflaeche_740_340_150']=reach
    (dest/f'Gegenbestand-{engine}.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
    print(engine,len(results['02']['texte']),len(results['08']['texte']), 'Freitexte und fünf Hilfen je Antwort')
if __name__=='__main__':run(sys.argv[1])
