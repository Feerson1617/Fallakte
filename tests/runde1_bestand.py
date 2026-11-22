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


def presentation(frame):
    """Open deliberately, project all facts and return to the same work area."""
    access=frame.locator('#lehrkraft')
    handle=access.locator('summary')
    open_button=frame.get_by_role('button',name='Gemeinsame Sicherung öffnen',exact=True)
    dialog=frame.locator('#material-dialog[open]')
    expect(frame.locator('nav #lehrkraft,nav [data-nav=summary]')).to_have_count(0)
    expect(open_button).to_have_count(0)
    expect(dialog).to_have_count(0)
    handle.tap()
    expect(open_button).to_be_visible()
    expect(dialog).to_have_count(0)
    open_button.tap()
    expect(dialog).to_have_attribute('data-view','summary')
    facts=dialog.locator('li').all_text_contents()
    for topic in ('Latexallergie','Infektionen','Alltag','Freundin','Regelschmerzen','Einsetzen'):
        assert any(topic in fact for fact in facts),topic
    expect(dialog.locator('input,textarea')).to_have_count(0)
    dialog.get_by_role('button',name='Zurück',exact=True).tap()
    expect(handle).to_be_focused()
    expect(open_button).to_have_count(0)


def reserve_paths(browser,engine,expected,prototype):
    page=browser.new_page(viewport={'width':820,'height':1180},has_touch=True)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(prototype.as_uri())
    expect(page.locator('[data-optional]')).to_have_text(['Tom','Celina'])
    presentation(page)
    expect(page.locator('#weiterarbeiten')).to_be_hidden()
    page.locator('#level-ESA').tap()
    page.locator('[data-optional=Tom]').tap()
    inner=page.frame_locator('#rahmen-reserve-Celina')
    tom=page.frame_locator('#rahmen-reserve-Tom')
    expect(tom.locator('#step')).to_have_text('Tom 1 von 3')
    tom.locator('#method-K').tap()
    tom.locator('#answer-B').tap()
    tom.locator('#send').tap()
    tom.locator('#next').tap()
    expect(tom.locator('#step')).to_have_text('Tom 2 von 3')
    logged=tom.locator('#desk details').first.text_content()
    page.locator('[data-nav=home]').tap()
    page.locator('[data-optional=Celina]').tap()
    expect(inner.locator('#step')).to_have_text('Celina 1 von 5')
    inner.locator('#method-Cu').tap()
    inner.locator('#help').tap()
    page.locator('[data-nav=resources]').tap()
    expect(inner.locator('#resource')).to_contain_text('Kupfer')
    inner.locator('#back').tap()
    expect(inner.locator('#resource')).to_have_text('Hilfe')
    expect(inner.locator('dialog[open]')).to_be_visible()
    expect(inner.locator('#selected')).to_contain_text('Kupfer')
    page.locator('[data-nav=home]').tap()
    page.locator('[data-optional=Tom]').tap()
    expect(tom.locator('#step')).to_have_text('Tom 2 von 3')
    assert tom.locator('#desk details').first.text_content()==logged
    for answer in ('C','A'):
        tom.locator('#answer-'+answer).tap()
        tom.locator('#send').tap()
        tom.locator('#next').tap()
    expect(page.locator('#start')).to_be_visible()
    page.locator('[data-optional=Celina]').tap()
    expect(inner.locator('#selected')).to_contain_text('Kupfer')
    expect(inner.locator('dialog[open]')).to_be_visible()
    # A restart at the paper mark introduces no fictitious previous response.
    page.reload()
    page.locator('#abschnitt-wahl').tap()
    presentation(page)
    expect(page.locator('#abschnitte button')).to_have_text(['Laura 1 – Latexallergie','Laura 2 – Zwei Schutzziele',
        'Laura 3 – Hormone und Alltag','Laura 4 – Schmerzen und Einlage','Laura 5 – Mein Schlussrat'])
    page.locator('#wieder-level-AHR').tap()
    page.locator('#wiederfall').get_by_role('button',name='Celina',exact=True).tap()
    expect(page.locator('#abschnitte button')).to_have_count(5)
    page.locator('#abschnitte button').nth(2).tap()
    expect(inner.locator('#step')).to_have_text('Celina 3 von 5')
    expect(inner.locator('#desk')).to_contain_text('AHR')
    expect(inner.get_by_text('Gesprächsverlauf',exact=True)).to_have_count(0)
    expect(inner.locator('#selected')).to_have_count(0)
    assert not errors,errors
    page.close()
    return dict(browser=engine,ausgangsdialoge=BASE,tom='1–3 mit Unterbrechung und Rückweg',
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
    strategy=chosen.get_attribute('data-strategy')
    chosen.tap()
    draft=first.locator('#aktueller-rat')
    history=first.locator('#beratung-verlauf').inner_text()
    expect(shell.locator('#gespraechsstand')).to_have_text('Laura 1 · ESA')
    expect(first.locator('#lokale-navigation')).to_be_hidden()
    expect(shell.locator('#modulaktionen button')).to_have_text(['Fallakten','Infokarten','Abschnitt auswählen'])
    presentation(first)
    expect(draft).to_have_attribute('data-about-strategy',strategy)
    expect(first.locator('#nachricht-senden')).to_be_disabled()
    assert first.locator('#beratung-verlauf').inner_text()==history
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
    expect(draft).to_have_attribute('data-about-strategy',strategy)
    assert first.locator('#beratung-verlauf').inner_text()==history
    shell.locator('[data-action=home]').tap()
    first.locator('[data-optional=Tom]').tap()
    reserve=first.frame_locator('#rahmen-reserve-Tom')
    expect(reserve.locator('#step')).to_have_text('Tom 1 von 3')
    expect(shell.locator('#gespraechsstand')).to_have_text('Tom 1 · ESA')
    reserve.locator('#method-K').tap()
    presentation(first)
    expect(reserve.locator('#selected')).to_contain_text('Kondom')
    shell.locator('#zurueck').tap();shell.locator('#zweiter-tag').tap()
    expect(field).to_have_value('1')
    expect(second.get_by_role('heading',name='Argumenten-Check',exact=True)).to_be_visible()
    shell.locator('#zurueck').tap();shell.locator('#erster-tag').tap()
    expect(reserve.locator('#selected')).to_contain_text('Kondom')
    shell.locator('[data-action=home]').tap();first.locator('#weiterarbeiten').tap()
    expect(draft).to_have_attribute('data-about-strategy',strategy)
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
                lehrkraftzugang='Explizit geöffnet und geschlossen; Entwurf, Verlauf und Sendesperre erhalten.',
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
