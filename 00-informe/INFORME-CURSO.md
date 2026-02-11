# Informe del Curso: Stack My Architecture iOS

## 1) Objetivo final

El objetivo del curso no es memorizar patrones, sino ser capaz de diseñar, construir y evolucionar una base de código iOS de producción (enterprise) de forma:

- Modular: escalable por features y por equipo.
- Mantenible: cambio barato y refactors seguros.
- Testable: confianza con estrategia de pruebas disciplinada.
- Concurrencia-segura: Swift 6.2 strict concurrency, sin data races.
- Centrada en negocio: DDD con lenguaje ubicuo, invariantes, eventos y límites claros.

Al finalizar el curso, el alumno podrá:

- Definir y defender límites de módulos/features y sus reglas de dependencia.
- Diseñar flujos completos `UI -> Application -> Domain -> Infrastructure` con responsabilidades limpias.
- Integrar DDD + Clean Architecture + Feature-First sin contradicciones ni capas artificiales.
- Diseñar navegación por eventos desacoplada y testeable, incluyendo deep links.
- Escribir SwiftUI moderno con flujo de datos correcto, performance y APIs actuales.
- Trabajar con Swift Concurrency estricta (aislamiento, `Sendable`, cancelación, backpressure).
- Operar con BDD + TDD: primero especificación, después tests, luego producción y refactor.

## 2) Fundamentos de ingeniería del curso

El curso se apoya en una premisa central: antes de codificar, se aclara intención y objetivo. Esto facilita dividir trabajo, reducir retrabajo y mejorar comunicación, delegación y testabilidad.

### 2.1 Iteración y lotes pequeños

- Trabajo en historias/casos de uso pequeños.
- Menor riesgo por iteración.
- Feedback más rápido.
- Cadencia de entrega sostenida.

### 2.2 Test como mecanismo primario de feedback

- Base en pruebas unitarias/aisladas por coste y velocidad.
- Integración y E2E con moderación por coste creciente.
- Disciplina explícita de test-first (TDD real).

### 2.3 Modularidad: bajo acoplamiento y alta cohesión

- Objetivo: módulos poco acoplados entre sí y muy cohesivos por dentro.
- Señal de acoplamiento alto: cambiar A obliga a tocar B sin necesidad de negocio.

### 2.4 Composición y DI fuera del core

- La inyección, wiring y composición viven en el `Composition Root`.
- El core de dominio/aplicación no se contamina con detalles de ensamblado.

## 3) Metodologías: BDD + TDD

Regla operativa:

- BDD define el qué y el por qué en lenguaje de negocio.
- TDD define el cómo con seguridad y feedback continuo.

### 3.1 BDD en el curso

BDD se usa para:

- Capturar escenarios `happy path`, `sad path` y `edge cases`.
- Mantener lenguaje ubicuo (DDD).
- Convertir escenarios en criterios de aceptación trazables.
- Derivar casos de uso (Application) y reglas/invariantes (Domain).

### 3.2 TDD en el curso

Se aplica el ciclo clásico:

1. Red: test que falla.
2. Green: implementación mínima que pasa.
3. Refactor: mejora de diseño manteniendo tests en verde.

### 3.3 Flujo integrado BDD + TDD por feature

1. Especificación BDD.
2. Contratos de diseño (puertos, modelos, errores, eventos).
3. TDD desde el core hacia afuera:
   - Unit tests en Domain/Application como base.
   - Integración para infraestructura.
   - UI tests mínimos para aceptación crítica.

## 4) Stack tecnológico y criterios

### 4.1 SwiftUI moderno

- SwiftUI como UI principal.
- Estado y flujo de datos explícitos.
- Composición de vistas, navegación moderna y testing de presentación.

### 4.2 Swift 6.2 + Concurrencia estricta

- `async/await`, `Task`, `TaskGroup`, `AsyncSequence`.
- `actors`, aislamiento y uso justificado de `@MainActor`.
- `Sendable` en fronteras de concurrencia.
- Cancelación y backpressure.
- Interoperabilidad con APIs legacy.

### 4.3 Modularización Feature-First

- Organización vertical por feature, no por capa global.
- Cada feature como unidad de negocio evolucionable.
- Separación progresiva: empezar simple y extraer cuando aporte valor real.

### 4.4 Clean Architecture por feature

Capas y reglas de dependencia dentro de cada feature:

- Domain: reglas puras, invariantes, modelos, eventos.
- Application: casos de uso y puertos.
- Interface: SwiftUI y adaptadores de presentación.
- Infrastructure: red, persistencia y adaptadores concretos.

### 4.5 DDD

- Bounded contexts.
- Lenguaje ubicuo.
- Entidades, value objects, agregados e invariantes.
- Domain events y políticas.
- Consistencia por agregado.

### 4.6 Navegación por eventos

