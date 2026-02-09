(function () {
  function deriveHubBase() {
    var href = window.location.href;
    if (href.indexOf('/ios/') !== -1) return href.split('/ios/')[0];
    if (href.indexOf('/android/') !== -1) return href.split('/android/')[0];
    return '';
  }

  function withFileSchemeIfNeeded(path) {
    var base = deriveHubBase();
    if (!base) return path;
    return base + path;
  }

  function setLinks() {
    var home = document.getElementById('course-switcher-home');
    var ios = document.getElementById('course-switcher-ios');
    var android = document.getElementById('course-switcher-android');
    if (!home || !ios || !android) return;
    home.href = withFileSchemeIfNeeded('/index.html');
    ios.href = withFileSchemeIfNeeded('/ios/index.html');
    android.href = withFileSchemeIfNeeded('/android/index.html');
    home.textContent = '🏠 Hub';
    ios.textContent = '📱 Curso iOS';
    android.textContent = '🤖 Curso Android';
  }

  function setupToggle() {
    var toggle = document.getElementById('course-switcher-toggle');
    var menu = document.getElementById('course-switcher-menu');
    if (!toggle || !menu) return;

    toggle.textContent = '☰ Cursos';
    toggle.title = 'Cambiar entre Hub, iOS y Android';

    toggle.addEventListener('click', function (event) {
      event.stopPropagation();
      var isHidden = menu.hasAttribute('hidden');
      if (isHidden) menu.removeAttribute('hidden');
      else menu.setAttribute('hidden', 'hidden');
    });

    document.addEventListener('click', function () {
      if (!menu.hasAttribute('hidden')) menu.setAttribute('hidden', 'hidden');
    });

    menu.addEventListener('click', function (event) {
      event.stopPropagation();
    });
  }

  setLinks();
  setupToggle();
})();
