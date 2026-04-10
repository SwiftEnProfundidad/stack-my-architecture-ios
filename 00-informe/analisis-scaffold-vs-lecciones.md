# Análisis: Scaffold vs Lecciones — ¿El estudiante puede construir el proyecto paso a paso?

**Fecha:** 2026-04-06
**Estado:** Hallazgos iniciales — requiere decisiones del autor

---

## Resumen ejecutivo

El scaffold (`apps/ios/ArchitectureKit/`) **compila, pasa tests y es funcional** como paquete SPM + HostApp. Sin embargo, un estudiante que siga las lecciones paso a paso **no** llega al scaffold actual sin intervención manual significativa. Las divergencias son de tres tipos:

1. **Estructura:** las lecciones enseñan un proyecto Xcode single-target con carpetas; el scaffold es un paquete SPM con 13 targets.
2. **Naming:** los nombres pedagógicos difieren del scaffold (documentado parcialmente en `anexos/equivalencias-scaffold.md`, pero con errores).
3. **API de Domain:** el Catalog del scaffold usa `Product(id:title:price:)` con `Double`, mientras las lecciones enseñan `Product(id:name:price:imageURL:)` con `Price(amount:currency:)`.

---

## Hallazgo 1 — CRÍTICO: `equivalencias-scaffold.md` tiene entradas incorrectas

El archivo `anexos/equivalencias-scaffold.md` es la referencia canónica, pero varias entradas no coinciden con el scaffold real:

| Línea | equivalencias dice | Scaffold real |
|---|---|---|
| 25 | `RemoteAuthGateway` → `RemoteAuthRepository` en `RemoteAuthRepository.swift` | Archivo real: `AuthHTTPRepository.swift`, tipo: `AuthHTTPRepository` |
| 26 | `StubAuthGateway` → `StubAuthRepository` en `StubAuthRepository.swift` | Archivo real: `InMemoryAuthRepository.swift`, tipo: `InMemoryAuthRepository` |
| 28 | `LoginView` en `Sources/FeatureLoginUI/LoginView.swift` | **ARCHIVO NO EXISTE** — solo hay `LoginViewModel.swift` |
| 84 | `LoadCatalogUseCase` → `FetchProductsUseCase` | Nombre real: `LoadCatalogUseCase` (NO cambió) |

### Acción requerida
Actualizar `equivalencias-scaffold.md` para reflejar el scaffold real.

---

## Hallazgo 2 — CRÍTICO: No existen vistas SwiftUI en el scaffold

El scaffold no contiene archivos de vista:

- `FeatureLoginUI/` solo tiene `LoginViewModel.swift` — **no hay `LoginView.swift`**
- `FeatureCatalogUI/` solo tiene `CatalogViewModel.swift` — **no hay `CatalogView.swift`**

Las únicas vistas SwiftUI están en `ArchitectureHostApp/Sources/ArchitectureHostAppApp.swift` como structs inline (`LoginScreen`, `CatalogScreen`). Además, usan patrones legacy:

| HostApp (actual) | Lecciones (enseñan) |
|---|---|
| `@StateObject` + `ObservableObject` + `@Published` | `@Observable` + `@State` (macro moderna) |
| `AppStore` monolítico con `@Published var route` | ViewModel por feature con `@Observable` |

### Impacto para el estudiante
- Las lecciones 04-interface-swiftui (Login y Catalog) enseñan a crear `LoginView.swift` y `CatalogView.swift`, pero esos archivos no existen en el scaffold.
- El estudiante no tiene un archivo de referencia para verificar su trabajo.
- El HostApp usa patrones diferentes a los enseñados.

### Opciones
1. **Crear `LoginView.swift` y `CatalogView.swift`** en el scaffold con `@Observable` (alinear scaffold con lecciones).
2. **Documentar** que las vistas son responsabilidad del estudiante y que el HostApp es solo smoke test.

---

## Hallazgo 3 — ALTO: Divergencia estructural sin puente explícito

| Aspecto | Lecciones (Etapa 1) | Scaffold |
|---|---|---|
| Tipo de proyecto | Xcode app single-target | SPM Package con 13 targets |
| Organización | Carpetas: `Features/Login/Domain/` | Targets: `FeatureLoginDomain/` |
| Imports | No necesarios (mismo target) | `import FeatureLoginDomain` explícito |
| Tests | `@testable import StackMyArchitecture` | `@testable import FeatureLoginDomain` |
| Visibility | `internal` (por defecto) | `public` (requerido entre targets) |

### Impacto para el estudiante
- Siguiendo la Etapa 1 literalmente, el estudiante crea un proyecto con carpetas.
- El scaffold ya es SPM modular.
- **No hay ninguna lección que explique la migración de carpetas a targets SPM.**
- El estudiante no sabe en qué punto debe hacer esa transición.

### Opciones
1. **Añadir una lección puente** (ej: `02-integracion/00b-migracion-spm.md`) que guíe la transición.
2. **Alinear Etapa 1** para que empiece directamente con SPM (más complejo para principiantes).
3. **Documentar** que el scaffold es la versión "evolucionada" y que la Etapa 1 es didáctica pura.

