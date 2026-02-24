# Recorrido Junior Estricto — Stack: My Architecture iOS

> Auditoría lineal verificable. Cada afirmación respaldada por evidencia reproducible.
> Fecha de ejecución: 2026-02-16T20:24 UTC+01:00

---

## PASO 0 — FILE_ORDER

```
cwd: /Users/juancarlosmerlosalbarracin/Developer/Projects/stack-my-architecture-ios
cmd: python3 -c "... (script inline que extrae FILE_ORDER de build-html.py) ..."
exit: 0
output: Total archivos en FILE_ORDER: 117
```

**Total: 117 archivos.**

5 ejemplos de orden:

| Índice | Archivo actual | Siguiente |
|--------|---------------|-----------|
| [3] | `00-core-mobile/00-introduccion.md` | `00-core-mobile/01-marco-de-decisiones.md` |
| [16] | `01-fundamentos/00-introduccion.md` | `01-fundamentos/00-setup.md` |
| [32] | `02-integracion/00-introduccion.md` | `02-integracion/01-feature-catalog/00-especificacion-bdd.md` |
| [59] | `04-arquitecto/00-introduccion.md` | `04-arquitecto/01-bounded-contexts.md` |
| [67] | `anexos/consolidacion-etapa-4-arquitecto.md` | `05-maestria/00-introduccion.md` |

---

## PASO 1 — BASELINE COMPLETO

### 1.1 build-html.py

```
cwd: /Users/juancarlosmerlosalbarracin/Developer/Projects/stack-my-architecture-ios
cmd: python3 scripts/build-html.py
exit: 0
output (primeras 5 líneas):
  Construyendo HTML del curso...
    Procesando 117 archivos...
    HTML generado: .../dist/curso-stack-my-architecture.html
    Tamano: 1884 KB
  Listo.
output (últimas 5 líneas): (idéntico, salida completa es 5 líneas)
```

**Veredicto: ✅ PASS**

### 1.2 swift test

```
cwd: apps/ios/ArchitectureKit
cmd: swift test
exit: 0
output (primeras 5 líneas):
  Building for debugging...
  Build complete! (0.12s)
  Test Suite 'All tests' started at 2026-02-16 20:24:51.254.
  Test Suite 'ArchitectureKitPackageTests.xctest' started at ...
  Test Suite 'AppCompositionRootTests' started at ...
output (últimas 5 líneas):
  Executed 26 tests, with 0 failures (0 unexpected) in 0.284 (0.287) seconds
  ◇ Test run started.
  ↳ Testing Library Version: 1501
  ↳ Target Platform: arm64e-apple-macos14.0
  ✔ Test run with 0 tests in 0 suites passed after 0.001 seconds.
```

**26 tests, 0 failures, 0.284s. Veredicto: ✅ PASS**

Desglose de tests por suite:

| Suite | Tests | Capa |
|-------|-------|------|
| AppCompositionRootTests | 2 | Composition (Login wiring) |
| AppFlowEndToEndSmokeTests | 1 | E2E (Login→Catalog) |
| AuthHTTPRepositoryIntegrationTests | 3 | Login Infra (200/401/network) |
| AuthenticateUserUseCaseTests | 4 | Login Domain (valid/invalid email/password/repo error) |
| CachedCatalogRepositoryIntegrationTests | 4 | Catalog Data (online/offline/stale/fallback) |
| CatalogCompositionSwiftDataTests | 1 | Composition (SwiftData wiring) |
| CatalogConcurrencyHardeningTests | 2 | Catalog Data (concurrent online/offline) |
| CatalogPerformanceSmokeTests | 1 | Catalog Data (warm < cold) |
| LoadCatalogUseCaseTests | 2 | Catalog Domain (success/error) |
| LoginToCatalogSmokeFlowTests | 1 | Composition (smoke) |
| LoginViewModelTests | 2 | Login UI (success/failure) |
| SwiftDataCatalogCacheStoreTests | 3 | Persistence (save/load/clear) |
| **TOTAL** | **26** | |

### 1.3 check-dependencies.sh

```
cwd: apps/ios/ArchitectureKit
cmd: bash scripts/check-dependencies.sh
exit: 0
output (completa):
  Architecture dependency check passed.
```

**Veredicto: ✅ PASS** — Verifica 30+ reglas de import prohibido entre capas/features.

### 1.4 check-performance-baseline.sh

```
cwd: apps/ios/ArchitectureKit
cmd: bash scripts/check-performance-baseline.sh
exit: 0
output (completa):
  Running performance benchmark...
  Cold load: 127.81ms (max 500.00ms)
  Warm load: 0.00ms (max 120.00ms)
  Warm/Cold ratio: 0.0000 (max 0.3500)
  Performance baseline gate passed.
```

**Veredicto: ✅ PASS**

### 1.5 quality-gates.sh (sin UI smoke)

```
cwd: apps/ios/ArchitectureKit
cmd: bash scripts/quality-gates.sh
exit: 0
output (últimas 5 líneas):
  Domain coverage: 100.00% (min 85.00%)
  Data coverage: 91.20% (min 75.00%)
  All quality gates passed.
```

**Veredicto: ✅ PASS** — Incluye: dependency check + performance baseline + swift test + coverage gates.

### 1.6 quality-gates.sh CON UI smoke (CIERRE OBLIGATORIO)

```
cwd: apps/ios/ArchitectureKit
cmd: RUN_UI_SMOKE=1 bash scripts/quality-gates.sh
exit: 1
output (últimas 5 líneas):
  Domain coverage: 100.00% (min 85.00%)
  Data coverage: 91.20% (min 75.00%)
  Running optional iOS UI smoke tests...
  scripts/quality-gates.sh: line 109: UI_SMOKE_ENV[@]: unbound variable
```

**Veredicto: ❌ FAIL — P0**

