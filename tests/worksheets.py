"""Read the delivered PDFs back independently of the HTML print template."""
import hashlib
import json
from pathlib import Path

from pypdf import PdfReader

OUT = Path(__file__).resolve().parents[1] / 'dist'
LEVELS = {'Foerder': ('Förder','Zeige, wo'), 'ESA': ('ESA','Unterstreiche'),
          'MSA': ('MSA','Kriterium'), 'AHR': ('AHR','Annahme')}


def check():
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
        if slug == 'AHR':
            assert all(word in texts[1] for word in ('Studie A','Studie B','Grenze','Endpunkt'))
        results.append(dict(datei=path.name,seiten=2,format='A4',
                            sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    assert len(list((OUT/'Laufzettel').glob('*.pdf'))) == 4
    (OUT/'qa'/'laufzettel.json').write_text(json.dumps({
        'html_sha256': hashlib.sha256((OUT/'Fallakte.html').read_bytes()).hexdigest(),
        'pdfs': results}, ensure_ascii=False, indent=2))
    print('Vier PDF-Fassungen, acht A4-Seiten und die Aufgaben aller Niveaus geprüft.')


if __name__ == '__main__':
    check()
