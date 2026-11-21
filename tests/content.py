"""Compare delivered versions, shared case facts, optional cases and measured Laura paths."""
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from playwright.sync_api import sync_playwright

from paths import complete_laura
from acceptance import LOCAL, MATRIX, QA, ROOT, save

APPROVED = 'e455e4dfd3aedf45954afb0cfb015578b70abde4'
MEASUREMENT_BASE = '0891d8c8aa8089d8c92850d70984a7d013e8814d'
STRATEGIES = ('K', 'P', 'Cu', 'H', 'K+P', 'K+Cu', 'K+H')

# Compare the output a team actually sees when responding, including all optional hints.
TRACE = """args => {
  const steps = [];
  const capture = () => {
    if (!document.getElementById('room').hidden)
      steps.push(['work','support-panel','send'].map(id=>document.getElementById(id)?.textContent));
  };
  document.addEventListener('click', capture, true);
  document.addEventListener('change', capture, true);
  try {
    (MATRIX)(args);
    capture();
    return {steps, history:document.getElementById('history').textContent,
            outcome:[...document.querySelectorAll('#work .unresolved,#work .response')].map(e=>e.textContent)};
  } finally {
    document.removeEventListener('click', capture, true);
    document.removeEventListener('change', capture, true);
  }
}"""


def check_case_facts(stages, levels):
    assert [s['id'] for s in stages]==['L0','L1','L3','L4','L6']
    expected = [
        (r'19',r'Krankheiten|Infektionen'),
        (r'schwanger',r'vergess|denke ich nicht immer',r'jeden Tag|täglich|regelmäßige Dinge'),
        (r'Freundin',r'übel',r'weiß ich nicht',r'Pille nicht nehmen',r'andere Hormone bin ich offen',
         r'Einsetzen einer Spirale macht mir Sorgen',r'beraten lassen'),
        (r'oft starke Schmerzen',r'nicht untersucht',r'Mehr Schmerzen möchte ich nicht',
         r'Infektionen ist mir weiterhin wichtig',r'Kondom wäre für uns in Ordnung'),
        (r'selbst',r'Beratung|Praxis',r'Nachteil|Vergleicht|Alternative')
    ]
    for s, facts in zip(stages,expected):
        for tier in levels:
            lines=s['message'] if isinstance(s['message'],list) else s['message'][tier]
            assert all(len(line.split())<=24 for line in lines)
            text=' '.join(lines)
            assert all(re.search(fact,text,re.I) for fact in facts), (s['id'],tier,text)
            assert not re.search(r'Blutung',text), text
    assert set(stages[0]['options'])=={'K','P','Cu','H'}
    assert all(set(s['options'])==set(STRATEGIES) for s in stages[1:])
    assert all(s.get('reviewPrevious') for s in stages[1:4])
    assert all('P' in s['declined'] for s in stages[2:])
    assert 'nicht sicher' in stages[2]['hints']['K+P']['fact']
    assert 'verstärken' in stages[3]['replies']['K+Cu']
    assert 'Beratung und mit meiner Zustimmung' in stages[4]['replies']['K+H']
    assert 'jedes Mal' in stages[4]['replies']['K']
    for tier, checks in [('MSA',[(2,'Einzelfall'),(2,'Sorge'),(3,'zwei Strategien'),(3,'Praxis'),(4,'Gewichte')]),
                         ('AHR',[(2,'Vorhersage'),(2,'Bedingung'),(3,'medizinischen Bedingung'),(4,'Alternative')])]:
        for i,word in checks:
            assert word in stages[i]['task'][tier], (tier,i,word)


def build_reference(reference,commit):
    inputs = ('app','assets','data','index.html','scorm','scripts/build.py','tests/dialogs.js')
    archive = subprocess.check_output(['git','archive','--format=zip',commit,*inputs],cwd=ROOT)
    with ZipFile(io.BytesIO(archive)) as files:
        files.extractall(reference)
    subprocess.run([sys.executable,'scripts/build.py'],cwd=reference,check=True)


