# Metodología TDD: práctica Red-Green-Refactor

En la lección anterior cerramos la especificación BDD (qué debe hacer el sistema). En esta lección aplicamos TDD para implementar esos comportamientos de forma incremental y segura.

## TDD: Test-Driven Development

### Qué es realmente

TDD es una disciplina de desarrollo que consiste en un ciclo de tres pasos que se repite una y otra vez, cada pocos minutos:

### Diagrama: el ciclo Red-Green-Refactor

```mermaid
graph LR
    RED["RED<br/>Escribe un test<br/>que FALLA"] --> GREEN["GREEN<br/>Escribe lo MINIMO<br/>para que PASE"]
    GREEN --> REFACTOR["REFACTOR<br/>Mejora el diseno<br/>sin cambiar comportamiento"]
    REFACTOR --> RED

    RED -.->|"Duracion: 1-3 min"| GREEN
    GREEN -.->|"Duracion: 1-5 min"| REFACTOR
    REFACTOR -.->|"Duracion: 0-5 min"| RED

    style RED fill:#f8d7da,stroke:#dc3545
    style GREEN fill:#d4edda,stroke:#28a745
    style REFACTOR fill:#cce5ff,stroke:#007bff
```

Cada vuelta al ciclo dura entre 2 y 10 minutos. Si llevas más de 10 minutos sin ejecutar tests, tu paso es demasiado grande. Pártelo.

**Paso 1 — Red.** Escribes un test que describe un comportamiento que tu código todavía no tiene. Ejecutas el test. El test falla (se muestra en rojo en Xcode). Esto es esperado y deseable. El test falla porque el comportamiento no existe todavía. Si el test pasa sin que hayas escrito nada nuevo, algo está mal: o el test es incorrecto, o el comportamiento ya existía y no lo sabías.

**Paso 2 — Green.** Ahora escribes el código de producción **mínimo** para hacer que el test pase. Mínimo significa mínimo. No escribes "un poco más por si acaso". No anticipas funcionalidad futura. Solo escribes lo estrictamente necesario para que ese test concreto pase. Si el test dice que cuando recibo un email inválido debo devolver un error, implemento exactamente eso y nada más. Ejecutas el test. Pasa (se muestra en verde).

**Paso 3 — Refactor.** Con el test en verde, miras el código (tanto el de producción como el del test) y te preguntas: "¿hay algo que pueda mejorar?" ¿Hay duplicación? ¿Hay nombres poco claros? ¿Hay código que se puede simplificar? Si es así, lo mejoras. Después de cada cambio, ejecutas los tests para verificar que siguen en verde. Si un test se pone rojo durante el refactor, deshaces el último cambio y lo intentas de otra forma.

Después del refactor, vuelves al Paso 1 con el siguiente comportamiento. Y así sucesivamente hasta que todos los escenarios BDD están implementados.

### Un ejemplo concreto con XCTest para que quede claro

Vamos a ver cómo funciona TDD en la práctica con un ejemplo muy sencillo: el Value Object `Email`. Queremos que `Email` solo pueda crearse si el string tiene formato válido. Si el formato es inválido, queremos que lance un error.

**Iteración 1 — Red:** escribimos el primer test.

```swift
import XCTest

final class EmailTests: XCTestCase {
    func test_init_with_valid_email_creates_email_successfully() {
        let email = try? Email("user@example.com")
        
        XCTAssertNotNil(email)
        XCTAssertEqual(email?.value, "user@example.com")
    }
}
```

Ejecutamos. El test no compila porque `Email` no existe. Eso es el "rojo" en TDD: puede ser un fallo de compilación o un `XCTAssertEqual` que no se cumple. Ambos cuentan como rojo.

**Iteración 1 — Green:** implementamos lo mínimo.

```swift
struct Email: Equatable {
    let value: String
    
    init(_ rawValue: String) throws {
        self.value = rawValue
    }
}
```

Ejecutamos. El test pasa. ¿Es la implementación completa? No, ni de lejos. No valida nada. Pero el test que tenemos solo pide que se pueda crear un `Email` con un string válido, y eso funciona. Lo mínimo para que pase.

**Iteración 1 — Refactor:** ¿hay algo que mejorar? Todavía no, son dos líneas.

**Iteración 2 — Red:** ahora añadimos el comportamiento de rechazo.

```swift
func test_init_with_string_without_at_sign_throws_error() {
    XCTAssertThrowsError(try Email("invalid-email")) { error in
        XCTAssertEqual(error as? Email.ValidationError, .invalidFormat)
    }
}
```

