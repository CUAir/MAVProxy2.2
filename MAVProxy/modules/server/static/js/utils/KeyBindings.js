var keyqueue = [];

function addKey({keycode, scope, action}) {
  window.key.unbind(keycode, scope);
  window.key(keycode, scope, action);
}

export function initKeyBindings() {
  window.key.filter = function(event) {
    var tagName = (event.target || event.srcElement).tagName;
    return !(tagName == 'INPUT' || tagName == 'SELECT' || tagName == 'TEXTAREA' || tagName == 'BUTTON');
  };
  keyqueue.forEach(addKey);
  keyqueue = [];
  window.key.setScope('home');
}

export function addKeyBindings(keybindings) {
  if (window.key) {
    keybindings.forEach(addKey);
  } else {
    // key not initialized yet, add to keyqueue
    keyqueue.push.apply(keyqueue, keybindings);
  }
}

export function setScope(scope: string) {
  window.key.setScope(scope);
}

