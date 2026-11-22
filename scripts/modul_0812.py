"""Compile the second lesson and its identical, resolved material bank."""
import base64
import json
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT/'module/08-12'
OUT = ROOT/'build/08-12'


def build():
    bank = run_path(str(MODULE/'inhalt.py'))['bank']()
    OUT.mkdir(parents=True, exist_ok=True)
    data = json.dumps(bank, ensure_ascii=False, indent=2)
    (OUT/'Aufgabenbank.json').write_text(data+'\n')
    page = (MODULE/'index.html').read_text()
    css = (MODULE/'nachrichten.css').read_text()
    for font in ('dmsans', 'dmseriftext'):
        name = font+'.ttf'
        css = css.replace('../../assets/'+name, 'data:font/ttf;base64,'+base64.b64encode((ROOT/'assets'/name).read_bytes()).decode())
    page = page.replace('<link rel="stylesheet" href="nachrichten.css">', '<style>'+css+'</style>')
    page = page.replace('id="material"></script>', 'id="material">'+data.replace('<',r'\u003c')+'</script>')
    for image in ('../../assets/laura.webp','assets/mutter.webp','assets/freundin.webp','assets/grossmutter.webp','assets/vater.webp'):
        src = f'src="{image}"'
        assert page.count(src) == 1
        page = page.replace(src, 'src="data:image/webp;base64,'+base64.b64encode((MODULE/image).read_bytes()).decode()+'"')
    for src in ('../../app/ui.js','nachrichten.js'):
        code = (MODULE/src).read_text()
        page = page.replace(f'<script src="{src}"></script>', '<script>'+code+'</script>')
    target = OUT/'Fallakte.html'
    target.write_text(page)
    return target
