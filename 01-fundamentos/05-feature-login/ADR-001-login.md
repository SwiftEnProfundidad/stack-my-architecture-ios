# ADR-001: Diseño de la Feature Login

## Qué es un ADR y por qué lo escribimos

Un Architecture Decision Record (ADR) es un documento corto que registra una decisión arquitectónica importante, junto con su contexto, las alternativas que se consideraron, y las consecuencias esperadas. Los ADRs sirven para que alguien que se incorpore al proyecto dentro de seis meses pueda entender **por qué** el código está como está, no solo **cómo** está.

Este es el primer ADR del curso. Documenta las decisiones que tomamos al diseñar la feature Login. Cada feature importante tendrá su propio ADR.

---

**Estado:** Aceptado
**Fecha:** Etapa 1
**Autores:** Equipo de desarrollo
**Feature:** Login (autenticación de usuario)

---

## Contexto

La aplicación necesita que el usuario se identifique antes de acceder al contenido. La autenticación se realiza con email y contraseña contra un servidor remoto. Esta es la primera feature del sistema y establece los patrones arquitectónicos que seguirán todas las features posteriores. Las decisiones aquí tomadas tienen impacto más allá del Login: definen cómo se estructura, se testea, y se compone cada feature del proyecto.

El equipo ha decidido usar una arquitectura Clean Architecture con organización Feature-First, metodología BDD para especificación y TDD para implementación, y XCTest como framework de testing.

---

## Decisión principal

Implementar Login como una feature vertical completa con cuatro capas (Domain, Application, Infrastructure, Interface), cada una con responsabilidades claras y reglas de dependencia estrictas. La feature es autónoma: contiene todo lo necesario para funcionar, no depende de otras features, y se comunica con el exterior a través de eventos (closures).

---

## Decisiones específicas y alternativas consideradas

### 1. Value Objects para Email y Password

**Decisión:** Usar structs con validación en el `init` que lanzan errores tipados. Si el `init` no lanza, el objeto es válido. No existe un `Email` o `Password` inválido en el sistema.

**Alternativas consideradas:**

**`init?` (failable initializer).** Devuelve `nil` si la validación falla. El problema es que pierde información: el llamante solo sabe que falló, pero no por qué. ¿El email no tenía arroba? ¿No tenía punto en el dominio? ¿Estaba vacío? Con `nil` no hay forma de distinguir. Descartada por pérdida de información.

**Validación en el Use Case.** En lugar de que `Email` se valide a sí mismo, el caso de uso podría validar el string antes de crear el `Email`. El problema es que esto permite crear un `Email` inválido si alguien se salta la validación. La responsabilidad se dispersa y se duplica. Descartada por fragilidad.

**Usar `String` directamente.** Sin Value Objects, el email y el password serían simples strings. Esto permite pasar un email donde se espera un password (ambos son `String`), no centraliza la validación, y no impide estados inválidos. Descartada por falta de seguridad de tipos.

**Justificación de la decisión:** Los Value Objects con validación en construcción eliminan una categoría completa de bugs: los estados inválidos. Si el objeto existe, es válido. Siempre. Esto simplifica todo el código que consume estos tipos porque no necesita volver a validar.

### 2. Errores tipados con `throws`

**Decisión:** Los constructores de Value Objects y la función del caso de uso usan `throws` con enums de error que conforman `Error`, `Equatable`, y `Sendable`.

**Alternativas consideradas:**

**Usar `Result<T, E>` como tipo de retorno.** En lugar de lanzar errores, devolver un `Result`. Es una opción válida, pero en Swift moderno con `async/await`, `throws` es más idiomático y se integra mejor con `try/catch` y `do/catch`. El código se lee de forma más natural. Descartada por verbosidad innecesaria.

**Errores genéricos (`Error` sin tipar).** Lanzar cualquier error sin un tipo específico. El problema es que el llamante no sabe qué errores puede recibir sin leer la implementación. Los errores tipados documentan en la interfaz qué puede fallar. Descartada por falta de claridad.

**Justificación:** Los errores tipados combinados con `throws` son la forma más idiomática en Swift de comunicar fallos recuperables con información precisa sobre la causa.

### 3. Protocolo AuthGateway como puerto

**Decisión:** Definir un protocolo `AuthGateway` en la capa Application que el caso de uso consume, e implementarlo en la capa Infrastructure.

**Alternativas consideradas:**

**Llamar a `URLSession` directamente desde el caso de uso.** Más simple, menos archivos. Pero acopla el caso de uso a la red: no se puede testear sin servidor, no se pueden hacer previews sin conexión, no se puede cambiar la implementación de red sin modificar el caso de uso. Descartada por acoplamiento.

**Usar un genérico en lugar de un existential.** `struct LoginUseCase<Gateway: AuthGateway>` en lugar de `any AuthGateway`. Esto elimina el overhead del existential box. Pero hace que el tipo del caso de uso dependa del tipo del gateway, lo que complica la composición. El overhead del existential es negligible para una operación que se ejecuta una vez por acción del usuario. Descartada por complejidad innecesaria.

**Justificación:** El protocolo como puerto es la materialización del principio de inversión de dependencias. Permite testear, previsualizar, y cambiar implementaciones sin afectar a la lógica de negocio.

### 4. `@Observable` para el ViewModel

**Decisión:** Usar la macro `@Observable` (Swift 5.9+ / iOS 17+) para el ViewModel.

**Alternativas consideradas:**

