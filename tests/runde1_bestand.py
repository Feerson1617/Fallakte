"""Exercise both optional cases and switch between the prototype and the published December 8 module."""
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from lxml.html import fromstring
from playwright.sync_api import expect, sync_playwright
from tagesauswahl import HOST, host

ROOT=Path(__file__).resolve().parents[1]
PROTO=ROOT/'dist/Runde-1/Fallakte.html'
BASE='ec94147fd8d61442305a0281f7df032f3162362c'
DAY8='5d27cc3d61db386468d3f851347690b33b5d86fe'
DAY8_HASH='a0588500259cc6255462d8670f3aa08c396730a1c7bdf6a37d34b82434839609'
QA=ROOT/'build/runde1'
sys.path.insert(0,str(ROOT/'scripts'))
from build import launcher


def sha(data):
    return hashlib.sha256(data).hexdigest()


def from_git(ref,path):
    return subprocess.check_output(['git','show',f'{ref}:{path}'],cwd=ROOT)


def documents(source):
    return {node.get('id'):base64.b64decode(node.text,validate=True)
            for node in fromstring(source).xpath('//script[@type="application/octet-stream"]')}


def replace_once(document,old,new):
    assert document.count(old)==1
    return document.replace(old,new)


def integration_fixture(root, prototype):
    # This development branch forks before the second module. Build the actual
    # later release in isolation and use it only in a temporary integration page.
    ref=root/'08-Referenz'
    inputs=('index.html','02-12.html','app','assets','data','scorm','module','tagesauswahl','scripts')
    archive=subprocess.check_output(['git','archive','--format=zip',DAY8,*inputs],cwd=ROOT)
    with ZipFile(io.BytesIO(archive)) as z:z.extractall(ref)
    subprocess.run([sys.executable,'scripts/build.py','--version','B'],cwd=ref,check=True)
    published=(ref/'dist/Version-B/Fallakte.html').read_bytes()
    old=documents(published)
    assert sha(old['modul-08'])==DAY8_HASH
    assert old['modul-08']==(ref/'build/08-12/Fallakte.html').read_bytes()
    # Protect the older branch's placeholder and the common header as well.
    tracked=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'module/08-12','tagesauswahl','index.html'],cwd=ROOT,text=True).splitlines()
    assert set(p.relative_to(ROOT).as_posix() for p in (ROOT/'module/08-12').rglob('*') if p.is_file())=={
        name for name in tracked if name.startswith('module/08-12/')}
    for name in tracked:
        assert (ROOT/name).read_bytes()==from_git(BASE,name),name
    proto=prototype.read_bytes()
    current=launcher('B',prototype).encode()
    placeholder=(ROOT/'module/08-12/index.html').read_bytes()
    assert documents(current)=={'modul-02':proto,'modul-08':placeholder}
    # Integrate the same two changes as the December 8 branch: its payload and group picture.
    current=replace_once(current,base64.b64encode(placeholder),base64.b64encode(old['modul-08']))
    current=replace_once(current,base64.b64encode((ROOT/'tagesauswahl/assets/laura-umfeld.webp').read_bytes()),
                         base64.b64encode((ref/'module/08-12/assets/laura-umfeld.webp').read_bytes()))
    assert current==replace_once(published,base64.b64encode(old['modul-02']),base64.b64encode(proto))
    (root/'index.html').write_bytes(current)
    (root/'host.html').write_text(HOST)
    return sha(current)


def legacy_data(browser):
    src=from_git(BASE,'data/dialogdaten.js').decode()
    data=json.loads(src.split('const FALLAKTE = ',1)[1].strip().removesuffix(';'))
    data['cases']={name:data['cases'][name] for name in ('Tom','Celina')}
    page=browser.new_page()
    page.add_script_tag(content=from_git(BASE,'data/lernhilfen.js').decode())
    hints=page.evaluate('Object.fromEntries(Object.entries(LERNHILFEN).filter(([id])=>/^[TC]/.test(id)))')
    page.close()
    return data,hints


