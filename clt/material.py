"""Verbindliche Wortlaute für die von Work gestalteten Karten."""
LEVELS=('Förder','ESA','MSA','AHR')
KARTEN={
'02':{
'Förder':('Mein erster Rat für Laura ist … Mein Grund: … Stichworte reichen.','Mein Rat für Laura ist …','Laura ist … wichtig. Die Methode hilft dabei, weil …'),
'ESA':('Ich rate Laura zu …, weil …','Ich rate Laura jetzt zu …','Für Laura ist … wichtig. Die Methode … Deshalb …'),
'MSA':('Welchen ersten Rat gibst du Laura? Was spricht dafür?','Welchen Rat gibst du Laura jetzt?','Verbinde ein Anliegen mit der Wirkung der Methode. Welche Grenze bleibt?'),
'AHR':('Welcher Rat passt zu Lauras erster Nachricht? Begründe deine Annahme.','Welche Empfehlung vertrittst du jetzt?','Wäge zwei Anliegen mit biologischen Gründen ab. Unter welcher Bedingung wäre ein anderer Rat vertretbar?')},
'08':{
'Förder':('Welche Nachricht hilft Laura zuerst? Mutter, Freundin, beide oder noch unsicher? Mein Grund: … Stichworte reichen.','Welche Nachricht hilft Laura jetzt?','Ich denke … Laura ist … wichtig. Der geprüfte Fakt zeigt …'),
'ESA':('Welche Nachricht findest du für Laura hilfreich? Warum?','Welche Nachricht hilft Laura jetzt besonders?','Ich finde …, weil Laura … Der Fakt … erklärt …'),
'MSA':('Welche Nachricht hilft Laura zunächst? Nenne deinen ersten Grund.','Welche ergänzte Nachricht hilft Laura jetzt besonders?','Verbinde ein Anliegen mit einem geprüften Fakt. Was bleibt für Laura offen?'),
'AHR':('Wie schätzt du die beiden Ratschläge zunächst ein? Begründe kurz.','Wie bewertest du die ergänzten Ratschläge jetzt?','Wäge die Anliegen und die Reichweite der biologischen Informationen ab. Begründe auch eine mögliche Unsicherheit.')}
}
ZEIT={'02':[('Ersten Rat mit eigenem Grund eingeben',5),('Erste Abstimmung am Empfehlungsrad',3),('Digitales Beratungsgespräch',20),('Schlussrat und Grund eingeben',5),('Zweites Empfehlungsrad und Vergleich der Gründe',9),('Reflexion',3)],
'08':[('Zwei Ratschläge lesen und erste Einschätzung begründen',7),('Digitale Analyse und Abwägung',22),('Abschließende Einschätzung begründen',5),('Vergleich von Einschätzung und geprüftem Fakt',8),('Reflexion',3)]}

def vertrag(day,bank):
    result=dict(tag=day+'12',format='Erste und letzte Antwort mit eigenem Grund stehen auf dem Gerät. Beide bleiben für den Vergleich in der geöffneten Sitzung erhalten.',niveaus={},phasen=ZEIT[day])
    for tier,(start,end,stem) in KARTEN[day].items():
        result['niveaus'][tier]={'einstieg':{'titel':'Mein erster Rat' if day=='02' else 'Meine erste Einschätzung','auftrag':start,'funktion':'Individuellen Ausgangspunkt vor der digitalen Arbeit festhalten.'},'abschluss':{'titel':'Mein Schlussrat' if day=='02' else 'Meine begründete Einschätzung','auftrag':end,'hilfe':stem,'funktion':'Eigenen abschließenden Grund einmal individuell formulieren.'}}
    if day=='02':
        result['einstiegstext']=bank['opening'];result['empfehlungsraeder']={'vorher':['Kondom','Kombinationspille','Kupferspirale','Hormonspirale'],'nachher':['Kondom','Kombinationspille','Kupferspirale','Hormonspirale','Kondom + weitere Methode'],'satz':'Zwei getrennte Druckvorlagen mit ausgeschriebenen Feldern und Platz für je 28 Markierungen. Bei einer Kombination wird die zusätzliche Methode im persönlichen Schlussrat genannt.'}
        result['sicherung']='Beide Empfehlungsräder betrachten. Ersten und letzten Rat mit ihren Gründen vergleichen. Auch bei derselben Methode kann die Begründung genauer geworden sein.'
    else:
        result['einstiegstext']={k:bank['cases'][k]['lesefassung'] for k in ('Mutter','Freundin')}
        result['sicherung']='Erste und abschließende Einschätzung vergleichen. Neben jeden Originalrat die erarbeitete biologische Ergänzung legen. In einem Grund den Bezug zwischen Anliegen und Fakt zeigen. Mutter, Freundin, beide und begründete Unsicherheit sind möglich. Laura entscheidet selbst.'
    result['erarbeitung']='Ausschließlich digital.'+(' Die vorbereiteten Infokarten können freiwillig genutzt werden. Alle benötigten Abschnitte stehen im Programm.' if day=='02' else '')
    result['unterbrechung']='Beim Zeichen „Stundenabschluss“ öffnen alle die persönliche Abschlussaufgabe. Die Fallinformationen sind auch bei frühem Stopp zugänglich. Offene Arbeit wird nicht als bestanden gewertet.'
    return result
