# ADR-0002: Navegación desacoplada por contrato

- Fecha: 2026-02-11
- Estado: Aprobado

## Contexto

Queremos que `Login` no conozca implementación de rutas ni vistas de otras features. En una app con múltiples features, si Login importa CatalogView directamente, cualquier cambio en Catalog rompe Login. Necesitamos un mecanismo que permita navegar sin acoplar features entre sí.

## Alternativas consideradas

1. **NavigationLink directo entre features** — Simple pero acopla Login a Catalog. Descartado por violación de bounded contexts.
2. **Coordinator pattern clásico (UIKit)** — Probado en UIKit pero no idiomático en SwiftUI con NavigationStack. Descartado por fricción con el modelo declarativo.
3. **Protocolo de navegación + closures (elegida)** — Cada feature emite intenciones (closures), el Composition Root las conecta al coordinador. Idiomático, testeable, desacoplado.

## Decisión

Definir protocolo `LoginNavigating` en `AppContracts` y resolverlo en `AppComposition` mediante closures de navegación conectadas a `NavigationStore`/`AppCoordinator`. Cada feature recibe un closure `onSuccess`/`onEvent` en su ViewModel; el Composition Root decide qué ruta empujar.

## Consecuencias

- Positivo: navegación testeable por unidad, features desacopladas, compatible con deep links futuros.
- Positivo: cada feature se puede desarrollar y testear en aislamiento.
- Negativo: añade un contrato extra (closure o protocolo) por flujo de navegación.
- Negativo: el Composition Root crece con cada nueva ruta (mitigado con factory methods por feature).

## Evidencia

- `Sources/AppContracts/NavigationContracts.swift`
- `Sources/AppComposition/AppCompositionRoot.swift`
- `Tests/AppCompositionTests/AppCompositionRootTests.swift` — `test_loginFlow_wiresNavigation_fromLoginToCatalog`

