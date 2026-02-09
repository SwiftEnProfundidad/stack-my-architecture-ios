#!/usr/bin/env node

const http = require('http');
const fs = require('fs');
const path = require('path');

loadEnv(path.join(__dirname, '.env'));

const PORT = Number(process.env.ASSISTANT_BRIDGE_PORT || 8787);
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || '';
const OPENAI_BASE_URL = process.env.OPENAI_BASE_URL || 'https://api.openai.com/v1';
const DEFAULT_MODEL = process.env.OPENAI_MODEL_DEFAULT || 'gpt-5.3';
const ALLOWED_MODELS = (process.env.OPENAI_ALLOWED_MODELS || 'gpt-5.3,gpt-5.2,gpt-4o-mini,gpt-4.1-mini')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);
const VISION_MODELS = (process.env.OPENAI_VISION_MODELS || 'gpt-4o-mini')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);
const DEFAULT_QUERY_PATH = '/ask';
const MAX_TOKENS_DEFAULT = Number(process.env.ASSISTANT_MAX_TOKENS_DEFAULT || 600);
const MAX_TOKENS_CAP = Number(process.env.ASSISTANT_MAX_TOKENS_CAP || 1200);
const SOFT_DAILY_BUDGET_USD = Number(process.env.ASSISTANT_SOFT_DAILY_BUDGET_USD || 2.0);
const DAILY_WARNING_USD = Number(process.env.ASSISTANT_DAILY_WARNING_USD || 0.25);
const MAX_IMAGES_PER_QUERY = 3;
const MAX_IMAGE_BYTES = 3 * 1024 * 1024;
const MAX_BODY_BYTES = 16 * 1024 * 1024;
const ALLOWED_IMAGE_TYPES = ['image/png', 'image/jpeg'];

const PRICES_PER_1K = {
    'gpt-5.3': { in: 0.0015, out: 0.006 },
    'gpt-5.2': { in: 0.0012, out: 0.0048 },
    'gpt-4o-mini': { in: 0.00015, out: 0.0006 },
    'gpt-4.1-mini': { in: 0.0004, out: 0.0016 }
};

const usage = {
    startedAt: new Date().toISOString(),
    totalRequests: 0,
    totalTokens: 0,
    totalPromptTokens: 0,
    totalCompletionTokens: 0,
    totalEstimatedCostUSD: 0,
    totalImagesCount: 0,
    lastRequest: null,
    daily: {
        dateKey: dateKeyToday(),
        requests: 0,
        tokens: 0,
        promptTokens: 0,
        completionTokens: 0,
        estimatedCostUSD: 0,
        imagesCount: 0
    }
};

