# Dependency governance y supply chain

## Modelo mental

Las dependencias son como proveedores externos de tu empresa: cada uno que añades te da capacidad, pero también te expone a su ritmo de cambio, sus bugs y su posible abandono. La gobernanza de dependencias es decidir conscientemente qué proveedores aceptas, bajo qué condiciones y con qué plan de salida.

## Ejemplo en el scaffold

En `ArchitectureKit`, el `Package.swift` define explícitamente qué targets pueden importar qué. `FeatureLoginDomain` solo depende de `CoreDomain`; nunca de `InfraHTTP` ni de `FeatureCatalogDomain`. El script `check-dependencies.sh` verifica estas reglas en cada build. Si alguien añade un `import InfraHTTP` dentro de `FeatureLoginDomain`, el gate falla. Consulta la Etapa 4 (`04-arquitecto/02-reglas-dependencia-ci.md`) para la estrategia completa.

## Cuándo sí / cuándo no

Aplica gobernanza de dependencias desde que tienes más de 3 módulos SPM o más de una dependencia externa. No la apliques a proyectos de un solo target donde el compilador ya controla todo.

## Reglas de dependencia modular

Define direcciones permitidas y prohibidas entre módulos. Las reglas deben ser ejecutables (lint/build checks) para evitar que la arquitectura dependa de disciplina manual.

## Política de upgrades

Establece cadencia de actualización (por ejemplo mensual/trimestral), criterios de priorización por riesgo y gates de validación (build, tests, perf, seguridad).

Cada upgrade relevante debe incluir plan de rollback.

## Supply chain basics

Usa lockfiles, verifica checksums cuando la herramienta lo permita y minimiza permisos/capacidades de dependencias.

Evita introducir SDKs sin justificar valor, riesgo y estrategia de salida.

## Dependency Governance Rules checklist

- [ ] Mapa de módulos y direcciones permitidas actualizado.
- [ ] Imports prohibidos definidos y chequeados.
- [ ] Política de versiones/upgrade publicada.
- [ ] Gates de upgrade definidos (test/perf/security).
- [ ] Plan de rollback por dependencia crítica.
- [ ] Inventario de dependencias con owner.
- [ ] Revisión periódica de dependencias huérfanas.

---


## Refuerzo pedagogico

### Objetivo
- Comprende el objetivo tecnico de esta leccion y que decision arquitectonica habilita.

### Prerrequisitos
- Revisa la leccion anterior del bloque y confirma que dominas sus conceptos clave.

### Practica guiada
- Aplica un cambio pequeno y verificable en el scaffold o en una plantilla operativa relacionada con esta leccion.

### Verificacion
- ¿Puedes identificar una dependencia crítica y su plan de rollback?
- ¿Puedes describir qué importaciones deben estar prohibidas por política de módulo?
- ¿Puedes explicar qué gate impediría un upgrade inseguro antes de mergear?

## Diagrama de arquitectura por capas

```mermaid
flowchart LR
  subgraph CORE["Core / Domain"]
    direction TB
    ENT[Entity]
    POL[Policy]
  end

  subgraph APP["Application"]
    direction TB
    BOOT[Composition Root]
    UC[UseCase]
    PORT["FeaturePort (contrato)"]
  end

  subgraph UI["Interface"]
    direction TB
    VM[ViewModel]
    VIEW[View]
  end

  subgraph INFRA["Infrastructure"]
    direction TB
    API[API Client]
    STORE[Persistence Adapter]
  end

  VM --> UC
  UC --> ENT
  UC -.o PORT
  BOOT -.-> PORT
  BOOT -.-> API
  BOOT -.-> STORE
  PORT --o API
  PORT --o STORE
  UC --o VM

  style CORE fill:#0f2338,stroke:#63a4ff,color:#dbeafe,stroke-width:2px
  style APP fill:#2a1f15,stroke:#fb923c,color:#ffedd5,stroke-width:2px
  style UI fill:#14262f,stroke:#93c5fd,color:#e0f2fe,stroke-width:2px
  style INFRA fill:#2a1d34,stroke:#c084fc,color:#f3e8ff,stroke-width:2px

  linkStyle 0 stroke:#f472b6,stroke-width:2.6px
  linkStyle 1 stroke:#f472b6,stroke-width:2.6px
  linkStyle 2 stroke:#60a5fa,stroke-width:2.8px
  linkStyle 3 stroke:#94a3b8,stroke-width:2px,stroke-dasharray:6 4
  linkStyle 4 stroke:#94a3b8,stroke-width:2px,stroke-dasharray:6 4
  linkStyle 5 stroke:#94a3b8,stroke-width:2px,stroke-dasharray:6 4
  linkStyle 6 stroke:#86efac,stroke-width:2.6px
  linkStyle 7 stroke:#86efac,stroke-width:2.6px
  linkStyle 8 stroke:#86efac,stroke-width:2.6px
```

La lectura del diagrama sigue esta semantica minima:
1. `-->` dependencia directa en runtime.
2. `-.->` wiring o configuracion.
3. `-.o` dependencia discontinua contra contrato/abstraccion.
4. `--o` salida o propagacion de resultado.
