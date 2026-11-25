"""Read the printed learner and reference PDFs independently of the application data."""
import re
import subprocess
from tempfile import TemporaryDirectory
from pathlib import Path
from zipfile import ZipFile

from auslieferung import PRINT, sha

LEVELS={'Foerder':'Förder','ESA':'ESA','MSA':'MSA','AHR':'AHR'}
METHODS={'K':'Kondom','P':'Kombinationspille','Cu':'Kupferspirale','H':'Hormonspirale'}
NUM=re.compile(r'(?<!\S)([1-4])(?=\s|$)')

def spaced(text):
    return ' '.join(text.split())

def pdf_cards(pdf,level):
    pages=subprocess.check_output(['pdftotext','-layout',str(pdf),'-']).decode().split('\f')
    result={}
    for n,page in enumerate(pages[:2],1):
        titles=list(re.finditer(r'^(Kondom|Kombinationspille|Kupferspirale|Hormonspirale)[ \t]+'+level+r'[ \t]*$',page,re.M))
        assert len(titles)==2,(pdf,n)
        for i,match in enumerate(titles):
            stop=titles[i+1].start() if i==0 else len(page)
            body=page[match.end():stop].strip()
            assert [m[1] for m in NUM.finditer(body)]==list('1234'),(pdf,n,body)
            result[match[1]]=(n,body)
    assert list(result)==list(METHODS.values())
    return result

def printed():
    out={}
    with ZipFile(PRINT) as z,TemporaryDirectory() as tmp:
        assert z.testzip() is None
        for level,display in LEVELS.items():
            pair=[]
            for name in (f'01_Schuelermaterial/Infokarten_{level}.pdf',f'02_Lehrkraft/Referenzkarten/Referenzkarten_{level}.pdf'):
                path=Path(tmp)/Path(name).name
                data=z.read(name);path.write_bytes(data)
                pair.append((pdf_cards(path,display),sha(data)))
            (student,hs),(reference,hr)=pair
            for key,title in METHODS.items():
                n,blank=student[title]
                nr,filled=reference[title]
                assert n==nr
                out[level,key]=dict(title=title,page=n,blank=blank,reference=filled,student_sha256=hs,reference_sha256=hr)
    return out

def compare(paper,entries,ways):
    assert [f['number'] for f in entries]==list(range(1,5))
    def insert(m):
        return m[1]+' '+entries[int(m[1])-1]['answer']
    numbered=NUM.sub(insert,paper['blank'])
    # Poppler positions a printed punctuation mark beyond the handwriting line.
    normalized=lambda s:re.sub(r' +([,.;:])',r'\1',spaced(s))
    reference=normalized(paper['reference'])
    assert normalized(numbered)==reference,(paper['title'],normalized(numbered),reference)
    full=paper['title']+' '+normalized(NUM.sub('',numbered))
    for route,card in ways.items():
        assert card['fields']==entries,(route,card['fields'],entries)
        assert spaced(card['text'])==full,(route,paper['title'],spaced(card['text']),full)
    return sha(full.encode())