# These classroom prompts no longer require a second learner. The clinical text is frozen.
COPY_EDITS = {
    'Wähle deinen Rat für Laura. Sag deinem Partner: Warum passt er? Nenne auch einen Nachteil.':
        'Wähle deinen Rat für Laura. Begründe ihn kurz. Nenne auch einen Nachteil.',
    'Wir haben den Artikel gelesen und unsere Vermutung besprochen.':
        'Wir haben den Artikel gelesen und eine Vermutung formuliert.',
    'Besprecht euren Grund. ': 'Überlege dir einen Grund. ',
    'Besprecht kurz euren Grund. Behaltet den Vorschlag bei oder ändert ihn.':
        'Prüfe deinen Grund. Behalte den Vorschlag bei oder ändere ihn.',
    'Besprecht euren neuen Rat. Behaltet ihn bei oder zieht ihn zurück.':
        'Prüfe deinen neuen Rat. Behalte ihn bei oder ziehe ihn zurück.'
}


def independent_work(value):
    serialized=json.dumps(value,ensure_ascii=False)
    for old,new in COPY_EDITS.items():
        serialized=serialized.replace(old,new)
    return json.loads(serialized)


def compare(reference):
    historical=reference/'measurement'
    build_reference(reference,APPROVED)
    build_reference(historical,MEASUREMENT_BASE)
    for name in ('app/lernhilfen.js','app/ui.js'):
        assert (ROOT/name).read_bytes()==(reference/name).read_bytes(), name

    paths = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        approved, candidate = browser.new_page(), browser.new_page()
        old_html=reference/'dist/Fallakte.html'
        approved.goto(old_html.as_uri())
        candidate.goto(LOCAL.as_uri())
        original, data = (page.evaluate('FALLAKTE') for page in (approved,candidate))
        comparable=candidate.evaluate('FALLAKTE')
        for stages in comparable['cases'].values():
            for stage in stages:
                stage.pop('recap',None)
                stage.pop('resumeTitle',None)
        assert comparable==independent_work(original)
        assert approved.evaluate('LERNHILFEN')==candidate.evaluate('LERNHILFEN')
        levels=data['meta']['levels']
        check_case_facts(data['cases']['Laura'],levels)

        old_trace=TRACE.replace('MATRIX',(reference/'tests/dialogs.js').read_text())
        new_trace=TRACE.replace('MATRIX',MATRIX)
        for tier in levels:
            for person in original['cases']:
                for strategy in STRATEGIES:
                    for page,label in ((approved,'Schritt'),(candidate,'Laura')):
                        page.reload()
                        if person!='Laura':
                            complete_laura(page,tier,step_label=label)
                    args=dict(person=person,tier=tier,strategy=strategy,testScaffold=True)
                    expected=approved.evaluate(old_trace,dict(args,data=original))
                    actual=candidate.evaluate(new_trace,dict(args,data=data))
                    assert actual==independent_work(expected), (person,tier,strategy)
                    paths+=1
        browser.close()
        counts=[]
        for engine in ('chromium','webkit'):
            exe=os.environ.get(engine.upper()+'_EXECUTABLE')
            browser=getattr(p,engine).launch(**({'executable_path':exe} if exe else {}))
            page=browser.new_page(viewport={'width':820,'height':1180},has_touch=True)
            for tier in levels:
                for corrected in (False,True):
                    row=dict(engine=engine,niveau=tier,korrektur_in_l0=corrected)
                    for version,url,n in [('vorher',historical/'dist/Fallakte.html',7),('jetzt',LOCAL,5)]:
                        page.goto(url.as_uri())
                        row[version]=complete_laura(page,tier,corrected,n,'Schritt' if version=='vorher' else 'Laura')
                    extra=3 if corrected else 0
                    assert row['vorher']['total']==(11 if tier in ('Foerder','ESA') else 15)+extra
                    assert row['jetzt']['total']==9+extra
                    assert row['vorher']['decisions']==6+corrected and row['jetzt']['decisions']==5+corrected
                    counts.append(row)
            browser.close()
    return dict(reference_commit=APPROVED,measurement_commit=MEASUREMENT_BASE,additional_cases_equal=True,shared_help_equal=True,
                laura_abschnitte=5,fachkern_geprueft=levels,rendered_paths=paths,bedienhandlungen=counts)


if __name__=='__main__':
    (QA/'inhaltsvergleich.json').unlink(missing_ok=True)
    with TemporaryDirectory() as directory:
        result=compare(Path(directory))
    save('inhaltsvergleich',result)
    print(f"{result['rendered_paths']} Dialogwege mit dem Stand {APPROVED[:7]} verglichen.")
