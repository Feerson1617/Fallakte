"""Build one self-contained HTML file and one SCO per teaching release."""
import argparse
import base64
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from modul_0212 import build as build_first_day

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'


def encoded(path):
    return base64.b64encode(path.read_bytes()).decode('ascii')


def single_replace(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f'Expected one occurrence of {old!r}')
    return text.replace(old, new)


def launcher(version, first_day):
    html = (ROOT / 'index.html').read_text()
    css = (ROOT / 'tagesauswahl/start.css').read_text()
    for font in ('dmsans', 'dmseriftext'):
        css = single_replace(css, f'../assets/{font}.ttf', 'data:font/ttf;base64,' + encoded(ROOT / f'assets/{font}.ttf'))
    html = single_replace(html, '<link rel="stylesheet" href="tagesauswahl/start.css">', f'<style>{css}</style>')
    for picture in ('assets/laura.webp', 'tagesauswahl/assets/laura-umfeld.webp'):
        html = single_replace(html, f'src="{picture}"', f'src="data:image/webp;base64,{encoded(ROOT / picture)}"')
    for name in ('sitzung', 'start'):
        code = (ROOT / f'tagesauswahl/{name}.js').read_text()
        html = single_replace(html, f'<script src="tagesauswahl/{name}.js"></script>', f'<script>{code}</script>')

    entries = {'modul-02': first_day}
    html = single_replace(html, 'data-entry="02-12.html"', 'data-entry="modul-02"')
    if version == 'B':
        from modul_0812 import build as build_second_day
        entries['modul-08'] = build_second_day()
        html = single_replace(html, 'aria-labelledby="datum-08" disabled', 'aria-labelledby="datum-08" data-entry="modul-08"')
    # Inert data. Only the selected document is decoded and mounted.
    payloads = [f'<script id="{key}" type="application/octet-stream">{encoded(path)}</script>' for key, path in entries.items()]
    licenses = '\n'.join(path.read_text() for path in sorted((ROOT / 'assets').glob('*-OFL.txt')))
    return single_replace(html, '</body>', '\n'.join([*payloads, f'<script type="text/plain">{licenses}</script>', '</body>']))


def manifest(version):
    ims = 'http://www.imsproject.org/xsd/imscp_rootv1p1p2'
    ET.register_namespace('', ims)
    ET.register_namespace('adlcp', 'http://www.adlnet.org/xsd/adlcp_rootv1p2')
    ET.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    document = ET.parse(ROOT / 'scorm/imsmanifest.xml')
    document.getroot().set('identifier', f'FALLAKTE-{version}')
    for title in document.iter(f'{{{ims}}}title'):
        title.text = 'Fallakte.'
    return ET.tostring(document.getroot(), encoding='utf-8', xml_declaration=True)


def release(version, first_day):
    target = OUT / f'Version-{version}'
    target.mkdir(parents=True, exist_ok=True)
    html = target / 'Fallakte.html'
    html.write_bytes(launcher(version, first_day).encode('utf-8'))
    with ZipFile(target / 'Fallakte-SCORM12.zip', 'w', ZIP_DEFLATED) as package:
        package.write(html, 'index.html')
        package.writestr('imsmanifest.xml', manifest(version))
        for schema in sorted((ROOT / 'scorm').glob('*.xsd')):
            package.write(schema, schema.name)
    print(target)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', choices=('A', 'B'))
    requested = parser.parse_args().version
    first = build_first_day()
    for version in ([requested] if requested else ['A', 'B']):
        release(version, first)