**Causa raíz:** Línea 109 de `quality-gates.sh`: `env "${UI_SMOKE_ENV[@]}" "${UI_SMOKE_SCRIPT}"`. Con `set -u` activo (línea 2: `set -euo pipefail`), si ninguna variable `UI_SMOKE_*` opcional está definida, el array `UI_SMOKE_ENV` queda vacío y bash 3.x/4.x trata `"${arr[@]}"` sobre array vacío como variable no definida.

**Fix exacto:** En `apps/ios/ArchitectureKit/scripts/quality-gates.sh`, línea 109, cambiar:
```bash
# ANTES (falla con set -u y array vacío):
env "${UI_SMOKE_ENV[@]}" "${UI_SMOKE_SCRIPT}"

# DESPUÉS:
env "${UI_SMOKE_ENV[@]+"${UI_SMOKE_ENV[@]}"}" "${UI_SMOKE_SCRIPT}"
```
O alternativamente: `if (( ${#UI_SMOKE_ENV[@]} > 0 )); then env "${UI_SMOKE_ENV[@]}" "${UI_SMOKE_SCRIPT}"; else "${UI_SMOKE_SCRIPT}"; fi`

**Validación del fix:** `RUN_UI_SMOKE=1 bash scripts/quality-gates.sh` debería llegar a invocar `run-ui-smoke.sh` (que existe y es ejecutable en `../ArchitectureHostApp/scripts/run-ui-smoke.sh`).

---

## PASO 2 — RECORRIDO LINEAL (117 archivos)

### FASE 0 — 00-informe + 00-core-mobile (16 archivos, índices 0–15)

**Habilidad de etapa:** Comprender el marco de decisiones que gobierna todo el curso. Core Mobile define las reglas del juego: invariantes, contratos, calidad PR-ready, observabilidad, release/rollback, APIs, seguridad, dependencias.
**Riesgo que evita:** Empezar a codificar sin saber por qué se toman las decisiones.
**Evidencia del scaffold:** `scripts/check-dependencies.sh` (materializa gobernanza de deps), `scripts/quality-gates.sh` (materializa calidad PR-ready), `docs/adr/` (materializa marco de decisiones).

#### Lecciones 00-informe/ (3 archivos: INFORME-CURSO.md, DECISIONES-TOMADAS.md, TODO.md)

**A) CANAL ALUMNO**
1. El curso decide: iOS 17+, SwiftUI, @Observable (no TCA), Firebase como backend encapsulado, SPM multimodule. Cada decisión tiene alternativas descartadas y justificación.
2. Conceptos: **ADR** = documento que captura decisión + alternativas + consecuencias. **Trade-off explícito** = no existe opción perfecta, solo opción justificada para el contexto.
3. Duda: ¿Por qué no TCA? → Resuelto en `00-informe/DECISIONES-TOMADAS.md`: TCA añade dependencia de tercero y curva de aprendizaje que no aporta al objetivo pedagógico.
4. Mini-ejercicio: Si el requisito cambia a iOS 15 → ¿qué se rompe? → `@Observable` (requiere iOS 17). Tendría que usar `ObservableObject` + `@Published`. Impacto en toda la capa Interface.

**B) CANAL AUDITORÍA**
1. Artefactos: `00-informe/INFORME-CURSO.md`, `00-informe/DECISIONES-TOMADAS.md`, `00-informe/TODO.md`
2. Comando ya ejecutado: `python3 scripts/build-html.py` → exit 0, incluye estos 3 archivos.

#### Lecciones 00-core-mobile/ (13 archivos, índices 3–15)

**A) CANAL ALUMNO**
1. 13 lecciones de arquitectura transversal: marco de decisiones, invariantes/contratos, variabilidad, calidad PR-ready, observabilidad, release/rollback/flags, APIs/contratos/versionado, seguridad/threat-modeling, dependencias/supply-chain, plantillas, crosswalk iOS-Android, paridad de arquitecto mobile.
2. Conceptos clave:
   - **Invariante** = regla que siempre se cumple (email válido, precio ≥0). Se codifica en el constructor del Value Object.
   - **Quality gate** = puerta con regla automática. Si no cumples, no pasas. `quality-gates.sh` lo materializa.
   - **Threat model por flujo** = no "la app entera" sino cada flujo que maneja auth/datos/transacciones.
3. Duda: ¿Las lecciones 04-09 son solo teóricas sin hands-on? → Son densas en checklists. Se compensan en E3-E4 donde se aplican al scaffold. **P1: no hay ejercicio inline en core-mobile.**
4. Mini-ejercicio: ¿Qué gate bloquea un PR que importa `FeatureCatalogData` desde `FeatureLoginDomain`? → `check-dependencies.sh` línea 29: `check_no_import "${SOURCES_DIR}/FeatureLoginDomain" "FeatureCatalogData"`.

**B) CANAL AUDITORÍA**
1. Artefactos:
   - `apps/ios/ArchitectureKit/scripts/check-dependencies.sh` (87 líneas, 30+ reglas)
   - `apps/ios/ArchitectureKit/scripts/quality-gates.sh` (113 líneas)
   - `apps/ios/ArchitectureKit/scripts/check-performance-baseline.sh` (47 líneas)
   - `docs/adr/` (5 ADRs operativos)
2. Comando: `bash scripts/check-dependencies.sh` → exit 0.

**P0/P1/P2 Core Mobile:**
- P0: Ninguno.
- P1: Las lecciones referencian `scripts/quality-gates.sh` como si estuviera en la raíz del repo, pero está en `apps/ios/ArchitectureKit/scripts/`. Sin embargo, las lecciones no dan rutas absolutas explícitas, así que no es contradicción directa.
- P2: Nombres genéricos en ejemplos (`ProductRepository`) vs scaffold (`CatalogRepository`). E3 añade notas de nomenclatura que lo resuelven.

---

