(function () {
  const meta = document.querySelector('meta[name="course-id"]');
  if (!meta) return;

  const courseId = meta.content;
  const keyCompleted = `sma:${courseId}:topics:completed`;
  const keyReview = `sma:${courseId}:topics:review`;
  const keyLastTopic = `sma:${courseId}:topics:last`;
  const keyScroll = `sma:${courseId}:topics:scroll`;
  const keyZen = `sma:${courseId}:zen`;
  const keyStats = `sma:${courseId}:stats`;
  const keyFontSize = `sma:${courseId}:font:size`;
  const keyCloudProfile = 'sma:cloud:profile:v1';
  const keyCloudUpdatedAtLegacy = `sma:${courseId}:cloud:updated-at`;
  const keyCloudUpdatedAtByProfilePrefix = `sma:${courseId}:cloud:updated-at:v2:`;
  const keyCloudEndpoint = 'sma:cloud:endpoint:v1';
  const keyAuthSession = 'sma:auth:session:v1';
  const keyAuthUser = 'sma:auth:user:v1';
  const DEFAULT_REMOTE_PROGRESS_BASE = 'https://architecture-stack.vercel.app';

  const completionBtn = document.getElementById('study-completion-toggle');
  const zenBtn = document.getElementById('study-zen-toggle');
  const progressEl = document.getElementById('study-progress');
  const indexActions = document.getElementById('study-ux-index-actions');

  const baseFontSize = 16;
  const minFontSize = 13;
  const maxFontSize = 19;

  let fontDownBtn = null;
  let fontUpBtn = null;

  const completed = readJson(keyCompleted, {});
  const review = readJson(keyReview, {});
  const scrollMap = readJson(keyScroll, {});
  const stats = ensureStatsShape(readJson(keyStats, {}));

  let timerState = { topicId: null, startedAt: null };
  let filterReviewOnly = false;
  let indexActionsInitialized = false;
  let indexActionsPending = false;
  let navDecorPending = false;
  const cloudSync = createCloudSync();

  const topics = Array.from(document.querySelectorAll('section.lesson')).map((section, index) => {
    const topicId = section.getAttribute('data-topic-id') || section.id || `topic-${index + 1}`;
    section.setAttribute('data-topic-id', topicId);
    return {
      id: topicId,
      section,
      path: normalizePath(section.getAttribute('data-lesson-path') || topicId)
    };
  });

  const navLinks = Array.from(document.querySelectorAll('a.doc-nav-link'));
  mapLinksToTopics(navLinks, topics);
  const navLinksByTopicId = indexNavLinksByTopicId(navLinks);
  hydrateTopicLessonLabels(topics, navLinksByTopicId);
  setupTopBarLayout();
  syncTopbarOffset();

  const reviewBtn = ensureReviewTopButton();

  setupFontControls();
  applySavedFontSize();
  reorderTopControls();
  observeTopControlsOrder();

  let currentTopic = resolveCurrentTopic(topics, location.hash, localStorage.getItem(keyLastTopic));
  if (!currentTopic) return;

  applyCompactMobileClass();
  renderTopic(currentTopic.id, false);
  markUiHydrated();
  applyZen(localStorage.getItem(keyZen) === '1');
  updateCompletionUi();
  updateReviewUi();
  updateProgressUi();
  scheduleDecorateNavStates();
  setupButtons();
  setupShortcuts();
  setupScrollPersistence();
  scheduleIndexActionsSetup();
  startTopicTimer(currentTopic.id);
  cloudSync.bootstrap();

  document.addEventListener('visibilitychange', function () {
    if (document.hidden) {
      stopTopicTimer();
    } else if (currentTopic) {
      startTopicTimer(currentTopic.id);
    }
  });

  window.addEventListener('beforeunload', function () {
    stopTopicTimer();
  });

  window.addEventListener('hashchange', function () {
    const next = resolveCurrentTopic(topics, location.hash, null);
    if (!next) return;
    renderTopic(next.id, true);
  });

  window.addEventListener('resize', debounce(function () {
    applyCompactMobileClass();
    updateCompletionUi();
    updateReviewUi();
    updateProgressUi();
    applyZen(document.body.classList.contains('study-ux-zen'));
    syncTopbarOffset();
  }, 120));

  function ensureStatsShape(raw) {
    return {
      totalTimeMs: Number(raw.totalTimeMs || 0),
      perTopicTimeMs: raw.perTopicTimeMs && typeof raw.perTopicTimeMs === 'object' ? raw.perTopicTimeMs : {},
      lastSessionStart: null
    };
  }

  function isCompactMobileViewport() {
    return window.innerWidth <= 480;
  }

  function applyCompactMobileClass() {
    document.body.classList.toggle('study-ux-compact-mobile', isCompactMobileViewport());
  }

  function persistStats() {
    localStorage.setItem(keyStats, JSON.stringify(stats));
    cloudSync.schedulePush();
  }

  function setupTopBarLayout() {
    const body = document.body;
    const bar = document.createElement('div');
    bar.id = 'global-topbar';
    bar.className = 'global-topbar';

    const left = document.createElement('div');
    left.id = 'global-topbar-left';
    left.className = 'global-topbar-left';

    const sidebarToggle = ensureSidebarToggleButton();
    const switcher = document.getElementById('course-switcher');
    const study = document.getElementById('study-ux-controls');
    const theme = document.getElementById('theme-controls');

    if (sidebarToggle) left.appendChild(sidebarToggle);
    if (switcher) left.appendChild(switcher);
    if (left.children.length > 0) bar.appendChild(left);
    bar.appendChild(ensureCurrentLessonContext());
    if (study) bar.appendChild(study);
    if (theme) bar.appendChild(theme);

    body.insertBefore(bar, body.firstChild);
    body.classList.add('with-global-topbar');
    setupSidebarToggleStateSync();
  }

  function ensureSidebarToggleButton() {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return null;

    let button = document.getElementById('sidebar-toggle-topbar');
    if (!button) {
      button = document.createElement('button');
      button.id = 'sidebar-toggle-topbar';
      button.type = 'button';
      button.textContent = '☰ Índice';
      button.setAttribute('aria-controls', 'sidebar');
      button.setAttribute('aria-expanded', String(document.body.classList.contains('sidebar-open')));
      button.addEventListener('click', function () {
        toggleSidebarFromTopbar();
      });
    }
    return button;
  }

  function toggleSidebarFromTopbar() {
    if (typeof window.toggleSidebar === 'function') {
      window.toggleSidebar();
    } else {
      document.body.classList.toggle('sidebar-open');
    }
    syncSidebarToggleState();
  }

  function setupSidebarToggleStateSync() {
    syncSidebarToggleState();
    if (typeof MutationObserver === 'undefined') return;
    const observer = new MutationObserver(function () {
      syncSidebarToggleState();
    });
    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
  }

  function syncSidebarToggleState() {
    const button = document.getElementById('sidebar-toggle-topbar');
    if (!button) return;
    const isOpen = document.body.classList.contains('sidebar-open');
    button.setAttribute('aria-expanded', String(isOpen));
    button.textContent = isOpen ? '✕ Índice' : '☰ Índice';
  }

  function syncTopbarOffset() {
    const bar = document.getElementById('global-topbar');
    if (!bar) return;
    const height = Math.ceil(bar.getBoundingClientRect().height) + 8;
    document.body.style.setProperty('--global-topbar-offset', `${height}px`);
  }

  function setupFontControls() {
    const controls = document.getElementById('study-ux-controls');
    if (!controls) return;

    fontDownBtn = document.getElementById('study-font-down');
    fontUpBtn = document.getElementById('study-font-up');

    if (!fontDownBtn) {
      fontDownBtn = document.createElement('button');
      fontDownBtn.id = 'study-font-down';
      fontDownBtn.type = 'button';
      fontDownBtn.textContent = 'A-';
      fontDownBtn.title = 'Disminuir tamaño del texto';
      fontDownBtn.addEventListener('click', function () {
        setFontSize(readFontSize() - 1);
      });
    }

    if (!fontUpBtn) {
      fontUpBtn = document.createElement('button');
      fontUpBtn.id = 'study-font-up';
      fontUpBtn.type = 'button';
      fontUpBtn.textContent = 'A+';
      fontUpBtn.title = 'Aumentar tamaño del texto';
      fontUpBtn.addEventListener('click', function () {
        setFontSize(readFontSize() + 1);
      });
    }
  }

  function readFontSize() {
    const value = Number(localStorage.getItem(keyFontSize) || baseFontSize);
    if (!Number.isFinite(value)) return baseFontSize;
    return Math.min(maxFontSize, Math.max(minFontSize, value));
  }

  function applySavedFontSize() {
    setFontSize(readFontSize(), false);
  }

  function setFontSize(px, persist = true) {
    const next = Math.min(maxFontSize, Math.max(minFontSize, Number(px) || baseFontSize));
    const content = document.getElementById('content');
    if (content) content.style.fontSize = `${next}px`;
    if (persist) localStorage.setItem(keyFontSize, String(next));
    if (fontDownBtn) fontDownBtn.disabled = next <= minFontSize;
    if (fontUpBtn) fontUpBtn.disabled = next >= maxFontSize;
  }

  function reorderTopControls() {
    const controls = document.getElementById('study-ux-controls');
    if (!controls) return;

    const assistantBtn = document.getElementById('study-ai-open-btn');

    const desired = [
      progressEl,
      fontDownBtn,
      fontUpBtn,
      completionBtn,
      reviewBtn,
      zenBtn,
      assistantBtn
    ].filter(Boolean);

    const current = Array.from(controls.children).filter((el) => desired.includes(el));
    const alreadyOrdered = current.length === desired.length && current.every((el, idx) => el === desired[idx]);
    if (alreadyOrdered) return;

    desired.forEach((el) => controls.appendChild(el));
    syncTopbarOffset();
  }

  function observeTopControlsOrder() {
    const controls = document.getElementById('study-ux-controls');
    if (!controls || typeof MutationObserver === 'undefined') return;

    const observer = new MutationObserver(function () {
      reorderTopControls();
      syncTopbarOffset();
    });
    observer.observe(controls, { childList: true });
  }

  function ensureReviewTopButton() {
    const controls = document.getElementById('study-ux-controls');
    if (!controls) return null;
    let btn = document.getElementById('study-review-toggle');
    if (!btn) {
      btn = document.createElement('button');
      btn.id = 'study-review-toggle';
      btn.type = 'button';
      controls.appendChild(btn);
    }
    return btn;
  }

  function ensureCurrentLessonContext() {
    let node = document.getElementById('study-current-lesson');
    if (node) return node;
    node = document.createElement('div');
    node.id = 'study-current-lesson';
    node.className = 'study-current-lesson';
    node.setAttribute('aria-live', 'polite');
    return node;
  }

  function normalizeLessonLabel(rawLabel) {
    const raw = String(rawLabel || '').replace(/\s+/g, ' ').trim();
    if (!raw) return '';

    const fullMatch = raw.match(/^Lecci[oó]n\s+(\d+)\s*:\s*(.+)$/i);
    if (fullMatch) {
      return `Lección ${fullMatch[1]}: ${fullMatch[2].trim()}`;
    }

    const numberOnlyMatch = raw.match(/^Lecci[oó]n\s+(\d+)$/i);
    if (numberOnlyMatch) {
      return `Lección ${numberOnlyMatch[1]}`;
    }

    return raw;
  }

  function extractBaseNavLabel(link) {
    if (!link) return '';
    const clone = link.cloneNode(true);
    clone.querySelectorAll('.study-ux-completed-badge, .study-ux-review-badge').forEach((badge) => badge.remove());
    return normalizeLessonLabel(clone.textContent || '');
  }

  function mapLinksToTopics(links, topicList) {
    links.forEach((link) => {
      if (!link.dataset.lessonLabel) {
        const label = extractBaseNavLabel(link);
        if (label) link.dataset.lessonLabel = label;
      }
      const target = (link.getAttribute('href') || '').replace('#', '');
      const topic = topicList.find((t) => t.id === target);
      if (topic) {
        link.dataset.topicId = topic.id;
      }
    });
  }

  function indexNavLinksByTopicId(links) {
    const byTopicId = new Map();
    links.forEach((link) => {
      const topicId = link.dataset.topicId;
      if (!topicId) return;
      const list = byTopicId.get(topicId) || [];
      list.push(link);
      byTopicId.set(topicId, list);
    });
    return byTopicId;
  }

  function resolveCurrentTopic(topicList, hash, stored) {
    const fromHash = (hash || '').replace('#', '');
    if (fromHash) {
      const foundHash = topicList.find((t) => t.id === fromHash);
      if (foundHash) return foundHash;
    }
    if (stored) {
      const foundStored = topicList.find((t) => t.id === stored);
      if (foundStored) return foundStored;
    }
    return topicList[0] || null;
  }

  function buildFallbackLessonLabel(topic, index) {
    const heading = topic && topic.section ? topic.section.querySelector('h1, h2, h3') : null;
    const title = heading ? String(heading.textContent || '').replace(/\s+/g, ' ').trim() : '';
    if (title) return `Lección ${index + 1}: ${title}`;
    return `Lección ${index + 1}`;
  }

  function hydrateTopicLessonLabels(topicList, linksByTopicId) {
    topicList.forEach((topic, index) => {
      const links = linksByTopicId.get(topic.id) || [];
      const fromNav = links
        .map((link) => normalizeLessonLabel(link.dataset.lessonLabel || ''))
        .find(Boolean);
      topic.lessonLabel = fromNav || buildFallbackLessonLabel(topic, index);
    });

    const doneBtn = document.createElement('button');
    doneBtn.type = 'button';
    doneBtn.className = 'study-topic-nav-complete';
    doneBtn.textContent = completed[topic.id] ? '↩ Desmarcar completado' : '✅ Marcar completado';
    doneBtn.addEventListener('click', function () {
      toggleCompletion(topic.id);
    });

    const nextBtn = document.createElement('button');
    nextBtn.type = 'button';
    nextBtn.textContent = 'Siguiente lección ➡';
    nextBtn.disabled = index === topics.length - 1;
    nextBtn.addEventListener('click', function () {
      if (index < topics.length - 1) renderTopic(topics[index + 1].id, true);
    });

    nav.appendChild(prevBtn);
    nav.appendChild(doneBtn);
    nav.appendChild(nextBtn);
  }

  function ensureLessonPrimaryHeadingLabel(topic) {
    if (!topic || !topic.section || !topic.lessonLabel) return;

    const staleInlineHeader = topic.section.querySelector('.study-lesson-inline-title');
    if (staleInlineHeader) staleInlineHeader.remove();

    const label = String(topic.lessonLabel || '').trim();
    if (!/^Lecci[oó]n\s+\d+/i.test(label)) return;

    const heading = topic.section.querySelector('h1, h2, h3');
    if (!heading) return;

    const current = String(heading.textContent || '').replace(/\s+/g, ' ').trim();
    if (!heading.dataset.smaOriginalHeading) {
      heading.dataset.smaOriginalHeading = current;
    }

    if (current !== label) {
      heading.textContent = label;
    }
  }

  function updateCurrentLessonContext(topic) {
    const node = document.getElementById('study-current-lesson');
    if (!node) return;
    const label = topic && topic.lessonLabel ? String(topic.lessonLabel).trim() : '';
    if (!label) {
      node.textContent = '';
      node.style.display = 'none';
      return;
    }
    node.style.display = '';
    node.textContent = label;
  }

  function markUiHydrated() {
    document.body.classList.add('sma-hydrated');
  }

  function ensureTopicNavigation(topic) {
    if (!topic) return;
    const index = topics.findIndex((t) => t.id === topic.id);
    if (index < 0) return;

    let nav = topic.section.querySelector('.study-topic-nav');
    if (!nav) {
      nav = document.createElement('div');
      nav.className = 'study-topic-nav';
      topic.section.appendChild(nav);
    }
    nav.innerHTML = '';

    const prevBtn = document.createElement('button');
    prevBtn.type = 'button';
    prevBtn.textContent = '⬅ Lección anterior';
    prevBtn.disabled = index === 0;
    prevBtn.addEventListener('click', function () {
      if (index > 0) renderTopic(topics[index - 1].id, true);
    });

    const doneBtn = document.createElement('button');
    doneBtn.type = 'button';
    doneBtn.className = 'study-topic-nav-complete';
    doneBtn.textContent = completed[topic.id] ? '↩ Desmarcar completado' : '✅ Marcar completado';
    doneBtn.addEventListener('click', function () {
      toggleCompletion(topic.id);
    });

    const nextBtn = document.createElement('button');
    nextBtn.type = 'button';
    nextBtn.textContent = 'Siguiente lección ➡';
    nextBtn.disabled = index === topics.length - 1;
    nextBtn.addEventListener('click', function () {
      if (index < topics.length - 1) renderTopic(topics[index + 1].id, true);
    });

    nav.appendChild(prevBtn);
    nav.appendChild(doneBtn);
    nav.appendChild(nextBtn);
  }

  function renderTopic(topicId, shouldRestoreScroll) {
    const target = topics.find((t) => t.id === topicId);
    if (!target) return;

    stopTopicTimer();

    topics.forEach((t) => {
      t.section.style.display = t.id === topicId ? '' : 'none';
    });
    markUiHydrated();

    navLinks.forEach((link) => {
      const active = link.dataset.topicId === topicId;
      link.classList.toggle('study-nav-active', active);
      if (active) {
        var sidebar = document.getElementById('sidebar');
        if (sidebar) {
          var linkTop = link.offsetTop;
          var sidebarH = sidebar.clientHeight;
          sidebar.scrollTop = Math.max(0, linkTop - sidebarH / 3);
        }
      }
    });

    currentTopic = target;
    ensureLessonPrimaryHeadingLabel(currentTopic);
    updateCurrentLessonContext(currentTopic);
    localStorage.setItem(keyLastTopic, currentTopic.id);
    cloudSync.schedulePush();

    if (location.hash.replace('#', '') !== currentTopic.id) {
      history.replaceState(null, '', `#${currentTopic.id}`);
    }

    ensureTopicNavigation(currentTopic);
    updateCompletionUi();
    updateReviewUi();
    updateProgressUi();

    if (shouldRestoreScroll) {
      restoreScrollForTopic(currentTopic.id);
    }

    if (typeof window.rerenderMermaidSafely === 'function') {
      window.rerenderMermaidSafely({ scope: target.section, visibleOnly: true });
    }

    startTopicTimer(currentTopic.id);
  }

  function setupButtons() {
    if (completionBtn) completionBtn.addEventListener('click', function () { toggleCompletion(); });
    if (reviewBtn) reviewBtn.addEventListener('click', function () { toggleReview(); });
    if (zenBtn) {
      zenBtn.addEventListener('click', function () {
        const next = !(localStorage.getItem(keyZen) === '1');
        localStorage.setItem(keyZen, next ? '1' : '0');
        applyZen(next);
      });
    }
  }

  function setupShortcuts() {
    document.addEventListener('keydown', function (event) {
      if (event.metaKey || event.ctrlKey || event.altKey) return;
      const tag = (event.target && event.target.tagName || '').toLowerCase();
      if (tag === 'input' || tag === 'textarea' || tag === 'select') return;

      const key = event.key.toLowerCase();
      if (key === 'c') {
        event.preventDefault();
        toggleCompletion();
      } else if (key === 'v') {
        event.preventDefault();
        toggleReview();
      } else if (key === 'z') {
        event.preventDefault();
        const next = !(localStorage.getItem(keyZen) === '1');
        localStorage.setItem(keyZen, next ? '1' : '0');
        applyZen(next);
      } else if (key === 'r') {
        event.preventDefault();
        goResume();
      } else if (key === 'g') {
        event.preventDefault();
        goInicio();
      } else if (key === 'n') {
        event.preventDefault();
        goRelative(1);
      } else if (key === 'p') {
        event.preventDefault();
        goRelative(-1);
      }
    });
  }

  function setupScrollPersistence() {
    const save = debounce(function () {
      if (!currentTopic) return;
      scrollMap[currentTopic.id] = Math.max(0, Math.round(window.scrollY || 0));
      localStorage.setItem(keyScroll, JSON.stringify(scrollMap));
    }, 180);
    window.addEventListener('scroll', save, { passive: true });
  }

  function scheduleIndexActionsSetup() {
    if (!indexActions || indexActionsInitialized || indexActionsPending) return;
    indexActionsPending = true;
    const run = function () {
      if (indexActionsInitialized) return;
      indexActionsPending = false;
      setupIndexActions();
      indexActionsInitialized = true;
    };
    if (typeof window.requestIdleCallback === 'function') {
      window.requestIdleCallback(function () { run(); }, { timeout: 700 });
      return;
    }
    setTimeout(run, 180);
  }

  function setupIndexActions() {
    if (!indexActions) return;
    indexActions.innerHTML = '';

    const rowPrimary = document.createElement('div');
    rowPrimary.className = 'study-ux-index-row';
    rowPrimary.appendChild(createButton('▶ Continuar donde lo dejaste', goResume, 'study-resume-btn'));
    rowPrimary.appendChild(createButton('➡ Ir al primer tema pendiente', goFirstIncomplete));
    rowPrimary.appendChild(createButton('🔁 Mostrar solo temas para repaso', toggleReviewFilter, 'study-filter-review'));
    rowPrimary.appendChild(createButton('🔗 Copiar enlace de sincronización', copySyncLink, 'study-sync-link'));
    rowPrimary.appendChild(createButton('🔐 Cuenta', goAuthPortal, 'study-auth-portal'));

    const statsBox = document.createElement('div');
    statsBox.id = 'study-stats';
    statsBox.className = 'study-ux-panel';

    const actionsBox = document.createElement('div');
    actionsBox.className = 'study-ux-panel';
    actionsBox.id = 'study-actions';
    actionsBox.appendChild(createButton('⬇ Exportar progreso', exportProgress));
    actionsBox.appendChild(createButton('⬆ Importar progreso', importProgress));
    actionsBox.appendChild(createButton('🗑 Resetear progreso', resetProgress));

    const importInput = document.createElement('input');
    importInput.type = 'file';
    importInput.accept = '.json,application/json';
    importInput.id = 'study-import-input';
    importInput.style.display = 'none';
    importInput.addEventListener('change', handleImportFileChange);
    actionsBox.appendChild(importInput);

    indexActions.appendChild(rowPrimary);
    indexActions.appendChild(statsBox);
    indexActions.appendChild(actionsBox);

    updateResumeButtonState();
    renderStats();
    updateProgressUi();
  }

  function createButton(label, onClick, id) {
    const btn = document.createElement('button');
    if (id) btn.id = id;
    btn.type = 'button';
    btn.textContent = label;
    btn.addEventListener('click', onClick);
    return btn;
  }

  function goAuthPortal() {
    const authUrl = buildAuthUrl();
    window.location.href = authUrl;
  }

  function goResume() {
    if (currentTopic) {
      scrollMap[currentTopic.id] = Math.max(0, Math.round(window.scrollY || 0));
      localStorage.setItem(keyScroll, JSON.stringify(scrollMap));
    }

    const last = localStorage.getItem(keyLastTopic) || (currentTopic && currentTopic.id) || null;
    const target = last ? topics.find((t) => t.id === last) : null;

    if (target) {
      if (currentTopic && currentTopic.id === target.id) {
        restoreScrollForTopic(target.id);
      } else {
        renderTopic(target.id, true);
      }
      return;
    }

    const pending = topics.find((t) => !completed[t.id]) || topics[0] || null;
    if (!pending) return;
    if (currentTopic && currentTopic.id === pending.id) {
      restoreScrollForTopic(pending.id);
      return;
    }
    renderTopic(pending.id, true);
  }

  function updateResumeButtonState() {
    const btn = document.getElementById('study-resume-btn');
    if (!btn) return;
    const last = localStorage.getItem(keyLastTopic);
    const exists = !!topics.find((t) => t.id === last);
    btn.disabled = !exists;
    btn.title = exists ? 'Abrir el último tema visitado' : 'Aún no hay un tema previo guardado';
  }

  function goInicio() {
    const first = topics[0];
    if (!first) return;
    renderTopic(first.id, true);
  }

  function goFirstIncomplete() {
    const pending = topics.find((t) => !completed[t.id]);
    if (!pending) return;
    renderTopic(pending.id, true);
  }

  function goRelative(delta) {
    if (!currentTopic) return;
    const idx = topics.findIndex((t) => t.id === currentTopic.id);
    if (idx < 0) return;
    const next = topics[idx + delta];
    if (!next) return;
    renderTopic(next.id, true);
  }

  function toggleCompletion(topicId) {
    const id = topicId || (currentTopic && currentTopic.id);
    if (!id) return;
    if (completed[id]) {
      delete completed[id];
    } else {
      completed[id] = true;
    }
    localStorage.setItem(keyCompleted, JSON.stringify(completed));
    cloudSync.schedulePush();
    const topic = topics.find((t) => t.id === id) || currentTopic;
    ensureTopicNavigation(topic);
    updateCompletionUi();
    updateProgressUi();
    decorateNavStateByTopicId(id);
    renderStats();
  }

  function toggleReview(topicId) {
    const id = topicId || (currentTopic && currentTopic.id);
    if (!id) return;
    if (review[id]) {
      delete review[id];
    } else {
      review[id] = true;
    }
    localStorage.setItem(keyReview, JSON.stringify(review));
    cloudSync.schedulePush();
    updateReviewUi();
    decorateNavStateByTopicId(id);
    applyReviewFilter();
    renderStats();
  }

  function updateCompletionUi() {
    if (!completionBtn || !currentTopic) return;
    const isDone = !!completed[currentTopic.id];
    const fullLabel = isDone ? '↩ Desmarcar' : '✅ Marcar completado';
    const compactLabel = isDone ? '↩ Hecho' : '✅ Hecho';
    completionBtn.textContent = isCompactMobileViewport() ? compactLabel : fullLabel;
    completionBtn.setAttribute('aria-label', fullLabel);
    completionBtn.title = fullLabel;
  }

  function updateReviewUi() {
    if (!reviewBtn || !currentTopic) return;
    const isReview = !!review[currentTopic.id];
    const fullLabel = isReview ? '❌ Quitar repaso' : '🔁 Marcar para repaso';
    const compactLabel = isReview ? '❌ Repaso' : '🔁 Repaso';
    reviewBtn.textContent = isCompactMobileViewport() ? compactLabel : fullLabel;
    reviewBtn.setAttribute('aria-label', fullLabel);
    reviewBtn.title = fullLabel;
  }

  function updateProgressUi() {
    const total = topics.length;
    const done = topics.filter((t) => !!completed[t.id]).length;
    const percent = total === 0 ? 0 : Math.round((done / total) * 100);
    if (progressEl) {
      const fullLabel = `Progreso: ${done}/${total} (${percent}%)`;
      progressEl.textContent = isCompactMobileViewport() ? `${done}/${total}` : fullLabel;
      progressEl.setAttribute('aria-label', fullLabel);
      progressEl.title = fullLabel;
    }
  }

  function scheduleDecorateNavStates() {
    if (navDecorPending) return;
    navDecorPending = true;
    const run = function () {
      navDecorPending = false;
      navLinksByTopicId.forEach((_links, topicId) => {
        decorateNavStateByTopicId(topicId);
      });
    };
    if (typeof window.requestIdleCallback === 'function') {
      window.requestIdleCallback(function () { run(); }, { timeout: 700 });
      return;
    }
    setTimeout(run, 180);
  }

  function decorateNavStateByTopicId(topicId) {
    if (!topicId) return;
    const links = navLinksByTopicId.get(topicId) || [];
    links.forEach((link) => {
      let completedBadge = link.querySelector('.study-ux-completed-badge');
      if (completed[topicId]) {
        if (!completedBadge) {
          completedBadge = document.createElement('span');
          completedBadge.className = 'study-ux-completed-badge';
          completedBadge.textContent = '✓';
          link.appendChild(completedBadge);
        }
      } else if (completedBadge) {
        completedBadge.remove();
      }

      let reviewBadge = link.querySelector('.study-ux-review-badge');
      if (review[topicId]) {
        if (!reviewBadge) {
          reviewBadge = document.createElement('span');
          reviewBadge.className = 'study-ux-review-badge';
          reviewBadge.textContent = '🔁';
          link.appendChild(reviewBadge);
        }
      } else if (reviewBadge) {
        reviewBadge.remove();
      }
    });
  }

  function toggleReviewFilter() {
    filterReviewOnly = !filterReviewOnly;
    const btn = document.getElementById('study-filter-review');
    if (btn) {
      btn.textContent = filterReviewOnly ? '🔁 Mostrar todos los temas' : '🔁 Mostrar solo temas para repaso';
      btn.classList.toggle('active', filterReviewOnly);
    }
    applyReviewFilter();
  }

  function applyReviewFilter() {
    navLinks.forEach((link) => {
      const topicId = link.dataset.topicId;
      if (!topicId) return;
      const show = !filterReviewOnly || !!review[topicId];
      const li = link.closest('li');
      if (li) li.style.display = show ? '' : 'none';
    });
  }

  function startTopicTimer(topicId) {
    if (!topicId) return;
    if (timerState.topicId === topicId && timerState.startedAt) return;
    timerState = { topicId, startedAt: Date.now() };
    stats.lastSessionStart = timerState.startedAt;
    persistStats();
  }

  function stopTopicTimer() {
    if (!timerState.topicId || !timerState.startedAt) return;
    const elapsed = Math.max(0, Date.now() - timerState.startedAt);
    stats.totalTimeMs += elapsed;
    stats.perTopicTimeMs[timerState.topicId] = Number(stats.perTopicTimeMs[timerState.topicId] || 0) + elapsed;
    stats.lastSessionStart = null;
    persistStats();
    timerState = { topicId: null, startedAt: null };
    renderStats();
  }

  function formatDuration(ms) {
    const totalMinutes = Math.floor(ms / 60000);
    const hours = Math.floor(totalMinutes / 60);
    const minutes = totalMinutes % 60;
    if (hours <= 0) return `${minutes}m`;
    return `${hours}h ${minutes}m`;
  }

  function renderStats() {
    const box = document.getElementById('study-stats');
    if (!box) return;
    const totalTopics = topics.length || 1;
    const done = topics.filter((t) => !!completed[t.id]).length;
    const avg = Math.round(stats.totalTimeMs / totalTopics);
    box.innerHTML = '';
    const title = document.createElement('h4');
    title.textContent = 'Estadísticas';
    const p1 = document.createElement('p');
    p1.textContent = `Tiempo total de estudio: ${formatDuration(stats.totalTimeMs)}`;
    const p2 = document.createElement('p');
    p2.textContent = `Temas completados: ${done} / ${topics.length}`;
    const p3 = document.createElement('p');
    p3.textContent = `Tiempo medio por tema: ${formatDuration(avg)}`;
    box.appendChild(title);
    box.appendChild(p1);
    box.appendChild(p2);
    box.appendChild(p3);
  }

  function exportProgress() {
    stopTopicTimer();
    const prefix = `sma:${courseId}:`;
    const data = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(prefix)) {
        data[key] = localStorage.getItem(key);
      }
    }

    const payload = {
      courseId: courseId,
      schemaVersion: 1,
      exportedAt: new Date().toISOString(),
      data: data
    };

    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${courseId}-progress.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  function importProgress() {
    const input = document.getElementById('study-import-input');
    if (!input) return;
    input.value = '';
    input.click();
  }

  function handleImportFileChange(event) {
    const input = event && event.target;
    if (!input || !input.files || !input.files.length) return;
    const file = input.files[0];
    if (!file) return;

    const lower = String(file.name || '').toLowerCase();
    if (!lower.endsWith('.json')) {
      alert('Archivo inválido o no compatible con este curso');
      return;
    }

    const reader = new FileReader();
    reader.onload = function () {
      let parsed = null;
      try {
        parsed = JSON.parse(String(reader.result || ''));
      } catch (_err) {
        alert('Archivo inválido o no compatible con este curso');
        return;
      }

      const validation = validateImportPayload(parsed);
      if (!validation.ok) {
        alert(validation.message || 'Archivo inválido o no compatible con este curso');
        return;
      }

      const confirmed = window.confirm('Esto reemplazará tu progreso actual de este curso. ¿Continuar?');
      if (!confirmed) return;

      const prefix = `sma:${courseId}:`;
      const keysToDelete = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith(prefix)) keysToDelete.push(key);
      }

      keysToDelete.forEach((k) => localStorage.removeItem(k));

      const data = parsed.data;
      Object.keys(data).forEach((key) => {
        localStorage.setItem(key, data[key]);
      });

      cloudSync.pushNow({ force: true }).finally(function () {
        alert('Progreso importado correctamente');
        window.location.reload();
      });
    };

    reader.onerror = function () {
      alert('Archivo inválido o no compatible con este curso');
    };

    reader.readAsText(file);
  }

  function validateImportPayload(payload) {
    if (!payload || typeof payload !== 'object') {
      return { ok: false, message: 'Archivo inválido o no compatible con este curso' };
    }

    if (!('courseId' in payload) || !('schemaVersion' in payload) || !('exportedAt' in payload) || !('data' in payload)) {
      return { ok: false, message: 'Archivo inválido o no compatible con este curso' };
    }

    if (String(payload.courseId) !== String(courseId)) {
      return { ok: false, message: 'El archivo no pertenece a este curso' };
    }

    if (!(payload.schemaVersion === 1 || String(payload.schemaVersion) === '1')) {
      return { ok: false, message: 'Versión de archivo no compatible' };
    }

    if (!payload.data || typeof payload.data !== 'object' || Array.isArray(payload.data)) {
      return { ok: false, message: 'Archivo inválido o no compatible con este curso' };
    }

    const prefix = `sma:${courseId}:`;
    const keys = Object.keys(payload.data);
    const invalid = keys.find((k) => !String(k).startsWith(prefix));
    if (invalid) {
      return { ok: false, message: 'Archivo inválido o no compatible con este curso' };
    }

    return { ok: true };
  }

  async function copySyncLink() {
    const profile = cloudSync.getProfileKey();
    if (!profile) {
      alert('No se pudo resolver profileKey para sincronización.');
      return;
    }

    const synced = await cloudSync.pushNow({ force: true });
    const url = buildSyncLink(profile, cloudSync.getSyncBaseUrl());
    try {
      if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
        await navigator.clipboard.writeText(url);
      } else {
        throw new Error('Clipboard API no disponible');
      }
      if (synced) {
        alert('Enlace de sincronización copiado y progreso sincronizado.');
      } else {
        alert('Enlace de sincronización copiado. No se pudo confirmar sincronización cloud en este momento.');
      }
    } catch (_error) {
      window.prompt('Copia este enlace para usar el mismo progreso en otro dispositivo:', url);
    }
  }

  async function resetProgress() {
    if (!window.confirm('Esto borrará tu progreso de este curso. ¿Deseas continuar?')) return;
    const prefix = `sma:${courseId}:`;
    const keys = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(prefix)) keys.push(key);
    }
    keys.forEach((k) => localStorage.removeItem(k));
    await cloudSync.pushNow({ force: true });
    window.location.reload();
  }

  function applyZen(isOn) {
    document.body.classList.toggle('study-ux-zen', isOn);
    if (zenBtn) {
      const fullLabel = isOn ? '🧘 Salir enfoque' : '🧘 Enfoque';
      const compactLabel = isOn ? '🧘 Salir' : '🧘 Zen';
      zenBtn.textContent = isCompactMobileViewport() ? compactLabel : fullLabel;
      zenBtn.setAttribute('aria-label', fullLabel);
      zenBtn.title = fullLabel;
    }
  }

  function restoreScrollForTopic(topicId) {
    const value = scrollMap[topicId];
    const top = typeof value === 'number' ? value : 0;
    requestAnimationFrame(() => {
      setTimeout(() => {
        window.scrollTo({ top: top, behavior: 'auto' });
      }, 0);
    });
  }

  function normalizePath(path) {
    if (!path) return '';
    let p = String(path).trim();
    p = p.replace(/^file:\/\/[A-Za-z]:/i, '');
    p = p.replace(/^file:\/\//i, '');
    p = p.replace(/\\/g, '/');
    p = p.replace(/^\.\//, '');
    p = p.replace(/^\/+/, '');
    p = p.split('?')[0];
    return p;
  }

  function createCloudSync() {
    const state = {
      bootstrapped: false,
      enabled: false,
      profileKey: '',
      updatedAtKey: keyCloudUpdatedAtLegacy,
      pendingTimer: null,
      pushing: false,
      lastSnapshot: '',
      syncBaseUrl: ''
    };

    async function bootstrap() {
      if (state.bootstrapped) return;
      state.bootstrapped = true;
      const hasProfileInUrl = hasProgressProfileQuery();
      state.profileKey = await resolveProfileKey();
      if (!state.profileKey) return;
      state.updatedAtKey = resolveCloudUpdatedAtKey(state.profileKey);
      if (!hasProfileInUrl) {
        migrateLegacyUpdatedAt(state.updatedAtKey);
      }
      ensureProgressProfileQuery(state.profileKey);
      state.syncBaseUrl = resolveSyncBaseUrl();

      const config = await fetchConfig();
      state.enabled = !!(config && config.enabled);
      if (!state.enabled) return;

      await pull();
      schedulePush(1400);
    }

    function schedulePush(wait = 900) {
      if (!state.enabled || !state.profileKey) return;
      if (state.pendingTimer) clearTimeout(state.pendingTimer);
      state.pendingTimer = setTimeout(function () {
        void pushNow();
      }, wait);
    }

    async function pushNow(options = {}) {
      if (!state.enabled || !state.profileKey || state.pushing) return false;
      const payload = collectCloudPayload();
      const snapshot = stableSerialize(payload);
      if (!options.force && snapshot === state.lastSnapshot) return false;

      state.pushing = true;
      try {
        const headers = { 'Content-Type': 'application/json' };
        const bearer = getAuthAccessToken();
        if (bearer) headers.Authorization = `Bearer ${bearer}`;
        const response = await fetch(stateUrl(), {
          method: 'POST',
          headers: headers,
          body: JSON.stringify({
            courseId,
            profileKey: state.profileKey,
            clientUpdatedAt: new Date().toISOString(),
            data: payload
          })
        });

        if (!response.ok) return false;
        const body = await response.json().catch(function () { return null; });
        const updatedAt = body && body.state && body.state.updatedAt ? String(body.state.updatedAt) : '';
        if (updatedAt) localStorage.setItem(state.updatedAtKey, updatedAt);
        state.lastSnapshot = snapshot;
        return true;
      } catch (_error) {
        return false;
      } finally {
        state.pushing = false;
      }
    }

    async function pull() {
      const query = new URLSearchParams({
        courseId: courseId,
        profileKey: state.profileKey
      });
      try {
        const headers = {};
        const bearer = getAuthAccessToken();
        if (bearer) headers.Authorization = `Bearer ${bearer}`;
        const response = await fetch(`${stateUrl()}?${query.toString()}`, {
          method: 'GET',
          headers: headers
        });
        if (!response.ok) return false;
        const body = await response.json().catch(function () { return null; });
        if (!body || !body.ok || !body.state || !body.state.data || typeof body.state.data !== 'object') {
          return false;
        }

        const remoteData = body.state.data;
        const remoteUpdatedAt = toTimestamp(body.state.updatedAt);
        const localUpdatedAt = toTimestamp(localStorage.getItem(state.updatedAtKey));
        const shouldApply = remoteUpdatedAt > localUpdatedAt || isLocalPayloadEmpty();
        if (!shouldApply) {
          state.lastSnapshot = stableSerialize(collectCloudPayload());
          return false;
        }

        applyCloudPayload(remoteData);
        if (body.state.updatedAt) localStorage.setItem(state.updatedAtKey, String(body.state.updatedAt));
        state.lastSnapshot = stableSerialize(collectCloudPayload());
        return true;
      } catch (_error) {
        return false;
      }
    }

    function collectCloudPayload() {
      return {
        completed: readJson(keyCompleted, {}),
        review: readJson(keyReview, {}),
        lastTopic: localStorage.getItem(keyLastTopic) || '',
        stats: readJson(keyStats, {}),
        zen: localStorage.getItem(keyZen) === '1',
        fontSize: Number(localStorage.getItem(keyFontSize) || baseFontSize)
      };
    }

    function isLocalPayloadEmpty() {
      const payload = collectCloudPayload();
      const doneKeys = Object.keys(payload.completed || {});
      const reviewKeys = Object.keys(payload.review || {});
      const lastTopic = String(payload.lastTopic || '').trim();
      return doneKeys.length === 0 && reviewKeys.length === 0 && !lastTopic;
    }

    function applyCloudPayload(payload) {
      if (payload.completed && typeof payload.completed === 'object') {
        localStorage.setItem(keyCompleted, JSON.stringify(payload.completed));
      }
      if (payload.review && typeof payload.review === 'object') {
        localStorage.setItem(keyReview, JSON.stringify(payload.review));
      }
      if (typeof payload.lastTopic === 'string') {
        localStorage.setItem(keyLastTopic, payload.lastTopic);
      }
      if (payload.stats && typeof payload.stats === 'object') {
        localStorage.setItem(keyStats, JSON.stringify(payload.stats));
      }
      if (typeof payload.zen === 'boolean') {
        localStorage.setItem(keyZen, payload.zen ? '1' : '0');
      }
      if (Number.isFinite(Number(payload.fontSize))) {
        localStorage.setItem(keyFontSize, String(Number(payload.fontSize)));
      }

      replaceObject(completed, readJson(keyCompleted, {}));
      replaceObject(review, readJson(keyReview, {}));
      const refreshedStats = ensureStatsShape(readJson(keyStats, {}));
      stats.totalTimeMs = refreshedStats.totalTimeMs;
      stats.perTopicTimeMs = refreshedStats.perTopicTimeMs;
      stats.lastSessionStart = null;

      const targetTopic = resolveCurrentTopic(topics, location.hash, localStorage.getItem(keyLastTopic));
      if (targetTopic && currentTopic && targetTopic.id !== currentTopic.id) {
        renderTopic(targetTopic.id, true);
      } else {
        ensureTopicNavigation(currentTopic);
        updateCompletionUi();
        updateReviewUi();
        updateProgressUi();
        scheduleDecorateNavStates();
        applyReviewFilter();
        renderStats();
      }
      updateResumeButtonState();
    }

    async function resolveProfileKey() {
      const authUserId = getAuthUserId();
      if (isValidProfileKey(authUserId)) {
        localStorage.setItem(keyCloudProfile, authUserId);
        return authUserId;
      }

      const fromQuery = new URLSearchParams(location.search).get('progressProfile');
      if (isValidProfileKey(fromQuery)) {
        localStorage.setItem(keyCloudProfile, String(fromQuery));
        return String(fromQuery);
      }

      const fromWindow = String(
        (window.__SMA_PROGRESS_PROFILE || window.__SMA_PROGRESS_SHARED_PROFILE || '')
      ).trim();
      if (isValidProfileKey(fromWindow)) {
        localStorage.setItem(keyCloudProfile, fromWindow);
        return fromWindow;
      }

      const stored = localStorage.getItem(keyCloudProfile);
      if (isValidProfileKey(stored)) return stored;

      const generated = await fingerprintProfileKey();
      if (generated) localStorage.setItem(keyCloudProfile, generated);
      return generated;
    }

    function hasProgressProfileQuery() {
      return new URLSearchParams(location.search).has('progressProfile');
    }

    function ensureProgressProfileQuery(profileKey) {
      if (!isValidProfileKey(profileKey)) return;
      try {
        const current = new URL(location.href);
        if (current.searchParams.get('progressProfile') === profileKey) return;
        current.searchParams.set('progressProfile', profileKey);
        history.replaceState(history.state, '', `${current.pathname}${current.search}${current.hash}`);
      } catch (_error) {
        return;
      }
    }

    function resolveCloudUpdatedAtKey(profileKey) {
      const normalized = String(profileKey || '').trim().replace(/[^A-Za-z0-9._:-]/g, '_');
      if (!normalized) return keyCloudUpdatedAtLegacy;
      return `${keyCloudUpdatedAtByProfilePrefix}${normalized}`;
    }

    function migrateLegacyUpdatedAt(targetKey) {
      if (!targetKey || targetKey === keyCloudUpdatedAtLegacy) return;
      if (localStorage.getItem(targetKey)) return;
      const legacyValue = localStorage.getItem(keyCloudUpdatedAtLegacy);
      if (!legacyValue) return;
      localStorage.setItem(targetKey, legacyValue);
    }

    function resolveSyncBaseUrl() {
      const params = new URLSearchParams(location.search);
      const fromQuery = normalizeBaseUrl(
        params.get('progressBase') || params.get('progressEndpoint') || ''
      );
      if (fromQuery) {
        localStorage.setItem(keyCloudEndpoint, fromQuery);
        return fromQuery;
      }

      const fromWindow = normalizeBaseUrl(
        String(window.__SMA_PROGRESS_SYNC_BASE_URL || window.__SMA_PROGRESS_BASE_URL || '')
      );
      if (fromWindow) {
        localStorage.setItem(keyCloudEndpoint, fromWindow);
        return fromWindow;
      }

      const fromStorage = normalizeBaseUrl(localStorage.getItem(keyCloudEndpoint) || '');
      if (fromStorage) return fromStorage;

      if (isLocalContext()) return DEFAULT_REMOTE_PROGRESS_BASE;
      return '';
    }

    async function fetchConfig() {
      try {
        const response = await fetch(configUrl(), { method: 'GET' });
        if (!response.ok) return { enabled: false };
        const body = await response.json().catch(function () { return null; });
        if (!body || typeof body !== 'object') return { enabled: false };
        return body;
      } catch (_error) {
        return { enabled: false };
      }
    }

    function configUrl() {
      return buildProgressUrl(state.syncBaseUrl, '/progress/config');
    }

    function stateUrl() {
      return buildProgressUrl(state.syncBaseUrl, '/progress/state');
    }

    function stableSerialize(value) {
      try {
        return JSON.stringify(value);
      } catch (_error) {
        return '';
      }
    }

    function toTimestamp(value) {
      const date = new Date(String(value || ''));
      const time = date.getTime();
      return Number.isFinite(time) ? time : 0;
    }

    function isValidProfileKey(value) {
      const key = String(value || '').trim();
      if (!key) return false;
      if (key.length > 128) return false;
      return /^[A-Za-z0-9._:-]+$/.test(key);
    }

    async function fingerprintProfileKey() {
      const parts = [
        navigator.userAgent || '',
        navigator.language || '',
        (navigator.languages || []).join(','),
        navigator.platform || '',
        String(navigator.hardwareConcurrency || ''),
        String(navigator.deviceMemory || ''),
        String(screen.width || ''),
        String(screen.height || ''),
        String(screen.colorDepth || ''),
        String(window.devicePixelRatio || ''),
        Intl.DateTimeFormat().resolvedOptions().timeZone || ''
      ];
      const source = parts.join('|');
      const digest = await sha256Hex(source);
      if (!digest) return `pf-${fallbackHash(source)}`;
      return `pf-${digest.slice(0, 48)}`;
    }

    async function sha256Hex(text) {
      if (!window.crypto || !window.crypto.subtle || typeof TextEncoder === 'undefined') return '';
      try {
        const bytes = new TextEncoder().encode(text);
        const hash = await window.crypto.subtle.digest('SHA-256', bytes);
        const list = Array.from(new Uint8Array(hash));
        return list.map((n) => n.toString(16).padStart(2, '0')).join('');
      } catch (_error) {
        return '';
      }
    }

    function fallbackHash(text) {
      let value = 2166136261;
      for (let i = 0; i < text.length; i += 1) {
        value ^= text.charCodeAt(i);
        value += (value << 1) + (value << 4) + (value << 7) + (value << 8) + (value << 24);
      }
      return Math.abs(value >>> 0).toString(16).padStart(8, '0');
    }

    function replaceObject(target, source) {
      Object.keys(target).forEach((key) => {
        delete target[key];
      });
      Object.keys(source || {}).forEach((key) => {
        target[key] = source[key];
      });
    }

    return {
      bootstrap,
      schedulePush,
      pushNow,
      getProfileKey: function () { return state.profileKey; },
      getSyncBaseUrl: function () { return state.syncBaseUrl; }
    };
  }

  function buildAuthUrl() {
    const base = deriveHubBase();
    if (base) return `${base}/auth/index.html`;
    if (location.protocol === 'http:' || location.protocol === 'https:') return '/auth/index.html';
    return 'https://architecture-stack.vercel.app/auth/index.html';
  }

  function deriveHubBase() {
    const href = String(window.location.href || '');
    if (href.indexOf('/ios/') !== -1) return href.split('/ios/')[0];
    if (href.indexOf('/android/') !== -1) return href.split('/android/')[0];
    if (href.indexOf('/sdd/') !== -1) return href.split('/sdd/')[0];
    return '';
  }

  function getAuthUserId() {
    const user = readJson(keyAuthUser, null);
    if (!user || typeof user !== 'object') return '';
    const id = String(user.id || '').trim();
    return id;
  }

  function getAuthAccessToken() {
    const session = readJson(keyAuthSession, null);
    if (!session || typeof session !== 'object') return '';
    const token = String(session.accessToken || '').trim();
    if (!token || token.length > 4096) return '';
    return token;
  }

  function buildSyncLink(profileKey, syncBaseUrl) {
    const url = new URL(window.location.href);
    url.searchParams.set('progressProfile', profileKey);
    const normalizedBase = normalizeBaseUrl(syncBaseUrl || '');
    if (normalizedBase && isLocalContext()) {
      url.searchParams.set('progressBase', normalizedBase);
    }
    return url.toString();
  }

  function buildProgressUrl(baseUrl, path) {
    const cleanPath = String(path || '').startsWith('/') ? String(path) : `/${String(path || '')}`;
    const normalized = normalizeBaseUrl(baseUrl || '');
    if (!normalized) return cleanPath;
    return `${normalized}${cleanPath}`;
  }

  function normalizeBaseUrl(value) {
    const raw = String(value || '').trim();
    if (!raw) return '';
    try {
      const parsed = new URL(raw);
      return `${parsed.protocol}//${parsed.host}`;
    } catch (_error) {
      return '';
    }
  }

  function isLocalContext() {
    return location.protocol === 'file:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1';
  }

  function readJson(key, fallback) {
    const raw = localStorage.getItem(key);
    if (!raw) return fallback;
    try {
      const parsed = JSON.parse(raw);
      return parsed && typeof parsed === 'object' ? parsed : fallback;
    } catch (_err) {
      return fallback;
    }
  }

  function debounce(fn, wait) {
    let t = null;
    return function () {
      const args = arguments;
      clearTimeout(t);
      t = setTimeout(function () {
        fn.apply(null, args);
      }, wait);
    };
  }

  window.toggleReview = toggleReview;
  window.startTopicTimer = startTopicTimer;
  window.stopTopicTimer = stopTopicTimer;
  window.exportProgress = exportProgress;
  window.resetProgress = resetProgress;
})();
