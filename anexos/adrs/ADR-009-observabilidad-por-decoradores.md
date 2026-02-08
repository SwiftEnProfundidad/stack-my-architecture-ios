## ADR-009: Observabilidad por decoradores y logger de aplicación
- Estado: Aprobado
- Contexto: Incidentes sin trazas útiles frenan diagnóstico de flujos async.
- Decisión: Añadir logging/tracing en infraestructura mediante decoradores y puerto de logger.
- Consecuencias: Mejor diagnóstico sin contaminar Domain/Application con SDKs concretos.
- Fecha: 2026-02-07