def reserve_paths(browser,engine,expected,prototype):
    page=browser.new_page(viewport={'width':820,'height':1180},has_touch=True)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(prototype.as_uri())
    expect(page.locator('[data-optional]')).to_have_text(['Tom','Celina'])
    page.locator('#level-ESA').tap()
    page.locator('[data-optional=Tom]').tap()
    inner=page.frame_locator('#reserve-platz iframe')
    expect(inner.locator('#step')).to_have_text('Tom 1 von 3')
    assert inner.locator('body').evaluate('()=>FALLAKTE')==expected[0]
    assert inner.locator('body').evaluate('()=>LERNHILFEN')==expected[1]
    assert page.locator('#reserve-platz iframe').bounding_box()['height']>=600
    inner.locator('#method-K').tap()
    inner.locator('#send').tap()
    inner.get_by_role('button',name='Vorschlag beibehalten',exact=True).tap()
    expect(inner.locator('#step')).to_have_text('Tom 2 von 3')
    expect(inner.locator('#history .article')).to_have_count(1)
    logged=inner.locator('#history').inner_text()
    page.locator('[data-nav=home]').tap()
    page.locator('[data-optional=Celina]').tap()
    expect(inner.locator('#step')).to_have_text('Celina 1 von 5')
    inner.locator('#method-Cu').tap()
    inner.locator('#help').tap()
    page.locator('[data-nav=resources]').tap()
    expect(inner.locator('#resources')).to_be_visible()
    inner.locator('#resources .return').tap()
    expect(inner.locator('#hint-current')).to_be_visible()
    expect(inner.locator('#method-Cu')).to_have_attribute('aria-pressed','true')
    page.locator('[data-nav=home]').tap()
    page.locator('[data-optional=Tom]').tap()
    expect(inner.locator('#step')).to_have_text('Tom 2 von 3')
    assert inner.locator('#history').inner_text()==logged
    inner.get_by_role('button',name='Weiter nach dem Lesen',exact=True).tap()
    inner.get_by_role('button',name='Fall abschließen',exact=True).tap()
    inner.get_by_role('button',name='Zur Fallübersicht',exact=True).tap()
    expect(page.locator('#start')).to_be_visible()
    page.locator('[data-optional=Celina]').tap()
    expect(inner.locator('#method-Cu')).to_have_attribute('aria-pressed','true')
    expect(inner.locator('#hint-current')).to_be_visible()
    # A restart at the paper mark introduces no fictitious previous response.
    page.reload()
    page.locator('#abschnitt-wahl').tap()
    page.locator('#wieder-level-AHR').tap()
    page.locator('#wiederfall').get_by_role('button',name='Celina',exact=True).tap()
    expect(page.locator('#abschnitte button')).to_have_count(5)
    page.locator('#abschnitte button').nth(2).tap()
    expect(inner.locator('#step')).to_have_text('Celina 3 von 5')
    expect(inner.locator('#room-level')).to_have_text('AHR')
    expect(inner.locator('#history .team')).to_have_count(0)
    expect(inner.locator('.method[aria-pressed=true]')).to_have_count(0)
    assert not errors,errors
    page.close()
    return dict(browser=engine,daten_und_hilfen_wie=BASE,tom='1–3 mit Unterbrechung und Rückweg',
                celina='Kupferentwurf und geöffnete Hilfe; nach Reload AHR, Abschnitt 3 ohne alte Antworten')


