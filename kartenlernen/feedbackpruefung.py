"""Verträge und Prüfergebnisse direkt aus den in der HTML-Datei eingebetteten Funktionen."""
import json
import subprocess
from collections import defaultdict
from collections import Counter
from playwright.sync_api import sync_playwright
from erstellen import HERE,ROOT,OUT,pack,sha

def katalog(pfad):
    daten={}
    for zeile in pfad.read_text().splitlines():
        if zeile.startswith('['):
            thema=zeile[1:-1];daten[thema]=[]
        elif zeile:
            felder=zeile.split('|')
            daten[thema].append(dict(soll=felder[0],merkmal=felder[1] if len(felder)==3 else '',text=felder[-1]))
    return daten

ANALYSE="""({q,m,card,cards,test})=>{
 const r={choice:test.choice||null,text:test.text||'',tries:1,last:null,repeat:false,attempts:[]};
 r.last=q.typ==='text'?Lernfeedback.analyze(q.modell,r.text):{state:r.choice===q.passend?'passend':'fehlvorstellung',parts:[],error:q.alternativen.find(a=>a.text===r.choice)?.muster};
 r.attempts.push(r.last);
 return {diagnose:r.last,rueckmeldung:rueckmeldung(q,m,r),wiederholt:rueckmeldung(q,m,{...r,tries:2,repeat:true}),
 dritter_versuch:rueckmeldung(q,m,{...r,tries:3,repeat:true}),hilfen:[1,2,3,4,5].map(n=>fachhilfe(q,m,r,card,n,cards))};
}"""
GRUPPEN=('entwicklung','reserve','korrektur','zwischenprobe','satzbauprobe','schlussreserve','scaffolding','transferreserve','abnahmereserve','kontrollreserve')
# Die ersten zwei neuen Proben wurden nach ihrer Erstprüfung zu Regressionstests.
STAENDE={'zwischenprobe':'7bab513','satzbauprobe':'7355692','schlussreserve':'56c4eed','transferreserve':'5fff213','abnahmereserve':'3b9811b','kontrollreserve':'a59c7c3'}
BATCH='({q,m,card,cards,tests})=>tests.map(test=>('+ANALYSE+')({q,m,card,cards,test}))'

def beurteilen(test,d):
    soll,merkmal=test['soll'],test.get('merkmal','')
    ist=d.get('kind',d['state'])
    if test['satz'] in ('entwicklung','reserve','Auswahl'):
        ist=d['state']
    gleich=ist==soll
    if merkmal in ('a','b'):
        gleich=gleich and d['parts']==[merkmal]
    elif merkmal=='richtung':
        gleich=gleich and d.get('relation')=='umgekehrt' and d['state']=='vertauscht'
    elif merkmal=='beide':
        gleich=gleich and len(d['parts'])==2
    elif merkmal and soll in ('fehlvorstellung','verwechslung','widerspruch'):
        gleich=gleich and d.get('error')==merkmal
    if gleich:return 'korrekt'
    if d['state']=='passend':return 'falsch_positiv'
    if soll=='passend' and d['state'] in ('fehlvorstellung','widerspruch','vertauscht'):return 'ungerechtfertigt_negativ'
    if d['state']=='unsicher' or (d['state']=='teilweise' and soll=='passend'):return 'vorsichtig_unvollstaendig'
    return 'falsche_diagnose'

def hilfen_pruefen(q,m,card,cards,medizin,result):
    diag,h,fb=result['diagnose'],result['hilfen'],result['rueckmeldung']
    assert len(h)==5 and all(h)
    karte,stelle=(cards[diag['quelle'][0]],diag['quelle'][1]) if diag.get('quelle') else (card,q['abschnitt'])
    assert h[0]==f"Lies auf deiner Infokarte {karte['nummer']} – {karte['titel']} unter der Überschrift „{karte['texte'][stelle]['titel']}“."
    assert h[4]==(m['beispiel'] if m else q['grund'])
    if not m:
        if diag['state']=='fehlvorstellung':
            alt=next(a for a in q['alternativen'] if a['muster']==diag['error'])
            assert alt['impuls'] in fb and alt['impuls']==h[1] and fb!=result['wiederholt']
        return
    if diag['state']=='unsicher':
        assert 'Deine Antwort kann richtig sein. Vergleiche sie mit diesem Beispiel.' in fb
    if diag['kind']=='zusatz':
        assert 'Zusatz' in fb and 'Beide Schritte' in h[1] and 'Zusatz' in h[2]
    if diag['state']=='vertauscht':
        assert m['zuerst'] in fb and h[1]==m['zuerst'] and 'kann richtig sein' not in fb
    elif diag['kind']=='beziehung':
        assert h[1]==m['verknuepfen']
    elif diag['kind']=='unsicher':
        assert h[1]=='Vergleiche deine Erklärung mit dem Beispiel.' and h[2]==m['vergleich']
    if diag['kind']=='ergebnis':
        assert diag['parts']==[] and diag['ergebnis'] and 'Du nennst das Ergebnis.' in fb
    if diag['error']:
        frage=medizin[diag['error']]['frage'] if diag.get('quelle') else m['fragen'][diag['error']]
        assert frage in fb and h[1]==frage
        if diag.get('quelle'):assert medizin[diag['error']]['info'] in fb and 'kann richtig sein' not in fb
        assert fb!=result['dritter_versuch']
    if diag['kind']=='teilweise':
        pos=0 if diag['parts']==['a'] else 1
        assert m['teile'][pos] in fb and h[1]==m['impulse'][1-pos] and h[3]==m['teile'][1-pos]

