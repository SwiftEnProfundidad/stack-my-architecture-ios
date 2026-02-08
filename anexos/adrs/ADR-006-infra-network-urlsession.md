## ADR-006: Infraestructura real mínima con URLSessionHTTPClient
- Estado: Aprobado
- Contexto: Se requiere conectar con red real manteniendo límites de Clean Architecture.
- Decisión: Introducir `HTTPClient` como puerto e implementar `URLSessionHTTPClient` en Infrastructure.
- Consecuencias: Tests de contrato en infra, dominio limpio y reemplazo futuro de transporte sin tocar core.
- Fecha: 2026-02-07
