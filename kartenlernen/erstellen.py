"""Eigenständige Auslieferung. Keine Änderungen an den bestehenden Builds."""
import base64
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=ROOT/'dist/Kartenlernen'
REF='562ea2566dd80e31c093f313b925adcb31e22c9a'
START='88ec05360259ab88967315c5dee800064e9ceef0'
sys.path.extend([str(ROOT/'vorbereitung'),str(ROOT/'scripts')])
from build import manifest
from bilder import make_graphics
from aufgaben import THEMEN,HILFEN,NIVEAUS
from zipfile import ZIP_DEFLATED,ZipInfo


def sha(data):return hashlib.sha256(data).hexdigest()
def pack(p,files):
    with ZipFile(p,'w') as z:
        for n,raw in sorted(files.items()):z.writestr(ZipInfo(n),raw,compress_type=ZIP_DEFLATED)
def reference():
    path='vorbereitung/Stationsplanung.zip'
    raw=(ROOT/path).read_bytes()
    assert raw==subprocess.check_output(['git','show',REF+':'+path],cwd=ROOT)
    with ZipFile(ROOT/path) as z:
        c=z.read('Kartenvertrag.json');s=json.loads(z.read('Stationsvertrag.json'))
        assert sha(c)==s['cardContractSHA256']
    return json.loads(c)['levels'],s


def build():
    cards,old=reference()
    material={'levels':{},'topics':list(THEMEN),'graphics':make_graphics()}
    work={'referenz':REF,'ausgangsstand':START,'kartenvertrag_sha256':old['cardContractSHA256'],'niveaus':{}}
    for ti,t in enumerate(NIVEAUS):
        levels=[]
        for n,c in enumerate(cards[t],1):
            fields=[dict(nummer=f['number'],wort=f['answer'],titel=next(sec['title'] for sec in c['sections'] if sec['id']==f['section'])) for f in c['fields']]
            levels.append(dict(titel=c['title'],nummer=n,seite='Vorderseite' if n<3 else 'Rückseite',position='oben' if n%2 else 'unten',
                ueberschrift=f'Kapitel {n} – '+c['title'],felder=fields,texte=[dict(titel=s['title'],lueckentext=s['template'],volltext=s['completedText']) for s in c['sections']],
                pearl=c['pearlIndex'],pearl_erklaerung=c['pearlExplanation']))
        work['niveaus'][t]=levels
        qs={}
        for i,(topic,versions) in enumerate(THEMEN.items()):
            info,prompt,answer,other,retry,feedback=versions[ti]
            correct=(i+ti+i//3)%2
            qs[topic]=dict(info=info,frage=prompt,antworten=[other,answer] if correct else [answer,other],richtig=correct,fehler=retry,rueckmeldung=feedback,
                hilfen=[*HILFEN[topic][ti],retry,'Passend ist: „'+answer+'“'])
        material['levels'][t]={'cards':levels,'fragen':qs}
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    styles=(HERE/'stil.css').read_text().replace('FONT_URL','data:font/ttf;base64,'+base64.b64encode((ROOT/'assets/dmsans.ttf').read_bytes()).decode())
    values=dict(STIL=styles,ANWENDUNG=(HERE/'app.js').read_text(),SITZUNG=(ROOT/'tagesauswahl/sitzung.js').read_text(),
        LERNSTOFF=json.dumps(material,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'),COMMIT=head,LIZENZ=(ROOT/'assets/dmsans-OFL.txt').read_text())
    raw=re.sub('|'.join(values),lambda m:values[m[0]],(HERE/'index.html').read_text()).encode()
    OUT.mkdir(exist_ok=True,parents=True);(OUT/'Vorbereitung.html').write_bytes(raw)
    files={x.name:x.read_bytes() for x in (ROOT/'scorm').glob('*.xsd')}
    pack(OUT/'Vorbereitung-SCORM12.zip',dict(files,**{'index.html':raw,'imsmanifest.xml':manifest('VORBEREITUNG-VIER-KAPITEL').replace(b'>Fallakte.<',b'>Fallakte - Vier Methoden<')}))
    guide='''# Kartenvertrag für Work

Ein A4-Blatt, Hochformat, Duplexdruck an der langen Kante. Auf beiden Seiten liegt die Schnittlinie genau in der Mitte. Vorderseite oben Kapitel 1, unten Kapitel 2. Rückseite oben Kapitel 3, unten Kapitel 4. Nach einem Schnitt bilden 1 und 3 sowie 2 und 4 je eine doppelseitige A5-Karte. Druck bei 100 Prozent prüfen.

Ersetze auf den bisherigen Schüler- und Musterkarten nur die Methodenüberschrift durch die unten genannte Kapitelüberschrift. Belasse das Niveau rechts und alle Fachtexte, Lücken, Feldnummern, Pearl-Werte und deren Erläuterung im Wortlaut der Referenz. Seiten 3 und 4 mit Laufzettel entfallen. Keine zusätzlichen Arbeitsaufträge, Abschnittsmarken oder Codes setzen. Eine deutliche Kapitelzahl und der ausgeschriebene Methodenname müssen auch in Graustufen eindeutig sein. Im Lückentext bedeuten {1} bis {4} die nummerierten Schreibfelder. Die Papieransicht am Gerät zeigt die vier nummerierten Felder in Papier-Reihenfolge. Die fett gedruckten Wörter kommen in die gleich nummerierten Lücken. Bereits richtige Wörter bleiben stehen. Im Zeitnotweg führt der Abschluss einer Karte zurück zur Musterkartenauswahl.

'''
    for t,cs in work['niveaus'].items():
        guide+='## '+('Förder' if t=='Foerder' else t)+'\n\n'
        for c in cs:
            guide+='### '+c['ueberschrift']+' · '+c['seite']+' '+c['position']+'\n\nPearl-Index '+c['pearl']+' · Richtwert nach pro familia '+c['pearl_erklaerung']+' Kein Maß für den Schutz vor sexuell übertragbaren Infektionen (STI).\n\n'
            for s in c['texte']:guide+='**'+s['titel']+'**  \n'+s['lueckentext']+'\n\n'
            guide+=' | '.join('Feld '+str(f['nummer'])+' → '+f['wort'] for f in c['felder'])+'\n\n'
    pack(OUT/'Kartenvertrag-Work.zip',{'Kartenvertrag.json':json.dumps(work,ensure_ascii=False,indent=2),'Kartenvertrag.md':guide})


if __name__=='__main__':build()
