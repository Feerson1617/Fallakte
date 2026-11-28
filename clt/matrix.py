"""Qualitative Zuordnung der realen Bildschirmzustände; keine Belastungsmessung."""
import csv
import hashlib
from io import StringIO

def matrix(rows,day):
    table=StringIO();w=csv.writer(table)
    w.writerow(['Nachweis','Niveau','Fall','Aufgabe','sichtbarer Wortlaut','Intrinsic','Extraneous','lernbezogene Verarbeitung','Element Interactivity','Split Attention','Redundanz','Kohärenz','Signalisierung','Räumliche Kontiguität','Segmentierung','Vorwissen','Transient Information','Worked Examples','Guidance Fading','Expertise Reversal','Verbleibende Anforderung'])
    for tier,r in rows:
        text=r['text'];task=r['task'];name=r['caseName'];ev=r['event'];ids=r['ids'];q=r['question']
        if day=='02':
            relations={'L01':'Latexallergie, Material und Schwangerschaftsschutz','L02':'Schwangerschaftsschutz und Risiko sexuell übertragbarer Infektionen','L03':'Einnahmeroutine und persönliche Verträglichkeit','L04':'Beschwerden, ärztliche Abklärung und Zustimmung','L05':'Anliegen, Wirkungsweise und Grenze des eigenen Rats'}
            relation=next((v for k,v in relations.items() if k in name),'Celinas Anliegen und Methodenwirkung' if 'Celina' in name else 'Toms eigener Handlungsspielraum und Aussagen der Forschung')
            doing='Die Wirksamkeit des eigenen Rats unter den aktuellen Bedingungen begründen.'
            memory='Der Chat hält bereits gesendete Vorschläge und Lauras Reaktion fest.' if 'Laura' in name else 'Frühere Beiträge bleiben im Gespräch. Bei Direkteinstieg ist das bisher Bekannte als Rückblick gekennzeichnet.'
            split='Der verlinkte Abschnitt steht im digitalen Arbeitsbereich. Die selbst erstellte Karte kann zum Nachschlagen dienen.'
        else:
            relation={'Wert':'Sprecher und persönliches Anliegen','Norm':'Aussage und zugrunde gelegte Regel','Folgerung':'Anliegen, Regel und daraus abgeleiteter Rat','Leerstelle':'Vorhandene und fehlende Bestandteile der Nachricht','Ergänzung':'Fehlender Bestandteil und verfügbare Fachinformation','Anwendung':'Geltungsbereich der geprüften Aussage im neuen Beispiel'}.get(task,'Anliegen, Herkunft und Reichweite der Aussage')
            doing='Den Grund in der Nachricht identifizieren und seine Bedeutung für Laura prüfen.'
            memory='Originalnachricht und fachlich bestätigte Auswahlen bleiben im Chat. Die Übersicht nennt den in der Sitzung geprüften Stand.'
            split='Quelle, Erklärung und Auswahl befinden sich am selben Gerät.'
        hint='hint' in ev or 'hilfe' in ev or 'Hilfe' in q
        wrong=any(x in text for x in ('noch nicht','Prüfe','fehlt','passt nicht')) or ev.startswith('grund-')
        free=any('erklaerung' in x or 'compare' in x for x in ids)
        personal='Gewicht' in task or 'Reichweite' in task or 'Fakt ' in task or 'abschlusskarte' in ids
        micro=('Hilfestufe lesen und auf die eigene Antwort beziehen.' if hint else 'Die eigene Erklärung mit der Aussage vergleichen.' if free else 'Den Anlass für die Rückmeldung prüfen.' if wrong else 'Einen eigenen Standpunkt mit einem fachlichen Grund abwägen.' if personal else doing)
        example=('Der aktuell geöffnete Impuls oder das Beispiel stehen im protokollierten Wortlaut.' if hint else 'Ein Beispiel ist freiwillig über Hilfe erreichbar.' if not personal else 'Der Sachbezug ist prüfbar. Ein persönliches Urteil bleibt offen.')
        key=hashlib.sha256((tier+str(r)).encode()).hexdigest()[:14]
        w.writerow([key,tier,name,task,text,relation,'Eine Aufgabe im Arbeitsbereich. Lange Ansichten haben Blättertasten.',micro,relation,split,'Keine parallele Niederschrift während der Erarbeitung.','Wortlaut und angebotene Steuerungen sind im Browserprotokoll nachprüfbar.',q or task,'Auftrag und Eingabe stehen zusammen. Die zugehörige Nachricht steht im rechten Gesprächsfeld oder in der schmalen Chatansicht.','Nur der aktuelle Schritt bzw. die geöffnete Hilfe.',relation,memory,example,'Hilfen schließen und den eigenen Weg fortsetzen.','Ohne Hilfe weiterarbeiten ist möglich.','Lesefähigkeit und Qualität der eigenen Begründung im Unterricht beurteilen.' if not hint else 'Verstehen des Beispiels und selbstständige Anwendung persönlich überprüfen.'])
    return table.getvalue()