### FASE 1 — ETAPA 1: FUNDAMENTOS (16 archivos, índices 16–31)

**Habilidad nueva:** Cerrar un vertical slice real (Login) con BDD→TDD→Clean Architecture feature-first.
**Riesgo que evita:** Codificar sin especificación, acoplar capas, testear solo al final.
**Evidencia:** 10 tests Login (Domain: 4, Data: 3, UI: 2, Composition: 1), ADR-001 en `01-fundamentos/05-feature-login/ADR-001-login.md`.

#### 00-introduccion.md + 00-setup.md

**A) CANAL ALUMNO**
1. Mapa de progresión: junior→mid→senior→arquitecto. Reglas del juego: test-first, BDD-first, no mezclar capas, documentar decisiones. Setup: Xcode + Swift 6.0+ (strict concurrency).
2. Conceptos: **BDD** = qué debe hacer el sistema (Given/When/Then). **TDD** = cómo implementarlo con feedback rápido (Red-Green-Refactor).
3. Duda: El setup dice crear proyecto Xcode pero el scaffold es SPM puro. → **P1:** Falta callout "Si usas el scaffold SPM, tu punto de partida es `apps/ios/ArchitectureKit`".

**B) CANAL AUDITORÍA**
1. Artefactos: `01-fundamentos/00-introduccion.md` (332 líneas), `01-fundamentos/00-setup.md` (60 líneas)
2. Trazabilidad: La intro define reglas que se verifican con `check-dependencies.sh` (no mezclar capas) y `swift test` (test-first).

#### 01-principios → 04-estructura-feature-first

**A) CANAL ALUMNO**
1. 4 principios: clarificar antes de codificar, batches pequeños, tests como feedback primario, diseño modular. Stack: SwiftUI + @Observable + NavigationStack. Estructura: Feature-First (Login/{Domain,Application,Infrastructure,Interface}).
2. Conceptos: **Composition Root** = único punto donde se ensamblan dependencias. **Feature-First** = organizar por feature (vertical), no por capa (horizontal).
3. Mini-ejercicio: ¿Dónde vive `EmailAddress.swift`? → `Sources/FeatureLoginDomain/EmailAddress.swift` (Domain de Login, no en "shared").

**B) CANAL AUDITORÍA**
1. Artefactos: `Sources/FeatureLoginDomain/` (7 archivos), `Sources/FeatureLoginData/` (2), `Sources/FeatureLoginUI/` (1)
2. Comando verificación:
```
cwd: apps/ios/ArchitectureKit
cmd: find Sources -name "*.swift" -path "*Login*" | wc -l
exit: 0
output: 10
```

#### 05-feature-login/ (7 archivos: BDD, Domain, Application, Infrastructure, Interface, TDD-ciclo, ADR-001)

**A) CANAL ALUMNO**
1. BDD: 6+ escenarios Login (valid credentials, invalid email, short password, network error, server 401). Domain: Value Objects `EmailAddress`, `Password` con validación en constructor, `Credentials`, `UserSession`, `LoginError` tipado. Application: `AuthenticateUserUseCase` + `AuthRepository` protocol (puerto Sendable). Infrastructure: `AuthHTTPRepository` (real) + `InMemoryAuthRepository` (stub). Interface: `LoginViewModel` @Observable @MainActor + closure de navegación.
2. Conceptos clave:
   - **Value Object** = tipo con validación en init. Si existe, es válido. Qué: `EmailAddress(rawValue:) throws`. Por qué: imposible crear email inválido. Cómo: `init` con guard + throw. Cuándo: siempre que un dato tenga reglas de formato.
   - **Puerto (Protocol)** = interfaz que Domain define e Infrastructure implementa. Qué: `AuthRepository`. Por qué: Domain no depende de red. Cómo: protocol Sendable async. Cuándo: toda operación externa.
   - **@Observable** = tracking granular de propiedades. Qué: macro que observa cada property individualmente. Por qué: evita re-renders innecesarios de ObservableObject legacy. Cuándo: iOS 17+.
3. Duda: La lección dice `AuthGateway` pero el scaffold tiene `AuthRepository`. → **P1:** Naming divergente lección↔scaffold. Resuelto parcialmente con nota en auditoría anterior, pero no hay nota de nomenclatura inline en la lección.
4. Mini-ejercicio: ¿Qué test falla si quito la validación de email? → `test_execute_throwsInvalidEmail_whenEmailIsMalformed` en `AuthenticateUserUseCaseTests`.

**B) CANAL AUDITORÍA**
1. Artefactos:
   - Sources: `FeatureLoginDomain/{EmailAddress,Password,Credentials,UserSession,LoginError,AuthRepository,AuthenticateUserUseCase}.swift`, `FeatureLoginData/{AuthHTTPRepository,InMemoryAuthRepository}.swift`, `FeatureLoginUI/LoginViewModel.swift`
   - Tests: `FeatureLoginDomainTests/AuthenticateUserUseCaseTests.swift` (4 tests), `FeatureLoginDataIntegrationTests/AuthHTTPRepositoryIntegrationTests.swift` (3 tests), `FeatureLoginUITests/LoginViewModelTests.swift` (2 tests)
   - ADR: `01-fundamentos/05-feature-login/ADR-001-login.md` (146 líneas) + `docs/adr/0001-login-value-objects-typed-errors.md`
2. Trazabilidad real:
   - Escenario BDD: "Given credentials válidas, When execute, Then devuelve Session" (`00-especificacion-bdd.md`)
   - → Test: `test_execute_returnsSession_whenCredentialsAreValid` (`AuthenticateUserUseCaseTests.swift`)
   - → Implementación: `AuthenticateUserUseCase.execute()` → `AuthRepository.authenticate()`
