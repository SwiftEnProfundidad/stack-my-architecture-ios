# ArchitectureKit (Curso)

Scaffold práctico del curso para ejecutar arquitectura por capas con dos features:
- `Login` (implementada verticalmente en Etapa 1)
- `Catalog` (política cache/offline preparada en Etapa 3)

Guía de contribución/CI: [`CONTRIBUTING.md`](CONTRIBUTING.md)

## Estructura

- `CoreDomain`
- `AppContracts`
- `FeatureLoginDomain`
- `FeatureLoginData`
- `FeatureLoginUI`
- `FeatureCatalogDomain`
- `FeatureCatalogUI`
- `AppComposition`

## Verificación rápida

```bash
cd apps/ios/ArchitectureKit
swift test
./scripts/check-dependencies.sh
./scripts/check-performance-baseline.sh
./scripts/quality-gates.sh
RUN_UI_SMOKE=1 ./scripts/quality-gates.sh
```

`quality-gates.sh` aplica:
- tests con cobertura;
- cobertura mínima por capa (Domain >= 85%, Data >= 75%);
- reglas de dependencia;
- benchmark cold/warm contra baseline (`benchmarks/performance-baseline.json`).
- smoke UI opcional con Host App/XCUITest (`RUN_UI_SMOKE=1`).

Si pasas `UI_SMOKE_RESULT_BUNDLE_PATH` o `UI_SMOKE_HISTORY_PATH` a `quality-gates.sh`,
las rutas relativas se resuelven respecto al directorio donde lo ejecutas.

## Host App (UI smoke)

`apps/ios/ArchitectureHostApp` contiene una app SwiftUI mínima para validar wiring real:
- login con `AppCompositionRoot`;
- navegación `Login -> Catálogo`;
- carga de catálogo con repositorio cacheado.

Ejecución directa:

```bash
cd apps/ios/ArchitectureHostApp
./scripts/run-ui-smoke.sh
```

Con bundle de resultado para evidencia:

```bash
cd apps/ios/ArchitectureHostApp
UI_SMOKE_RESULT_BUNDLE_PATH=/tmp/architecturehostapp-ui-smoke.xcresult ./scripts/run-ui-smoke.sh
```

Con reintento controlado:

```bash
cd apps/ios/ArchitectureHostApp
UI_SMOKE_ATTEMPTS=2 ./scripts/run-ui-smoke.sh
```

Exportar evidencias desde `.xcresult`:

```bash
cd apps/ios/ArchitectureHostApp
./scripts/extract-xcresult-evidence.sh /tmp/architecturehostapp-ui-smoke.xcresult /tmp/architecturehostapp-ui-smoke-evidence
```

Histórico de estabilidad local:

```bash
cd apps/ios/ArchitectureHostApp
./scripts/summarize-ui-smoke-history.sh artifacts/ui-smoke-history.jsonl
```

## Estado actual del scaffold

- Etapa 1:
  - vertical slice de `Login` con tests unitarios y de wiring.
- Etapa 2:
  - `AuthHTTPRepository` desacoplado (`HTTPClient` + `SessionStore`).
  - tests de integración para éxito, 401 y fallo de red.
- Etapa 3:
  - `CachedCatalogRepository` con política `remote-first + fallback cache + TTL`.
  - tests de integración online/offline con toggle de conectividad.
- Etapa 3 (persistencia real):
  - adaptador `SwiftDataCatalogCacheStore` detrás de `CatalogCacheStore`.
  - tests in-memory de save/load/clear.
- Etapa 4 (base):
  - ADRs iniciales en `docs/adr`.
  - quality gate de dependencias (`scripts/check-dependencies.sh`).
- Etapa 5 (base):
  - smoke test de flujo `Login -> Catalog` con `AuthHTTPRepository`.
  - smoke E2E `Login -> Catalog load` con composición real.
  - performance smoke cold/warm (`remote` vs `offline cache`) con umbrales.
- Etapa 5 (hardening):
  - stress tests concurrentes en `CachedCatalogRepository` (online/offline).
  - smoke UI real con Host App + XCUITest.
