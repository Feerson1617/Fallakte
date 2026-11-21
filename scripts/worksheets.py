"""Render the student handouts and the teacher's classroom materials."""
from html import escape
import json
from pathlib import Path
import re

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MATERIAL = ROOT / 'material/laufzettel'
OUT = ROOT / 'dist/Laufzettel'


def fields(labels):
    return ''.join(f'<div class="field">{escape(label)}</div><div class="line"></div>' for label in labels)


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    template = (MATERIAL / 'vorlage.html').read_text()
    tasks = json.loads((MATERIAL / 'aufgaben.json').read_text())
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto((MATERIAL / 'vorlage.html').as_uri())
        page.emulate_media(media='print')
        for tier, prompts in tasks.items():
            slots = {k: fields(v) if isinstance(v, list) else escape(v) for k, v in prompts.items()}
            slots['niveau'] = tier
            page.set_content(re.sub(r'{{(\w+)}}', lambda m: slots[m[1]], template))
            page.evaluate('document.fonts.ready')
            for sheet in page.locator('.page').all():
                clipped = sheet.evaluate("""sheet => {
                  const page = sheet.getBoundingClientRect();
                  const footer = sheet.querySelector('footer').getBoundingClientRect();
                  const words = document.createTreeWalker(sheet, NodeFilter.SHOW_TEXT);
                  const range = document.createRange();
                  for (let text; (text=words.nextNode());) {
                    if (!text.textContent.trim()) continue;
                    range.selectNodeContents(text);
                    const parent = text.parentElement;
                    const box = (parent.closest('.box,header,footer,section') || sheet).getBoundingClientRect();
                    const bottom = parent.closest('footer') ? page.bottom : footer.top;
                    for (const line of range.getClientRects()) {
                      if (line.left < Math.max(page.left,box.left)-1 || line.right > Math.min(page.right,box.right)+1 ||
                          line.top < page.top || line.bottom > Math.min(bottom,box.bottom)+1)
                        return text.textContent;
                    }
                  }
                  return null;
                }""")
                assert clipped is None, (tier,clipped)
            slug = 'Foerder' if tier == 'Förder' else tier
            page.pdf(path=OUT / f'Laufzettel-{slug}.pdf', prefer_css_page_size=True,
                     print_background=True, tagged=True)
        data = (ROOT / 'data/dialogdaten.js').read_text().split('=', 1)[1].strip()[:-1]
        facts = [stage['pauseFact'] for stage in json.loads(data)['cases']['Laura']]
        teacher = (ROOT / 'material/lehrkraft/unterrichtsstopp.html').read_text()
        page.set_content(teacher.replace('{{fakten}}', ''.join(f'<li>{escape(f)}</li>' for f in facts)))
        page.pdf(path=ROOT / 'dist/Fallakte-Lehrkraft.pdf', prefer_css_page_size=True,
                 print_background=True, tagged=True)
        browser.close()


if __name__ == '__main__':
    build()