---

## Hallazgo 4 — ALTO: Divergencias de API Catalog no documentadas

La sección "Feature Catalog" de `equivalencias-scaffold.md` (líneas 78-87) está incompleta:

| Lecciones enseñan | Scaffold real | Documentado en equivalencias |
|---|---|---|
| `product.name: String` | `product.title: String` | ❌ NO |
| `Price(amount: Decimal, currency: String)` | `price: Double` | ❌ NO |
| `product.imageURL: URL` | No existe | ❌ NO |
| `ProductRepository.loadAll()` | `CatalogRepository.fetchCatalog()` | ❌ NO |
| `CatalogError.invalidData` | No existe (solo `.network`, `.offlineNoCache`, `.staleCacheUnavailable`) | ❌ NO |
| `CatalogGateway` | `CatalogRepository` | ✅ Sí |
| `LoadCatalogUseCase` | `LoadCatalogUseCase` | ❌ INCORRECTO (dice `FetchProductsUseCase`) |

### Impacto para el estudiante
Un estudiante que siga las lecciones del Catalog Domain creará `Product` con `name`, `Price` y `imageURL`. Al comparar con el scaffold, verá tipos completamente diferentes sin explicación de por qué.

---

## Hallazgo 5 — MEDIO: Gaps en la guía "dónde poner el código en Xcode"

### Etapa 1 (01-fundamentos) — ✅ BUENA
Las lecciones 04 a 06 dan instrucciones explícitas paso a paso:
- "Crea el archivo: `App/StackMyArchitectureApp.swift`"
- "Paso a paso en Xcode: 1. Click derecho en carpeta App/..."
- Tabla de errores comunes con soluciones

### Etapa 2 (02-integracion) — ⚠️ MIXTA
- Las lecciones del Catalog (`01-feature-catalog/`) incluyen rutas scaffold al inicio:
  > "Ruta scaffold relacionada: `apps/ios/ArchitectureKit/Sources/`"
- Pero los snippets dentro de las lecciones usan nombres pedagógicos y no indican archivo destino exacto.
- Algunas lecciones ya tienen "## Implementación en tu proyecto" (añadido por Claude Code) con divergencias documentadas.

### Etapa 3 (03-evolucion) — ⚠️ PARCIALMENTE CORREGIDA
- 6 de 7 lecciones procesadas por Claude Code con sección "Implementación" + divergencias.
- `07-backend-firebase.md` recién procesado.
- Los snippets de código dentro del cuerpo de las lecciones siguen usando API pedagógica (`product.name`, `Price`, `loadAll`).

### Etapas 4-5 — ❌ SIN PROCESAR
- 16 archivos aún tienen `<!-- semántica-flechas:auto -->` sin secciones de implementación.

---

## Hallazgo 6 — MEDIO: El HostApp funciona pero no se referencia en las lecciones

El `ArchitectureHostApp` es una app iOS completa y funcional:
- Login → Catalog flow con `InMemoryAuthRepository`
- SwiftData cache con `SwiftDataCatalogCacheStore`
- XCUITests con smoke test
- Credenciales por defecto: `student@course.dev` / `Passw0rd!`

Pero:
- **Ninguna lección de Etapa 1-3 menciona** que el estudiante puede ejecutar el HostApp para ver su trabajo.
- El HostApp usa `@StateObject`/`ObservableObject` mientras las lecciones enseñan `@Observable`.
- No hay instrucciones de cómo ejecutar el HostApp.

---

## Hallazgo 7 — INFO: Archivos InfraPersistence y InMemory sin uso en SessionStore

`InfraPersistence/` contiene:
- `SessionStore.swift` (protocolo con `save`, `load`, `clear`)
- Un segundo archivo (probablemente `InMemorySessionStore.swift`)

`AuthHTTPRepository` usa `SessionStore` para guardar la sesión tras login exitoso. Pero `InMemoryAuthRepository` (que es lo que usa el HostApp) NO usa `SessionStore` — simplemente devuelve un `UserSession` hardcodeado.

Esto significa que el flujo de persistencia de sesión solo funciona con `AuthHTTPRepository`, que requiere un servidor HTTP real que no se proporciona.

---

## Tabla resumen: Archivos del scaffold y qué lección los introduce

