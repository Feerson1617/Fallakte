"""Compose the new day with the exact, independently reproducible December 2 release."""
import base64
import hashlib
import json
import re
import subprocess
from pathlib import Path
from shutil import copy2
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from familienrat_medien import compile_media, media_markdown

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT/'module/familienrat'
OUT = ROOT/'dist/Familienrat'
REF = ROOT/'build/Referenz-8b50305'
BASE = '8b50305b6d98a19e1771a842ea9917c67282ecb9'
OLD = '5d27cc3d61db386468d3f851347690b33b5d86fe'
DAY02 = '6f969460d00005fefd27fed985b6c95b7f1203bee0a9e4d72fcaaf9aea605cb2'
SHELL = '6a7be7f9a7aa9510c096fddec167ad1152d1f4e1fab6fe563ce462ac5d3bd430'
PRACTICE = '911ec450aad893068bbc8af040f09ff7704faa270253f1b7ff84d421ae76ed6f'
from arbeitsplatz import einbetten

def sha(data):
    return hashlib.sha256(data).hexdigest()
def git(*args, cwd=ROOT):
    return subprocess.check_output(['git',*args],cwd=cwd)
def url(mime,data):
    return 'data:'+mime+';base64,'+base64.b64encode(data).decode()
def payload(html,day):
    match=re.search(rb'<script id="modul-'+day+rb'" type="application/octet-stream">([A-Za-z0-9+/=]+)</script>',html)
    return match[1]
FIELD_NAMES = {
    'cases':'Familienperspektiven', 'tasks':'Aufgaben in Unterrichtsreihenfolge','original':'Originalnachricht',
    'missing':'Fehlender Bestandteil','portrait':'Porträtdatei','card':'Fachkartenstelle',
    'prompt':'Bildschirmfrage','answers':'Aussagen und Rückmeldungen','text':'Wortlaut','feedback':'Rückmeldung',
    'ok':'Fachlich passend zur Frage','hints':'Grundfassung der fünf Hilfen','helpByLevel':'Hilfen nach Niveau (Stufe 1 bis 5)',
    'shortOptions':'Zuerst sichtbare Förderoptionen (Index ab 0)','transfer':'Weitere Anwendung nach Lösungshilfe',
    'addition':'Ergänzung für Laura','connection':'Fachlicher Bezug und Grenze','titles':'Sichtbare Abschnittstitel',
    'advancedPrompt':'Anwendungsfrage MSA und AHR','advancedText':'Aussage MSA und AHR','advancedFeedback':'Rückmeldung MSA und AHR',
    'crossReference':'Herkunft des belegenden Fakts bei eigener Verbindung','evidenceSentences':'Passende Originalsatznummern (ab 0)',
    'matrix':'Argumentationsmatrix','field':'Feld auf dem Bogen','first':'Persönliche Erstspur','paper':'Geprüftes Papierergebnis',
    'return':'Rückweg zum Chat','recovery':'Direkteinstiege','sectionId':'Kennung der Teilfrage','section':'Abschnitt',
    'ui':'Bedienbeschriftungen und Aufträge','levelPrompts':'Arbeitsaufträge nach Niveau',
    'limits':'Prüfung der Aussagegrenze','review':'Rückmeldungen beim Vergleich','stems':'Satzbausteine',
    'evaluation':'Persönlicher Bewertungsauftrag','expectation':'Erwarteter persönlicher Beleg',
    'media':'Verbindliche Medienführung','fields':'Papierfelder','steps':'Übergabepunkte','orders':'Aufträge nach Niveau',
    'action':'Schülerhandlung','screen':'Sichtbarer Papierauftrag','condition':'Zeitpunkt','kind':'Ergebnisart',
    'returnText':'Wortgleicher Rückkehrhinweis','nextId':'Nächster digitaler Schritt','restart':'Wiedereinstieg nach dem Papierauftrag',
    'screens':'Bildverzeichnis der Work-Übergabe','sourceMapping':'Quellennummern zu Fachkarten und Kompetenzen'
}
def markdown(data, depth=2):
    """Render every contract value; preserve the reading order of task and feedback."""
    if isinstance(data, dict):
        lines=[]
        for key,value in data.items():
            key=FIELD_NAMES.get(key,key)
            if isinstance(value,(list,dict)):
                lines.extend(['','#'*min(depth,6)+' '+key,'',markdown(value,depth+1)])
            else:
                lines.append('- **'+key+'** · '+('Ja' if value is True else 'Nein' if value is False else str(value)))
        return '\n'.join(lines)
    if isinstance(data,list):
        return '\n\n'.join(markdown(item,depth) for item in data)
    return str(data)