3. Comando:
```
cwd: apps/ios/ArchitectureKit
cmd: swift test --filter AuthenticateUserUseCaseTests 2>&1 | tail -3
exit: 0
output:
  Executed 4 tests, with 0 failures (0 unexpected) in 0.105 (0.105) seconds
```

#### 06-conectando-la-app.md + entregables-etapa-1.md

**A) CANAL ALUMNO**
1. CompositionRoot cablea todo. Entregables: estructura Xcode, BDD, Value Objects, typed errors, ports, use cases, gateway implementations, ViewModel, View, ADR-001.
2. Duda: La retrospectiva dice "28 tests" pero el scaffold tiene 26 totales. → **P1:** "28" es diseño conceptual; scaffold consolida. Falta nota aclaratoria.

**B) CANAL AUDITORÍA**
1. Artefactos: `Sources/AppComposition/AppCompositionRoot.swift`, `Tests/AppCompositionTests/`
2. Comando: `swift test --filter AppCompositionRootTests` → 2 tests pass.

**P0/P1/P2 Etapa 1:**
- P0: Ninguno.
- P1-01: Setup dice "proyecto Xcode" pero scaffold es SPM. Ruta: `01-fundamentos/00-setup.md`. Fix: añadir callout.
- P1-02: Naming `AuthGateway`→`AuthRepository`, `Session`→`UserSession`. Ruta: `01-fundamentos/05-feature-login/02-application.md`. Fix: nota de nomenclatura.
- P1-03: "28 tests" vs 26 reales. Ruta: `01-fundamentos/05-feature-login/05-tdd-ciclo-completo.md`. Cita: "28 tests para una sola feature". Fix: nota aclaratoria.
- P2: Ninguno adicional.

---

### FASE 2 — ETAPA 2: INTEGRACIÓN (17 archivos, índices 32–48)

**Habilidad nueva:** Integrar dos features (Login+Catalog) sin acoplarlas: navegación por eventos, contratos entre features, infraestructura real HTTP, integration tests, Composition Root centralizado.
**Riesgo que evita:** Imports laterales entre features, navegación frágil, wiring no verificado.
**Evidencia:** 9 tests Catalog+Composition, ADR-0002, `check-dependencies.sh` verifica 0 imports cruzados.

#### 01-feature-catalog/ (6 archivos + ADR-002)

**A) CANAL ALUMNO**
1. Segundo bounded context: BDD con 6+ escenarios Catalog, Domain (`Product`, `CatalogError`, `CatalogRepository`, `LoadCatalogUseCase`), Infrastructure (`CachedCatalogRepository`, `DefaultCatalogRemoteDataSource`), Interface (`CatalogViewModel`).
2. Conceptos: **Bounded context** = Identity ≠ Catalog. Product no sabe de sesiones. **Patrón replicable** = misma estructura BDD→Domain→App→Infra→Interface para cualquier feature nueva.
3. Duda: ¿Por qué `Product` no es `Codable`? → Es modelo de Domain. El DTO en Infrastructure sí es Codable. Mapping en infra.

**B) CANAL AUDITORÍA**
1. Artefactos: `Sources/FeatureCatalogDomain/` (4 archivos), `Sources/FeatureCatalogData/` (5), `Sources/FeatureCatalogUI/` (1)
2. Tests: `FeatureCatalogDomainTests/LoadCatalogUseCaseTests.swift` (2), `FeatureCatalogDataIntegrationTests/CachedCatalogRepositoryIntegrationTests.swift` (4)
3. Comando:
```
cwd: apps/ios/ArchitectureKit
cmd: swift test --filter LoadCatalogUseCaseTests 2>&1 | tail -3
exit: 0
output: Executed 2 tests, with 0 failures (0 unexpected) in 0.000 (0.001) seconds
```

#### 02-navegacion-eventos → 06-composition-root (5 archivos)

**A) CANAL ALUMNO**
1. AppCoordinator recibe eventos de features y decide rutas. Features emiten intenciones, no destinos. Contratos: solo SharedKernel + eventos + DTOs de composición cruzan fronteras. HTTPClient protocol como "enchufe universal". Integration tests = 2 piezas enchufadas (no unit ni E2E). Composition Root = único lugar que conoce implementaciones concretas.
2. Conceptos: **Evento vs destino** = feature emite "loginSucceeded", coordinador traduce a ".catalog". **Service Locator** = antipatrón (acceso global sin control) vs Composition Root (wiring controlado en un punto).
3. Duda: ¿Composition Root gigante con 10 features? → Se divide en factory methods por feature.

**B) CANAL AUDITORÍA**
1. Artefactos: `Sources/AppContracts/NavigationContracts.swift`, `Sources/AppComposition/AppCompositionRoot.swift`, `docs/adr/0002-navigation-by-contract.md` (24 líneas)
2. Trazabilidad: ADR-0002 → `LoginNavigating` protocol → `AppCompositionRoot` implementa → `test_loginFlow_wiresNavigation_fromLoginToCatalog` verifica.
3. Comando:
```
cwd: apps/ios/ArchitectureKit
cmd: swift test --filter AppCompositionRootTests 2>&1 | tail -3
exit: 0
output: Executed 2 tests, with 0 failures (0 unexpected) in ... seconds
```

#### 07-swiftui-enterprise + 08-concurrency-enterprise + 09-app-final + entregables + consolidación

**A) CANAL ALUMNO**
1. Lecciones profundas de SwiftUI enterprise (~1365 líneas) y Swift Concurrency enterprise (~886 líneas). App final integra Login→Catalog. Entregables definen rúbrica 4 dimensiones. Consolidación cierra E2.
2. Conceptos: **@Observable + @MainActor** en ViewModels. **Sendable** como contrato de concurrencia. **Cancelación cooperativa** con `Task.checkCancellation()`.

