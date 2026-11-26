"""Vergleiche jeden signierten Work-Zustand mit den Aufzeichnungen der Auslieferung."""
import csv
import gzip
import io
import json
import re
from collections import Counter, defaultdict
from zipfile import ZipFile, ZIP_DEFLATED

import openpyxl

from abnahme import SOURCE, documents_pdf
from auslieferung import OUT, QA, sha
from sprachpruefung import documents, bank


def digest(text):
    return sha(text.encode())


def table(rows):
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerows(rows)
    return out.getvalue()


def sources():
    with ZipFile(SOURCE/'Work.zip') as source:
        book = openpyxl.load_workbook(io.BytesIO(source.read('Seiten_und_Medienwechselmatrix.xlsx')), read_only=True)
        sheets = [list(sheet.values) for sheet in book]
    with ZipFile(SOURCE/'Referenz-562ea25.zip') as z:
        states = {r['id']:r for line in z.read('Bildschirmzustaende.jsonl').splitlines() if (r:=json.loads(line))}
        media = list(csv.DictReader(io.StringIO(z.read('Medienwechselmatrix.csv').decode())))
    return sheets,states,media


def observations():
    words = {}
    paired = defaultdict(list)
    for p in sorted(QA.iterdir()):
        if p.name in ['Work-Gegenprobe.json','Weitere-Papieransichten.json']:
            rows=json.loads(p.read_text())
        elif p.name.endswith(('.jsonl.gz','.ndjson.gz')):
            with gzip.open(p,'rt') as stream:
                rows=[json.loads(line) for line in stream]
        else:
            continue
        for n,r in enumerate(rows,1):
            ref=p.name+'#'+str(n)
            current=r.get('ganzer_bildschirm') or r.get('bildschirm') or r.get('text')
            if not current:
                continue
            words.setdefault(current,ref)
            if r.get('alter_bildschirm'):
                paired[r['alter_bildschirm']].append((current,ref))
    return words,paired


def latest(text, module, banks):
    reasons=[]
    if module=='Celina' and 'Zusatzbogen nicht zur Hand?' in text:
        stage=re.search(r'Celina (\d) von 5',text)
        if stage and ' · Schreibe deine Begründung auf. Kreise die richtige Aussage ein.' in text:
            s=banks['Celina']['stages'][int(stage[1])-1]
            k=next(k for k,v in s['choices'].items() if v+'Auswahl ändern' in text)
            answers='\n\n'.join(l+' · '+v for l,v in zip('ABC',s['checks'][k]['answers']))
            text=text.replace(' · Schreibe deine Begründung auf. Kreise die richtige Aussage ein.',
                ' · Lies A, B und C hier am iPad. Schreibe deine Begründung auf den Celina-Bogen. Kreise dort den Buchstaben der passenden Aussage ein.')
            text=text.replace('Zusatzbogen nicht zur Hand?'+('\n\n'+answers if answers in text else ''),answers)
            reasons.append('Celina: Aussagen zur gewählten Empfehlung unmittelbar sichtbar')
    old='4. Erkläre kurz, warum du diese Nachricht hilfreich findest. Wählst du beide, erkläre beide.'
    if old in text:
        text=text.replace(old,banks['UB08']['evaluation']['Förder'].splitlines()[-1])
        reasons.append('LA-02: Nachricht mit biologischem Fakt bewerten')
    old='Am iPad ist deine persönliche Prüfung noch offen. Tippe auf „Lauras Frage – Prüfen“.'
    if old in text:
        text=text.replace(old,' '.join(banks['UB08']['ui']['endRecovery'].split()))
        reasons.append('LA-04: Papiernachweis nach Neustart')
    return text,reasons


