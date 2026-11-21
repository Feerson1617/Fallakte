"""Read the delivered PDFs back independently of the HTML print template."""
import hashlib
import json
import math
from pathlib import Path

from pypdf import PdfReader

OUT = Path(__file__).resolve().parents[1] / 'dist'
LEVELS = {'Foerder': ('Förder','Meinen Rat kann ich jetzt begründen'), 'ESA': ('ESA','Jetzt kann ich besser erklären'),
          'MSA': ('MSA','Kriterium'), 'AHR': ('AHR','Annahme')}


def check_wheel(number):
    path = OUT / f'Empfehlungsrad-{number}.pdf'
    pages = PdfReader(path).pages
    assert len(pages) == 1
    page = pages[0]
    assert abs(float(page.mediabox.width)-1191) < 2 and abs(float(page.mediabox.height)-842) < 2
    text = ' '.join(page.extract_text().split())
    instructions, separator, wheel_text = text.partition('Markiere einen freien Kreis bei deiner Empfehlung.')
    assert separator
    names = ['Kondom', 'Kombinationspille', 'Kupferspirale', 'Hormonspirale']
    combined = 'Kondom + weitere Methode'
    assert (combined in wheel_text) == (number == 2)
    if number == 2:
        names.append(combined)
        assert 'beide Namen auf deinen Laufzettel' in instructions
    assert all(name in wheel_text for name in names)
    # Measure the printed circles in the wheel's millimetre coordinate system.
    sectors = [[] for name in names]
    span = 360 / len(sectors)
    points = []
    for args, op in page.get_contents().operations:
        if op == b'm':
            points = list(args)
        elif op in (b'c', b'l'):
            points.extend(args)
        elif op == b'S' and points:
            xs, ys = points[::2], points[1::2]
            width, height = max(xs)-min(xs), max(ys)-min(ys)
            if width > 50:  # outline of a sector
                continue
            assert 7 <= width <= 8 and abs(width-height) < .01
            x, y = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
            angle = (math.degrees(math.atan2(y, x)) + 90 + span/2) % 360
            radius = math.hypot(x, y)
            assert radius + width/2 < 131
            assert radius * math.sin(math.radians(min(angle % span, span-angle % span))) > width/2
            field = sectors[int(angle//span)]
            assert all(math.dist((x,y), other) >= width+1 for other in field)
            field.append((x,y))
    counts = [len(field) for field in sectors]
    assert counts == [28]*len(names), (path, counts)
    return dict(datei=path.name, seiten=1, format='A3 quer', markierungen=dict(zip(names,counts)),
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())


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
        'empfehlungsraeder': [check_wheel(number) for number in (1, 2)],
        'pdfs': results}, ensure_ascii=False, indent=2))
    print('Vier Laufzettel, Faktenfolie, Beobachtungsraster und zwei A3-Räder mit je 28 Markierungen pro Feld geprüft.')


if __name__ == '__main__':
    check()
