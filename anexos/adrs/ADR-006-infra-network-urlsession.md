# ADR-006: Infraestructura real mínima con URLSessionHTTPClient

**Estado:** Aceptado  
**Fecha:** 2026-02-07  
**Contexto:** Etapa 2 - Integración / Lección: Infra real network

---

## Decisión

Introducir HTTPClient como puerto e implementar URLSessionHTTPClient en Infrastructure.

---

## Contexto

### El problema

Conectar con red real manteniendo límites de Clean Architecture.

### Las restricciones

- Mantener Clean Architecture (Domain sin dependencias de infraestructura)
- Facilitar testing con mocks/stubs
- Ser comprensible para un junior (sin magia de frameworks)
- Escalar a múltiples features sin caos

---

## Opciones consideradas

### Opción A: Usar Alamofire directamente en Application layer

- **Pros:** Simplicidad inicial, menos código
- **Contras:** Acoplamiento fuerte, difícil de testear, no escala

### Opción B: Crear wrapper propio complejo sobre URLSession

- **Pros:** [Beneficios de esta opción]
- **Contras:** [Desventajas significativas]

### Opción C: Infraestructura real mínima (elegida)

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

Ver la lección [04-infra-real-network](../../02-integracion/04-infra-real-network.md) para el código completo.

---

## Consecuencias

### Positivas

- Tests de contrato en infra, dominio limpio, reemplazo futuro sin tocar core
- Facilita testing unitario e integración
- Código más mantenible a largo plazo

### Negativas

- Más código inicial que usar Alamofire directo
- Requiere más archivos y estructura inicial

### Riesgos

- Tentación de exponer detalles HTTP en Domain; requiere mapeo de errores
- Requiere code reviews consistentes para mantener el patrón

---

## Referencias

- [Lección relacionada](../../02-integracion/04-infra-real-network.md)
- [Template ADR](./TEMPLATE-ADR.md)

---

<!-- plantilla-pedagogica:auto -->

## Refuerzo pedagogico
Contexto: normalizacion automatica para `anexos/adrs/ADR-006-infra-network-urlsession.md`.

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

**Anterior:** [ADR-005: Contratos entre features por eventos/modelos mín... ←](ADR-005-contratos-features.md) · **Siguiente:** [ADR-007: Estrategia de cache network-first + TTL + fallback →](ADR-007-cache-network-first-ttl.md)
