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

- **Pros:**
  - Fricción de contribución mínima: el alumno puede hacer merge de cualquier cambio sin esperar a que pase ninguna verificación, lo que acelera la iteración durante el aprendizaje inicial
  - Sin configuración adicional de CI ni de scripts de validación; el proyecto arranca con cero overhead de herramientas
- **Contras:**
  - Sin ningún gate, las violaciones de arquitectura (un import de UIKit en Domain, un ciclo de dependencias) se acumulan silenciosamente y son muy costosas de revertir cuando se detectan tarde
  - El alumno no desarrolla el hábito de validar sus cambios antes de integrar; al llegar a un equipo real con CI estricto, el cambio de cultura es brusco y genera frustración
  - No hay señal objetiva de que el código cumple los principios enseñados; el aprendizaje queda solo en la teoría sin ningún mecanismo de verificación, aunque sea manual

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

Ver la lección [06-quality-gates](../../04-arquitecto/06-quality-gates.md) para el código completo.

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

- [Lección relacionada](../../04-arquitecto/06-quality-gates.md)
- [Template ADR](./TEMPLATE-ADR.md)

---

<!-- plantilla-pedagógica:auto -->

## Refuerzo pedagógico
Contexto: normalización automática para `anexos/adrs/ADR-014-quality-gates-conceptuales.md`.

### Objetivo
- Define el resultado concreto esperado al finalizar esta lección.

### Prerrequisitos
- Revisa la lección anterior inmediata y confirma los conceptos base antes de continuar.

### Práctica guiada
- Aplica un cambio pequeño y verificable en el scaffold relacionado con esta lección.

### Validación
- Checklist rápido:
  - [ ] Entiendo la decisión técnica principal de la lección.
  - [ ] He ejecutado una comprobación mínima (test/build/script) asociada.
  - [ ] Puedo explicar el trade-off clave con mis palabras.