Ejecutamos. Falla porque `Email.ValidationError` no existe y porque el `init` actual acepta cualquier string.

**Iteración 2 — Green:** añadimos la validación.

```swift
struct Email: Equatable {
    let value: String
    
    enum ValidationError: Error, Equatable {
        case invalidFormat
    }
    
    init(_ rawValue: String) throws {
        guard rawValue.contains("@") else {
            throw ValidationError.invalidFormat
        }
        self.value = rawValue
    }
}
```

Ejecutamos. Ambos tests pasan.

**Iteración 2 — Refactor:** la validación es muy básica (solo mira si hay una arroba), pero para estos dos tests es suficiente. Lo dejaremos así de momento. Si un test futuro necesita una validación más completa, el test nos lo pedirá.

**Iteración 3 — Red:** ¿y si el email está vacío?

```swift
func test_init_with_empty_string_throws_error() {
    XCTAssertThrowsError(try Email("")) { error in
        XCTAssertEqual(error as? Email.ValidationError, .invalidFormat)
    }
}
```

Ejecutamos. Pasa sin cambiar nada, porque un string vacío no contiene "@" y nuestra validación ya lo cubre. ¿Eso es bueno o malo? Es bueno: significa que la implementación ya cubre este caso. Pero el test tiene valor documental: deja explícito que un email vacío es inválido. Lo dejamos.

¿Ves el ritmo? Test que falla, implementación mínima, limpieza. Test que falla, implementación mínima, limpieza. Cada iteración dura entre 2 y 10 minutos. El feedback es inmediato. En ningún momento pasas más de unos minutos sin saber si tu código funciona o no.

### Lo que TDD te regala además de tests

Los tests son el resultado más visible de TDD, pero no el más importante. Lo más importante es lo que TDD hace por tu **diseño**:

Cuando un test es difícil de escribir, es una señal de que el componente que estás testeando tiene demasiadas responsabilidades o demasiadas dependencias. Si para testear un caso de uso necesitas montar un servidor HTTP, crear una base de datos, y configurar un sistema de navegación, el test te está gritando: "este componente depende de demasiadas cosas, sepáralo". Esa señal es oro puro. Si la escuchas y separas las responsabilidades, tu diseño mejora. Si la ignoras y hackeas el test para que funcione, acumulas deuda técnica.

Cuando necesitas muchos mocks o stubs complicados, es otra señal. Significa que tus dependencias son demasiado concretas o demasiado amplias. La solución no es usar un framework de mocking más potente, sino rediseñar las dependencias para que sean más simples y abstractas (protocolos estrechos con pocos métodos).

Cuando un test se rompe por un cambio que no debería afectarle, estás testeando implementación en vez de comportamiento. Un test que verifica "llama a esta función exactamente 3 veces" se rompe si cambias la implementación aunque el comportamiento sea el mismo. Un test que verifica "dado estas entradas, produce estas salidas" solo se rompe si el comportamiento cambia. Siempre prefiere testear entradas y salidas.

### Guía completa de Test Doubles: stubs, spies, mocks, fakes y dummies

Antes de seguir, necesitas entender un concepto fundamental que vas a usar en **cada test** del curso: los **test doubles**. Un test double es un objeto falso que sustituye a una dependencia real durante un test. Es como un actor de reparto que hace el papel de otro personaje en una escena de ensayo.

¿Por qué necesitas objetos falsos? Imagina que quieres testear el `LoginUseCase`. El UseCase necesita un `AuthGateway` para autenticar al usuario. El `AuthGateway` real llama a un servidor por internet. Si usaras el real en tus tests:

- Los tests **tardarían segundos** en vez de milisegundos (hay que esperar a la red).
- Los tests **fallarían sin internet** (no puedes testear en un avión o en el metro).
- Los tests **no serían deterministas**: a veces el servidor responde, a veces no, a veces tarda mucho.
- **No podrías controlar** qué responde el servidor. ¿Cómo testeas el escenario de "credenciales incorrectas" si el servidor decide que son correctas?

La solución es crear un **objeto falso** que se comporta como el `AuthGateway` real pero que tú controlas completamente. Ese objeto falso es un **test double**.

Hay 5 tipos de test doubles. Cada uno tiene un propósito diferente:

