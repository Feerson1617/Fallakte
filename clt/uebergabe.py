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
            for key in ['original','lesefassung','tasks','transfer','addition','connection','missing']:assert person[key]==ref['cases'][n][key]
        for k in ('cards','limits','opening','second'):assert b[k]==ref[k]
        return 'Vier Originalnachrichten, Lesefassungen, Fachkarten, Aufgaben, Rückmeldungen, Anwendungsfragen, Grenzen und Lauras Falltexte wurden feldweise gegen c4814a9 verglichen.'
    old=json.loads(git('data/laura-0212.json'));cards=json.loads((HERE/'Infokarten.json').read_text())
    for k in ('opening','facts','goalRules','strategies'):assert b[k]==old[k],k
    for k,s in b['stages'].items():
        ref=old['stages'][k]
        for field in ('knownFacts','learningGoal','recovery'):assert s[field]==ref[field]
        for t,l in s['levels'].items():
            assert l['message']==ref['levels'][t]['message']
            for m,w in l['strategies'].items():
                original=ref['levels'][t]['strategies'][m]
                for field in ('status','reply','feedback','condition','questions'):assert w[field]==original[field]
                if t in ('ESA','Foerder'):assert w['options']==original['options']
                else:
                    assert [s['text'] for s in w['options']]==list(ref['anchors'].values())
                    assert [s['feedback'] for s in w['options']]==[ref['anchorFeedback'][a]['text'] for a in ref['anchors']]
    for i,m in enumerate(('K','P','Cu','H')):
        for sec in b['cards'][m]['sections'].values():
            for t,cs in cards.items():assert sec['levels'][t]==next(r['volltext'] for r in cs[i]['texte'] if r['titel']==sec['title'])
    return 'Fallinformationen, bekannte Anliegen je Abschnitt, Lernziele, Empfehlungen, Bedingungen, Rückfragen und Reaktionen entsprechen c4814a9. Die früher per Buchstabe geprüften Aussagen stehen auf MSA/AHR als vollständiger Wortlaut zur Auswahl. Alle 80 niveauabhängigen Kartenabschnitte stimmen mit den Work-Texten aus bbdc2e1 überein.'
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
        logs={};screens={};rows={};counts=[];geoerrors=[];ngeo=0;paths=0
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
                for profile in PROFILES:
                    d=base/profile;prefix=f'{e}/{t}/{profile}/'
                    row=json.loads((d/'Pruefung.json').read_text());assert row['html_sha256']==sha(raw);counts.append(row)
                    for k in ('Pruefung.json','Zustaende.json.gz','Geometrie.json'):logs[prefix+k]=(d/k).read_bytes()
                    for v in json.loads(gzip.decompress(logs[prefix+'Zustaende.json.gz'])):rows[(t,dump(v))]=(t,v)
                    for g in json.loads(logs[prefix+'Geometrie.json']):
                        ngeo+=g['checks'];geoerrors.extend((prefix,issue) for issue in g['issues'])
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
            evidence=(QA/'Sitzung'/('Sitzungspruefung-'+e+'.json')).read_bytes()
            assert json.loads(evidence)['html_sha256']==sha((OUT/'Fallakte-08-12.html').read_bytes())
            logs['Tageswechsel/'+e+'.json']=evidence
            img=QA/'Sitzung'/f'{e}-{day}-frueher-Stopp.jpg';screens['Stundenabschluss/'+img.name]=img.read_bytes()
        c=vertrag(day,b);c['revision']=revision
        archive(target/'Materialvertrag-Work.zip',{'Materialvertrag.json':dump(c),'Auftraege.md':md_contract(c)})
        archive(target/'CLT-Abnahmematrix.zip',{'Matrix.csv':matrix(rows.values(),day),'Grundlagen.md':(HERE/'Grundlagen.md').read_bytes(),'Perspektiven.md':(HERE/'planung.md').read_bytes(),'Zeitplanung.json':dump(c['phasen'])})
        archive(target/'Pruefprotokolle.zip',logs)
        failnote=f'Bei {len(geoerrors)} Beobachtungen ließ sich die vollständige Erreichbarkeit einer angebotenen Taste nicht nachweisen. Die betreffenden Beschriftungen, Positionen, Browser und Fenster stehen im Geometrieprotokoll.' if geoerrors else 'Alle in den Geometrieprotokollen erfassten aktiven Steuerungen waren über ihren aktuellen Ansichtsabschnitt erreichbar.'
        report=f"""# Prüfung am {day}.12.2026

Commit `{revision}`. SHA-256 der Offline-Datei `{sha(raw)}`.

{protection}

Die Lehrkraft gibt zwei Karten getrennt aus. Die Arbeit dazwischen läuft digital. Das Menü „Stundenabschluss“ ist auch bei frühem Stopp erreichbar. Wer bereits einen anderen Rat gesendet hat, kann ihn im Gespräch nachlesen. Persönliche Gründe werden im Unterricht besprochen.

{len(counts)} Browser-, Niveau- und Fensterdurchläufe. Die Matrix umfasst {len(rows)} unterschiedliche protokollierte Kombinationen von Niveau, Kontext, Wortlaut und Bedienelementen. {ngeo} Geometrieprüfungen erfassten aktive Steuerelemente. {failnote} Weitere 40 Tast- und Navigationstests mit Chromium und WebKit prüften physische Treffer bis zum äußeren Fenster. Die Bildschirmtastatur wurde durch eine verkleinerte Höhe simuliert.

{(str(paths)+' vollständige Folgen sendbarer Laura-Empfehlungen. Zusätzlich wurden unpassende Einzelvorschläge, Begründungsoptionen, wiederholte Fehler, Karten, Rückfragen, Hilfen und beide Zusatzfälle geprüft. Pro Niveau und Browser wurden alle 108 sendbaren Celina-Folgen und Toms vollständiger Weg gespielt.') if day=='02' else 'Alle vier Personen mit eigenständiger Auswahl, Fehlversuchen, Hilfen und Lösungsoffenlegung. Alle zwölf Kombinationen aus Gewichtung und Anliegen wurden bearbeitet, einschließlich begründeter Unsicherheit und anderer sachlicher Verknüpfungen. Je Niveau und Browser prüften 864 Statusbeobachtungen die Teilmengen falscher Auswahlen bei Hilfetiefe null bis fünf und nachträglich geöffneter Hilfe. Die Quellenwahl allein vergibt keinen Hilfestatus.'}

Das Offline-HTML und index.html im SCO stimmen byteweise überein. Das SCORM-1.2-Manifest wurde gegen das Schema geprüft. Version A enthält ausschließlich den ersten Unterrichtstag. Beide Fassungen enthalten dasselbe erste Modul.

## Grenzen und Geltungsbereich

Prüfprotokolle enthalten die tatsächlich beobachteten Ausgaben. Wiederholungen führen bei einzelnen Aufgaben auf denselben Fehlertext zurück. Die Quelle der Familienantworten, Lösungsoffenlegung, verspätete Hilfe, vorheriger Vorschlag und fachlicher Stand bleiben unterscheidbar. Unendlich viele Freitexte und Unterbrechungsfolgen lassen sich nicht vollständig prüfen. Freie UB-Begründungen haben keine automatische inhaltliche Diagnose. Native Tastatur, produktives itslearning, Hilfsmittel wie Screenreader, fremde Schriftmetriken, tatsächliches Leseverständnis und reale Minuten mit 28 Lernenden sind offen. Die Matrix begründet Gestaltungsentscheidungen. Eine empirische Entlastung ist nicht nachgewiesen.

Die beiden Browser prüfen angebotene Antworten und fachlich unterschiedliche Übergänge. Beliebige Mischfolgen aller Hilfetiefen, Kartenaufrufe und Fachfehler mit frei gewählten Wiederholungen sind nicht einzeln nachgespielt. Bei langen Arbeitsansichten gelangen Lernende über Blättertasten zum nächsten Teil. Freiwilliges Scrollen bleibt im Gespräch möglich.
"""
        (target/'Pruefbericht.md').write_text(report)
        screens['Pruefbericht.md']=report;screens['Zaehlungen.json']=dump(counts);screens['Geometriebefunde.json']=dump(geoerrors)
        archive(target/'Sichtpruefung.zip',screens)
        files={p.name:p.read_bytes() for p in HERE.iterdir() if p.suffix in {'.py','.js','.md','.json'}}
        files['Ausfuehren.md']='Im Repository den dokumentierten Commit auschecken. Die vollständigen Befehle und exakten Paketversionen stehen in Ablauf.yml. Die Tests laufen an den ausgelieferten HTML- und ZIP-Dateien.'
        files['Ablauf.yml']=(ROOT/'.github/workflows/clt.yml').read_bytes()
        archive(target/'Reproduzierbare-Tests.zip',files)
        for p in (package,OUT/(stem+'.html')):shutil.copyfile(p,target/p.name)
        (target/'SHA256SUMS').write_text(''.join(sha(p.read_bytes())+'  '+p.name+'\n' for p in sorted(target.iterdir()) if p.name!='SHA256SUMS'))
        print(stem,len(rows),ngeo,len(geoerrors),paths)
if __name__=='__main__':release()
