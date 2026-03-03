(function () {
  var REMOTE_LINKS = {
    home: 'https://architecture-stack.vercel.app',
    ios: 'https://architecture-stack.vercel.app/ios/index.html',
    android: 'https://architecture-stack-android.vercel.app',
    sdd: 'https://architecture-stack-sdd.vercel.app'
  };
  var AUTH_USER_KEY = 'sma:auth:user:v1';
  var AUTH_SESSION_KEY = 'sma:auth:session:v1';
  var CLOUD_PROFILE_KEY = 'sma:cloud:profile:v1';

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

  function isLocalContext() {
    var host = String(window.location.hostname || '').toLowerCase();
    if (window.location.protocol === 'file:') return true;
    if (!host) return false;
    if (host === 'localhost' || host === '127.0.0.1' || host === '::1' || host === '0.0.0.0') return true;
    if (host.endsWith('.local')) return true;
    if (/^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(host)) return true;
    if (/^192\.168\.\d{1,3}\.\d{1,3}$/.test(host)) return true;
    var private172 = host.match(/^172\.(\d{1,3})\.\d{1,3}\.\d{1,3}$/);
    if (private172) {
      var secondOctet = Number(private172[1]);
      if (Number.isFinite(secondOctet) && secondOctet >= 16 && secondOctet <= 31) return true;
    }
    return false;
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

  function appendQueryParam(url, key, value) {
    if (!url || !key || !value) return url;
    try {
      var target = new URL(url, window.location.href);
      target.searchParams.set(key, value);
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

  function readJsonStorage(key) {
    try {
      var raw = localStorage.getItem(key);
      if (!raw) return null;
      var parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== 'object') return null;
      return parsed;
    } catch (_error) {
      return null;
    }
  }

  function readStoredAuthUser() {
    var user = readJsonStorage(AUTH_USER_KEY);
    if (!user || !user.id) return null;
    return user;
  }

  function readStoredAuthSession() {
    var session = readJsonStorage(AUTH_SESSION_KEY);
    if (!session || !session.accessToken) return null;
    return session;
  }

  function hasValidSession(session) {
    if (!session || !session.accessToken) return false;
    if (!session.expiresAt) return true;
    var expiresAt = Date.parse(String(session.expiresAt));
    if (!Number.isFinite(expiresAt)) return true;
    return expiresAt > Date.now();
  }

  function clearStoredAuth() {
    localStorage.removeItem(AUTH_USER_KEY);
    localStorage.removeItem(AUTH_SESSION_KEY);
    localStorage.removeItem(CLOUD_PROFILE_KEY);
  }

  function hasAuthenticatedUser() {
    var user = readStoredAuthUser();
    var session = readStoredAuthSession();
    if (!user || !hasValidSession(session)) {
      clearStoredAuth();
      return false;
    }
    return true;
  }

  function resolveCurrentPath() {
    return window.location.pathname + window.location.search + window.location.hash;
  }

  function sanitizeNextPath(path) {
    try {
      var target = new URL(path || resolveCurrentPath(), window.location.origin);
      ['progressProfile', 'progressBase', 'progressEndpoint'].forEach(function (key) {
        target.searchParams.delete(key);
      });
      return target.pathname + target.search + target.hash;
    } catch (_error) {
      return '/index.html';
    }
  }

  function resolveLoginUrl(syncParams, nextPath) {
    var base = resolveCourseLink('/auth/login.html', REMOTE_LINKS.home + '/auth/login.html', syncParams);
    return appendQueryParam(base, 'next', nextPath || '/index.html');
  }

  function enforceAuthenticatedAccess(syncParams) {
    if (isLocalContext()) return true;
    if (hasAuthenticatedUser()) return true;
    var loginUrl = resolveLoginUrl(new URLSearchParams(), sanitizeNextPath(resolveCurrentPath()));
    window.location.replace(loginUrl);
    return false;
  }

  function setLinks(syncParams) {
    var home = document.getElementById('course-switcher-home');
    var ios = document.getElementById('course-switcher-ios');
    var android = document.getElementById('course-switcher-android');
    var sdd = document.getElementById('course-switcher-sdd');
    if (!home || !ios || !android) return;

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
      clearStoredAuth();
      if (isLocalContext()) {
        window.location.href = resolveCourseLink('/index.html', REMOTE_LINKS.home, new URLSearchParams());
        return;
      }
      window.location.href = resolveLoginUrl(new URLSearchParams(), '/index.html');
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

  var syncParams = collectSyncParams();
  if (!enforceAuthenticatedAccess(syncParams)) return;
  setLinks(syncParams);
  setupToggle();
})();