def switch_days(browser,engine,first_url,lms,size):
    page=browser.new_page(viewport=dict(zip(('width','height'),size)),has_touch=True)
    errors,requests=[],[]
    permitted={first_url,first_url.replace('/host.html','/index.html')} if lms else set()
    def route(request):
        if request.request.url in permitted:request.continue_()
        else:requests.append(request.request.url);request.abort()
    page.route('http*/**',route)
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(first_url)
    shell=page.frame(name='sco') if lms else page.main_frame
    shell.locator('#erster-tag').tap()
    first=shell.frame_locator('iframe[title^=Mittwoch]')
    first.locator('#level-ESA').tap()
    first.locator('#neu').tap()
    chosen=first.locator('.strategie:visible').first
    chosen.tap()
    strategy=chosen.get_attribute('id')
    history=first.locator('#beratung-verlauf').inner_text()
    expect(shell.locator('#gespraechsstand')).to_have_text('Laura 1 · ESA')
    expect(first.locator('#lokale-navigation')).to_be_hidden()
    shell.locator('#zurueck').tap()
    shell.locator('#zweiter-tag').tap()
    second=shell.frame_locator('iframe[title^=Dienstag]')
    second.get_by_role('button',name='Mutter 1 – Argumenten-Check',exact=True).tap()
    field=second.get_by_role('combobox',name='Fakt',exact=True)
    field.select_option('1')
    expect(shell.locator('#modulaktionen button')).to_have_text(['Nachrichten','Fachkarten','Nach Neustart'])
    assert second.locator('body').evaluate('()=>typeof window.LAURA')=='undefined'
    shell.locator('#zurueck').tap()
    shell.locator('#erster-tag').tap()
    expect(first.locator('#'+strategy)).to_have_attribute('aria-pressed','true')
    assert first.locator('#beratung-verlauf').inner_text()==history
    shell.locator('[data-action=home]').tap()
    first.locator('[data-optional=Tom]').tap()
    reserve=first.frame_locator('#reserve-platz iframe')
    expect(reserve.locator('#step')).to_have_text('Tom 1 von 3')
    expect(shell.locator('#gespraechsstand')).to_have_text('Tom 1 · ESA')
    reserve.locator('#method-K').tap()
    shell.locator('#zurueck').tap();shell.locator('#zweiter-tag').tap()
    expect(field).to_have_value('1')
    expect(second.get_by_role('heading',name='Argumenten-Check',exact=True)).to_be_visible()
    shell.locator('#zurueck').tap();shell.locator('#erster-tag').tap()
    expect(reserve.locator('#method-K')).to_have_attribute('aria-pressed','true')
    shell.locator('[data-action=home]').tap();first.locator('#weiterarbeiten').tap()
    expect(first.locator('#'+strategy)).to_have_attribute('aria-pressed','true')
    calls=[]
    if lms:
        expect(page.locator('iframe')).to_have_count(1)
        assert page.evaluate('calls')==[['LMSInitialize','']]
        page.locator('iframe').evaluate("e=>e.src='about:blank'")
        page.wait_for_function('calls.length===2')
        calls=page.evaluate('calls')
        assert calls==[['LMSInitialize',''],['LMSFinish','']]
    assert not errors and not requests,(errors,requests)
    page.close()
    return dict(browser=engine,viewport=list(size),format='LMS-Testfenster' if lms else 'Datei',
                laura_entwurf=strategy,tag_08='Mutter 1 – Fakt, Zeile 1',reserve_entwurf='Tom – Kondom',
                scorm_sitzung=calls,skriptfehler=errors,externe_anfragen=requests)


def main():
    assert PROTO.is_file(), 'Zuerst python scripts/build.py ausführen.'
    QA.mkdir(parents=True,exist_ok=True)
    reports,reserve=[],[]
    with TemporaryDirectory() as temp,sync_playwright() as pw:
        root=Path(temp)
        prototype=root/'Prototyp.html'
        prototype.write_bytes(PROTO.read_bytes())
        proto_sha=sha(prototype.read_bytes())
        combined_sha=integration_fixture(root,prototype)
        with host(root) as url:
            for name in ('chromium','webkit'):
                b=getattr(pw,name).launch(executable_path=os.getenv(name.upper()+'_EXECUTABLE'))
                reserve.append(reserve_paths(b,name,legacy_data(b),prototype))
                for lms,size in [(False,(820,1180)),(True,(1180,820))]:
                    reports.append(switch_days(b,name,url+'/host.html' if lms else (root/'index.html').as_uri(),lms,size))
                print(name,'Reservewege und Tageswechsel bestanden.',flush=True)
                b.close()
    assert sha(PROTO.read_bytes())==proto_sha, 'Prüfung nach zwischenzeitlichem Neubau wiederholen.'
    output=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                html_sha256=proto_sha,schutz_08={'commit':DAY8,'sha256':DAY8_HASH,
                'gemeinsamer_rahmen':BASE,'testverbund_sha256':combined_sha},
                tageswechsel=reports,reserve=reserve,
                geltung='Funktionsprobe der Zusatzfälle. Die fachliche Gesamtabnahme bleibt einer späteren Runde vorbehalten.')
    (QA/'bestand.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
