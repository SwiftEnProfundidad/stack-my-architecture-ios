# Roadmap V2 (Práctico e Incremental)

Esta versión traduce el curso a ejecución real en repo con dos features: `Login` y `Catalog`.

## Progreso actual en repo

- [x] Package SPM multi-target base creado.
- [x] Etapa 1 operable (Login + tests de UseCase/ViewModel/Composition).
- [x] Etapa 2 base operable (AuthRepository HTTP + SessionStore + integración).
- [x] Etapa 3 base operable (Catalog cache/offline + TTL + integración).
- [x] Etapa 3 persistencia real (SwiftData adapter in-memory testable).
- [x] Etapa 3 observabilidad base (métrica de path + cache hit/miss + latencia ms).
- [x] Etapa 4 base operable (ADRs en `/docs/adr` + gate de dependencias).
- [x] Etapa 4 quality gates CI (workflow + cobertura mínima por capa).
- [x] Etapa 5 base (smoke flow Login -> Catalog + composición de Catalog con SwiftData).
- [x] Etapa 5 avanzada (smoke E2E Login->Catalog load + performance cold/warm).
- [x] Etapa 5 avanzada (gate baseline de performance por commit).
- [x] Etapa 5 avanzada (hardening concurrente bajo carga + UI smoke con host app/XCUITest).

## Etapa 1 (Junior) — Base operable

**Objetivo:** cerrar un vertical slice real de `Login` con capas separadas y tests.

**Temas concretos**
- Contratos de dominio (`AuthRepository`, `AuthenticateUserUseCase`).
- Value Objects (`EmailAddress`, `Password`).
- Navegación desacoplada por protocolo (`LoginNavigating`).
- Composition Root mínimo.

**Qué se construye**
- Package SPM multi-target en `apps/ios/ArchitectureKit`.
- `Login` end-to-end (Domain + Data in-memory + UI ViewModel + Composition).

**DoD**
- [x] `AuthenticateUserUseCase` con tests unitarios.
- [x] `LoginViewModel` con tests de estado y navegación.
- [x] `AppCompositionRoot` probado para wiring `Login -> Catalog`.

## Etapa 2 (Mid) — Integración + Concurrency temprana

**Objetivo:** usar `async/await` como base de networking y sesión.

**Temas concretos**
- Repositorio real de auth (HTTP + store de sesión).
- Cancelación y errores tipados.
- Contratos de navegación entre features.

**Qué se construye**
- `FeatureLoginData` con adaptadores reales.
- Tests de integración de repositorio de auth.

**DoD**
- [x] Casos de uso async.
- [x] Tests de integración online/error/credenciales inválidas.
- [x] Navegación desacoplada validada por contrato.

## Etapa 3 (Senior) — Catalog + Cache/Offline

**Objetivo:** agregar `Catalog` con política de datos explícita.

**Temas concretos**
- `remote-first + fallback cache`.
- TTL y consistencia básica.
- SwiftData aislado detrás de adaptadores.

**Qué se construye**
- `CatalogRepository` con store local.
- Métricas de cache hit y latencia.

**DoD**
- [x] Tests integración online/offline.
- [x] SwiftData solo en capa de infraestructura.
- [x] Política de cache documentada.

## Etapa 4 (Arquitecto) — Gobernanza y ADRs

**Objetivo:** convertir decisiones en reglas auditables.

**Temas concretos**
- ADRs versionadas.
- Reglas de dependencia entre targets.
- Quality gates medibles.

**Qué se construye**
- `/docs/adr/000x-*.md`.
- CI con reglas de dependencia, tests y cobertura.

**DoD**
- [x] ADRs mínimas creadas y vigentes.
- [x] CI falla ante violación de arquitectura.
- [x] Cobertura mínima por capa.

## Etapa 5 (Maestría) — Hardening y evolución

**Objetivo:** reforzar concurrencia, performance y mantenibilidad.

**Temas concretos**
- Actor isolation donde aporte.
- Tests concurrentes en rutas críticas.
- Optimización de render/carga.

**Qué se construye**
- Refactors guiados por métricas.
- Evidencia final de arquitectura operable.

**DoD**
- [x] Pruebas concurrentes en data layer.
- [x] UI smoke de flujo Login -> Catalog.
- [x] Métricas before/after documentadas.

## Modularización elegida

Se usa **un solo Package SPM con múltiples targets** para este curso.

Razón práctica:
- menor fricción didáctica y operacional;
- dependencias explícitas desde el inicio;
- suficiente para 2 features sin sobrecoste de versionado.

## Reglas de dependencia (curso)

- `Feature*Domain` no depende de UI ni Data.
- `Feature*Data` depende de su `Feature*Domain`.
- `Feature*UI` depende de su `Feature*Domain` + `AppContracts`.
- `AppComposition` es el único target que conoce todas las piezas.
- Las features no se importan entre sí.
