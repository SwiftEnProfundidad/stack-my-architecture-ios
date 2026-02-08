# Stack: My Architecture iOS

> Curso práctico para diseñar, construir y evolucionar una base de código iOS enterprise con disciplina de ingeniería real.

---

## Navegación

- [Objetivo del curso](#objetivo)
- [Índice de contenidos](#índice-de-contenidos)
- [Progresión formativa](#progresión-formativa)
- [Cómo usar este material](#cómo-usar-este-material)

---

## Objetivo

Ser capaz de diseñar, construir y evolucionar una base de código iOS de producción (enterprise) de forma:

- **Modular** — escalable por features y por equipo.
- **Mantenible** — cambio barato y refactors seguros.
- **Testable** — confianza con estrategia de pruebas disciplinada.
- **Concurrencia-segura** — Swift 6.2 strict concurrency, sin data races.
- **Centrada en negocio** — DDD con lenguaje ubicuo, invariantes, eventos y límites claros.

---

## Índice de contenidos

### Informe fundacional

- [Informe completo del curso](00-informe/INFORME-CURSO.md)

### Etapa 1 — Junior: Fundamentos operables

- [Introducción y objetivos](01-fundamentos/00-introduccion.md)
- [Principios de ingeniería](01-fundamentos/01-principios-ingenieria.md)
- [Metodología BDD: especificación y descubrimiento](01-fundamentos/02-metodologia-bdd-tdd.md)
- [Metodología TDD: práctica Red-Green-Refactor](01-fundamentos/02-metodologia-tdd-practica.md)
- [Stack tecnológico](01-fundamentos/03-stack-tecnologico.md)
- [Estructura Feature-First](01-fundamentos/04-estructura-feature-first.md)
- **Feature Login:**
  - [Especificación BDD](01-fundamentos/05-feature-login/00-especificacion-bdd.md)
  - [Domain](01-fundamentos/05-feature-login/01-domain.md)
  - [Application](01-fundamentos/05-feature-login/02-application.md)
  - [Infrastructure](01-fundamentos/05-feature-login/03-infrastructure.md)
  - [Interface SwiftUI](01-fundamentos/05-feature-login/04-interface-swiftui.md)
  - [TDD: ciclo completo](01-fundamentos/05-feature-login/05-tdd-ciclo-completo.md)
  - [ADR-001: Login](01-fundamentos/05-feature-login/ADR-001-login.md)
- [Entregables Etapa 1](01-fundamentos/entregables-etapa-1.md)

### Etapa 2 — Mid: Integración y disciplina

- [Introducción](02-integracion/00-introduccion.md)
- **Feature Catalog:**
  - [Especificación BDD](02-integracion/01-feature-catalog/00-especificacion-bdd.md)
  - [Domain](02-integracion/01-feature-catalog/01-domain.md)
  - [Application](02-integracion/01-feature-catalog/02-application.md)
  - [Infrastructure](02-integracion/01-feature-catalog/03-infrastructure.md)
  - [Interface SwiftUI](02-integracion/01-feature-catalog/04-interface-swiftui.md)
  - [ADR-002: Catalog](02-integracion/01-feature-catalog/ADR-002-catalog.md)
- [Navegación por eventos](02-integracion/02-navegacion-eventos.md)
- [Contratos entre features](02-integracion/03-contratos-features.md)
- [Infraestructura real: Network](02-integracion/04-infra-real-network.md)
- [Integration tests](02-integracion/05-integration-tests.md)
- [Composition Root](02-integracion/06-composition-root.md)
- [Entregables Etapa 2](02-integracion/entregables-etapa-2.md)

### Etapa 3 — Senior: Evolución y resiliencia

- [Introducción](03-evolucion/00-introduccion.md)
- [Caching y offline](03-evolucion/01-caching-offline.md)
- [Consistencia e invalidación](03-evolucion/02-consistencia.md)
- [Observabilidad](03-evolucion/03-observabilidad.md)
- [Tests avanzados](03-evolucion/04-tests-avanzados.md)
- [Trade-offs y riesgos](03-evolucion/05-trade-offs.md)
- [SwiftData como ProductStore](03-evolucion/06-swiftdata-store.md)
- [Backend Firebase](03-evolucion/07-backend-firebase.md)
- [Entregables Etapa 3](03-evolucion/entregables-etapa-3.md)

### Etapa 4 — Arquitecto: Plataforma y gobernanza

- [Introducción](04-arquitecto/00-introduccion.md)
- [Bounded contexts](04-arquitecto/01-bounded-contexts.md)
- [Reglas de dependencia y CI](04-arquitecto/02-reglas-dependencia-ci.md)
- [Navegación y deep links como plataforma](04-arquitecto/03-navegacion-deeplinks.md)
- [Versionado y SPM](04-arquitecto/04-versionado-spm.md)
- [Guía de arquitectura](04-arquitecto/05-guia-arquitectura.md)
- [Quality gates](04-arquitecto/06-quality-gates.md)
- [Entregables Etapa 4](04-arquitecto/entregables-etapa-4.md)

### Etapa 5 — Maestría: Concurrency, SwiftUI moderno y composición

- [Introducción](05-maestria/00-introduccion.md)
- [Isolation domains y Sendable](05-maestria/01-isolation-domains.md)
- [Actors en arquitectura](05-maestria/02-actors-en-arquitectura.md)
- [Structured concurrency](05-maestria/03-structured-concurrency.md)
- [Testing concurrente](05-maestria/04-testing-concurrente.md)
- [SwiftUI state moderno](05-maestria/05-swiftui-state-moderno.md)
- [SwiftUI performance](05-maestria/06-swiftui-performance.md)
- [Composición avanzada](05-maestria/07-composicion-avanzada.md)
- [Memory leaks y diagnóstico](05-maestria/08-memory-leaks-y-diagnostico.md)
- [Migración a Swift 6](05-maestria/09-migracion-swift6.md)
- [Entregables Etapa 5](05-maestria/entregables-etapa-5.md)

### Anexos

- [Atlas visual de arquitectura](anexos/diagramas/atlas-arquitectura.md) — Diagramas globales de referencia
- [Glosario](anexos/glosario.md)
- [Template ADR](anexos/adrs/TEMPLATE-ADR.md)

---

## Progresión formativa

```
Junior ──────> Mid ──────> Senior ──────> Arquitecto ──────> Maestría
Fundamentos    Integración  Evolución      Plataforma         Concurrency
1 feature      2 features   Cache/offline  Bounded contexts   Actors/Sendable
BDD/TDD base   Navegación   Observabilidad Gobernanza         SwiftUI moderno
               Contratos    Trade-offs     Quality gates      Composición
                                                              Diagnóstico
```

---

## Cómo usar este material

1. **Sigue el orden**: cada etapa construye sobre la anterior.
2. **No saltes a código sin BDD**: primero escenarios, luego contratos, luego TDD.
3. **Cada lección incluye**: explicación, código completo (producción + tests), diagramas, ADRs y checklist de smells.
4. **Formato**: Markdown versionable en Git. HTML navegable se genera a partir de estos fuentes.

---

## Contrato de profundidad (aplica a todas las lecciones)

Para mantener el nivel que pides (de junior absoluto a arquitecto operable), cada lección del curso se considera válida solo si cubre este contrato:

1. **Definición simple + modelo mental**: explicación para quien empieza de cero, sin perder precisión técnica.
2. **Cuándo sí / cuándo no**: límites de uso y anti-patrones, con motivo técnico.
3. **Ejemplo mínimo + ejemplo realista**: no basta el snippet corto; se necesita traducción a caso enterprise.
4. **BDD + TDD trazables**: escenario, test, implementación y refactor deben estar conectados.
5. **Concurrencia/estado/performance cuando aplique**: aislamiento, cancelación, sendability, flujo de datos o coste de render explicitados.
6. **Evidencia verificable**: código, tests, decisiones y señales de operación.

Este contrato no es opcional ni decorativo; es la forma de convertir conocimiento en hábito profesional.

### Integración de skills en trabajo diario

Cuando la lección lo requiera, se aplica explícitamente:

- `swift-concurrency`: decisiones de aislamiento, `Sendable`, cancelación y pruebas concurrentes.
- `swiftui-expert-skill`: estado moderno, composición de vistas y performance medible.
- `windsurf-rules-ios` (si aplica al repo objetivo): consistencia de estilo y gobernanza técnica del equipo.

La meta no es “mencionar skills”, sino usarlas para tomar mejores decisiones y dejar evidencia de impacto.

---

## Qué NO es este curso

- No es una chuleta de patrones.
- No es escribir producción y agregar tests al final.
- No es usar `@MainActor` para silenciar warnings sin justificar límites.
- No es adoptar modas; es construir un sistema coherente guiado por requisitos, tests y límites.
