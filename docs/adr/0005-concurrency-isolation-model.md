# ADR-0005: Modelo de aislamiento de concurrencia

- Fecha: 2026-02-11
- Estado: Aprobado

## Contexto

Swift 6 exige seguridad de concurrencia explícita en fronteras de aislamiento.

## Decisión

- UI/ViewModels y navegación en `@MainActor`.
- Estado mutable compartido en `actor` (`InMemorySessionStore`, `InMemoryCatalogCacheStore`, `InMemoryConnectivityChecker`).
- contratos cross-layer `Sendable`.

## Consecuencias

- Positivo: menor riesgo de data races.
- Negativo: más disciplina en diseño de tipos y pruebas.

## Evidencia

- `FeatureLoginUI/LoginViewModel.swift`
- `AppComposition/NavigationStore.swift`
- `InfraPersistence/InMemorySessionStore.swift`
- `FeatureCatalogData/InMemoryCatalogStores.swift`