def zusammenfassung(rows):
    ergebnis={}
    for schluessel in ('satz','modell','soll','merkmal'):
        groups=defaultdict(list)
        for r in rows:groups[r.get(schluessel) or 'ohne'].append(r)
        ergebnis[schluessel]={k:dict(Counter(r['bewertung'] for r in v),gesamt=len(v)) for k,v in groups.items()}
    return ergebnis

def run(previous):
    sets={n:katalog(HERE/'pruefdaten'/f'{n}.txt') for n in GRUPPEN}
    frozen={name:subprocess.check_output(['git','show',commit+':kartenlernen/diagnose.js'],cwd=ROOT).decode() for name,commit in STAENDE.items()}
    def version(commit,name):return subprocess.check_output(['git','show',commit+':kartenlernen/'+name],cwd=ROOT).decode()
    for name in ['gesundheit.js','diagnose.js','antwortmodelle.py','hilfe.js']:
        assert version(STAENDE['kontrollreserve'],name)==(HERE/name).read_text(),name
    for name in ('transferreserve','abnahmereserve','kontrollreserve'):
        frozen[name]=version(STAENDE[name],'gesundheit.js')+'\n'+frozen[name]
    vertrag=[];ergebnisse=[];fragen=['# Aufgabenübersicht','']
    with sync_playwright() as pw,pw.chromium.launch() as browser:
        page=browser.new_page();page.goto((OUT/'Vorbereitung.html').as_uri())
        old=browser.new_page();old.goto((previous/'Vorbereitung.html').as_uri())
        oldmat=old.evaluate("JSON.parse(document.querySelector('#material').textContent)")
        probe=browser.new_page()
        mat=page.evaluate("JSON.parse(document.querySelector('#material').textContent)")
        medizin=page.evaluate("Object.fromEntries(Object.entries(Lernfeedback.gesundheit).map(([code,{info,frage,karte,abschnitt}])=>[code,{info,frage,karte,abschnitt}]))")
        for tier,l in mat['levels'].items():
            fragen.extend(['## '+('Förder' if tier=='Foerder' else tier),''])
            for i,(q,card) in enumerate(zip(l['fragen'],l['cards']),1):
                ref=card['texte'][q['abschnitt']]
                m=mat['modelle'].get(q.get('modell'));tests=[]
                if m:
                    model=q['modell']
                    history={r['text'].strip().casefold() for n in GRUPPEN[:-1] for r in sets[n][model]}
                    held={r['text'].strip().casefold() for r in sets['kontrollreserve'][model]}
                    assert len(held)>=20 and len(held)==len(sets['kontrollreserve'][model]) and history.isdisjoint(held) and len(history|held)>=100
                    for n,bank in sets.items():tests.extend(dict(satz=n,**row) for row in bank[model])
                else:tests=[dict(satz='Auswahl',choice=o,soll='passend' if o==q['passend'] else 'fehlvorstellung') for o in q['optionen']]
                faelle=[]
                oldl=oldmat['levels'][tier]
                before=old.evaluate(BATCH,dict(q=oldl['fragen'][i-1],card=oldl['cards'][i-1],cards=oldl['cards'],m=oldmat['modelle'].get(q.get('modell')),tests=tests))
                after=page.evaluate(BATCH,dict(q=q,card=card,cards=l['cards'],m=m,tests=tests))
                first={}
                if m:
                    for name,src in frozen.items():
                        rows=sets[name][model]
                        results=probe.evaluate("""({src,rows,model})=>{const f=new Function(src+';return Lernfeedback.analyze')();return rows.map(r=>f(model,r.text));}""",dict(src=src,rows=rows,model=model))
                        first.update({(name,t['text']):r for t,r in zip(rows,results)})
                for test,result,prev in zip(tests,after,before):
                    hilfen_pruefen(q,m,card,l['cards'],medizin,result)
                    bewertung=beurteilen(test,result['diagnose'])
                    if test['satz'] in ('Auswahl','entwicklung','korrektur','scaffolding'):assert bewertung=='korrekt',(test,result)
                    row=dict(niveau=tier,kapitel=i,modell=q.get('modell'),**test,ist=result['diagnose']['state'],bewertung=bewertung,vorher=prev,**result)
                    row['hilfenauswertung']=('sollbezogen' if bewertung=='korrekt' else
                        'vorsichtiger Vergleich oder Teilhinweis' if bewertung=='vorsichtig_unvollstaendig' else 'am Soll vorbeigeführt')
                    if (test['satz'],test.get('text')) in first:
                        d=first[test['satz'],test['text']]
                        row.update(erstpruefung=d,erstbewertung=beurteilen(test,d))
                    faelle.append(row);ergebnisse.append(row)
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

