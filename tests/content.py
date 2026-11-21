"""Compare case content and observed actions against the approved classroom build."""
import io
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from playwright.sync_api import sync_playwright

from paths import complete_laura
from acceptance import LOCAL, MATRIX, QA, ROOT, save

APPROVED = 'fa3009c87076dd93e1d241c6142c83b416769990'
STRATEGIES = ('K', 'P', 'Cu', 'H', 'K+P', 'K+Cu', 'K+H')
TRACE = """args => {
  const work = document.getElementById('work');
  const steps = [];
  const capture = () => {
    if (document.getElementById('room').hidden) return;
    // Compare the clinical outcome independently of the final navigation controls.
    const text = current?.mode==='finished'
      ? Array.from(work.querySelectorAll('.unresolved,.response,.paper-note'), e=>e.textContent)
      : work.textContent;
    steps.push([text, document.getElementById('support-panel').textContent,
                document.getElementById('send')?.textContent]);
  };
  document.addEventListener('click', capture, true);
  document.addEventListener('change', capture, true);
  try {
    (MATRIX)(args);
    capture();
    // At L1/L3 a retained recommendation and its confirmation may now share a bubble.
    let shortReview=false;
    const history=[];
    for (const entry of document.querySelector('#history').children) {
      if (entry.matches('.chat-step')) shortReview=args.person==='Laura' && ['Foerder','ESA'].includes(args.tier) &&
        args.data.cases.Laura.some(s=>['L1','L3'].includes(s.id) && s.title===entry.textContent);
      if (shortReview && entry.matches('.team')) {
        const content=entry.querySelector('p').textContent;
        if (content==='Wir bleiben bei unserem Vorschlag.') continue;
        history.push(entry.querySelector('strong').textContent+content.replace(/^Wir bleiben bei unserem Vorschlag[.] /,''));
      } else history.push(entry.textContent);
    }
    return {steps, history};
  } finally {
    document.removeEventListener('click', capture, true);
    document.removeEventListener('change', capture, true);
  }
}""".replace('MATRIX', MATRIX)


def compare(reference):
    inputs = ('app', 'assets', 'data', 'index.html', 'scorm', 'scripts/build.py')
    archive = subprocess.check_output(['git', 'archive', '--format=zip', APPROVED, *inputs], cwd=ROOT)
    with ZipFile(io.BytesIO(archive)) as files:
        files.extractall(reference)
    subprocess.run([sys.executable, 'scripts/build.py'], cwd=reference, check=True)
    for name in ('app/lernhilfen.js', 'app/ui.js'):
        assert (ROOT / name).read_bytes() == (reference / name).read_bytes(), name

    paths = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        approved = browser.new_page()
        candidate = browser.new_page()
        approved.goto((reference/'dist/Fallakte.html').as_uri())
        candidate.goto(LOCAL.as_uri())
        original = approved.evaluate('FALLAKTE')
        data = candidate.evaluate('FALLAKTE')
        # Compare every field except the approved level-specific L1/L3 reviews and L6 prompts.
        comparable = candidate.evaluate('FALLAKTE')
        for index in (1,3):
            assert comparable['cases']['Laura'][index].pop('reviewLevels')==['Foerder','ESA']
        src, dst = (value['cases']['Laura'][6] for value in (original,comparable))
        for level in ('Foerder','ESA'):
            dst['task'][level] = src['task'][level]
        dst['helpBefore']['ESA'][0] = src['helpBefore']['ESA'][0]
        dst['hintQuestions']['ESA'] = src['hintQuestions']['ESA']
        assert comparable == original
        help_before = approved.evaluate('LERNHILFEN')
        help_after = candidate.evaluate('LERNHILFEN')
        assert set(help_after['L3'].pop('kartenfrage'))=={'P','Cu','H'}
        example=help_after['L6']['beispiel']
        for level in ('MSA','AHR'):
            assert example[level]==help_before['L6']['beispiel']
        for level in ('Foerder','ESA'):
            assert 'Kondom' in example[level]
            help_after['L6'][level]=help_before['L6'][level]
        help_after['L6']['beispiel']=help_before['L6']['beispiel']
        assert help_before==help_after

        for tier in original['meta']['levels']:
            for person in original['cases']:
                for strategy in STRATEGIES:
                    for page in (approved, candidate):
                        page.reload()
                        if person!='Laura': complete_laura(page,tier)
                    case = dict(person=person, tier=tier, strategy=strategy, testScaffold=True)
                    expected = approved.evaluate(TRACE, dict(case, data=original, reference=True))
                    actual = candidate.evaluate(TRACE, dict(case, data=data))
                    assert actual['history']==expected['history'], (person,tier,strategy,'history')
                    if person!='Laura' or tier in ('MSA','AHR'):
                        assert actual['steps']==expected['steps'], (person,tier,strategy,'steps')
                    paths += 1
        browser.close()
        counts = []
        for engine in ('chromium','webkit'):
            exe=os.environ.get(engine.upper()+'_EXECUTABLE')
            browser=getattr(p,engine).launch(**({'executable_path':exe} if exe else {}))
            page=browser.new_page(viewport={'width':820,'height':1180},has_touch=True)
            for tier in ('Foerder','ESA','MSA','AHR'):
                for corrected in (False,True):
                    record=dict(engine=engine,niveau=tier,korrektur_in_l0=corrected)
                    for version,url in [('vorher',reference/'dist/Fallakte.html'),('jetzt',LOCAL)]:
                        page.goto(url.as_uri())
                        record[version]=complete_laura(page,tier,corrected)
                    old=record['vorher']['total']
                    new=record['jetzt']['total']
                    assert old==(18 if corrected else 15)
                    assert new==(old-4 if tier in ('Foerder','ESA') else old)
                    counts.append(record)
            browser.close()
    return dict(reference_commit=APPROVED, built_data_equal=True, shared_help_equal=True,
                rendered_paths=paths, bedienhandlungen=counts)



if __name__ == '__main__':
    (QA/'inhaltsvergleich.json').unlink(missing_ok=True)
    with TemporaryDirectory() as directory:
        result = compare(Path(directory))
    save('inhaltsvergleich', result)
    print(f"{result['rendered_paths']} Dialogwege samt Hilfen und Rückmeldungen gegen {APPROVED[:7]} geprüft.")
