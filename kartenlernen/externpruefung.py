"""Unverändertes externes Prüfurteil und Sichtprüfung der zugehörigen Hilfen am Offline-Build."""
import csv
from collections import Counter
import os
from playwright.sync_api import sync_playwright
from erstellen import HERE,OUT,sha
from wiedereinstieg import GEOMETRIE

DATEI=HERE/'pruefdaten/Unabhaengiger_Freitexttest_30c32c4.csv'
# In diesen sechs Zeilen war die Kategorie der damaligen Software leer.
# Für die Prüfung der Erklärung wird das fachlich bezeichnete Thema separat festgehalten.
FEHLERTHEMA={15:'sti',17:'einnahme',36:'sti',52:'sperma',54:'kontakt',55:'kondomschutz'}
def original():
    assert sha(DATEI.read_bytes())=='ea8de261e589d2a8d7d836b56a680d6dbc71965b26d808ac93c6bbb98352a617'
    with DATEI.open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f,delimiter=';'))
    assert len(rows)==73
    return [dict(satz='extern',nummer=i,modell=row['Aufgabe'],text=row['Testantwort'],
                 soll=row['Fachliches Soll (Prüfurteil)'],damals=row['Diagnose 30c32c4'],
                 merkmal=row['Erkannte Fehlerkategorie'] or FEHLERTHEMA.get(i,'')) for i,row in enumerate(rows,1)]

def auswertung(rows):
    assert sorted(r['nummer'] for r in rows)==list(range(1,74))
    return {soll:dict(anzahl=len(gruppe),vorher=sum(r['damals']==soll for r in gruppe),
                      jetzt=sum(r['ist']==soll for r in gruppe),ausgaben=dict(Counter(r['ist'] for r in gruppe)))
            for soll in sorted({r['soll'] for r in rows}) if (gruppe:=[r for r in rows if r['soll']==soll])}

# Pro Text eine frische Sitzung. Die geänderte Ansicht über ihre sichtbaren Tasten öffnen.
WEG="""({row,tier})=>{
 const $=s=>document.querySelector(s);
 const tap=(a,v)=>$('[data-action="'+a+'"]'+(v===undefined?'':'[data-value="'+v+'"]')).click();
 const mat=JSON.parse($('#material').textContent),qs=mat.levels[tier].fragen;
 const eingabe=t=>{const el=$('#entry');el.value=t;el.dispatchEvent(new Event('input',{bubbles:true}));};
 tap('level',tier);tap('questions');
 for(const q of qs){
   if(q.modell===row.modell)break;
   if(q.typ==='wahl')tap('pick',q.optionen.indexOf(q.passend));
   else{eingabe(mat.modelle[q.modell].beispiel);tap('check');}
   tap('advance');
 }
 eingabe(row.text);tap('check');
 const lesen=()=>$('#page').innerText,antwort=lesen();
 const d=Lernfeedback.analyze(row.modell,row.text),m=mat.modelle[row.modell];
 const korrektur=d.error?(d.quelle?Lernfeedback.gesundheit[d.error].info:m.fehler[d.error]):'';
 const frage=d.error?(d.quelle?Lernfeedback.gesundheit[d.error].frage:m.fragen[d.error]):'';
 function pruefe(test,meldung){if(!test)throw Error(row.nummer+' · '+meldung);}
 if(row.soll!=='passend')pruefe(!$('[data-action=advance]'),'unberechtigte Bestätigung');
 if(row.merkmal)pruefe(d.error===row.merkmal && antwort.includes(frage),'falscher Denkimpuls');
 if(d.state==='unsicher')pruefe(antwort.includes('Vergleiche deine Erklärung mit dem Beispiel.') && !antwort.includes('kann richtig sein') && $('[data-action=compare]').classList.contains('primary'),'kein neutraler Selbstvergleich');
 tap('help');const hilfen=[lesen()];
 for(let i=2;i<=5;i++){tap('more');hilfen.push(lesen());}
 pruefe(hilfen[4].includes(m.beispiel),'Beispiel fehlt');
 if(korrektur)pruefe(hilfen[1].includes(frage) && hilfen[3].includes(korrektur) && hilfen[4].includes(korrektur),'Fehlerbezug in Hilfe 2/4/5');
 if(d.state==='vertauscht')pruefe(hilfen[4].includes('Reihenfolge'),'Ursache in Hilfe 5');
 const h5geometrie=GEOMETRIE();
 tap('back');
 if(!$('[data-action=compare]'))return {antwort,hilfen,vergleich:null,h5geometrie};
 tap('compare');
 const vergleiche=$('#page p:last-of-type').textContent;
 pruefe(vergleiche.includes(m.beispiel) && (!korrektur || vergleiche.includes(korrektur)),'Korrektur im Vergleich');
 if(d.state==='vertauscht')pruefe(vergleiche.includes('Reihenfolge'),'Ursache im Vergleich');
 if(d.state==='unsicher')pruefe($('.selbstcheck')?.textContent===m.vergleich,'Leitfragen fehlen');
 const teile=[$('#draft').textContent];
 while($('[data-action=later]')){tap('later');teile.push($('#draft').textContent);}
 pruefe(teile.join('')===row.text,'Antwort verändert');
 const geometrie=GEOMETRIE();
 tap('compared');
 pruefe(['question','end'].includes($('#page').dataset.screen),'Abschlussweg');
 return {antwort,hilfen,vergleich:vergleiche,selbstvergleich:true,geometrie,h5geometrie};
}""".replace('GEOMETRIE()', '('+GEOMETRIE+')()')

def browserwege():
    rows=original();wege=[]
    with sync_playwright() as pw:
        for engine in ('chromium','webkit'):
            with getattr(pw,engine).launch(executable_path=os.getenv(engine.upper()+'_EXECUTABLE')) as b:
                page=b.new_page(viewport={'width':390,'height':560},has_touch=True)
                for row in rows:
                    page.goto((OUT/'Vorbereitung.html').as_uri())
                    page.evaluate("async()=>{document.documentElement.style.fontSize='125%';await document.fonts.ready}")
                    tier='MSA' if row['modell'] in ('pille','schleim') else 'AHR'
                    ist=page.evaluate(WEG,dict(row=row,tier=tier))
                    assert not ist['h5geometrie'] and not ist.get('geometrie'),(engine,row,ist)
                    wege.append(dict(browser=engine,nummer=row['nummer'],**ist))
    return wege
