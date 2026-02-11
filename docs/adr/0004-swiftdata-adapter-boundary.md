# ADR-0004: SwiftData aislado detrás de adaptadores

- Fecha: 2026-02-11
- Estado: Propuesto

## Contexto

SwiftData es infraestructura y no debe contaminar Domain/Application/UI.

## Decisión

Mantener contratos de persistencia (`SessionStore`, `CatalogCacheStore`) y encapsular implementación SwiftData en un adaptador de infraestructura.

## Consecuencias

- Positivo: reemplazo de tecnología de persistencia sin tocar use cases ni view models.
- Negativo: coste inicial de mapeo DTO/Entity.

## Acción pendiente

Implementar adaptador SwiftData para `CatalogCacheStore` en Etapa 3 avanzada.