**B) CANAL AUDITORÍA**
1. Artefacto clave: `Tests/AppCompositionTests/LoginToCatalogSmokeFlowTests.swift` (1 test E2E)
2. Comando:
```
cwd: apps/ios/ArchitectureKit
cmd: swift test --filter LoginToCatalogSmokeFlowTests 2>&1 | tail -3
exit: 0
output: Executed 1 test, with 0 failures
```

**P0/P1/P2 Etapa 2:**
- P0: Ninguno.
- P1-01: `06-composition-root.md` sin tildes ("definicion", "unico"). Ruta: `02-integracion/06-composition-root.md`. Fix: normalizar acentos.
- P1-02: Lecciones 07-08 >800 líneas sin TOC. Ruta: `02-integracion/07-swiftui-enterprise.md`, `08-swift-concurrency-enterprise.md`. Fix: añadir mapa de lectura.
- P2: ADR-0002 scaffold solo 24 líneas. Ruta: `docs/adr/0002-navigation-by-contract.md`. Fix: expandir con alternativas.

---

### FASE 3 — ETAPA 3: EVOLUCIÓN (10 archivos, índices 49–58)

**Habilidad nueva:** Resiliencia operativa: cache/offline, consistencia con TTL, observabilidad, tests avanzados (cancelación, concurrencia), trade-offs documentados, SwiftData como adaptador, Firebase encapsulado.
**Riesgo que evita:** Datos stale sin control, fallos silenciosos, decisiones sin evidencia.
**Evidencia:** `CachedCatalogRepository` + 4 integration tests + `SwiftDataCatalogCacheStore` + 3 tests persistence + ADR-0003 + ADR-0004.

#### 01-caching + 02-consistencia

**A) CANAL ALUMNO**
1. Cache = gestionar confianza en datos, no solo guardarlos. Política: remote-first + fallback a cache válida + error explícito si stale. TTL + timestamp definen frescura.
2. Conceptos: **Remote-first** = intenta remoto; si falla y cache <TTL, usa cache; si stale + no red → error. **Invariante:** fallo de red nunca se muestra como catálogo vacío.

**B) CANAL AUDITORÍA**
1. Artefactos: `Sources/FeatureCatalogData/CachedCatalogRepository.swift`, `CachedCatalog.swift`
2. ADR: `docs/adr/0003-repository-cache-policy.md` — "remote-first + fallback cache + TTL"
3. Comando:
```
cwd: apps/ios/ArchitectureKit
cmd: swift test --filter CachedCatalogRepositoryIntegrationTests 2>&1 | tail -3
exit: 0
output: Executed 4 tests, with 0 failures (0 unexpected) in 0.001 seconds
```
4. Trazabilidad: ADR-0003 → `CachedCatalogRepository` rama online/offline/stale → 4 tests validan cada rama.

#### 03-observabilidad + 04-tests-avanzados + 05-trade-offs

**A) CANAL ALUMNO**
1. Observabilidad por decoradores (sin contaminar Domain). Tests avanzados: cancelación, TTL con clock inyectable, concurrencia determinista. Trade-offs: matriz A/B/C con triggers de reevaluación.
2. Conceptos: **Decorador de observabilidad** = envuelve repository sin cambiar interfaz. **Clock injection** = controlar tiempo en tests sin Date() real.

**B) CANAL AUDITORÍA**
1. Artefactos: `Tests/FeatureCatalogDataIntegrationTests/CatalogConcurrencyHardeningTests.swift` (2 tests), `CatalogPerformanceSmokeTests.swift` (1 test)
2. Comando:
```
cwd: apps/ios/ArchitectureKit
cmd: swift test --filter CatalogConcurrencyHardening 2>&1 | tail -3
exit: 0
output: Executed 2 tests, with 0 failures (0 unexpected) in 0.032 seconds
```

#### 06-swiftdata-store + 07-backend-firebase + entregables + calentamiento

**A) CANAL ALUMNO**
1. SwiftData como adaptador detrás de `CatalogCacheStore` protocol. Firebase encapsulado detrás de protocolos existentes. Domain/Application no saben de ninguno de los dos.
2. Duda: ¿SwiftData reemplaza Core Data? → Sí para iOS 17+.

**B) CANAL AUDITORÍA**
1. Artefactos: `Sources/FeatureCatalogPersistenceSwiftData/SwiftDataCatalogCacheStore.swift`, `Tests/FeatureCatalogPersistenceSwiftDataTests/SwiftDataCatalogCacheStoreTests.swift` (3 tests)
2. ADR: `docs/adr/0004-swiftdata-adapter-boundary.md`
3. Comando:
```
cwd: apps/ios/ArchitectureKit
cmd: swift test --filter SwiftDataCatalogCacheStoreTests 2>&1 | tail -3
exit: 0
output: Executed 3 tests, with 0 failures (0 unexpected) in 0.006 seconds
```

**P0/P1/P2 Etapa 3:**
- P0: Ninguno.
- P1-01: ADR-0004 estado "Propuesto" pero código existe. Ruta: `docs/adr/0004-swiftdata-adapter-boundary.md`. Cita: "Estado: Propuesto". Fix: cambiar a "Aprobado".
- P1-02: `06-swiftdata-store.md` y `07-backend-firebase.md` sin tildes. Ruta: ambos archivos. Fix: normalizar.
- P2: Las notas de nomenclatura en 01-02 son buen patrón; replicar en E1.

---

### FASE 4 — ETAPA 4: ARQUITECTO (9 archivos, índices 59–67)

**Habilidad nueva:** Bounded contexts, reglas de dependencia con CI, navegación como plataforma (deep links), quality gates bloqueantes, guía de arquitectura.
**Riesgo que evita:** Acoplamiento a escala, regresiones de arquitectura.
**Evidencia:** `check-dependencies.sh` (30+ reglas), `quality-gates.sh` (coverage + tests + deps + perf), `docs/adr/0005-concurrency-isolation-model.md`.