```mermaid
graph TD
    TD["Test Doubles<br/>Objetos falsos para tests"] --> DUMMY["Dummy<br/>No hace nada.<br/>Solo rellena un parametro."]
    TD --> STUB["Stub<br/>Devuelve datos fijos.<br/>Tu configuras que devuelve."]
    TD --> SPY["Spy<br/>Registra las llamadas.<br/>Puedes verificar que se llamo."]
    TD --> MOCK["Mock<br/>Verifica expectativas.<br/>Falla si no se cumple lo esperado."]
    TD --> FAKE["Fake<br/>Implementacion real simplificada.<br/>Funciona pero con atajos."]

    style DUMMY fill:#f8f9fa,stroke:#6c757d
    style STUB fill:#d4edda,stroke:#28a745
    style SPY fill:#cce5ff,stroke:#007bff
    style MOCK fill:#fff3cd,stroke:#ffc107
    style FAKE fill:#ffe0cc,stroke:#fd7e14
```

#### 1. Dummy (el maniquí)

Un **dummy** es un objeto que se pasa como parámetro pero que **nunca se usa realmente**. Existe solo para que el código compile. Es como un maniquí en una tienda de ropa: ocupa el espacio pero no hace nada.

```swift
// Ejemplo: necesitas pasar un Logger pero en este test no te importa el logging
struct DummyLogger: Logger {
    func log(_ message: String, level: LogLevel) {
        // No hace nada. Es un dummy.
    }
}

// Lo usas así en el test:
let useCase = LoginUseCase(gateway: stubGateway, logger: DummyLogger())
// El DummyLogger solo está ahí para que compile. No verificas nada sobre él.
```

**Cuándo usarlo:** Cuando un componente pide una dependencia que no es relevante para lo que estás testeando. Si estás testeando la lógica de login, el logger no importa, así que pasas un dummy.

#### 2. Stub (el actor con guión fijo)

Un **stub** es un objeto que **devuelve datos predefinidos** que tú configuras. Es como un actor que siempre dice la misma frase, sin importar qué le preguntes. Tú le dices "cuando te pidan autenticar, devuelve esta sesión" o "cuando te pidan autenticar, lanza este error".

```swift
// Ejemplo: un stub del AuthGateway
struct AuthGatewayStub: AuthGateway {
    // Tú configuras qué resultado devuelve:
    let result: Result<Session, Error>
    
    func authenticate(credentials: Credentials) async throws -> Session {
        // Siempre devuelve lo que tú le configuraste.
        // No llama a ningún servidor. No hace nada más.
        return try result.get()
    }
}

// En el test, lo usas así:
func test_login_exitoso_devuelve_session() async throws {
    // ARRANGE: configuro el stub para que devuelva éxito
    let sessionEsperada = Session(token: "abc123", email: "user@test.com")
    let stub = AuthGatewayStub(result: .success(sessionEsperada))
    let useCase = LoginUseCase(gateway: stub)
    
    // ACT: ejecuto el caso de uso
    let resultado = try await useCase.execute(email: "user@test.com", password: "Pass1234")
    
    // ASSERT: verifico que me devolvió la sesión del stub
    XCTAssertEqual(resultado, sessionEsperada)
}
```

**Cuándo usarlo:** Cuando necesitas **controlar qué datos recibe** el componente que estás testeando. El stub es el test double más común. Lo usarás en casi todos los tests del curso.

**La clave del stub:** tú decides de antemano qué devuelve. No verifica si fue llamado o no. Solo devuelve lo que tú le dijiste.

#### 3. Spy (el espía que toma notas)

Un **spy** es un stub que además **registra las llamadas que recibe**. Es como un espía que devuelve la respuesta correcta pero también apunta en su libreta: "me llamaron con estos parámetros, a esta hora, tantas veces".

```swift
// Ejemplo: un spy del AuthGateway
final class AuthGatewaySpy: AuthGateway, @unchecked Sendable {
    let result: Result<Session, Error>
    
    // El spy registra las llamadas:
    private(set) var authenticateCallCount = 0
    private(set) var receivedCredentials: [Credentials] = []
    
    init(result: Result<Session, Error>) {
        self.result = result
    }
    
    func authenticate(credentials: Credentials) async throws -> Session {
        // Registra que fue llamado:
        authenticateCallCount += 1
        receivedCredentials.append(credentials)
        
        // Y devuelve lo configurado (como un stub):
        return try result.get()
    }
}

// En el test, verificas que se llamó correctamente:
func test_usecase_envia_credenciales_al_gateway() async throws {
    // ARRANGE
    let session = Session(token: "abc", email: "user@test.com")
    let spy = AuthGatewaySpy(result: .success(session))
    let useCase = LoginUseCase(gateway: spy)
    
    // ACT
    _ = try await useCase.execute(email: "user@test.com", password: "Pass1234")
    
    // ASSERT: verifico que el gateway fue llamado exactamente 1 vez
    XCTAssertEqual(spy.authenticateCallCount, 1)
    // Y que recibió las credenciales correctas
    XCTAssertEqual(spy.receivedCredentials.first?.email.value, "user@test.com")
}
```

