"""Compile the two optional legacy cases into their own offline document."""
import base64
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def inline_asset(match):
    path = ROOT/'assets'/match[1]
    mime = {'.webp':'image/webp','.ttf':'font/ttf'}[path.suffix]
    encoded = base64.b64encode(path.read_bytes()).decode('ascii')
    return f'url("data:{mime};base64,{encoded}")'


def reserve_html():
    data = json.loads((ROOT/'data/dialogdaten.js').read_text().split('const FALLAKTE = ',1)[1].strip().removesuffix(';'))
    data['cases'] = {person:data['cases'][person] for person in ('Tom','Celina')}

    # Keep the existing reserve hints and their shared constants. No Laura data in this document.
    definitions, hints = (ROOT/'data/lernhilfen.js').read_text().split('const LERNHILFEN = {')
    definitions = re.sub(r'^const \w+Laura = [^\n]*;\n', '', definitions, flags=re.M)
    hints = definitions+'const LERNHILFEN = {\n  C0:'+hints.split('\n  C0:',1)[1]
    assert 'Laura' not in hints

    # The original engine owns the two conversations. The parent now owns home,
    # level selection, restart and SCORM. Include only the conversation runtime.
    engine = (ROOT/'app/app.js').read_text()
    prefix = engine[:engine.index('const cases = {')]
    state = engine[engine.index('const sessions ='):engine.index('function show(id)')]
    room = engine[engine.index('function openCase('):engine.index("$('open-recovery').onclick")]
    # Omit the obsolete Laura-only refusal branch and feedback from the delivered code too.
    room,n=re.subn(r"return current\.person==='Laura' \? '[^']*' : ('Celina[^']*');",r"return \1;",room)
    assert n==1
    a=room.index('    if (shortLaura() && s.declined')
    b=room.index('    showQuestionAnswer(area);',a)
    room=room[:a]+room[b:]
    scripts = ['const FALLAKTE = '+json.dumps(data,ensure_ascii=False)+';',hints,
               (ROOT/'app/ui.js').read_text(),(ROOT/'app/lernhilfen.js').read_text(),prefix+state+room]

    css = re.sub(r'url\("\.\./assets/([^"]+)"\)',inline_asset,(ROOT/'app/style.css').read_text())
    licenses = '\n'.join(p.read_text() for p in sorted((ROOT/'assets').glob('*-OFL.txt')))
    page = (ROOT/'module/0212/reserve-template.html').read_text()
    return page.replace('/* RESERVE_STYLE */',css).replace('/* RESERVE_SCRIPTS */',
        '\n'.join(scripts).replace('</script',r'<\/script')).replace('RESERVE_LICENSES',licenses)
