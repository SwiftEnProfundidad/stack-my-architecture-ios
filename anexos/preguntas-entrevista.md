# Anexo: Batería de Preguntas para Entrevistas Técnicas

> Preguntas objetivo con respuestas modelos basadas en el contenido del curso

---

## Cómo Usar Este Anexo

Este documento organiza preguntas por nivel (Junior → Mid → Senior → Architect) y por tema. Las respuestas son modelos que puedes adaptar a tu experiencia real.

---

## NIVEL 1: FUNDAMENTOS (Junior → Mid)

### Clean Architecture & Separation of Concerns

**P: ¿Qué es Clean Architecture y por qué usarla en iOS?**

> **R:** Es una arquitectura que separa responsabilidades en capas concéntricas: Domain (reglas de negocio), Application (casos de uso), Infrastructure (detalles técnicos) e Interface (UI). En iOS, nos protege del " Massive View Controller" y permite testear la lógica de negocio sin simuladores. El principio clave es: "Las dependencias apuntan siempre hacia adentro" - el domain no conoce UI ni network.

**P: ¿Cuál es la diferencia entre Domain y Application?**

> **R:** Domain contiene los objetos de valor, entidades, invariantes y errores de dominio. Es puro, sin dependencias externas. Application contiene los casos de uso que orquestan el domain: coordinan qué entidades llamar, en qué orden, y qué hacer con los resultados. Un caso de uso pertenece a application, un UserID o EmailValidation pertenece a domain.

**P: ¿Por qué usar Protocols en lugar de clases concretas?**

> **R:** Protocols permiten inversión de dependencias. En lugar de que el ViewModel cree directamente un NetworkManager (acoplamiento fuerte), depende de un protocolo UserRepository. Esto permite: (1) inyectar mocks en tests, (2) cambiar implementación sin tocar código cliente, (3) trabajar con interfaces que documentan intención mejor que implementaciones.

---

### Testing & TDD

**P: ¿Cuál es la diferencia entre unit test, integration test y UI test?**

> **R:** Unit test verifica una unidad aislada (una función, un use case) con mocks. Rápidos (<10ms), determinísticos. Integration test verifica que componentes reales funcionan juntos (API real + base de datos real). Más lentos, detectan problemas de integración. UI test verifica flujos completos desde la perspectiva del usuario. Lentos, frágiles, pero validan el journey completo.

**P: ¿Cuándo usar TDD y cuándo no?**

> **R:** TDD brilla donde la lógica es compleja y estable: cálculos financieros, reglas de validación, flujos de estado. No vale la pena donde hay alto churn visual: animaciones experimentales, prototipos de UI, features que cambian semanalmente. Mi criterio: si el coste de un bug > coste del test + tiempo de escribirlo, entonces TDD.

**P: ¿Cómo testeas código asíncrono?**

> **R:** Swift concurrency facilita esto enormemente. Con async/await puedo usar XCTest con async throws func. Para controlar el tiempo en tests, inyecto un Clock o un TaskScheduler protocol. En tests uso un ImmediateScheduler que ejecuta sincrónicamente; en producción uso el real. Esto elimina sleeps y race conditions en tests.

---

### SwiftUI & Swift 6

**P: ¿Cuál es la diferencia entre @State, @StateObject y @ObservedObject?**

> **R:** @State es para datos privados de la view que mutan localmente (strings, bools). @StateObject crea y retiene un ObservableObject que pertenece a esa view (ViewModels). @ObservedObject recibe un objeto externo que la view no posee. La regla es: si la view crea y posee el objeto → @StateObject; si lo recibe → @ObservedObject.

**P: ¿Qué es Structured Concurrency y por qué importa?**

> **R:** Es el modelo de concurrencia de Swift 5.5+ basado en async/await y Task. A diferencia de completion handlers, structured concurrency garantiza que las tareas hijas completan antes que las padres, eliminando fugas de memoria comunes en closures. Permite cancelación cooperativa: una Task cancelled notifica a sus hijas para que aborten gracefulmente.

