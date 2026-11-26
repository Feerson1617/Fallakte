// Prüfe jede angebotene Taste mit der tatsächlichen Position auf allen Teilansichten.
() => {
  const result={screens:0,checks:0,issues:[]};
  const known=new Set();
  function hit(node,field){
    const r=node.getBoundingClientRect(),b=field?.getBoundingClientRect();
    if(b && (r.x<b.x-1||r.right>b.right+1||r.top<b.top-1||r.bottom>b.bottom+1))return false;
    const x=r.x+r.width/2,y=r.y+r.height/2;
    return r.width>=43.5 && r.height>=43.5 && node.contains(document.elementFromPoint(x,y));
  }
  window.geometrie=(key,root)=>{
    if(known.has(key))return;known.add(key);result.screens++;
    Arbeitsplatz.refresh();
    const sheet=root.querySelector('.blatt'),f=sheet?.querySelector(':scope > .blatt-inhalt');
    const controls=[...root.querySelectorAll('button,summary,textarea,select')].filter(n=>{
      if(!n.getClientRects().length || n.disabled)return false;
      for(let d=n.parentElement;d;d=d.parentElement)if(d.matches('details:not([open])') && d.querySelector(':scope > summary')!==n)return false;return true;
    });
    const missing=new Set(controls.filter(n=>!n.closest('.gespraech,.blatt-wechsel')));
    const pager=sheet?.querySelector(':scope > .blatt-wechsel');
    const before=f?.scrollLeft||0;
    const positions=new Map();
    const inspect=()=>{for(const n of [...missing]){
      if(hit(n,n.closest('.blatt-inhalt'))){missing.delete(n);continue;}
      const r=n.getBoundingClientRect(),b=f?.getBoundingClientRect(),who=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);
      const arr=positions.get(n)||[];arr.push([Math.round(r.x),Math.round(r.y),Math.round(r.right),Math.round(r.bottom),Math.round(b?.left),Math.round(b?.top),Math.round(b?.right),Math.round(b?.bottom),who?.id||who?.tagName]);
      positions.set(n,arr);
    }};
    if(pager && !pager.hidden && f){
      const prev=pager.firstElementChild,next=pager.lastElementChild;
      let steps=0;while(!prev.disabled && steps++<100)prev.click();
      inspect();steps=0;
      while(!next.disabled && steps++<100){next.click();inspect();}
      while(!prev.disabled && f.scrollLeft>before+1)prev.click();
    }else inspect();
    result.checks+=controls.length;
    for(const n of missing)result.issues.push({key:key.slice(0,90),id:n.id,text:n.textContent.trim().slice(0,120),size:[n.offsetWidth,n.offsetHeight],positions:positions.get(n)});
  };
  window.geometrieStand=()=>result;
}
