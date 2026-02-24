(function () {
  if (window.__smaThemeControlsInitialized) return;
  window.__smaThemeControlsInitialized = true;

  var THEME_VALUES = ['light', 'dark'];
  var STYLE_VALUES = ['enterprise', 'bold', 'paper'];
  var CODE_THEME_VALUES = ['monokai', 'github', 'github-dark', 'atom-one-dark'];

  var THEME_ALIASES = {
    light: 'light',
    dark: 'dark',
    claro: 'light',
    oscuro: 'dark'
  };

  var STYLE_ALIASES = {
    enterprise: 'enterprise',
    bold: 'bold',
    paper: 'paper'
  };

  var CODE_THEME_ALIASES = {
    monokai: 'monokai',
    github: 'github',
    'github-dark': 'github-dark',
    github_dark: 'github-dark',
    githubdark: 'github-dark',
    'atom-one-dark': 'atom-one-dark',
    atom_one_dark: 'atom-one-dark',
    atomonedark: 'atom-one-dark',
    'atom-one': 'atom-one-dark'
  };

  function normalizeStoredValue(value) {
    return String(value || '').trim().toLowerCase().replace(/\s+/g, '-');
  }

  function sanitizeChoice(value, allowed, aliases) {
    var normalized = normalizeStoredValue(value);
    if (!normalized) return null;
    var mapped = aliases[normalized] || normalized;
    return allowed.indexOf(mapped) >= 0 ? mapped : null;
  }

  function readStoredChoice(key, allowed, aliases) {
    var raw = localStorage.getItem(key);
    var clean = sanitizeChoice(raw, allowed, aliases);
    if (!clean) {
      if (raw) localStorage.removeItem(key);
      return null;
    }
    if (raw !== clean) localStorage.setItem(key, clean);
    return clean;
  }

  function resetVisualPreferences() {
    localStorage.removeItem('course-theme');
    localStorage.removeItem('course-style');
    localStorage.removeItem('course-code-theme');
  }

  function shouldResetVisualPreferencesFromQuery() {
    try {
      return new URLSearchParams(window.location.search).has('reset-ui');
    } catch (_) {
      return false;
    }
  }

  if (shouldResetVisualPreferencesFromQuery()) {
    resetVisualPreferences();
  }

  function getPreferredTheme() {
    var saved = readStoredChoice('course-theme', THEME_VALUES, THEME_ALIASES);
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function getPreferredStyle() {
    return readStoredChoice('course-style', STYLE_VALUES, STYLE_ALIASES) || 'enterprise';
  }

  function getPreferredCodeTheme() {
    return readStoredChoice('course-code-theme', CODE_THEME_VALUES, CODE_THEME_ALIASES) || 'monokai';
  }

  function activeTheme() {
    return sanitizeChoice(document.documentElement.getAttribute('data-theme'), THEME_VALUES, THEME_ALIASES) || 'light';
  }

  function activeStyle() {
    return sanitizeChoice(document.documentElement.getAttribute('data-style'), STYLE_VALUES, STYLE_ALIASES) || 'enterprise';
  }

  function readVar(name, fallback) {
    var value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return value || fallback;
  }

  function buildMermaidPalette() {
    var theme = activeTheme();
    var style = activeStyle();
    var accent = readVar('--accent', '#2563eb');
    var accentLight = readVar('--accent-light', accent);
    var accentDark = readVar('--accent-dark', accent);
    var bg = readVar('--bg', '#ffffff');
    var bgSurface = readVar('--bg-surface', bg);
    var bgElevated = readVar('--bg-elevated', bgSurface);
    var text = readVar('--text', '#0f172a');
    var border = readVar('--border', '#cbd5e1');
    var line = theme === 'dark' ? accentLight : accentDark;

    var direct = theme === 'dark' ? '#f472b6' : '#d946ef';
    var dashedClosed = theme === 'dark' ? '#cbd5e1' : '#64748b';
    var dashedOpen = theme === 'dark' ? '#93c5fd' : '#2563eb';
    var solidOpen = theme === 'dark' ? '#6ee7b7' : '#059669';

    if (style === 'paper') {
      direct = theme === 'dark' ? '#fda4af' : '#be185d';
      dashedClosed = theme === 'dark' ? '#e5d7c5' : '#6b5b4a';
      dashedOpen = theme === 'dark' ? '#bfdbfe' : '#1d4ed8';
      solidOpen = theme === 'dark' ? '#86efac' : '#166534';
    }

    if (style === 'bold') {
      direct = '#f472b6';
      dashedClosed = '#d4d4d8';
      dashedOpen = '#60a5fa';
      solidOpen = '#34d399';
    }

    return {
      bg: bgSurface,
      text: text,
      nodeBg: bgElevated,
      nodeBorder: border,
      line: line,
      labelBg: bg,
      direct: direct,
      dashedClosed: dashedClosed,
      dashedOpen: dashedOpen,
      solidOpen: solidOpen
    };
  }

  function applyMermaidCssVars() {
    var p = buildMermaidPalette();
    var root = document.documentElement;
    root.style.setProperty('--mermaid-bg', p.bg);
    root.style.setProperty('--mermaid-text', p.text);
    root.style.setProperty('--mermaid-node-bg', p.nodeBg);
    root.style.setProperty('--mermaid-node-border', p.nodeBorder);
    root.style.setProperty('--mermaid-line', p.line);
    root.style.setProperty('--mermaid-label-bg', p.labelBg);
    root.style.setProperty('--mermaid-legend-direct', p.direct);
    root.style.setProperty('--mermaid-legend-dashed-closed', p.dashedClosed);
    root.style.setProperty('--mermaid-legend-dashed-open', p.dashedOpen);
    root.style.setProperty('--mermaid-legend-solid-open', p.solidOpen);
  }

  function buildMermaidThemeVariables() {
    var p = buildMermaidPalette();
    return {
      background: p.bg,
      primaryColor: p.nodeBg,
      primaryTextColor: p.text,
      primaryBorderColor: p.nodeBorder,
      secondaryColor: p.bg,
      tertiaryColor: p.bg,
      lineColor: p.line,
      textColor: p.text,
      mainBkg: p.nodeBg,
      nodeBorder: p.nodeBorder,
      clusterBkg: p.bg,
      clusterBorder: p.nodeBorder,
      edgeLabelBackground: p.labelBg,
      titleColor: p.text,
      actorBkg: p.nodeBg,
      actorBorder: p.nodeBorder,
      actorTextColor: p.text,
      actorLineColor: p.line,
      signalColor: p.line,
      signalTextColor: p.text,
      noteBkgColor: p.labelBg,
      noteBorderColor: p.nodeBorder,
      noteTextColor: p.text,
      classText: p.text,
      labelTextColor: p.text
    };
  }

  function isVisibleMermaidBlock(el) {
    if (!el || !el.isConnected) return false;
    var section = el.closest('section.lesson');
    if (section) {
      var sectionStyle = window.getComputedStyle(section);
      if (sectionStyle.display === 'none' || sectionStyle.visibility === 'hidden') return false;
    }
    var style = window.getComputedStyle(el);
    return style.display !== 'none' && style.visibility !== 'hidden';
  }

  function normalizeMermaidBlock(el) {
    if (!el.dataset.originalMermaid) {
      if (el.querySelector('svg')) return false;
      el.dataset.originalMermaid = (el.textContent || '').trimEnd();
    }
    if (!el.dataset.originalMermaid) return false;
    el.innerHTML = '';
    el.textContent = el.dataset.originalMermaid;
    el.removeAttribute('data-processed');
    return true;
  }

  var mermaidSvgUid = 0;

  function setImportantStyle(el, prop, value) {
    if (!el || !el.style) return;
    el.style.setProperty(prop, value, 'important');
  }

  function rewriteSvgReference(value, idMap) {
    var current = String(value || '');
    if (!current || current.indexOf('#') < 0) return current;

    current = current.replace(/url\(#([^)]+)\)/g, function (full, id) {
      var mapped = idMap[id];
      return mapped ? 'url(#' + mapped + ')' : full;
    });

    current = current.replace(/^#([A-Za-z_][\w:.-]*)$/, function (full, id) {
      var mapped = idMap[id];
      return mapped ? '#' + mapped : full;
    });

    return current;
  }

  function uniquifySvgIds(svg) {
    if (!svg || svg.dataset.smaIdsPatched === '1') return;

    mermaidSvgUid += 1;
    var prefix = 'sma-svg-' + mermaidSvgUid + '-';
    var idMap = {};

    svg.querySelectorAll('[id]').forEach(function (node) {
      var oldId = node.getAttribute('id');
      if (!oldId || idMap[oldId]) return;
      var nextId = prefix + oldId;
      idMap[oldId] = nextId;
      node.setAttribute('id', nextId);
    });

    if (!Object.keys(idMap).length) {
      svg.dataset.smaIdsPatched = '1';
      return;
    }

    var attrs = ['marker-start', 'marker-mid', 'marker-end', 'fill', 'stroke', 'filter', 'clip-path', 'mask', 'href', 'xlink:href'];
    svg.querySelectorAll('*').forEach(function (node) {
      attrs.forEach(function (attr) {
        var raw = node.getAttribute(attr);
        if (!raw) return;
        var next = rewriteSvgReference(raw, idMap);
        if (next !== raw) node.setAttribute(attr, next);
      });
      var inlineStyle = node.getAttribute('style');
      if (inlineStyle && inlineStyle.indexOf('#') >= 0) {
        var nextInlineStyle = rewriteSvgReference(inlineStyle, idMap);
        if (nextInlineStyle !== inlineStyle) node.setAttribute('style', nextInlineStyle);
      }
    });

    svg.dataset.smaIdsPatched = '1';
  }

  function findMarkerId(svg, baseId) {
    if (!svg || !baseId) return null;
    var exact = svg.querySelector('marker[id=\"' + baseId + '\"]');
    if (exact) return exact.getAttribute('id');
    var suffix = svg.querySelector('marker[id$=\"-' + baseId + '\"]');
    return suffix ? suffix.getAttribute('id') : null;
  }

  function ensureSequenceDirection(svg, selector, markerId, lineColor) {
    if (!markerId) return;
    svg.querySelectorAll(selector).forEach(function (line) {
      if (!line.getAttribute('marker-end')) {
        line.setAttribute('marker-end', 'url(#' + markerId + ')');
      }
      setImportantStyle(line, 'stroke', lineColor);
      setImportantStyle(line, 'stroke-width', '2');
      setImportantStyle(line, 'opacity', '1');
    });
  }

  function enforceSequenceArrows(svg, palette) {
    var arrow = findMarkerId(svg, 'arrowhead') || findMarkerId(svg, 'filled-head');
    var filled = findMarkerId(svg, 'filled-head') || arrow;
    var cross = findMarkerId(svg, 'crosshead') || arrow;

    ensureSequenceDirection(svg, 'line.messageLine0, path.messageLine0', arrow, palette.line);
    ensureSequenceDirection(svg, 'line.messageLine1, path.messageLine1', arrow, palette.line);
    ensureSequenceDirection(svg, 'line.messageLine2, path.messageLine2', filled || cross || arrow, palette.line);

    svg.querySelectorAll('marker').forEach(function (marker) {
      if (!marker.getAttribute('markerWidth') || Number(marker.getAttribute('markerWidth')) < 10) {
        marker.setAttribute('markerWidth', '12');
      }
      if (!marker.getAttribute('markerHeight') || Number(marker.getAttribute('markerHeight')) < 10) {
        marker.setAttribute('markerHeight', '12');
      }
      marker.setAttribute('overflow', 'visible');
    });
  }

  function applyMermaidSvgOverrides(root) {
    var p = buildMermaidPalette();
    var host = root && typeof root.querySelectorAll === 'function' ? root : document;
    host.querySelectorAll('pre.mermaid svg').forEach(function (svg) {
      uniquifySvgIds(svg);

      svg.querySelectorAll('text, tspan').forEach(function (el) {
        el.setAttribute('fill', p.text);
        setImportantStyle(el, 'fill', p.text);
        setImportantStyle(el, 'color', p.text);
      });
      svg.querySelectorAll('foreignObject div, foreignObject span').forEach(function (el) {
        setImportantStyle(el, 'color', p.text);
      });
      svg.querySelectorAll('.edgePath .path, path.relation, line').forEach(function (el) {
        setImportantStyle(el, 'stroke', p.line);
      });
      svg.querySelectorAll('.arrowheadPath, marker path, marker polygon, marker polyline').forEach(function (el) {
        setImportantStyle(el, 'fill', p.line);
        setImportantStyle(el, 'stroke', p.line);
        setImportantStyle(el, 'opacity', '1');
      });
      svg.querySelectorAll('.edgeLabel rect, .labelBkg').forEach(function (el) {
        setImportantStyle(el, 'fill', p.labelBg);
        setImportantStyle(el, 'opacity', '1');
      });

      enforceSequenceArrows(svg, p);
    });
  }

  function rerenderMermaidSafely(options) {
    options = options || {};
    applyMermaidCssVars();
    if (typeof mermaid === 'undefined') return;

    var scope = options.scope && typeof options.scope.querySelectorAll === 'function' ? options.scope : document;
    var visibleOnly = options.visibleOnly !== false;
    var blocks = Array.prototype.slice.call(scope.querySelectorAll('pre.mermaid'));
    if (visibleOnly) {
      blocks = blocks.filter(isVisibleMermaidBlock);
    }
    var renderableBlocks = blocks.filter(normalizeMermaidBlock);
    if (!renderableBlocks.length) {
      applyMermaidSvgOverrides(scope);
      return;
    }

    renderableBlocks.forEach(function (el) {
      el.setAttribute('data-sma-mermaid-pending', '1');
    });

    var selector = 'pre.mermaid[data-sma-mermaid-pending=\"1\"]';
    var finish = function () {
      renderableBlocks.forEach(function (el) {
        el.removeAttribute('data-sma-mermaid-pending');
      });
      applyMermaidSvgOverrides(scope);
    };

    try {
      mermaid.initialize({
        startOnLoad: false,
        theme: 'base',
        securityLevel: 'loose',
        deterministicIds: false,
        themeVariables: buildMermaidThemeVariables(),
        flowchart: { htmlLabels: true, curve: 'basis' }
      });
      mermaid.run({ querySelector: selector }).then(finish).catch(finish);
    } catch (e) {}
  }

  function applyStyle(style) {
    style = sanitizeChoice(style, STYLE_VALUES, STYLE_ALIASES) || 'enterprise';
    document.documentElement.setAttribute('data-style', style);
    localStorage.setItem('course-style', style);
    var btn = document.getElementById('style-cycle-btn');
    if (btn) btn.textContent = 'Estilo: ' + style.charAt(0).toUpperCase() + style.slice(1);
    applyMermaidCssVars();
  }

  function cycleStyle() {
    var current = activeStyle();
    var currentIndex = STYLE_VALUES.indexOf(current);
    if (currentIndex < 0) currentIndex = 0;
    var next = STYLE_VALUES[(currentIndex + 1 + STYLE_VALUES.length) % STYLE_VALUES.length];
    applyStyle(next);
    rerenderMermaidSafely();
  }

  function applyCodeTheme(theme) {
    theme = sanitizeChoice(theme, CODE_THEME_VALUES, CODE_THEME_ALIASES) || 'monokai';
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
    var current = readStoredChoice('course-code-theme', CODE_THEME_VALUES, CODE_THEME_ALIASES) || 'monokai';
    var currentIndex = CODE_THEME_VALUES.indexOf(current);
    if (currentIndex < 0) currentIndex = 0;
    var next = CODE_THEME_VALUES[(currentIndex + 1 + CODE_THEME_VALUES.length) % CODE_THEME_VALUES.length];
    applyCodeTheme(next);
  }

  function applyTheme(theme) {
    theme = sanitizeChoice(theme, THEME_VALUES, THEME_ALIASES) || 'light';
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('course-theme', theme);
    var btn = document.getElementById('theme-toggle');
    if (btn) {
      btn.textContent = theme === 'dark' ? 'Tema: Oscuro' : 'Tema: Claro';
      btn.title = theme === 'dark' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro';
    }
    applyMermaidCssVars();
  }

  function toggleTheme() {
    var current = activeTheme();
    applyTheme(current === 'dark' ? 'light' : 'dark');
    rerenderMermaidSafely();
  }

  window.applyStyle = applyStyle;
  window.cycleStyle = cycleStyle;
  window.applyCodeTheme = applyCodeTheme;
  window.cycleCodeTheme = cycleCodeTheme;
  window.applyTheme = applyTheme;
  window.toggleTheme = toggleTheme;
  window.resetVisualPreferences = resetVisualPreferences;
  window.rerenderMermaidSafely = rerenderMermaidSafely;

  applyStyle(getPreferredStyle());
  applyCodeTheme(getPreferredCodeTheme());
  applyTheme(getPreferredTheme());

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', rerenderMermaidSafely, { once: true });
  } else {
    setTimeout(rerenderMermaidSafely, 0);
  }
})();
