"""Walk the rendered UI by the meaning of its visible German answers. No solution bank."""
import hashlib
import json
import os
import re
from pathlib import Path
from playwright.sync_api import expect, sync_playwright

ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/'dist/Familienrat/Fallakte.html'
OUT=ROOT/'build/Familienrat-Lernwege'
# Observer's interpretations of the original messages; fragments match visible choices.
READINGS={
    'Mutter':[
        ('Lauras körperliche Gesundheit','Ihr liegt Lauras Gesundheit am Herzen.'),
        ('Bei so einer Entscheidung sollte man mögliche Beschwerden','Sie will, dass Beschwerden bei solchen Entscheidungen zählen.'),
        ('Die Schwangerschaft fortsetzen','Sie rät zum Austragen.'),
        ('Fakt','Die Begründung enthält noch keine Erklärung des körperlichen Vorgangs.'),
        ('Es kommt zu Blutungen','Die Gebärmutter zieht sich zusammen. Ein Vergleich mit dem Austragen fehlt.')],
    'Freundin':[
        ('Lauras Ausbildung und ihre Pläne','Sie möchte, dass Laura selbst planen kann.'),
        ('Man sollte überlegen, wann Kinder','Ein allgemeiner Grundsatz zur Lebensplanung.'),
        ('Einen Abbruch mit Medikamenten vornehmen','Sie rät zum Abbruch.'),
        ('Fakt','Wünsche kennen wir. Einen biologischen Beleg liefert das noch nicht.'),
        ('Ja. Eine spätere Schwangerschaft bleibt möglich','Laura kann später schwanger werden. Eine Garantie gibt es nicht.')],
    'Großmutter':[
        ('Ungeborenes Leben sollte','Sie stellt eine Schutzregel auf.'),
        ('Die Schwangerschaft fortsetzen','Ihr persönlicher Rat ist Austragen.'),
        ('Wert','Das zu schützende Gut bleibt als Wert unausgesprochen.'),
        ('Mir ist das ungeborene','Sie gewichtet ungeborenes Leben. Das ist ihre Überzeugung.')],
    'Vater':[
        ('Laura soll selbst gut informiert','Er vertraut auf Lauras eigene Entscheidung.'),
        ('Die medizinischen Möglichkeiten in einer Arztpraxis','Er empfiehlt Information in der Praxis.'),
        ('Norm','Vom Einzelfall zur Regel fehlt ein Schritt.'),
        ('Vor wichtigen medizinischen Entscheidungen','Allgemein gilt für ihn, sich zu informieren. Laura entscheidet.')],
}
MISREAD={'Mutter':'Weil Medikamente eingesetzt','Freundin':'Ja. Eine spätere Schwangerschaft ist garantiert',
         'Großmutter':'Ungeborenes menschliches Leben sollte','Vater':'Laura, lass deine medizinischen'}
TRANSFER={'Mutter':['Die Gebärmutter zieht','Kontraktionen können auch ohne Operation'], 'Freundin':['Nein. Sie ist möglich','Nach einem komplikationslosen Abbruch bleibt'],
          'Großmutter':['Körperliche Gesundheit'],'Vater':['Jede Person sollte']}

def walk(b,tier,stumble):
    page=b.new_page(has_touch=True,viewport={'width':820 if stumble else 1180,'height':1180 if stumble else 820})
    page.goto(APP.as_uri()); page.locator('#zweiter-tag').click();f=page.frame_locator('iframe[title^=Dienstag]')
    page.set_default_timeout(4500)
    log=[]
    def control(id):f.locator('#'+id).click()
    def choose(texts):
        if isinstance(texts,str):texts=[texts]
        matches=f.locator('button[id^=answer-]').filter(has_text=re.compile('^(?:'+'|'.join(map(re.escape,texts))+')'))
        expect(matches).to_have_count(1)
        if not matches.is_visible():f.locator('#more-options summary').click()
        label=matches.inner_text();matches.click()
        log.append(dict(abschnitt=f.locator('h1').inner_text(),frage=f.locator('section h2').last.inner_text(),
                        gewaehlt=label,rueckmeldung=f.locator('#response').inner_text()))
    def family(name):
        control('next')
        for fragment,thought in READINGS[name]:
            if f.locator('textarea').is_visible():
                f.locator('textarea').fill(thought);control('compare')
                log.append(dict(eigene_formulierung=thought))
            if stumble and fragment==READINGS[name][-1][0]:
                choose(MISREAD[name]);control('help');control('hint-last')
                log.append(dict(erklaerung=f.locator('#dialog-body p').inner_text()))
                control('dismiss')
            choose(fragment);control('next')
        if stumble:choose(TRANSFER[name])
        log.append(dict(papier=f.locator('[data-handoff]').inner_text()));control('next')
    f.locator('#level-0').select_option(tier);control('start')
    for n in ('Mutter','Freundin'):family(n)
    control('next')
    log.append(dict(persoenlicher_auftrag=f.locator('[data-handoff]').inner_text()))
    control('next')
    # Separate paper perspectives deliberately use different, defensible weightings.
    weight={'Förder':0,'ESA':1,'MSA':2,'AHR':2}[tier]
    control('weight-'+str(weight))
    for i in ([0,1] if weight==2 else [weight]):
        control('concern-'+str(i))
        if stumble:control('fact-2')
        control('fact-'+str(i));choose('Nein. Sie');control('next')
    expect(f.locator('[data-terminal]')).to_be_visible()
    log.append(dict(abschluss=f.locator('section').inner_text()))
    if stumble:
        for n in ('Großmutter','Vater'):control('open-'+n);family(n)
    page.close()
    return dict(niveau=tier,weg='Fehlvorstellung und Hilfe' if stumble else 'Regulär',handlungen=log)

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.getenv('CHROMIUM_EXECUTABLE'))
        routes=[walk(browser,t,s) for t in ('Förder','ESA','MSA','AHR') for s in (False,True)]
        version=browser.version;browser.close()
    commit=json.loads((APP.parent/'Work-Materialvertrag.json').read_text())['commit']
    (OUT/'Lernwege.json').write_text(json.dumps(dict(commit=commit,html_sha256=hashlib.sha256(APP.read_bytes()).hexdigest(),browser=version,wege=routes),ensure_ascii=False,indent=2))