**Cuándo usarlo:** Cuando además de controlar la respuesta, necesitas **verificar que la llamada se hizo correctamente**. Por ejemplo: verificar que el UseCase NO llama al gateway cuando el email es inválido.

**En este curso, la mayoría de nuestros "stubs" son en realidad spies**: devuelven datos configurados Y registran las llamadas. Usamos el nombre "stub" por simplicidad, pero técnicamente son spies.

#### 4. Mock (el verificador estricto)

Un **mock** es un spy que además **verifica automáticamente que se cumplieron sus expectativas**. Es como un juez que no solo observa sino que dicta sentencia: "esperaba que me llamaran exactamente 2 veces con estos parámetros, y no fue así, así que el test falla".

```swift
// Ejemplo conceptual de un mock (NO lo usamos en este curso):
let mock = MockAuthGateway()
mock.expect(.authenticate, calledTimes: 1, withArguments: credentials)

// Después de ejecutar el código...
mock.verify() // Si no se cumplieron las expectativas, el test falla automáticamente
```

**Cuándo usarlo:** En frameworks de mocking como OCMock o Mockito (en Android). En Swift puro con XCTest, **no usamos mocks en este sentido**. Usamos spies + asserts manuales, que es más claro y más fácil de depurar. Si un spy tiene un `assert` manual que verifica la llamada, logra lo mismo que un mock pero de forma más explícita.

**En resumen: en este curso NO usamos mocks.** Usamos stubs y spies con asserts manuales. Esto es una decisión deliberada: los mocks automáticos hacen que los tests sean más difíciles de leer y de depurar cuando fallan.

#### 5. Fake (la implementación simplificada)

Un **fake** es una implementación real pero simplificada. No es un objeto que "finge" como un stub. Es un objeto que realmente funciona, pero con atajos. Es como un restaurante de mentira que realmente cocina pero solo tiene 3 platos en el menú.

```swift
// Ejemplo: un fake de ProductStore que usa memoria en vez de disco
struct InMemoryProductStore: ProductStore {
    private var products: [Product] = []
    
    mutating func save(_ products: [Product]) {
        self.products = products // Guarda en memoria, no en disco
    }
    
    func loadAll() -> [Product] {
        return products // Lee de memoria, no de disco
    }
}
```

**Cuándo usarlo:** En **tests de integración** donde necesitas que la dependencia realmente funcione pero no quieres la complejidad de la implementación real. Un `InMemoryProductStore` funciona como el `FileProductStore` real pero sin tocar el disco, lo que hace los tests más rápidos y sin efectos secundarios.

#### Resumen visual: cuándo usar cada uno

```mermaid
graph TD
    Q["Que necesito en el test?"] --> Q1{"Necesito controlar<br/>que devuelve?"}
    Q1 -->|"NO"| DUMMY["Usa un DUMMY<br/>Solo rellena parametro"]
    Q1 -->|"SI"| Q2{"Necesito verificar<br/>que se llamo?"}
    Q2 -->|"NO"| STUB["Usa un STUB<br/>Devuelve datos fijos"]
    Q2 -->|"SI"| SPY["Usa un SPY<br/>Registra llamadas + devuelve datos"]

    Q -->  Q3{"Necesito una impl.<br/>real simplificada?"}
    Q3 -->|"SI"| FAKE["Usa un FAKE<br/>Implementacion ligera"]

    style DUMMY fill:#f8f9fa,stroke:#6c757d
    style STUB fill:#d4edda,stroke:#28a745
    style SPY fill:#cce5ff,stroke:#007bff
    style FAKE fill:#ffe0cc,stroke:#fd7e14
```

**Regla práctica para este curso:** el 90% de las veces usarás un **spy** (que incluye la funcionalidad de stub). El 10% restante será un **fake** para tests de integración. Los dummies los usarás ocasionalmente. Los mocks automáticos, nunca.

