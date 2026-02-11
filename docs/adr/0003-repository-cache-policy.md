# ADR-0003: Política de datos en Catalog (`remote-first + fallback cache + TTL`)

- Fecha: 2026-02-11
- Estado: Aprobado

## Contexto

`Catalog` debe funcionar con conectividad intermitente sin degradar consistencia silenciosamente.

## Decisión

Implementar `CachedCatalogRepository` con:
- remoto primero cuando hay red;
- fallback a cache si remoto falla y cache válida;
- en offline, devolver cache válida; si no, error explícito.

## Consecuencias

- Positivo: resiliencia sin ocultar estado de frescura.
- Negativo: mayor complejidad de pruebas de integración.

## Evidencia

- `FeatureCatalogData/CachedCatalogRepository.swift`
- `FeatureCatalogDataIntegrationTests/CachedCatalogRepositoryIntegrationTests.swift`

