(function () {
  if (window.__smaThemeControlsInitialized) return;
  window.__smaThemeControlsInitialized = true;

  function getPreferredTheme() {
    const saved = localStorage.getItem('course-theme');
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function getPreferredStyle() {
    return localStorage.getItem('course-style') || 'enterprise';
  }

  function getPreferredCodeTheme() {
    return localStorage.getItem('course-code-theme') || 'monokai';
  }

  function applyStyle(style) {
    document.documentElement.setAttribute('data-style', style);
    localStorage.setItem('course-style', style);
    const btn = document.getElementById('style-cycle-btn');
    if (btn) btn.textContent = 'Estilo: ' + style.charAt(0).toUpperCase() + style.slice(1);
  }

  function cycleStyle() {
    const styles = ['enterprise', 'bold', 'paper'];
    const current = document.documentElement.getAttribute('data-style') || 'enterprise';
    const next = styles[(styles.indexOf(current) + 1) % styles.length];
    applyStyle(next);
    rerenderMermaidSafely();
  }

  function applyCodeTheme(theme) {
    localStorage.setItem('course-code-theme', theme);
    document.documentElement.setAttribute('data-code-theme', theme);
    var btn = document.getElementById('code-theme-cycle-btn');
    if (btn) btn.textContent = 'Codigo: ' + theme.charAt(0).toUpperCase() + theme.slice(1).replace(/-/g, ' ');

    rehighlightAll();
  }

  function rehighlightAll() {
    if (!window.hljs) return;
    document.querySelectorAll('pre code[data-highlighted]').forEach(function (block) {
      block.removeAttribute('data-highlighted');
      window.hljs.highlightElement(block);
    });
  }

  function cycleCodeTheme() {
    const themes = ['monokai', 'github', 'github-dark', 'atom-one-dark'];
    const current = localStorage.getItem('course-code-theme') || 'monokai';
    const next = themes[(themes.indexOf(current) + 1) % themes.length];
    applyCodeTheme(next);
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('course-theme', theme);
    const btn = document.getElementById('theme-toggle');
    if (btn) {
      btn.textContent = theme === 'dark' ? 'Tema: Oscuro' : 'Tema: Claro';
      btn.title = theme === 'dark' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro';
    }
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    applyTheme(current === 'dark' ? 'light' : 'dark');
    rerenderMermaidSafely();
  }

  function currentMermaidTheme() {
    const theme = document.documentElement.getAttribute('data-theme') || 'light';
    return theme === 'dark' ? 'dark' : 'default';
  }

  function rerenderMermaidSafely() {
    if (typeof mermaid === 'undefined') return;

    var blocks = document.querySelectorAll('pre.mermaid');
    blocks.forEach(function (el) {
      var original = el.dataset.originalMermaid;
      if (!original) return;
      el.innerHTML = '';
      el.textContent = original;
      el.removeAttribute('data-processed');
    });

    try {
      mermaid.initialize({ startOnLoad: false, theme: currentMermaidTheme(), securityLevel: 'loose' });
      mermaid.run({ querySelector: 'pre.mermaid' }).catch(function () {});
    } catch (e) {}
  }

  window.applyStyle = applyStyle;
  window.cycleStyle = cycleStyle;
  window.applyCodeTheme = applyCodeTheme;
  window.cycleCodeTheme = cycleCodeTheme;
  window.applyTheme = applyTheme;
  window.toggleTheme = toggleTheme;

  applyStyle(getPreferredStyle());
  applyCodeTheme(getPreferredCodeTheme());
  applyTheme(getPreferredTheme());
})();
