"""Verträge und Prüfergebnisse direkt aus den in der HTML-Datei eingebetteten Funktionen."""
import json
from collections import Counter
from playwright.sync_api import sync_playwright
from erstellen import HERE,OUT,pack,sha

def katalog(pfad):
    daten={}
    for zeile in pfad.read_text().splitlines():
        if zeile.startswith('['):
            thema=zeile[1:-1];daten[thema]=[]
        elif zeile:
            soll,text=zeile.split('|',1)
            daten[thema].append(dict(soll=soll,text=text))
    return daten

ANALYSE="""({q,m,card,test})=>{
 const r={choice:test.choice||null,text:test.text||'',tries:1,last:null,repeat:false,attempts:[]};
 r.last=q.typ==='text'?Lernfeedback.analyze(q.modell,r.text):{state:r.choice===q.passend?'passend':'fehlvorstellung',parts:[],error:q.alternativen.find(a=>a.text===r.choice)?.muster};
 r.attempts.push(r.last);
 return {diagnose:r.last,rueckmeldung:rueckmeldung(q,m,r),wiederholt:rueckmeldung(q,m,{...r,tries:2,repeat:true}),
 hilfen:[1,2,3,4,5].map(n=>fachhilfe(q,m,r,card,n))};
}"""
def run():
    sets={n:katalog(HERE/'pruefdaten'/f'{n}.txt') for n in ('entwicklung','reserve')}
    assert sha((HERE/'diagnose.js').read_bytes())=='07093ec1a278a19e62aee8ca18420f50d268f4cb95c9b70089205df415a0b0db'
    vertrag=[];ergebnisse=[];fragen=['# Aufgabenübersicht',''];res=Counter()
    with sync_playwright() as pw,pw.chromium.launch() as browser:
        page=browser.new_page();page.goto((OUT/'Vorbereitung.html').as_uri())
        mat=page.evaluate("JSON.parse(document.querySelector('#material').textContent)")
        for tier,l in mat['levels'].items():
            fragen.extend(['## '+('Förder' if tier=='Foerder' else tier),''])
            for i,(q,card) in enumerate(zip(l['fragen'],l['cards']),1):
                ref=card['texte'][q['abschnitt']]
                m=mat['modelle'].get(q.get('modell'));tests=[]
                if m:
                    model=q['modell']
                    assert len({x['text'] for x in sets['entwicklung'][model]})>=40
                    assert not {x['text'] for x in sets['entwicklung'][model]} & {x['text'] for x in sets['reserve'][model]}
                    for n,bank in sets.items():tests.extend(dict(satz=n,**row) for row in bank[model])
                else:tests=[dict(satz='Auswahl',choice=o,soll='passend' if o==q['passend'] else 'fehlvorstellung') for o in q['optionen']]
                faelle=[]
                for test in tests:
                    result=page.evaluate(ANALYSE,dict(q=q,m=m,card=card,test=test))
                    ist=result['diagnose']['state'];soll=test['soll'];k=test['satz']
                    assert ist==soll or (k=='reserve' and ist=='unsicher'),(model,test,ist)
                    row=dict(niveau=tier,kapitel=i,**test,ist=ist,**result)
                    ergebnisse.append(row);faelle.append(row)
                    res[k,'gesamt']+=1;res[k,'gleich']+=int(ist==soll)
                    res[k,'falschpositiv']+=int(ist=='passend' and soll!='passend')
                fragen.extend([f"{i}. **{card['titel']}** · {q['frage']}  ",f"   {('Kurze eigene Erklärung' if m else 'Eine Antwort auswählen')} · „{ref['titel']}“",''])
                if not m:
                    fragen.extend(['   - '+o for o in q['optionen']]+[''])
                vertrag.append(dict(lerninformationsseiten=l['info'][i-1],papierhilfe=dict(blatt=card['seite'],position=card['position'],stufen=['Blatthälfte und Lückennummern finden',card['felder']]),niveau=tier,kapitel=i,karte=card['ueberschrift'],blatt=[card['seite'],card['position']],
                    quelle=ref,aufgabe=q,antwortmodell=m,beispiele=faelle,
                    abschluss='Eigene Erklärung prüfen, überarbeiten oder nach fachlichem Versuch selbst mit Beispiel vergleichen.' if m else 'Passende Aussage auswählen und begründete Rückmeldung lesen.'))
    readme='''# Scaffoldingvertrag

Die 16 Aufgaben stehen in der Reihenfolge der vier gedruckten Karten. Jede Referenzstelle enthält den unveränderten Wortlaut. Die JSON-Datei verknüpft Aufgabe, Ziel, tatsächliche Antwortmöglichkeiten, Teilaussagen, Denkfehler, Rückmeldungen und fünf Hilfeansichten. Bei den freien Erklärungen sind die Ausgaben für jede getestete Formulierung einzeln enthalten.

1. Karte und exakte Überschrift finden. Die digitale Ersatzkarte öffnet an dieser Stelle.
2. Fehlenden Teil erfragen oder die konkrete Fehlvorstellung aufgreifen.
3. Mit Teilfrage oder Satzanfang formulieren.
4. Die fehlende fachliche Beziehung erklären.
5. Ein fachliches Beispiel mit der eigenen Antwort vergleichen.

Die aktuelle Eingabe bestimmt die Hilfe bei jedem Öffnen neu. Die Stufennummer bleibt erhalten. Die Auswertung berücksichtigt ganze Aussagen, Richtung der Beziehung, eindeutige Verneinungen und Widersprüche. Unbekannte Zusätze sperren eine positive Rückmeldung. Unklare, fachlich unpassende und unvollständige Texte lassen sich überarbeiten oder mit dem Beispiel vergleichen. Leere Eingaben erhalten einen Satzanfang. Ein abgeschlossener Selbstvergleich wird intern gesondert vermerkt. Das Lesen der digitalen Kartenstelle allein gilt als Quellenarbeit. Nach einem Fehlversuch wird eine Verbesserung bestätigt. Antworten und Zwischenstände liegen nur im Arbeitsspeicher.

Die Auswertung ist regelbasiert. Bei ungewöhnlichen Wörtern, verschachtelten Nebensätzen, unklaren Pronomen oder Verneinungen kann sie gültige Erklärungen offenlassen. Sie beurteilt keine Person. Die Reserve wurde nach Festlegung der Erkennungsregeln getrennt geschrieben und nicht zum Anpassen dieser Regeln verwendet. Eine zweite menschliche Begutachtung und Lernendentexte aus der Schulpraxis stehen aus.
'''
    dump=lambda x:json.dumps(x,ensure_ascii=False,indent=2)
    pack(OUT/'Scaffoldingvertrag.zip',{'Scaffoldingvertrag.md':readme,'Aufgaben-und-Hilfen.json':dump(vertrag)})
    (OUT/'Aufgabenuebersicht.md').write_text('\n'.join(fragen))
    counts={k:{p:res[k,p] for p in ('gesamt','gleich','falschpositiv')} for k in ('entwicklung','reserve','Auswahl')}
    pack(OUT/'Feedback-Testkatalog.zip',{'Entwicklung.txt':(HERE/'pruefdaten/entwicklung.txt').read_bytes(),'Pruefreserve.txt':(HERE/'pruefdaten/reserve.txt').read_bytes(),'Ergebnisse.json':dump(ergebnisse),'Auswertung.json':dump(counts)})
    return counts
