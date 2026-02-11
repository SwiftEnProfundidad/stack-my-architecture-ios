# ADR-0002: Navegación desacoplada por contrato

- Fecha: 2026-02-11
- Estado: Aprobado

## Contexto

Queremos que `Login` no conozca implementación de rutas ni vistas de otras features.

## Decisión

Definir protocolo `LoginNavigating` en `AppContracts` y resolverlo en `AppComposition` mediante `NavigationStore`.

## Consecuencias

- Positivo: navegación testeable por unidad, features desacopladas.
- Negativo: añade un contrato extra por flujo.

## Evidencia

- `AppContracts/NavigationContracts.swift`
- `AppCompositionTests/AppCompositionRootTests.swift`

