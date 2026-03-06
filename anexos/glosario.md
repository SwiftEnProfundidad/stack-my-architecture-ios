# Glosario iOS

Términos clave del curso ordenados alfabéticamente. Úsalo como mapa rápido cuando una lección introduzca un concepto nuevo y quieras volver a su primera aparición.

---

| Término | Definición | Primera aparición |
|---------|-----------|-------------------|
| **ACL (Anti-Corruption Layer)** | Capa de traducción entre bounded contexts para que un modelo externo no contamine tu modelo interno. | `04-arquitecto/01-bounded-contexts.md` |
| **Actor** | Tipo de Swift que protege estado mutable y serializa el acceso concurrente para evitar data races. | `05-maestria/02-actors-en-arquitectura.md` |
| **ADR** | Architecture Decision Record: documento breve que captura una decisión, alternativas y consecuencias. | `01-fundamentos/01-principios-ingenieria.md` |
| **Agregado** | Grupo de entidades y value objects gobernado por una raíz que protege invariantes de consistencia. | `00-core-mobile/02-invariantes-y-contratos.md` |
| **Aislamiento por actor** | Regla de Swift Concurrency que limita desde dónde se puede leer o mutar un estado protegido por un actor. | `05-maestria/01-isolation-domains.md` |
| **AppCoordinator** | Coordinador principal que decide navegación y composición entre features sin acoplar vistas entre sí. | `02-integracion/02-navegacion-eventos.md` |
| **@Bindable** | Property wrapper que permite crear bindings a propiedades de un objeto `@Observable` inyectado. | `02-integracion/07-swiftui-enterprise.md` |
| **Backpressure** | Mecanismo para que el consumidor controle el ritmo del productor cuando los datos llegan más rápido de lo que se procesan. | `05-maestria/03-structured-concurrency.md` |
| **Backend for Frontend (BFF)** | Backend orientado a una experiencia concreta de cliente, adaptado a las necesidades de la app. | `03-evolucion/07-backend-firebase.md` |
| **BDD** | Behavior-Driven Development: forma de especificar comportamiento con escenarios legibles antes de implementar. | `01-fundamentos/02-metodologia-bdd-tdd.md` |
| **Bitácora de aprendizaje** | Registro breve donde el alumno documenta qué entendió, qué le costó y qué validó. | `anexos/quizzes-autoevaluacion.md` |
| **Bounded Context** | Límite semántico donde un término tiene un significado preciso y ownership claro. | `04-arquitecto/01-bounded-contexts.md` |
| **Cache-first** | Estrategia que sirve primero desde caché local y refresca desde red en segundo plano. | `03-evolucion/01-caching-offline.md` |
| **Cancellation cooperative** | Modelo donde una tarea no se detiene “sola”; el código debe comprobar si fue cancelada y reaccionar. | `05-maestria/03-structured-concurrency.md` |
| **Checklist PR-ready** | Lista mínima de calidad antes de mergear: tests, riesgos, rollback, observabilidad y seguridad. | `00-core-mobile/04-calidad-pr-ready.md` |
| **Clean Architecture** | Diseño donde las capas externas dependen de las internas y no al revés. | `01-fundamentos/01-principios-ingenieria.md` |
| **Clock inyectado** | Reloj pasado como dependencia para hacer tests deterministas sobre tiempo, TTL o expiración. | `03-evolucion/02-consistencia.md` |
| **Composition Root** | Punto único donde se crean e interconectan las implementaciones concretas de la app. | `02-integracion/06-composition-root.md` |
| **Contract Test** | Test que verifica que una implementación concreta respeta el contrato definido por su protocolo. | `02-integracion/05-integration-tests.md` |
| **Context Map** | Diagrama que muestra bounded contexts y las relaciones entre ellos. | `04-arquitecto/01-bounded-contexts.md` |
| **CQRS** | Separación entre comandos que cambian estado y consultas que lo leen, para reducir ambigüedad y acoplamiento. | `anexos/guia-cqs-cqrs.md` |
| **Cross-feature contract** | Contrato explícito entre features para cooperar sin importarse directamente. | `02-integracion/03-contratos-features.md` |
| **Data race** | Acceso concurrente no coordinado a memoria mutable que puede producir resultados inconsistentes. | `05-maestria/01-isolation-domains.md` |
| **Deep Link** | URL o ruta externa que abre una pantalla concreta de la app. | `04-arquitecto/03-navegacion-deeplinks.md` |
| **Decorador** | Patrón que envuelve otra implementación para añadir comportamiento sin modificarla. | `03-evolucion/03-observabilidad.md` |
| **Dependency governance** | Reglas para controlar qué dependencias entran al sistema, quién las aprueba y cómo se versionan. | `00-core-mobile/09-dependency-governance-supply-chain.md` |
| **DTO** | Data Transfer Object: estructura de datos de transporte, separada del modelo de dominio. | `02-integracion/04-infra-real-network.md` |
| **Entidad** | Objeto con identidad propia que persiste en el tiempo y no se define solo por su valor. | `00-core-mobile/02-invariantes-y-contratos.md` |
| **Error budget** | Presupuesto de errores aceptable antes de priorizar fiabilidad por encima de nuevas funcionalidades. | `00-core-mobile/05-observabilidad-operacion.md` |
| **Escenario Given/When/Then** | Formato de BDD para describir contexto, acción y resultado esperado. | `01-fundamentos/02-metodologia-bdd-tdd.md` |
| **Feature flag** | Interruptor configurable que activa o desactiva funcionalidad sin redeploy completo. | `00-core-mobile/06-release-rollback-flags.md` |
| **Feature-First** | Organización vertical del código por capacidades completas en vez de por capas horizontales globales. | `01-fundamentos/04-estructura-feature-first.md` |
| **Flaky test** | Test que falla de forma aleatoria sin cambios de código y erosiona la confianza del equipo. | `02-integracion/05-integration-tests.md` |
| **Freshness Policy** | Política que decide si unos datos siguen siendo suficientemente frescos para mostrarse. | `03-evolucion/02-consistencia.md` |
| **HTTPClient** | Puerto de infraestructura que abstrae el transporte HTTP real de la app. | `02-integracion/04-infra-real-network.md` |
| **Infrastructure** | Capa que implementa puertos con detalles concretos de red, persistencia o SDKs externos. | `01-fundamentos/01-principios-ingenieria.md` |
| **Integration Test** | Test que verifica colaboración real entre varios componentes, dejando dobles solo en los bordes externos. | `02-integracion/05-integration-tests.md` |
| **Invariante** | Regla que siempre debe cumplirse en el dominio, aunque cambie la UI o la infraestructura. | `00-core-mobile/02-invariantes-y-contratos.md` |
| **Isolation Domain** | Agrupación de responsabilidades concurrentes con fronteras explícitas de aislamiento y paso de datos. | `05-maestria/01-isolation-domains.md` |
| **Lenguaje ubicuo** | Vocabulario compartido entre negocio y desarrollo usado en código, tests y conversaciones. | `00-core-mobile/02-invariantes-y-contratos.md` |
| **MainActor** | Aislamiento que obliga a ejecutar cierto código en el hilo principal, útil para UI y ViewModels. | `02-integracion/07-swiftui-enterprise.md` |
| **Mapper** | Componente que traduce entre modelos de dominio, DTOs, entidades de caché o payloads externos. | `02-integracion/04-infra-real-network.md` |
| **ModelContainer** | Contenedor principal de SwiftData que gestiona el modelo persistente y su contexto. | `03-evolucion/06-swiftdata-store.md` |
| **Navigation policy** | Regla central que decide si una navegación se permite, redirige o rechaza. | `04-arquitecto/03-navegacion-deeplinks.md` |
| **Network-first** | Estrategia que intenta primero la red y recurre a caché local solo como fallback. | `03-evolucion/01-caching-offline.md` |
| **Observabilidad estructurada** | Registro de eventos, métricas y contexto con formato consistente para operar y diagnosticar la app. | `03-evolucion/03-observabilidad.md` |
| **@Observable** | Macro moderna de Swift que convierte un tipo en observable para SwiftUI sin `@Published`. | `02-integracion/07-swiftui-enterprise.md` |
| **Offline-first** | Enfoque donde la experiencia base del usuario sigue funcionando aunque la red falle o llegue tarde. | `03-evolucion/01-caching-offline.md` |
| **Ownership** | Responsabilidad clara de un equipo sobre un bounded context, sus contratos y su evolución. | `04-arquitecto/01-bounded-contexts.md` |
| **Port / Puerto** | Interfaz definida por una capa interna para expresar lo que necesita sin depender de detalles concretos. | `01-fundamentos/01-principios-ingenieria.md` |
| **ProductStore** | Puerto local de persistencia para guardar y recuperar catálogo sin exponer SwiftData al dominio. | `03-evolucion/06-swiftdata-store.md` |
| **Project final** | Entrega integradora donde el alumno debe demostrar dominio técnico y criterio arquitectónico. | `anexos/proyecto-final.md` |
| **Quality Gate** | Condición automática que debe cumplirse antes de promocionar un cambio a una rama superior. | `04-arquitecto/06-quality-gates.md` |
| **Release train** | Cadencia predecible de entregas que reduce improvisación y permite gobernar riesgos. | `00-core-mobile/06-release-rollback-flags.md` |
| **Repository** | Abstracción que expone operaciones del dominio sin filtrar detalles de red o almacenamiento. | `01-fundamentos/04-estructura-feature-first.md` |
| **Rollback** | Estrategia para volver atrás o mitigar rápidamente un cambio que degradó producción. | `00-core-mobile/06-release-rollback-flags.md` |
| **Sendable** | Protocolo de Swift que indica que un valor puede cruzar fronteras de concurrencia con seguridad. | `02-integracion/04-infra-real-network.md` |
| **Shared Kernel** | Conjunto mínimo de tipos compartidos entre bounded contexts bajo gobierno explícito. | `04-arquitecto/01-bounded-contexts.md` |
| **SLO** | Service Level Objective: objetivo medible de fiabilidad o rendimiento que guía decisiones operativas. | `00-core-mobile/05-observabilidad-operacion.md` |
| **Small Batches** | Disciplina de entregar cambios pequeños, completos y validados para acelerar feedback. | `01-fundamentos/01-principios-ingenieria.md` |
| **SPM** | Swift Package Manager: herramienta para modularizar, resolver dependencias y versionar paquetes Swift. | `04-arquitecto/04-versionado-spm.md` |
| **Spy** | Test double que registra llamadas recibidas para verificar interacciones entre componentes. | `01-fundamentos/02-metodologia-tdd-practica.md` |
| **Strict Concurrency** | Modo de Swift 6 que eleva a problema visible muchos riesgos de concurrencia en compilación. | `05-maestria/09-migracion-swift6.md` |
| **Structured Concurrency** | Modelo de Swift donde las tareas hijas viven y terminan bajo una jerarquía controlada. | `05-maestria/03-structured-concurrency.md` |
| **Stub** | Doble de prueba que devuelve respuestas predefinidas sin lógica real de producción. | `01-fundamentos/02-metodologia-tdd-practica.md` |
| **SUT** | System Under Test: componente exacto que estamos validando en un test concreto. | `01-fundamentos/02-metodologia-tdd-practica.md` |
| **SwiftData** | Framework moderno de persistencia local de Apple usado en el curso detrás de puertos de infraestructura. | `03-evolucion/06-swiftdata-store.md` |
| **TaskGroup** | API de Swift para lanzar y coordinar varias tareas hijas estructuradas. | `05-maestria/03-structured-concurrency.md` |
| **TDD** | Test-Driven Development: ciclo Red → Green → Refactor para guiar diseño y validación. | `01-fundamentos/02-metodologia-bdd-tdd.md` |
| **Threat modeling** | Análisis sistemático de amenazas, activos, vectores y mitigaciones antes de que el fallo llegue a producción. | `00-core-mobile/08-seguridad-privacidad-threat-modeling.md` |
| **TTL** | Time-To-Live: tiempo máximo que un dato cacheado se considera válido antes de expirar. | `03-evolucion/01-caching-offline.md` |
| **UDF (unidirectional data flow)** | Flujo de datos donde el estado baja y las acciones suben, reduciendo ambigüedad en UI. | `02-integracion/07-swiftui-enterprise.md` |
| **Unit Test** | Test rápido y determinista que valida un componente en aislamiento. | `01-fundamentos/02-metodologia-tdd-practica.md` |
| **Value Object** | Objeto sin identidad, definido por sus valores y normalmente inmutable. | `00-core-mobile/02-invariantes-y-contratos.md` |
| **Vertical slicing** | Forma de dividir el sistema en features completas de arriba abajo en vez de por tecnología. | `01-fundamentos/04-estructura-feature-first.md` |
| **Wiring** | Ensamblado concreto de dependencias en el Composition Root o en factories de composición. | `02-integracion/06-composition-root.md` |

---

## Cómo usar este glosario

1. Si un término te suena pero no lo dominas, vuelve a su **primera aparición** y relee esa lección antes de seguir.
2. Si aparece en varias etapas, usa este glosario para distinguir cuándo un concepto se introduce y cuándo se profundiza.
3. Si detectas un término del curso que aún no esté aquí, añádelo al cerrar la etapa correspondiente: el glosario también forma parte del mantenimiento arquitectónico.

---

<!-- plantilla-pedagógica:auto -->

## Refuerzo pedagógico
Contexto: normalización automática para `anexos/glosario.md`.

### Objetivo
- Consolidar un vocabulario técnico común para todas las etapas del curso.

### Prerrequisitos
- Haber leído al menos la introducción de la etapa en la que estás trabajando.

### Práctica guiada
- Elige cinco términos del bloque actual y explica con tus palabras dónde aparecen en el scaffold real.

### Validación
- Checklist rápido:
  - [ ] Distingo términos de dominio, aplicación, interfaz e infraestructura.
  - [ ] Sé volver a la lección donde se introdujo cada término importante.
  - [ ] Puedo explicar al menos un trade-off asociado a los conceptos nuevos de mi etapa actual.
