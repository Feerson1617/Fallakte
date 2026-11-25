// Node enthält Acorn. Im Prüfprozess mit --expose-internals ausführen.
const fs = require('node:fs');
const {parse} = require('internal/deps/acorn/acorn/dist/acorn');
const input = JSON.parse(fs.readFileSync(0,'utf8'));
const output = {};
for (const [key,source] of Object.entries(input)) {
  const rows=[];
  function technicalRole(node, parent) {
    if (parent?.type !== 'CallExpression' || parent.arguments[0] !== node) return '';
    const operation = parent.callee.property?.name || parent.callee.name;
    if (['getElementById','querySelector','querySelectorAll','closest','matches'].includes(operation)) return 'DOM-Element suchen';
    if (['addEventListener','removeEventListener'].includes(operation)) return 'Ereignisname';
    if (['createElement','createElementNS'].includes(operation)) return 'HTML-Element oder XML-Namensraum';
    if (['getAttribute','setAttribute','removeAttribute','hasAttribute','toggleAttribute'].includes(operation)) return 'Attributname';
    return '';
  }
  function visit(n,parent){
    if(!n || typeof n!=='object')return;
    if(n.type==='Literal' && typeof n.value==='string' || n.type==='TemplateLiteral'){
      rows.push({stelle:'Z'+n.loc.start.line+':'+(n.loc.start.column+1),typ:n.type==='Literal'?'JS-Literal':'JS-Template',
                 rolle:technicalRole(n,parent),text:n.type==='Literal'?n.value:source.slice(n.start,n.end)});
    }
    for(const value of Object.values(n))if(Array.isArray(value))value.forEach(child=>visit(child,n));else if(value?.type)visit(value,n);
  }
  visit(parse(source,{ecmaVersion:'latest',locations:true}));output[key]=rows;
}
process.stdout.write(JSON.stringify(output));
