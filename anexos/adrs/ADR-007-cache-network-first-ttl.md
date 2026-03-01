# ADR-007: Estrategia de cache network-first + TTL + fallback

**Estado:** Aceptado  
**Fecha:** 2026-02-07  
**Contexto:** Etapa 3 - Evolución / Lección: Caching offline

---

## Decisión

Intentar remoto primero; usar cache solo ante fallo y si TTL válido.

---

## Contexto

### El problema

Mejorar resiliencia sin mentir con datos obsoletos.

### Las restricciones

- Mantener Clean Architecture (Domain sin dependencias de infraestructura)
- Facilitar testing con mocks/stubs
- Ser comprensible para un junior (sin magia de frameworks)
- Escalar a múltiples features sin caos

---

## Opciones consideradas

### Opción A: Cache-first (rápido pero posiblemente obsoleto)

- **Pros:** Simplicidad inicial, menos código
- **Contras:** Acoplamiento fuerte, difícil de testear, no escala

### Opción B: Siempre remoto (fresco pero lento y frágil)

- **Pros:** [Beneficios de esta opción]
- **Contras:** [Desventajas significativas]

### Opción C: Estrategia de cache network-first + TTL + fallback (elegida)

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

Ver la lección [01-caching-offline](../../03-evolucion/01-caching-offline.md) para el código completo.

---

## Consecuencias

### Positivas

- UX robusta en mala red, control explícito de frescura
- Facilita testing unitario e integración
- Código más mantenible a largo plazo

### Negativas

- Primera carga siempre requiere red; implementación más compleja
- Requiere más archivos y estructura inicial

### Riesgos

- TTL mal configurado puede servir datos muy viejos; requiere tuning
- Requiere code reviews consistentes para mantener el patrón

---

## Referencias

- [Lección relacionada](../../03-evolucion/01-caching-offline.md)
- [Template ADR](./TEMPLATE-ADR.md)

---

<!-- plantilla-pedagogica:auto -->

## Refuerzo pedagogico
Contexto: normalizacion automatica para `anexos/adrs/ADR-007-cache-network-first-ttl.md`.

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

