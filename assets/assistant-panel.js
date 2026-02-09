; (function () {
    var STORAGE_PREFIX = 'sma:assistant:';
    var KEY_OPEN = STORAGE_PREFIX + 'open';
    var KEY_MESSAGES = STORAGE_PREFIX + 'messages';
    var KEY_MODEL = STORAGE_PREFIX + 'model';
    var KEY_MAX_TOKENS = STORAGE_PREFIX + 'max_tokens';
    var KEY_PROXY_BASE = STORAGE_PREFIX + 'proxy_base';

    var VISION_FALLBACK_MODEL = 'gpt-4o-mini';
    var MEMORY_RECENT_LIMIT = 8;
    var MEMORY_SUMMARY_LIMIT = 1800;
    var IMAGE_MAX_ATTACHMENTS = 3;
    var IMAGE_MAX_BYTES = 3 * 1024 * 1024;
    var IMAGE_MAX_DIMENSION = 1280;
    var SMALL_PNG_MAX_BYTES = 350 * 1024;
    var JPEG_QUALITY = 0.85;
    var DAILY_WARNING_DEFAULT = 0.25;

    var courseId = detectCourseId() || 'unknown';
    var KEY_MEMORY = 'sma:' + courseId + ':assistant:memory';

    var state = {
        isOpen: localStorage.getItem(KEY_OPEN) === '1',
        model: localStorage.getItem(KEY_MODEL) || 'gpt-4o-mini',
        maxTokens: Number(localStorage.getItem(KEY_MAX_TOKENS) || 600),
        proxyBase: normalizeProxyBase(localStorage.getItem(KEY_PROXY_BASE) || defaultProxyBase()),
        queryPath: '/assistant/query',
        messages: readMessages(),
        pendingAttachments: [],
        isLoading: false,
        metrics: null,
        lastRequest: null,
        dailyWarningUsd: DAILY_WARNING_DEFAULT,
        availableModels: ['gpt-5.3', 'gpt-5.2', 'gpt-5.2-codex', 'gpt-4o-mini', 'gpt-4.1-mini'],
        maxAttachments: IMAGE_MAX_ATTACHMENTS,
        maxImageBytes: IMAGE_MAX_BYTES,
        allowedImageTypes: ['image/png', 'image/jpeg'],
        visionModels: [VISION_FALLBACK_MODEL]
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
        attachmentsBox: null,
        attachmentsCounter: null,
        clearContextBtn: null
    };

    function detectCourseId() {
        var meta = document.querySelector('meta[name="course-id"]');
        if (!meta || !meta.content) return null;
        var value = String(meta.content || '').trim();
        return value || null;
    }

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

    function readMemory() {
        try {
            var raw = localStorage.getItem(KEY_MEMORY);
            var parsed = raw ? JSON.parse(raw) : {};
            return normalizeMemory(parsed);
        } catch (_err) {
            return normalizeMemory({});
        }
    }

    function normalizeMemory(memory) {
        var parsed = memory && typeof memory === 'object' ? memory : {};
        var summary = truncateText(String(parsed.conversation_summary || ''), MEMORY_SUMMARY_LIMIT);
        var recent = Array.isArray(parsed.recent_messages) ? parsed.recent_messages : [];
        var normalizedRecent = recent
            .map(function (item) {
                if (!item || typeof item !== 'object') return null;
                var role = item.role === 'assistant' ? 'assistant' : 'user';
                var text = truncateText(String(item.text || ''), 900);
                if (!text) return null;
                return {
                    role: role,
                    text: text,
                    at: Number(item.at || Date.now())
                };
            })
            .filter(Boolean)
            .slice(-MEMORY_RECENT_LIMIT);

        return {
            conversation_summary: summary,
            recent_messages: normalizedRecent
        };
    }

    function saveMemory(memory) {
        var normalized = normalizeMemory(memory);
        localStorage.setItem(KEY_MEMORY, JSON.stringify(normalized));
    }

    function clearMemory() {
        localStorage.removeItem(KEY_MEMORY);
        setStatus('Contexto del asistente limpiado.', 'success');
    }

    function updateMemoryWithTurn(userText, assistantText) {
        var memory = readMemory();
        var now = Date.now();

        memory.recent_messages.push({
            role: 'user',
            text: truncateText(String(userText || ''), 900),
            at: now
        });
        memory.recent_messages.push({
            role: 'assistant',
            text: truncateText(String(assistantText || ''), 900),
            at: now + 1
        });

        if (memory.recent_messages.length > MEMORY_RECENT_LIMIT) {
            var overflow = memory.recent_messages.slice(0, memory.recent_messages.length - MEMORY_RECENT_LIMIT);
            memory.recent_messages = memory.recent_messages.slice(-MEMORY_RECENT_LIMIT);

            var digest = overflow.map(function (item) {
                return (item.role === 'assistant' ? 'A: ' : 'U: ') + truncateText(item.text, 160);
            }).join(' ');

            var mergedSummary = [memory.conversation_summary, digest]
                .filter(Boolean)
                .join(' ')
                .trim();

            memory.conversation_summary = truncateText(mergedSummary, MEMORY_SUMMARY_LIMIT);
        }

        saveMemory(memory);
    }

    function buildMemoryPayload() {
        var memory = readMemory();
        return {
            conversation_summary: memory.conversation_summary,
            recent_messages: memory.recent_messages.map(function (item) {
                return {
                    role: item.role,
                    text: item.text
                };
            })
        };
    }

    function truncateText(value, maxLen) {
        var text = String(value || '').replace(/\s+/g, ' ').trim();
        if (!text) return '';
        if (!maxLen || text.length <= maxLen) return text;
        return text.slice(0, Math.max(1, maxLen - 1)).trim() + '…';
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
        proxyInput.placeholder = 'http://localhost:8090';
        proxyInput.value = state.proxyBase;
        proxyInput.addEventListener('change', function () {
            state.proxyBase = normalizeProxyBase(proxyInput.value);
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

        var attachmentsCounter = document.createElement('div');
        attachmentsCounter.className = 'assistant-attachments-summary';

        var attachmentsBox = document.createElement('div');
        attachmentsBox.className = 'assistant-attachments is-empty';

        var textarea = document.createElement('textarea');
        textarea.placeholder = 'Pregunta algo sobre el contenido seleccionado o sobre el tema actual.';

        var fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.className = 'assistant-file-input';
        fileInput.accept = 'image/png,image/jpeg';
        fileInput.multiple = true;
        fileInput.addEventListener('change', function () {
            handleSelectedFiles(fileInput.files);
            fileInput.value = '';
        });

        var actions = document.createElement('div');
        actions.className = 'sma-assistant-footer-actions';

        var attachBtn = document.createElement('button');
        attachBtn.type = 'button';
        attachBtn.textContent = '📎 Adjuntar imagen';
        attachBtn.addEventListener('click', function () {
            if (state.isLoading || !refs.fileInput) return;
            refs.fileInput.click();
        });

        var clearContextBtn = document.createElement('button');
        clearContextBtn.type = 'button';
        clearContextBtn.textContent = '🧹 Limpiar contexto';
        clearContextBtn.addEventListener('click', function () {
            clearMemory();
        });

        var clearBtn = document.createElement('button');
        clearBtn.type = 'button';
        clearBtn.textContent = 'Limpiar chat';
        clearBtn.addEventListener('click', function () {
            state.messages = [];
            persistMessages();
            renderMessages();
            setStatus('Conversación vacía.', 'success');
        });

        var sendBtn = document.createElement('button');
        sendBtn.type = 'button';
        sendBtn.textContent = 'Consultar';
        sendBtn.addEventListener('click', function () {
            submitQuestion(textarea.value);
        });

        actions.appendChild(attachBtn);
        actions.appendChild(clearContextBtn);
        actions.appendChild(clearBtn);
        actions.appendChild(sendBtn);

        var status = document.createElement('div');
        status.className = 'sma-assistant-status';

        footer.appendChild(attachmentsCounter);
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
        refs.attachmentsCounter = attachmentsCounter;
        refs.clearContextBtn = clearContextBtn;

        setOpen(state.isOpen);
        renderMessages();
        renderPendingAttachments();
        setStatus('Listo. Selecciona texto o escribe una consulta.');
        fetchBridgeConfig();
        refreshMetrics();
    }

    function escapeHtml(value) {
        return String(value || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
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
        if (refs.clearContextBtn) refs.clearContextBtn.disabled = state.isLoading;
    }

    function setStatus(text, tone) {
        if (!refs.status) return;
        refs.status.textContent = text;
        refs.status.className = 'sma-assistant-status';
        if (tone === 'warning') refs.status.classList.add('is-warning');
        if (tone === 'error') refs.status.classList.add('is-error');
        if (tone === 'success') refs.status.classList.add('is-success');
    }

    function formatBytes(size) {
        var n = Number(size || 0);
        if (n < 1024) return n + ' B';
        if (n < 1024 * 1024) return (n / 1024).toFixed(1) + ' KB';
        return (n / (1024 * 1024)).toFixed(2) + ' MB';
    }

    function normalizeProxyBase(value) {
        var raw = String(value || '').trim();
        if (!raw) return defaultProxyBase();
        return raw.replace(/\/$/, '');
    }

    function defaultProxyBase() {
        if (location.protocol === 'file:') return 'http://localhost:8090';
        var host = location && location.hostname ? location.hostname : '';
        if (host === 'localhost' || host === '127.0.0.1') return 'http://localhost:8090';
        var origin = String(location.origin || '').trim();
        if (!origin || origin === 'null') return 'http://localhost:8090';
        return origin;
    }

    function proxyCandidates() {
        var list = [
            normalizeProxyBase(state.proxyBase),
            defaultProxyBase(),
            'http://localhost:8090',
            'http://localhost:8787'
        ];

        if (location.protocol === 'http:' || location.protocol === 'https:') {
            var origin = normalizeProxyBase(location.origin);
            if (origin) list.push(origin);
        }

        return uniqueList(list.filter(Boolean));
    }

    function uniqueList(list) {
        var seen = {};
        var out = [];
        (list || []).forEach(function (item) {
            var key = String(item || '').trim();
            if (!key || seen[key]) return;
            seen[key] = true;
            out.push(key);
        });
        return out;
    }

    function supportsVisionModel(model) {
        return state.visionModels.indexOf(String(model || '').trim()) >= 0;
    }

    function updateAttachmentCounter(note, tone) {
        if (!refs.attachmentsCounter) return;
        refs.attachmentsCounter.className = 'assistant-attachments-summary';
        if (tone === 'warning') refs.attachmentsCounter.classList.add('is-warning');
        if (tone === 'error') refs.attachmentsCounter.classList.add('is-error');

        var base = 'Imágenes: ' + state.pendingAttachments.length + ' / ' + state.maxAttachments;
        refs.attachmentsCounter.textContent = note ? base + ' · ' + note : base;
    }

    function renderPendingAttachments(note, tone) {
        if (!refs.attachmentsBox) return;

        refs.attachmentsBox.innerHTML = '';
        if (!state.pendingAttachments.length) {
            refs.attachmentsBox.classList.add('is-empty');
        } else {
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
                size.textContent = formatBytes(att.size) + ' · ' + (att.type === 'image/png' ? 'PNG' : 'JPEG');

                info.appendChild(name);
                info.appendChild(size);

                var remove = document.createElement('button');
                remove.type = 'button';
                remove.className = 'assistant-image-remove';
                remove.textContent = '❌';
                remove.title = 'Quitar imagen';
                remove.setAttribute('data-attachment-id', att.id);
                remove.addEventListener('click', function () {
                    state.pendingAttachments = state.pendingAttachments.filter(function (item) {
                        return item.id !== att.id;
                    });
                    renderPendingAttachments();
                    setStatus('Imagen eliminada.', 'success');
                });

                row.appendChild(thumb);
                row.appendChild(info);
                row.appendChild(remove);
                refs.attachmentsBox.appendChild(row);
            });
        }

        updateAttachmentCounter(note, tone);
    }

    function readFileAsDataUrl(file) {
        return new Promise(function (resolve, reject) {
            var reader = new FileReader();
            reader.onload = function () { resolve(String(reader.result || '')); };
            reader.onerror = function () { reject(new Error('No se pudo leer la imagen.')); };
            reader.readAsDataURL(file);
        });
    }

    function readBlobAsDataUrl(blob) {
        return new Promise(function (resolve, reject) {
            var reader = new FileReader();
            reader.onload = function () { resolve(String(reader.result || '')); };
            reader.onerror = function () { reject(new Error('No se pudo convertir la imagen procesada.')); };
            reader.readAsDataURL(blob);
        });
    }

    function loadImageFromDataUrl(dataUrl) {
        return new Promise(function (resolve, reject) {
            var image = new Image();
            image.onload = function () { resolve(image); };
            image.onerror = function () { reject(new Error('No se pudo procesar la imagen seleccionada.')); };
            image.src = dataUrl;
        });
    }

    function canvasToBlob(canvas, type, quality) {
        return new Promise(function (resolve) {
            canvas.toBlob(function (blob) {
                resolve(blob || null);
            }, type, quality);
        });
    }

    function base64ByteLength(base64) {
        var normalized = String(base64 || '').replace(/\s+/g, '');
        if (!normalized) return 0;
        var padding = 0;
        if (normalized.endsWith('==')) padding = 2;
        else if (normalized.endsWith('=')) padding = 1;
        return Math.floor((normalized.length * 3) / 4) - padding;
    }

    function normalizeImageType(type) {
        var normalized = String(type || '').toLowerCase();
        if (normalized === 'image/jpg') normalized = 'image/jpeg';
        return normalized;
    }

    function compressImage(file) {
        var inputType = normalizeImageType(file.type);

        if (state.allowedImageTypes.indexOf(inputType) < 0) {
            return Promise.reject(new Error((file.name || 'archivo') + ': formato no permitido (solo PNG o JPEG).'));
        }

        return readFileAsDataUrl(file)
            .then(function (dataUrl) {
                return loadImageFromDataUrl(dataUrl).then(function (image) {
                    var width = image.width;
                    var height = image.height;
                    var maxSide = Math.max(width, height);
                    var scale = maxSide > IMAGE_MAX_DIMENSION ? (IMAGE_MAX_DIMENSION / maxSide) : 1;
                    var targetWidth = Math.max(1, Math.round(width * scale));
                    var targetHeight = Math.max(1, Math.round(height * scale));

                    var canvas = document.createElement('canvas');
                    canvas.width = targetWidth;
                    canvas.height = targetHeight;

                    var context = canvas.getContext('2d');
                    if (!context) {
                        throw new Error((file.name || 'archivo') + ': no se pudo inicializar canvas para compresión.');
                    }

                    context.drawImage(image, 0, 0, targetWidth, targetHeight);

                    var keepPng = inputType === 'image/png' && file.size <= SMALL_PNG_MAX_BYTES && scale >= 0.999;
                    var outputType = keepPng ? 'image/png' : 'image/jpeg';
                    var quality = keepPng ? 0.92 : JPEG_QUALITY;

                    return canvasToBlob(canvas, outputType, quality)
                        .then(function (blob) {
                            if (!blob) {
                                throw new Error((file.name || 'archivo') + ': no se pudo generar imagen comprimida.');
                            }

                            if (blob.size > state.maxImageBytes) {
                                throw new Error((file.name || 'archivo') + ': supera 3MB tras compresión.');
                            }

                            return readBlobAsDataUrl(blob).then(function (processedDataUrl) {
                                var base64 = String(processedDataUrl.split(',')[1] || '').trim();
                                var sizeBytes = base64ByteLength(base64);

                                if (!base64 || !sizeBytes) {
                                    throw new Error((file.name || 'archivo') + ': no se pudo serializar imagen en base64.');
                                }

                                if (sizeBytes > state.maxImageBytes) {
                                    throw new Error((file.name || 'archivo') + ': supera 3MB tras compresión.');
                                }

                                return {
                                    id: 'att-' + Date.now() + '-' + Math.random().toString(36).slice(2, 8),
                                    name: truncateText(file.name || 'imagen', 90),
                                    type: outputType,
                                    size: sizeBytes,
                                    data: base64,
                                    dataUrl: processedDataUrl
                                };
                            });
                        });
                });
            });
    }

    function handleSelectedFiles(fileList) {
        var files = Array.prototype.slice.call(fileList || []);
        if (!files.length) return;

        var remainingSlots = state.maxAttachments - state.pendingAttachments.length;
        if (remainingSlots <= 0) {
            setStatus('Solo puedes adjuntar hasta ' + state.maxAttachments + ' imágenes por consulta.', 'warning');
            updateAttachmentCounter('Límite alcanzado', 'warning');
            return;
        }

        var accepted = files.slice(0, remainingSlots);
        var ignoredCount = files.length - accepted.length;

        Promise.all(accepted.map(compressImage))
            .then(function (processed) {
                state.pendingAttachments = state.pendingAttachments.concat(processed).slice(0, state.maxAttachments);
                if (ignoredCount > 0) {
                    setStatus('Se ignoraron ' + ignoredCount + ' imagen(es) por superar el límite.', 'warning');
                    renderPendingAttachments('Se ignoraron ' + ignoredCount + ' imagen(es)', 'warning');
                    return;
                }
                setStatus('Imágenes listas para enviar.', 'success');
                renderPendingAttachments();
            })
            .catch(function (err) {
                var message = err && err.message ? err.message : 'No se pudieron procesar las imágenes.';
                setStatus(message, 'warning');
                renderPendingAttachments('Revisa el formato y tamaño', 'warning');
            });
    }

    function normalizeUsage(responseJson) {
        var usage = responseJson && responseJson.usage ? responseJson.usage : {};

        var inputTokens = Number(
            usage.inputTokens ||
            usage.input_tokens ||
            usage.prompt_tokens ||
            responseJson.inputTokens ||
            responseJson.input_tokens ||
            responseJson.prompt_tokens ||
            0
        );

        var outputTokens = Number(
            usage.outputTokens ||
            usage.output_tokens ||
            usage.completion_tokens ||
            responseJson.outputTokens ||
            responseJson.output_tokens ||
            responseJson.completion_tokens ||
            0
        );

        var totalTokens = Number(
            usage.totalTokens ||
            usage.total_tokens ||
            responseJson.totalTokens ||
            responseJson.total_tokens ||
            inputTokens + outputTokens
        );

        var estimatedCostUsd = Number(
            usage.estimatedCostUsd ||
            usage.estimated_cost_usd ||
            responseJson.estimatedCostUsd ||
            responseJson.estimated_cost_usd ||
            0
        );

        return {
            inputTokens: inputTokens,
            outputTokens: outputTokens,
            totalTokens: totalTokens,
            estimatedCostUsd: estimatedCostUsd
        };
    }

    function normalizeMetrics(metrics) {
        var input = metrics && typeof metrics === 'object' ? metrics : {};
        var daily = input.daily && typeof input.daily === 'object' ? input.daily : {};

        return {
            totalRequests: Number(input.total_requests || input.totalRequests || input.requests || 0),
            totalTokens: Number(input.total_tokens || input.totalTokens || 0),
            totalEstimatedCostUsd: Number(
                input.total_estimated_cost_usd ||
                input.totalEstimatedCostUsd ||
                input.session_total_cost_usd ||
                input.estimatedCostUsd ||
                0
            ),
            dailyCostUsd: Number(daily.estimated_cost_usd || daily.estimatedCostUsd || input.dailyCostUsd || 0),
            dailyImagesCount: Number(daily.images_count || daily.imagesCount || 0),
            softDailyBudgetUsd: Number(input.soft_daily_budget_usd || input.softDailyBudgetUsd || 0)
        };
    }

    function renderMetrics(metrics) {
        state.metrics = metrics || state.metrics;

        if (!refs.metricsBox) return;

        var normalized = normalizeMetrics(state.metrics || {});
        var last = state.lastRequest;
        var lines = [];

        if (last) {
            var modelLine = '<div><strong>Modelo activo</strong>: ' + escapeHtml(last.model || state.model) + '</div>';
            lines.push(modelLine);
            lines.push('<div><strong>Última consulta</strong>: ' + last.inputTokens + ' / ' + last.outputTokens + ' / ' + last.totalTokens + ' tokens</div>');
            lines.push('<div><strong>Coste última consulta</strong>: ' + Number(last.estimatedCostUsd || 0).toFixed(6) + ' USD</div>');
            lines.push('<div><strong>Consulta con imágenes</strong>: ' + (last.hasImages ? 'Sí (' + last.imagesCount + ')' : 'No') + '</div>');
            if (last.warning) {
                lines.push('<div class="assistant-metric-warning"><strong>Aviso</strong>: ' + escapeHtml(last.warning) + '</div>');
            }
        } else {
            lines.push('<div><strong>Modelo activo</strong>: ' + escapeHtml(state.model) + '</div>');
            lines.push('<div>Sin consultas recientes en esta sesión.</div>');
        }

        lines.push('<div><strong>Coste acumulado del día</strong>: ' + normalized.dailyCostUsd.toFixed(6) + ' USD</div>');
        lines.push('<div><strong>Coste total de sesión</strong>: ' + normalized.totalEstimatedCostUsd.toFixed(6) + ' USD</div>');
        lines.push('<div><strong>Requests totales</strong>: ' + normalized.totalRequests + '</div>');

        if (normalized.softDailyBudgetUsd > 0) {
            lines.push('<div><strong>Presupuesto diario</strong>: ' + normalized.dailyCostUsd.toFixed(6) + ' / ' + normalized.softDailyBudgetUsd.toFixed(2) + ' USD</div>');
        }

        if (normalized.dailyCostUsd >= state.dailyWarningUsd) {
            lines.push('<div class="assistant-metric-warning"><strong>Umbral diario</strong>: coste diario superior a ' + state.dailyWarningUsd.toFixed(2) + ' USD.</div>');
        }

        refs.metricsBox.innerHTML = lines.join('');
    }

    function proxyUrl(path) {
        var base = normalizeProxyBase(state.proxyBase);
        var normalizedPath = String(path || '').trim();
        if (!normalizedPath.startsWith('/')) normalizedPath = '/' + normalizedPath;
        return base + normalizedPath;
    }

    function checkProxy(base) {
        return fetch(normalizeProxyBase(base) + '/health', { method: 'GET' })
            .then(function (res) { return res.ok; })
            .catch(function () { return false; });
    }

    function ensureProxyBaseReachable() {
        var candidates = proxyCandidates();

        function probe(index) {
            if (index >= candidates.length) return Promise.resolve(false);
            var candidate = candidates[index];
            return checkProxy(candidate).then(function (ok) {
                if (!ok) return probe(index + 1);
                if (state.proxyBase !== candidate) {
                    state.proxyBase = candidate;
                    if (refs.proxyInput) refs.proxyInput.value = candidate;
                    saveConfig();
                }
                return true;
            });
        }

        return probe(0);
    }

    function queryPathCandidates() {
        return uniqueList([
            state.queryPath,
            '/assistant/query',
            '/ask'
        ]);
    }

    function parseJsonSafe(text) {
        try {
            return JSON.parse(text);
        } catch (_err) {
            return null;
        }
    }

    function postQueryWithFallback(payload, signal) {
        var paths = queryPathCandidates();

        function tryPath(index) {
            if (index >= paths.length) {
                return Promise.reject(new Error('No se encontró endpoint de consulta válido en el proxy.'));
            }

            var path = paths[index];
            return fetch(proxyUrl(path), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
                signal: signal
            }).then(function (res) {
                return res.text().then(function (text) {
                    var json = parseJsonSafe(text) || {};

                    if ((res.status === 404 || res.status === 405) && index + 1 < paths.length) {
                        return tryPath(index + 1);
                    }

                    if (!res.ok) {
                        var errorText = json.error || json.detail || ('HTTP ' + res.status);
                        throw new Error(String(errorText));
                    }

                    if (state.queryPath !== path) {
                        state.queryPath = path;
                    }

                    return json;
                });
            });
        }

        return tryPath(0);
    }

    function fetchBridgeConfig() {
        return ensureProxyBaseReachable()
            .then(function (ok) {
                if (!ok) {
                    setStatus('Asistente no disponible. Inicia open-proxy.command', 'warning');
                    return null;
                }
                return fetch(proxyUrl('/config'));
            })
            .then(function (res) {
                if (!res) return null;
                if (!res.ok) throw new Error('HTTP ' + res.status);
                return res.json();
            })
            .then(function (cfg) {
                if (!cfg) return;

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

                if (cfg.query_path || cfg.queryPath) {
                    state.queryPath = String(cfg.query_path || cfg.queryPath);
                }

                if (cfg.max_images || cfg.maxImages) {
                    state.maxAttachments = Math.max(1, Math.min(3, Number(cfg.max_images || cfg.maxImages) || IMAGE_MAX_ATTACHMENTS));
                }

                if (cfg.max_image_bytes || cfg.maxImageBytes) {
                    var maxBytesCfg = Number(cfg.max_image_bytes || cfg.maxImageBytes);
                    if (Number.isFinite(maxBytesCfg) && maxBytesCfg > 0) {
                        state.maxImageBytes = maxBytesCfg;
                    }
                }

                if (Array.isArray(cfg.vision_models) && cfg.vision_models.length) {
                    state.visionModels = cfg.vision_models.map(function (value) {
                        return String(value || '').trim();
                    }).filter(Boolean);
                }

                if (cfg.daily_warning_usd || cfg.dailyWarningUsd) {
                    var dailyWarn = Number(cfg.daily_warning_usd || cfg.dailyWarningUsd);
                    if (Number.isFinite(dailyWarn) && dailyWarn > 0) {
                        state.dailyWarningUsd = dailyWarn;
                    }
                }

                renderPendingAttachments();
            })
            .catch(function () {
                setStatus('Asistente no disponible. Inicia open-proxy.command', 'warning');
            });
    }

    function refreshMetrics() {
        return ensureProxyBaseReachable()
            .then(function (ok) {
                if (!ok) {
                    renderMetrics(null);
                    return null;
                }
                return fetch(proxyUrl('/metrics'));
            })
            .then(function (res) {
                if (!res) return null;
                if (!res.ok) throw new Error('HTTP ' + res.status);
                return res.json();
            })
            .then(function (metrics) {
                if (!metrics) return;
                renderMetrics(metrics);
            })
            .catch(function () {
                renderMetrics(null);
            });
    }

    function extractAnswer(responseJson) {
        if (responseJson && typeof responseJson.answer === 'string' && responseJson.answer.trim()) {
            return responseJson.answer.trim();
        }

        if (responseJson && typeof responseJson.output_text === 'string' && responseJson.output_text.trim()) {
            return responseJson.output_text.trim();
        }

        if (responseJson && responseJson.data && typeof responseJson.data.answer === 'string') {
            var answer = String(responseJson.data.answer || '').trim();
            if (answer) return answer;
        }

        return 'No se recibió contenido de respuesta.';
    }

    function collectContext(metadata) {
        return {
            courseId: metadata && metadata.courseId ? metadata.courseId : courseId,
            topicId: metadata && metadata.topicId ? metadata.topicId : null,
            selectedText: metadata && metadata.selectedText ? metadata.selectedText : null,
            surroundingContext: metadata && metadata.surroundingContext ? metadata.surroundingContext : null
        };
    }

    function submitQuestion(rawQuestion, metadata) {
        if (state.isLoading) return;

        var question = String(rawQuestion || '').trim();
        if (!question) {
            setStatus('Escribe una pregunta antes de consultar.', 'warning');
            return;
        }

        var attachmentsSnapshot = state.pendingAttachments.slice(0, state.maxAttachments).map(function (att) {
            return {
                id: att.id,
                name: att.name,
                type: att.type,
                size: att.size,
                data: att.data,
                dataUrl: att.dataUrl
            };
        });

        var hasImages = attachmentsSnapshot.length > 0;
        var selectedModel = String(state.model || '').trim() || VISION_FALLBACK_MODEL;
        var effectiveModel = selectedModel;
        var localWarning = null;

        if (hasImages && !supportsVisionModel(selectedModel)) {
            effectiveModel = VISION_FALLBACK_MODEL;
            localWarning = 'El modelo seleccionado no soporta imágenes. Se usará ' + VISION_FALLBACK_MODEL + '.';
        }

        var context = collectContext(metadata);
        var payload = {
            prompt: question,
            question: question,
            model: effectiveModel,
            selectedModel: selectedModel,
            maxTokens: state.maxTokens,
            context: context,
            courseId: context.courseId,
            topicId: context.topicId,
            selectedText: context.selectedText,
            surroundingContext: context.surroundingContext,
            memory: buildMemoryPayload(),
            images: attachmentsSnapshot.map(function (att) {
                return {
                    name: att.name,
                    type: att.type,
                    data: att.data
                };
            })
        };

        pushMessage('user', question, attachmentsSnapshot);
        if (refs.textarea) refs.textarea.value = '';
        setLoadingState(true);
        setStatus(localWarning ? localWarning + ' Enviando…' : 'Enviando…', localWarning ? 'warning' : null);

        var controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
        var timeoutId = setTimeout(function () {
            if (controller) controller.abort();
        }, 60000);

        postQueryWithFallback(payload, controller ? controller.signal : undefined)
            .then(function (json) {
                var answer = extractAnswer(json);
                var usage = normalizeUsage(json);

                var responseWarning = String((json && json.warning) || '').trim();
                var warningText = [localWarning, responseWarning].filter(Boolean).join(' ');

                var responseModel = String((json && json.model) || effectiveModel || selectedModel).trim() || selectedModel;
                var responseHasImages = Boolean(json && (json.hasImages || json.has_images || hasImages));
                var responseImagesCount = Number(
                    (json && (json.imagesCount || json.images_count)) ||
                    (json && json.usage && (json.usage.imagesCount || json.usage.images_count)) ||
                    attachmentsSnapshot.length
                );

                state.lastRequest = {
                    model: responseModel,
                    requestedModel: selectedModel,
                    warning: warningText,
                    inputTokens: usage.inputTokens,
                    outputTokens: usage.outputTokens,
                    totalTokens: usage.totalTokens,
                    estimatedCostUsd: usage.estimatedCostUsd,
                    hasImages: responseHasImages,
                    imagesCount: responseImagesCount
                };

                pushMessage('assistant', answer);
                updateMemoryWithTurn(question, answer);

                state.pendingAttachments = [];
                renderPendingAttachments();

                if (json && json.metrics) {
                    renderMetrics(json.metrics);
                } else {
                    renderMetrics(state.metrics);
                }

                if (warningText) {
                    setStatus('Respuesta recibida con aviso: ' + warningText, 'warning');
                } else {
                    setStatus('Respuesta recibida.', 'success');
                }
            })
            .catch(function (err) {
                var message = err && err.name === 'AbortError'
                    ? 'Tiempo de espera agotado al consultar el asistente.'
                    : (err && err.message ? err.message : 'error desconocido');
                setStatus(message + ' Inicia open-proxy.command si el proxy no está activo.', 'error');
            })
            .finally(function () {
                clearTimeout(timeoutId);
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
