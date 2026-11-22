"""Print the same portraits used in the built lesson as a single reference sheet."""
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
IMAGES=ROOT/'module/08-12/assets'
PORTRAITS={'Laura, 19':ROOT/'assets/laura.webp','Mutter':IMAGES/'mutter.webp',
           'Freundin':IMAGES/'freundin.webp','Großmutter':IMAGES/'grossmutter.webp','Vater':IMAGES/'vater.webp'}


def print_sheet(target):
    portraits=''.join(f'<figure><img src="{file.as_uri()}" alt=""><figcaption>{name}</figcaption></figure>'
                      for name,file in PORTRAITS.items())
    document=f'''<!doctype html><html lang="de"><meta charset="utf-8"><title>Laura und ihr Umfeld</title>
    <style>
    @font-face{{font-family:DM;src:url("{(ROOT/'assets/dmsans.ttf').as_uri()}")}}
    @font-face{{font-family:Serif;src:url("{(ROOT/'assets/dmseriftext.ttf').as_uri()}")}}
    @page{{size:A4 landscape;margin:0}}
    *{{box-sizing:border-box}}body{{margin:0;padding:14mm;background:#f7f6f0;color:#213e34;font:13pt DM,sans-serif}}
    header{{padding-top:4mm;border-top:2px solid #315746}}h1{{font:32pt Serif,serif;margin:1mm 0 7mm}}
    main{{display:grid;grid-template-columns:124mm 1fr;gap:10mm;align-items:center}}
    .gruppe{{width:124mm;height:124mm;border-radius:4mm}}
    section{{display:grid;grid-template-columns:repeat(3,1fr);gap:8mm 4mm}}
    figure{{margin:0}}figure img{{display:block;width:40mm;height:40mm;border-radius:3mm}}figcaption{{margin-top:2mm}}
    </style><header>Fallakte. · 08.12.2026<h1>Laura und ihr Umfeld</h1></header>
    <main><img class="gruppe" src="{(IMAGES/'laura-umfeld.webp').as_uri()}" alt="Laura mit ihren vier Bezugspersonen">
    <section>{portraits}</section></main></html>'''
    # Opening the local sheet makes the exact build images and fonts available without a server.
    source=ROOT/'build/08-12/Figuren-Druck.html'
    source.write_text(document)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.getenv('CHROMIUM_EXECUTABLE'))
        page=browser.new_page()
        page.goto(source.as_uri())
        page.evaluate('async()=>{await document.fonts.ready; await Promise.all([...document.images].map(i=>i.decode()))}')
        page.pdf(path=target,prefer_css_page_size=True,print_background=True)
        browser.close()
