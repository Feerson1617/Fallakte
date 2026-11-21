"""Create the offline HTML and SCORM package, using only the standard library."""
import base64
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/02-12'


def asset(match):
    path = ROOT / 'assets' / match[1]
    mime = {'.webp': 'image/webp', '.ttf': 'font/ttf'}[path.suffix]
    encoded = base64.b64encode(path.read_bytes()).decode('ascii')
    return f'url("data:{mime};base64,{encoded}")'


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    html = (ROOT / '02-12.html').read_text()
    css = re.sub(r'url\("\.\./assets/([^"]+)"\)', asset, (ROOT / 'app/style.css').read_text())
    html = html.replace('<link rel="stylesheet" href="app/style.css">', '<style>' + css + '</style>')
    for script in ('data/dialogdaten.js', 'data/lernhilfen.js', 'app/ui.js', 'app/lernhilfen.js', 'app/wiederaufnahme.js', 'app/app.js'):
        code = (ROOT / script).read_text().replace('</script', r'<\/script')
        html = html.replace(f'<script src="{script}"></script>', '<script>' + code + '</script>')
    licenses = '\n'.join(path.read_text() for path in sorted((ROOT / 'assets').glob('*-OFL.txt')))
    html = html.replace('</body>', '<script type="text/plain" id="font-licenses">' + licenses + '</script>\n</body>')
    local = OUT / 'Fallakte.html'
    local.write_text(html, encoding='utf-8')
    package = OUT / 'Fallakte-SCORM12.zip'
    with ZipFile(package, 'w', ZIP_DEFLATED) as z:
        z.write(local, 'index.html')
        for path in sorted((ROOT / 'scorm').iterdir()):
            z.write(path, path.name)
    with ZipFile(package) as z:
        assert z.testzip() is None
        manifest = ET.fromstring(z.read('imsmanifest.xml'))
        ns = {'i': 'http://www.imsproject.org/xsd/imscp_rootv1p1p2'}
        resource = manifest.find('i:resources/i:resource', ns)
        item = manifest.find('.//i:item', ns)
        assert manifest.findtext('i:metadata/i:schemaversion', namespaces=ns) == '1.2'
        assert item.attrib['identifierref'] == resource.attrib['identifier']
        assert resource.attrib['{http://www.adlnet.org/xsd/adlcp_rootv1p2}scormtype'] == 'sco'
        assert z.read(resource.attrib['href']) == local.read_bytes()
        assert all(f.attrib['href'] in z.namelist() for f in resource.findall('i:file', ns))
    return local


if __name__ == '__main__':
    print(build())
