(function () {
  var REMOTE_LINKS = {
    home: 'https://architecture-stack.vercel.app',
    ios: 'https://architecture-stack.vercel.app/ios/index.html',
    android: 'https://architecture-stack-android.vercel.app',
    sdd: 'https://architecture-stack-sdd.vercel.app'
  };
  var AUTH_USER_KEY = 'sma:auth:user:v1';
  var AUTH_SESSION_KEY = 'sma:auth:session:v1';

  function deriveHubBase() {
    var href = window.location.href;
    if (href.indexOf('/ios/') !== -1) return href.split('/ios/')[0];
    if (href.indexOf('/android/') !== -1) return href.split('/android/')[0];
    if (href.indexOf('/sdd/') !== -1) return href.split('/sdd/')[0];
    return '';
  }

  function isWebContext() {
    return window.location.protocol === 'http:' || window.location.protocol === 'https:';
  }

  function collectSyncParams() {
    var source = new URLSearchParams(window.location.search || '');
    var keep = new URLSearchParams();
    ['progressProfile', 'progressBase', 'progressEndpoint'].forEach(function (key) {
      var value = source.get(key);
      if (value) keep.set(key, value);
    });
    return keep;
  }

  function appendSyncParams(url, params) {
    if (!url || !params || Array.from(params.keys()).length === 0) return url;
    try {
      var target = new URL(url, window.location.href);
      params.forEach(function (value, key) {
        if (!target.searchParams.has(key)) target.searchParams.set(key, value);
      });
      if (/^[a-zA-Z][a-zA-Z\d+\-.]*:/.test(url)) return target.toString();
      return target.pathname + target.search + target.hash;
    } catch (_error) {
      return url;
    }
  }

  function resolveCourseLink(path, remoteFallback, syncParams) {
    var base = deriveHubBase();
    if (base) return appendSyncParams(base + path, syncParams);
    if (isWebContext()) return appendSyncParams(remoteFallback, syncParams);
    return appendSyncParams(path, syncParams);
  }

  function setLinks() {
    var home = document.getElementById('course-switcher-home');
    var ios = document.getElementById('course-switcher-ios');
    var android = document.getElementById('course-switcher-android');
    var sdd = document.getElementById('course-switcher-sdd');
    if (!home || !ios || !android) return;

    var syncParams = collectSyncParams();
    home.href = resolveCourseLink('/index.html', REMOTE_LINKS.home, syncParams);
    ios.href = resolveCourseLink('/ios/index.html', REMOTE_LINKS.ios, syncParams);
    android.href = resolveCourseLink('/android/index.html', REMOTE_LINKS.android, syncParams);
    if (sdd) sdd.href = resolveCourseLink('/sdd/index.html', REMOTE_LINKS.sdd, syncParams);

    home.textContent = '🏠 Cursos';
    ios.textContent = '📱 Curso iOS';
    android.textContent = '🤖 Curso Android';
    if (sdd) sdd.textContent = '🧠 Curso IA + SDD';
    setAuthLinks(syncParams);
  }

  function setAuthLinks(syncParams) {
    var menu = document.getElementById('course-switcher-menu');
    if (!menu) return;
    var user = readStoredAuthUser();
    var authUrl = resolveCourseLink('/auth/index.html', REMOTE_LINKS.home + '/auth/index.html', syncParams);

    var authLink = ensureMenuLink(menu, 'course-switcher-auth');
    authLink.href = authUrl;
    authLink.textContent = user && user.id
      ? '👤 ' + String(user.email || 'Cuenta')
      : '🔐 Registro / Login';

    var logoutLink = ensureMenuLink(menu, 'course-switcher-logout');
    logoutLink.href = '#';
    logoutLink.textContent = '🚪 Cerrar sesión';
    logoutLink.style.display = user && user.id ? '' : 'none';
    logoutLink.onclick = function (event) {
      event.preventDefault();
      localStorage.removeItem(AUTH_USER_KEY);
      localStorage.removeItem(AUTH_SESSION_KEY);
      window.location.href = authUrl;
    };
  }

  function ensureMenuLink(menu, id) {
    var link = document.getElementById(id);
    if (link) return link;
    var li = document.createElement('li');
    link = document.createElement('a');
    link.id = id;
    li.appendChild(link);
    menu.appendChild(li);
    return link;
  }

  function readStoredAuthUser() {
    try {
      var raw = localStorage.getItem(AUTH_USER_KEY);
      if (!raw) return null;
      var parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== 'object') return null;
      if (!parsed.id) return null;
      return parsed;
    } catch (_error) {
      return null;
    }
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
