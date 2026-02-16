# ADR-0004: SwiftData aislado detrás de adaptadores

- Fecha: 2026-02-11
- Estado: Aprobado

## Contexto

SwiftData es infraestructura y no debe contaminar Domain/Application/UI.

## Decisión

Mantener contratos de persistencia (`SessionStore`, `CatalogCacheStore`) y encapsular implementación SwiftData en un adaptador de infraestructura.

## Consecuencias

- Positivo: reemplazo de tecnología de persistencia sin tocar use cases ni view models.
- Negativo: coste inicial de mapeo DTO/Entity.

## Implementación

Adaptador implementado en `Sources/FeatureCatalogPersistenceSwiftData/SwiftDataCatalogCacheStore.swift`, verificado con 3 tests en `Tests/FeatureCatalogPersistenceSwiftDataTests/`.
