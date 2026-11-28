"""Stellt Work-Material, Matrix, reale Protokolle und SCORM eines geprüften Commits zusammen."""
import base64
import gzip
import hashlib
import json
import re
import shutil
import subprocess
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree, html
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from clt_inhalte import klar, QUELLEN, NACHRICHTEN
from material import LEVELS,vertrag
from matrix import matrix

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=ROOT/'dist/Gesamt'
QA=ROOT/'build/CLT'
PHYS=ROOT/'build/Gesamtpruefung/Ergonomie'
PROFILES=('quer','hoch','kurs','schmal','tastatur')

def dump(o):
    return json.dumps(o,ensure_ascii=False,indent=2)
def sha(b):
    return hashlib.sha256(b).hexdigest()
def archive(path,entries):
    with ZipFile(path,'w',ZIP_DEFLATED,compresslevel=8) as z:
        for k,v in sorted(entries.items()):z.writestr(k,v)
    with ZipFile(path) as z:assert z.testzip() is None
def bank(raw,id):
    return json.loads(html.fromstring(raw.decode()).xpath(f'string(//script[@id="{id}"])'))
def md_contract(c):
    parts=['# Material für Work',c['format'],c['erarbeitung'],c['unterbrechung'],c['sicherung']]
    for t,v in c['niveaus'].items():
        parts.append('## '+t)
        for card in v.values():
            parts.extend(['### '+card['titel'],card['auftrag']])
            if 'hilfe' in card:parts.append(card['hilfe'])
    if 'empfehlungsraeder' in c:
        for k,v in c['empfehlungsraeder'].items():parts.append(' · '.join(v) if isinstance(v,list) else v)
    parts+=['## Zeitplanung für 45 Minuten']+[f'{a} · {n} Minuten' for a,n in c['phasen']]
    return '\n\n'.join(parts)
