# Assistant Bridge (proxy local)

Este servicio evita exponer la API key en el navegador.

## Qué hace

- Expone [`/ask`](assistant-bridge/server.js) para consultas del panel IA.
- Expone [`/metrics`](assistant-bridge/server.js) para coste/tokens/requests.
- Expone [`/config`](assistant-bridge/server.js) para modelos y límites.
- Guarda la API key solo en servidor vía [`.env`](assistant-bridge/.env.example:1).

## Flujo de datos

1. Usuario selecciona texto en el curso (iOS o Android).
2. El botón “Consultar al asistente” envía selección + `courseId` + `topicId` al panel.
3. El panel hace `fetch` al proxy local (`http://localhost:8787`).
4. El proxy llama a OpenAI y devuelve respuesta + métricas.
5. El panel muestra respuesta y métricas en split view.

## Configuración

1. Copia [`.env.example`](assistant-bridge/.env.example:1) a `.env`.
2. Rellena `OPENAI_API_KEY`.
3. Opcional: ajusta `ASSISTANT_SOFT_DAILY_BUDGET_USD` y `ASSISTANT_MAX_TOKENS_CAP`.

El panel permite ajustar el presupuesto diario en runtime y lo sincroniza con el proxy.

### Nota importante sobre modelos GPT-5.x

Si tu API key/proyecto aún no tiene acceso a `gpt-5.3` o `gpt-5.2`, el bridge hace fallback automático a `gpt-4o-mini` y devuelve un aviso en la respuesta. Esto evita errores duros de consulta.

## Arranque

Desde la raíz del repo:

```bash
cp assistant-bridge/.env.example assistant-bridge/.env
node assistant-bridge/server.js
```

Verificación rápida:

```bash
curl http://localhost:8787/health
curl http://localhost:8787/config
curl http://localhost:8787/metrics
```

## Endpoints

- `GET /health`
- `GET /config`
- `POST /config/runtime`
- `GET /metrics`
- `POST /ask`

Body mínimo de `/ask`:

```json
{
  "question": "Explícame este bloque",
  "model": "gpt-4o-mini",
  "maxTokens": 600,
  "courseId": "stack-my-architecture-ios",
  "topicId": "02-integracion-01-feature-catalog-02-application",
  "selectedText": "...",
  "surroundingContext": "..."
}
```
