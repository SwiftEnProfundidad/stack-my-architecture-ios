# ADR-005: Contratos entre features por eventos/modelos mínimos

**Estado:** Aceptado  
**Fecha:** 2026-02-07  
**Contexto:** Etapa 2 - Integración / Lección: Contratos entre features

---

## Decisión

Compartir solo contratos públicos mínimos (eventos/tipos), nunca clases internas.

---

## Contexto

### El problema

Integración entre Login y Catalog sin invadir internals de cada uno.

### Las restricciones

- Mantener Clean Architecture (Domain sin dependencias de infraestructura)
- Facilitar testing con mocks/stubs
- Ser comprensible para un junior (sin magia de frameworks)
- Escalar a múltiples features sin caos

---

## Opciones consideradas

### Opción A: Shared Kernel grande con todo compartido

- **Pros:** Simplicidad inicial, menos código
- **Contras:** Acoplamiento fuerte, difícil de testear, no escala

### Opción B: Import directo de implementaciones entre features

- **Pros:** [Beneficios de esta opción]
- **Contras:** [Desventajas significativas]

### Opción C: Contratos entre features por eventos/modelos mínimos (elegida)

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

Ver la lección [03-contratos-features](../../02-integracion/03-contratos-features.md) para el código completo.

---

## Consecuencias

### Positivas

- Evolución segura por feature, menor riesgo de cascada de cambios
- Facilita testing unitario e integración
- Código más mantenible a largo plazo

### Negativas

- Más archivos de contratos que mantener
- Requiere más archivos y estructura inicial

### Riesgos

- Tentación de compartir demasiado; requiere disciplina en code reviews
- Requiere code reviews consistentes para mantener el patrón

---

## Referencias

- [Lección relacionada](../../02-integracion/03-contratos-features.md)
- [Template ADR](./TEMPLATE-ADR.md)

---

<!-- plantilla-pedagogica:auto -->

## Refuerzo pedagogico
Contexto: normalizacion automatica para `anexos/adrs/ADR-005-contratos-features.md`.

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

