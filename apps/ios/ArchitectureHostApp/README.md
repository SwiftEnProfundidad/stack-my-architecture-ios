# ArchitectureHostApp

Host app SwiftUI mínima para smoke tests reales de arquitectura:
- Login con `AppCompositionRoot`
- Navegación desacoplada `Login -> Catálogo`
- Carga de catálogo con repositorio cacheado
- Escenarios UI: login válido y login inválido

## Ejecutar smoke test

```bash
cd apps/ios/ArchitectureHostApp
./scripts/run-ui-smoke.sh
```

El script:
1. genera el proyecto con `xcodegen`;
2. detecta un simulador iPhone disponible;
3. ejecuta `XCUITest` del flujo end-to-end.
4. permite reintentos controlados con `UI_SMOKE_ATTEMPTS`.
5. guarda histórico local en `artifacts/ui-smoke-history.jsonl` (ignorado por git).

Nota: si defines `UI_SMOKE_RESULT_BUNDLE_PATH` o `UI_SMOKE_HISTORY_PATH` con rutas relativas,
se resuelven respecto al directorio desde el que invocas el script.

Para guardar el resultado `.xcresult`:

```bash
cd apps/ios/ArchitectureHostApp
UI_SMOKE_RESULT_BUNDLE_PATH=/tmp/architecturehostapp-ui-smoke.xcresult ./scripts/run-ui-smoke.sh
```

Con reintentos (anti-flaky):

```bash
cd apps/ios/ArchitectureHostApp
UI_SMOKE_ATTEMPTS=2 ./scripts/run-ui-smoke.sh
```

Resumen legible del bundle:

```bash
cd apps/ios/ArchitectureHostApp
./scripts/summarize-xcresult.sh /tmp/architecturehostapp-ui-smoke.xcresult
```

Extraer evidencias (diagnostics + attachments de fallos):

```bash
cd apps/ios/ArchitectureHostApp
./scripts/extract-xcresult-evidence.sh /tmp/architecturehostapp-ui-smoke.xcresult /tmp/architecturehostapp-ui-smoke-evidence
```

Resumen de estabilidad histórica:

```bash
cd apps/ios/ArchitectureHostApp
./scripts/summarize-ui-smoke-history.sh artifacts/ui-smoke-history.jsonl
```
