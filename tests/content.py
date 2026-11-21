"""Compare the delivered learner materials with the approved Git revision."""
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from playwright.sync_api import sync_playwright
from pypdf import PdfReader

from acceptance import LOCAL, MATRIX, OUT, QA, ROOT, save

APPROVED = '859a01d27989ed93d57759346aa2c6420d51b273'
STRATEGIES = ('K', 'P', 'Cu', 'H', 'K+P', 'K+Cu', 'K+H')
# Compare the approved tasks, decisions and feedback independently of the new help UI.
# The history keeps the order of all sent messages, replies and shared articles.
TRACE = """args => {
  const work = document.getElementById('work');
  const steps = [];
  const capture = () => {
    const copy = work.cloneNode(true);
    if (current && stage().id==='L0') copy.querySelectorAll('.extra-method,.combine').forEach(e => e.remove());
    copy.querySelectorAll('.tools,.hint,.pick,.task-reminder summary').forEach(e => e.remove());
    for (const button of copy.querySelectorAll('button.text-button')) {
      if (/^Karte „.+“ lesen$|^Chatstelle lesen$|^Artikel nachlesen$/.test(button.textContent)) button.remove();
    }
    copy.querySelector('.decision-guide')?.remove();
    const oldGuides = ['Stimmt in der Klasse über euren ersten Rat ab.',
      'Bleibt ihr bei eurem Vorschlag oder ändert ihr ihn? Sagt euch kurz, warum.',
      'Bleibt ihr dabei oder zieht ihr den Vorschlag zurück? Sagt euch kurz, warum.'];
    copy.querySelectorAll('p').forEach(e => { if (oldGuides.includes(e.textContent)) e.remove(); });
    const title = copy.querySelector('#task-title');
    if (title && ['Dein Vorschlag','Prüfe deine Nachricht','Mein erster Rat','Zuerst auf dem Laufzettel','Wähle eine Methode'].includes(title.textContent)) title.remove();
    steps.push([copy.textContent, document.getElementById('send')?.textContent]);
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


def pdf_text(path):
    return [' '.join(page.extract_text().split()) for page in PdfReader(path).pages]


def compare(reference):
    inputs = ('app', 'assets', 'data', 'index.html', 'material', 'scorm', 'scripts/build.py', 'scripts/worksheets.py')
    archive = subprocess.check_output(['git', 'archive', '--format=zip', APPROVED, *inputs], cwd=ROOT)
    with ZipFile(io.BytesIO(archive)) as files:
        files.extractall(reference)
    # Apply the approved age and L0 changes to the independently archived materials.
    dialog_file = reference / 'data/dialogdaten.js'
    dialog = dialog_file.read_text()
    for before, after, count in [('Hi, ich bin Laura. Ich bin 16.', 'Hi, ich bin Laura. Ich bin 19.', 1),
                                 ('Hi, ich bin Laura, 16.', 'Hi, ich bin Laura, 19.', 3)]:
        assert dialog.count(before) == count
        dialog = dialog.replace(before, after)
    data = json.loads(dialog.split('=', 1)[1].strip()[:-1])
    first = data['cases']['Laura'][0]
    assert first['id'] == 'L0'
    for section in ('options','hints','replies'):
        for combination in ('K+P','K+Cu','K+H'):
            del first[section][combination]
    first['task'] = dict.fromkeys(first['task'], 'Wähle die Methode, die du bei „Mein erster Rat“ notiert hast.')
    dialog_file.write_text('const FALLAKTE = '+json.dumps(data, ensure_ascii=False, indent=2)+';\n')
    for script in ('scripts/build.py', 'scripts/worksheets.py'):
        subprocess.run([sys.executable, script], cwd=reference, check=True)
    sources = ('data/dialogdaten.js', 'material/laufzettel/aufgaben.json', 'material/laufzettel/vorlage.html')
    for name in sources:
        assert (ROOT / name).read_bytes() == (reference / name).read_bytes(), name

    reference_dist = reference / 'dist'
    pdfs = {}
    for slug in ('Foerder', 'ESA', 'MSA', 'AHR'):
        name = Path('Laufzettel') / f'Laufzettel-{slug}.pdf'
        actual = pdf_text(OUT / name)
        assert len(actual) == 2 and actual == pdf_text(reference_dist / name), name
        pdfs[slug] = [hashlib.sha256(text.encode()).hexdigest() for text in actual]

    paths = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        approved = browser.new_page()
        candidate = browser.new_page()
        reference_url = (reference_dist / 'Fallakte.html').as_uri()
        approved.goto(reference_url)
        candidate.goto(LOCAL.as_uri())
        data = approved.evaluate('FALLAKTE')
        assert candidate.evaluate('FALLAKTE') == data, 'Falldaten in der gebauten HTML-Datei'
        for tier in data['meta']['levels']:
            for person in data['cases']:
                for strategy in STRATEGIES:
                    for page in (approved, candidate):
                        page.reload()
                    case = dict(person=person, tier=tier, strategy=strategy, data=data)
                    expected = approved.evaluate(TRACE, case)
                    actual = candidate.evaluate(TRACE, case)
                    for part in ('steps', 'history'):
                        assert actual[part] == expected[part], (person, tier, strategy, part)
                    paths += 1
        browser.close()
    return dict(reference_commit=APPROVED, approved_change='Laura · Alter 19 · L0 vier Einzelmethoden und Rückgriff auf den notierten Rat', source_files=sources, built_data_equal=True,
                rendered_paths=paths, pdf_page_text_sha256=pdfs)


if __name__ == '__main__':
    (QA / 'inhaltsvergleich.json').unlink(missing_ok=True)
    with TemporaryDirectory() as directory:
        result = compare(Path(directory))
    save('inhaltsvergleich', result)
    print(f"{result['rendered_paths']} Dialogwege und acht gedruckte Seiten stimmen mit {APPROVED[:7]} überein.")
