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
    const btn = document.getElementById('code-theme-cycle-btn');
    if (btn) btn.textContent = 'Código: ' + theme.charAt(0).toUpperCase() + theme.slice(1).replace(/-/g, ' ');

    const hljsLink = document.getElementById('hljs-theme');
    if (hljsLink) {
      const themeMap = {
        monokai: 'monokai.min.css',
        github: 'github.min.css',
        'github-dark': 'github-dark.min.css',
        'atom-one-dark': 'atom-one-dark.min.css'
      };
      hljsLink.href = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/' + (themeMap[theme] || 'monokai.min.css');
    }

    if (window.hljs) {
      document.querySelectorAll('pre code').forEach(block => window.hljs.highlightElement(block));
    }
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

    const blocks = document.querySelectorAll('pre.mermaid');
    blocks.forEach((el) => {
      if (!el.dataset.originalMermaid) {
        el.dataset.originalMermaid = el.textContent || '';
      }
      el.textContent = el.dataset.originalMermaid;
      el.removeAttribute('data-processed');
    });

    mermaid.initialize({ startOnLoad: false, theme: currentMermaidTheme(), securityLevel: 'loose' });
    mermaid.run({ querySelector: 'pre.mermaid' });
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