Bei unklarer Bedeutung enthält der optionale Vergleich den eigenen Entwurf, zwei aufgabenspezifische Vergleichsfragen und das biologische Beispiel. Eine bestätigte Vertauschung führt zur Frage nach der Ursache. Das eigene Urteil im Vergleich setzt nur den Sitzungsstatus „selbstvergleich“. Das Ergebnis einer Verhütungsaussage und die beiden Teilziele können getrennt erkannt werden.

Für gesundheitlich relevante Fehlaussagen nennt Gemeinsame-Fehlvorstellungen.json den Korrekturtext und den Denkimpuls. Die Diagnosen in Aufgaben-und-Hilfen.json führen unter quelle bei einem solchen Treffer den nullbasierten Karten- und Abschnittsindex. Dadurch öffnet die Hilfe auch bei einem methodenübergreifenden Zusatz die zutreffende Originalstelle. Die reguläre Frage bleibt ihrer eigenen Karte zugeordnet.

Die aktuelle Eingabe bestimmt die Hilfe bei jedem Öffnen neu. Die Stufennummer bleibt erhalten. Die Auswertung berücksichtigt ganze Aussagen, Richtung der Beziehung, eindeutige Verneinungen und Widersprüche. Unbekannte Zusätze sperren eine positive Rückmeldung. Unklare, fachlich unpassende und unvollständige Texte lassen sich überarbeiten oder mit dem Beispiel vergleichen. Leere Eingaben erhalten einen Satzanfang. Ein abgeschlossener Selbstvergleich wird intern gesondert vermerkt. Das Lesen der digitalen Kartenstelle allein gilt als Quellenarbeit. Nach einem Fehlversuch wird eine Verbesserung bestätigt. Antworten und Zwischenstände liegen nur im Arbeitsspeicher.

Die Auswertung ist regelbasiert. Bei ungewöhnlichen Wörtern, verschachtelten Nebensätzen, unklaren Pronomen oder Verneinungen kann sie gültige Erklärungen offenlassen. Sie beurteilt keine Person. Die Reserve wurde nach Festlegung der Erkennungsregeln getrennt geschrieben und nicht zum Anpassen dieser Regeln verwendet. Eine zweite menschliche Begutachtung und Lernendentexte aus der Schulpraxis stehen aus.
'''
    readme+='''
## Nachprüfen und erweitern

Die Aufgaben in aufgaben.py verweisen mit modell auf eines der Modelle in antwortmodelle.py. Dort stehen Kern, zugelassene Alternativen, Beziehung, Fehlvorstellungen, Denkfragen und Beispiel. diagnose.js liefert state, kind, parts, error und relation. hilfe.js verwendet die aktuelle Analyse im Editor, den zuletzt geprüften Versuch in der Rückmeldung und die im Arbeitsspeicher geführten Versuche. Für ein neues Modell werden fachliche Satzmuster und Gegenproben einschließlich Negation und Umkehrrichtung benötigt.