**P: ¿Cómo evitas el "callback hell" en Swift?**

> **R:** async/await elimina el problema. En lugar de nested completion handlers, escribo código lineal que parece síncrono pero ejecuta asíncrono. Para operaciones múltiples, uso async let para paralelismo estructurado, o TaskGroup cuando el número de tareas es dinámico. El compilador maneja el estado de la máquina, no yo.

---

## NIVEL 2: INTEGRACIÓN (Mid → Senior)

### Arquitectura Modular

**P: ¿Cómo comunicas dos features sin acoplarlas?**

> **R:** Usando eventos y protocols. Features definen protocols que otros pueden implementar (contratos). Se comunican mediante event bus tipado: cuando algo importante ocurre, emite un evento. Features interesados se suscriben. Ningún feature conoce la existencia de otros, solo conocen los eventos y protocols. Esto permite cambiar, añadir o remover features sin tocar código existente.

**P: ¿Qué es un Composition Root y dónde va?**

> **R:** Es el único lugar donde se ensamblan las dependencias. En apps pequeñas: AppDelegate/SceneDelegate. En apps grandes: un assembly específico. Allí creo instancias reales de repositories, los inyecto en use cases, estos en ViewModels, y finalmente en Views. El Composition Root es "la mugre inevitable" pero contenida: todo el wiring explícito está ahí, no disperso.

**P: ¿Cómo manejas navegación en arquitectura limpia?**

> **R:** La navegación es un efecto secundario coordinado por un Router/Coordinator. El ViewModel no navega directamente; emite un evento de navegación ("userWantsProfile") que el coordinador escucha y traduce a una acción de UIKit/SwiftUI. Esto desacopla la lógica de presentación de la implementación de navegación, permitiendo testear la intención de navegación sin simulador.

---

### Manejo de Estado

**P: ¿Dónde vive el estado en tu arquitectura?**

> **R:** El estado inmutable y de negocio vive en Domain (entidades value objects). El estado de presentación (UI state) vive en Application (ViewModels con @Observable/@Published). El estado de infraestructura (caching, tokens) vive en Infrastructure. Cada capa maneja el estado que le corresponde, y fluye hacia afuera mediante inmutabilidad: domain retorna nuevos valores, no muta existentes.

**P: ¿Cómo manejas errores a través de capas?**

> **R:** Domain define errores específicos de dominio (Email.InvalidFormat, Network.Timeout). Application mapea errores de infraestructura a errores de dominio para que la UI no conozca detalles técnicos. UI recibe Resultados tipados: .success(DomainModel) o .failure(DomainError). No uso excepciones para flujo de control; uso tipos que representan el resultado.

**P: ¿SwiftData o Core Data? ¿Cuándo cada uno?**

> **R:** SwiftData para proyectos nuevos con iOS 17+ target. Menos boilerplate, integración nativa con SwiftUI, API moderna con macros. Core Data para proyectos legacy, soporte iOS 15/16, o cuando necesitas features avanzadas que SwiftData aún no tiene (NSFetchedResultsController complejo, migrations pesadas). Ambos pueden abstraerse tras un repository protocol para swap futuro.

---

### Networking & APIs

**P: ¿Cómo diseñas contratos de API que no rompan la app?**

> **R:** (1) Contract tests: tests que validan que nuestros mocks responden igual que el servidor real. (2) Versioning semántico en APIs: campos nuevos son aditivos, nunca cambio tipo ni elimino sin deprecación. (3) Parsing defensivo: uso de default values, campos opcionales, graceful degradation. (4) Feature flags: si la API cambia, la app puede desactivar la feature hasta update.

**P: ¿Cómo implementas retry y backoff en red?**

