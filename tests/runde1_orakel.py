"""Independent biological expectations, without loading the bank's solution flags.

The phrases identify the causal claim, not the option ID or the order of the choices.
When the copy changes, inspect the whole claim again before changing a phrase here.
"""
import re

CLAIMS = {
    'L01':{
        'K':(r'passendes Kondom ohne Latex hält Spermien zurück',r'synthetisches Kondom ohne Latex fängt Sperma auf'),
        'P':(r'Pille hemmt den Eisprung.*Kondom ohne Latex bleibt möglich',r'Pille hemmt vor allem den Eisprung.*nicht zwingend'),
        'Cu':(r'Kupfer hemmt Spermien.*Kondom ohne Latex kann passen',r'Kupfer beeinträchtigt Spermien.*ohne Hormone'),
        'H':(r'Spirale verändert den Schleim für Spermien.*Kondom ohne Latex kommt infrage',r'Hormonspirale erschwert Spermien den Weg.*latexfreies Kondom bleibt'),
        'K+P':(r'Kondom ohne Latex hält Spermien zurück.*Pille hemmt den Eisprung',r'latexfreie Kondom bildet eine Barriere.*Pille hemmt'),
        'K+Cu':(r'Kondom ohne Latex hält Spermien zurück.*Kupfer hemmt Spermien',r'latexfreies Kondom bildet eine Barriere.*Kupfer kann zusätzlich Spermien beeinträchtigen'),
        'K+H':(r'Kondom ohne Latex hält Spermien zurück.*Hormon verändert den Schleim',r'latexfreie Kondom bildet eine Barriere.*Hormonspirale erschwert Spermien den Weg'),
    },
    'L02':{
        'K':(r'Es senkt das Risiko vieler Infektionen, aber nicht ganz',r'senkt bei richtiger Anwendung das Risiko vieler STI.*Risiko bleibt'),
        'P':(r'Pille hemmt den Eisprung.*vor Infektionen schützt sie nicht',r'Eisprung hemmt.*STI-Anliegen bleibt bei der Pille allein offen'),
        'Cu':(r'Kupfer hemmt Spermien.*vor Infektionen schützt es nicht',r'Wirkung auf Spermien mindert das STI-Risiko nicht'),
        'H':(r'Schleim hält Spermien auf.*vor Infektionen schützt die Hormonspirale nicht',r'Schleim am Gebärmutterhals erschwert Spermien den Weg.*keinen STI-Schutz'),
        'K+P':(r'Pille hemmt den Eisprung.*Kondom ohne Latex hält Spermien zurück und senkt das Risiko',r'Pille hemmt vor allem den Eisprung.*Kondom.*senkt das STI-Risiko'),
        'K+Cu':(r'Kupfer hemmt Spermien.*Kondom ohne Latex hält Spermien zurück und senkt das Risiko',r'Kupfer beeinträchtigt Spermien.*Kondom hält Sperma zurück und senkt'),
        'K+H':(r'Hormonspirale erschwert Spermien den Weg.*Kondom ohne Latex.*senkt das Risiko',r'Hormonspirale erschwert Spermien den Weg.*Kondom trägt zur Verhütung bei und senkt'),
    }
}

# In these chapters both lower levels assess the same causal relationships. ESA has
# an additional distractor. Neither answer positions nor the application's grade are used.
LATER_CLAIMS = {
    'L03': {
        'K': r'beim Sex, nicht jeden Tag.*Freundin betrifft die Pille',
        'P': r'Vergessene Tabletten können den Schutz mindern.*nichts Sicheres über Laura.*STI-Schutz fehlt',
        'Cu': r'Kupferspirale wirkt ohne tägliche Einnahme.*nicht vor Infektionen',
        'H': r'ohne tägliche Tablette.*Erfahrung mit der Pille entscheidet nicht.*STI-Schutz fehlt',
        'K+P': r'Pille benötigt regelmäßige Einnahme.*Kondom beim Sex senkt auch das STI-Risiko',
        'K+Cu': r'Kupfer wirkt ohne tägliche Einnahme.*beim Sex braucht Laura.*Kondom für den STI-Schutz',
        'K+H': r'Hormonspirale wirkt ohne tägliche Tablette.*Kondom muss beim Sex.*senkt das STI-Risiko',
    },
    'L04': {
        'K': r'Kondom verändert die Regel nicht.*Schmerzen sollten.*ärztlich abgeklärt',
        'P': r'Pille können Regelschmerzen geringer werden.*ist offen.*STI-Schutz fehlt',
        'Cu': r'Kupfer kann Regelschmerzen verstärken.*Beratung und muss selbst zustimmen.*keinen STI-Schutz',
        'H': r'Hormonspirale können die Schmerzen nachlassen.*Sicher ist das nicht.*keinen STI-Schutz',
        'K+P': r'Kondom senkt das STI-Risiko.*Pille kann Regelschmerzen lindern.*Eignung muss geklärt',
        'K+Cu': r'Kondom senkt das STI-Risiko.*Kupfer kann Regelschmerzen verstärken.*Ohne Beratung und Lauras Zustimmung keine Einlage',
        'K+H': r'Kondom senkt das STI-Risiko.*Hormonspirale könnte Schmerzen lindern.*Beratung und Lauras Zustimmung',
    },
    'L05': {
        'K': r'Kondom ohne Latex hält Spermien zurück und senkt das STI-Risiko.*bei jedem Sex muss es richtig sitzen',
        'P': r'Pille kann Schwangerschaften verhindern.*Tägliche Einnahme kann schwierig.*Schutz vor Infektionen fehlt',
        'Cu': r'Kupferspirale wirkt lange ohne Hormone.*kann Schmerzen verstärken und schützt allein nicht vor STI',
        'H': r'Hormonspirale braucht keine tägliche Einnahme.*Schmerzen passt, ist offen.*STI-Schutz fehlt',
        'K+P': r'Kondom senkt das STI-Risiko.*Pille hemmt den Eisprung, braucht aber regelmäßige Einnahme',
        'K+Cu': r'Kondom senkt das STI-Risiko.*Kupfer wirkt lange, kann aber Schmerzen verstärken.*Einlage ist noch offen',
        'K+H': r'Kondom senkt das STI-Risiko.*Hormonspirale wirkt lange.*ob sie passt und Laura die Einlage möchte, ist offen',
    },
}


def correct_reason(tier,stage,strategy,labels):
    pattern=(LATER_CLAIMS[stage][strategy] if stage in LATER_CLAIMS
             else CLAIMS[stage][strategy][0 if tier=='Foerder' else 1])
    matches=[i for i,label in enumerate(labels) if re.search(pattern,label,re.I|re.S)]
    assert len(matches)==1, (tier,stage,strategy,pattern,labels)
    return matches[0]