### La regla de un test a la vez

Una tentación muy común, sobre todo al principio, es escribir todos los tests de golpe ("ya sé todos los escenarios, los escribo todos y luego implemento"). Esto rompe el ciclo TDD y tiene varias consecuencias negativas:

Pierdes el feedback incremental. Si tienes 7 tests rojos, no sabes cuál abordar primero ni cuánto te falta.

Tiendes a sobre-implementar. En lugar de lo mínimo para un test, implementas "lo mínimo para 7 tests", que es mucho más código de golpe y mucho más difícil de depurar si algo falla.

Pierdes la oportunidad de que cada test guíe el diseño. El test 3 podría revelar que necesitas cambiar el diseño que hiciste en el test 2. Si implementaste los 7 de golpe, el cambio es mucho más costoso.

La disciplina es: un test a la vez. Escríbelo, ponlo en rojo, implementa lo mínimo, ponlo en verde, refactoriza, y **solo entonces** pasa al siguiente test.

---

## Cómo conviven BDD y TDD en el flujo real del curso

Ahora que entiendes ambas prácticas por separado, vamos a ver cómo se combinan en el flujo que seguiremos cada vez que construyamos una feature. Este flujo tiene siete pasos, siempre en el mismo orden:

### Diagrama: el flujo completo BDD → TDD

```mermaid
flowchart TD
    S1["1. Especificacion BDD<br/>Escenarios Given/When/Then"] --> S2["2. Decisiones de dominio<br/>Value Objects, Errores, Eventos"]
    S2 --> S3["3. Diseno de contratos<br/>Protocolos - puertos"]
    S3 --> S4["4. TDD en Domain<br/>Value Objects + Tests"]
    S4 --> S5["5. TDD en Application<br/>Use Cases + Tests con stubs"]
    S5 --> S6["6. Infrastructure<br/>Gateways reales + Contract tests"]
    S6 --> S7["7. Interface SwiftUI<br/>ViewModel + View"]

    S1 -.->|"Sin codigo"| S3
    S4 -.->|"Con TDD"| S7

    style S1 fill:#f8f9fa,stroke:#6c757d
    style S2 fill:#f8f9fa,stroke:#6c757d
    style S3 fill:#f8f9fa,stroke:#6c757d
    style S4 fill:#d4edda,stroke:#28a745
    style S5 fill:#cce5ff,stroke:#007bff
    style S6 fill:#fff3cd,stroke:#ffc107
    style S7 fill:#ffe0cc,stroke:#fd7e14
```

Fíjate en la dirección: **del centro hacia fuera**. Domain primero (las reglas puras), luego Application (la orquestación), luego Infrastructure (la conexión con el mundo real), y finalmente Interface (lo que ve el usuario). Esta dirección no es arbitraria — es lo que garantiza que cada capa sea testeable de forma independiente.

### Diagrama: dirección de implementación (del core hacia fuera)

```mermaid
graph LR
    subgraph CORE["Core - sin dependencias"]
        DOMAIN["Domain<br/>Email, Password<br/>AuthGateway protocol"]
    end
    
    subgraph MIDDLE["Orquestacion"]
        APP["Application<br/>LoginUseCase"]
    end
    
    subgraph EDGE["Periferia - dependencias reales"]
        INFRA["Infrastructure<br/>RemoteAuthGateway"]
        UI["Interface<br/>LoginView"]
    end

    DOMAIN --> APP
    APP --> INFRA
    APP --> UI
    
    style CORE fill:#d4edda,stroke:#28a745
    style MIDDLE fill:#cce5ff,stroke:#007bff
    style EDGE fill:#fff3cd,stroke:#ffc107
```

Las flechas apuntan hacia fuera: el Domain no sabe nada de Application. Application no sabe nada de Infrastructure ni de Interface. Solo el Composition Root (que veremos en la Etapa 2) conoce todas las piezas y las conecta. Esta es la **Dependency Rule** de Clean Architecture: las dependencias siempre apuntan hacia adentro, nunca hacia fuera.

**Paso 1: Especificación BDD.** Escribimos todos los escenarios de la feature (happy path, sad path, edge cases). Esto se hace en un documento Markdown, no en código. El resultado es la lista completa de comportamientos que el sistema debe soportar.

**Paso 2: Decisiones de dominio.** De los escenarios extraemos las decisiones de diseño: qué Value Objects necesitamos, qué errores existen, qué eventos se emiten, qué invariantes debe respetar el dominio. Todavía no escribimos código, pero ya sabemos qué piezas necesitamos.

