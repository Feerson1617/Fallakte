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
START='542eddf02d913e30289211c5b27cc242004a3d7c'
sys.path.extend([str(ROOT/'vorbereitung'),str(ROOT/'scripts')])
from build import manifest
from bilder import make_graphics
from aufgaben import BILDER,TITEL,INFOHILFE,BILDDETAIL,FRAGEN,NIVEAUS
from antwortmodelle import MODELLE
from kartentexte import karte
from druckkarten import druck
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
    material={'levels':{},'modelle':MODELLE,'graphics':{k:v for k,v in make_graphics().items() if k in sum((list(pair) for pair in BILDER),[])}}
    work={'referenz':REF,'ausgangsstand':START,'kartenvertrag_sha256':old['cardContractSHA256'],'niveaus':{}}
    for ti,t in enumerate(NIVEAUS):
        levels,info=[],[]
        for ch,vorlage in enumerate(cards[t]):
            card,kerne=karte(t,ch,vorlage)
            levels.append(card)
            info.append([dict(titel=TITEL[ch][part],bild=BILDER[ch][part],hilfe=[INFOHILFE[ch][part][0], BILDDETAIL[t][ch][part] if t in BILDDETAIL else INFOHILFE[ch][part][1]],felder=[2*part+1,2*part+2],
                text=kerne[2*part:2*part+2]) for part in range(2)])
        work['niveaus'][t]=levels
        qs=[]
        for ch,original in enumerate(FRAGEN[t]):
            q=dict(original)
            if q['typ']=='wahl':
                options=[q['passend'],*[a['text'] for a in q['alternativen']]]
                q['optionen']=options[::-1] if (ti+ch)%2 else options
            qs.append(q)
        material['levels'][t]={'cards':levels,'info':info,'fragen':qs}
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    styles=(HERE/'stil.css').read_text().replace('FONT_URL','data:font/ttf;base64,'+base64.b64encode((ROOT/'assets/dmsans.ttf').read_bytes()).decode())
    values=dict(STIL=styles,ANWENDUNG='\n'.join((HERE/f).read_text() for f in ['gesundheit.js','diagnose.js','hilfe.js','app.js']),SITZUNG=(ROOT/'tagesauswahl/sitzung.js').read_text(),
        LERNSTOFF=json.dumps(material,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'),COMMIT=head,LIZENZ=(ROOT/'assets/dmsans-OFL.txt').read_text())
    raw=re.sub('|'.join(values),lambda m:values[m[0]],(HERE/'index.html').read_text()).encode()
    OUT.mkdir(exist_ok=True,parents=True);(OUT/'Vorbereitung.html').write_bytes(raw)
    files={x.name:x.read_bytes() for x in (ROOT/'scorm').glob('*.xsd')}
    pack(OUT/'Vorbereitung-SCORM12.zip',dict(files,**{'index.html':raw,'imsmanifest.xml':manifest('VORBEREITUNG-VIER-KAPITEL').replace(b'>Fallakte.<',b'>Fallakte - Vier Methoden<')}))
    drucke={}
    guide = "# Kartenvertrag für Work\n\nKartenvertrag.json ist die verbindliche Textquelle. Schülerblatt und Muster entstehen aus denselben Feldern. A4, Hochformat, beidseitig an der langen Kante, 100 %. Erst nach dem Zeichen der Lehrkraft in der Mitte schneiden. Die Feldnummer bleibt auf dem Papier stehen.\n"
    diff = ["# Änderungen gegenüber dem gelieferten Infokartenpaket", "", "Je Abschnitt stehen bisheriger und neuer Wortlaut sowie das neue Schreibfeld nebeneinander.", ""]
    work['druckvorlage']='Infokarten_27-11-2026_542eddf.zip'
    work['fragenverweise']={}
    for tier,cs in work['niveaus'].items():
        work['fragenverweise'][tier]=[]
        for index,(card,oldcard,q) in enumerate(zip(cs,cards[tier],FRAGEN[tier])):
            heading=card['texte'][q['abschnitt']]['titel']
            work['fragenverweise'][tier].append(dict(kapitel=index+1,frage=q['frage'],ueberschrift=heading))
            name=tier+' · '+card['ueberschrift']
            guide+='\n## '+name+'\n\n'+card['seite']+' '+card['position']+'\n\n'
            diff+=['## '+name,'']
            for j,(neu,alt) in enumerate(zip(card['texte'],oldcard['sections'])):
                guide+=neu['titel']+'  \n'+neu['lueckentext']+'\n\n'
                diff += [f"- {alt['title']} → **{neu['titel']}**", '  - Bisher · '+alt['completedText'], '  - Jetzt · '+neu['volltext']]
            for neu,alt in zip(card['felder'],oldcard['fields']):
                guide+=f"Feld {neu['nummer']} · {neu['wort']}  \n"
                diff.append(f"- Feld {neu['nummer']} · {alt['answer']} → {neu['wort']}")
            guide+='\nPearl-Index '+card['pearl']+' · '+card['pearl_erklaerung']+'\n\nFrage · '+q['frage']+'  \nKartenstelle · '+heading+'\n'
        for muster in (False,True):
            typ='Musterkarten' if muster else 'Schuelerkarten'
            drucke[f'{typ}/{tier}.pdf']=druck(cs,tier,muster,ROOT/'assets/dmsans.ttf')
    work['eingangsabgleich_sha256']=sha((HERE/'pruefdaten/Druckabgleich-542eddf.xlsx').read_bytes())
    work['kartenvertrag_sha256']=sha(json.dumps(work['niveaus'],sort_keys=True,ensure_ascii=False).encode())
    pack(OUT/'Kartenvertrag-Work.zip',{'Kartenvertrag.json':json.dumps(work,ensure_ascii=False,indent=2),'Kartenvertrag.md':guide,'Textaenderungen.md':'\n'.join(diff),**drucke})

if __name__=='__main__':build()
