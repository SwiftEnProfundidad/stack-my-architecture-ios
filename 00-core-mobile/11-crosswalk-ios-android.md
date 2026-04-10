# Crosswalk iOS ↔ Android

## Modelo mental

Este crosswalk mapea dos cosas: (1) la equivalencia de niveles de responsabilidad entre los tracks iOS y Android del programa, y (2) los conceptos técnicos equivalentes entre plataformas. Un alumno iOS que domina "integrate" puede dialogar con un compañero Android en el mismo nivel porque resuelven el mismo problema con herramientas distintas. Este documento les da el vocabulario común.

## Equivalencia de tracks por responsabilidad

Los niveles del track Android son los del programa Stack My Architecture Android. La equivalencia es por responsabilidad demostrable, no por nombre de carpeta.

| Responsabilidad | Entregable que la demuestra | iOS (este curso) | Android |
|---|---|---|---|
| **build** | Feature completa con tests y contratos de capa | Etapa 1: Fundamentos | Nivel 0 |
| **integrate** | Features conectadas sin acoplamiento directo | Etapa 2: Integración | Junior |
| **operate** | Sistema observable, con rollback y feature flags | Etapa 3: Evolución | Mid |
| **govern** | ADRs, quality gates ejecutables, gestión de deuda | Etapa 4: Arquitecto | Senior |
| **optimize under constraints** | Decisiones de rendimiento con evidencia medible | Etapa 5: Maestría | Maestría |

Cada nivel implica que el anterior está consolidado. No se puede "govern" sin saber "integrate".

## Crosswalk técnico: conceptos equivalentes iOS ↔ Android

| Responsabilidad | iOS | Android |
|---|---|---|
| Navegación desacoplada | `Coordinator` + eventos de intención | `NavController` + `NavigationComponent` |
| Contrato de feature | `protocol FeaturePort` | `interface` en módulo de dominio |
| Lógica de negocio | `UseCase` (struct/actor) | `UseCase` (clase en dominio) |
| Estado reactivo | `Combine` / `AsyncStream` | `StateFlow` / `SharedFlow` (Coroutines) |
| Inyección de dependencias | Composition Root manual | `Hilt` / Composition Root manual |
| Módulos y límites | `SPM targets` en `Package.swift` | `Gradle modules` |
| Reglas de dependencia ejecutables | Swift Package Manager access control | `Forbidden dependency rules` en Gradle |
| Persistencia local | `CoreData` / `SwiftData` | `Room` |
| Concurrencia segura | `async/await` + `Actor` (Swift 6) | `Coroutines` + `suspend` + `Mutex` |
| Observabilidad | `os_log` / `os_signpost` | `Timber` / `Logcat` estructurado |

---

## Qué sigue

La siguiente lección, [Paridad de Mobile Architect iOS ↔ Android](12-mobile-architect-parity-ios-android.md), define qué significa exactamente tener profundidad en iOS con paridad arquitectónica en Android, con criterios concretos para evaluación, contratación y coordinación de equipos.
