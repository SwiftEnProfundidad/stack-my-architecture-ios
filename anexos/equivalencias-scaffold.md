# Equivalencias: nombres pedagógicos ↔ scaffold real

Las lecciones del curso usan **nombres pedagógicos** elegidos por su claridad didáctica.
El scaffold real (`apps/ios/ArchitectureKit/`) usa nombres ligeramente distintos para reflejar
convenciones de un proyecto enterprise real.

Esta tabla es la referencia canónica. Cuando una lección diga `LoginUseCase`, busca
`AuthenticateUserUseCase` en el scaffold.

---

## Tabla de equivalencias — Feature Login

| Nombre en lecciones | Nombre en scaffold | Ruta en scaffold |
|---|---|---|
| `Email` | `EmailAddress` | `Sources/FeatureLoginDomain/EmailAddress.swift` |
| `Password` | `Password` | `Sources/FeatureLoginDomain/Password.swift` |
| `Credentials` | `Credentials` | `Sources/FeatureLoginDomain/Credentials.swift` |
| `Session` | `UserSession` | `Sources/FeatureLoginDomain/UserSession.swift` |
| `AuthError` | `LoginError` | `Sources/FeatureLoginDomain/LoginError.swift` |
| `Email.ValidationError.invalidFormat` | `LoginError.invalidEmail` | `Sources/FeatureLoginDomain/LoginError.swift` |
| `Password.ValidationError.empty` | `LoginError.invalidPassword` | `Sources/FeatureLoginDomain/LoginError.swift` |
| `AuthGateway` (protocol/puerto) | `AuthRepository` | `Sources/FeatureLoginDomain/AuthRepository.swift` |
| `LoginUseCase` | `AuthenticateUserUseCase` | `Sources/FeatureLoginDomain/AuthenticateUserUseCase.swift` |
| `RemoteAuthGateway` | `AuthHTTPRepository` | `Sources/FeatureLoginData/AuthHTTPRepository.swift` |
| `StubAuthGateway` | `InMemoryAuthRepository` | `Sources/FeatureLoginData/InMemoryAuthRepository.swift` |
| `LoginViewModel` | `LoginViewModel` | `Sources/FeatureLoginUI/LoginViewModel.swift` |
| `LoginView` | `LoginView` | `Sources/FeatureLoginUI/LoginView.swift` |
| `@testable import StackMyArchitecture` | `@testable import FeatureLoginDomain` | en cada test |

---

## Diferencias estructurales

| Aspecto | Lecciones | Scaffold |
|---|---|---|
| Capas | Domain / Application / Infrastructure / Interface | Domain / Data / UI |
| Protocolo `AuthGateway` vive en | `Application/Ports/` | `FeatureLoginDomain/` (dentro del módulo Domain) |
| Errores de validación | Cada VO tiene su propio `ValidationError` anidado | Enum unificado `LoginError` en el módulo Domain |
| Modularización | Carpetas dentro de un único target Xcode | 13 targets SPM independientes |
| Import en Domain | Domain no importa Foundation (regla didáctica pura) | `EmailAddress` y `Password` importan Foundation para `trimmingCharacters` |

---

## Por qué existen estas diferencias

**Los nombres pedagógicos** (`AuthGateway`, `LoginUseCase`, `Email`) son más cortos y directos,
facilitando la comprensión cuando se aprende el patrón por primera vez.

**Los nombres del scaffold** (`AuthRepository`, `AuthenticateUserUseCase`, `EmailAddress`) siguen
convenciones enterprise habituales en proyectos iOS reales:
- `AuthRepository` es la nomenclatura estándar en proyectos Clean Architecture iOS.
- `AuthenticateUserUseCase` es más explícito sobre la acción que realiza.
- `EmailAddress` evita colisión de nombres con otros contextos que puedan tener un tipo `Email`.
- `LoginError` unificado reduce la proliferación de tipos de error por cada Value Object.

**El patrón es idéntico en ambos casos.** Solo cambia la nomenclatura y algunas decisiones
de convención que serían naturales al evolucionar el código pedagógico hacia producción.

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
