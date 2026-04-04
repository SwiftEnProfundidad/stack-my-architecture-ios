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

- **Pros:**
  - Las reglas de dependencia son verificadas por el compilador de Swift desde el primer commit; una importación incorrecta entre módulos produce un error de compilación, no una violación detectada más tarde
  - El grafo de dependencias queda explicitado en el `Package.swift`, lo que facilita auditorías y onboarding de nuevos desarrolladores
- **Contras:**
  - Crear y mantener 5-10 módulos SPM desde el inicio supone un overhead significativo de configuración (targets, productos, dependencias en `Package.swift`) antes de haber escrito una sola línea de lógica de negocio
  - Los tiempos de compilación incremental aumentan al tener múltiples módulos; Xcode necesita reconstruir módulos afectados en cascada, ralentizando el ciclo de feedback durante el aprendizaje
  - Mover código entre módulos una vez que las reglas están fijadas es costoso: requiere actualizar imports, resolver accesibilidad (`public`/`internal`) y ajustar el `Package.swift`; el coste de error es alto si los límites iniciales estaban mal definidos

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

