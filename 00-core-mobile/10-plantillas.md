# Plantillas operativas (con ejemplos reales)

Cada plantilla aquí tiene un criterio de validez: el artefacto resultante debe poder ser leído por otra persona y respondido con “entiendo el problema, la decisión y cómo verificar si funcionó”. Si no cumple ese criterio, no está terminado.

---

## 1) ADR template (Architecture Decisión Record)

### Plantilla

Autor:

Estado: `propuesta` | `aceptada` | `rechazada` | `obsoleta`

Contexto:

Decisión:

Alternativas consideradas:

Trade-offs:

Consecuencias:

Métricas/criterios de éxito:

Fecha de revisión:

### Ejemplo (navegación desacoplada)

Autor: equipo iOS.

Estado: `aceptada`

Contexto:
Login y Catálogo necesitan coordinar navegación sin acoplar features entre sí.

Decisión:
Usar navegación por eventos (intenciones emitidas por feature) y coordinación central en Composition Root.

Alternativas consideradas:
- `NavigationLink` directo entre features.
- Router global con strings mágicos.

Trade-offs:
- A favor: mejor testabilidad y menor acoplamiento.
- En contra: requiere más wiring inicial.

Consecuencias:
- El wiring queda concentrado en Composition Root.
- Cada feature mantiene límites de dependencia.

Métricas/criterios de éxito:
- 0 imports directos entre `FeatureLogin` y `FeatureCatalog`.
- Tests de coordinación pasando para rutas críticas.

Fecha de revisión:
2026-07-01.

---

## 2) RFC template (cambio relevante)

### Plantilla

Autor:

Estado: `borrador` | `en revisión` | `aceptado` | `rechazado`

Stakeholders (quién aprueba):

Fecha límite de decisión:

Problema:

Objetivo:

Opciones:

Recomendación:

Plan de rollout:

Plan de rollback:

Riesgos abiertos:

### Ejemplo (introducir caché en catálogo)

Autor: equipo iOS.

Estado: `aceptado`

Stakeholders (quién aprueba): tech lead iOS, product manager.

Fecha límite de decisión: 2026-02-14.

Problema:
El catálogo tarda demasiado en redes inestables y no ofrece experiencia offline mínima.

Objetivo:
Reducir tiempo de primera visualización y permitir lectura de último estado conocido.

Opciones:
- Solo remoto (sin caché).
- Caché en memoria.
- Caché persistente con TTL.

Recomendación:
Caché persistente con TTL y fallback a remoto cuando expire.

Plan de rollout:
1. Activar en porcentaje pequeño.
2. Monitorizar latencia y errores de stale data.
3. Expandir por cohortes.

Plan de rollback:
Feature flag para desactivar caché y volver a remoto puro.

Riesgos abiertos:
Riesgo de datos obsoletos si el TTL queda mal calibrado.

---

## 3) PR Review checklist

> Items marcados con **[B]** son bloqueantes: el PR no se mergea si están sin marcar. Items sin marca son mejoras deseables que pueden quedar como follow-up documentado.

### Plantilla

- [ ] **[B]** Arquitectura: límites y dependencias correctos.
- [ ] **[B]** Tests: cobertura suficiente del impacto.
- [ ] **[B]** Edge cases: fallos previsibles cubiertos.
- [ ] Observabilidad: logs/métricas para diagnóstico.
- [ ] **[B]** Seguridad/privacidad: PII/secretos revisados.
- [ ] Plan de rollback documentado (si el cambio lo requiere).

### Ejemplo de uso (extracto)

- [x] **[B]** Arquitectura: sin imports cruzados entre features.
- [x] **[B]** Tests: unit + integration en verde para login y catálogo.
- [x] **[B]** Edge cases: expiración de sesión y fallo de red cubiertos.
- [ ] Observabilidad: pendiente añadir evento estable para retry de catálogo. *(no bloqueante — follow-up documentado en ticket #42)*
- [x] **[B]** Seguridad/privacidad: logger redacta email/token.
- [x] Plan de rollback: flag de caché documentado.

Comentario final de revisión:
“Aprobable: todos los bloqueantes en verde. Observabilidad de retry queda como follow-up en #42”.

---

## 4) DoD template (Definition of Done)

> Cada ítem incluye quién valida: el autor lo ejecuta, CI lo verifica automáticamente, o el revisor lo confirma en la PR.

### Plantilla

Build: *(valida: CI)*

Tests: *(valida: CI + autor)*

Quality gates: *(valida: CI)*

Documentación: *(valida: revisor)*

Operación: *(valida: autor + revisor)*

### Ejemplo (feature Login)

Build:
Compila en CI y local sin warnings críticos de concurrencia.

Tests:
Unit tests de `Email`, `Password` y `AuthenticateUserUseCase` pasando.

Quality gates:
Dependencias correctas + strict concurrency + coverage crítica.

Documentación:
ADR-001 actualizado y escenario BDD trazable a tests.

Operación:
Evento de fallo de login instrumentado sin PII.

---

## 5) Tabla de métricas before/after

> `Before` y `After` deben incluir unidad (ms, %, pp, nº). `Delta` debe expresarse como porcentaje o puntos absolutos con signo. `Evidencia` debe ser verificable por un tercero (log, perfilado, dashboard).

### Plantilla

| Métrica | Before | After | Delta | Evidencia |
|---|---:|---:|---:|---|
| | | | | |
| | | | | |

### Ejemplo (catálogo con caché)

| Métrica | Before | After | Delta | Evidencia |
|---|---:|---:|---:|---|
| Tiempo medio de carga catálogo (ms) | 1200 | 430 | -64% | perfilado local + logs agregados |
| Tasa de error en red inestable | 8.5% | 3.1% | -5.4 pp | monitorización de errores por endpoint |
| Reintentos manuales por sesión | 2.4 | 0.9 | -62% | eventos UX “retry_tapped” |

---

## 6) Mobile Threat Model Lite

Plantilla y ejemplo completo en la lección dedicada: [Seguridad, privacidad y threat modeling](08-seguridad-privacidad-threat-modeling.md).


## 🔭 Explora el scaffold — Plantillas en acción

```bash
# ADR de Login: plantilla aplicada en el scaffold
cat 01-fundamentos/05-feature-login/ADR-001-login.md

# Especificación BDD: plantilla de escenarios aplicada
cat 01-fundamentos/05-feature-login/00-especificacion-bdd.md | head -40
```

Estos dos archivos son las plantillas de esta lección aplicadas a un caso real. El ADR documenta la decisión arquitectónica; el BDD documenta el comportamiento esperado. Juntos son la evidencia que hace una PR revisable.

---

## Qué sigue

La siguiente lección, [Crosswalk iOS ↔ Android](11-crosswalk-ios-android.md), mapea las responsabilidades de este track iOS a su equivalente en Android, para que puedas colaborar con equipos multiplataforma con un lenguaje técnico común.
