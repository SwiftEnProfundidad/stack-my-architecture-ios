## ADR-007: Estrategia de cache `network-first` + TTL + fallback
- Estado: Aprobado
- Contexto: Mejorar resiliencia sin mentir con datos obsoletos.
- Decisión: Intentar remoto primero; usar cache solo ante fallo y si TTL válido.
- Consecuencias: UX robusta en mala red y control explícito de frescura.
- Fecha: 2026-02-07
