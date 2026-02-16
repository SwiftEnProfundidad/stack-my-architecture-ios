# ADR-014: Quality gates conceptuales orientados a arquitectura

**Estado:** Aceptado  
**Fecha:** 2026-02-07  
**Contexto:** Etapa 4 - Arquitecto / Lección: Quality gates

---

## Decisión

Definir gates como marco conceptual y checkpoints de disciplina técnica.

---

## Contexto

### El problema

Esta edición prioriza aprendizaje de arquitectura sobre automatización completa de pipeline.

### Las restricciones

- Mantener Clean Architecture (Domain sin dependencias de infraestructura)
- Facilitar testing con mocks/stubs
- Ser comprensible para un junior (sin magia de frameworks)
- Escalar a múltiples features sin caos

---

## Opciones consideradas

### Opción A: Pipeline CI/CD completo con gates automáticos (complejo para el curso)

- **Pros:** Simplicidad inicial, menos código
- **Contras:** Acoplamiento fuerte, difícil de testear, no escala

### Opción B: Sin gates (sin estándares de calidad)

- **Pros:** [Beneficios de esta opción]
- **Contras:** [Desventajas significativas]

### Opción C: Quality gates conceptuales orientados a arquitectura (elegida)

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

Ver la lección [06-quality-gates](../04-arquitecto/06-quality-gates.md) para el código completo.

---

## Consecuencias

### Positivas

- El alumno interioriza criterios de calidad antes de industrializar CI en versión posterior
- Facilita testing unitario e integración
- Código más mantenible a largo plazo

### Negativas

- Menos 'guardarraíles' automáticos; depende más de code reviews manuales
- Requiere más archivos y estructura inicial

### Riesgos

- Alumno puede saltarse gates si no hay enforcement; requiere mentoring activo
- Requiere code reviews consistentes para mantener el patrón

---

## Referencias

- [Lección relacionada](../04-arquitecto/06-quality-gates.md)
- [Template ADR](./TEMPLATE-ADR.md)

---

**Anterior:** [ADR-013: Modularización/versionado SPM progresivos ←](ADR-013-versionado-spm-progresivo.md) · **Siguiente:** [ADR-NNN: [Título de la decisión] →](TEMPLATE-ADR.md)
