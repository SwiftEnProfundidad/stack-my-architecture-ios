# ADR-011: Bounded contexts con ownership y contratos

**Estado:** Aceptado  
**Fecha:** 2026-02-07  
**Contexto:** Etapa 4 - Arquitecto / Lección: Bounded contexts

---

## Decisión

Definir contextos (Identity, Catalog, etc.) con ownership, contratos y reglas de cambio.

---

## Contexto

### El problema

Escalado por equipos necesita límites semánticos explícitos.

### Las restricciones

- Mantener Clean Architecture (Domain sin dependencias de infraestructura)
- Facilitar testing con mocks/stubs
- Ser comprensible para un junior (sin magia de frameworks)
- Escalar a múltiples features sin caos

---

## Opciones consideradas

### Opción A: Monolito sin límites claros (rápido al inicio, caos al crecer)

- **Pros:** Simplicidad inicial, menos código
- **Contras:** Acoplamiento fuerte, difícil de testear, no escala

### Opción B: Microservicios desde día 1 (overkill para el curso, complejidad innecesaria)

- **Pros:** [Beneficios de esta opción]
- **Contras:** [Desventajas significativas]

### Opción C: Bounded contexts (elegida)

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

Ver la lección [01-bounded-contexts](../../04-arquitecto/01-bounded-contexts.md) para el código completo.

---

## Consecuencias

### Positivas

- Menos fricción entre equipos, menor acoplamiento accidental
- Facilita testing unitario e integración
- Código más mantenible a largo plazo

### Negativas

- Overhead de definir y mantener contratos entre contextos
- Requiere más archivos y estructura inicial

### Riesgos

- Bounded contexts mal definidos pueden crear más fricción; requiere experiencia en DDD
- Requiere code reviews consistentes para mantener el patrón

---

## Referencias

- [Lección relacionada](../../04-arquitecto/01-bounded-contexts.md)
- [Template ADR](./TEMPLATE-ADR.md)

---

<!-- plantilla-pedagogica:auto -->

## Refuerzo pedagogico
Contexto: normalizacion automatica para `anexos/adrs/ADR-011-bounded-contexts-governance.md`.

### Objetivo
- Define el resultado concreto esperado al finalizar esta leccion.

### Prerrequisitos
- Revisa la leccion anterior inmediata y confirma los conceptos base antes de continuar.

### Practica guiada
- Aplica un cambio pequeno y verificable en el scaffold relacionado con esta leccion.

### Validacion
- Checklist rapido:
  - [ ] Entiendo la decision tecnica principal de la leccion.
  - [ ] He ejecutado una comprobacion minima (test/build/script) asociada.
  - [ ] Puedo explicar el trade-off clave con mis palabras.

**Anterior:** [ADR-010: Firebase como backend principal encapsulado ←](ADR-010-firebase-backend-principal.md) · **Siguiente:** [ADR-012: Reglas de dependencia progresivas →](ADR-012-reglas-dependencia-progresivas.md)