def module_document():
    bank=json.loads((SRC/'material.json').read_text())
    bank['commit']=git('rev-parse','HEAD').decode().strip()
    from clt_inhalte import familie
    bank=familie(bank)
    css=(SRC/'style.css').read_text()
    for token,file in [('FONT_SANS','dmsans.ttf'),('FONT_SERIF','dmseriftext.ttf')]:
        css=css.replace(token,url('font/ttf',(ROOT/'assets'/file).read_bytes()))
    imgs={}
    for name,file in bank['designFiles'].items():
        raw=(ROOT/'assets'/file).read_bytes() if name=='Laura' else git('show',OLD+':module/08-12/assets/'+file)
        imgs[name]=url('image/webp',raw)
    content=json.dumps(bank,ensure_ascii=False,indent=2)
    page=(SRC/'index.html').read_text().replace('STYLES',css).replace('MATERIAL',content.replace('<','\\u003c')).replace('PORTRAITS',json.dumps(imgs)).replace('PROGRAM',(SRC/'app.js').read_text())
    licenses='\n'.join(p.read_text() for p in sorted((ROOT/'assets').glob('*-OFL.txt')))
    page=page.replace('</html>','<script type="text/plain" id="font-licenses">'+licenses+'</script></html>')
    return bank,einbetten(page)

def build():
    REF.parent.mkdir(exist_ok=True)
    if not REF.exists():
        subprocess.run(['git','clone','--shared','--no-checkout',str(ROOT),str(REF)],check=True)
        git('checkout','--detach',BASE,cwd=REF)
    assert git('rev-parse','HEAD',cwd=REF).decode().strip()==BASE
    assert not git('status','--porcelain','--untracked-files=no',cwd=REF)
    subprocess.run(['python','scripts/vorabkandidat.py'],cwd=REF,check=True)
    original=REF/'dist/Vorabkandidat'
    shell=(original/'Fallakte.html').read_bytes()
    assert sha(shell)==SHELL and sha(base64.b64decode(payload(shell,b'02')))==DAY02
    bank,page=module_document()
    content=json.dumps(bank,ensure_ascii=False,indent=2)
    app=shell.replace(payload(shell,b'08'),base64.b64encode(page.encode()))
    assert payload(app,b'02')==payload(shell,b'02') and len(app)<10_000_000
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'Fallakte.html').write_bytes(app)
    with ZipFile(original/'Fallakte-SCORM12.zip') as source,ZipFile(OUT/'Fallakte-SCORM12.zip','w',ZIP_DEFLATED) as dest:
        for n in source.namelist():
            info=ZipInfo(n)
            dest.writestr(info,app if n=='index.html' else source.read(n),compress_type=ZIP_DEFLATED)
    copy2(REF/'dist/Uebungsakte/Uebungsakte.html',OUT/'Uebungsakte.html')
    # Use the published SCO's original ZIP metadata as well as its identical payload.
    practice_zip='Uebungsakte-SCORM12.zip'
    with ZipFile(REF/'dist/Uebungsakte'/practice_zip) as source, ZipFile(OUT/practice_zip,'w') as dest:
        for item in source.infolist():
            data=source.read(item)
            item.date_time=(2026,11,23,5,24,50) if item.filename.endswith('.xsd') else (2026,11,23,5,26,10)
            item.external_attr=(0o100644 if item.filename.endswith(".xsd") else 0o600) << 16
            dest.writestr(item,data)
    assert sha((OUT/practice_zip).read_bytes())=='2f47b664d7de5d48b902f810fd7a8c5a950c1a0bd9124eca3d271a99354d2d37'
    assert sha((OUT/'Uebungsakte.html').read_bytes())==PRACTICE
    (OUT/'Work-Materialvertrag.json').write_text(content+'\n')
    matrix=media_markdown(bank['media'],bank['commit'])
    (OUT/'Medienwechsel-und-Papierfeldmatrix.md').write_text(matrix)
    (OUT/'Medienwechsel-und-Papierfeldmatrix.json').write_text(json.dumps(dict(commit=bank['commit'],**bank['media']),ensure_ascii=False,indent=2)+'\n')
    (OUT/'Work-Materialvertrag.md').write_text('# Work · Familiennachrichten am 08.12.2026\n\n'+
        'Für die Produktion gilt Commit `'+bank['commit']+'`. Gestaltungsreferenz: `'+bank['design']+'`. '+
        'Abschnittstitel, Fragen und Feldnamen wörtlich übernehmen. Die Codes im Vertrag sind interne Kennungen. '+
        'Bei jeder Auswahl gehören text und feedback zusammen. ok markiert nur den Lösungsschlüssel für die Lehrkraft. '+
        'Die persönliche Gewichtung wird auf dem eigenen Bogen begründet. Die Auswahl am Gerät prüft Fakt und Aussagegrenze. Eigene Begründungen bleiben offen.\n\n'+
        '## Papierweg und Ausfallweg\n\n'+bank['analog']+' '+bank['paperRecovery']+'\n\n'+
        'Die Felder „Meine erste Antwort“ und „Nach dem Prüfen“ bleiben getrennt. '+
        'Die Medienwechsel- und Papierfeldmatrix ist verbindlich für Feldnamen, Aufträge und Rückkehrziele. '+
        'Bei Lauras Frage bleiben die persönliche erste Antwort und die spätere Ergänzung getrennt lesbar.\n\n'+markdown(bank)+'\n')
    print(OUT)
if __name__=='__main__':build()