const server = http.createServer(async (req, res) => {
    setCors(res);

    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    if (req.method === 'GET' && req.url === '/health') {
        writeJson(res, 200, { ok: true, service: 'assistant-bridge', query_path: DEFAULT_QUERY_PATH });
        return;
    }

    if (req.method === 'GET' && req.url === '/config') {
        writeJson(res, 200, {
            models: ALLOWED_MODELS,
            default_model: DEFAULT_MODEL,
            max_tokens_default: MAX_TOKENS_DEFAULT,
            max_tokens_cap: MAX_TOKENS_CAP,
            soft_daily_budget_usd: SOFT_DAILY_BUDGET_USD,
            daily_warning_usd: DAILY_WARNING_USD,
            max_images: MAX_IMAGES_PER_QUERY,
            max_image_bytes: MAX_IMAGE_BYTES,
            vision_models: VISION_MODELS,
            query_path: DEFAULT_QUERY_PATH
        });
        return;
    }

    if (req.method === 'GET' && req.url === '/metrics') {
        rollDailyIfNeeded();
        writeJson(res, 200, metricsPayload());
        return;
    }

    if (req.method === 'POST' && (req.url === '/ask' || req.url === '/assistant/query')) {
        if (!OPENAI_API_KEY) {
            writeJson(res, 500, {
                error: 'OPENAI_API_KEY no está configurada en assistant-bridge/.env'
            });
            return;
        }

        const body = await readJsonBody(req, res);
        if (!body) return;

        const question = String(body.question || body.prompt || '').trim();
        if (!question) {
            writeJson(res, 400, { error: 'question/prompt es obligatoria' });
            return;
        }

        const imagesResult = normalizeImages(body.images);
        if (imagesResult.error) {
            writeJson(res, 400, { error: imagesResult.error });
            return;
        }

        const images = imagesResult.value;
        const requestedModel = ALLOWED_MODELS.includes(body.model) ? body.model : DEFAULT_MODEL;
        const maxTokens = clampNumber(body.maxTokens, 100, MAX_TOKENS_CAP, MAX_TOKENS_DEFAULT);

        rollDailyIfNeeded();

        let warning = null;
        if (SOFT_DAILY_BUDGET_USD > 0 && usage.daily.estimatedCostUSD >= SOFT_DAILY_BUDGET_USD) {
            warning = 'Presupuesto diario superado (soft limit).';
        }

        let usedModel = requestedModel;
        if (images.length > 0 && !VISION_MODELS.includes(usedModel)) {
            usedModel = 'gpt-4o-mini';
            warning = warning
                ? `${warning} El modelo ${requestedModel} no soporta visión. Fallback a ${usedModel}.`
                : `El modelo ${requestedModel} no soporta visión. Fallback automático a ${usedModel}.`;
        }

        const prompt = buildPrompt({
            question,
            selectedText: body.selectedText || (body.context && body.context.selectedText),
            surroundingContext: body.surroundingContext || (body.context && body.context.surroundingContext),
            courseId: body.courseId || (body.context && body.context.courseId),
            topicId: body.topicId || (body.context && body.context.topicId),
            memory: normalizeMemory(body.memory)
        });

        try {
            const completion = await callOpenAI({
                model: usedModel,
                maxTokens,
                prompt,
                images
            });

            const answer = extractAnswer(completion);
            const usageTokens = completion && completion.usage ? completion.usage : {};

            const promptTokens = Number(usageTokens.prompt_tokens || 0);
            const completionTokens = Number(usageTokens.completion_tokens || 0);
            const totalTokens = Number(usageTokens.total_tokens || promptTokens + completionTokens);
            const estimated = estimateCost(usedModel, promptTokens, completionTokens);

            registerUsage({
                model: usedModel,
                promptTokens,
                completionTokens,
                totalTokens,
                estimatedCostUSD: estimated,
                imagesCount: images.length
            });

            const responsePayload = {
                ok: true,
                answer,
                model: usedModel,
                selectedModel: requestedModel,
                warning,
                hasImages: images.length > 0,
                imagesCount: images.length,
                usage: {
                    inputTokens: promptTokens,
                    outputTokens: completionTokens,
                    totalTokens,
                    estimatedCostUsd: estimated,
                    hasImages: images.length > 0,
                    imagesCount: images.length,
                    prompt_tokens: promptTokens,
                    completion_tokens: completionTokens,
                    total_tokens: totalTokens,
                    estimated_cost_usd: estimated
                },
                metrics: metricsPayload()
            };

            writeJson(res, 200, responsePayload);
        } catch (err) {
            writeJson(res, 502, {
                ok: false,
                error: 'Fallo al consultar OpenAI',
                detail: err && err.message ? err.message : 'unknown'
            });
        } finally {
            images.forEach((item) => {
                item.data = '';
            });
            body.images = [];
        }

        return;
    }

    writeJson(res, 404, { error: 'Not found' });
});

server.listen(PORT, () => {
    console.log(`[assistant-bridge] running on http://localhost:${PORT}`);
    if (!OPENAI_API_KEY) {
        console.warn('[assistant-bridge] WARNING: OPENAI_API_KEY no configurada.');
    }
});

function setCors(res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

function writeJson(res, status, payload) {
    res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify(payload));
}

function readJsonBody(req, res) {
    return new Promise((resolve) => {
        let raw = '';
        req.on('data', (chunk) => {
            raw += chunk;
            if (raw.length > MAX_BODY_BYTES) {
                writeJson(res, 413, { error: 'Payload demasiado grande' });
                resolve(null);
            }
        });

        req.on('end', () => {
            try {
                const parsed = raw ? JSON.parse(raw) : {};
                resolve(parsed);
            } catch (_err) {
                writeJson(res, 400, { error: 'JSON inválido' });
                resolve(null);
            }
        });
    });
}

function normalizeMemory(memory) {
    if (!memory || typeof memory !== 'object') return { conversation_summary: '', recent_messages: [] };

    const summary = String(memory.conversation_summary || '').trim().slice(0, 1800);
    const recent = Array.isArray(memory.recent_messages)
        ? memory.recent_messages
            .map((item) => {
                if (!item || typeof item !== 'object') return null;
                const role = item.role === 'assistant' ? 'assistant' : 'user';
                const text = String(item.text || '').trim().slice(0, 900);
                if (!text) return null;
                return { role, text };
            })
            .filter(Boolean)
            .slice(-8)
        : [];

    return {
        conversation_summary: summary,
        recent_messages: recent
    };
}

