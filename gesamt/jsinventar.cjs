// Node enthält Acorn. Im Prüfprozess mit --expose-internals ausführen.
const fs = require('node:fs');
const {parse} = require('internal/deps/acorn/acorn/dist/acorn');
const input = JSON.parse(fs.readFileSync(0,'utf8'));
const output = {};
const helpers = new Set(['element','el','btn','button','control','add','appendMessage','paragraph','go']);
const technicalParameters = new Set(['tag','id','cls','action','kind','type']);
const technicalProperties = new Set(['id','className','type','autocomplete','autocapitalize','inputMode','role']);

function children(node) {
  return Object.values(node).flat().filter(value => value && typeof value.type === 'string');
}

for (const [key,source] of Object.entries(input)) {
  const root=parse(source,{ecmaVersion:'latest',locations:true});
  const names=new Map();
  function declarations(node) {
    if(node.type==='FunctionDeclaration' && helpers.has(node.id.name)){
      // Mehrdeutige lokale Hilfsfunktionen sind kein belastbarer Verwendungsbeleg.
      const args=node.params.map(p=>p.name || p.left?.name);
      names.set(node.id.name,names.has(node.id.name)?[]:args);
    }
    children(node).forEach(declarations);
  }
  declarations(root);
  function technicalRole(node,parent) {
    if(parent?.type==='BinaryExpression' && ['===','!==','==','!='].includes(parent.operator))return 'Vergleichswert im Kontrollfluss';
    if(parent?.type==='SwitchCase' && parent.test===node)return 'Fallunterscheidung im Kontrollfluss';
    if(parent?.type==='AssignmentExpression' && parent.right===node && technicalProperties.has(parent.left.property?.name))return 'DOM-Kennung oder technische Eigenschaft';
    if(parent?.type!=='CallExpression')return '';
    const index=parent.arguments.indexOf(node);
    if(index<0)return '';
    if(parent.callee.type==='Identifier'){
      const arg=names.get(parent.callee.name)?.[index];
      if(technicalParameters.has(arg))return 'Technischer Parameter '+arg+' von '+parent.callee.name;
    }
    if(index!==0)return '';
    const operation=parent.callee.property?.name || parent.callee.name;
    if(['getElementById','querySelector','querySelectorAll','closest','matches'].includes(operation))return 'DOM-Element suchen';
    if(['addEventListener','removeEventListener'].includes(operation))return 'Ereignisname';
    if(['createElement','createElementNS'].includes(operation))return 'HTML-Element oder XML-Namensraum';
    if(['getAttribute','setAttribute','removeAttribute','hasAttribute','toggleAttribute'].includes(operation))return 'Attributname';
    return '';
  }
  const rows=[];
  function visit(node,parent) {
    if(node.type==='Literal' && typeof node.value==='string' || node.type==='TemplateLiteral'){
      rows.push({stelle:'Z'+node.loc.start.line+':'+(node.loc.start.column+1),typ:node.type==='Literal'?'JS-Literal':'JS-Template',
        rolle:technicalRole(node,parent),text:node.type==='Literal'?node.value:source.slice(node.start,node.end)});
    }
    children(node).forEach(child=>visit(child,node));
  }
  visit(root);
  output[key]=rows;
}
process.stdout.write(JSON.stringify(output));
