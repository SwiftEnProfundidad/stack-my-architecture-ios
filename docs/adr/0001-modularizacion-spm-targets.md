# ADR-0001: Modularización con un Package SPM multi-target

- Fecha: 2026-02-11
- Estado: Aprobado

## Contexto

El curso trabaja con dos features (`Login`, `Catalog`) y foco en arquitectura aplicable, no en complejidad de release management entre múltiples repos/packages.

## Decisión

Usar un único `Package.swift` con múltiples targets (`CoreDomain`, `Infra*`, `Feature*`, `AppComposition`).

## Consecuencias

- Positivo: menor fricción didáctica, grafo claro de dependencias, ejecución simple con `swift test`.
- Negativo: aislamiento de release menos estricto que multi-package.

## Revisión

Revisar al crecer a más de 4 features reales o al necesitar versionado independiente por equipo.