function buildPrompt(input) {
    const lines = [
        'Eres un asistente didáctico para cursos técnicos.',
        'Responde SIEMPRE en español.',
        'Explica con claridad para nivel junior.',
        'Evita bloques de código largos y evita suposiciones avanzadas.',
        ''
    ];

    if (input.courseId) lines.push(`Curso: ${input.courseId}`);
    if (input.topicId) lines.push(`Tema: ${input.topicId}`);

    if (input.memory && input.memory.conversation_summary) {
        lines.push('', 'conversation_summary:');
        lines.push(input.memory.conversation_summary);
    }

    if (input.memory && Array.isArray(input.memory.recent_messages) && input.memory.recent_messages.length) {
        lines.push('', 'recent_messages:');
        input.memory.recent_messages.forEach((item) => {
            lines.push(`- ${item.role}: ${item.text}`);
        });
    }

    if (input.selectedText) {
        lines.push('', 'Texto seleccionado:');
        lines.push(String(input.selectedText).slice(0, 1800));
    }
    if (input.surroundingContext) {
        lines.push('', 'Contexto cercano:');
        lines.push(String(input.surroundingContext).slice(0, 1800));
    }

    lines.push('', 'Pregunta del usuario:');
    lines.push(input.question);

    return lines.join('\n');
}

