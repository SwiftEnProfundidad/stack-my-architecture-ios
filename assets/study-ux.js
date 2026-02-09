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
  setupTopBarLayout();

  const reviewBtn = ensureReviewTopButton();

  setupFontControls();
  applySavedFontSize();
  reorderTopControls();
  observeTopControlsOrder();

  let currentTopic = resolveCurrentTopic(topics, location.hash, localStorage.getItem(keyLastTopic));
  if (!currentTopic) return;

  renderTopic(currentTopic.id, false);
  applyZen(localStorage.getItem(keyZen) === '1');
  updateCompletionUi();
  updateReviewUi();
  updateProgressUi();
  decorateNavStates();
  setupButtons();
  setupShortcuts();
  setupScrollPersistence();
  setupIndexActions();
  startTopicTimer(currentTopic.id);

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

  function ensureStatsShape(raw) {
    return {
      totalTimeMs: Number(raw.totalTimeMs || 0),
      perTopicTimeMs: raw.perTopicTimeMs && typeof raw.perTopicTimeMs === 'object' ? raw.perTopicTimeMs : {},
      lastSessionStart: null
    };
  }

  function persistStats() {
    localStorage.setItem(keyStats, JSON.stringify(stats));
  }

  function setupTopBarLayout() {
    const body = document.body;
    const bar = document.createElement('div');
    bar.id = 'global-topbar';
    bar.className = 'global-topbar';

    const switcher = document.getElementById('course-switcher');
    const study = document.getElementById('study-ux-controls');
    const theme = document.getElementById('theme-controls');

    if (switcher) bar.appendChild(switcher);
    if (study) bar.appendChild(study);
    if (theme) bar.appendChild(theme);

    body.insertBefore(bar, body.firstChild);
    body.classList.add('with-global-topbar');
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
    document.documentElement.style.fontSize = `${next}px`;
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
  }

  function observeTopControlsOrder() {
    const controls = document.getElementById('study-ux-controls');
    if (!controls || typeof MutationObserver === 'undefined') return;

    const observer = new MutationObserver(function () {
      reorderTopControls();
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

  function mapLinksToTopics(links, topicList) {
    links.forEach((link) => {
      const target = (link.getAttribute('href') || '').replace('#', '');
      const topic = topicList.find((t) => t.id === target);
      if (topic) {
        link.dataset.topicId = topic.id;
      }
    });
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

  function ensureTopicNavigation() {
    topics.forEach((topic, index) => {
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
    });
  }

  function renderTopic(topicId, shouldRestoreScroll) {
    const target = topics.find((t) => t.id === topicId);
    if (!target) return;

    stopTopicTimer();

    topics.forEach((t) => {
      t.section.style.display = t.id === topicId ? '' : 'none';
    });

    navLinks.forEach((link) => {
      const active = link.dataset.topicId === topicId;
      link.classList.toggle('study-nav-active', active);
      if (active) link.scrollIntoView({ block: 'nearest' });
    });

    currentTopic = target;
    localStorage.setItem(keyLastTopic, currentTopic.id);

    if (location.hash.replace('#', '') !== currentTopic.id) {
      history.replaceState(null, '', `#${currentTopic.id}`);
    }

    ensureTopicNavigation();
    updateCompletionUi();
    updateReviewUi();
    updateProgressUi();

    if (shouldRestoreScroll) {
      restoreScrollForTopic(currentTopic.id);
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

  function setupIndexActions() {
    if (!indexActions) return;
    indexActions.innerHTML = '';

    const rowPrimary = document.createElement('div');
    rowPrimary.className = 'study-ux-index-row';
    rowPrimary.appendChild(createButton('▶ Continuar donde lo dejaste', goResume, 'study-resume-btn'));
    rowPrimary.appendChild(createButton('➡ Ir al primer tema pendiente', goFirstIncomplete));
    rowPrimary.appendChild(createButton('🔁 Mostrar solo temas para repaso', toggleReviewFilter, 'study-filter-review'));

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
    ensureTopicNavigation();
    updateCompletionUi();
    updateProgressUi();
    decorateNavStates();
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
    updateReviewUi();
    decorateNavStates();
    applyReviewFilter();
    renderStats();
  }

  function updateCompletionUi() {
    if (!completionBtn || !currentTopic) return;
    completionBtn.textContent = completed[currentTopic.id] ? '↩ Desmarcar' : '✅ Marcar completado';
  }

  function updateReviewUi() {
    if (!reviewBtn || !currentTopic) return;
    reviewBtn.textContent = review[currentTopic.id] ? '❌ Quitar repaso' : '🔁 Marcar para repaso';
  }

  function updateProgressUi() {
    const total = topics.length;
    const done = topics.filter((t) => !!completed[t.id]).length;
    const percent = total === 0 ? 0 : Math.round((done / total) * 100);
    if (progressEl) {
      progressEl.textContent = `Progreso: ${done}/${total} (${percent}%)`;
    }
  }

  function decorateNavStates() {
    navLinks.forEach((link) => {
      const topicId = link.dataset.topicId;
      if (!topicId) return;

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

      alert('Progreso importado correctamente');
      window.location.reload();
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

  function resetProgress() {
    if (!window.confirm('Esto borrará tu progreso de este curso. ¿Deseas continuar?')) return;
    const prefix = `sma:${courseId}:`;
    const keys = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(prefix)) keys.push(key);
    }
    keys.forEach((k) => localStorage.removeItem(k));
    window.location.reload();
  }

  function applyZen(isOn) {
    document.body.classList.toggle('study-ux-zen', isOn);
    if (zenBtn) {
      zenBtn.textContent = isOn ? '🧘 Salir enfoque' : '🧘 Enfoque';
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
