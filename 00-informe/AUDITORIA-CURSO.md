# Auditoría del Curso: Stack My Architecture iOS

Fecha: 2026-02-16

## Resumen ejecutivo

Se completó una auditoría integral del curso iOS con 8 lotes de mejoras incrementales. Todos los quality gates pasan en verde tras las modificaciones.

## Verificación final

| Gate | Resultado |
|------|-----------|
| `python3 scripts/build-html.py` | ✅ 117 archivos, 1884 KB |
| `swift test` | ✅ 26 tests, 0 failures |
| `./scripts/quality-gates.sh` | ✅ Domain 100%, Data 91.20% |
| `./scripts/check-dependencies.sh` | ✅ passed |
| `./scripts/check-performance-baseline.sh` | ✅ passed |

## Hallazgos y resolución

### P0 — Críticos (todos resueltos)

| ID | Hallazgo | Resolución |
|----|----------|------------|
| P0-01 | Cadena de navegación rota en 02-integracion (saltaba 4 lecciones) | Regenerada cadena completa Anterior/Siguiente en 82 archivos según FILE_ORDER |
| P0-02 | 23 archivos sin enlaces Anterior/Siguiente | Todos los archivos del curso tienen navegación correcta |
| P0-03 | Cadena rota en 01-fundamentos (setup flow) | Corregida: setup → principios → BDD → TDD → stack → estructura |
| P0-04 | FILE_ORDER de 05-maestria con rúbrica antes del contenido final | Reordenado: contenido → entregables → rúbrica final. 37 archivos actualizados |

### P1 — Importantes (todos resueltos)

| ID | Hallazgo | Resolución |
|----|----------|------------|
| P1-01 | 00-core-mobile esquelético (20-106 líneas) | 9 archivos enriquecidos con: modelo mental, diagrama Mermaid, ejemplo conectado al scaffold, cuándo-sí/cuándo-no |
| P1-02 | Etapas 3-4 sin ejercicios guiados | 13 ejercicios guiados añadidos (7 en Etapa 3, 6 en Etapa 4). Cada uno con: objetivo, instrucciones paso a paso, criterios de éxito, solución razonada con código |
| P1-03 | 07-swiftui-enterprise y 08-concurrency-enterprise sin cierre | Añadido cierre narrativo, ejercicio guiado trazable al scaffold y conexión explícita al siguiente paso en ambas lecciones |
| P1-04 | Alineación doc↔scaffold pendiente | Verificada. Discrepancias de nomenclatura (ProductRepository vs CatalogRepository) resueltas con notas de nomenclatura en 4 archivos de Etapa 3 |

### P2 — Pulido (todos resueltos)

| ID | Hallazgo | Resolución |
|----|----------|------------|
| P2-01 | Acentos inconsistentes en 07-swiftui-enterprise, 08-concurrency-enterprise, 06-swiftdata-store, 07-backend-firebase | 279 acentos corregidos (138 + 80 + 25 + 36) |
| P2-02 | entregables-etapa-5 sin navegación final | Resuelto en Lote 1 (navegación global) |
| P2-03 | Annexes sin referencia desde lecciones adyacentes | Verificado: los entregables ya enlazan correctamente a los annexes de consolidación/calentamiento |

## Lotes ejecutados

| Lote | Descripción | Archivos afectados |
|------|-------------|-------------------|
| 1 | Navegación Anterior/Siguiente completa | 82 archivos |
| 2 | Reorden FILE_ORDER 05-maestria + nav | 37 archivos + build-html.py |
| 3 | Enriquecimiento 00-core-mobile | 9 archivos |
| 4 | Ejercicios guiados Etapas 3-4 | 13 archivos |
| 5 | Cierre narrativo enterprise | 2 archivos |
| 6 | Alineación doc↔scaffold | 4 archivos (notas nomenclatura) |
| 7 | Pulido de acentos | 4 archivos (279 correcciones) |
| 8 | Informe y cierre | Este documento |

## Matriz curricular: Etapa → Skill → Evidencia

| Etapa | Skill principal | Ejercicio guiado | Test trazable |
|-------|----------------|-----------------|---------------|
| 0-Core | Decisiones, invariantes, contratos, variabilidad, calidad, observabilidad, release, APIs, seguridad, dependencias | — (referencia transversal) | — |
| 1-Fundamentos | Build: TDD, Clean Architecture, Feature Login | Step-by-step TDD en 6 lecciones | 26 tests scaffold |
| 2-Integración | Integrate: Feature Catalog, navegación, contratos, composition root | Ejercicio SwiftUI enterprise + Concurrency enterprise | Smoke tests, integration tests |
| 3-Evolución | Operate: cache, consistencia, observabilidad, tests avanzados, trade-offs, SwiftData, Firebase | 7 ejercicios guiados (cache TTL, invalidación, decorador logging, cancelación, trade-off, round-trip SwiftData, encapsulación Firebase) | Tests de cache, persistencia, composición |
| 4-Arquitecto | Govern: bounded contexts, reglas dependencia, navegación deeplinks, versionado SPM, guía arquitectura, quality gates | 6 ejercicios guiados (mapear contexts, verificar regla, trazar deep link, grafo SPM, auditar guía, ejecutar gates) | check-dependencies.sh, quality-gates.sh |
| 5-Maestría | Optimize: isolation domains, actors, structured concurrency, testing concurrente, SwiftUI moderno, performance, composición, memory leaks, migración Swift 6, debugging | Contenido narrativo profundo (10 lecciones × 300-500 líneas) | — (ejercicios de pensamiento arquitectónico) |

## Notas de mantenimiento

- **FILE_ORDER** es la fuente de verdad para navegación. Cualquier archivo nuevo debe añadirse a `scripts/build-html.py` y regenerar la navegación.
- **Nomenclatura doc↔scaffold**: las lecciones de Etapa 3 usan nombres genéricos (ProductRepository) con nota de mapeo a nombres reales del scaffold (CatalogRepository). Si el scaffold se renombra, actualizar las notas.
- **Acentos**: las lecciones 07-swiftui-enterprise y 08-concurrency-enterprise fueron escritas originalmente sin acentos. Se corrigieron 279 instancias. Futuras ediciones deben mantener acentos correctos.
