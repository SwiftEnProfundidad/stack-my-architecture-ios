# ADR-010: Firebase como backend principal encapsulado

**Estado:** Aceptado  
**Fecha:** 2026-02-07  
**Contexto:** Etapa 3 - Evolución / Lección: Backend Firebase

---

## Decisión

Adoptar Firebase Auth + Firestore encapsulados en Infrastructure.

---

## Contexto

### El problema

Curso requiere backend gratuito, integrable y didáctico para Auth + datos.

### Las restricciones

- Mantener Clean Architecture (Domain sin dependencias de infraestructura)
- Facilitar testing con mocks/stubs
- Ser comprensible para un junior (sin magia de frameworks)
- Escalar a múltiples features sin caos

---

## Opciones consideradas

### Opción A: Crear backend propio (requiere servidor, más complejo para el curso)

- **Pros:** Simplicidad inicial, menos código
- **Contras:** Acoplamiento fuerte, difícil de testear, no escala

### Opción B: Usar mock estático sin backend real (no demuestra integración real)

- **Pros:**
  - Cero dependencias externas; todos los datos viven en el código fuente y los tests son totalmente deterministas
  - El alumno puede trabajar sin conexión a internet y sin configurar ningún servicio en la nube
- **Contras:**
  - No enseña a integrar un backend real ni a gestionar errores de red auténticos (timeouts, problemas de autenticación, permisos de Firestore); el aprendizaje queda incompleto
  - Los datos mock no reflejan la asincronía real de una llamada remota, ocultando problemas de estado de carga, paginación y manejo de streams que el alumno encontrará en proyectos reales
  - Cuando el alumno pase a un proyecto con backend real, tendrá que reaprender la integración desde cero; el mock no transfiere conocimiento práctico

### Opción C: Firebase como backend principal encapsulado (elegida)

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

Ver la lección [07-backend-firebase](../../03-evolucion/07-backend-firebase.md) para el código completo.

---

## Consecuencias

### Positivas

- Arranque rápido del alumno, separación limpia de capas, tests de integración guiados
- Facilita testing unitario e integración
- Código más mantenible a largo plazo

### Negativas

- Vendor lock-in a Firebase; dependencia de servicio externo
- Requiere más archivos y estructura inicial

### Riesgos

- Cambios en APIs de Firebase pueden romper ejemplos; requiere mantenimiento de versiones
- Requiere code reviews consistentes para mantener el patrón

---

## Referencias

- [Lección relacionada](../../03-evolucion/07-backend-firebase.md)
- [Template ADR](./TEMPLATE-ADR.md)

---

<!-- plantilla-pedagógica:auto -->

## Refuerzo pedagógico
Contexto: normalización automática para `anexos/adrs/ADR-010-firebase-backend-principal.md`.

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
