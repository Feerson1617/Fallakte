"""Die unveränderten Vorbereitungsdateien der früheren Auslieferungen beilegen."""
import argparse
from pathlib import Path
from auslieferung import OUT,PREP,pack,rebuild,sha

VERSIONEN=(
    ('Fallakte-Sprachpruefung-3565a45','3565a45d8688ce002b29dcb2dd04b54750e187f0','Fallakte-Vorbereitung',
     '2e0caf45c2573087203df09a9a078404870d7089697e92a0ab3672f3a2e34c10','03c4220a989aee03b8f42c914af421b58c2048ab71f955b4ae0675ba49f8b4f3'),
    ('Fallakte-Gesamt-f5fa5db','f5fa5db2cd6fe076c7c435b39b8b6485837aa2a2','Fallakte-Vorbereitung',
     '51b6e9edf5a072eef8eadaebd8bd650d3274c625b4825590af0180fb3de82a64','61e07293f5836cc1393f561263d1a959f8c02cb84119d06203febbb6f7028487'),
    ('Vorbereitung-7f26cd7',PREP,'Vorbereitung',
     '5478c3c93d80ed5c3b368257a2754f5e585eefd63c9fd3cc74860b93bd75d49b','c57b54d3190cb82e281d80b30a24b0d1b3ac9cde3a052e50beedf578ac126963'),
)

def run(archiv):
    files={};hashes=[]
    for name,commit,base,html,scorm in VERSIONEN:
        if archiv:
            folder=archiv/name
        elif commit==PREP:
            folder=rebuild(commit,'vorbereitung/bauen.py','Vorbereitung')
        else:
            folder=rebuild(commit,'gesamt/auslieferung.py','Gesamt')
        for suffix,checksum in [('.html',html),('-SCORM12.zip',scorm)]:
            path=name+'/'+base+suffix
            raw=(folder/(base+suffix)).read_bytes()
            assert sha(raw)==checksum,path
            files[path]=raw;hashes.append(checksum+'  '+path)
    files['SHA256SUMS']='\n'.join(hashes)+'\n'
    files['Liesmich.md']='# Rückfallversionen der Vorbereitung\n\nDer Ordner mit 3565a45 enthält die zuletzt ausgelieferte Sprachfassung. f5fa5db ist die frühere integrierte Fassung. 7f26cd7 ist die eigenständig nutzbare ursprüngliche Vorbereitung. Jedes Verzeichnis enthält eine Offline-Datei sowie das zugehörige SCORM-Paket. Die Prüfsummen stimmen mit den damaligen Auslieferungsnachweisen überein.\n'
    pack(OUT/'Rueckfall-Vorbereitung.zip',files)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--archiv',type=Path);run(p.parse_args().archiv)