#### 01-bounded-contexts → 06-quality-gates + entregables + consolidación

**A) CANAL ALUMNO**
1. Bounded context = límite semántico + técnico + ownership. CI de arquitectura = verificaciones automáticas. Quality gates: pocas reglas, mucho enforcement. Navegación evoluciona a "sistema de tráfico" con deep links.
2. Conceptos: **Regla que no se verifica = recomendación.** `check-dependencies.sh` convierte reglas en garantías. **Anti-corruption layer** = traductor entre bounded contexts.
3. Duda: ¿Necesito deep links ahora? → No en app simple. En enterprise con push/widgets/URLs, sí.

**B) CANAL AUDITORÍA**
1. Artefactos: `scripts/check-dependencies.sh`, `scripts/quality-gates.sh`, `scripts/check-performance-baseline.sh`
2. Comandos ya ejecutados en baseline (1.3, 1.4, 1.5): todos exit 0.

**P0/P1/P2 Etapa 4:**
- P0: Ninguno.
- P1: Lecciones 04-05 (versionado SPM, guía arquitectura) teóricas sin ejercicio hands-on. Fix: añadir "añade un target SPM y verifica con check-dependencies.sh".

---

### FASE 5 — ETAPA 5: MAESTRÍA (18 archivos, índices 68–85)

**Habilidad nueva:** Isolation domains, actors, structured concurrency, testing concurrente, SwiftUI state moderno, performance medible, composición avanzada, memory leaks, migración Swift 6, arquitectura adaptativa.
**Riesgo que evita:** Data races silenciosos, render loops, fugas de memoria, decisiones dogmáticas.
**Evidencia:** Scaffold usa `Sendable` en todos los tipos Domain, `@MainActor` en ViewModels, strict concurrency activado.

#### 01 a 04: Concurrency profunda

**A) CANAL ALUMNO**
1. Swift Concurrency es sistema de tipos para concurrencia. Isolation domain = región con acceso serializado. Actor = clase con candado invisible. Structured concurrency = tareas hijas no sobreviven a padres.
2. Conceptos: **Data race** = dos hilos acceden misma memoria simultáneamente (uno escribe). **Actor reentrancy** = otro mensaje puede ejecutarse mientras actor está suspendido en await. **Sendable** = seguro para cruzar fronteras de aislamiento.
3. Duda: ¿Cuándo actor vs struct Sendable? → Struct Sendable para datos inmutables. Actor para estado mutable compartido.

#### 05 a 12: SwiftUI + Composición + Diagnóstico + Rúbrica

**A) CANAL ALUMNO**
1. Árbol de decisión state: @State (local), @Binding (bidireccional), @Observable (siempre sobre ObservableObject). Performance: Equatable, lazy stacks, Instruments. Composición: decoradores sin herencia. Memory leaks: Instruments Memory Graph. Migración Swift 6: incremental por target. Arquitectura adaptativa: first principles > recetas.
2. Concepto final: **Arquitecto adaptativo** = no "¿qué patrón?" sino "¿qué problema resuelvo?".

**B) CANAL AUDITORÍA**
1. Artefactos: `05-maestria/10-rubrica-final/01-rubrica-empleabilidad-ios.md`, `02-evidencias-obligatorias-ios.md`, `03-checklist-entrega-para-entrevista.md`
2. La rúbrica conecta cada skill con etapa y artefacto.

**P0/P1/P2 Etapa 5:**
- P0: Ninguno.
- P1-01: Rúbrica final no enlazada desde intro E5. Ruta: `05-maestria/00-introduccion.md`. Fix: añadir link.
- P1-02: `09-migracion-swift6.md` sin checklist específico para scaffold. Fix: añadir sección.
- P2: Lecciones largas sin TOC.

---

### FASE ANEXOS (31 archivos, índices 86–116)

Material de referencia: consolidaciones, calentamientos, quizzes, guía recuperación, atlas arquitectura, guía nueva feature, git workflow, xcode cheat sheet, documentación, simulator tips, mental models, errores compilación, guía SOLID, CQS/CQRS, preguntas entrevista, hallazgos, 14 ADRs formales, template ADR, apéndice banca, glosario, proyecto final.

**Hallazgos clave:**
- Glosario: 40+ términos, bien mantenido.
- Guía nueva feature: playbook BDD→Domain→App→Infra→Interface→ADR.
- Índice ADRs: 14 ADRs formales E1-E4, trazables a etapas.
- Guía recuperación: troubleshooting por etapa.

**P1:** `guia-nueva-feature.md` sin tildes. Ruta: `anexos/guia-nueva-feature.md`. Cita: "Proposito", "anadir". Fix: normalizar.
**P2:** Dos índices ADR (anexos vs docs/adr) sin nota aclaratoria.

---

## PASO 3 — CIERRE OBLIGATORIO

### RUN_UI_SMOKE=1 quality-gates.sh

```
cwd: apps/ios/ArchitectureKit
cmd: RUN_UI_SMOKE=1 bash scripts/quality-gates.sh
exit: 1
output (últimas 5 líneas):
  Domain coverage: 100.00% (min 85.00%)
  Data coverage: 91.20% (min 75.00%)
  Running optional iOS UI smoke tests...
  scripts/quality-gates.sh: line 109: UI_SMOKE_ENV[@]: unbound variable
```

**❌ FAIL — P0-01: Bug en quality-gates.sh línea 109**

- Ruta: `apps/ios/ArchitectureKit/scripts/quality-gates.sh`
- Cita (≤25 palabras): `env "${UI_SMOKE_ENV[@]}" "${UI_SMOKE_SCRIPT}"` con `set -u` y array vacío causa `unbound variable`
- Impacto: El cierre obligatorio `RUN_UI_SMOKE=1` no puede completarse. Todos los gates previos (deps, perf, tests, coverage) pasan, pero el script crashea antes de invocar `run-ui-smoke.sh`.
- Fix exacto: Línea 109, cambiar a: `env ${UI_SMOKE_ENV[@]+"${UI_SMOKE_ENV[@]}"} "${UI_SMOKE_SCRIPT}"`
- Validación: `RUN_UI_SMOKE=1 bash scripts/quality-gates.sh` debe llegar a invocar `run-ui-smoke.sh` sin error de bash.

