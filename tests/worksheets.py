"""Read the delivered PDFs back independently of the HTML print template."""
import hashlib
import json
from pathlib import Path

from pypdf import PdfReader

OUT = Path(__file__).resolve().parents[1] / 'dist'
LEVELS = {'Foerder': ('Förder','Meinen Rat kann ich jetzt begründen'), 'ESA': ('ESA','Jetzt kann ich besser erklären'),
          'MSA': ('MSA','Kriterium'), 'AHR': ('AHR','Annahme')}


def check():
    prompts = json.loads((OUT.parent/'material/laufzettel/aufgaben.json').read_text())
    results = []
    for slug, (level, skill) in LEVELS.items():
        path = OUT / 'Laufzettel' / f'Laufzettel-{slug}.pdf'
        reader = PdfReader(path)
        assert len(reader.pages) == 2
        texts = []
        for page in reader.pages:
            w, h = float(page.mediabox.width), float(page.mediabox.height)
            assert abs(w-595)<2 and abs(h-842)<2
            text = ' '.join(page.extract_text().split())
            assert level in text and 'Lehrkraft' not in text and '{{' not in text
            texts.append(text)
        for required in ('Infektionen', 'Mein erster Rat', 'Vorschlag A', 'Vorschlag B',
                         'Mein letzter Rat', 'Sicherung', skill, '1 / 2'):
            assert required in texts[0], (slug, required)
        assert all(word in texts[1] for word in ('Celina','Tom','Zusatzfall','2 / 2'))
        for field, value in prompts[level].items():
            page_text=texts[1 if field.startswith(('celina','tom')) else 0]
            for prompt in value if isinstance(value,list) else [value]:
                assert prompt in page_text, (level,field,prompt)
        if slug == 'AHR':
            assert all(word in texts[1] for word in ('Studie A','Studie B','Grenze','Endpunkt'))
        results.append(dict(datei=path.name,seiten=2,format='A4',
                            sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    assert len(list((OUT/'Laufzettel').glob('*.pdf'))) == 4
    teacher = OUT / 'Fallakte-Lehrkraft.pdf'
    pages = PdfReader(teacher).pages
    assert len(pages) == 2
    for page, (width, height) in zip(pages, [(842, 595), (595, 842)]):
        assert abs(float(page.mediabox.width) - width) < 2
        assert abs(float(page.mediabox.height) - height) < 2
    facts = ' '.join(pages[0].extract_text().split())
    rubric = ' '.join(pages[1].extract_text().split())
    data = json.loads((OUT.parent/'data/dialogdaten.js').read_text().split('=', 1)[1].strip()[:-1])
    assert all(stage['pauseFact'] in facts for stage in data['cases']['Laura'])
    assert all(label in rubric for label in ('Fallwissen','Vergleich','Gewichtung','Grenzen','Erster Rat','Letzter Rat'))
    (OUT/'qa'/'laufzettel.json').write_text(json.dumps({
        'html_sha256': hashlib.sha256((OUT/'Fallakte.html').read_bytes()).hexdigest(),
        'lehrkraft': dict(datei=teacher.name,sha256=hashlib.sha256(teacher.read_bytes()).hexdigest()),
        'pdfs': results}, ensure_ascii=False, indent=2))
    print('Vier Laufzettel mit acht A4-Seiten sowie Faktenfolie und Beobachtungsraster geprüft.')


if __name__ == '__main__':
    check()
