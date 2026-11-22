"""Build the standalone round-one prototype and both views of its Work contract."""
import base64
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist/Runde-1'


def data_url(file,mime):
    return f'data:{mime};base64,'+base64.b64encode(file.read_bytes()).decode('ascii')


def commit():
    return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()


def reference(ref,bank):
    card=bank['cards'][ref['method']]
    return card['title']+' · '+card['sections'][ref['section']]['title']


def readable(bank):
    def lines(items):
        return '\n'.join('- '+str(item) for item in items)
    def details(items):
        return '\n'.join(f'{key}. {item}' for key,item in enumerate(items,1))
    def questions(context):
        return lines(f"{q['id']} · {q['text']} — {q['answer']}" for q in context['questions'])
    text=['# Materialvertrag für Work · Fallakte Laura',f"Inhaltsbank {bank['version']} · Stand `{bank['buildCommit']}`",
          'Planungs- und Redaktionsfassung für den 02.12.2026. Die spielbaren Abschnitte sind in der Übersicht gekennzeichnet.',
          '## Analoger Einstieg',bank['opening'],'Erster Rat und biologischer Grund werden im Einstieg auf dem Laufzettel festgehalten.',
          '## Auswertung der Empfehlung',
          'Bei einem biologischen Fehler (A) erklären die Rückmeldungen die zutreffende Kartenstelle. '
          'Fehlt ein bekanntes Schutzziel (B), kann die lernende Person ihren Rat ergänzen. '
          'Bei einer vertretbaren Strategie (C) bleiben die genannten Bedingungen Teil der Beratung.',
          lines(bank['facts'][r['fact']]+' · Mindestens eine passende Methode: '+', '.join(r['requiresAny']) for r in bank['goalRules']),
          'Die Codeprüfung verwendet `'+bank['normalization']+'`. Sie prüft den gewählten Fachanker. '
          'Die eigenständige Begründung steht auf dem Laufzettel.']
    for stage in bank['stages'].values():
        text+=['## '+stage['id']+' · '+stage['title'],
               '**Stand** '+('im Prototyp bearbeitbar' if stage['playable'] else 'fachlich spezifiziert'),
               '**Neue Fallinformation** '+stage['information'],
               '**Bis hier bekannte Fakten**',lines(bank['facts'][key] for key in stage['knownFacts']),
               '**Biologischer Lerngegenstand** '+stage['learningGoal'],
               '**Fachinformation** '+stage['evidence'],
               '**Wiedereinstieg** '+stage['recovery'],
               '**Fachanker auf dem Laufzettel**', '\n'.join(f'- {key}. {value}' for key,value in stage['anchors'].items()),
               '**Prüfcode für MSA und AHR** '+stage['code'],
               '**Rückmeldung zum jeweiligen Fachanker**',lines(f"{key}. {fb['text']} ({reference(fb['card'],bank)})" for key,fb in stage['anchorFeedback'].items())]
        for tier,task in stage['levels'].items():
            text+=['### '+bank['levels'][tier]+' · '+task['taskId'],'**Nachricht von Laura** '+task['message'],
                   '**Auftrag** '+task['task'], '**Hinweis im Arbeitsbereich** '+task.get('evidence',stage['evidence']),
                   '**Zuerst sichtbare Strategien** '+', '.join(task['primary'])]
            if task['paperPrompt']:text+=['**Weg zum Laufzettel** '+task['paperPrompt']]
            if task['returnPrompt']:text+=['**Zurück ins Gespräch** '+task['returnPrompt']]
            before=task['before']
            text+=['**Vor der Auswahl** '+reference(before['card'],bank),questions(before),details(before['hints'])]
            for key,way in task['strategies'].items():
                text+=['#### '+bank['strategies'][key]['label']+' ('+key+')',
                       '**Einordnung** '+way['status']+' · '+way['condition'],
                       '**Rückmeldung** '+way['feedback'],'**Kartenstelle** '+reference(way['card'],bank)]
                if way['extraCards']:
                    text+=['**Ergänzende Kartenstellen** '+', '.join(reference(ref,bank) for ref in way['extraCards'])]
                if way.get('goalCard'):text+=['**Kartenstelle zum fehlenden Schutzziel** '+reference(way['goalCard'],bank)]
                if way['reply']:text+=['**Laura nach einer freigegebenen Nachricht** '+way['reply']]
                if way['options']:
                    text+=['**Biologische Begründungsoptionen**',lines(
                        f"{o['id']} · {o['text']} — {'fachlich zutreffend' if o['correct'] else 'erneut prüfen'}. {o['feedback']} ({reference(o['card'],bank)})"
                        for o in way['options'])]
                if way['questions']:
                    text+=['**Freiwillige Rückfragen**',questions(way)]
                text+=['**Gestufte Hilfen**',details(way['hints'])]
    text+=['## Infokarten']
    for card in bank['cards'].values():
        text+=['### '+card['title']]
        for section in card['sections'].values():text+=['**'+section['title']+'** '+section['text']]
    shared=bank['consolidation']
    text+=['## Gemeinsame Sicherung',lines(shared['facts']),shared['paperField'],shared['prompt'],shared['compare']]
    return '\n\n'.join(text)+'\n'


def build():
    from reserve_0212 import reserve_html
    OUT.mkdir(parents=True,exist_ok=True)
    bank=json.loads((ROOT/'data/laura-0212.json').read_text())
    bank['buildCommit']=commit()
    contract=json.dumps(bank,ensure_ascii=False,indent=2)+'\n'
    (OUT/'Materialvertrag.json').write_text(contract)
    (OUT/'Materialvertrag.md').write_text(readable(bank))
    document=(ROOT/'docs/0212-umsetzungsstand.md').read_text()
    (OUT/'0212-umsetzungsstand.md').write_text(document.replace(
        'siehe `Materialvertrag.json`, Feld `buildCommit`.', '`'+bank['buildCommit']+'`'))
    page=(ROOT/'02-12.html').read_text()
    def stylesheet(match):
        file=ROOT/match[1]
        css=file.read_text()
        css=re.sub(r'url\("([^"]+\.ttf)"\)',lambda m:'url("'+data_url(file.parent/m[1],'font/ttf')+'")',css)
        return '<style>\n'+css+'\n</style>'
    page=re.sub(r'<link rel="stylesheet" href="([^"]+\.css)">',stylesheet,page)
    page=re.sub(r'src="(assets/[^"]+\.webp)"',lambda m:'src="'+data_url(ROOT/m[1],'image/webp')+'"',page)
    page=page.replace('<script id="materialvertrag" type="application/json"></script>',
        '<script id="materialvertrag" type="application/json">'+contract.replace('<','\\u003c')+'</script>')
    reserve=base64.b64encode(reserve_html().encode()).decode('ascii')
    page=page.replace('id="reserve" type="application/octet-stream"></script>','id="reserve" type="application/octet-stream">'+reserve+'</script>')
    def javascript(m):
        source=(ROOT/m[1]).read_text().replace('</script',r'<\/script')
        return '<script>\n'+source+'\n</script>'
    page=re.sub(r'<script src="(module/0212/[^"]+\.js)"></script>',javascript,page)
    license_text='\n'.join(p.read_text() for p in sorted((ROOT/'assets').glob('*-OFL.txt')))
    page=page.replace('</body>','<script type="text/plain" id="font-licenses">'+license_text+'</script>\n</body>')
    dest=OUT/'Fallakte.html'
    dest.write_text(page)
    assert dest.stat().st_size<10_000_000
    print(dest,sha256(dest.read_bytes()).hexdigest())
    return dest


if __name__=='__main__':build()