**`ObservableObject` con `@Published`.** Es el enfoque que Apple introdujo con SwiftUI en iOS 13. Funciona, pero tiene un defecto fundamental: cualquier cambio en cualquier `@Published` property invalida todas las vistas que observan el objeto, independientemente de qué propiedad cambió. `@Observable` tiene tracking granular: solo se re-renderizan las vistas que leen la propiedad que cambió. Descartada por ineficiencia y por ser la API legacy.

**State machine / Reducer pattern.** Un modelo tipo Redux donde el estado es un struct inmutable y los cambios se hacen a través de acciones que pasan por un reducer. Es más testeable en teoría (puedes testear el reducer como función pura), pero añade una capa de indirección que no se justifica para una feature simple como Login. Lo consideraremos en la Etapa 3 si la complejidad lo requiere. Descartada por sobreingeniería.

**Justificación:** `@Observable` es más eficiente, más limpio (no necesita `@Published` en cada propiedad), y es la dirección en la que Apple está llevando SwiftUI.

### 5. Navegación por closure inyectado

**Decisión:** El ViewModel recibe un closure `onLoginSucceeded: (Session) -> Void` que el Composition Root inyecta. La feature Login no sabe a dónde se navega después del éxito.

**Alternativas consideradas:**

**`NavigationLink` directo en la vista.** `LoginView` tendría un `NavigationLink(destination: HomeView())`. Simple, pero acopla Login a Home. Si Home cambia, Login se ve afectado. Si quieres reutilizar Login en otro contexto, no puedes sin modificarlo. Descartada por acoplamiento.

**Coordinator/Router como dependencia del ViewModel.** El ViewModel recibiría un protocolo `Navigator` que define acciones de navegación. Esto es más formal que un closure, pero para una sola acción ("login exitoso") un closure es suficiente. Un protocolo de navegación tiene sentido cuando hay múltiples destinos posibles desde una feature. Lo consideraremos en la Etapa 2 cuando haya navegación más compleja. Descartada por sobreingeniería en esta etapa.

**Justificación:** Un closure es la forma más simple y desacoplada de comunicar un evento sin crear abstracciones innecesarias. Es suficiente para la Etapa 1 y se puede evolucionar a un coordinador formal cuando la complejidad lo requiera.

### 6. DTOs separados de los modelos de Domain

**Decisión:** `AuthRequest` y `AuthResponse` son tipos separados de `Credentials` y `Session`. El mapping se hace dentro del gateway.

**Alternativas consideradas:**

**Hacer `Session` conforme a `Codable`.** Permite usar `Session` directamente para parsear JSON. Menos archivos, menos mapping. Pero acopla el Domain al formato del API. Si el servidor cambia el nombre de un campo, el modelo de Domain tiene que cambiar, lo que afecta en cascada a tests, casos de uso, y ViewModels. Descartada por acoplamiento.

**Justificación:** La separación entre modelos de Domain y DTOs de Infrastructure aísla el core de negocio de los cambios en servicios externos. El coste es unos pocos tipos adicionales y un mapping; el beneficio es estabilidad del Domain a largo plazo.

### 7. StubAuthGateway con delay configurable

**Decisión:** Crear un `StubAuthGateway` con un delay por defecto de 0.5 segundos, configurable.

**Justificación:** El stub permite desarrollo sin servidor, previews de SwiftUI instantáneas, y tests de integración rápidos. El delay simula latencia real para detectar problemas de UX durante el desarrollo. El delay se puede poner a 0 para tests unitarios que necesitan ser rápidos.

---

## Consecuencias

### Positivas

La feature tiene separación clara de responsabilidades por capas. Todos los tests (28) se ejecutan en menos de un segundo sin dependencias externas. Las SwiftUI Previews funcionan sin servidor. Cambiar la implementación del gateway (de remoto a stub, o de URLSession a otra librería) requiere cambiar una sola línea en el Composition Root. La feature se puede extraer a un módulo SPM en el futuro sin reestructuración.

### Negativas (trade-offs aceptados)

La feature tiene más archivos que un enfoque "ViewModel + View" directo (aproximadamente 12 archivos de producción y 5 de tests, frente a 2-3 archivos en un enfoque simplificado). Este es un trade-off consciente: más archivos a cambio de más claridad, más testeabilidad, y más facilidad de mantenimiento a largo plazo.

El aprendizaje inicial es más empinado. Un junior necesita entender Value Objects, puertos, adaptadores, y el ciclo BDD+TDD antes de poder contribuir. Pero una vez que entiende el patrón con Login, puede aplicarlo a cualquier feature nueva sin reinventar la rueda.

### Riesgos identificados

Ninguno para esta escala. La principal preocupación a futuro es que SharedKernel crezca demasiado si no somos disciplinados en mantener los tipos específicos de cada feature dentro de su directorio. Esto se monitoriza en cada code review.

---

## Referencias

Cada decisión está demostrada con código real y tests en las lecciones correspondientes:

**Especificación BDD:** [00-especificacion-bdd.md](00-especificacion-bdd.md) — Los escenarios que guían todas las decisiones.
**Capa Domain:** [01-domain.md](01-domain.md) — Value Objects, errores, eventos.
**Capa Application:** [02-application.md](02-application.md) — Caso de uso, puertos, traducción de errores.
**Capa Infrastructure:** [03-infrastructure.md](03-infrastructure.md) — Gateway, DTOs, contract tests.
**Capa Interface:** [04-interface-swiftui.md](04-interface-swiftui.md) — ViewModel, Vista, Composition Root.
**Retrospectiva TDD:** [05-tdd-ciclo-completo.md](05-tdd-ciclo-completo.md) — Patrones y lecciones aprendidas.
