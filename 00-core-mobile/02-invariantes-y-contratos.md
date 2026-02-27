# Invariantes y contratos

## Modelo mental

Un invariante es un muro de carga en un edificio: si lo quitas, todo se derrumba. Un contrato es la puerta entre habitaciones: define qué puede pasar y qué no, sin que cada habitación necesite conocer el interior de la otra.

```mermaid
flowchart TD
    INV["Invariante: Email válido"] --> VO["Value Object Email"]
    VO --> DOM["Domain lo exige"]
    DOM --> APP["Application lo propaga"]
    APP --> INFRA["Infrastructure lo respeta"]
    INFRA --> TEST["Tests lo verifican"]
```

## Invariantes (must-never-happen)

Un invariante es una verdad del sistema que no debe romperse nunca. No es documentación bonita; es una condición de seguridad de negocio o de integridad técnica.

Ejemplos: un token expirado nunca se usa para llamar API, una orden pagada no vuelve a estado pendiente, un evento crítico no se pierde silenciosamente.

Codifica invariantes en tres capas: modelo de dominio, contratos de entrada/salida y pruebas. Si el invariante solo vive en una wiki, no existe.

## Ejemplo en el scaffold

En `ArchitectureKit`, el Value Object `Email` (en `FeatureLoginDomain`) es un invariante codificado: solo se puede construir si contiene `@`. Esto garantiza que ninguna capa posterior (Application, Infrastructure, UI) reciba un email malformado. El test `EmailTests.test_invalidEmail_throwsError` verifica esta invariante. Consulta la Etapa 1 (`01-fundamentos/05-feature-login/01-domain.md`) para ver la implementación TDD completa.

## Cuándo sí / cuándo no

Codifica como invariante todo lo que, si se viola, produce daño de negocio o corrupción de datos. No conviertas en invariante preferencias de estilo o reglas que cambian con frecuencia (esas son políticas configurables, no muros de carga).

## Contratos clave

Contrato de dominio define límites entre agregados y reglas de negocio.

Contrato de feature define qué expone cada módulo y qué no puede importar.

Contrato API define request/response, errores esperables, idempotencia y versionado.

Contrato de test define qué comportamiento es obligatorio proteger ante regresión.

## Contract tests vs integration tests vs E2E

Los contract tests validan que productor y consumidor cumplen un acuerdo explícito, con bajo coste y alta señal de ruptura de contrato.

Los integration tests verifican colaboración real entre componentes internos y detectan errores de wiring, mapping o persistencia.

Los E2E validan recorrido completo y experiencia de usuario; son más caros y deben reservarse para flujos críticos de negocio.

Guía pragmática: protege reglas con unit/contract, wiring con integration y valor de negocio crítico con E2E.

---

<!-- plantilla-pedagogica:auto -->

## Refuerzo pedagogico
Contexto: normalizacion automatica para `00-core-mobile/02-invariantes-y-contratos.md`.

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

**Anterior:** [Marco de decisiones arquitectónicas ←](01-marco-de-decisiones.md) · **Siguiente:** [Variabilidad y evolución sin caos →](03-variabilidad-y-evolucion.md)

<!-- semantica-flechas:auto -->
## Semantica de flechas aplicada a esta arquitectura

```mermaid
flowchart LR
    subgraph APP["App / Composition module"]
        CR["CompositionRoot"]
        COORD["AppCoordinator"]
    end

    subgraph FEATURE["Feature module"]
        VM["FeatureViewModel"]
        UC["UseCase"]
        PORT["Repository protocol"]
    end

    subgraph INFRA["Infrastructure module"]
        ADAPTER["RemoteRepository adapter"]
        STORE["LocalStore"]
    end

    CR -.-> COORD
    CR -.-> ADAPTER
    VM --> UC
    UC -.o PORT
    ADAPTER --o PORT
    ADAPTER --> STORE
```text

Lectura semantica minima de este diagrama:

1. `-->` dependencia directa en runtime.
2. `-.->` wiring y configuracion de ensamblado.
3. `-.o` dependencia contra contrato/abstraccion.
4. `--o` salida/propagacion desde implementacion concreta.

