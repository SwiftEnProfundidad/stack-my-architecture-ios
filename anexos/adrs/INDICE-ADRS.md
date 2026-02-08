# Indice de ADRs (Architecture Decision Records)

Este documento centraliza todas las decisiones arquitectónicas de la edición vigente del curso.

---

## Como usar este indice

- Cada ADR tiene un identificador único (`ADR-XXX`).
- El estado indica si la decisión sigue activa.
- La ubicación apunta al archivo ADR completo.
- Las lecciones pueden incluir contexto inline, pero la fuente formal es este índice + archivos ADR.

---

## Tabla de ADRs

| ADR | Titulo | Estado | Etapa | Ubicacion |
|---|---|---|---|---|
| ADR-001 | Login con Value Objects + validación en construcción | Aprobado | E1 | [ADR-001-login](../../01-fundamentos/05-feature-login/ADR-001-login.md) |
| ADR-002 | Catalog con Domain semántico y errores tipados | Aprobado | E2 | [ADR-002-catalog](../../02-integracion/01-feature-catalog/ADR-002-catalog.md) |
| ADR-003 | Composition Root único para ensamblaje | Aprobado | E2 | [ADR-003-composition-root-unico](ADR-003-composition-root-unico.md) |
| ADR-004 | Navegación event-driven desacoplada | Aprobado | E2 | [ADR-004-navegacion-event-driven](ADR-004-navegacion-event-driven.md) |
| ADR-005 | Contratos entre features vía eventos/modelos compartidos mínimos | Aprobado | E2 | [ADR-005-contratos-features](ADR-005-contratos-features.md) |
| ADR-006 | Infra de red mínima real con `URLSessionHTTPClient` | Aprobado | E2 | [ADR-006-infra-network-urlsession](ADR-006-infra-network-urlsession.md) |
| ADR-007 | Cache `network-first` + TTL + fallback controlado | Aprobado | E3 | [ADR-007-cache-network-first-ttl](ADR-007-cache-network-first-ttl.md) |
| ADR-008 | Política explícita de consistencia e invalidación | Aprobado | E3 | [ADR-008-consistencia-invalidation-policy](ADR-008-consistencia-invalidation-policy.md) |
| ADR-009 | Observabilidad por decoradores y logger de dominio de app | Aprobado | E3 | [ADR-009-observabilidad-por-decoradores](ADR-009-observabilidad-por-decoradores.md) |
| ADR-010 | Firebase como backend principal encapsulado | Aprobado | E3 | [ADR-010-firebase-backend-principal](ADR-010-firebase-backend-principal.md) |
| ADR-011 | Bounded contexts con ownership y contratos | Aprobado | E4 | [ADR-011-bounded-contexts-governance](ADR-011-bounded-contexts-governance.md) |
| ADR-012 | Reglas de dependencia progresivas (doc -> script -> compilador) | Aprobado | E4 | [ADR-012-reglas-dependencia-progresivas](ADR-012-reglas-dependencia-progresivas.md) |
| ADR-013 | Modularización/versionado SPM progresivos por señales | Aprobado | E4 | [ADR-013-versionado-spm-progresivo](ADR-013-versionado-spm-progresivo.md) |
| ADR-014 | Quality gates conceptuales orientados a arquitectura | Aprobado | E4 | [ADR-014-quality-gates-conceptuales](ADR-014-quality-gates-conceptuales.md) |

---

## Reglas para crear nuevas ADRs

Crear ADR cuando:

1. Afecta a más de una feature o bounded context.
2. Cambia contratos públicos o política de dependencia.
3. Cambia estrategia de concurrencia, navegación, persistencia o gobernanza.
4. Introduce trade-off A/B/C con impacto de equipo.

No crear ADR para cambios locales de bajo impacto y fácil reversión.

---

## Cadencia de mantenimiento

- Revisar este índice al cierre de cada etapa.
- Marcar reemplazos cuando una decisión quede obsoleta.
- Mantener trazabilidad entre ADR y lecciones correspondientes.