**Paso 3: Diseño de contratos.** Definimos los protocolos (puertos) que el caso de uso necesita para comunicarse con el mundo exterior, y los modelos del dominio. Este paso es diseño sobre papel (o en nuestra cabeza), no implementación.

**Paso 4: TDD en Domain.** Empezamos a implementar con TDD, desde el core hacia fuera. Primero los Value Objects y los tipos de dominio. Tests unitarios puros con XCTest, sin dependencias externas. Cada test sigue el ciclo Red-Green-Refactor.

**Paso 5: TDD en Application.** Con el dominio listo, implementamos los casos de uso con TDD. Los tests unitarios usan dobles (stubs) de los puertos para aislar el caso de uso de la infraestructura. Verificamos que el caso de uso orquesta correctamente: valida, delega, traduce errores.

**Paso 6: Infrastructure.** Implementamos las versiones concretas de los puertos (gateway de red, repositorio de persistencia). Escribimos contract tests que verifican que la implementación cumple el contrato del protocolo: dado un input, produce el output esperado.

**Paso 7: Interface (SwiftUI).** Conectamos la UI con el caso de uso a través de un ViewModel. Tests mínimos de aceptación para los criterios más críticos. La vista no contiene lógica de negocio.

Cada uno de estos pasos se explica en profundidad en las lecciones de la Feature Login. Por ahora, lo importante es que entiendas el orden y la lógica: BDD primero para saber qué construir, luego TDD desde el core hacia fuera para construirlo con seguridad.

### La dirección importa: del core hacia fuera

Fíjate en que el orden de implementación va del centro hacia la periferia: Domain primero, luego Application, luego Infrastructure, luego Interface. Esto no es casualidad. Tiene una razón de diseño fundamental.

Si empiezas por la UI ("primero voy a montar la pantalla y luego ya veré cómo la conecto"), tiendes a diseñar todo desde la perspectiva de la vista. El ViewModel se convierte en un cajón de sastre que hace de todo, la lógica de negocio se dispersa, y cuando quieres testear algo, necesitas montar toda la UI.

Si empiezas por el dominio, diseñas las reglas de negocio de forma pura, sin ninguna dependencia de UI ni de red. Luego el caso de uso orquesta esas reglas sin saber nada de SwiftUI. Luego la infraestructura implementa los puertos sin saber nada de la vista. Y al final, la vista simplemente consume lo que ya existe. Cada capa se construye sobre la anterior, y cada capa es testeable de forma independiente.

---

## Lo que NO es BDD y lo que NO es TDD

Hay muchas confusiones comunes sobre ambas prácticas. Vamos a aclararlas para que no arrastres ideas incorrectas:

**BDD no es "escribir Gherkin".** Gherkin es un formato (Given/When/Then). BDD es una práctica de descubrimiento y especificación. Puedes hacer BDD perfectamente escribiendo los escenarios en un documento de texto sin ningún formato especial. Lo que importa es el proceso de pensar y capturar los comportamientos, no el formato en que los escribes. En este curso usaremos Given/When/Then porque es claro y universal, pero no usaremos herramientas como Cucumber ni automatizaremos los escenarios Gherkin. Los escenarios BDD nos sirven como especificación que luego traducimos manualmente a tests XCTest.

**TDD no es "tener tests".** Puedes tener un proyecto con 500 tests y no haber hecho TDD en ningún momento. TDD es un ciclo de desarrollo específico (Red-Green-Refactor) donde el test se escribe antes de la implementación. Si escribes la implementación primero y luego le añades tests, estás haciendo "test-after", que tiene valor (mejor que no tener tests), pero no guía el diseño de la misma forma.

**TDD no es "testear todo obsesivamente".** No todo necesita un test unitario. Los tests triviales (getters que devuelven una propiedad, por ejemplo) no aportan valor. TDD te lleva a testear **comportamientos**, no líneas de código. Si un comportamiento es tan simple que no puede fallar, no necesita test.

**BDD y TDD no son mutuamente excluyentes.** No es "o BDD o TDD". En este curso usamos ambos, en ese orden: BDD para especificar, TDD para implementar. Son complementarios, no competidores.

---

**Anterior:** [Metodología BDD: especificación y descubrimiento ←](02-metodologia-bdd-tdd.md) · **Siguiente:** [Stack tecnológico →](03-stack-tecnologico.md)
