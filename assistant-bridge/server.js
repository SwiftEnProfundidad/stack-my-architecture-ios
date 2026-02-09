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
const MAX_TOKENS_DEFAULT = Number(process.env.ASSISTANT_MAX_TOKENS_DEFAULT || 600);
const MAX_TOKENS_CAP = Number(process.env.ASSISTANT_MAX_TOKENS_CAP || 1200);
const SOFT_DAILY_BUDGET_USD = Number(process.env.ASSISTANT_SOFT_DAILY_BUDGET_USD || 2.0);
const MAX_IMAGES_PER_QUERY = 3;
const MAX_IMAGE_BYTES = 5 * 1024 * 1024;
const ALLOWED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/webp'];

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
    daily: {
        dateKey: dateKeyToday(),
        requests: 0,
        tokens: 0,
        promptTokens: 0,
        completionTokens: 0,
        estimatedCostUSD: 0
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
        writeJson(res, 200, { ok: true, service: 'assistant-bridge' });
        return;
    }

    if (req.method === 'GET' && req.url === '/config') {
        writeJson(res, 200, {
            models: ALLOWED_MODELS,
            default_model: DEFAULT_MODEL,
            max_tokens_default: MAX_TOKENS_DEFAULT,
            max_tokens_cap: MAX_TOKENS_CAP,
            soft_daily_budget_usd: SOFT_DAILY_BUDGET_USD
        });
        return;
    }

    if (req.method === 'GET' && req.url === '/metrics') {
        rollDailyIfNeeded();
        writeJson(res, 200, metricsPayload());
        return;
    }

    if (req.method === 'POST' && req.url === '/ask') {
        if (!OPENAI_API_KEY) {
            writeJson(res, 500, {
                error: 'OPENAI_API_KEY no está configurada en assistant-bridge/.env'
            });
            return;
        }

        const body = await readJsonBody(req, res);
        if (!body) return;

        const question = String(body.question || '').trim();
        if (!question) {
            writeJson(res, 400, { error: 'question es obligatoria' });
            return;
        }

        const images = normalizeImages(body.images);
        if (images.error) {
            writeJson(res, 400, { error: images.error });
            return;
        }

        const model = ALLOWED_MODELS.includes(body.model) ? body.model : DEFAULT_MODEL;
        const maxTokens = clampNumber(body.maxTokens, 100, MAX_TOKENS_CAP, MAX_TOKENS_DEFAULT);

        rollDailyIfNeeded();

        let warning = null;
        if (SOFT_DAILY_BUDGET_USD > 0 && usage.daily.estimatedCostUSD >= SOFT_DAILY_BUDGET_USD) {
            warning = 'Presupuesto diario superado (soft limit).';
        }

        const prompt = buildPrompt({
            question,
            selectedText: body.selectedText,
            surroundingContext: body.surroundingContext,
            courseId: body.courseId,
            topicId: body.topicId
        });

        try {
            let usedModel = model;
            let completion;
            let runtimeWarning = warning;

            try {
                completion = await callOpenAI({
                    model: usedModel,
                    maxTokens,
                    prompt,
                    images: images.value
                });
            } catch (err) {
                const detail = err && err.message ? String(err.message) : '';
                const shouldFallbackModel =
                    usedModel !== 'gpt-4o-mini' &&
                    (detail.includes('model_not_found') ||
                        detail.includes('does not exist') ||
                        detail.includes('not available') ||
                        detail.includes('unsupported_model'));

                if (!shouldFallbackModel) throw err;

                usedModel = 'gpt-4o-mini';
                completion = await callOpenAI({
                    model: usedModel,
                    maxTokens,
                    prompt,
                    images: images.value
                });

                runtimeWarning = runtimeWarning
                    ? `${runtimeWarning} Fallback a ${usedModel}.`
                    : `El modelo solicitado no está disponible en tu API key. Fallback automático a ${usedModel}.`;
            }

            const answer = extractAnswer(completion);
            const usageTokens = completion && completion.usage ? completion.usage : {};

            const promptTokens = Number(usageTokens.prompt_tokens || 0);
            const completionTokens = Number(usageTokens.completion_tokens || 0);
            const totalTokens = Number(usageTokens.total_tokens || promptTokens + completionTokens);
            const estimated = estimateCost(usedModel, promptTokens, completionTokens);

            registerUsage({
                promptTokens,
                completionTokens,
                totalTokens,
                estimatedCostUSD: estimated
            });

            writeJson(res, 200, {
                answer,
                model: usedModel,
                warning: runtimeWarning,
                usage: {
                    prompt_tokens: promptTokens,
                    completion_tokens: completionTokens,
                    total_tokens: totalTokens,
                    estimated_cost_usd: estimated
                },
                metrics: metricsPayload()
            });
        } catch (err) {
            writeJson(res, 502, {
                error: 'Fallo al consultar OpenAI',
                detail: err && err.message ? err.message : 'unknown'
            });
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
            if (raw.length > 1_000_000) {
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
                image_url: { url: img.dataUrl }
            }))
        ]
        : prompt;

    const response = await fetch(`${OPENAI_BASE_URL}/chat/completions`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${OPENAI_API_KEY}`
        },
        body: JSON.stringify({
            model,
            temperature: 0.2,
            max_tokens: maxTokens,
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
        const type = String((raw && raw.type) || '').toLowerCase();
        const size = Number((raw && raw.size) || 0);
        const dataUrl = String((raw && raw.dataUrl) || '').trim();

        if (!ALLOWED_IMAGE_TYPES.includes(type)) {
            return { error: 'Formato de imagen no permitido. Usa PNG, JPG, JPEG o WEBP.' };
        }
        if (!size || size > MAX_IMAGE_BYTES) {
            return { error: 'Una imagen supera el tamaño máximo permitido (5MB).' };
        }
        if (!dataUrl.startsWith('data:image/')) {
            return { error: 'Imagen inválida en payload.' };
        }

        items.push({
            name: String((raw && raw.name) || 'imagen'),
            type,
            size,
            dataUrl
        });
    }

    return { value: items };
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

    usage.daily.requests += 1;
    usage.daily.tokens += Number(data.totalTokens || 0);
    usage.daily.promptTokens += Number(data.promptTokens || 0);
    usage.daily.completionTokens += Number(data.completionTokens || 0);
    usage.daily.estimatedCostUSD = Number((usage.daily.estimatedCostUSD + Number(data.estimatedCostUSD || 0)).toFixed(8));
}

function metricsPayload() {
    return {
        started_at: usage.startedAt,
        total_requests: usage.totalRequests,
        total_tokens: usage.totalTokens,
        total_prompt_tokens: usage.totalPromptTokens,
        total_completion_tokens: usage.totalCompletionTokens,
        total_estimated_cost_usd: usage.totalEstimatedCostUSD,
        soft_daily_budget_usd: SOFT_DAILY_BUDGET_USD,
        daily: {
            date_key: usage.daily.dateKey,
            requests: usage.daily.requests,
            tokens: usage.daily.tokens,
            prompt_tokens: usage.daily.promptTokens,
            completion_tokens: usage.daily.completionTokens,
            estimated_cost_usd: usage.daily.estimatedCostUSD
        }
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
        estimatedCostUSD: 0
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
