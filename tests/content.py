"""Compare the built casework and every conversation with the pre-cleanup release."""
import io
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from playwright.sync_api import sync_playwright

from acceptance import LOCAL, MATRIX, QA, ROOT, save

APPROVED = 'fc9b01c8c13b7bd4632c5b34e054a428ebc931d7'
STRATEGIES = ('K', 'P', 'Cu', 'H', 'K+P', 'K+Cu', 'K+H')
TRACE = """args => {
  const work = document.getElementById('work');
  const steps = [];
  const capture = () => {
    // The heading and navigation on the final screen changed. Its decision still matters.
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
    return {steps, history: Array.from(document.querySelector('#history').children, e => e.textContent)};
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
    for name in ('data/lernhilfen.js', 'app/lernhilfen.js', 'app/ui.js'):
        assert (ROOT / name).read_bytes() == (reference / name).read_bytes(), name

    paths = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        approved = browser.new_page()
        candidate = browser.new_page()
        approved.goto((reference/'dist/Fallakte.html').as_uri())
        candidate.goto(LOCAL.as_uri())
        data = approved.evaluate('FALLAKTE')
        del data['meta']['stopTask']
        for stage in data['cases']['Laura']:
            del stage['pauseFact']
        assert candidate.evaluate('FALLAKTE') == data
        for tier in data['meta']['levels']:
            for person in data['cases']:
                for strategy in STRATEGIES:
                    for page in (approved, candidate):
                        page.reload()
                    case = dict(person=person, tier=tier, strategy=strategy, data=data, testScaffold=True)
                    expected = approved.evaluate(TRACE, dict(case, reference=True))
                    actual = candidate.evaluate(TRACE, case)
                    for part in ('steps','history'):
                        assert actual[part] == expected[part], (person,tier,strategy,part)
                    paths += 1
        browser.close()
    return dict(reference_commit=APPROVED, removed_fields=['meta.stopTask','cases.Laura[*].pauseFact'],
                built_data_equal=True, shared_help_equal=True, rendered_paths=paths)


if __name__ == '__main__':
    (QA/'inhaltsvergleich.json').unlink(missing_ok=True)
    with TemporaryDirectory() as directory:
        result = compare(Path(directory))
    save('inhaltsvergleich', result)
    print(f"{result['rendered_paths']} Dialogwege samt Hilfen und Rückmeldungen gegen {APPROVED[:7]} geprüft.")
