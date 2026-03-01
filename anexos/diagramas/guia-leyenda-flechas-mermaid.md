# Guía rápida: leyenda de flechas Mermaid

Referencia mínima para mantener semántica consistente en los diagramas del curso.

```mermaid
flowchart LR
    VIEW[SwiftUI View] --> VM[ViewModel]
    VM -.-> ROOT[Composition Root]
    VM ==> PORT[Protocol / Port]
    VM --o OUT[Telemetry / Output]
```

## Convención

- `-->` Dependencia directa (runtime).
- `-.->` Wiring / configuración.
- `==>` Contrato / abstracción.
- `--o` Salida / propagación.
