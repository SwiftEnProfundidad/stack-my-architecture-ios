(function () {
  function deriveHubBase() {
    var href = window.location.href;
    if (href.indexOf('/ios/') !== -1) return href.split('/ios/')[0];
    if (href.indexOf('/android/') !== -1) return href.split('/android/')[0];
    if (href.indexOf('/sdd/') !== -1) return href.split('/sdd/')[0];
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
    var sdd = document.getElementById('course-switcher-sdd');
    if (!home || !ios || !android) return;
    home.href = withFileSchemeIfNeeded('/index.html');
    ios.href = withFileSchemeIfNeeded('/ios/index.html');
    android.href = withFileSchemeIfNeeded('/android/index.html');
    if (sdd) sdd.href = withFileSchemeIfNeeded('/sdd/index.html');
    home.textContent = '🏠 Cursos';
    ios.textContent = '📱 Curso iOS';
    android.textContent = '🤖 Curso Android';
    if (sdd) sdd.textContent = '🧠 Curso IA + SDD';
  }

  function setupToggle() {
    var toggle = document.getElementById('course-switcher-toggle');
    var menu = document.getElementById('course-switcher-menu');
    if (!menu) return;

    if (toggle) {
      toggle.addEventListener('click', function (e) {
        e.stopPropagation();
        menu.classList.toggle('open');
      });

      document.addEventListener('click', function () {
        menu.classList.remove('open');
      });

      menu.addEventListener('click', function (e) {
        e.stopPropagation();
      });
    }
  }

  setLinks();
  setupToggle();
})();
