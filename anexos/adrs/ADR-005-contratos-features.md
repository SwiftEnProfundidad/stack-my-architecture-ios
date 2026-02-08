## ADR-005: Contratos entre features por eventos/modelos mínimos
- Estado: Aprobado
- Contexto: Integración entre Login y Catalog sin invadir internals.
- Decisión: Compartir solo contratos públicos mínimos (eventos/tipos), nunca clases internas.
- Consecuencias: Evolución segura por feature y menor riesgo de cascada de cambios.
- Fecha: 2026-02-07