> **R:** En capa Infrastructure, envuelvo el client HTTP en un decorator RetryableNetworkClient que implementa el mismo protocolo. Implementa exponential backoff con jitter para evitar thundering herd. Distingue errores retriables (5xx, timeout) vs no retriables (4xx). Respeto circuit breaker: si fallos consecutivos > threshold, "abro" el circuito y fallo rápido sin intentar, protegiendo el servidor y la UX.

**P: ¿Cómo cacheas datos y mantienes consistencia?**

> **R:** Estrategia "network-first with local fallback" para freshness, o "cache-first with background refresh" para offline. Invalidación por TTL (time-based), event-driven (cuando sabemos que cambió), o version-based (etag). Consistencia mediante single source of truth: la app solo escribe cache desde un punto central (repository), nunca scattered writes. Observable cache permite que UI reaccione a cambios.

---

## NIVEL 3: MAESTRÍA (Senior → Architect)

### Concurrencia Avanzada

**P: ¿Actors vs Locks: cuándo usar cada uno?**

> **R:** Actors en Swift son la evolución de locks: garantizan serialización de acceso sin deadlocks ni olvidar unlock. Los uso para estado mutable compartido (cache, counters). Locks (NSLock, os_unfair_lock) solo cuando necesito máxima performance en hot paths y puedo garantizar correctitud manual. En Swift 6, preferiría @MainActor para UI state y custom actors para estado compartido del dominio.

**P: ¿Cómo evitas race conditions en arquitectura?**

> **R:** (1) Inmutabilidad: estado que no cambia no tiene race conditions. (2) Actors: estado mutable aislado en actors que serializan acceso. (3) Value types (struct) por defecto: no comparten referencia. (4) Isolation checking del compilador Swift 6: asegura que sendable types cruzan boundaries thread-safe. (5) Testing de estrés: instrumentos como Thread Sanitizer y tests con múltiples threads concurrentes.

**P: ¿Cómo manejas cancelación de operaciones largas?**

> **R:** Structured concurrency hace esto natural. Una Task lanzada hereda el contexto de cancelación de su padre. En código async, verifico Task.isCancelled en puntos de suspensión. Para operaciones en curso (descarga de archivo, parsing pesado), uso cooperative cancellation: la operación verifica periódicamente si debe abortar y libera recursos gracefulmente. No uso force-cancel ni kill threads.

---

### Testing Avanzado

**P: ¿Cómo testeas código que depende del tiempo?**

> **R:** Inyección de abstracciones. En lugar de llamar Date() o Task.sleep directamente, dependo de un protocolo Clock. En producción inyecto ContinuousClock(); en tests, InstantClock que avanza manualmente. Esto permite testear timeouts, debounces, y lógica time-sensitive de forma determinística y instantánea.

**P: ¿Qué son los Contract Tests y por qué importan?**

> **R:** Validan que nuestros mocks/stubs se comportan como el sistema real. Ejemplo: tengo un API mock para tests unitarios. Un contract test verifica que cuando el servidor real responde X, mi mock también responde X. Detectan cuando la API real cambia y nuestros tests unitarios están testando contra comportamiento obsoleto. Son el puente entre unit tests rápidos y tests de integración lentos.

**P: ¿Cómo mantienes tests determinísticos?**

> **R:** Eliminando fuentes de no-determinismo: (1) no usar sleep() reales, usar clocks inyectados; (2) no usar Date() real, usar time provider; (3) no usar random real, usar seeded random; (4) no usar filesystem real, usar in-memory; (5) no usar network real en unit tests. Cada test debe producir el mismo resultado dadas las mismas entradas, siempre.

---

### Performance & Observabilidad

**P: ¿Cómo identificas cuellos de botella en iOS?**

> **R:** Instruments: Time Profiler para CPU, Allocations para memoria, Network para I/O, Hangs para responsividad. Métricas en producción: Firebase Performance Monitoring, MetricKit. Patrones comunes en iOS: (1) síncrono en main thread → mover a background; (2) retain cycles en closures → [weak self]; (3) over-fetching de red → pagination; (4) Core Data blocking main → contextos privados; (5) SwiftUI recálculos excesivos → identificar qué causa invalidación.