def verify_source(day,b):
    git=lambda f:subprocess.check_output(['git','show','c4814a9:'+f],cwd=ROOT)
    if day=='08':
        ref=json.loads(git('module/familienrat/material.json'))
        for n,person in b['cases'].items():
            orig=ref['cases'][n]
            for key in ['transfer','addition','connection','missing']:assert person[key]==orig[key]
            visible=orig['lesefassung'].replace('deine Ausbildung beenden. Vielleicht möchtest du später Kinder.',
                              'deine Ausbildung beenden und vielleicht später Kinder bekommen.')
            if n in NACHRICHTEN:visible=' '.join(NACHRICHTEN[n])
            assert person['original']==person['lesefassung']==visible
            lines=[t.strip() for t in re.findall(r'[^.!?]+[.!?]+|[^.!?]+$',visible)]
            assert len(person['tasks'])==len(orig['tasks'])
            for task,previous in zip(person['tasks'],orig['tasks']):
                clean=lambda x:json.loads(json.dumps(x,ensure_ascii=False).replace('Öffne „Fakt · Wert · Norm · Folgerung“. Lies die vier Fragen.','Tippe auf „Begriff erklären“. Wähle ein Wort.'))
                for key in previous:
                    if key=='evidenceSentences':
                        assert [lines[i] for i in task[key]]==QUELLEN[n][task['id']]
                    elif n in NACHRICHTEN and task['id'] in (*QUELLEN[n],'Leerstelle') and key in ('prompt','hints','helpByLevel'):
                        assert task[key] and (key!='hints' or len(task[key])==5)
                    elif n in NACHRICHTEN and task['id']=='Leerstelle' and key=='answers':
                        for now,old in zip(task[key],previous[key],strict=True):
                            if old['ok']:feedback='Ja. Für diesen Rat fehlt noch eine biologische Information.'
                            else:
                                line=QUELLEN[n][old['text']][-1]
                                assert line in now['feedback'] and line in visible
                                feedback=now['feedback']
                            assert now==dict(old,feedback=feedback)
                    elif n=='Freundin' and task['id']=='Folgerung' and key=='answers':
                        for i,(a,old) in enumerate(zip(task[key],previous[key],strict=True)):
                            assert a==(dict(old,feedback='Die Arztpraxis ist ein nächster Schritt. Was rät die Freundin Laura zur Schwangerschaft?') if i==2 else old)
                    else:assert task[key]==clean(previous[key]),(n,task['id'],key)
        for k in ('cards','limits','opening','second'):assert b[k]==ref[k]
        return 'Die vier sichtbaren Nachrichten und Quellenaufgaben verwenden dieselbe Lesefassung. Alle fachlich passenden Quellenstellen wurden am vollständigen Satzwortlaut verankert. Die unterstützende Bedienanweisung nennt den tatsächlichen Begriffszugang. Fachliche Antworten, Rückmeldungen, Anwendungsfragen, Karten, Grenzen und Lauras Anliegen wurden feldweise gegen c4814a9 geprüft.'
    old=json.loads(git('data/laura-0212.json'));cards=json.loads((HERE/'Infokarten.json').read_text())
    for k in ('opening','facts','goalRules','strategies'):assert b[k]==old[k],k
    for k,s in b['stages'].items():
        ref=old['stages'][k]
        for field in ('knownFacts','learningGoal','recovery'):assert s[field]==ref[field]
        for t,l in s['levels'].items():
            assert l['message']==ref['levels'][t]['message']
            if t in ('Foerder','ESA'):
                wortlaut=json.dumps(l,ensure_ascii=False).lower()
                for begriff in ('synthetisch','medizinische eignung klären','sagt ihre verträglichkeit nicht voraus'):
                    assert begriff not in wortlaut,(k,t,begriff)
            for m,w in l['strategies'].items():
                original=ref['levels'][t]['strategies'][m]
                for field in ('status','reply','feedback','condition','questions'):assert w[field]==(klar(original[field]) if field in ('condition','feedback') else original[field])
                if t in ('ESA','Foerder'):assert w['options']==[dict(o,text=klar(o['text']),feedback=klar(o['feedback'])) for o in original['options']]
                else:
                    assert [s['text'] for s in w['options']]==list(map(klar,ref['anchors'].values()))
                    assert [s['feedback'] for s in w['options']]==[klar(ref['anchorFeedback'][a]['text']) for a in ref['anchors']]
    for i,m in enumerate(('K','P','Cu','H')):
        for sec in b['cards'][m]['sections'].values():
            for t,cs in cards.items():assert sec['levels'][t]==next(r['volltext'] for r in cs[i]['texte'] if r['titel']==sec['title'])
    return 'Fallinformationen, bekannte Anliegen je Abschnitt, Lernziele, Empfehlungen, Bedingungen, Rückfragen und Reaktionen entsprechen c4814a9. Die früher per Buchstabe geprüften Aussagen stehen auf MSA/AHR als vollständiger Wortlaut zur Auswahl. Alle 80 niveauabhängigen Kartenabschnitte stimmen mit den aktuellen Work-Texten der Vorbereitung überein.'
