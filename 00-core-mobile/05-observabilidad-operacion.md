# Observabilidad y operación

## Modelo mental

Si tu app fuera un avión, la observabilidad sería la caja negra y los instrumentos del cockpit. Sin ellos, cuando algo falla solo puedes adivinar. Con ellos, puedes reconstruir exactamente qué pasó, cuándo y por qué. La observabilidad no es "añadir prints": es diseñar señales que activen decisiones.

## Ejemplo en el scaffold

En `ArchitectureKit`, la Etapa 3 introduce observabilidad mediante decoradores. El patrón es envolver un `ProductRepository` real con un `LoggingProductRepository` que registra evento, resultado y duración sin contaminar el core. El `AppComposition` decide qué decoradores aplicar. Esto permite activar o desactivar logging sin tocar Domain ni Application. El patrón completo se practica en [Observabilidad — Etapa 3](../03-evolucion/03-observabilidad.md).

## Cuándo sí / cuándo no

Añade observabilidad desde el momento en que tienes flujos críticos de usuario (login, carga de datos, sync). No instrumentes todo: instrumenta lo que activa decisión (errores, latencia, tasas de éxito). Evita logging de PII sin política de redacción.

## Logging

Usa logs estructurados con campos estables (evento, feature, resultado, error_code, correlation_id). Evita texto libre como única señal.

Nunca loguees PII sin política de redacción. Define redaction por defecto para email, teléfono, token, identificadores sensibles. Aplica sampling en eventos ruidosos para controlar coste.

## Metrics

Mide golden signals adaptadas a mobile: éxito/fracaso de flujos críticos, latencia percibida, crash-free sessions, hangs en main thread (detectables en Xcode Hangs organizer), cold start, consumo de memoria y tasa de retry.

No midas todo. Mide lo que activa decisión.

## Tracing

En mobile el tracing extremo puede ser caro. Úsalo en caminos de alto valor (login, checkout, sync) y con correlación hacia backend mediante correlation IDs.

## SLO y error budget

Define SLO por capacidad de usuario, no por componente interno aislado. Ejemplo: sync exitosa de tareas > 99.0% en 28 días.

El error budget convierte fiabilidad en presupuesto gestionable. Si se consume rápido, prioriza estabilidad sobre nueva feature.

## Alert hygiene

Una alerta vale si dispara acción concreta. Elimina alertas sin playbook, con falsos positivos recurrentes o sin dueño.

## Template: Minimal Observability Spec

Usa esta plantilla de especificación mínima para definir qué debes instrumentar en cada flujo crítico:

Nombre del flujo:

Eventos obligatorios:

Métricas obligatorias:

Campos sensibles y redacción:

Umbrales de alerta:

Dashboard de referencia:

Owner operativo:

## Template: Incident Runbook Skeleton

Usa este esqueleto como punto de partida para crear el runbook de cada incidente:

Tipo de incidente:

Señal de detección:

Impacto esperado:

Primera mitigación:

Condición de rollback:

Validación post-mitigación:

Comunicación interna/externa:

Acciones preventivas posteriores:


## 🔭 Explora el scaffold — Puntos de observabilidad

```bash
# Busca los puntos donde el scaffold registra errores y eventos
grep -rn "Logger\|os_log\|print" apps/ios/ArchitectureKit/Sources/ | grep -v ".swift:#" | head -15
```

Los puntos donde el scaffold emite logs son exactamente los puntos de observabilidad de esta lección: errores de autenticación, fallos de red, transiciones de estado. En producción, estos logs serán los primeros datos disponibles cuando algo falle.

---

## Qué sigue

Con observabilidad en operación, el siguiente paso es gestionar cambios en producción con seguridad: cómo hacer releases progresivos y cómo recuperarte rápidamente si algo sale mal.

