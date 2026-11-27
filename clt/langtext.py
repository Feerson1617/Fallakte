"""Lange fachliche Antworten im ausgepackten SCO über sichtbare Blättertasten erreichen."""
import json,sys,os
from pathlib import Path
from hashlib import sha256
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'gesamt'),str(ROOT/'tests')]
from lernspur_test import antwort
from ergonomie import room,reach,touch,HIT
from tagesauswahl import HOST,host
out=ROOT/'build/CLT/Langtext';out.mkdir(exist_ok=True,parents=True);rows=[]
with TemporaryDirectory() as tmp,sync_playwright() as pw:
    site=Path(tmp)
    with ZipFile(ROOT/'dist/Gesamt/Fallakte-08-12-SCORM12.zip') as z:z.extractall(site)
    (site/'host.html').write_text(HOST)
    with host(site) as url,pw.webkit.launch(executable_path=os.getenv('WEBKIT_EXECUTABLE')) as b:
        for day in ('02','08'):
            p=b.new_page(viewport={'width':740,'height':340},has_touch=True);p.set_default_timeout(5000)
            p.goto(url+'/host.html');p.frame_locator('[name=sco]').locator('#erster-tag').wait_for();s=p.frame(name='sco')
            f=room(s,'erster' if day=='02' else 'zweiter')
            f.evaluate("document.documentElement.style.fontSize='150%';Arbeitsplatz.refresh()")
            if day=='02':
                touch(f,'#level-ESA');touch(f,'#neu');antwort(f);touch(f,'[data-strategy="K+H"]')
                target=f.locator('[data-option="L01.ESA.K+H.3"]')
            else:
                s.locator('[data-action=recovery]').click();f.locator('#level-0').select_option('AHR')
                f.locator('#person').select_option('Lauras Frage');f.locator('#entry').select_option('2');f.locator('#open-entry').click()
                touch(f,'#weight-0');touch(f,'#concern-1');target=f.locator('#fact-1')
            reach(f,target);assert target.evaluate(HIT)
            rows.append(dict(tag=day,wortlaut=target.inner_text(),rechteck=target.bounding_box(),treffbar=True))
            p.screenshot(path=out/(day+'-Aussage-mit-grosser-Schrift.jpg'),quality=82);p.close()
    (out/'Langtextpruefung.json').write_text(json.dumps(dict(html_sha256=sha256((site/'index.html').read_bytes()).hexdigest(),webkit=rows),ensure_ascii=False,indent=2))
