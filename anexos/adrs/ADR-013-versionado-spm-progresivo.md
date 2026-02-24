# ADR-013: Modularización/versionado SPM progresivos

**Estado:** Aceptado  
**Fecha:** 2026-02-07  
**Contexto:** Etapa 4 - Arquitecto / Lección: Versionado SPM

---

## Decisión

Mantener inicio simple y escalar SPM por señales medibles de dolor.

---

## Contexto

### El problema

Sobremodularizar temprano penaliza productividad.

### Las restricciones

- Mantener Clean Architecture (Domain sin dependencias de infraestructura)
- Facilitar testing con mocks/stubs
- Ser comprensible para un junior (sin magia de frameworks)
- Escalar a múltiples features sin caos

---

## Opciones consideradas

### Opción A: Un solo módulo monolítico (simple pero no escala)

- **Pros:** Simplicidad inicial, menos código
- **Contras:** Acoplamiento fuerte, difícil de testear, no escala

### Opción B: 10+ módulos desde el inicio (overhead de gestión)

- **Pros:** [Beneficios de esta opción]
- **Contras:** [Desventajas significativas]

### Opción C: Modularización/versionado SPM progresivos (elegida)

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

Ver la lección [04-versionado-spm](../../04-arquitecto/04-versionado-spm.md) para el código completo.

---

## Consecuencias

### Positivas

- Mejor balance entre entrega rápida y gobernanza arquitectónica
- Facilita testing unitario e integración
- Código más mantenible a largo plazo

### Negativas

- Deuda técnica de refactorización cuando se decide modularizar
- Requiere más archivos y estructura inicial

### Riesgos

- Postergar demasiado la modularización puede hacerla muy costosa; requiere monitoreo de métricas
- Requiere code reviews consistentes para mantener el patrón

---

## Referencias

- [Lección relacionada](../../04-arquitecto/04-versionado-spm.md)
- [Template ADR](./TEMPLATE-ADR.md)

---

<!-- plantilla-pedagogica:auto -->

## Refuerzo pedagogico
Contexto: normalizacion automatica para `anexos/adrs/ADR-013-versionado-spm-progresivo.md`.

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

**Anterior:** [ADR-012: Reglas de dependencia progresivas ←](ADR-012-reglas-dependencia-progresivas.md) · **Siguiente:** [ADR-014: Quality gates conceptuales orientados a arquitec... →](ADR-014-quality-gates-conceptuales.md)
