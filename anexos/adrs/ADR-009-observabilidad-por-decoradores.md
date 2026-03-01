# ADR-009: Observabilidad por decoradores y logger de aplicación

**Estado:** Aceptado  
**Fecha:** 2026-02-07  
**Contexto:** Etapa 3 - Evolución / Lección: Observabilidad

---

## Decisión

Añadir logging/tracing en infraestructura mediante decoradores y puerto de logger.

---

## Contexto

### El problema

Incidentes sin trazas útiles frenan diagnóstico de flujos async.

### Las restricciones

- Mantener Clean Architecture (Domain sin dependencias de infraestructura)
- Facilitar testing con mocks/stubs
- Ser comprensible para un junior (sin magia de frameworks)
- Escalar a múltiples features sin caos

---

## Opciones consideradas

### Opción A: Loggear directamente con print/os_log desde cualquier lugar

- **Pros:** Simplicidad inicial, menos código
- **Contras:** Acoplamiento fuerte, difícil de testear, no escala

### Opción B: Usar SDK completo de terceros (Firebase, Datadog) en todo el código

- **Pros:** [Beneficios de esta opción]
- **Contras:** [Desventajas significativas]

### Opción C: Observabilidad por decoradores y logger de aplicación (elegida)

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

Ver la lección [03-observabilidad](../../03-evolucion/03-observabilidad.md) para el código completo.

---

## Consecuencias

### Positivas

- Mejor diagnóstico sin contaminar Domain/Application con SDKs concretos
- Facilita testing unitario e integración
- Código más mantenible a largo plazo

### Negativas

- Overhead de los decoradores; más código boilerplate
- Requiere más archivos y estructura inicial

### Riesgos

- Logging excesivo puede impactar performance; logging insuficiente no ayuda en debugging
- Requiere code reviews consistentes para mantener el patrón

---

## Referencias

- [Lección relacionada](../../03-evolucion/03-observabilidad.md)
- [Template ADR](./TEMPLATE-ADR.md)

---

<!-- plantilla-pedagogica:auto -->

## Refuerzo pedagogico
Contexto: normalizacion automatica para `anexos/adrs/ADR-009-observabilidad-por-decoradores.md`.

### Objetivo
- Define el resultado concreto esperado al finalizar esta leccion.

### Prerrequisitos
- Revisa la leccion anterior inmediata y confirma los conceptos base antes de continuar.

### Validacion
- Checklist rapido:
  - [ ] Entiendo la decision tecnica principal de la leccion.
  - [ ] He ejecutado una comprobacion minima (test/build/script) asociada.
  - [ ] Puedo explicar el trade-off clave con mis palabras.

