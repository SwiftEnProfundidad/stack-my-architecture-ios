# Purpose and Scope

This rubric defines the **minimum professional bar** for an iOS engineer and the **higher bar** expected from a Mobile Architect.

It is not designed to reward familiarity with APIs or frameworks in isolation, but to evaluate **decision-making quality under real-world constraints**: correctness, safety, operability, and long-term maintainability.

The rubric assumes an enterprise context where:
- Systems evolve over time.
- Teams change.
- Failures are inevitable.
- Poor decisions compound silently.

Its goal is to distinguish between code that merely works and systems that can be **safely evolved, operated, and governed**.

---

# What This Rubric Evaluates

This rubric evaluates **outcomes and evidence**, not intent.

It focuses on:
- Architectural boundaries and contracts.
- Correctness and safety (including concurrency).
- Quality gates and test discipline.
- Operability (observability, release, rollback).
- Security and privacy posture.
- Traceability of decisions through explicit artifacts.

A submission is evaluated as a **system**, not as a collection of files.

---

# What This Rubric Does Not Evaluate

This rubric does **not** evaluate:
- Knowledge of specific APIs or syntactic features.
- Code volume, cleverness, or stylistic preferences.
- Pattern usage without contextual justification.
- Personal opinions or undocumented assumptions.

Technology choices are acceptable **only when justified by explicit constraints, trade-offs, and evidence**.

---

# Evaluation Principles

## Principle 1 — Context Over Patterns
There are no universally correct architectures.
Decisions are evaluated based on how well they respond to **explicit constraints** (time, risk, scale, team composition), not on theoretical purity.

Pattern application without contextual justification is considered a weakness.

---

## Principle 2 — Explicit Trade-offs
Every architectural decision introduces trade-offs.

Strong solutions:
- Acknowledge alternatives.
- Explain why options were rejected.
- Make accepted trade-offs explicit.

Unacknowledged trade-offs indicate shallow reasoning.

---

## Principle 3 — Invariants First
Invariants define what must **never** happen in the system
(e.g., data corruption, loss of confirmed user actions, security or privacy violations).

Any solution that violates an invariant, regardless of other benefits, is automatically disqualified.

---

## Principle 4 — Design for Change, Not Prediction
Architectures are evaluated on their ability to **absorb change**, not to predict the future.

Strong designs:
- Make frequent changes easy.
- Protect stable areas from accidental coupling.
- Favor incremental evolution over big-bang rewrites.

Over-engineering for hypothetical futures is penalized.

---

## Principle 5 — Evidence Over Opinion
Claims must be supported by **observable evidence**.

Acceptable evidence includes:
- Tests and coverage.
- Metrics before and after changes.
- ADRs and RFCs.
- Operational artifacts (logs, alerts, runbooks).

Statements without evidence are treated as opinions and do not contribute to the score.

---

## Principle 6 — Operability Is Part of Correctness
A system that cannot be observed, rolled back, or safely operated is considered incomplete.

Correctness includes:
- Knowing when the system is failing.
- Limiting blast radius.
- Recovering safely from incidents.

Operability is a core architectural responsibility, not an optional add-on.

---

## Principle 7 — Governance Enables Scale
Systems fail at scale not because of individual mistakes, but because of **ungoverned evolution**.

Architectural governance is evaluated through:
- Dependency rules.
- Quality gates.
- Decision traceability.
- Shared standards enforced by tooling and process.

Absence of governance mechanisms is a structural risk.

---

# Threshold Interpretation

The **Minimum Hireable** threshold represents a professional baseline suitable for working safely in an enterprise codebase.

The **Architect Ready** threshold represents the ability to:
- Make and defend architectural decisions.
- Reduce systemic risk.
- Enable teams to move faster without degrading quality.

The difference between the two is not knowledge, but **judgment**.

---

# Rúbrica final de empleabilidad iOS (Production-Readiness)

## Propósito

