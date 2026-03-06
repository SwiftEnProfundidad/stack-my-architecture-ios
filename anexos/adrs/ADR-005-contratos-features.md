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

- **Pros:**
  - Acceso inmediato a todos los métodos y datos de la feature importada sin definir contratos
  - Menos archivos intermedios; el código entre features se conecta directamente
- **Contras:**
  - Crea dependencias circulares: si Login importa Catalog y Catalog importa Login, el compilador falla
  - Un cambio interno en una feature (renombrar un método, cambiar un tipo) rompe todas las features que la importan
  - Imposible compilar o testear una feature de forma aislada; el grafo de dependencias se convierte en un monolito oculto

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

Ver la lección [03-contratos-features](../../02-integración/03-contratos-features.md) para el código completo.

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

- [Lección relacionada](../../02-integración/03-contratos-features.md)
- [Template ADR](./TEMPLATE-ADR.md)

---

<!-- plantilla-pedagógica:auto -->

## Refuerzo pedagógico
Contexto: normalización automática para `anexos/adrs/ADR-005-contratos-features.md`.

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