def paper_anchor(row, pages):
    person=row[1].split(' · ')[-1]
    if row[3]=='Wiederaufnahme':
        case=row[4] if row[4] in ('Tom','Celina') else 'Laura'
        anchors=[case]
        if case=='Laura':anchors.extend(['Laura 1','Laura 5'])
        elif case in row[8] and 'und' not in row[8]:
            anchors.extend([case+' 1',case+(' 3' if case=='Tom' else ' 5')])
    elif person=='Familiennachrichten':
        anchors=[row[10].split(' / ')[0]]
        if row[3]=='LA-02' and row[2]=='Förder':
            anchors=['1. Welche Frage von Laura wählst du?', '2. Welcher Fakt passt?', '3. Welche Nachricht hilft Laura?', '4. Warum hilft der Fakt Laura?']
        if ' / ' in row[10]:
            field=row[10].split(' / ')[1]
            if field in ('Meine erste Antwort','Nach dem Prüfen'):
                # Two columns are interleaved by pdftotext on Förder and ESA.
                anchors.extend(['Meine erste','Antwort'] if field.startswith('Meine') else ['Nach dem','Prüfen'])
    elif row[10] in ('Mein erster Rat','Mein Schlussrat'):
        anchors=[row[10]]
    else:
        num=int(row[3][2:]) if row[3].startswith('L0') else int(row[3])
        anchors=[person+' '+str(num),'A ','B ','C ']
        if row[10].startswith('Mein Schlussrat'):anchors.append('Mein Schlussrat')
    printed=' '.join(' '.join(pages[int(v)-1].split()) for v in row[9].split('–'))
    assert all(anchor in printed for anchor in anchors),(row[0],anchors,printed[:100])
    return ' | '.join(anchors)


def frame_text(text):
    return text.partition('\n\n')[2] if text.startswith('←\nTagesauswahl\n') else text


def additional(words, observed, states, results):
    old_by_text={s['bildschirm']:s for s in states.values()}
    targets={frame_text(r['soll']):r for r in results.values()}
    extended={}
    alt=QA/'Schnittstellenreferenz/Navigationsprobe.jsonl.gz'
    if alt.is_file():
        with gzip.open(alt,'rt') as src:
            for i,line in enumerate(src,1):
                record=json.loads(line);extended.setdefault(record['text'],i)
    for t,ref in words.items():
        if t in observed:continue
        before=None;approved=None
        if t in old_by_text:
            before=t;source=old_by_text[t]['id'];reason='Wortgleich mit ursprünglicher Browseransicht'
        elif t in extended:
            before=t;source='Nav-Referenz#'+str(extended[t]);reason='Zusätzlicher Aufnahmezeitpunkt; beide Builds wortgleich'
        elif frame_text(t) in targets:
            approved=targets[frame_text(t)]
            before=states[approved['id']]['bildschirm'];source=approved['id']
            reason='Modulwortlaut vollständig gegen Work-Soll geprüft; Aufnahmezeitpunkt der äußeren Abschnittsanzeige separat'
        else:
            source=None;reason='Separater Wortlautvergleich offen'
        yield dict(ist_sha256=digest(t),text=t,nachweis=ref,vergleich=reason,ursprung=source,
            alttext=before,alt_sha256=digest(before) if before else None,
            soll_modul_sha256=digest(frame_text(approved['soll'])) if approved else None)