Der Feedback-Testkatalog enthält pro Eingabe die alten und neuen tatsächlichen Browser-Ausgaben. Die Kategorien sind vorher festgelegt. Ein vorsichtiger Selbstvergleich bei einer richtigen Antwort ist eine verfehlte Direktdiagnose. Entwicklung und alte Reserve stammen aus dem Ausgangsstand. Korrektur, Zwischenprobe und Satzbauprobe gehören zum Regressionsbestand. Ihre später verbesserten Trefferquoten sind keine blinden Ergebnisse. Für die beiden Zwischenproben ist die erstmalige Auswertung mit der zuvor festgelegten Revision separat enthalten. Die frühere Schlussreserve gehört jetzt zum Regressionsbestand. Die Transferprobe wurde erstmals gegen 5fff213 ausgewertet. Nach acht offenen Einordnungen wurden ihre Texte als Regression übernommen. Die nächste Probe gegen 3b9811b ergab sieben vorsichtige Diagnosen. Beide Zwischenproben sind als Regression erhalten. Für die letzte Kontrollreserve wurden Erkennung, Katalog und Hilfetexte vorab auf a59c7c3 festgelegt. Die 80 Texte dieser Reserve wurden anschließend formuliert. Bei acht alten umgekehrten Kausalsätzen gilt gemäß aktuellem Auftrag explizit „vertauscht“. Der Satz „Die Eizelle kann nicht befruchtet werden“ nennt nur das Ergebnis. Die früheren Sollangaben sind in b3abb52 erhalten. Alle Freitextfälle enthalten die tatsächlichen Rückmeldungen und fünf Hilfeansichten. Die Spalte hilfenauswertung prüft die Übereinstimmung mit der Sollbedeutung und die implementierten fachlichen Hilferegeln. Sie misst keine Lernwirkung. Keine Bewertung durch eine zweite Person. Zum Wiederholen den Workflow „Vorbereitung · Vier Kapitel“ mit vollständiger Git-Historie ausführen.
'''
    dump=lambda x:json.dumps(x,ensure_ascii=False,indent=2)
    pack(OUT/'Scaffoldingvertrag.zip',{'Scaffoldingvertrag.md':readme,'Aufgaben-und-Hilfen.json':dump(vertrag),'Gemeinsame-Fehlvorstellungen.json':dump(medizin)})
    (OUT/'Aufgabenuebersicht.md').write_text('\n'.join(fragen))
    final=[r for r in ergebnisse if r['satz']=='kontrollreserve']
    assert all(r['diagnose']==r['erstpruefung'] for r in final)
    Ziele={'sprachlich_normal':lambda r:r['merkmal']=='normal','schreibung':lambda r:r['merkmal']=='schreibung','teil_und_fehler':lambda r:r['soll'] in ('teilweise','fehlvorstellung','verwechslung','widerspruch')}
    zielwerte={}
    for k,fn in Ziele.items():
        subset=[r for r in final if fn(r)]
        # Vorher kannte nur die gröberen Zustände. Beide Messweisen ausweisen.
        grob={'verwechslung':'fehlvorstellung','beziehung':'unsicher','zusatz':'unsicher'}
        zielwerte[k]=dict(gesamt=len(subset),korrekt=sum(r['bewertung']=='korrekt' for r in subset),
            vorher_grob=sum(r['vorher']['diagnose']['state']==grob.get(r['soll'],r['soll']) for r in subset),
            jetzt_grob=sum(r['diagnose']['state']==grob.get(r['soll'],r['soll']) for r in subset))
    counts=dict(gesamt=zusammenfassung(ergebnisse),kontrollreserve=zusammenfassung(final),hilfen=dict(Counter(r['hilfenauswertung'] for r in final)),
        vorher_nachher={soll:{'gesamt':len(rows),'vorher':sum(beurteilen(r,r['vorher']['diagnose'])=='korrekt' for r in rows),'jetzt':sum(r['bewertung']=='korrekt' for r in rows)} for soll in sorted({r['soll'] for r in final}) if (rows:=[r for r in final if r['soll']==soll])},ziele=zielwerte,
        je_modell={m:zusammenfassung([r for r in final if r['modell']==m])['soll'] for m in sets['kontrollreserve']},
        verschiedene_texte={m:len({r['text'].strip().casefold() for r in ergebnisse if r['modell']==m}) for m in sets['kontrollreserve']},
        erstpruefungen={n:dict(commit=c,sha256=sha(frozen[n].encode()),auswertung=dict(Counter(r['erstbewertung'] for r in ergebnisse if r['satz']==n))) for n,c in STAENDE.items()})
    pack(OUT/'Feedback-Testkatalog.zip',{**{n+'.txt':(HERE/'pruefdaten'/(n+'.txt')).read_bytes() for n in GRUPPEN},'Ergebnisse.json':dump(ergebnisse),'Auswertung.json':dump(counts)})
    return counts