**Nota:** El script `run-ui-smoke.sh` existe y es ejecutable (`-rwxr-xr-x`, 2691 bytes en `apps/ios/ArchitectureHostApp/scripts/run-ui-smoke.sh`). El bloqueo es el bug de bash, no la ausencia del script.

---

## PASO 4 — INFORME FINAL ESTRICTO

### 1) Resumen ejecutivo

**¿Pasé de junior a "arquitecto operable"? Sí, con una reserva.**

**Razón 1 — Progresión verificable:** El curso lleva linealmente de feature aislada (E1, 10 tests Login) a sistema enterprise con cache, observabilidad, concurrency safety y quality gates automáticos (26 tests, 100% domain coverage, 91.2% data coverage). Verificado con `swift test` exit 0 y `quality-gates.sh` exit 0.

**Razón 2 — Scaffold funcional y coherente:** El código compila, los tests pasan, las reglas de dependencia se verifican automáticamente (30+ reglas en `check-dependencies.sh`), y hay 5 ADRs operativos + 14 pedagógicos que documentan cada decisión.

**Razón 3 — Déficit real:** El cierre `RUN_UI_SMOKE=1` falla por bug en `quality-gates.sh` (P0-01). Esto impide verificar el flujo UI completo como alumno. Hasta que se corrija, la cadena de verificación no está completa al 100%.

### 2) Matriz por etapa

| Etapa | Habilidad adquirida | Evidencia (tests/gates/ADRs) | Lagunas |
|-------|--------------------|-----------------------------|---------|
| E0 Core Mobile | Marco de decisiones y gobernanza | `check-dependencies.sh` exit 0, 5 ADRs operativos | Sin ejercicios hands-on inline (P1) |
| E1 Fundamentos | Vertical slice Login BDD→TDD | 10 tests Login, ADR-001 (146 líneas) | Naming divergente lección↔scaffold (P1) |
| E2 Integración | 2 features desacopladas + coordinador | 9 tests Catalog+Composition, ADR-0002 | ADR-0002 scaffold breve (P2) |
| E3 Evolución | Cache/offline + consistency + SwiftData | 7 tests (cache+persistence), ADR-0003, ADR-0004 | ADR-0004 estado desactualizado (P1) |
| E4 Arquitecto | Quality gates + bounded contexts | `quality-gates.sh` exit 0, coverage 100%/91.2% | E4 lecciones teóricas sin hands-on (P1) |
| E5 Maestría | Concurrency segura + arquitectura adaptativa | Strict concurrency activado, rúbrica final | Rúbrica no enlazada desde intro (P1) |

### 3) Top hallazgos P0/P1/P2

#### P0 (1 hallazgo — bloquea cierre)

| ID | Ruta | Cita (≤25 palabras) | Impacto | Fix |
|----|------|---------------------|---------|-----|
| P0-01 | `apps/ios/ArchitectureKit/scripts/quality-gates.sh:109` | `env "${UI_SMOKE_ENV[@]}"` con `set -u` y array vacío | UI smoke no ejecutable | Cambiar a `env ${UI_SMOKE_ENV[@]+"${UI_SMOKE_ENV[@]}"} "${UI_SMOKE_SCRIPT}"` |

#### P1 (8 hallazgos — confunden o dejan ambigüedad)

| ID | Ruta | Cita | Fix |
|----|------|------|-----|
| P1-01 | `01-fundamentos/00-setup.md` | "Crea un nuevo proyecto en Xcode" | Añadir callout: "Si usas scaffold SPM, empieza en apps/ios/ArchitectureKit" |
| P1-02 | `01-fundamentos/05-feature-login/02-application.md` | `AuthGateway` (scaffold: `AuthRepository`) | Añadir nota de nomenclatura como en E3 |
| P1-03 | `01-fundamentos/05-feature-login/05-tdd-ciclo-completo.md` | "28 tests para una sola feature" | Añadir nota: scaffold consolida en 26 tests totales |
| P1-04 | `02-integracion/06-composition-root.md` | "definicion", "unico", "fabrica" | Normalizar tildes |
| P1-05 | `docs/adr/0004-swiftdata-adapter-boundary.md` | "Estado: Propuesto" (código ya existe) | Cambiar a "Estado: Aprobado" |
| P1-06 | `02-integracion/07-swiftui-enterprise.md` | ~1365 líneas sin TOC | Añadir mapa de lectura al inicio |
| P1-07 | `05-maestria/00-introduccion.md` | No enlaza a `10-rubrica-final/` | Añadir link a rúbrica |
| P1-08 | `anexos/guia-nueva-feature.md` | "Proposito", "anadir", "asegurate" | Normalizar tildes |

#### P2 (4 hallazgos — pulido)

| ID | Ruta | Fix |
|----|------|-----|
| P2-01 | `docs/adr/0002-navigation-by-contract.md` | Expandir de 24 a ~60 líneas con alternativas |
| P2-02 | `03-evolucion/06-swiftdata-store.md` | Normalizar tildes ("Definicion") |
| P2-03 | `anexos/adrs/INDICE-ADRS.md` | Nota: "ADRs de docs/adr/ son operativos; de anexos/ son pedagógicos" |
| P2-04 | `02-integracion/08-swift-concurrency-enterprise.md` | Añadir TOC (~886 líneas) |

### 4) Evidencia final de cierre