- Las features emiten intenciones/eventos.
- Un coordinador/sistema de navegación decide la ruta.
- Facilita deep links, trazabilidad y tests sin UI real.

### 4.7 Composition Root

- Módulo principal para DI, factories, wiring y adaptadores.
- Regla: composición fuera del core.

## 5) Progresión formativa: Junior -> Mid -> Senior -> Arquitecto -> Maestría

La progresión se diseñó para evitar saltos conceptuales. Primero se aprende a construir una feature completa con disciplina. Después se integra una segunda feature y se introduce concurrencia lo suficientemente pronto para sostener red/caché sin deuda técnica. Más tarde se trabaja resiliencia, y finalmente se escala a gobernanza y maestría.

### Etapa 1: Junior (fundamentos operables)

Meta:

- Entender límites, capas y flujo end-to-end en una feature pequeña.

Construcción:

- Estructura base Feature-First.
- Feature `Login` completa mínima:
  - escenarios BDD,
  - casos de uso,
  - dominio con invariantes/errores,
  - infraestructura mínima,
  - UI SwiftUI simple.

Entregables:

- Escenarios BDD con trazabilidad.
- Unit tests de casos de uso (TDD).
- Primer diagrama de dependencias.
- Primer ADR de Login.

Validación:

- Separación correcta de responsabilidades.
- Test-first real.
- Concurrencia segura en dobles de prueba cuando aplique.

### Etapa 2: Mid (integración y disciplina)

Meta:

- Integrar features manteniendo límites, contratos y pruebas.

Construcción:

- Segunda feature `Products/Catalog`.
- Navegación por eventos entre features.
- Infra real mínima (network) + contract tests de repositorio.
- Swift Concurrency aplicada en casos de uso y ViewModels (cancelación, aislamiento, `Sendable`).
- Primeros tests de integración entre 2+ componentes.

Entregables:

- Event bus/coordinador con tests.
- Contratos entre features (eventos/modelos/dependencias).
- Integration tests en infraestructura.
- Evidencia de criterios de concurrencia en wiring y coordinación.
- ADRs por feature.

### Etapa 3: Senior (evolución y resiliencia)

Meta:

- Tomar decisiones de arquitectura bajo cambio y escala con datos reales de operación.

Construcción:

- Caching/offline en `Products`.
- Estrategias de consistencia e invalidación.
- SwiftData como adaptador de infraestructura (no como centro del diseño).
- Observabilidad mínima (logging/tracing de eventos).
- Pruebas avanzadas:
  - snapshot (si aplica),
  - concurrencia (cancelación/backpressure),
  - integración rápida y confiable.

Entregables:

- Estrategia de cache con invariantes y tests.
- Observabilidad mínima usable para debugging.
- Documento de trade-offs y riesgos.

### Etapa 4: Arquitecto (plataforma y gobernanza)

Meta:

- Escalar sistema y equipo con estándares y enforcement.

Construcción:

- Bounded contexts y contratos entre contexts.
- Reglas de dependencia automatizadas (lint/CI conceptual).
- Guía de navegación por eventos y deep links como plataforma.
- Estrategia de versionado/paquetización (SPM, multi-target).
- Quality gates medibles por tipo de cambio.

Entregables:

- Guía de arquitectura del repositorio con convenciones y enforcement.
- ADRs macro de gobernanza.
- Quality gates conceptuales con criterios verificables:
  - tests,
  - cobertura crítica,
  - reglas de dependencia,
  - strict concurrency.

### Etapa 5: Maestría (concurrencia avanzada y composición)

Meta:

- Consolidar criterio de arquitecto senior para diseño concurrente, performance de UI y evolución segura a largo plazo.

Construcción:

- Isolation domains, `Sendable`, actores y structured concurrency.
- Testing concurrente no flaky.
- Estado moderno y performance en SwiftUI.
- Composición avanzada, diagnóstico y migración progresiva.

Entregables:

- Evidencia de arquitectura concurrente segura en casos reales.
- Pruebas concurrentes deterministas.
- Plan de migración/evolución con riesgos explícitos y mitigaciones.

## 6) Persistencia del material del curso

El curso se mantendrá como documento vivo y versionable:

- Markdown para estudio y control de cambios en Git.
- HTML para lectura cómoda, índice y navegación por lecciones.

Cada lección incluirá:

- Explicación paso a paso.
- Código completo (producción + tests).
- Diagramas en texto.
- ADRs y trade-offs.
- Checklist de smells y criterios de decisión (`cuándo sí/cuándo no`).

## 7) Qué no es este curso

- No es una chuleta de patrones.
- No es escribir producción y agregar tests al final.
- No es usar `@MainActor` para silenciar warnings sin justificar límites.
- No es adoptar modas; es construir un sistema coherente guiado por requisitos, tests y límites.
