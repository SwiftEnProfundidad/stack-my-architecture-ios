# ADR-008: Política explícita de consistencia e invalidación

**Estado:** Aceptado  
**Fecha:** 2026-02-07  
**Contexto:** Etapa 3 - Evolución / Lección: Consistencia

---

## Decisión

Definir reglas de frescura/invalidación testeables y documentadas.

---

## Contexto

### El problema

Cache sin política produce comportamientos ambiguos y bugs difíciles.

### Las restricciones

- Mantener Clean Architecture (Domain sin dependencias de infraestructura)
- Facilitar testing con mocks/stubs
- Ser comprensible para un junior (sin magia de frameworks)
- Escalar a múltiples features sin caos

---

## Opciones consideradas

### Opción A: Invalidación manual por el desarrollador cuando cree conveniente

- **Pros:** Simplicidad inicial, menos código
- **Contras:** Acoplamiento fuerte, difícil de testear, no escala

### Opción B: Sin invalidación, siempre confiar en TTL

- **Pros:** [Beneficios de esta opción]
- **Contras:** [Desventajas significativas]

### Opción C: Política explícita de consistencia e invalidación (elegida)

- **Pros:** Balance entre simplicidad y arquitectura limpia, testeable, escalable
- **Contras:** Más boilerplate que las opciones naive, requiere disciplina

---

## Decisión detallada

Elegimos la **Opción C** porque:

1. **Respeta Clean Architecture**: Las capas internas (Domain/Application) permanecen puras
2. **Testabilidad**: Podemos inyectar mocks sin modificar código productivo
3. **Escalabilidad**: El patrón funciona tanto para 2 features como para 20
4. **Claridad pedagógica**: Un junior puede entender el flujo de datos

Descartamos las opciones A y B por los problemas de acoplamiento y complejidad que introducen.

### Implementación en el curso

Ver la lección [02-consistencia](../03-evolucion/02-consistencia.md) para el código completo.

---

## Consecuencias

### Positivas

- Decisiones previsibles, menor deuda operativa, debugging más rápido
- Facilita testing unitario e integración
- Código más mantenible a largo plazo

### Negativas

- Más código de gestión de estado; complejidad adicional
- Requiere más archivos y estructura inicial

### Riesgos

- Política demasiado agresiva puede invalidar innecesariamente; muy laxa puede servir datos obsoletos
- Requiere code reviews consistentes para mantener el patrón

---

## Referencias

- [Lección relacionada](../03-evolucion/02-consistencia.md)
- [Template ADR](./TEMPLATE-ADR.md)

---

**Anterior:** [ADR-007: Estrategia de cache network-first + TTL + fallback ←](ADR-007-cache-network-first-ttl.md) · **Siguiente:** [ADR-009: Observabilidad por decoradores y logger de aplic... →](ADR-009-observabilidad-por-decoradores.md)