**P: ¿Cómo implementas logging efectivo?**

> **R:** Estructurado y contextual: timestamp, severity, componente, correlación ID (para trazar requests a través del sistema), y payload relevante. Niveles: debug (verbose, local only), info (flujos de negocio), warning (recuperables), error (fallos). En producción, aggregators como Datadog/Splunk. No loggeo PII (Personally Identifiable Information). Sampling para alto volumen. Contextual logging: cada log incluye metadata de la operación en curso.

**P: ¿Cómo manejas memory leaks?**

> **R:** Prevención: (1) [weak self] en closures que capturan self; (2) weak references en delegates; (3) romper ciclos en dependencias con unowned/weak según lifecycle. Detección: Memory Graph Debugger en Xcode (muestra objetos vivos y quién los retiene), Leaks instrument en Instruments. Testing: tests de allocación que crean/destruyen componentes y verifican que reference count llega a cero.

---

## NIVEL 4: ARQUITECTURA ESTRATÉGICA

### Diseño de Sistemas

**P: ¿Cómo diseñarías una app que soporte 5 equipos trabajando en paralelo?**

> **R:** Modularización en bounded contexts: cada equipo es owner de un módulo con API pública clara. Contratos versionados: cambios en API requieren coordinación, internals son libres. CI independiente por módulo: un equipo no bloquea a otros. Feature flags: permiten integrar código sin activar funcionalidad. Comunicación asíncrona: eventos entre módulos, no llamadas síncronas que acoplan. Arquitectura de plugins: nuevos features se añaden sin tocar código existente.

**P: ¿Monorepo vs multirepo para iOS?**

> **R:** Monorepo cuando: equipos pequeños (<20 devs), alta necesidad de refactors globales, builds cacheados con Bazel/SWC. Multirepo cuando: equipos grandes con ownership claro, necesidad de versionado semántico independiente, diferentes ciclos de release. Híbrido: core monorepo + features en SPM packages con versionado.

**P: ¿Cómo manejas versionado de APIs y retrocompatibilidad?**

> **R:** Versionado semántico: MAJOR (breaking changes, coordino migración), MINOR (features aditivas, seguro actualizar), PATCH (bugs). En APIs: additive changes only (nuevos campos opcionales). Feature flags en app para usar nuevos endpoints solo cuando listo. Deprecación: anuncio con tiempo, mantengo versión vieja durante ventana de migración, telemetry para saber quién usa qué.

---

### Liderazgo Técnico

**P: ¿Cómo convences al equipo de una decisión arquitectónica?**

> **R:** Evidencia sobre opiniones: prototipos con métricas, no "creo que es mejor". Trade-offs explícitos: "Esto mejora X pero costa Y, lo aceptamos porque...". RFC (Request for Comments): documento que presenta problema, opciones, recomendación, y solicita feedback. Small wins: implementar en feature piloto, demostrar valor, luego expandir. No imposición: si hay resistencia fuerte, entender preocupaciones y iterar.

**P: ¿Cómo balanceas deuda técnica vs velocidad de negocio?**

> **R:** Deuda táctica vs estratégica: táctica es consciente, temporal, con plan de pago. Estratégica es ignorada hasta bloquear. Budget técnico: 20% de capacidad sprint para refactoring. Métricas: cuando velocity decae o defect rate crece, es momento de invertir. Coste de oportunidad: cada día sin pagar deuda acumula interés. Big-bang rewrites son riesgosos; prefiero refactoring incremental con feature flags.

**P: ¿Cómo documentas arquitectura para que sea útil?**

> **R:** ADRs para decisiones irreversibles: contexto, decisión, consecuencias. Diagramas como código (Mermaid) versionados con el código. READMEs en cada módulo: qué hace, cómo usarlo, ejemplos. No documento lo obvio (qué hace un init), sí documento el porqué (por qué esta abstracción y no otra). Living documentation: tests son la mejor doc porque están forzadas a estar actualizados.

