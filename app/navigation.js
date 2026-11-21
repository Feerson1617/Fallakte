// In a standalone file or an ordinary LMS frame, the original header owns navigation.
(() => {
  if (parent === window) return;
  const actions = [
    {id:'home', label:'Fallakten', icon:'folder'},
    {id:'resources', label:'Infokarten', icon:'book'},
    {id:'recovery', label:'Nach Neustart', icon:'restart'}
  ];
  let port;
  let recoveryOrigin;

  function publish() {
    port.postMessage({type:'view', active:screen, status:screen==='room'
      ? [$('step').textContent, $('room-level').textContent].filter(Boolean).join(' · ') : ''});
  }

  function navigate(action) {
    if (action === 'home') {
      home();
      $('level-title').tabIndex = -1;
      $('level-title').focus({preventScroll:true});
    } else if (action === 'resources') {
      openCards();
    } else if (action === 'recovery' && screen !== 'recovery') {
      if (screen === 'resources' && returnTo === 'recovery') {
        resume();
      } else {
        recoveryOrigin = {screen, returnTo};
        $('open-recovery').click();
      }
    }
  }

  function cancelRecovery() {
    if (recoveryOrigin?.screen === 'room') {
      openCase(current.person, current.level);
    } else if (recoveryOrigin?.screen === 'resources') {
      returnTo = recoveryOrigin.returnTo;
      show('resources');
      $('resources').querySelector('h1').focus({preventScroll:true});
    } else {
      navigate('home');
    }
  }

  const observer = new MutationObserver(publish);
  window.addEventListener('message', event => {
    if (event.source !== parent || event.data !== 'fallakte:navigation' || !event.ports[0]) return;
    port?.close();
    port = event.ports[0];
    port.onmessage = ({data}) => navigate(data);
    document.documentElement.classList.add('mit-tagesnavigation');
    // Keep the module's heading and focus target in its accessible conversation.
    $('room').prepend($('room-identity'));
    $('leave-recovery').textContent = 'Zurück';
    $('leave-recovery').onclick = cancelRecovery;
    for (const section of ['home','room','recovery','resources']) {
      observer.observe($(section), {attributes:true, attributeFilter:['hidden']});
    }
    for (const label of ['step','room-level']) {
      observer.observe($(label), {childList:true, subtree:true, characterData:true});
    }
    port.postMessage({type:'ready', actions});
    publish();
  });
})();
