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

- **Pros:**
  - Los datos mostrados al usuario son siempre los más recientes; no hay riesgo de mostrar información obsoleta
  - Implementación trivial: no se necesita ninguna capa de almacenamiento local ni lógica de TTL
- **Contras:**
  - Sin conectividad (vuelo, túnel, red inestable) la app muestra errores en lugar de datos útiles; la experiencia offline es inexistente
  - Cada acción del usuario genera una petición de red; en condiciones de latencia alta el tiempo de respuesta percibido empeora notablemente
  - No hay resiliencia ante caídas del servidor: un error transitorio del backend se convierte inmediatamente en error visible para el usuario

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