---

## PREGUNTAS TRAMPA (Red Flags)

### ¿Cuál es la "mejor" arquitectura?

❌ **Mal:** "MVVM es la mejor" o "VIPER es superior"

✅ **Bien:** "No existe la mejor arquitectura universal. Depende de: tamaño del equipo, complejidad del dominio, constraints de tiempo, experiencia del equipo. He usado MVVM para apps simples, Clean Architecture para dominios complejos, y adapto según evolucionan los requisitos."

### ¿Por qué no usaste [tecnología hype]?

❌ **Mal:** "No la conozco" o "Es mala"

✅ **Bien:** "Evalué [tecnología] en el contexto de nuestro proyecto. Los beneficios eran X, pero los costes eran Y (ej: curva de aprendizaje, riesgo de tecnología inmadura, vendor lock-in). Elegí [alternativa] porque optimizaba para nuestros constraints específicos: estabilidad, hiring, tiempo de delivery."

### ¿Has cometido errores arquitectónicos?

❌ **Mal:** "No, todo salió bien"

✅ **Bien:** "Sí. En [proyecto] sobre-ingenierizé abstracciones anticipando requisitos que nunca llegaron. Costó velocidad inicial y complejidad innecesaria. Aprendí a diseñar para el problema actual con hooks de extensión, no para hipotéticos futuros. Ahora aplico YAGNI con cuidado."

---

## GUÍA DE ESTUDIO POR NIVEL

### Preparándote para Junior → Mid
- Domina: Clean Architecture básica, testing unitario, SwiftUI moderno
- Practica: Explicar por qué separas domain de UI
- Evita: "Siempre uso X", "Nunca uso Y"

### Preparándote para Mid → Senior
- Domina: Modularización, TDD completo, concurrencia Swift 6
- Practica: Discutir trade-offs de decisiones reales
- Evita: Respuestas teóricas sin ejemplos concretos

### Preparándote para Senior → Architect
- Domina: Diseño de sistemas, métricas, escalabilidad de equipos
- Practica: Arquitectura de soluciones a problemas abiertos
- Evita: Diseños perfectos ignorando constraints de negocio

---

## Simulacro de Entrevista Completa

**Escenario:** Entrevista para Senior iOS Engineer en fintech

**Entrevistador:** "Cuéntame sobre una arquitectura que hayas diseñado"

**Respuesta modelo:**
> "Diseñé la arquitectura de una app de trading con equipo de 6 developers. El problema era: códigos legacy con acoplamiento entre trading, portfolio y user profile. Cualquier cambio en uno rompía los otros.
>
> Decidí: modularización por bounded contexts (trading, portfolio, user), comunicación vía eventos tipados, y contratos claros con protocols.
>
> Trade-off: overhead inicial de abstracciones vs velocidad futura. Acepté el coste porque las métricas mostraban que el 40% de los bugs eran por acoplamiento accidental.
>
> Implementé en 2 meses con migración gradual (feature flags). Resultados: reducción del 60% en bugs de integración, tiempo de build de 8 a 3 minutos, y 3 equipos pudieron trabajar en paralelo sin conflictos de merge.
>
> Si volviera a hacerlo: invertiría más en contract tests upfront. Detectamos inconsistencias APIs tarde en el proceso."

---

## Recursos Adicionales

- [Cracking the Coding Interview](http://www.crackingthecodinginterview.com/) - Para algoritmos y estructuras de datos
- [System Design Interview](https://www.amazon.com/System-Design-Interview-Insiders-Guide/dp/0991344620) - Para diseño de sistemas distribuidos
- [The Manager's Path](https://www.amazon.com/Managers-Path-Leaders-Navigating-Growth/dp/1491973897) - Para crecimiento a liderazgo técnico

---

**Consejo final:** Las mejores respuestas combinan principios sólidos, experiencia real, y humildad para reconocer que siempre hay trade-offs.
