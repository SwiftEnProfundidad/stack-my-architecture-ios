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
        btn.addEventListener('click', function () {
            var payload = selectionPayload();
            hideSelectionButton(btn);
            if (!payload) return;
            if (window.SMAAssistantPanel) {
                window.SMAAssistantPanel.askSelection(payload);
            }
        });

        document.body.appendChild(btn);

        function showFromCurrentSelection() {
            var text = selectionText();
            if (!text) {
                hideSelectionButton(btn);
                return;
            }

            var sel = window.getSelection();
            if (!sel || sel.rangeCount === 0) {
                hideSelectionButton(btn);
                return;
            }

            var rect = sel.getRangeAt(0).getBoundingClientRect();
            if (!rect || (!rect.width && !rect.height)) {
                hideSelectionButton(btn);
                return;
            }

            btn.style.display = 'inline-block';
            btn.style.top = String(Math.max(8, rect.bottom + window.scrollY + 10)) + 'px';
            btn.style.left = String(Math.max(8, rect.left + window.scrollX)) + 'px';
        }

        document.addEventListener('selectionchange', showFromCurrentSelection);
        document.addEventListener('mouseup', showFromCurrentSelection);
        document.addEventListener('keyup', function (event) {
            if (event.key === 'Escape') {
                hideSelectionButton(btn);
                return;
            }
            showFromCurrentSelection();
        });

        document.addEventListener('click', function (event) {
            if (event.target === btn) return;
            var target = event.target;
            var panel = document.querySelector('.sma-assistant-panel');
            if (panel && panel.contains(target)) return;
            hideSelectionButton(btn);
        });

        document.addEventListener('scroll', function () {
            if (btn.style.display !== 'none') showFromCurrentSelection();
        }, true);
    }

    function hideSelectionButton(btn) {
        btn.style.display = 'none';
    }

    ensureAiButtonInControls();
    ensureSelectionButton();
})();
