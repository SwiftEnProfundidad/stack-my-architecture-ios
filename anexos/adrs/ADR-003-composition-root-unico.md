## ADR-003: Composition Root único para ensamblaje
- Estado: Aprobado
- Contexto: El sistema crece por features y necesita wiring claro sin contaminar el core.
- Decisión: Centralizar creación de dependencias en un único Composition Root (factories + wiring).
- Consecuencias: Cambios de infraestructura se localizan; UseCases/ViewModels no crean dependencias concretas.
- Fecha: 2026-02-07
