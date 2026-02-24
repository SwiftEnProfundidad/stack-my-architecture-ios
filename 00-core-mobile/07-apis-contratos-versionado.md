# APIs, contratos y versionado

## Modelo mental

Un contrato API es como un acuerdo comercial entre dos empresas: define qué se entrega, en qué formato, qué pasa si algo falla y cómo se gestionan los cambios. Si el acuerdo es ambiguo, cada parte interpreta a su manera y aparecen bugs en producción. Si el acuerdo es explícito, los cambios se negocian antes de romper nada.

## Ejemplo en el scaffold

En `ArchitectureKit`, el `HTTPClient` protocol en `InfraHTTP` define el contrato entre la app y el backend: `func execute(_ request: URLRequest) async throws -> (Data, HTTPResponse)`. El `AuthHTTPGateway` en `FeatureLoginData` traduce respuestas HTTP a tipos de dominio (`Session` o `AuthError`). Los `FeatureLoginDataIntegrationTests` verifican que esta traducción respeta el contrato. Consulta la Etapa 2 (`02-integracion/04-infra-real-network.md`) para la implementación completa.

## Cuándo sí / cuándo no

Define contratos explícitos siempre que haya una frontera entre módulos o entre cliente y servidor. No formalices contratos para comunicación interna dentro de un mismo módulo donde el compilador ya garantiza tipos.

## Disciplina de contrato API

Define contratos explícitos: shape de datos, códigos de estado, errores de negocio vs técnicos, idempotencia y semántica de reintento.

Evita respuestas ambiguas. Un cliente móvil necesita saber si debe reintentar, pedir reautenticación, invalidar cache o mostrar error final.

## Error Taxonomy starter

| Categoría | Ejemplo | Acción cliente |
|---|---|---|
| AUTH_EXPIRED | token vencido | refresh token + retry único |
| AUTH_INVALID | credenciales inválidas | cerrar sesión / relogin |
| RATE_LIMITED | 429 | backoff exponencial |
| TRANSIENT_NETWORK | timeout/reset | retry acotado |
| VALIDATION_ERROR | payload inválido | no retry, corregir request |
| BUSINESS_RULE | regla de dominio | no retry, feedback usuario |
| SERVER_FAILURE | 5xx | retry acotado + degradación |

## Auth móvil (OAuth2/JWT) bases

Gestiona refresh token con almacenamiento seguro y rotación. Nunca hardcodees secretos en cliente. Minimiza alcance de tokens y protege ciclo de vida de sesión.

## Retries/backoff

Retry solo en fallos transitorios idempotentes. Usa backoff exponencial con jitter para evitar tormentas.

No retries en errores de validación, reglas de negocio o auth inválida sin refresh válido.

## Versionado

Diferencia cambios backward-compatible (campos opcionales nuevos, endpoints nuevos) de breaking changes (campo requerido nuevo, semántica alterada, eliminación de endpoint).

Establece política de deprecación con ventana temporal y comunicación anticipada.

## API Contract Checklist

- [ ] Contrato request/response versionado.
- [ ] Taxonomía de errores documentada.
- [ ] Idempotencia declarada por endpoint.
- [ ] Política de retry por categoría de error.
- [ ] Compatibilidad backward evaluada.
- [ ] Plan de deprecación y fecha límite.

---

**Anterior:** [Release, rollback y feature flags ←](06-release-rollback-flags.md) · **Siguiente:** [Seguridad, privacidad y threat modeling →](08-seguridad-privacidad-threat-modeling.md)
