"""Beide Tage in einer Sitzung mit Quelle, Hilfe, Unterbrechung und frischem Neustart prüfen."""
import json,os,sys
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'gesamt'),str(ROOT/'tests')]
from lernspur_test import antwort,schluss
from ergonomie import room,touch
from tagesauswahl import host,HOST
OUT=ROOT/'build/CLT/Sitzung';OUT.mkdir(exist_ok=True,parents=True)
BUNDLE=ROOT/'dist/Gesamt'
rows=[]
sample='Ich möchte berücksichtigen, dass Laura selbst über ihren Körper entscheidet.'
with TemporaryDirectory() as tmp,sync_playwright() as pw:
    site=Path(tmp)
    with ZipFile(BUNDLE/'Fallakte-08-12-SCORM12.zip') as z:z.extractall(site)
    raw=(BUNDLE/'Fallakte-08-12.html').read_bytes();assert raw==(site/'index.html').read_bytes()
    (site/'host.html').write_text(HOST)
    with host(site) as url:
        for e in ([sys.argv[1]] if len(sys.argv)>1 else ['chromium','webkit']):
            with getattr(pw,e).launch(executable_path=os.getenv(e.upper()+'_EXECUTABLE')) as b:
                for i,tier in enumerate(('Förder','ESA','MSA','AHR')):
                    ti=tier.replace('Förder','Foerder')
                    p=b.new_page(viewport={'width':820,'height':1180},has_touch=True);p.set_default_timeout(5000)
                    sco=i%2==0;source=url+'/host.html' if sco else (BUNDLE/'Fallakte-08-12.html').as_uri()
                    external=[];errors=[]
                    p.on('request',lambda r:external.append(r.url) if r.url.startswith(('http://','https://')) and not r.url.startswith(url+'/') else None)
                    p.on('pageerror',lambda x:errors.append(str(x)))
                    def open_page():
                        p.goto(source)
                        if not sco:return p.main_frame
                        p.frame_locator('[name=sco]').locator('#erster-tag').wait_for();return p.frame(name='sco')
                    s=open_page();a=room(s,'erster');a.locator('#level-'+ti).click();a.locator('#neu').click();antwort(a);touch(a,'[data-strategy=K]')
                    if i>=2:a.locator('#erklaerung').fill(sample)
                    touch(a,'#hilfe');touch(a,'#hilfe-weiter');touch(a,'#hilfe-weiter')
                    s.locator('#zurueck').click();f=room(s,'zweiter');f.locator('#level-0').select_option(tier);f.locator('#start').click();antwort(f);f.locator('#next').click()
                    if i>=2:f.locator('textarea').fill('Der Mutter ist Lauras Gesundheit wichtig.')
                    s.locator('#zurueck').click();a=room(s,'erster')
                    expect(a.locator('#material-titel')).to_contain_text('Hilfe 3')
                    touch(a,'#material-zurueck')
                    if i>=2:assert a.locator('#erklaerung').input_value()==sample
                    s.locator('[data-action=recovery]').click();a.locator('#abbrechen').click()
                    if i>=2:assert a.locator('#erklaerung').input_value()==sample
                    s.locator('[data-action=abschluss]').click();expect(a.locator('#lernspur h1')).to_have_text('Dein Schlussrat')
                    early=a.locator('.spur-chat').inner_text()
                    assert 'Regelschmerzen' in early and 'Latex' in early
                    if i==0:p.screenshot(path=OUT/(e+'-02-frueher-Stopp.jpg'),quality=63)
                    schluss(a);s.locator('#zurueck').click();f=room(s,'zweiter')
                    if i>=2:assert f.locator('textarea').input_value()=='Der Mutter ist Lauras Gesundheit wichtig.'
                    s.locator('[data-action=abschluss]').click();expect(f.locator('#lernspur h1')).to_have_text('Deine Einschätzung am Ende')
                    if i==0:p.screenshot(path=OUT/(e+'-08-frueher-Stopp.jpg'),quality=63)
                    schluss(f);s=open_page();f=room(s,'zweiter');s.locator('[data-action=recovery]').click()
                    f.locator('#level-0').select_option(tier);f.locator('#person').select_option('Freundin');f.locator('#entry').select_option('3');f.locator('#open-entry').click()
                    if i>=2:assert not f.locator('textarea').input_value()
                    s.locator('[data-action=abschluss]').click();antwort(f);expect(f.locator('#lernspur')).to_contain_text('keine erste Antwort')
                    assert not external and not errors and not p.context.storage_state()['origins']
                    rows.append(dict(browser=e,niveau=tier,scorm=sco,hilfe_erhalten=3,externe_anfragen=external,skriptfehler=errors))
                    p.close()
(OUT/('Sitzungspruefung-'+(sys.argv[1] if len(sys.argv)>1 else 'beide')+'.json')).write_text(json.dumps(dict(html_sha256=sha256(raw).hexdigest(),wege=rows),ensure_ascii=False,indent=2))