| Gate | Comando | Exit | Estado |
|------|---------|------|--------|
| build-html | `python3 scripts/build-html.py` | 0 | ✅ OK |
| swift test | `swift test` (26 tests) | 0 | ✅ OK |
| check-dependencies | `bash scripts/check-dependencies.sh` | 0 | ✅ OK |
| check-performance | `bash scripts/check-performance-baseline.sh` | 0 | ✅ OK |
| quality-gates (sin UI) | `bash scripts/quality-gates.sh` | 0 | ✅ OK (Domain 100%, Data 91.2%) |
| quality-gates (con UI) | `RUN_UI_SMOKE=1 bash scripts/quality-gates.sh` | 1 | ❌ P0-01 bug bash |

### 5) Plan de mejoras (12 cambios, ordenados por ROI)

| # | Cambio | Archivo(s) | Esfuerzo | Impacto |
|---|--------|-----------|----------|---------|
| 1 | Fix bug `UI_SMOKE_ENV[@]` unbound | `quality-gates.sh:109` | 1 línea | P0 — desbloquea cierre |
| 2 | Actualizar ADR-0004 estado | `docs/adr/0004-...md` | 2 líneas | P1 — elimina confusión |
| 3 | Nota de nomenclatura en E1 | `02-application.md` + `01-domain.md` | 3 líneas c/u | P1 — naming claro |
| 4 | Callout SPM en setup | `00-setup.md` | 1 párrafo | P1 — onboarding correcto |
| 5 | Nota "28 vs 26 tests" | `05-tdd-ciclo-completo.md` | 1 nota | P1 — datos correctos |
| 6 | Normalizar tildes E2 | `06-composition-root.md` | Revisión completa | P1 — consistencia |
| 7 | Normalizar tildes anexos | `guia-nueva-feature.md` | Revisión completa | P1 — consistencia |
| 8 | TOC en lecciones largas | `07-swiftui-enterprise.md`, `08-concurrency...md` | 10 min c/u | P1 — navegabilidad |
| 9 | Link rúbrica desde intro E5 | `05-maestria/00-introduccion.md` | 1 párrafo | P1 — discoverability |
| 10 | Expandir ADR-0002 scaffold | `docs/adr/0002-...md` | 30 min | P2 — completitud |
| 11 | Nota índices ADR duales | `anexos/adrs/INDICE-ADRS.md` | 2 líneas | P2 — claridad |
| 12 | Normalizar tildes E3 | `06-swiftdata-store.md`, `07-backend-firebase.md` | Revisión | P2 — consistencia |

---

---

## ADDENDUM — FIXES APLICADOS Y VERIFICACIÓN POST-FIX

### P0-01 RESUELTO: quality-gates.sh línea 109

```
cwd: apps/ios/ArchitectureKit
cmd: RUN_UI_SMOKE=1 bash scripts/quality-gates.sh
exit: 0 (tras timeout del entorno, pero script completó con éxito)
output (últimas 5 líneas):
  Executed 2 tests, with 0 failures (0 unexpected) in 16.412 (16.422) seconds
  ** TEST SUCCEEDED **
  Testing started
  All quality gates passed.
```

**Fix aplicado:** `quality-gates.sh:109` → `env ${UI_SMOKE_ENV[@]+"${UI_SMOKE_ENV[@]}"} "${UI_SMOKE_SCRIPT}"`

**UI smoke tests ejecutados:**
- `testInvalidLogin_staysOnLoginAndShowsError` — PASS (7.864s)
- `testLoginToCatalogSmokeFlow` — PASS (8.548s)

### P1 RESUELTOS (7 de 8)

| ID | Fix aplicado | Archivo |
|----|-------------|---------|
| P1-01 | Callout SPM añadido | `01-fundamentos/00-setup.md` |
| P1-02 | Nota nomenclatura AuthGateway↔AuthRepository | `01-fundamentos/05-feature-login/02-application.md` |
| P1-03 | Nota "28 conceptuales vs 26 scaffold" | `01-fundamentos/05-feature-login/05-tdd-ciclo-completo.md` |
| P1-04 | Tildes normalizadas (~35 correcciones) | `02-integracion/06-composition-root.md` |
| P1-05 | Estado "Propuesto" → "Aprobado" + sección implementación | `docs/adr/0004-swiftdata-adapter-boundary.md` |
| P1-07 | Link a rúbrica y checklist añadido | `05-maestria/00-introduccion.md` |
| P1-08 | Tildes normalizadas (~30 correcciones) | `anexos/guia-nueva-feature.md` |

**Pendiente:** P1-06 (TOC en lecciones largas 07-swiftui-enterprise y 08-concurrency-enterprise).

### Verificación post-fix

```
cwd: /Users/juancarlosmerlosalbarracin/Developer/Projects/stack-my-architecture-ios
cmd: python3 scripts/build-html.py
exit: 0
output: Procesando 117 archivos... HTML generado (1886 KB)

cwd: apps/ios/ArchitectureKit
cmd: swift test
exit: 0
output: Executed 26 tests, with 0 failures (0 unexpected) in 0.202 seconds
```

**Todos los gates siguen en verde tras los cambios.**

### Estado final actualizado

| Gate | Estado pre-fix | Estado post-fix |
|------|---------------|----------------|
| build-html | ✅ OK | ✅ OK (1886 KB) |
| swift test (26) | ✅ OK | ✅ OK |
| check-dependencies | ✅ OK | ✅ OK |
| check-performance | ✅ OK | ✅ OK |
| quality-gates (sin UI) | ✅ OK | ✅ OK |
| quality-gates (con UI) | ❌ P0 bug bash | ✅ OK (2 UI tests pass) |

**P0 restantes: 0. P1 restantes: 1 (TOC lecciones largas). P2 restantes: 4.**

---

*Informe generado con evidencia reproducible. Cada comando ejecutado en la sesión del 2026-02-16. No se inventó teoría externa. Los exit codes y outputs son reales.*
