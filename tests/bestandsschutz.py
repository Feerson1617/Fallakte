"""Rebuild both independent Git references; allow only the reviewed overview changes."""
import hashlib
import io
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

from lxml import etree, html

FACHSTAND = 'ca77bf793ef1d2577d2f474895de15c503eb6df2'
TAGESSTAND = 'c1e5ce6a4f228d0f9e1c9b68df63159c27dddbda'
ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def archive(commit, folder, paths):
    raw = subprocess.check_output(['git','archive','--format=zip',commit,*paths],cwd=ROOT)
    with ZipFile(io.BytesIO(raw)) as files:
        files.extractall(folder)
        return [name for name in files.namelist() if not name.endswith('/')]


def build(folder):
    subprocess.run([sys.executable,'scripts/build.py'],cwd=folder,check=True)


def check_logic(original, current):
    # Everything up to and after the overview renderer includes the session,
    # feedback, revision, help, recovery and completion logic.
    def regions(source):
        prefix, rest = source.split('function home() {')
        menu, lesson = rest.split('function openCase(')
        return prefix, menu, lesson
    before, _, lesson = regions(original.decode())
    after, menu, current_lesson = regions(current.decode())
    visibility = "  $('open-recovery').hidden=id!=='home';\n"
    assert after.count(visibility) == 1 and after.replace(visibility,'') == before
    assert current_lesson == lesson
    assert digest(menu.encode()) == 'e1f5df33191d66f95bd2ecb7a7ddd9c7e6a3cfc83dffd708aaae9dd80514264c', 'Nicht freigegebene Änderung in home()'


def check_template(original, current):
    old, new = (html.fromstring(text) for text in (original,current))
    for selector in ('//header//nav','//*[@id="room-identity"]','//*[@id="recovery"]',
                     '//*[@id="resources"]','//*[@id="room"]','//head','//body/script'):
        assert [etree.tostring(e,with_tail=False) for e in old.xpath(selector)] == [
            etree.tostring(e,with_tail=False) for e in new.xpath(selector)], selector
    assert digest(current) == '549378f1cd4a600d8612fb2e895af1e743c9628a2c050c62a983236d1923e885'


def build_references(root):
    shared = root/'gemeinsam'
    archive(TAGESSTAND, shared, ('index.html','02-12.html','app','assets','data','scorm',
                                 'module','tagesauswahl','scripts/build.py','scripts/modul_0212.py'))
    build(shared)
    original = root/'fachstand'
    names = archive(FACHSTAND, original, ('index.html','app','assets','data','scorm','scripts/build.py'))
    build(original)
    frozen = (original/'dist/Fallakte.html').read_bytes()
    for name in names:
        if name == 'scripts/build.py':
            continue
        path = original/name
        old = path.read_bytes()
        current = (ROOT/('02-12.html' if name=='index.html' else name)).read_bytes()
        if name == 'app/app.js':
            check_logic(old,current)
        elif name == 'index.html':
            check_template(old,current)
        elif name == 'app/style.css':
            assert digest(current) == 'd9e394632729de5ef5e848006fd9fd17e194face1b5cf4876e41ec3af4036d38'
        else:
            assert current == old, name
            continue
        path.write_bytes(current)
    # Reuse the original compiler with exactly those three permitted UI inputs.
    build(original)
    return frozen, (original/'dist/Fallakte.html').read_bytes(), shared/'dist'
