; (function () {
    var STORAGE_PREFIX = 'sma:assistant:';
    var KEY_OPEN = STORAGE_PREFIX + 'open';
    var KEY_MESSAGES = STORAGE_PREFIX + 'messages';
    var KEY_MODEL = STORAGE_PREFIX + 'model';
    var KEY_MAX_TOKENS = STORAGE_PREFIX + 'max_tokens';
    var KEY_PROXY_BASE = STORAGE_PREFIX + 'proxy_base';

    var state = {
        isOpen: localStorage.getItem(KEY_OPEN) === '1',
        model: localStorage.getItem(KEY_MODEL) || 'gpt-4o-mini',
        maxTokens: Number(localStorage.getItem(KEY_MAX_TOKENS) || 600),
        proxyBase: normalizeProxyBase(localStorage.getItem(KEY_PROXY_BASE) || defaultProxyBase()),
        messages: readMessages(),
        pendingAttachments: [],
        isLoading: false,
        metrics: null,
        availableModels: ['gpt-5.3', 'gpt-5.2', 'gpt-4o-mini', 'gpt-4.1-mini'],
        maxAttachments: 3,
        maxImageBytes: 5 * 1024 * 1024,
        allowedImageTypes: ['image/png', 'image/jpeg', 'image/webp'],
        visionModels: ['gpt-4o-mini']
    };

    var refs = {
        panel: null,
        body: null,
        textarea: null,
        status: null,
        modelSelect: null,
        tokensInput: null,
        proxyInput: null,
        metricsBox: null,
        sendBtn: null,
        attachBtn: null,
        fileInput: null,
        attachmentsBox: null
    };

    function readMessages() {
        try {
            var raw = localStorage.getItem(KEY_MESSAGES);
            var parsed = raw ? JSON.parse(raw) : [];
            return Array.isArray(parsed) ? parsed.slice(-40) : [];
        } catch (_err) {
            return [];
        }
    }

    function persistMessages() {
        var compact = state.messages.slice(-40).map(function (msg) {
            return {
                role: msg.role,
                text: msg.text,
                at: msg.at
            };
        });
        localStorage.setItem(KEY_MESSAGES, JSON.stringify(compact));
    }

    function saveConfig() {
        localStorage.setItem(KEY_MODEL, state.model);
        localStorage.setItem(KEY_MAX_TOKENS, String(state.maxTokens));
        localStorage.setItem(KEY_PROXY_BASE, state.proxyBase);
    }

    function setOpen(isOpen) {
        state.isOpen = !!isOpen;
        localStorage.setItem(KEY_OPEN, state.isOpen ? '1' : '0');
        if (state.isOpen) document.body.classList.add('sma-assistant-open');
        else document.body.classList.remove('sma-assistant-open');
    }

    function createPanel() {
        var panel = document.createElement('aside');
        panel.className = 'sma-assistant-panel';
        panel.setAttribute('aria-label', 'Panel de asistente IA');

        var header = document.createElement('div');
        header.className = 'sma-assistant-header';
        var title = document.createElement('div');
        title.className = 'sma-assistant-header-title';
        title.textContent = '💬 Asistente';
        var closeBtn = document.createElement('button');
        closeBtn.type = 'button';
        closeBtn.textContent = 'Cerrar';
        closeBtn.addEventListener('click', function () {
            setOpen(false);
        });
        header.appendChild(title);
        header.appendChild(closeBtn);

        var config = document.createElement('details');
        config.className = 'sma-assistant-config';
        var summary = document.createElement('summary');
        summary.textContent = 'Configuración IA';
        config.appendChild(summary);

        var grid = document.createElement('div');
        grid.className = 'sma-assistant-config-grid';

        var modelLabel = document.createElement('label');
        modelLabel.textContent = 'Modelo';
        var modelSelect = document.createElement('select');
        state.availableModels.forEach(function (m) {
            var option = document.createElement('option');
            option.value = m;
            option.textContent = m;
            modelSelect.appendChild(option);
        });
        modelSelect.value = state.model;
        modelSelect.addEventListener('change', function () {
            state.model = modelSelect.value;
            saveConfig();
        });
        modelLabel.appendChild(modelSelect);

        var tokensLabel = document.createElement('label');
        tokensLabel.textContent = 'Máx tokens (recomendado 600)';
        var tokensInput = document.createElement('input');
        tokensInput.type = 'number';
        tokensInput.min = '100';
        tokensInput.max = '1200';
        tokensInput.step = '50';
        tokensInput.value = String(state.maxTokens);
        tokensInput.addEventListener('change', function () {
            var value = Number(tokensInput.value || 600);
            if (!value || value < 100) value = 600;
            if (value > 1200) value = 1200;
            state.maxTokens = value;
            tokensInput.value = String(value);
            saveConfig();
        });
        tokensLabel.appendChild(tokensInput);

        var proxyLabel = document.createElement('label');
        proxyLabel.textContent = 'Proxy local';
        var proxyInput = document.createElement('input');
        proxyInput.type = 'text';
        proxyInput.autocomplete = 'off';
        proxyInput.placeholder = 'http://localhost:8787';
        proxyInput.value = state.proxyBase;
        proxyInput.addEventListener('change', function () {
            state.proxyBase = String(proxyInput.value || '').trim() || 'http://localhost:8787';
            proxyInput.value = state.proxyBase;
            saveConfig();
            refreshMetrics();
        });
        proxyLabel.appendChild(proxyInput);

        grid.appendChild(modelLabel);
        grid.appendChild(tokensLabel);
        grid.appendChild(proxyLabel);
        config.appendChild(grid);

        var metricsBox = document.createElement('div');
        metricsBox.className = 'sma-assistant-metrics';
        metricsBox.textContent = 'Métricas: cargando…';
        config.appendChild(metricsBox);

        var body = document.createElement('div');
        body.className = 'sma-assistant-body';

        var footer = document.createElement('div');
        footer.className = 'sma-assistant-footer';

        var attachmentsBox = document.createElement('div');
        attachmentsBox.className = 'assistant-attachments is-empty';

        var textarea = document.createElement('textarea');
        textarea.placeholder = 'Pregunta algo sobre el contenido seleccionado o sobre el tema actual.';

        var fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/png,image/jpeg,image/webp';
        fileInput.multiple = true;
        fileInput.style.display = 'none';
        fileInput.addEventListener('change', function () {
            handleSelectedFiles(fileInput.files);
            fileInput.value = '';
        });

        var actions = document.createElement('div');
        actions.className = 'sma-assistant-footer-actions';
        var attachBtn = document.createElement('button');
        attachBtn.type = 'button';
        attachBtn.textContent = '📎 Adjuntar imágenes';
        attachBtn.addEventListener('click', function () {
            if (state.isLoading) return;
            if (!refs.fileInput) return;
            refs.fileInput.click();
        });
        var clearBtn = document.createElement('button');
        clearBtn.type = 'button';
        clearBtn.textContent = 'Limpiar';
        clearBtn.addEventListener('click', function () {
            state.messages = [];
            persistMessages();
            renderMessages();
            setStatus('Conversación vacía.');
        });
        var sendBtn = document.createElement('button');
        sendBtn.type = 'button';
        sendBtn.textContent = 'Consultar';
        sendBtn.addEventListener('click', function () {
            submitQuestion(textarea.value);
        });
        actions.appendChild(attachBtn);
        actions.appendChild(clearBtn);
        actions.appendChild(sendBtn);
        var status = document.createElement('div');
        status.className = 'sma-assistant-status';
        footer.appendChild(attachmentsBox);
        footer.appendChild(textarea);
        footer.appendChild(fileInput);
        footer.appendChild(actions);
        footer.appendChild(status);

        panel.appendChild(header);
        panel.appendChild(config);
        panel.appendChild(body);
        panel.appendChild(footer);
        document.body.appendChild(panel);

        refs.panel = panel;
        refs.body = body;
        refs.textarea = textarea;
        refs.status = status;
        refs.modelSelect = modelSelect;
        refs.tokensInput = tokensInput;
        refs.proxyInput = proxyInput;
        refs.metricsBox = metricsBox;
        refs.sendBtn = sendBtn;
        refs.attachBtn = attachBtn;
        refs.fileInput = fileInput;
        refs.attachmentsBox = attachmentsBox;

        setOpen(state.isOpen);
        renderMessages();
        renderPendingAttachments();
        setStatus('Listo. Selecciona texto o escribe una consulta.');
        fetchBridgeConfig();
        refreshMetrics();
    }

    function pushMessage(role, text, attachments) {
        state.messages.push({
            role: role,
            text: String(text || ''),
            at: Date.now(),
            attachments: Array.isArray(attachments) ? attachments.slice(0, state.maxAttachments) : []
        });
        if (state.messages.length > 40) state.messages = state.messages.slice(-40);
        persistMessages();
        renderMessages();
    }

    function renderMessages() {
        if (!refs.body) return;
        refs.body.innerHTML = '';
        if (!state.messages.length) {
            var empty = document.createElement('div');
            empty.className = 'sma-assistant-msg assistant';
            empty.textContent = 'Sin mensajes todavía.';
            refs.body.appendChild(empty);
            return;
        }
        state.messages.forEach(function (msg) {
            var row = document.createElement('div');
            row.className = 'sma-assistant-msg ' + (msg.role === 'user' ? 'user' : 'assistant');

            var textBlock = document.createElement('div');
            textBlock.className = 'assistant-msg-text';
            textBlock.textContent = msg.text;
            row.appendChild(textBlock);

            if (Array.isArray(msg.attachments) && msg.attachments.length) {
                var images = document.createElement('div');
                images.className = 'assistant-msg-images';
                msg.attachments.forEach(function (att) {
                    var item = document.createElement('div');
                    item.className = 'assistant-msg-image-item';
                    var img = document.createElement('img');
                    img.src = att.dataUrl;
                    img.alt = att.name || 'Imagen adjunta';
                    var cap = document.createElement('div');
                    cap.className = 'assistant-msg-image-caption';
                    cap.textContent = att.name || 'imagen';
                    item.appendChild(img);
                    item.appendChild(cap);
                    images.appendChild(item);
                });
                row.appendChild(images);
            }

            refs.body.appendChild(row);
        });
        refs.body.scrollTop = refs.body.scrollHeight;
    }

    function setLoadingState(isLoading) {
        state.isLoading = !!isLoading;
        if (refs.sendBtn) {
            refs.sendBtn.disabled = state.isLoading;
            refs.sendBtn.textContent = state.isLoading ? 'Enviando…' : 'Consultar';
        }
        if (refs.attachBtn) refs.attachBtn.disabled = state.isLoading;
    }

    function formatBytes(size) {
        var n = Number(size || 0);
        if (n < 1024) return n + ' B';
        if (n < 1024 * 1024) return (n / 1024).toFixed(1) + ' KB';
        return (n / (1024 * 1024)).toFixed(2) + ' MB';
    }

    function supportsVisionModel(model) {
        return state.visionModels.indexOf(String(model || '').trim()) >= 0;
    }

    function renderPendingAttachments() {
        if (!refs.attachmentsBox) return;

        refs.attachmentsBox.innerHTML = '';
        if (!state.pendingAttachments.length) {
            refs.attachmentsBox.classList.add('is-empty');
            return;
        }
        refs.attachmentsBox.classList.remove('is-empty');

        state.pendingAttachments.forEach(function (att) {
            var row = document.createElement('div');
            row.className = 'assistant-image-preview';

            var thumb = document.createElement('img');
            thumb.className = 'assistant-image-thumb';
            thumb.src = att.dataUrl;
            thumb.alt = att.name || 'Imagen';

            var info = document.createElement('div');
            info.className = 'assistant-image-meta';
            var name = document.createElement('div');
            name.className = 'assistant-image-name';
            name.textContent = att.name;
            var size = document.createElement('div');
            size.className = 'assistant-image-size';
            size.textContent = formatBytes(att.size);
            info.appendChild(name);
            info.appendChild(size);

            var remove = document.createElement('button');
            remove.type = 'button';
            remove.className = 'assistant-image-remove';
            remove.textContent = '❌ Quitar';
            remove.setAttribute('data-attachment-id', att.id);
            remove.addEventListener('click', function () {
                state.pendingAttachments = state.pendingAttachments.filter(function (x) {
                    return x.id !== att.id;
                });
                renderPendingAttachments();
            });

            row.appendChild(thumb);
            row.appendChild(info);
            row.appendChild(remove);
            refs.attachmentsBox.appendChild(row);
        });
    }

    function readFileAsDataUrl(file) {
        return new Promise(function (resolve, reject) {
            var reader = new FileReader();
            reader.onload = function () { resolve(String(reader.result || '')); };
            reader.onerror = function () { reject(new Error('No se pudo leer la imagen.')); };
            reader.readAsDataURL(file);
        });
    }

    function downscaleDataUrl(dataUrl, mimeType) {
        return new Promise(function (resolve) {
            var image = new Image();
            image.onload = function () {
                if (image.width <= 1600) {
                    resolve(dataUrl);
                    return;
                }
                var ratio = 1600 / image.width;
                var canvas = document.createElement('canvas');
                canvas.width = 1600;
                canvas.height = Math.max(1, Math.round(image.height * ratio));
                var ctx = canvas.getContext('2d');
                if (!ctx) {
                    resolve(dataUrl);
                    return;
                }
                ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
                var outType = mimeType === 'image/png' || mimeType === 'image/webp' ? mimeType : 'image/jpeg';
                resolve(canvas.toDataURL(outType, 0.9));
            };
            image.onerror = function () {
                resolve(dataUrl);
            };
            image.src = dataUrl;
        });
    }

    function processImageFile(file) {
        var normalizedType = (file.type === 'image/jpg') ? 'image/jpeg' : file.type;
        return readFileAsDataUrl(file)
            .then(function (dataUrl) {
                return downscaleDataUrl(dataUrl, normalizedType);
            })
            .then(function (finalDataUrl) {
                return {
                    id: 'att-' + Date.now() + '-' + Math.random().toString(36).slice(2, 8),
                    name: file.name || 'imagen',
                    size: Number(file.size || 0),
                    type: normalizedType,
                    dataUrl: finalDataUrl
                };
            });
    }

    function handleSelectedFiles(fileList) {
        var files = Array.prototype.slice.call(fileList || []);
        if (!files.length) return;

        var remainingSlots = state.maxAttachments - state.pendingAttachments.length;
        if (remainingSlots <= 0) {
            setStatus('Solo puedes adjuntar hasta 3 imágenes por consulta.');
            return;
        }

        var rejected = [];
        var accepted = [];
        files.forEach(function (file) {
            var type = String(file.type || '').toLowerCase();
            if (type === 'image/jpg') type = 'image/jpeg';

            if (state.allowedImageTypes.indexOf(type) < 0) {
                rejected.push((file.name || 'archivo') + ': formato no permitido (usa PNG, JPG, JPEG o WEBP).');
                return;
            }
            if (Number(file.size || 0) > state.maxImageBytes) {
                rejected.push((file.name || 'archivo') + ': supera 5MB.');
                return;
            }
            accepted.push(file);
        });

        if (accepted.length > remainingSlots) {
            var ignored = accepted.length - remainingSlots;
            accepted = accepted.slice(0, remainingSlots);
            rejected.push('Has intentado adjuntar más de 3 imágenes. Se ignoraron ' + ignored + '.');
        }

        if (!accepted.length) {
            if (rejected.length) setStatus(rejected.join(' '));
            return;
        }

        Promise.all(accepted.map(processImageFile))
            .then(function (items) {
                state.pendingAttachments = state.pendingAttachments.concat(items).slice(0, state.maxAttachments);
                renderPendingAttachments();
                if (rejected.length) setStatus(rejected.join(' '));
                else setStatus('Imágenes adjuntadas: ' + state.pendingAttachments.length + '/3');
            })
            .catch(function () {
                setStatus('No se pudieron procesar las imágenes seleccionadas.');
            });
    }

    function buildMultimodalContent(question, attachments) {
        var content = [{ type: 'input_text', text: question }];
        (attachments || []).forEach(function (att) {
            content.push({ type: 'input_image', image_url: att.dataUrl });
        });
        return content;
    }

    function setStatus(text) {
        if (!refs.status) return;
        refs.status.textContent = text;
    }

    function defaultProxyBase() {
        var host = location && location.hostname ? location.hostname : '';
        if (host === 'localhost' || host === '127.0.0.1') {
            return 'http://localhost:8787';
        }
        return location.origin || 'http://localhost:8787';
    }

    function normalizeProxyBase(value) {
        var raw = String(value || '').trim();
        if (!raw) return defaultProxyBase();
        return raw.replace(/\/$/, '');
    }

    function renderMetrics(metrics) {
        state.metrics = metrics || null;
        if (!refs.metricsBox) return;
        if (!metrics) {
            refs.metricsBox.textContent = 'Métricas: no disponibles.';
            return;
        }

        var totalReq = Number(metrics.total_requests || 0);
        var totalTok = Number(metrics.total_tokens || 0);
        var totalCost = Number(metrics.total_estimated_cost_usd || 0);
        var dayCost = Number((metrics.daily || {}).estimated_cost_usd || 0);
        var budget = Number(metrics.soft_daily_budget_usd || 0);
        var budgetTxt = budget > 0 ? (dayCost.toFixed(4) + ' / ' + budget.toFixed(2) + ' USD') : (dayCost.toFixed(4) + ' USD');

        refs.metricsBox.innerHTML = [
            '<div><strong>Requests</strong>: ' + totalReq + '</div>',
            '<div><strong>Tokens</strong>: ' + totalTok + '</div>',
            '<div><strong>Coste total</strong>: ' + totalCost.toFixed(4) + ' USD</div>',
            '<div><strong>Coste diario</strong>: ' + budgetTxt + '</div>'
        ].join('');
    }

    function proxyUrl(path) {
        var base = normalizeProxyBase(state.proxyBase);
        return base + path;
    }

    function checkProxy(base) {
        return fetch(normalizeProxyBase(base) + '/health', { method: 'GET' })
            .then(function (res) { return res.ok; })
            .catch(function () { return false; });
    }

    function ensureProxyBaseReachable() {
        var current = normalizeProxyBase(state.proxyBase);
        return checkProxy(current).then(function (ok) {
            if (ok) return true;

            var host = location && location.hostname ? location.hostname : '';
            var isLocal = host === 'localhost' || host === '127.0.0.1';
            var fallback = 'http://localhost:8787';
            if (!isLocal || current === fallback) return false;

            return checkProxy(fallback).then(function (fallbackOk) {
                if (!fallbackOk) return false;
                state.proxyBase = fallback;
                if (refs.proxyInput) refs.proxyInput.value = fallback;
                saveConfig();
                setStatus('Proxy detectado automáticamente en ' + fallback);
                return true;
            });
        });
    }

    function fetchBridgeConfig() {
        return ensureProxyBaseReachable().then(function () {
            return fetch(proxyUrl('/config'));
        })
            .then(function (res) {
                if (!res.ok) throw new Error('HTTP ' + res.status);
                return res.json();
            })
            .then(function (cfg) {
                var models = Array.isArray(cfg.models) && cfg.models.length ? cfg.models : state.availableModels;
                state.availableModels = models;

                if (!models.includes(state.model)) {
                    state.model = cfg.default_model || models[0];
                    saveConfig();
                }

                if (refs.modelSelect) {
                    refs.modelSelect.innerHTML = '';
                    models.forEach(function (m) {
                        var option = document.createElement('option');
                        option.value = m;
                        option.textContent = m;
                        refs.modelSelect.appendChild(option);
                    });
                    refs.modelSelect.value = state.model;
                }

                if (cfg.max_tokens_default && !localStorage.getItem(KEY_MAX_TOKENS)) {
                    state.maxTokens = Number(cfg.max_tokens_default);
                    if (refs.tokensInput) refs.tokensInput.value = String(state.maxTokens);
                }
            })
            .catch(function () {
                setStatus('No se pudo cargar /config. Inicia el proxy: node assistant-bridge/server.js');
            });
    }

    function refreshMetrics() {
        return ensureProxyBaseReachable().then(function () {
            return fetch(proxyUrl('/metrics'));
        })
            .then(function (res) {
                if (!res.ok) throw new Error('HTTP ' + res.status);
                return res.json();
            })
            .then(function (metrics) {
                renderMetrics(metrics);
            })
            .catch(function () {
                renderMetrics(null);
            });
    }

    function buildPrompt(question) {
        return [
            'Eres un asistente de apoyo para un curso técnico.',
            'Responde en español, con claridad, en formato breve.',
            'No escribas bloques de código largos.',
            'No sustituyas al instructor ni redefinas arquitectura.',
            'Solo explica, aclara, compara y da ejemplos cortos.',
            '',
            'Pregunta del usuario:',
            question
        ].join('\n');
    }

    function submitQuestion(rawQuestion, metadata) {
        if (state.isLoading) return;
        var question = String(rawQuestion || '').trim();
        if (!question) {
            setStatus('Escribe una pregunta antes de consultar.');
            return;
        }

        if (state.pendingAttachments.length && !supportsVisionModel(state.model)) {
            setStatus('El modelo seleccionado no soporta imágenes. Usa gpt-4o-mini.');
            return;
        }

        var attachmentsSnapshot = state.pendingAttachments.slice(0, state.maxAttachments).map(function (att) {
            return {
                id: att.id,
                name: att.name,
                size: att.size,
                type: att.type,
                dataUrl: att.dataUrl
            };
        });

        pushMessage('user', question, attachmentsSnapshot);
        if (refs.textarea) refs.textarea.value = '';
        setLoadingState(true);
        setStatus('Enviando…');

        var payload = {
            question: question,
            model: state.model,
            maxTokens: state.maxTokens,
            courseId: metadata && metadata.courseId ? metadata.courseId : null,
            topicId: metadata && metadata.topicId ? metadata.topicId : null,
            selectedText: metadata && metadata.selectedText ? metadata.selectedText : null,
            surroundingContext: metadata && metadata.surroundingContext ? metadata.surroundingContext : null,
            images: attachmentsSnapshot.map(function (att) {
                return {
                    name: att.name,
                    type: att.type,
                    size: att.size,
                    dataUrl: att.dataUrl
                };
            }),
            input: [
                {
                    role: 'user',
                    content: buildMultimodalContent(question, attachmentsSnapshot)
                }
            ]
        };

        fetch(proxyUrl('/ask'), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
            .then(function (res) {
                if (!res.ok) {
                    throw new Error('HTTP ' + res.status);
                }
                return res.json();
            })
            .then(function (json) {
                var content = json && json.answer ? String(json.answer).trim() : '';
                if (!content) content = 'No se recibió contenido de respuesta.';

                if (json && json.model && refs.modelSelect && refs.modelSelect.value !== json.model) {
                    state.model = json.model;
                    refs.modelSelect.value = json.model;
                    saveConfig();
                }

                pushMessage('assistant', content);
                state.pendingAttachments = [];
                renderPendingAttachments();
                if (json && json.metrics) renderMetrics(json.metrics);

                if (json && json.warning) {
                    setStatus('Respuesta recibida con aviso: ' + json.warning);
                } else {
                    setStatus('Respuesta recibida.');
                }
            })
            .catch(function (err) {
                setStatus('Error al consultar: ' + (err && err.message ? err.message : 'desconocido'));
                alert('No se pudo completar la consulta. Revisa que el proxy local esté activo en ' + state.proxyBase + ' y ejecuta: node assistant-bridge/server.js');
            })
            .finally(function () {
                setLoadingState(false);
                refreshMetrics();
            });
    }

    window.SMAAssistantPanel = {
        open: function () { setOpen(true); },
        close: function () { setOpen(false); },
        toggle: function () { setOpen(!state.isOpen); },
        ask: function (question) {
            setOpen(true);
            submitQuestion(question);
        },
        askSelection: function (payload) {
            var question = 'Explícame este fragmento de forma simple y práctica.';
            setOpen(true);
            submitQuestion(question, payload || {});
        },
        prefill: function (question) {
            setOpen(true);
            if (refs.textarea) refs.textarea.value = String(question || '');
            if (refs.textarea) refs.textarea.focus();
        }
    };

    createPanel();
})();