Esta rúbrica define una señal defendible de salida para el curso iOS. Sirve para autoevaluación, preparación de entrevista y defensa de portfolio con evidencia. No evalúa opiniones: evalúa decisiones, implementación, operación y trazabilidad.

Está alineada con el Core Mobile en [`00-core-mobile/04-calidad-pr-ready.md`](../../00-core-mobile/04-calidad-pr-ready.md), [`00-core-mobile/05-observabilidad-operacion.md`](../../00-core-mobile/05-observabilidad-operacion.md), [`00-core-mobile/06-release-rollback-flags.md`](../../00-core-mobile/06-release-rollback-flags.md), [`00-core-mobile/07-apis-contratos-versionado.md`](../../00-core-mobile/07-apis-contratos-versionado.md), [`00-core-mobile/08-seguridad-privacidad-threat-modeling.md`](../../00-core-mobile/08-seguridad-privacidad-threat-modeling.md), [`00-core-mobile/09-dependency-governance-supply-chain.md`](../../00-core-mobile/09-dependency-governance-supply-chain.md) y [`00-core-mobile/10-plantillas.md`](../../00-core-mobile/10-plantillas.md).

## Reglas de scoring

Puntuación total: **100 puntos**.

Cada categoría se puntúa en una escala 0–100 interna y se multiplica por su peso.

Fórmula:

`Total = Σ (score_categoria × peso_categoria)`

Donde el peso está expresado en porcentaje.

## Hard blockers (fallo automático)

Si aparece cualquiera de estos bloqueadores, el resultado final es **No apto**, aunque el total supere umbrales:

- No tests o cobertura no significativa en áreas críticas requeridas.
- Patrones de concurrencia inseguros (estado mutable compartido sin aislamiento explícito).
- Ausencia de manejo de errores en flujos de red/autenticación.
- Ausencia de estrategia de rollback/flags para features de riesgo.
- Filtración de PII en logs o analytics.
- Ausencia de artefactos de evidencia para decisiones clave (ADRs, checklist PR, métricas antes/después).

### Criterio operativo de “cobertura significativa”

Para evitar ambigüedad, esta rúbrica considera cobertura significativa cuando se cumple uno de estos esquemas:

- **Domain/Core**: objetivo recomendado `85–90%+`.
- **Data/Repositories**: objetivo recomendado `80–85%+`.
- **UI**: objetivo recomendado `60–70%+` **o** evidencia equivalente por tests de contrato/integración/aceptación cuando la cobertura por línea no represente bien el riesgo.

La regla no premia un número aislado: exige evidencia de protección real en caminos críticos.

### Red flags explícitas de concurrencia insegura

Se considera hard blocker de concurrencia si aparece cualquiera de estos patrones:

- Uso de `@MainActor` como parche global para esconder carreras sin delimitar aislamiento.
- Mutación de estado compartido desde `Task.detached` o concurrencia no estructurada sin frontera explícita.
- Ignorar cancelación o absorber `CancellationError` sin tratamiento.
- Fronteras `Sendable`/actor no definidas para datos compartidos entre dominios de ejecución.

### Qué cuenta como estrategia real de rollback/flags

Ejemplos válidos de estrategia:

- Kill-switch operativo para desactivar ruta de riesgo.
- Flag server-side con control de exposición.
- Criterios explícitos de phased rollout/canary con umbrales de parada.
- Fallback funcional definido para degradación controlada.

Ejemplo inválido (hard blocker):

- “Si falla, sacamos hotfix” como único plan.

### Checklist mínimo para evitar fuga de PII

Esta rúbrica considera PII en móvil, como mínimo: email, teléfono, matrícula, ubicación precisa, identificadores persistentes y tokens de sesión.

Reglas mínimas:

- Nunca loguear tokens.
- Enmascarar identificadores sensibles.
- Aplicar redacción por defecto en logging/analytics.
- Usar sampling en eventos ruidosos para reducir exposición accidental.

### Mínimo obligatorio de trazabilidad de evidencia

Sin este set mínimo, aplica hard blocker de trazabilidad:

- `>= 3` ADRs.
- `>= 1` RFC.
- `>= 1` PR review checklist aplicado.
- `>= 1` tabla de métricas before/after.
- Minimal Observability Spec.
- Release Readiness Checklist.
- Threat Model Lite.
- API Contract Checklist.

## Umbrales de decisión

- **Minimum Hireable**: `>= 70/100` y sin hard blockers.
- **Architect Ready**: `>= 85/100` y sin hard blockers, con mínimo `>= 75` en Observabilidad/Operación, Seguridad/Privacidad y Arquitectura/Límites.

## Categorías y pesos

| Categoría | Peso | Qué se evalúa | Evidencia esperada |
|---|---:|---|---|
| Architecture & Boundaries (Clean / Feature-First / Contracts) | 15% | Límites claros, contratos entre módulos, dependencias dirigidas | Diagrama de dependencias + contratos + ADRs |
| Concurrency Safety (Swift 6 / Sendable / actors / cancellation) | 15% | Aislamiento correcto, cancelación, ausencia de data races | Tests concurrentes + decisiones de aislamiento |
| Testing & Quality Gates (BDD/TDD + cobertura) | 15% | Estrategia de pruebas y gates reproducibles | CI verde + cobertura y matriz de tests |
| API Integration Discipline (contratos, taxonomía de errores, retries/backoff) | 10% | Integración robusta y consistente | API checklist + manejo de errores por categoría |
| Observability & Operability (logs/metrics, SLO/error budget, alert hygiene) | 15% | Señales accionables y operación realista | Spec de observabilidad + runbook + SLO |
| Release Strategy (flags, phased rollout, rollback) | 10% | Despliegue controlado y mitigación | Release checklist + plan rollback |
| Security & Privacy (tokens, PII, threat model lite) | 10% | Protección de datos y superficie de ataque | Threat model lite + evidencia de redacción PII |
| Performance & UX (budget, SwiftUI perf, accessibility baseline) | 5% | Rendimiento y UX medibles | Métricas before/after + baseline accesibilidad |
| Documentation & Decision Traceability (ADRs/RFCs, DoD, PR review) | 5% | Trazabilidad de decisiones y disciplina de entrega | ADRs + RFC + DoD + PR checklist |

## Bandas de calidad por categoría

| Banda | Rango | Interpretación |
|---|---:|---|
| Deficiente | 0–49 | Riesgo alto, no defendible en entrevista técnica |
| Operativo básico | 50–69 | Funciona, pero con huecos de producción |
| Hireable sólido | 70–84 | Defendible para rol iOS con guía de equipo |
| Architect-level | 85–100 | Defendible para diseño, operación y evolución |

## Criterios medibles recomendados por categoría

### Testing & Quality Gates

- **Domain/Core**: cobertura objetivo **85–90%+**.
- **Data/Repositories**: cobertura objetivo **80–85%+**.
- **UI**: cobertura objetivo **60–70%+** o evidencia equivalente con tests de contrato/integración/aceptación cuando aplique.
- Tasa de flaky tests en suite crítica: **< 2%**.

### Observability & Operability

- SLO definido para al menos 2 flujos críticos.
- Error budget explícito y acción definida cuando se agota.
- Alertas accionables: 100% con owner y runbook asociado.

### Performance & UX

- Cold start p50 y p95 medidos en dispositivo real o baseline reproducible.
- Frame drops en flujo crítico medidos y comparados before/after.
- Baseline de accesibilidad (labels, navegación y contraste) validada.

### Security & Privacy

- Tokens en storage seguro de plataforma.
- Política de redacción de PII aplicada en logs.
- Threat model lite actualizado y con mitigaciones priorizadas.

## Resultado final

| Estado | Condición |
|---|---|
| No apto | Cualquier hard blocker activo |
| No apto | Total < 70 |
| Minimum Hireable | Total >= 70 y sin hard blockers |
| Architect Ready | Total >= 85, sin hard blockers y mínimos por categoría crítica |
