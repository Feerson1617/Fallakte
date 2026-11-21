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

APPROVED = '940138ed9d95e4d5ee79ffa34cc70ba22a4ff7ae'
STRATEGIES = ('K', 'P', 'Cu', 'H', 'K+P', 'K+Cu', 'K+H')

# Compare the output a team actually sees when responding, while opening all optional hints. The help text is audited separately.
TRACE = """args => {
  const steps = [];
  const capture = () => {
    if (!document.getElementById('room').hidden)
      steps.push(['work','send'].map(id=>document.getElementById(id)?.textContent));
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


def leaves(value, path=''):
    if isinstance(value, (dict,list)):
        items=value.items() if isinstance(value,dict) else enumerate(value)
        for key,child in items:
            yield from leaves(child,(path+'.' if path else '')+str(key))
    else:
        yield path,value


def changes(before,after):
    old,new=dict(leaves(before)),dict(leaves(after))
    return [dict(stelle=key,vorher=old.get(key),jetzt=new.get(key))
            for key in sorted(old.keys()|new.keys()) if old.get(key)!=new.get(key)]


def case_changes(original,data):
    for key in original.keys()|data.keys():
        if key!='cases':
            assert original[key]==data[key],key
    assert original['cases'].keys()==data['cases'].keys()
    edits=[]
    for person,stages in original['cases'].items():
        new_stages=data['cases'][person]
        assert [s['id'] for s in stages]==[s['id'] for s in new_stages]
        for old,new in zip(stages,new_stages):
            for row in changes(old,new):
                path=row['stelle']
                is_task=(old['id'] in ('L1','L3','L4','L6') and path in ('task.Foerder','task.ESA'))
                allowed={
                    'L3':{'hints.K.find','hints.K.fact'},'L4':{'hints.K.find','hints.K.fact'},
                    'C0':{'hints.Cu.1','hints.K+Cu.1'},'C2':{'hints.K.0','hints.K.1'}
                }
                assert is_task or path in allowed.get(old['id'],()), (old['id'],path)
                edits.append(dict(abschnitt=old['id'],**row))
    return edits


def compare(reference):
    build_reference(reference,APPROVED)
    for name in ('app/lernhilfen.js','app/ui.js','app/wiederaufnahme.js'):
        assert (ROOT/name).read_bytes()==(reference/name).read_bytes(), name

    paths = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        approved, candidate = browser.new_page(), browser.new_page()
        old_html=reference/'dist/Fallakte.html'
        approved.goto(old_html.as_uri())
        candidate.goto(LOCAL.as_uri())
        original, data = (page.evaluate('FALLAKTE') for page in (approved,candidate))
        edits=case_changes(original,data)
        help_before,help_now=(page.evaluate('LERNHILFEN') for page in (approved,candidate))
        assert help_before.keys()==help_now.keys()
        for stage,old in help_before.items():
            new=help_now[stage]
            if stage in ('T1','T2'):
                assert old==new
            else:
                assert old['beispielMethode']==new['beispielMethode']
                assert old['MSA']==new['MSA'] and old['AHR']==new['AHR']
            edits.extend(dict(abschnitt=stage,stelle='Hilfe.'+r['stelle'],vorher=r['vorher'],jetzt=r['jetzt'])
                         for r in changes(old,new))
        task_edits=[row for row in edits if row['stelle'].startswith('task.')]
        levels=data['meta']['levels']
        check_case_facts(data['cases']['Laura'],levels)

        old_trace=TRACE.replace('MATRIX',(reference/'tests/dialogs.js').read_text())
        new_trace=TRACE.replace('MATRIX',MATRIX)
        for tier in levels:
            for person in original['cases']:
                for strategy in STRATEGIES:
                    for page in (approved,candidate):
                        page.reload()
                        if person!='Laura':
                            complete_laura(page,tier)
                    args=dict(person=person,tier=tier,strategy=strategy,testScaffold=True)
                    expected=approved.evaluate(old_trace,dict(args,data=original))
                    actual=candidate.evaluate(new_trace,dict(args,data=data))
                    serialized=json.dumps(expected,ensure_ascii=False)
                    for row in task_edits:
                        serialized=serialized.replace(row['vorher'],row['jetzt'])
                    assert actual==json.loads(serialized), (person,tier,strategy)
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
                    for version,url in [('vorher',old_html),('jetzt',LOCAL)]:
                        page.goto(url.as_uri())
                        row[version]=complete_laura(page,tier,corrected)
                    extra=3 if corrected else 0
                    assert row['vorher']['steps']==row['jetzt']['steps']
                    assert row['vorher']['total']==row['jetzt']['total']==9+extra
                    assert row['vorher']['decisions']==row['jetzt']['decisions']==5+corrected
                    counts.append(row)
            browser.close()
    return dict(reference_commit=APPROVED,textaenderungen=edits,fachdaten_gleich=True,shared_help_equal=True,
                laura_abschnitte=5,fachkern_geprueft=levels,rendered_paths=paths,bedienhandlungen=counts)


if __name__=='__main__':
    (QA/'inhaltsvergleich.json').unlink(missing_ok=True)
    with TemporaryDirectory() as directory:
        result=compare(Path(directory))
    save('inhaltsvergleich',result)
    print(f"{result['rendered_paths']} Dialogwege mit dem Stand {APPROVED[:7]} verglichen.")