| Archivo scaffold | Lección que lo enseña | ¿Snippet copiable? | ¿Archivo destino claro? |
|---|---|---|---|
| `FeatureLoginDomain/EmailAddress.swift` | `01-fund/05-login/01-domain.md` | ✅ (como `Email`) | ✅ "Features/Login/Domain/Models/" |
| `FeatureLoginDomain/Password.swift` | `01-fund/05-login/01-domain.md` | ✅ | ✅ |
| `FeatureLoginDomain/Credentials.swift` | `01-fund/05-login/01-domain.md` | ✅ | ✅ |
| `FeatureLoginDomain/UserSession.swift` | `01-fund/05-login/01-domain.md` | ✅ (como `Session`) | ✅ |
| `FeatureLoginDomain/LoginError.swift` | `01-fund/05-login/01-domain.md` | ✅ (como `AuthError`) | ✅ |
| `FeatureLoginDomain/AuthRepository.swift` | `01-fund/05-login/02-application.md` | ✅ (como `AuthGateway`) | ✅ "Application/Ports/" |
| `FeatureLoginDomain/AuthenticateUserUseCase.swift` | `01-fund/05-login/02-application.md` | ✅ (como `LoginUseCase`) | ✅ |
| `FeatureLoginData/AuthHTTPRepository.swift` | `01-fund/05-login/03-infrastructure.md` | ✅ (como `RemoteAuthGateway`) | ✅ |
| `FeatureLoginData/InMemoryAuthRepository.swift` | `01-fund/05-login/03-infrastructure.md` | ✅ (como `StubAuthGateway`) | ✅ |
| `FeatureLoginUI/LoginViewModel.swift` | `01-fund/05-login/04-interface-swiftui.md` | ✅ | ✅ |
| **`FeatureLoginUI/LoginView.swift`** | `01-fund/05-login/04-interface-swiftui.md` | ✅ | ❌ **NO EXISTE EN SCAFFOLD** |
| `AppComposition/AppCompositionRoot.swift` | `01-fund/06-conectando-la-app.md` | ✅ (como `CompositionRoot`) | ✅ |
| `FeatureCatalogDomain/Product.swift` | `02-int/01-catalog/01-domain.md` | ⚠️ Diverge (name→title, Price→Double) | ⚠️ Ruta scaffold mencionada, no ruta Xcode |
| `FeatureCatalogDomain/CatalogRepository.swift` | `02-int/01-catalog/02-application.md` | ⚠️ Diverge (loadAll→fetchCatalog) | ⚠️ |
| `FeatureCatalogDomain/CatalogError.swift` | `02-int/01-catalog/01-domain.md` | ⚠️ Diverge (invalidData no existe) | ⚠️ |
| `FeatureCatalogDomain/LoadCatalogUseCase.swift` | `02-int/01-catalog/02-application.md` | ⚠️ | ⚠️ |
| `FeatureCatalogData/CachedCatalogRepository.swift` | `03-evo/01-caching-offline.md` | ⚠️ | ⚠️ |
| `FeatureCatalogData/CatalogDataContracts.swift` | Varias lecciones | ⚠️ No como archivo unificado | ❌ |
| `FeatureCatalogPersistenceSwiftData/` | `03-evo/06-swiftdata-store.md` | ⚠️ | ⚠️ |
| `AppContracts/NavigationContracts.swift` | `02-int/02-navegacion-eventos.md` | ⚠️ Diverge (AppDestination vs AppRoute) | ⚠️ |
| **`FeatureCatalogUI/CatalogView.swift`** | `02-int/01-catalog/04-interface-swiftui.md` | ✅ | ❌ **NO EXISTE EN SCAFFOLD** |

---

## Recomendaciones priorizadas

### P0 — Corregir errores factuales
1. **Actualizar `equivalencias-scaffold.md`** con los nombres reales del scaffold (AuthHTTPRepository, InMemoryAuthRepository, LoadCatalogUseCase).
2. **Completar la sección Catalog** con las divergencias de campos (name→title, Price→Double, imageURL no existe).

### P1 — Decisión arquitectónica: ¿crear vistas en el scaffold?
Decidir si:
- (A) Se crean `LoginView.swift` y `CatalogView.swift` en el scaffold usando `@Observable` — alineando con las lecciones.
- (B) Se documenta explícitamente que las vistas son ejercicio del estudiante.

### P2 — Puente estructura single-target → SPM
Añadir contenido que explique cuándo y cómo el proyecto pasa de carpetas Xcode a targets SPM. Posible ubicación: inicio de Etapa 2 o de Etapa 4.

### P3 — Completar el refactor de lecciones
Los 22 archivos restantes con `<!-- semántica-flechas:auto -->` necesitan:
- Lectura del diagrama step-by-step
- Sección "Implementación en tu proyecto" con divergencias
- Sección "Qué sigue"

### P4 — Alinear HostApp con patrones enseñados
El HostApp usa `@StateObject`/`ObservableObject`/`@Published` (legacy). Las lecciones enseñan `@Observable`/`@State`. Considerar migrar el HostApp o documentar la diferencia.

---

## Estado del scaffold — ¿Compila y es funcional?

| Verificación | Estado |
|---|---|
| `swift build` (ArchitectureKit) | ✅ Compila |
| `swift test` (ArchitectureKit) | ✅ Pasa (7 test targets) |
| HostApp compila | ✅ (requiere `xcodebuild`) |
| HostApp ejecuta Login→Catalog | ✅ Funcional |
| XCUITests smoke | ✅ Pasa |
| `check-dependencies.sh` | ✅ Pasa |

**El scaffold es funcional.** El problema no es que esté roto, sino que el camino desde las lecciones hasta el scaffold tiene gaps no documentados.
