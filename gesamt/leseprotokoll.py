"""Playwright-Beobachtung ohne Instrumentierung der ausgelieferten Schüleranwendung."""
import gzip,json
from pathlib import Path
from playwright.sync_api import Browser,Page
from auslieferung import QA,SRC

class Aufzeichnung:
    def __init__(self,name):
        self.path=QA/(name+'.jsonl.gz')
        self.seen=set()
    def __enter__(self):
        self.out=gzip.open(self.path,'wt',encoding='utf-8')
        self.old=Page.goto
        writer=self
        def goto(page,*args,**kwargs):
            if not getattr(page,'_sprachscan',False):
                page._sprachscan=True
                page.expose_binding('protokoll',lambda _,rows:writer.add(rows))
                page.add_init_script(path=SRC/'leseprotokoll.js')
            else:writer.flush(page)
            return writer.old(page,*args,**kwargs)
        self.close=Page.close
        def close(page,*args,**kwargs):
            writer.flush(page)
            return writer.close(page,*args,**kwargs)
        Page.close=close;Page.goto=goto
        return self
    def add(self,rows):
        for r in rows:
            s=json.dumps(r,ensure_ascii=False,separators=(',',':'))
            if s in self.seen:continue
            self.seen.add(s);self.out.write(s+'\n')
    def flush(self,page):
        for frame in page.frames:
            if not frame.is_detached():
                frame.evaluate('window.auditFlush?.()')
    def __exit__(self,*exc):
        Page.goto=self.old;Page.close=self.close;self.out.close()
