# ADR-012: Reglas de dependencia progresivas

**Estado:** Aceptado  
**Fecha:** 2026-02-07  
**Contexto:** Etapa 4 - Arquitecto / Lección: Reglas dependencia CI

---

## Decisión

Aplicar enforcement progresivo: convención documentada -> scripts -> modularización estricta.

---

## Contexto

### El problema

Las reglas arquitectónicas solo en texto no evitan regresiones.

### Las restricciones

- Mantener Clean Architecture (Domain sin dependencias de infraestructura)
- Facilitar testing con mocks/stubs
- Ser comprensible para un junior (sin magia de frameworks)
- Escalar a múltiples features sin caos

---

## Opciones consideradas

### Opción A: Solo documentación (ignorada fácilmente)

- **Pros:** Simplicidad inicial, menos código
- **Contras:** Acoplamiento fuerte, difícil de testear, no escala

### Opción B: Modularización estricta desde día 1 (lento, fricción para el alumno)

- **Pros:** [Beneficios de esta opción]
- **Contras:** [Desventajas significativas]

### Opción C: Reglas de dependencia progresivas (elegida)

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

Ver la lección [02-reglas-dependencia-ci](../../04-arquitecto/02-reglas-dependencia-ci.md) para el código completo.

---

## Consecuencias

### Positivas

- Control sostenible sin sobrerregular etapas tempranas
- Facilita testing unitario e integración
- Código más mantenible a largo plazo

### Negativas

- Período intermedio donde las reglas son 'suaves' y pueden romperse
- Requiere más archivos y estructura inicial

### Riesgos

- Transición mal gestionada puede dejar reglas sin enforcement; requiere disciplina del equipo
- Requiere code reviews consistentes para mantener el patrón

---

## Referencias

- [Lección relacionada](../../04-arquitecto/02-reglas-dependencia-ci.md)
- [Template ADR](./TEMPLATE-ADR.md)

---

<!-- plantilla-pedagogica:auto -->

## Refuerzo pedagogico
Contexto: normalizacion automatica para `anexos/adrs/ADR-012-reglas-dependencia-progresivas.md`.

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

**Anterior:** [ADR-011: Bounded contexts con ownership y contratos ←](ADR-011-bounded-contexts-governance.md) · **Siguiente:** [ADR-013: Modularización/versionado SPM progresivos →](ADR-013-versionado-spm-progresivo.md)