def release():
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    both={}
    for day in ('02','08'):
        stem='Fallakte-'+day+'-12';raw=(OUT/(stem+'.html')).read_bytes();package=OUT/(stem+'-SCORM12.zip')
        with ZipFile(package) as z:
            assert not z.testzip() and z.read('index.html')==raw
            manifest=etree.parse(BytesIO(z.read('imsmanifest.xml')))
            etree.XMLSchema(etree.parse(str(ROOT/'scorm/adlcp_rootv1p2.xsd'))).assertValid(manifest)
            assert manifest.xpath('string(//*[local-name()="schemaversion"])')=='1.2'
        assert revision.encode() in raw
        mods={k:base64.b64decode(v) for k,v in re.findall(r'<script id="modul-(\d+)" type="application/octet-stream">([^<]+)',raw.decode())}
        if day=='02':assert set(mods)=={'02'};both['02']=sha(mods['02'])
        else:assert set(mods)=={'02','08'} and sha(mods['02'])==both['02']
        b=bank(mods[day],'materialvertrag' if day=='02' else 'material')
        protection=verify_source(day,b);target=ROOT/'dist/CLT'/stem;target.mkdir(parents=True,exist_ok=True)
        logs={};screens={};rows={};counts=[];geoerrors=[];ngeo=0;paths=0;seiten=[]
        for e in ('chromium','webkit'):
            for t in LEVELS:
                base=QA/f'{day}-{t}-{e}'
                if day=='02':
                    evidence=json.loads((base/'Ratfolgen.json').read_text());assert evidence['html_sha256']==sha(raw)
                    assert len(set(evidence['folgen']))==1792;paths+=len(evidence['folgen'])
                    assert len(evidence['zusatz']['Tom'])==1 and len(evidence['zusatz']['Celina'])==108
                    logs[f'{e}/{t}/Ratfolgen.json']=(base/'Ratfolgen.json').read_bytes()
                else:
                    status=json.loads((base/'Statuswege.json').read_text())
                    assert status['html_sha256']==sha(raw) and len(status['pruefungen'])==48*18
                    logs[f'{e}/{t}/Statuswege.json']=(base/'Statuswege.json').read_bytes()
                personal=QA/'Lernspuren'/f'{day}-{t}-{e}'
                lr=json.loads((personal/'Lernspuren.json').read_text())
                assert lr['revision_html']==sha(raw) and len(lr['antwortpaare'])==(28 if day=='02' else 16) and not lr['fehler']
                assert lr['altbestand']==1058 and len(lr['ansichten'])==20
                for name in ('Lernspuren.json','Altbestand.json.gz'):logs[f'Lernspuren/{e}/{t}/'+name]=(personal/name).read_bytes()
                for pic in personal.glob('*.jpg'):screens[f'Lernspuren/{e}/{t}/'+pic.name]=pic.read_bytes()
                if (personal/'Lernweg.webm').is_file():screens['Demonstration.webm']=(personal/'Lernweg.webm').read_bytes()
                for row in lr['ansichten']:
                    z=dict(text=row['text'],task=row['schritt'],caseName='Persönlicher Vergleich',event=row['schritt'],ids=row['tasten'],question=row['titel'])
                    rows[t,dump(z)]=(t,z)
                if day=='08':
                    more=json.loads((base/'Familienfolgen.json').read_text())
                    assert more['html_sha256']==sha(raw) and not more['errors'] and sum(v['pass'] for v in more['counts'].values())==1414
                    logs[f'{e}/{t}/Familienfolgen.json']=(base/'Familienfolgen.json').read_bytes()
                for profile in PROFILES:
                    d=base/profile;prefix=f'{e}/{t}/{profile}/'
                    row=json.loads((d/'Pruefung.json').read_text());assert row['html_sha256']==sha(raw);counts.append(row)
                    for k in ('Pruefung.json','Zustaende.json.gz','Geometrie.json'):logs[prefix+k]=(d/k).read_bytes()
                    for v in json.loads(gzip.decompress(logs[prefix+'Zustaende.json.gz'])):rows[(t,dump(v))]=(t,v)
                    for g in json.loads(logs[prefix+'Geometrie.json']):
                        seiten.extend(dict(profil=prefix,**v) for v in g['seiten']);ngeo+=g['checks'];geoerrors.extend((prefix,issue) for issue in g['issues'])
                    if t in ('Förder','AHR') and profile in ('hoch','kurs','quer'):
                        img=next(d.glob('*.jpg'));screens[prefix+img.name]=img.read_bytes()
        for p in PHYS.glob('Trefferpruefung-*.json'):
            data=json.loads(p.read_text())
            if data['html_sha256']==sha((OUT/'Fallakte-08-12.html').read_bytes()):logs['Treffer/'+p.name]=p.read_bytes()
        hits=set()
        for k,v in logs.items():
            if k.startswith('Treffer/'):
                for x in json.loads(v)['wege']:hits.add((x['browser'],x['breite'],x['niveau']))
        assert len(hits)==40,len(hits)
        suffix='Laura' if day=='02' else 'Familie'
        for p in PHYS.glob('*-'+suffix+'.jpg'):screens['Treffer/'+p.name]=p.read_bytes()
        for e in ('chromium','webkit'):
            drafts=(QA/'Gegenpruefung'/f'Entwuerfe-{e}.json').read_bytes()
            audit=json.loads(drafts)
            assert audit['html_sha256' if day=='02' else 'familien_html_sha256']==sha(raw)
            assert len(audit['wege'])==70 and len(audit['fehlerhilfen'])==500 and len(audit['zusaetzliche_wege'])==68
            logs['Entwuerfe-und-Fehlerhilfen/'+e+'.json']=drafts
            evidence=(QA/'Sitzung'/('Sitzungspruefung-'+e+'.json')).read_bytes()
            assert json.loads(evidence)['html_sha256']==sha((OUT/'Fallakte-08-12.html').read_bytes())
            logs['Tageswechsel/'+e+'.json']=evidence
            img=QA/'Sitzung'/f'{e}-{day}-frueher-Stopp.jpg';screens['Stundenabschluss/'+img.name]=img.read_bytes()
        longtext=QA/'Langtext'
        evidence=(longtext/'Langtextpruefung.json').read_bytes()
        assert json.loads(evidence)['html_sha256']==sha((OUT/'Fallakte-08-12.html').read_bytes())
        img=longtext/(day+'-Aussage-mit-grosser-Schrift.jpg')
        screens[img.name]=img.read_bytes();logs['Langtextpruefung.json']=evidence
        logs['Seitenumfang.json.gz']=gzip.compress(dump(seiten).encode(),mtime=0)
        c=vertrag(day,b);c['revision']=revision
        if day=='02':
            source=(ROOT/'material/lehrkraft/empfehlungsrad.html').read_text()
            source=source.replace('<script src="../../data/dialogdaten.js"></script>','')
            source=source.replace("['K','P','Cu','H'].map(id => [FALLAKTE.methods[id][0]])",
                                  "[['Kondom'],['Kombinationspille'],['Kupferspirale'],['Hormonspirale']]")
            for font in ('dmsans','dmseriftext'):
                source=source.replace('../../assets/'+font+'.ttf','data:font/ttf;base64,'+base64.b64encode((ROOT/'assets'/(font+'.ttf')).read_bytes()).decode())
            archive(target/'Empfehlungsraeder.zip',{name+'.html':source.replace("new URLSearchParams(location.search).get('rad') === '2'",value)
                    for name,value in [('Erstes-Empfehlungsrad','false'),('Zweites-Empfehlungsrad','true')]})
        (target/'Unterrichtssteuerung.md').write_text('\n\n'.join(['# Unterrichtssteuerung',c['erarbeitung'],c['unterbrechung'],c['sicherung'],'## Zeitplanung für 45 Minuten']+[f'{n} Minuten · {a}' for a,n in c['phasen']]))
        archive(target/'CLT-Abnahmematrix.zip',{'Matrix.csv':matrix(rows.values(),day),'Fachdidaktische-Durchsicht.md':(HERE/('Beratung.md' if day=='02' else 'Familiennachrichten.md')).read_bytes(),'Grundlagen.md':(HERE/'Grundlagen.md').read_bytes(),'Perspektiven.md':(HERE/'planung.md').read_bytes(),'Zeitplanung.json':dump(c['phasen'])})
        for engine in ('chromium','webkit'):
            for name in ('Einstieg','Sprache'):
                key=f'{name}-{engine}.json';payload=(QA/'Freigabestufen'/key).read_bytes()
                parsed=json.loads(payload)
                if name=='Sprache':
                    assert parsed['html_sha256']==sha((OUT/'Fallakte-08-12.html').read_bytes()) and parsed['ub1_sha256']==sha((OUT/'Fallakte-02-12.html').read_bytes())
                else:assert all(row['html_sha256']==sha((OUT/f"Fallakte-{row['tag']}-12.html").read_bytes()) for row in parsed)
                logs['Freigabestufen/'+key]=payload
        for name in ('Antwortmodelle.json',):
            shutil.copyfile(QA/'Freigabestufen'/name,target/name)
        for name in ('Sprachreserve.tsv','Sprachreserve-blind.tsv','Arbeitsplatz-und-Diagnose.md'):
            shutil.copyfile(HERE/name,target/name)
        archive(target/'Pruefprotokolle.zip',logs)
        failnote=f'Bei {len(geoerrors)} Beobachtungen ließ sich die vollständige Erreichbarkeit einer angebotenen Taste nicht nachweisen. Die betreffenden Beschriftungen, Positionen, Browser und Fenster stehen im Geometrieprotokoll.' if geoerrors else 'Alle in den Geometrieprotokollen erfassten aktiven Steuerungen waren über ihren aktuellen Ansichtsabschnitt erreichbar.'
        report=f"""# Prüfung am {day}.12.2026

Commit `{revision}`. SHA-256 der Offline-Datei `{sha(raw)}`.

{protection}

Gegenprüfung gegenüber ac86cb8: Auf 46 sendbaren Wegen musste der HIV-Irrtum vor der Kontrollauswahl berichtigt werden. Alle 46 Empfehlungen blieben nach der Überarbeitung sendbar. Weitere 68 Freitextwege betrafen Familiennachrichten, Tom und Celina. Zusätzlich wurden auf 500 unterschiedlichen Quellen-, Auswahl- und Konfliktwegen der Familiennachrichten und Zusatzfälle jeweils alle fünf Hilfetexte geprüft. Die Zahlen beziehen sich jeweils auf einen Browser. Die Protokolle enthalten die tatsächlich angezeigten Hilfen.

Die erste Antwort wird vor Fachkarten und inhaltlichen Hilfen mit dem eigenen Grund im Arbeitsspeicher festgehalten. Beim Signal „Stundenabschluss“ stehen alle entscheidungsrelevanten Informationen bereit. Erst nach dem eigenen abschließenden Grund erscheint der Vergleich. Nach einem Neustart zeigt er eine fehlende erste Antwort ausdrücklich an. Persönliche Entscheidungen bespricht die Klasse. Die freiwilligen Zusatzfälle öffnen nach einer tatsächlich ausgefüllten persönlichen Abschlussaufgabe.

Pro Browser und Niveau wurden alle {28 if day=='02' else 16} geordneten Paare aus erster und abschließender Auswahl eingegeben. Die neue Textgegenprobe umfasst {len(json.loads((HERE/'Freitext-Gegenbestand.json').read_text()))} vorgegebene Äußerungen, davon im ersten Besuch die verhütungsbezogenen und neutralen Aussagen. Der zusätzliche Altbestand umfasst 1.058 unabhängige Freitexte je Browser und Niveau. Die Protokolle trennen eine erkannte konkrete Fehlvorstellung von einem unbewerteten Entwurf. Der Vergleich zweier persönlicher Entscheidungen vergibt weder Punkte noch ein Lernzuwachsurteil.

{len(counts)} Browser-, Niveau- und Fensterdurchläufe. Die Matrix umfasst {len(rows)} unterschiedliche protokollierte Kombinationen von Niveau, Kontext, Wortlaut und Bedienelementen. {ngeo} Geometrieprüfungen erfassten aktive Steuerelemente. {failnote} Im Protokoll Seitenumfang.json.gz steht die gemessene Anzahl der Teilansichten pro Arbeitszustand. Weitere 40 Tast- und Navigationstests mit Chromium und WebKit prüften physische Treffer bis zum äußeren Fenster. Die Bildschirmtastatur wurde durch eine verkleinerte Höhe simuliert.

{(str(paths)+' vollständige Folgen sendbarer Laura-Empfehlungen. Zusätzlich wurden unpassende Einzelvorschläge, Begründungsoptionen, wiederholte Fehler, Karten, Rückfragen, Hilfen und beide Zusatzfälle geprüft. Pro Niveau und Browser wurden alle 108 sendbaren Celina-Folgen und Toms vollständiger Weg gespielt.') if day=='02' else 'Alle vier Personen mit eigenständiger Auswahl, Fehlversuchen, Hilfen und Lösungsoffenlegung. Alle zwölf Kombinationen aus Gewichtung und Anliegen wurden bearbeitet, einschließlich begründeter Unsicherheit und anderer sachlicher Verknüpfungen. Je Niveau und Browser prüften 864 Statusbeobachtungen die Teilmengen falscher Auswahlen bei Hilfetiefe null bis fünf und nachträglich geöffneter Hilfe. Die Quellenwahl allein vergibt keinen Hilfestatus.'}

Das Offline-HTML und index.html im SCO stimmen byteweise überein. Das SCORM-1.2-Manifest wurde gegen das Schema geprüft. Version A enthält ausschließlich den ersten Unterrichtstag. Beide Fassungen enthalten dasselbe erste Modul.

## Grenzen und Geltungsbereich

Prüfprotokolle enthalten die tatsächlich beobachteten Ausgaben. Wiederholungen führen bei einzelnen Aufgaben auf denselben Fehlertext zurück. Die Quelle der Familienantworten, Lösungsoffenlegung, verspätete Hilfe, vorheriger Vorschlag und fachlicher Stand bleiben unterscheidbar. Unendlich viele Freitexte und Unterbrechungsfolgen lassen sich nicht vollständig prüfen. Bei freien Begründungen prüft die Software ausdrücklich formulierte medizinische Behauptungen mit eng begrenzten Regeln. Die Antwortmodelle prüfen weitere eng beschriebene Gedanken. Bei offenem Wortlaut bleibt der Selbstvergleich verfügbar. Die gemessenen Treffer und Abweichungen stehen in Freigabestufen/Sprache; nicht erkannte richtige Antworten werden als Abweichung gezählt. Persönliche Gewichtungen werden im Unterricht besprochen. Native Tastatur, produktives itslearning, Hilfsmittel wie Screenreader, fremde Schriftmetriken, tatsächliches Leseverständnis und reale Minuten mit 28 Lernenden sind offen. Die Matrix begründet Gestaltungsentscheidungen. Eine empirische Entlastung ist nicht nachgewiesen.

Zusätzlich wurden im Familienmodul pro Browser 5.656 Wege mit geordneten Folgen falscher Antworten, später aufgerufenen Hilfen sowie unterschiedlichen Anliegen, Fakten und Grenzen geprüft.

Die beiden Browser prüfen angebotene Antworten und fachlich unterschiedliche Übergänge. Beliebige Mischfolgen aller Hilfetiefen, Kartenaufrufe und Fachfehler mit frei gewählten Wiederholungen sind nicht einzeln nachgespielt. Bei langen Arbeitsansichten gelangen Lernende über Blättertasten zum nächsten Teil. Freiwilliges Scrollen bleibt im Gespräch möglich.
"""
        (target/'Pruefbericht.md').write_text(report)
        screens['Pruefbericht.md']=report;screens['Zaehlungen.json']=dump(counts);screens['Geometriebefunde.json']=dump(geoerrors)
        archive(target/'Sichtpruefung.zip',screens)
        files={p.name:p.read_bytes() for p in HERE.iterdir() if p.suffix in {'.py','.js','.md','.json','.tsv'}}
        files['Gegenpruefung-CLT.json.gz']=(HERE/'Gegenpruefung-CLT.json.gz').read_bytes()
        files['Ausfuehren.md']='Im Repository den dokumentierten Commit auschecken. Die vollständigen Befehle und exakten Paketversionen stehen in Ablauf.yml. Die Tests laufen an den ausgelieferten HTML- und ZIP-Dateien.'
        files['Ablauf.yml']=(ROOT/'.github/workflows/clt.yml').read_bytes()
        archive(target/'Reproduzierbare-Tests.zip',files)
        for p in (package,OUT/(stem+'.html')):shutil.copyfile(p,target/p.name)
        (target/'SHA256SUMS').write_text(''.join(sha(p.read_bytes())+'  '+p.name+'\n' for p in sorted(target.iterdir()) if p.name!='SHA256SUMS'))
        print(stem,len(rows),ngeo,len(geoerrors),paths)
if __name__=='__main__':release()
