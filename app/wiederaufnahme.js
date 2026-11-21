'use strict';

// Cases supply their own ordered stages. The caller owns navigation and session state.
function renderRecovery(root, cases, levels, start) {
  root.replaceChildren();
  let person=Object.keys(cases)[0];
  let tier;

  function group(legend) {
    const field=el('fieldset');
    const choices=el('div','recovery-options');
    field.append(el('legend','',legend),choices);
    root.append(field);
    return choices;
  }
  function select(group, selected) {
    for (const b of group.children) b.setAttribute('aria-pressed',b===selected);
  }
  const people=group('Welcher Fall?');
  const tiers=group('Welches Niveau steht auf deinem Laufzettel?');
  const steps=group('Welche Nummer hast du markiert?');
  function drawSteps() {
    steps.parentElement.hidden=!tier;
    steps.replaceChildren();
    if (!tier) return;
    cases[person].forEach((stage,index)=>{
      const label=person+' '+(index+1)+' – '+(stage.resumeTitle || stage.title);
      steps.append(button(label,()=>start(person,tier,index),'outline'));
    });
  }
  for (const name of Object.keys(cases)) {
    const b=button(name,()=>{
      person=name;
      select(people,b);
      drawSteps();
    },'outline');
    b.setAttribute('aria-pressed',name===person);
    people.append(b);
  }
  for (const [key,label] of Object.entries(levels)) {
    const b=button(label,()=>{
      tier=key;
      select(tiers,b);
      drawSteps();
    },'outline');
    b.setAttribute('aria-pressed','false');
    tiers.append(b);
  }
  drawSteps();
}
