; (function () {
    function ensureAiButtonInControls() {
        var controls = document.getElementById('study-ux-controls');
        if (!controls) return;
        if (document.getElementById('study-ai-open-btn')) return;

        var btn = document.createElement('button');
        btn.id = 'study-ai-open-btn';
        btn.type = 'button';
        btn.textContent = '💬 Asistente IA';
        btn.title = 'Abrir panel de asistente IA';
        btn.addEventListener('click', function () {
            if (window.SMAAssistantPanel) {
                window.SMAAssistantPanel.toggle();
            }
        });

        controls.appendChild(btn);
    }

    function selectionText() {
        var sel = window.getSelection ? window.getSelection() : null;
        if (!sel) return '';
        var text = String(sel.toString() || '').trim();
        if (!text) return '';
        if (text.length > 1200) text = text.slice(0, 1200);
        return text;
    }

    function currentCourseId() {
        var meta = document.querySelector('meta[name="course-id"]');
        return meta && meta.content ? String(meta.content).trim() : null;
    }

    function currentTopicId() {
        var hashId = String(location.hash || '').replace(/^#/, '').trim();
        if (hashId) return hashId;

        var targetLesson = document.querySelector('.lesson:target');
        if (targetLesson && targetLesson.id) return targetLesson.id;

        var selected = document.querySelector('.doc-nav-link.selected');
        if (selected) {
            var href = String(selected.getAttribute('href') || '').replace(/^#/, '').trim();
            if (href) return href;
        }

        return null;
    }

    function selectionPayload() {
        var text = selectionText();
        if (!text) return null;

        var sel = window.getSelection ? window.getSelection() : null;
        if (!sel || sel.rangeCount === 0) return null;

        var node = sel.anchorNode;
        var element = node && node.nodeType === 1 ? node : (node ? node.parentElement : null);
        var contextHost = element && element.closest ? element.closest('pre, code, p, li, blockquote, h1, h2, h3, h4') : null;
        var surrounding = contextHost ? String(contextHost.textContent || '').trim() : '';
        if (surrounding.length > 900) surrounding = surrounding.slice(0, 900);

        return {
            selectedText: text,
            surroundingContext: surrounding,
            courseId: currentCourseId(),
            topicId: currentTopicId()
        };
    }

    function ensureSelectionButton() {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'sma-assistant-selection-btn';
        btn.textContent = 'Consultar al asistente';
        btn.style.display = 'none';

        var HIDE_DELAY_MS = 1500;
        var hideTimer = null;
        var lastPayload = null;
        var lastRect = null;

        function cancelHideTimer() {
            if (hideTimer) {
                clearTimeout(hideTimer);
                hideTimer = null;
            }
        }

        function scheduleHide(clearPayload, delayMs) {
            cancelHideTimer();
            var delay = typeof delayMs === 'number' ? delayMs : HIDE_DELAY_MS;
            hideTimer = setTimeout(function () {
                hideSelectionButton(btn);
                if (clearPayload) {
                    lastPayload = null;
                    lastRect = null;
                }
            }, delay);
        }

        function normalizeRect(rect) {
            if (!rect) return null;
            return {
                top: Number(rect.top || 0),
                left: Number(rect.left || 0),
                bottom: Number(rect.bottom || 0),
                right: Number(rect.right || 0),
                width: Number(rect.width || 0),
                height: Number(rect.height || 0)
            };
        }

        function showButtonAt(rect) {
            if (!rect) return;
            btn.style.display = 'inline-block';

            var viewportWidth = window.innerWidth || document.documentElement.clientWidth || 0;
            var viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0;
            var offsetWidth = btn.offsetWidth || 0;
            var offsetHeight = btn.offsetHeight || 0;

            var left = Math.max(8, rect.left);
            var top = Math.max(8, rect.bottom + 10);

            if (viewportWidth > 24 && offsetWidth > 0) {
                left = Math.min(left, viewportWidth - offsetWidth - 8);
            }
            if (viewportHeight > 24 && offsetHeight > 0) {
                top = Math.min(top, viewportHeight - offsetHeight - 8);
            }

            btn.style.top = String(top) + 'px';
            btn.style.left = String(left) + 'px';
        }

        function showFromCurrentSelection() {
            var payload = selectionPayload();
            if (!payload) {
                if (lastPayload && lastRect) {
                    cancelHideTimer();
                    showButtonAt(lastRect);
                    scheduleHide(false);
                    return;
                }
                scheduleHide(true, 300);
                return;
            }

            var sel = window.getSelection();
            if (!sel || sel.rangeCount === 0) {
                if (lastPayload && lastRect) {
                    cancelHideTimer();
                    showButtonAt(lastRect);
                    scheduleHide(false);
                    return;
                }
                scheduleHide(true, 300);
                return;
            }

            var rect = sel.getRangeAt(0).getBoundingClientRect();
            if (!rect || (!rect.width && !rect.height)) {
                if (lastPayload && lastRect) {
                    cancelHideTimer();
                    showButtonAt(lastRect);
                    scheduleHide(false);
                    return;
                }
                scheduleHide(true, 300);
                return;
            }

            cancelHideTimer();
            lastPayload = payload;
            lastRect = normalizeRect(rect);
            showButtonAt(lastRect);
        }

        btn.addEventListener('mousedown', function (event) {
            event.preventDefault();
            cancelHideTimer();
        });

        btn.addEventListener('click', function () {
            cancelHideTimer();
            var payload = selectionPayload() || lastPayload;
            hideSelectionButton(btn);
            lastPayload = null;
            lastRect = null;
            if (!payload) return;
            if (window.SMAAssistantPanel) {
                window.SMAAssistantPanel.askSelection(payload);
            }
        });

        document.body.appendChild(btn);

        document.addEventListener('selectionchange', showFromCurrentSelection);
        document.addEventListener('mouseup', showFromCurrentSelection);
        document.addEventListener('keyup', function (event) {
            if (event.key === 'Escape') {
                cancelHideTimer();
                hideSelectionButton(btn);
                lastPayload = null;
                lastRect = null;
                return;
            }
            showFromCurrentSelection();
        });

        document.addEventListener('click', function (event) {
            if (event.target === btn) return;
            var target = event.target;
            var panel = document.querySelector('.sma-assistant-panel');
            if (panel && panel.contains(target)) return;
            if (selectionPayload()) {
                showFromCurrentSelection();
                return;
            }
            cancelHideTimer();
            hideSelectionButton(btn);
            lastPayload = null;
            lastRect = null;
        });

        document.addEventListener('scroll', function () {
            if (btn.style.display === 'none') return;
            var payload = selectionPayload();
            if (payload) {
                lastPayload = payload;
                showFromCurrentSelection();
                return;
            }
            scheduleHide(true, 250);
        }, true);
    }

    function hideSelectionButton(btn) {
        btn.style.display = 'none';
    }

    ensureAiButtonInControls();
    if (document.body && typeof MutationObserver !== 'undefined') {
        var observer = new MutationObserver(function () {
            ensureAiButtonInControls();
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }
    ensureSelectionButton();
})();
