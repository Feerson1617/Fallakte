"""Render the four student handouts with the Chromium installed for acceptance."""
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
                assert sheet.evaluate('(e)=>e.querySelector("footer").getBoundingClientRect().bottom < e.getBoundingClientRect().bottom'), tier
            slug = 'Foerder' if tier == 'Förder' else tier
            page.pdf(path=OUT / f'Laufzettel-{slug}.pdf', prefer_css_page_size=True,
                     print_background=True, tagged=True)
        browser.close()


if __name__ == '__main__':
    build()