def run():
    sheets,states,old_matrix=sources()
    rows,extra,inventory,locations,changes=sheets
    canonical=defaultdict(dict)
    for row in changes[1:]:
        i=int(row[0].rsplit('-',1)[1])-1
        assert states[row[12]]['bildschirm'].split('\n')[i]==row[8],(row[0],i)
        canonical[row[12]][i]=row[9]
    assert len(canonical)==1170 and len(changes)==1339
    words,paired=observations()
    banks={m:bank(dom) for m,(dom,_) in documents((OUT/'Fallakte-Gesamt.html').read_bytes()).items()}
    results={}
    for r in inventory[1:]:
        ident=r[0];old=states[ident];original=old['bildschirm'];assert digest(original)==r[10]
        lines=original.split('\n')
        for i,v in canonical[ident].items():lines[i]=v
        work='\n'.join(lines);assert digest(work)==r[11],ident
        target,reason=latest(work,old['modul'],banks)
        result=target if target in words else None
        ref=words.get(target)
        if result is None:
            matches=paired.get(original,[])
            if matches:result,ref=matches[0]
        results[ident]=dict(id=ident,modul=old['modul'],niveau=old['niveau'],alt_sha256=r[10],
            work_sha256=r[11],soll_sha256=digest(target),ist_sha256=digest(result) if result else None,
            soll=target,ist=result,nachweis=ref,originalnachweis=r[8],aenderungsgrund=reason,
            einstufung='wortgleich' if result==target else 'Abweichung' if result else 'ohne Treffer')
    counts=Counter(r['einstufung'] for r in results.values())
    print(counts,flush=True)
    with gzip.open(QA/'Kompaktvergleich.json.gz','wt') as f:json.dump(results,f,ensure_ascii=False)
    observed={r['ist'] for r in results.values() if r['ist']}
    extras=list(additional(words,observed,states,results))
    stats=dict(vertrag=counts,weitere=Counter(x['vergleich'] for x in extras),niveaus={})
    for r in results.values():
        grade=r['niveau'] or 'ohne Niveaustatus';key=r['modul']+' · '+grade
        stats['niveaus'].setdefault(key,Counter())[r['einstufung']]+=1
    (QA/'Vertragsumfang.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2))
    pdfs=documents_pdf()
    matrix=[list(rows[0])+['Nachweis aktueller Bildschirm','Sollprüfung','Zusatzauftrag','Verifizierte Druckanker']]
    for row in rows[1:]:
        row=list(row);k=row[16];result=results[k]
        module='08-12' if '08.12' in row[1] else '02-12'
        pdf=module+'/'+row[8]
        assert pdf in pdfs and all(0<int(v)<=len(pdfs[pdf]) for v in row[9].split('–')),(pdf,row[9])
        anchor=paper_anchor(row,pdfs[pdf])
        if result['aenderungsgrund']:
            if row[1].endswith('Celina'):
                row[17]='Lies A, B und C zu deiner Auswahl am iPad. Schreibe die Begründung auf den Celina-Bogen und kreise dort A, B oder C ein.'
            if row[3]=='LA-02' and row[2]=='Förder':
                row[10]='1. Lauras Frage / 2. Fakt (M oder F) / 3. Nachricht / 4. Warum hilft die Nachricht Laura bei ihrer Frage? Nutze den biologischen Fakt.'
                row[17]=banks['UB08']['evaluation']['Förder']
            if 'LA-04' in row[3] and 'Papiernachweis' in str(result['aenderungsgrund']):
                row[13]='Bereits auf Papier geprüft: ohne erneuten Klick festhalten. Offen: Lauras Frage – Prüfen'
                row[14]='Festhalten bzw. LA-03';row[17]='Status auf Seite 2 lesen. Die erste Antwort stehen lassen. Nur in „Festhalten“ ergänzen.'
        row[12]=result['ist'] or result['soll']
        matrix.append(row+[result['nachweis'],result['einstufung'],'; '.join(result['aenderungsgrund']),anchor])
    ubcsv=table(matrix)
    combined=[list(old_matrix[0])]
    combined.extend(list(row.values()) for row in old_matrix if row['modul']=='PREP')
    for r in matrix[1:]:
        old=states[r[16]]
        combined.append([old['modul'],r[2],r[3],r[4],r[8],r[9],r[10],r[10],r[17],r[13],r[14],r[12],r[16]])
    assert len(combined)==263
    (QA/'Medienwechselmatrix.csv').write_text(ubcsv)
    # Preserve all additional real observations separately, including shell/preparation.
    with ZipFile(QA/'Fallakte-Bildschirmtextvertrag.zip','w',ZIP_DEFLATED,compresslevel=7) as z:
        z.writestr('UB-Bildschirmvergleich.jsonl','\n'.join(json.dumps(r,ensure_ascii=False) for r in results.values()))
        z.writestr('Weitere-Beobachtungen.jsonl','\n'.join(json.dumps(row,ensure_ascii=False) for row in extras))
        for r in sorted(QA.glob('*.gz')):
            if r.name.endswith(('.jsonl.gz','.ndjson.gz')):z.write(r,'Browserquellen/'+r.name)
        for r in [QA/'Weitere-Papieransichten.json',QA/'Work-Gegenprobe.json',QA/'Schnittstellenreferenz/Navigationsprobe.jsonl.gz']:
            if r.is_file():z.write(r,'Browserquellen/'+r.relative_to(QA).as_posix())
        z.write(QA/'Vertragsumfang.json','Vertragsumfang.json')
        z.writestr('Medienwechselmatrix-UB.csv',ubcsv)
        z.writestr('Medienwechselmatrix-Gesamt.csv',table(combined))
        for name,sheet in [('Work-Weitere-Lernwege',extra),('Work-Organisationsfundstellen',locations),('Work-Zeilendiff',changes)]:
            z.writestr(name+'.csv',table(sheet))
    return counts


if __name__=='__main__':run()