async function callOpenAI({ model, maxTokens, prompt, images }) {
    const imageItems = Array.isArray(images) ? images : [];

    const userContent = imageItems.length
        ? [
            { type: 'text', text: prompt },
            ...imageItems.map((img) => ({
                type: 'image_url',
                image_url: { url: `data:${img.type};base64,${img.data}` }
            }))
        ]
        : prompt;

    const tokenLimitField = String(model || '').startsWith('gpt-5') ? 'max_completion_tokens' : 'max_tokens';

    const response = await fetch(`${OPENAI_BASE_URL}/chat/completions`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${OPENAI_API_KEY}`
        },
        body: JSON.stringify({
            model,
            temperature: 0.2,
            [tokenLimitField]: maxTokens,
            messages: [
                {
                    role: 'system',
                    content: 'Asistente pedagógico. Claro, práctico, breve y preciso.'
                },
                {
                    role: 'user',
                    content: userContent
                }
            ]
        })
    });

    const json = await response.json();
    if (!response.ok) {
        throw new Error(`OpenAI HTTP ${response.status}: ${JSON.stringify(json)}`);
    }
    return json;
}

function normalizeImages(input) {
    if (!Array.isArray(input) || !input.length) return { value: [] };

    if (input.length > MAX_IMAGES_PER_QUERY) {
        return { error: `Máximo ${MAX_IMAGES_PER_QUERY} imágenes por consulta` };
    }

    const items = [];
    for (const raw of input) {
        const type = normalizeImageType((raw && raw.type) || '');
        const name = String((raw && raw.name) || 'imagen').slice(0, 120);

        if (!ALLOWED_IMAGE_TYPES.includes(type)) {
            return { error: 'Formato de imagen no permitido. Solo PNG o JPEG.' };
        }

        const base64 = extractBase64Image(raw, type);
        if (!base64) {
            return { error: 'Imagen inválida en payload.' };
        }

        const sizeBytes = base64ByteLength(base64);
        if (!sizeBytes || sizeBytes > MAX_IMAGE_BYTES) {
            return { error: 'Una imagen supera el tamaño máximo permitido (3MB).' };
        }

        items.push({
            name,
            type,
            data: base64,
            sizeBytes
        });
    }

    return { value: items };
}

function normalizeImageType(type) {
    const normalized = String(type || '').toLowerCase().trim();
    if (normalized === 'image/jpg') return 'image/jpeg';
    return normalized;
}

function extractBase64Image(raw, type) {
    if (!raw || typeof raw !== 'object') return '';

    if (typeof raw.data === 'string' && raw.data.trim()) {
        return normalizeBase64(raw.data);
    }

    if (typeof raw.dataUrl === 'string' && raw.dataUrl.trim()) {
        const prefix = `data:${type};base64,`;
        if (!raw.dataUrl.startsWith(prefix)) return '';
        return normalizeBase64(raw.dataUrl.slice(prefix.length));
    }

    return '';
}

function normalizeBase64(value) {
    return String(value || '').replace(/\s+/g, '').trim();
}

function base64ByteLength(base64) {
    const normalized = normalizeBase64(base64);
    if (!normalized) return 0;
    const padding = normalized.endsWith('==') ? 2 : normalized.endsWith('=') ? 1 : 0;
    return Math.floor((normalized.length * 3) / 4) - padding;
}

function extractAnswer(payload) {
    const choice = payload && payload.choices && payload.choices[0];
    const msg = choice && choice.message;
    const text = msg && msg.content ? String(msg.content).trim() : '';
    return text || 'No se recibió respuesta de contenido.';
}

function estimateCost(model, promptTokens, completionTokens) {
    const p = PRICES_PER_1K[model] || PRICES_PER_1K['gpt-4o-mini'];
    const inCost = (Number(promptTokens || 0) / 1000) * p.in;
    const outCost = (Number(completionTokens || 0) / 1000) * p.out;
    return Number((inCost + outCost).toFixed(8));
}

function registerUsage(data) {
    usage.totalRequests += 1;
    usage.totalTokens += Number(data.totalTokens || 0);
    usage.totalPromptTokens += Number(data.promptTokens || 0);
    usage.totalCompletionTokens += Number(data.completionTokens || 0);
    usage.totalEstimatedCostUSD = Number((usage.totalEstimatedCostUSD + Number(data.estimatedCostUSD || 0)).toFixed(8));
    usage.totalImagesCount += Number(data.imagesCount || 0);

    usage.daily.requests += 1;
    usage.daily.tokens += Number(data.totalTokens || 0);
    usage.daily.promptTokens += Number(data.promptTokens || 0);
    usage.daily.completionTokens += Number(data.completionTokens || 0);
    usage.daily.estimatedCostUSD = Number((usage.daily.estimatedCostUSD + Number(data.estimatedCostUSD || 0)).toFixed(8));
    usage.daily.imagesCount += Number(data.imagesCount || 0);

    usage.lastRequest = {
        at: new Date().toISOString(),
        model: data.model,
        inputTokens: Number(data.promptTokens || 0),
        outputTokens: Number(data.completionTokens || 0),
        totalTokens: Number(data.totalTokens || 0),
        estimatedCostUsd: Number(data.estimatedCostUSD || 0),
        hasImages: Number(data.imagesCount || 0) > 0,
        imagesCount: Number(data.imagesCount || 0)
    };
}

function metricsPayload() {
    return {
        started_at: usage.startedAt,
        total_requests: usage.totalRequests,
        total_tokens: usage.totalTokens,
        total_prompt_tokens: usage.totalPromptTokens,
        total_completion_tokens: usage.totalCompletionTokens,
        total_estimated_cost_usd: usage.totalEstimatedCostUSD,
        total_images_count: usage.totalImagesCount,
        session_total_cost_usd: usage.totalEstimatedCostUSD,
        soft_daily_budget_usd: SOFT_DAILY_BUDGET_USD,
        daily_warning_usd: DAILY_WARNING_USD,
        daily: {
            date_key: usage.daily.dateKey,
            requests: usage.daily.requests,
            tokens: usage.daily.tokens,
            prompt_tokens: usage.daily.promptTokens,
            completion_tokens: usage.daily.completionTokens,
            estimated_cost_usd: usage.daily.estimatedCostUSD,
            images_count: usage.daily.imagesCount
        },
        last_request: usage.lastRequest
    };
}

function rollDailyIfNeeded() {
    const key = dateKeyToday();
    if (usage.daily.dateKey === key) return;
    usage.daily = {
        dateKey: key,
        requests: 0,
        tokens: 0,
        promptTokens: 0,
        completionTokens: 0,
        estimatedCostUSD: 0,
        imagesCount: 0
    };
}

function dateKeyToday() {
    const d = new Date();
    const y = d.getUTCFullYear();
    const m = String(d.getUTCMonth() + 1).padStart(2, '0');
    const day = String(d.getUTCDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
}

function clampNumber(value, min, max, fallback) {
    const n = Number(value);
    if (!Number.isFinite(n)) return fallback;
    if (n < min) return min;
    if (n > max) return max;
    return Math.round(n);
}

function loadEnv(filePath) {
    if (!fs.existsSync(filePath)) return;
    const raw = fs.readFileSync(filePath, 'utf8');
    raw.split(/\r?\n/).forEach((line) => {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('#')) return;
        const idx = trimmed.indexOf('=');
        if (idx <= 0) return;
        const key = trimmed.slice(0, idx).trim();
        const value = trimmed.slice(idx + 1).trim();
        if (!(key in process.env)) {
            process.env[key] = value;
        }
    });
}
