// Node enthält Acorn. Im Prüfprozess mit --expose-internals ausführen.
const fs = require('node:fs');
const {parse} = require('internal/deps/acorn/acorn/dist/acorn');
const input = JSON.parse(fs.readFileSync(0,'utf8'));
const output = {};
for (const [key,source] of Object.entries(input)) {
  const rows=[];
  function visit(n){
    if(!n || typeof n!=='object')return;
    if(n.type==='Literal' && typeof n.value==='string' || n.type==='TemplateLiteral'){
      rows.push({stelle:'Z'+n.loc.start.line+':'+(n.loc.start.column+1),typ:n.type==='Literal'?'JS-Literal':'JS-Template',
                 text:n.type==='Literal'?n.value:source.slice(n.start,n.end)});
    }
    for(const value of Object.values(n))if(Array.isArray(value))value.forEach(visit);else if(value?.type)visit(value);
  }
  visit(parse(source,{ecmaVersion:'latest',locations:true}));output[key]=rows;
}
process.stdout.write(JSON.stringify(output));
