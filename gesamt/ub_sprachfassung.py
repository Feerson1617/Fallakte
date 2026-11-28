"""Zwei Unterrichtstage getrennt von der eigenständig ausgelieferten Vorbereitung bauen."""
import argparse
import base64
from pathlib import Path
import re
import sys
from auslieferung import ROOT, OUT, JOINT, PAYLOAD, manifest, pack, rebuild, sha, single_replace
sys.path.insert(0,str(ROOT/'scripts'))
from modul_0212 import build as laura, commit
from familienrat_build import module_document

def bauen(joint):
    shell=(joint/'Fallakte.html').read_bytes()
    assert sha(shell)=='254e5d06cb9190250bacc63fa9eea6c118846b45ce2b305ffa640d766f44a820'
    shell=shell.decode()
    assert len(re.findall(PAYLOAD,shell))==2
    shell=re.sub(PAYLOAD,'',shell)
    shell=single_replace(shell,'id="zweiter-tag"','id="zweiter-tag" data-modulnavigation')
    shell=single_replace(shell,'</head>',f'<meta name="revision" content="{commit()}"></head>')
    shell=single_replace(shell,"entry.actions = data.actions;","entry.actions = data.actions; if(new URLSearchParams(location.search).has('lehrkraft'))entry.port.postMessage('lehrkraft');")
    shell=single_replace(shell,'</head>',"""<style>
      #tageshilfe{position:fixed;right:.45rem;top:2px;z-index:1;background:#ffdb69;color:#342b16;border:1px solid #a17812;border-radius:.5rem;min-height:44px;padding:.35em .65em;font:700 1rem/1.12 system-ui}
      #auswahl{padding-top:max(52px,4vh)}
      @media(max-height:660px){#auswahl header{padding:0;margin-bottom:.5rem;border:0}#auswahl .tag img{height:clamp(48px,calc((100dvh - 190px)*.9),260px);object-fit:contain}}
      @media(max-width:580px) and (max-height:660px){#auswahl .tag img{height:clamp(44px,calc((100dvh - 205px)/2),125px)}}
      @container(max-width:60rem){#tagesnavigation .wortmarke{display:none}}
      #arbeitsplatz{height:var(--sichtbar,100dvh)}
      #tageshinweis[hidden]{display:none}
      #tageshinweis{max-width:25rem;background:#fffdf7;color:#213c34;border:1px solid #aebbb2;border-radius:.5rem}
      #tageshinweis button{min-height:44px;font:inherit}
    </style></head>""")
    shell=single_replace(shell,'<header>',"""<button type="button" id="tageshilfe" aria-controls="tageshinweis">Ich brauche Hilfe</button>
      <div id="tageshinweis" hidden><p>Suche das Datum deiner Stunde. Tippe auf das Bild mit diesem Datum.</p><button type="button" id="auswahl-zurueck">Zurück zur Auswahl</button></div><header>""")
    shell=single_replace(shell,'</body>',"""<script>
      const dayHelp=document.querySelector('#tageshilfe'), instruction=document.querySelector('#tageshinweis');
      function orientation(open){
        instruction.hidden=!open;
        document.querySelector('.tage').hidden=open;
        document.querySelector('#auswahl header').hidden=open;
        dayHelp.setAttribute('aria-expanded',String(open));
        (open?document.querySelector('#auswahl-zurueck'):dayHelp).focus({preventScroll:true});
      }
      dayHelp.onclick=()=>orientation(instruction.hidden);
      document.querySelector('#auswahl-zurueck').onclick=()=>orientation(false);
      function fit(){
        let w=window,offset=0,end=Math.min(innerHeight,visualViewport?.height||innerHeight);
        try{while(w!==w.parent && w.frameElement){
          offset+=w.frameElement.getBoundingClientRect().top+w.frameElement.clientTop;w=w.parent;
          end=Math.min(end,(w.visualViewport?.height||w.innerHeight)-offset);
        }}catch{}
        document.documentElement.style.setProperty('--sichtbar',Math.max(1,end)+'px');
      }
      window.addEventListener('resize',fit);window.visualViewport?.addEventListener('resize',fit);
      try{if(parent!==window)parent.visualViewport?.addEventListener('resize',fit);}catch{}
      fit();
    </script></body>""")
    shell=single_replace(shell,'entry.active = data.active;', 'entry.abschluss = data.abschluss; entry.active = data.active;')
    shell=single_replace(shell,'if (button.dataset.action === entry.active)', "if(button.dataset.action==='abschluss')button.disabled=!entry.abschluss; if (button.dataset.action === entry.active)")
    days={'02':laura().read_bytes(),'08':module_document()[1].encode()}
    OUT.mkdir(parents=True,exist_ok=True)
    for version,allowed in [('02-12',['02']),('08-12',['02','08'])]:
        page=shell
        if '08' not in allowed:page=single_replace(page,'data-entry="modul-08"','disabled')
        embeds=''.join(f'<script id="modul-{day}" type="application/octet-stream">{base64.b64encode(days[day]).decode()}</script>' for day in allowed)
        raw=single_replace(page,'</body>',embeds+'</body>').encode()
        name='Fallakte-'+version
        (OUT/(name+'.html')).write_bytes(raw)
        schema={p.name:p.read_bytes() for p in (ROOT/'scorm').glob('*.xsd')}
        pack(OUT/(name+'-SCORM12.zip'),dict(schema,**{'index.html':raw,'imsmanifest.xml':manifest('FALLAKTE-'+version)}))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--unterricht',type=Path)
    args=parser.parse_args()
    bauen(args.unterricht or rebuild(JOINT,'scripts/familienrat_build.py','Familienrat'))
