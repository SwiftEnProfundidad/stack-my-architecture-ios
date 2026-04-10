# Equivalencias: nombres pedagógicos ↔ scaffold real

> **Estado (Fase 1 completada):** Los nombres de Feature Login ya están unificados entre lecciones y scaffold. Esta tabla documenta las **diferencias que persisten** (principalmente arquitectura de errores y nombres de Feature Catalog/navegación).

---

## Feature Login — Diferencias restantes

La mayoría de nombres de Feature Login coinciden ahora con el scaffold. Las únicas divergencias son:

| Aspecto | Lecciones | Scaffold | Motivo |
|---|---|---|---|
| Arquitectura de errores de VO | `EmailAddress.ValidationError.invalidFormat`, `Password.ValidationError.empty` | `LoginError.invalidEmail`, `LoginError.invalidPassword` | Pedagógico: la lección enseña errores anidados primero; el scaffold usa enum unificado desde el inicio |
| Case de error de red | `LoginError.connectivity` | `LoginError.network` | Pedagógico: nombre más descriptivo en la lección |
| Import en tests | `@testable import StackMyArchitecture` | `@testable import FeatureLoginDomain/Data/UI` | Modularización: la lección usa un único target Xcode |

### Nombres ya unificados ✅

`EmailAddress`, `Password`, `Credentials`, `UserSession`, `LoginError`, `AuthRepository`, `AuthenticateUserUseCase`, `AuthHTTPRepository`, `InMemoryAuthRepository`, `LoginViewModel`, `LoginView`, `LoginNavigating`

---

## Diferencias estructurales (independiente de nombres)

| Aspecto | Lecciones | Scaffold |
|---|---|---|
| Capas | Domain / Application / Infrastructure / Interface | Domain / Data / UI |
| Protocolo `AuthRepository` vive en | `Application/Ports/` | `FeatureLoginDomain/` (dentro del módulo Domain) |
| Errores de VO | Cada VO tiene su propio `ValidationError` anidado | Enum unificado `LoginError` en el módulo Domain |
| Modularización | Carpetas dentro de un único target Xcode | 13 targets SPM independientes |
| Import en Domain | Domain no importa Foundation (regla didáctica pura) | `EmailAddress` y `Password` importan Foundation para `trimmingCharacters` |

---

## Por qué persisten estas diferencias

Las diferencias restantes son **intencionales por razones pedagógicas**:

- La lección enseña `ValidationError` anidado en los VOs para mostrar cómo un VO puede ser autónomo y auto-validante. El scaffold lo simplifica con un `LoginError` unificado para mostrar el resultado final enterprise. Ambos patrones son correctos — la lección muestra el camino, el scaffold muestra el destino.
- `LoginError.connectivity` vs `.network`: diferencia de naming sin impacto arquitectónico.
- La modularización en targets SPM es la arquitectura real, pero añade complejidad irrelevante en la fase de aprendizaje del patrón.

**El patrón arquitectónico es idéntico en ambos casos.** Solo cambia la nomenclatura y algunas decisiones de convención que serían naturales al evolucionar el código pedagógico hacia producción.

---

## Mapa de importación en tests

Cuando las lecciones dicen:
```swift
@testable import StackMyArchitecture
```

En el scaffold es:
```swift
@testable import FeatureLoginDomain  // para tests de Domain y casos de uso
@testable import FeatureLoginData    // para tests de Infrastructure
@testable import FeatureLoginUI      // para tests de Interface
```

---

## Feature Catalog

| Nombre en lecciones | Nombre en scaffold | Ruta en scaffold |
|---|---|---|
| `Product(id:name:price:imageURL:)` | `Product(id:title:price:)` | `Sources/FeatureCatalogDomain/Product.swift` |
| `product.name` | `product.title` | campo renombrado |
| `Price(amount: Decimal, currency: String)` | `price: Double` — sin tipo `Price` | `Product.price` directamente |
| `product.imageURL: URL` | no existe en scaffold | — |
| `CatalogError.invalidData` | no existe — solo `.network`, `.offlineNoCache`, `.staleCacheUnavailable` | `Sources/FeatureCatalogDomain/CatalogError.swift` |
| `CatalogGateway` (protocol/puerto) | `CatalogRepository` | `Sources/FeatureCatalogDomain/CatalogRepository.swift` |
| `ProductRepository.loadAll()` | `CatalogRepository.fetchCatalog()` | `Sources/FeatureCatalogDomain/CatalogRepository.swift` |
| `LoadCatalogUseCase` | `LoadCatalogUseCase` | `Sources/FeatureCatalogDomain/LoadCatalogUseCase.swift` |
| `CatalogViewModel` | `CatalogViewModel` (`@Observable`) | `Sources/FeatureCatalogUI/CatalogViewModel.swift` |
| `CatalogView` | `CatalogView` | `Sources/FeatureCatalogUI/CatalogView.swift` |
| `RemoteCatalogGateway` | `CachedCatalogRepository` | `Sources/FeatureCatalogData/CachedCatalogRepository.swift` |

---

## Navegación y Composition Root

| Nombre en lecciones | Nombre en scaffold | Ruta en scaffold |
|---|---|---|
| `AppDestination` | `AppRoute` | `Sources/AppContracts/NavigationContracts.swift` |
| `CompositionRoot` | `AppCompositionRoot` | `Sources/AppComposition/AppCompositionRoot.swift` |
| `NavigationCoordinator` | `NavigationStore` | `Sources/AppComposition/NavigationStore.swift` |
| `LoginNavigating` (protocol) | `LoginNavigating` | `Sources/AppContracts/NavigationContracts.swift` |

---

## Patrones SwiftUI — Lecciones vs Scaffold

| Aspecto | Lecciones | Scaffold |
|---|---|---|
| Observación | `@Observable` (macro moderna) | `@Observable` (macro moderna) |
| Binding en vistas | `@Bindable var viewModel` | `@Bindable var viewModel` |
| ViewModel es | `@Observable @MainActor class` | `@Observable @MainActor public final class` |
| Vista recibe VM por | init parameter | init parameter |
