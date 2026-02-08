## ADR-004: Navegación event-driven desacoplada
- Estado: Aprobado
- Contexto: Navegación directa entre vistas aumenta acoplamiento entre features.
- Decisión: Las features emiten eventos/intenciones; el coordinador decide rutas.
- Consecuencias: Deep links testeables, trazabilidad y menor dependencia cruzada.
- Fecha: 2026-02-07
