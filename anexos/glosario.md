# Glosario

Términos clave del curso ordenados alfabéticamente.

---

| Término | Definición |
|---------|-----------|
| **ADR** | Architecture Decision Record: documento que captura una decisión de diseño, sus alternativas, y consecuencias |
| **Agregado** | Grupo de entidades/VOs con un root que protege invariantes de consistencia |
| **Anti-Corruption Layer (ACL)** | Capa de traducción entre dos bounded contexts para evitar contaminación de modelos |
| **Backpressure** | Mecanismo para que un consumidor controle el ritmo del productor en streams |
| **BDD** | Behavior-Driven Development: especificación de comportamiento con escenarios Gherkin (Given/When/Then) |
| **Bounded Context** | Límite semántico donde un término tiene un significado preciso y un equipo tiene ownership |
| **Cache-first** | Estrategia de caché que sirve datos locales primero y actualiza desde el servidor en background |
| **Clean Architecture** | Diseño con reglas de dependencia: las capas externas dependen de las internas, nunca al revés |
| **Composition Root** | Punto único donde se ensamblan todas las dependencias del sistema (factory methods, wiring) |
| **Context Map** | Diagrama que muestra los bounded contexts del sistema y las relaciones entre ellos |
| **Contract Test** | Test que verifica que una implementación cumple el contrato de su puerto/protocolo |
| **Cooperative Cancellation** | Modelo de cancelación de Swift donde el código debe verificar explícitamente si fue cancelado |
| **Decorador** | Patrón que envuelve un objeto para añadir comportamiento sin modificar el original (ej: `CachedProductRepository`) |
| **Deep Link** | URL que abre una pantalla específica de la app (ej: `myapp://catalog`) |
| **Domain Event** | Hecho relevante que ya ocurrió en el dominio (ej: `UserLoggedIn`) |
| **DDD** | Domain-Driven Design: modelado de software centrado en el dominio de negocio |
| **DTO** | Data Transfer Object: estructura que representa datos en tránsito (JSON, caché), separada del modelo de Domain |
| **Entidad** | Objeto con identidad propia que persiste en el tiempo |
| **Feature-First** | Organización del código por features (vertical) en vez de por capas (horizontal) |
| **Flaky Test** | Test que a veces pasa y a veces falla sin cambiar el código, erosionando la confianza en el suite |
| **Integration Test** | Test que verifica 2+ componentes reales colaborando, con stubs solo en los bordes (red, disco) |
| **Invariante** | Regla que siempre debe cumplirse en el dominio (ej: email con formato válido, precio no negativo) |
| **Lenguaje ubicuo** | Vocabulario compartido entre negocio y desarrollo, usado en código, tests, y conversaciones |
| **Network-first** | Estrategia de caché que intenta el servidor primero y usa caché solo como fallback |
| **@Observable** | Macro de Swift (iOS 17+) que hace un tipo observable por SwiftUI sin `@Published` |
| **Ownership** | Responsabilidad de un equipo sobre un bounded context: define modelos, contratos, y ADRs |
| **Puerto** | Protocolo que define una interfaz requerida por la capa Application, implementada por Infrastructure |
| **Quality Gate** | Condición automática que debe cumplirse antes de mergear un cambio (tests, lint, concurrency) |
| **Sendable** | Protocolo de Swift que garantiza paso seguro de datos entre fronteras de concurrencia |
| **Shared Kernel** | Tipos compartidos entre bounded contexts con ownership compartido (ej: `Session`) |
| **Small Batches** | Disciplina de trabajar en incrementos pequeños y completos para feedback rápido |
| **SPM** | Swift Package Manager: herramienta de Apple para gestionar dependencias y modularizar código |
| **Spy** | Test double que registra las llamadas que recibe para verificar interacciones (ej: `LoggerSpy`) |
| **Strict Concurrency** | Modo de Swift 6 que detecta data races en tiempo de compilación (`SWIFT_STRICT_CONCURRENCY=complete`) |
| **Stub** | Test double que devuelve respuestas predefinidas sin lógica real (ej: `ProductRepositoryStub`) |
| **SUT** | System Under Test: el componente que se está testeando en un test dado |
| **TDD** | Test-Driven Development: ciclo Red → Green → Refactor. Test primero, implementación después |
| **TTL** | Time-To-Live: tiempo máximo que un dato en caché se considera válido antes de expirar |
| **Unit Test** | Test que verifica un componente aislado, rápido, determinista, y sin dependencias externas |
| **Value Object** | Objeto sin identidad, definido por sus valores, inmutable (ej: `Price`, `Email`) |
| **Vertical Slicing** | Sinónimo de Feature-First: organización por features completas de arriba a abajo |
