# ETAPA 6: Proyecto Final iOS — Delivery Enterprise End-to-End

## Ruta scaffold relacionada

- `apps/ios/ArchitectureKit/Sources/`
- `apps/ios/ArchitectureKit/Tests/`
- `apps/ios/ArchitectureHostApp/`

## Objetivo

Cerrar el curso con un proyecto defendible de nivel profesional: no solo una app que funcione, sino una solución que puedas explicar, operar, evolucionar y justificar en entrevista técnica.

En esta etapa debes demostrar que integras de forma coherente todo lo aprendido en Core Mobile, Junior, Midlevel, Senior, Arquitecto y Maestría.

## Reto obligatorio

Implementa la iniciativa **Commerce+** sobre la base del proyecto del curso:

1. Extiende la app actual (`Login + Catalog`) con una nueva capacidad de negocio real.
2. Mantén límites arquitectónicos claros (Domain, Application, Interface, Infrastructure).
3. Entrega evidencia técnica y operativa, no solo pantallas.

### Funcionalidad mínima exigida

Debes implementar **2 features nuevas** (mínimo una de flujo principal y una de soporte):

1. Flujo principal (elige una):
- `Checkout + Order Confirmation`
- `Favorites + Saved Lists`
- `Profile + Session Management`

2. Flujo de soporte (elige una):
- `Search + Filter avanzado`
- `Offline cache para catálogo`
- `Observabilidad de flujos críticos`

## Arquitectura objetivo del proyecto final

```mermaid
flowchart LR
  subgraph APP["App / Composition"]
    CR["CompositionRoot"]
    COORD["AppCoordinator"]
  end

  subgraph FEATURE["Features (Catalog, Checkout, Profile)"]
    VM["FeatureViewModel"]
    UC["UseCase"]
    PORT["Port / Contract"]
  end

  subgraph INFRA["Infrastructure"]
    API["Remote Adapter"]
    CACHE["Local Store"]
  end

  CR -.-> COORD
  CR -.-> API
  VM --> UC
  UC -.o PORT
  API --o PORT
  API --> CACHE
```

Lectura de flechas aplicada:

1. `-->` dependencia directa en runtime.
2. `-.->` wiring/configuración en composition root.
3. `-.o` dependencia contra contrato.
4. `--o` salida desde implementación concreta.

## Alcance técnico obligatorio

### 1) Calidad y testing

- TDD por comportamiento crítico (`Red -> Green -> Refactor`).
- Suite mínima:
  - tests de dominio de reglas de negocio,
  - tests de aplicación (casos de uso),
  - tests de infraestructura (mapeo/errores),
  - al menos 1 test de integración entre capas.

### 2) Concurrencia segura

- Tipos de dominio cruzando fronteras async: `Sendable`.
- ViewModels de UI en `@MainActor`.
- Cancelación explícita en tareas largas o reintentos.

### 3) Operación y observabilidad

- Logs estructurados en flujos críticos.
- Señales de error accionables.
- Runbook corto para incidente principal.

### 4) Release y mitigación

- Estrategia de rollout (flag o activación progresiva).
- Plan de rollback concreto y ejecutable.

### 5) Seguridad y privacidad

- Sin PII en logs.
- Tokens/sesión gestionados con criterio seguro.
- Amenazas y mitigaciones principales documentadas.

## Plan de ejecución recomendado (7 hitos)

1. Definir escenarios BDD y alcance.
2. Diseñar contratos y límites de dependencias.
3. Implementar dominio y casos de uso con TDD.
4. Integrar infraestructura y manejo de errores.
5. Conectar interfaz y navegación.
6. Añadir observabilidad, release y seguridad.
7. Preparar defensa técnica con evidencia.

## Definición de Done de la etapa

La etapa está cerrada cuando:

1. La app cumple el alcance funcional mínimo.
2. El pipeline técnico está en verde.
3. Existe evidencia verificable de arquitectura, testing, operación y seguridad.
4. Puedes defender decisiones y trade-offs sin apoyarte en explicaciones ambiguas.

## Entregables de esta etapa

Consulta y completa la rúbrica de entrega:

- [Lección 2: Rúbrica y entrega del Proyecto Final](./01-rubrica-y-entrega.md)
- [Lección 3: Guía paso a paso — 7 hitos con código y verificación](./02-guia-paso-a-paso.md)

Y usa como soporte:

- [`05-maestria/rubrica-final/01-rubrica-empleabilidad-ios.md`](../05-maestria/rubrica-final/01-rubrica-empleabilidad-ios.md)
- [`05-maestria/rubrica-final/02-evidencias-obligatorias-ios.md`](../05-maestria/rubrica-final/02-evidencias-obligatorias-ios.md)
- [`05-maestria/rubrica-final/03-checklist-entrega-para-entrevista.md`](../05-maestria/rubrica-final/03-checklist-entrega-para-entrevista.md)

## 🔨 Checkpoint Xcode — Verifica el punto de partida del proyecto final

```bash
# El scaffold completo debe estar en verde antes de empezar
cd apps/ios/ArchitectureKit && swift test

# Revisa el estado de todos los módulos
swift package show-dependencies

# Gate de dependencias: confirma que no hay violaciones
grep -rn "^import SwiftUI\|^import UIKit" Sources/FeatureLoginDomain Sources/FeatureCatalogDomain 2>/dev/null || echo "✅ Domain puro"
```

**Criterios de partida para el proyecto final:**
- `swift test` termina con todos los tests en verde
- No hay violaciones de dependencias en Domain
- Tienes Xcode abierto con el Package.swift del scaffold
