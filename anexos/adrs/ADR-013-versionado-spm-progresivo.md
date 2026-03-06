# ADR-013: Modularización/versionado SPM progresivos

**Estado:** Aceptado  
**Fecha:** 2026-02-07  
**Contexto:** Etapa 4 - Arquitecto / Lección: Versionado SPM

---

## Decisión

Mantener inicio simple y escalar SPM por señales medibles de dolor.

---

## Contexto

### El problema

Sobremodularizar temprano penaliza productividad.

### Las restricciones

- Mantener Clean Architecture (Domain sin dependencias de infraestructura)
- Facilitar testing con mocks/stubs
- Ser comprensible para un junior (sin magia de frameworks)
- Escalar a múltiples features sin caos

---

## Opciones consideradas

### Opción A: Un solo módulo monolítico (simple pero no escala)

- **Pros:** Simplicidad inicial, menos código
- **Contras:** Acoplamiento fuerte, difícil de testear, no escala

### Opción B: 10+ módulos desde el inicio (overhead de gestión)

- **Pros:**
  - Los límites de compilación entre módulos son forzados por Swift desde el principio: no es posible que un módulo de Domain importe uno de Infrastructure sin que el `Package.swift` lo declare explícitamente
  - Tiempos de compilación paralelos en CI mejoran desde el inicio; cada módulo se puede cachear y reconstruir de forma independiente con herramientas como `xcodebuild` o Tuist
- **Contras:**
  - El `Package.swift` con 10+ targets y sus dependencias cruzadas se convierte en una fuente de conflictos de merge frecuentes y errores de configuración difíciles de depurar para un alumno que aún está aprendiendo la arquitectura
  - El modificador de acceso `public` debe aplicarse a todo símbolo que cruce fronteras de módulo; el alumno dedica tiempo a ajustar visibilidades en lugar de centrarse en la lógica de dominio y los patrones arquitectónicos
  - Si los límites del módulo se definen mal al inicio (por ejemplo, agrupando por tipo técnico en lugar de por dominio), refactorizarlos más adelante es muy costoso: implica mover ficheros, actualizar imports en decenas de sitios y reconfigurar el `Package.swift`

### Opción C: Modularización/versionado SPM progresivos (elegida)

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

Ver la lección [04-versionado-spm](../../04-arquitecto/04-versionado-spm.md) para el código completo.

---

## Consecuencias

### Positivas

- Mejor balance entre entrega rápida y gobernanza arquitectónica
- Facilita testing unitario e integración
- Código más mantenible a largo plazo

### Negativas

- Deuda técnica de refactorización cuando se decide modularizar
- Requiere más archivos y estructura inicial

### Riesgos

- Postergar demasiado la modularización puede hacerla muy costosa; requiere monitoreo de métricas
- Requiere code reviews consistentes para mantener el patrón

---

## Referencias

- [Lección relacionada](../../04-arquitecto/04-versionado-spm.md)
- [Template ADR](./TEMPLATE-ADR.md)

---

<!-- plantilla-pedagógica:auto -->

## Refuerzo pedagógico
Contexto: normalización automática para `anexos/adrs/ADR-013-versionado-spm-progresivo.md`.

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
