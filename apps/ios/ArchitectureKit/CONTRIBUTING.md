# Contribución (ArchitectureKit)

## Requisitos

- Xcode/Swift con soporte Swift 6.2
- `jq` instalado (usado por `quality-gates.sh`)

## Flujo local antes de PR

```bash
cd apps/ios/ArchitectureKit
./scripts/quality-gates.sh
```

El script ejecuta:
- tests con cobertura;
- reglas de dependencia;
- benchmark cold/warm contra baseline;
- cobertura mínima por capa:
  - Domain >= 85%
  - Data >= 75%
- smoke tests de flujo E2E y performance cold/warm.

Smoke UI opcional (Host App + XCUITest):

```bash
cd apps/ios/ArchitectureKit
RUN_UI_SMOKE=1 ./scripts/quality-gates.sh
```

Si además defines `UI_SMOKE_RESULT_BUNDLE_PATH` o `UI_SMOKE_HISTORY_PATH`, las rutas relativas
se interpretan respecto al directorio desde el que lanzas `quality-gates.sh`.

O ejecución aislada:

```bash
cd apps/ios/ArchitectureHostApp
./scripts/run-ui-smoke.sh
```

Con evidencia `.xcresult` local:

```bash
cd apps/ios/ArchitectureHostApp
UI_SMOKE_RESULT_BUNDLE_PATH=/tmp/architecturehostapp-ui-smoke.xcresult ./scripts/run-ui-smoke.sh
```

Con reintento anti-flaky:

```bash
cd apps/ios/ArchitectureHostApp
UI_SMOKE_ATTEMPTS=2 ./scripts/run-ui-smoke.sh
```

Extracción de evidencias:

```bash
cd apps/ios/ArchitectureHostApp
./scripts/extract-xcresult-evidence.sh /tmp/architecturehostapp-ui-smoke.xcresult /tmp/architecturehostapp-ui-smoke-evidence
```

Resumen histórico local:

```bash
cd apps/ios/ArchitectureHostApp
./scripts/summarize-ui-smoke-history.sh artifacts/ui-smoke-history.jsonl
```

## Baseline de performance

Archivo: `benchmarks/performance-baseline.json`

Para actualizar baseline conscientemente:
1. Ejecuta `./scripts/check-performance-baseline.sh`
2. Revisa `benchmarks/performance-last-run.json`
3. Si el cambio está justificado, ajusta `performance-baseline.json` en el mismo PR y explica el motivo.

## Ajustar thresholds temporalmente

```bash
DOMAIN_MIN_COVERAGE=90 DATA_MIN_COVERAGE=80 ./scripts/quality-gates.sh
```

## CI en GitHub

Workflow: `.github/workflows/architecturekit-quality.yml`

El workflow publica:
- artefacto `architecturehostapp-ui-smoke-xcresult`;
- artefacto `architecturehostapp-ui-smoke-evidence` (diagnostics/attachments);
- resumen de ejecución en `GITHUB_STEP_SUMMARY` (resultado + evidencias + histórico).

Se dispara en `push` y `pull_request` cuando hay cambios en:
- `apps/ios/ArchitectureKit/**`
- `apps/ios/ArchitectureHostApp/**`
- `docs/adr/**`

## Criterios de merge

- `quality-gates.sh` en verde.
- Sin violaciones de dependencia entre capas/features.
- ADR actualizada o nueva cuando cambie una decisión arquitectónica.
