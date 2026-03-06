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

- **Pros:**
  - Dashboard de observabilidad listo para usar con alertas, métricas y trazas distribuidas sin escribir infraestructura propia
  - Integración con servicios de crash reporting (Crashlytics) y performance monitoring (Firebase Performance) en un solo SDK ya conocido por el alumno
- **Contras:**
  - El SDK se importa directamente en capas de Domain o Application, lo que introduce una dependencia concreta en el núcleo del sistema; imposible cambiar de proveedor sin tocar múltiples capas
  - En tests unitarios el SDK intenta conectarse a servicios externos o requiere configuración de `GoogleService-Info.plist`; los tests se vuelven lentos, frágiles y dependientes de la red
  - El vendor lock-in es total: logs, trazas y métricas quedan atados al formato y retención del proveedor; migrar a otra plataforma implica reescribir cada punto de observabilidad

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

<!-- plantilla-pedagógica:auto -->

## Refuerzo pedagógico
Contexto: normalización automática para `anexos/adrs/ADR-009-observabilidad-por-decoradores.md`.

### Objetivo
- Define el resultado concreto esperado al finalizar esta lección.

### Prerrequisitos
- Revisa la lección anterior inmediata y confirma los conceptos base antes de continuar.

### Validación
- Checklist rápido:
  - [ ] Entiendo la decisión técnica principal de la lección.
  - [ ] He ejecutado una comprobación mínima (test/build/script) asociada.
  - [ ] Puedo explicar el trade-off clave con mis palabras.
