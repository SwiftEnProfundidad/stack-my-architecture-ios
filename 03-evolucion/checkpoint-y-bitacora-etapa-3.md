# Checkpoint y bitácora - Etapa 3: Evolución

Esta etapa valida que ya puedes hacer crecer el sistema con cache, consistencia, observabilidad y backend sin romper la base anterior.

## Qué debes poder hacer antes de avanzar

- Diseñar `network-first`, `cache-first` o TTL con criterio.
- Explicar una política de consistencia y sus riesgos.
- Añadir observabilidad útil a repositorios o flujos críticos.
- Integrar SwiftData o backend real detrás de puertos.
- Defender trade-offs de evolución sin caer en “porque sí”.

## Checklist de cierre

- [ ] Puedo justificar una política de frescura y su TTL.
- [ ] Entiendo por qué SwiftData debe quedar encapsulado en infraestructura.
- [ ] Sé qué logs o métricas mínimas necesito para diagnosticar un fallo.
- [ ] Puedo explicar cómo cambia el sistema al introducir Firebase o backend real sin romper capas internas.
- [ ] Distingo una mejora evolutiva real de un parche con deuda escondida.

## Mini-quiz de autoevaluación

1. ¿Qué problema resuelve inyectar el reloj en tests de consistencia?
2. ¿Cuándo usarías `network-first` y cuándo no?
3. ¿Por qué observabilidad no equivale a meter `print` por todos lados?
4. ¿Qué riesgo aparece si SwiftData se cuela en dominio?
5. ¿Qué trade-off aceptas cuando eliges Firebase como backend inicial?

## Bitácora guiada

### Lo que ya domino

Resume qué parte de la evolución del sistema ya ves con claridad.

### Lo que aún me cuesta

Escribe dónde aparecen más dudas: consistencia, cache, observabilidad o backend.

### Riesgo mejor entendido

Anota un riesgo que antes no veías y ahora sí sabes detectar.

### Próximo paso

Define qué criterio necesitas para pasar de evolucionar features a gobernar arquitectura.
