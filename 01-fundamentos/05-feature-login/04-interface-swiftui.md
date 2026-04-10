# Feature Login: Capa Interface (SwiftUI)

## La última capa: donde el usuario ve y toca

Hemos construido las tres capas internas de la feature Login: el Domain con sus Value Objects y errores tipados, la Application con el caso de uso y el puerto, y la Infrastructure con el gateway real y el stub. Todo testeado con XCTest, todo desacoplado, todo siguiendo los escenarios BDD.

Ahora llegamos a la capa más externa: la Interface. Esta es la capa que el usuario ve y con la que interactúa. Contiene dos componentes: el **ViewModel** que adapta los datos del caso de uso al formato que la UI necesita, y la **Vista SwiftUI** que muestra esos datos y recoge las acciones del usuario.

La regla fundamental de esta capa es: **no contiene lógica de negocio**. La vista no valida emails. No decide si el login fue exitoso. No traduce errores. Solo muestra lo que el ViewModel le dice y envía las acciones del usuario al ViewModel. Es la capa más "tonta" del sistema, y eso es exactamente lo que queremos.

> **Nota de equivalencias con el scaffold:** Los nombres de esta lección coinciden exactamente con el scaffold `apps/ios/ArchitectureKit` (`LoginViewModel`, `LoginView`, `AuthenticateUserUseCase`, `LoginError`, `UserSession`). Las diferencias son de **implementación**, no de nomenclatura: el scaffold usa `@Observable @MainActor` con un enum `Phase` (`.idle`, `.loading`, `.authenticated`) en lugar de `isLoading: Bool`, y `@Bindable` en la View. El Checkpoint Xcode al final de esta lección explica cada diferencia en detalle.

### Recordatorio de principios

Aquí reaparece el **Principio 4** de [Principios de ingeniería](../01-principios-ingenieria.md): la UI se mantiene cohesionada en presentación y desacoplada del core de negocio.

---

## Diagrama: cómo fluyen los datos entre Vista y ViewModel

```mermaid
sequenceDiagram
    participant User as Usuario
    participant View as LoginView
    participant VM as LoginViewModel
    participant UC as AuthenticateUserUseCase

    User->>View: Escribe email
    View->>VM: email = user@test.com Bindable
    
    User->>View: Escribe password
    View->>VM: password = "Pass1234"
    
    User->>View: Pulsa "Iniciar sesión"
    View->>VM: await submit()
    
    VM->>VM: isLoading = true, errorMessage = nil
    Note over View: SwiftUI detecta cambio<br/>muestra ProgressView
    
    VM->>UC: await execute email, password
    
    alt Login exitoso
        UC-->>VM: UserSession token abc
        VM->>VM: navigator?.goToCatalog()
        Note over View: Navegacion delegada<br/>al coordinator via LoginNavigating
    end
    
    alt Login fallido
        UC-->>VM: throws error
        VM->>VM: errorMessage = Email invalido
        VM->>VM: isLoading = false
        Note over View: SwiftUI detecta cambio<br/>muestra error en rojo
    end
```

La vista **no sabe nada** de `AuthenticateUserUseCase`, ni de `AuthRepository`, ni de `EmailAddress`, ni de `Password`. Solo conoce strings (`email`, `password`, `errorMessage`) y booleans (`isLoading`). **Esa es la separación de responsabilidades en acción.**

### Diagrama: qué sabe cada componente

```mermaid
graph TD
    subgraph View["LoginView - lo que ve el usuario"]
        V1["Sabe: email, password, isLoading, errorMessage"]
        V2["NO sabe: como se valida un email"]
        V3["NO sabe: que es AuthRepository"]
        V4["NO sabe: a donde navegar despues"]
    end

    subgraph ViewModel["LoginViewModel - el puente"]
        VM1["Sabe: AuthenticateUserUseCase, estado de la UI"]
        VM2["NO sabe: como se autentica"]
        VM3["NO sabe: que vista lo muestra"]
    end

    subgraph UseCase["AuthenticateUserUseCase - la logica"]
        UC1["Sabe: validar y delegar"]
        UC2["NO sabe: quien lo llama"]
        UC3["NO sabe: que pasa con el resultado"]
    end

    View --> ViewModel --> UseCase

    style View fill:#ffe0cc,stroke:#fd7e14
    style ViewModel fill:#cce5ff,stroke:#007bff
    style UseCase fill:#d4edda,stroke:#28a745
```

---

## El LoginViewModel

El ViewModel es el puente entre el caso de uso y la vista. Su responsabilidad es triple: almacenar el estado que la vista necesita mostrar (email, password, loading, error), invocar el caso de uso cuando el usuario pulsa el botón, y traducir el resultado del caso de uso a un formato que la vista pueda mostrar directamente (strings de error, flags booleanos).

```swift
// StackMyArchitecture/Features/Login/Interface/LoginNavigating.swift

protocol LoginNavigating: AnyObject {
    @MainActor func goToCatalog()
}
```

```swift
// StackMyArchitecture/Features/Login/Interface/LoginViewModel.swift

import SwiftUI

@Observable
@MainActor
final class LoginViewModel {
    var email = ""
    var password = ""
    var isLoading = false
    var errorMessage: String?
    
    private let useCase: AuthenticateUserUseCase
    private weak var navigator: (any LoginNavigating)?
    
    init(
        useCase: AuthenticateUserUseCase,
        navigator: any LoginNavigating
    ) {
        self.useCase = useCase
        self.navigator = navigator
    }
    
    func submit() async {
        isLoading = true
        errorMessage = nil
        
        do {
            _ = try await useCase.execute(email: email, password: password)
            navigator?.goToCatalog()
        } catch let error as LoginError {
            errorMessage = Self.message(for: error)
        } catch {
            errorMessage = "Error inesperado. Inténtalo de nuevo."
        }
        
        isLoading = false
    }
    
    private static func message(for error: LoginError) -> String {
        switch error {
        case .invalidEmail:
            return "El email no tiene un formato válido."
        case .emptyPassword:
            return "La contraseña no puede estar vacía."
        case .invalidCredentials:
            return "Email o contraseña incorrectos."
        case .connectivity:
            return "Sin conexión a internet. Inténtalo de nuevo."
        }
    }
}
```

**Explicación línea por línea del LoginViewModel completo:**

`import SwiftUI` — Necesitamos SwiftUI porque el ViewModel usa la macro `@Observable` que pertenece al framework Observation (parte de SwiftUI). Este es el único archivo de la feature Login que importa SwiftUI (aparte de la vista). El Domain, la Application, y la Infrastructure no importan SwiftUI.

`@Observable` — Esta macro de Swift 5.9 le dice a SwiftUI: "observa las propiedades de este objeto y cuando alguna cambie, actualiza las partes de la vista que la leen". Sin `@Observable`, SwiftUI no sabría cuándo re-renderizar la vista. Con `@Observable`, SwiftUI detecta automáticamente qué propiedad leyó cada parte de la vista, y solo actualiza esa parte cuando esa propiedad cambia. Es mucho más eficiente que el antiguo `ObservableObject` + `@Published`.

`@MainActor` — Esto garantiza que **todo el código de esta clase** se ejecuta en el hilo principal (main thread). ¿Por qué es necesario? Porque las propiedades del ViewModel (`email`, `password`, `isLoading`, `errorMessage`) son leídas por SwiftUI para renderizar la vista. SwiftUI exige que las mutaciones de estado de UI ocurran en el main thread. Si cambiaras `isLoading` desde un hilo de background, la app podría crashear o mostrar datos corruptos. `@MainActor` previene eso automáticamente.

`final class` — Usamos `class` (no `struct`) porque: (1) `@Observable` solo funciona con clases, y (2) el ViewModel tiene identidad (es un objeto único que la vista observa, no un valor que se copia). `final` significa que nadie puede heredar de esta clase.

`var email = ""` — El email que el usuario escribe en el TextField. Es `var` (mutable) porque SwiftUI lo modifica a través de bindings cuando el usuario teclea. Empieza vacío.

`var password = ""` — Lo mismo para el password.

`var isLoading = false` — Indica si hay una petición en curso. Cuando es `true`, la vista muestra un spinner y deshabilita el botón. Empieza en `false` porque cuando abres la pantalla, no hay ninguna petición en curso.

`var errorMessage: String?` — El mensaje de error que se muestra al usuario. Es `Optional` (`String?`) porque la mayor parte del tiempo no hay error (es `nil`). Solo tiene valor cuando algo falla.

`private let useCase: AuthenticateUserUseCase` — La dependencia del UseCase. Es `private` porque nadie fuera del ViewModel necesita acceder al UseCase. Es `let` (constante) porque no cambia después de la creación.

`private weak var navigator: (any LoginNavigating)?` — La dependencia de navegación. Es `weak` porque el coordinador (que implementa `LoginNavigating`) es dueño del ViewModel a través del Composition Root — tenerlo `strong` crearía un ciclo de retención. El tipo `any LoginNavigating` permite inyectar cualquier objeto que conforme el protocolo: el coordinador real en producción, o un `LoginNavigatorSpy` en tests.

**El método `submit()` paso a paso:**

```mermaid
flowchart TD
    START["Usuario pulsa Submit"] --> LOADING["isLoading = true<br/>errorMessage = nil"]
    LOADING --> TRY["try await login.execute<br/>email, password"]
    TRY -->|"Exito"| SUCCESS["navigator?.goToCatalog()<br/>Navega a la siguiente pantalla"]
    TRY -->|"LoginError"| KNOWN["errorMessage = mensaje especifico<br/>Email invalido / Password vacio /<br/>Credenciales incorrectas / Sin conexion"]
    TRY -->|"Otro error"| UNKNOWN["errorMessage = Error inesperado"]
    SUCCESS --> DONE["isLoading = false"]
    KNOWN --> DONE
    UNKNOWN --> DONE

    style START fill:#cce5ff,stroke:#007bff
    style SUCCESS fill:#d4edda,stroke:#28a745
    style KNOWN fill:#f8d7da,stroke:#dc3545
    style UNKNOWN fill:#f8d7da,stroke:#dc3545
```

`isLoading = true` — Lo primero que hace submit: pone el loading en true. SwiftUI detecta el cambio y muestra el spinner automáticamente.

`errorMessage = nil` — Limpia cualquier error previo. Si el usuario vio "Email inválido", corrigió el email, y volvió a pulsar submit, no queremos que el error anterior siga visible mientras se procesa la nueva petición.

`do { let session = try await login.execute(...) }` — Ejecuta el UseCase. `try` porque puede lanzar errores. `await` porque es asíncrono (el UseCase llama al gateway que simula una petición de red). Si todo va bien, `session` contiene la sesión del servidor.

`navigator?.goToCatalog()` — Si llegamos aquí, el login fue exitoso. Llamamos al navigator para que realice la navegación. El navigator (`any LoginNavigating`) no sabe nada de HTTP ni de Domain; solo sabe navegar. En producción será el coordinador. En tests, un spy que registra si se llamó.

`catch let error as LoginError` — Si el UseCase lanzó un error, lo capturamos y verificamos si es un `LoginError` (un error conocido y tipado). `as` intenta convertir el error genérico al tipo específico. Si la conversión funciona, entramos en este bloque.

`Self.message(for: error)` — Traducimos el error de negocio a un string legible por humanos. `Self` (con S mayúscula) se refiere al tipo `LoginViewModel`, no a la instancia `self`.

`catch { errorMessage = "Error inesperado..." }` — Si el error NO es un `LoginError` (por ejemplo, un error del sistema que no anticipamos), mostramos un mensaje genérico. Este `catch` sin tipo es el "catch-all" de Swift: captura cualquier error que no fue capturado por los `catch` anteriores.

`isLoading = false` — Siempre, sin importar si el login fue exitoso o falló, ponemos isLoading en false. El spinner desaparece. Fíjate en que esta línea está **fuera** del `do/catch`, así que se ejecuta en todos los casos.

Vamos a analizar cada decisión de diseño:

### Por qué `@Observable` y no `ObservableObject`

`@Observable` es la macro introducida en Swift 5.9 (iOS 17) que reemplaza al protocolo `ObservableObject` con `@Published`. La diferencia principal es la granularidad de las actualizaciones. Con `ObservableObject`, cualquier cambio en cualquier `@Published` property invalida todas las vistas que observan el objeto, aunque solo una propiedad haya cambiado. Con `@Observable`, SwiftUI sabe exactamente qué propiedad leyó cada vista, y solo invalida las vistas que leen la propiedad que cambió.

En nuestro caso, si solo cambia `isLoading`, solo se re-renderiza la parte de la vista que lee `isLoading`. El `TextField` del email no se toca porque no lee `isLoading`. Esto es más eficiente, pero sobre todo es el enfoque moderno que Apple recomienda. No hay razón para usar `ObservableObject` en código nuevo.

### Por qué `@MainActor`

El ViewModel muta propiedades (`email`, `password`, `isLoading`, `errorMessage`) que SwiftUI observa. SwiftUI requiere que las mutaciones de estado que afectan a la UI ocurran en el hilo principal. Si mutas `isLoading` desde un hilo de background, SwiftUI puede crashear o comportarse de forma errática.

`@MainActor` garantiza que todas las mutaciones del ViewModel ocurren en el main thread. No necesitas hacer `DispatchQueue.main.async` manualmente. Swift Concurrency se encarga de ejecutar el código del ViewModel en el main actor automáticamente.

Recuerda la regla del curso: `@MainActor` está justificado aquí porque el ViewModel genuinamente necesita ejecutarse en el main thread (muta estado de UI). No lo estamos usando para silenciar warnings.

### Por qué usamos el protocolo `LoginNavigating`

Cuando el login es exitoso, el ViewModel llama a `navigator?.goToCatalog()`. El protocolo `LoginNavigating` define el contrato de navegación: el ViewModel dice "navega al catálogo" sin saber qué coordinador o vista se encarga de ello.

Esto es la navegación por contrato. La feature Login es completamente independiente de lo que ocurre después. Si mañana quieres que después del login se vaya a una pantalla de onboarding en lugar de Catalog, implementas otro `LoginNavigating` en el Composition Root. Login no se entera. Además, el patrón de protocolo (en lugar de closure) hace la intención explícita y testeable con un simple spy.

### Por qué la traducción de errores a strings está en el ViewModel

El método `message(for:)` traduce cada caso de `LoginError` a un string legible por el usuario. Esta traducción vive en el ViewModel porque es una responsabilidad de **presentación**, no de negocio. El Domain sabe que las credenciales son inválidas. La Application sabe que eso es un `LoginError.invalidCredentials`. Pero el texto "Email o contraseña incorrectos." es un detalle de presentación que solo le importa a la UI.

Si el día de mañana necesitas localizar la app a otros idiomas, solo cambias estos strings en el ViewModel (o los mueves a un sistema de localización). Ni el Domain ni la Application cambian.

---

## La LoginView

La vista SwiftUI es el componente más simple de toda la feature. No tiene lógica. Solo layout y bindings.

```swift
// StackMyArchitecture/Features/Login/Interface/LoginView.swift

import SwiftUI

struct LoginView: View {
    @State private var viewModel: LoginViewModel
    
    init(viewModel: LoginViewModel) {
        _viewModel = State(wrappedValue: viewModel)
    }
    
    var body: some View {
        Form {
            Section {
                TextField("Email", text: $viewModel.email)
                    .textContentType(.emailAddress)
                    .autocorrectionDisabled()
                    .textInputAutocapitalization(.never)
                    .keyboardType(.emailAddress)
                
                SecureField("Contraseña", text: $viewModel.password)
                    .textContentType(.password)
            }
            
            if let error = viewModel.errorMessage {
                Section {
                    Text(error)
                        .foregroundStyle(.red)
                        .font(.callout)
                }
            }
            
            Section {
                Button {
                    Task { await viewModel.submit() }
                } label: {
                    if viewModel.isLoading {
                        ProgressView()
                            .frame(maxWidth: .infinity)
                    } else {
                        Text("Iniciar sesión")
                            .frame(maxWidth: .infinity)
                    }
                }
                .disabled(viewModel.isLoading || viewModel.email.isEmpty || viewModel.password.isEmpty)
            }
        }
        .navigationTitle("Login")
    }
}
```

Vamos a repasar cada parte:

**Los TextFields.** El `TextField` del email tiene configuraciónes que mejoran la experiencia del usuario: `textContentType(.emailAddress)` activa el autocompletado del teclado, `textInputAutocapitalization(.never)` desactiva la mayúscula inicial (los emails no empiezan por mayúscula), y `keyboardType(.emailAddress)` muestra el teclado con arroba. El `SecureField` oculta los caracteres del password. Estos son detalles de UX que no afectan a la lógica, pero que hacen la diferencia entre una app amateur y una profesional.

**El binding.** `$viewModel.email` y `$viewModel.password` son bindings bidireccionales: cuando el usuario escribe, el ViewModel se actualiza automáticamente, y cuando el ViewModel cambia (por ejemplo, al limpiar un error), la vista se actualiza también. Esto es la magia de SwiftUI + `@Observable`: el flujo de datos es declarativo y automático.

**El manejo de errores.** Si `viewModel.errorMessage` no es `nil`, se muestra un texto rojo. Cuando el usuario pulsa submit de nuevo, el ViewModel limpia el error (`errorMessage = nil`) antes de hacer la llamada. Si la llamada falla, se muestra el nuevo error.

**El botón de submit.** El botón lanza un `Task` que ejecuta `viewModel.submit()`. ¿Por qué un `Task`? Porque `submit()` es `async` (hace una petición de red a través del caso de uso), pero el closure del `Button` es síncrono. El `Task` crea un contexto async dentro del closure síncrono. El botón se deshabilita cuando `isLoading` es `true` para evitar que el usuario pulse dos veces.

**El `@State` wrapping del ViewModel.** Fíjate en que el ViewModel se declara como `@State private var viewModel`. Esto es necesario porque con `@Observable`, SwiftUI necesita "poseer" el objeto para observar sus cambios. El `init` recibe el ViewModel y lo envuelve en `State`. Esta es la forma idiomática de inyectar un `@Observable` ViewModel en una vista SwiftUI.

---

## Tests del ViewModel

El ViewModel se puede testear sin UI, sin SwiftUI, sin renderizar nada. Solo necesitamos un stub del caso de uso y verificar que el ViewModel actualiza su estado correctamente.

Pero hay un detalle: el ViewModel depende de `AuthenticateUserUseCase`, que es un struct (no un protocolo). ¿Cómo lo stubbeamos? No necesitamos stubear el UseCase directamente. `AuthenticateUserUseCase` depende de `AuthRepository` (que sí es un protocolo), así que inyectamos un `AuthRepositoryStub` en el caso de uso y controlamos el comportamiento desde ahí. Es como una cadena: controlamos el stub del gateway, el gateway controla lo que hace el UseCase, y el UseCase controla lo que hace el ViewModel.

```mermaid
graph LR
    TEST["Test"] -.->|"crea y configura"| STUB["AuthRepositoryStub<br/>tu decides que devuelve"]
    STUB -.->|"se inyecta en"| UC["AuthenticateUserUseCase"]
    UC -.->|"se inyecta en"| VM["LoginViewModel<br/>el SUT"]

    style TEST fill:#cce5ff,stroke:#007bff
    style STUB fill:#d4edda,stroke:#28a745
    style UC fill:#fff3cd,stroke:#ffc107
    style VM fill:#ffe0cc,stroke:#fd7e14
```

```swift
// StackMyArchitectureTests/Features/Login/Interface/LoginViewModelTests.swift

import XCTest
@testable import StackMyArchitecture

// MARK: - Test Doubles

final class LoginNavigatorSpy: LoginNavigating {
    private(set) var goToCatalogCallCount = 0
    func goToCatalog() { goToCatalogCallCount += 1 }
}

@MainActor
final class LoginViewModelTests: XCTestCase {
    
    // MARK: - Helpers
    
    private func makeSUT(
        gatewayResult: Result<UserSession, LoginError> = .success(UserSession(token: "t", email: "e"))
    ) -> (sut: LoginViewModel, repository: AuthRepositoryStub, navigator: LoginNavigatorSpy) {
        let gateway = AuthRepositoryStub(result: gatewayResult)
        let useCase = AuthenticateUserUseCase(repository: gateway)
        let navigator = LoginNavigatorSpy()
        let sut = LoginViewModel(useCase: useCase, navigator: navigator)
        return (sut, gateway, navigator)
    }
```

**Explicación del makeSUT del ViewModel:**

`@MainActor final class LoginViewModelTests` — Toda la clase de tests está marcada con `@MainActor`. ¿Por qué? Porque el ViewModel que testeamos es `@MainActor`, y para acceder a sus propiedades necesitamos estar en el mismo actor. Sin este atributo, los tests no compilarían.

`gatewayResult: Result<UserSession, LoginError> = .success(...)` — El primer parámetro del makeSUT te permite configurar qué devuelve el gateway. Si no pasas nada, devuelve éxito por defecto. Esto simplifica los tests que no se preocupan por el resultado del gateway (como el test del estado inicial).

`LoginNavigatorSpy()` — El spy de navegación. Es un doble de test que implementa `LoginNavigating` y registra cuántas veces se llamó a `goToCatalog()`. Al devolver `navigator` en la tupla, cada test puede verificar si la navegación fue disparada.

Dentro de makeSUT, se crean cuatro componentes: stub → useCase → spy → viewModel. Cada uno se inyecta en el siguiente.

```swift
    // MARK: - Initial State
    
    func test_init_starts_with_empty_fields_and_no_error() {
        let (sut, _, _) = makeSUT()
        
        XCTAssertEqual(sut.email, "")
        XCTAssertEqual(sut.password, "")
        XCTAssertFalse(sut.isLoading)
        XCTAssertNil(sut.errorMessage)
    }
```

**Explicación del test de estado inicial:**

Este test verifica que cuando creas un ViewModel nuevo, su estado es correcto: email vacío, password vacío, no está cargando, y no hay ningún mensaje de error. Parece trivial, pero documenta un requisito: "cuando el usuario abre la pantalla de Login, no debe ver ningún error ni estado de carga". Si alguien cambiara accidentalmente el valor inicial de `isLoading` a `true`, este test lo detectaría inmediatamente.

`let (sut, _, _) = makeSUT()` — Creamos el ViewModel. El `_` descarta el gateway porque en este test no nos importa (no vamos a llamar a submit, así que el gateway no se usa). Usamos los valores por defecto de makeSUT.

`XCTAssertFalse(sut.isLoading)` — Verifica que `isLoading` es `false`. Es como `XCTAssertEqual(sut.isLoading, false)` pero más legible.

`XCTAssertNil(sut.errorMessage)` — Verifica que no hay ningún mensaje de error. `nil` en Swift significa "no tiene valor" o "está vacío".

```swift
    // MARK: - Happy Path
    
    func test_submit_with_valid_credentials_navigates_to_catalog() async {
        let (sut, _, navigator) = makeSUT(
            gatewayResult: .success(UserSession(token: "abc", email: "user@example.com"))
        )
        sut.email = "user@example.com"
        sut.password = "pass123"
        
        await sut.submit()
        
        XCTAssertEqual(navigator.goToCatalogCallCount, 1)
        XCTAssertNil(sut.errorMessage)
    }
```

**Explicación del test del happy path (el más interesante):**

Este test verifica que cuando el usuario escribe credenciales válidas y pulsa submit, el ViewModel llama a `navigator.goToCatalog()`.

`let (sut, _, navigator) = makeSUT(...)` — Desestructuramos la tupla para obtener el spy de navegación. El `_` descarta el gateway porque en este test no necesitamos inspeccionarlo directamente.

`XCTAssertEqual(navigator.goToCatalogCallCount, 1)` — Verificamos que `goToCatalog()` fue llamado exactamente una vez. El `LoginNavigatorSpy` registra cada llamada. Si el ViewModel no llamó al navigator (por un bug en el flujo), el contador será 0 y el test fallará.

**¿Por qué un spy y no un closure?** Porque `LoginNavigating` es un protocolo, y los protocolos admiten spies. El spy hace la intención explícita: estamos verificando un comportamiento ("se llamó a goToCatalog"), no capturando un valor.

`sut.email = "user@example.com"` y `sut.password = "pass123"` — Simulamos que el usuario escribió en los campos de texto. En la app real, esto lo haría SwiftUI a través de los bindings. En el test, lo hacemos directamente.

`await sut.submit()` — Ejecutamos el submit. Usamos `await` porque `submit()` es `async`. El test espera a que termine toda la ejecución (incluyendo la llamada al UseCase y al gateway stub) antes de continuar.

`XCTAssertEqual(receivedSession, expectedSession)` — Verificamos que la trampa capturó la sesión correcta. Si `receivedSession` sigue siendo `nil`, significa que el closure nunca se ejecutó (lo cual sería un bug). Si contiene una sesión diferente, también es un bug.

`XCTAssertNil(sut.errorMessage)` — Verificamos que no hay mensaje de error. En el happy path, todo sale bien, así que no debería haber error.

```swift
    // MARK: - Error Display
    
    func test_submit_with_invalid_email_shows_email_error_message() async {
        let (sut, _, _) = makeSUT()
        sut.email = "invalid"
        sut.password = "pass123"
        
        await sut.submit()
        
        XCTAssertEqual(sut.errorMessage, "El email no tiene un formato válido.")
    }
```

**Explicación del test de error de email:**

Este test verifica un sad path: cuando el usuario escribe un email sin arroba y pulsa submit, el ViewModel muestra un mensaje de error específico.

`sut.email = "invalid"` — Simulamos un email sin arroba. El Value Object `EmailAddress` rechazará este string.

Fíjate en que **no configuramos el gateway para que falle**. Usamos el gateway por defecto (que devuelve éxito). ¿Por qué? Porque el error ocurre **antes** de llegar al gateway. El UseCase intenta crear un `EmailAddress` con "invalid", el `EmailAddress` lanza `ValidationError.invalidFormat`, el UseCase lo traduce a `LoginError.invalidEmail`, y el ViewModel lo traduce al string "El email no tiene un formato válido." El gateway ni se entera porque nunca se llega a llamar.

`XCTAssertEqual(sut.errorMessage, "El email no tiene un formato válido.")` — Verificamos que el ViewModel tradujo el error al mensaje correcto. Si el mensaje fuera diferente (un typo, por ejemplo), el test fallaría.

```swift
    func test_submit_with_empty_password_shows_password_error_message() async {
        let (sut, _, _) = makeSUT()
        sut.email = "user@example.com"
        sut.password = ""
        
        await sut.submit()
        
        XCTAssertEqual(sut.errorMessage, "La contraseña no puede estar vacía.")
    }
    
    func test_submit_with_rejected_credentials_shows_credentials_error() async {
        let (sut, _, _) = makeSUT(gatewayResult: .failure(.invalidCredentials))
        sut.email = "user@example.com"
        sut.password = "wrong"
        
        await sut.submit()
        
        XCTAssertEqual(sut.errorMessage, "Email o contraseña incorrectos.")
    }
    
    func test_submit_with_connectivity_error_shows_connectivity_message() async {
        let (sut, _, _) = makeSUT(gatewayResult: .failure(.connectivity))
        sut.email = "user@example.com"
        sut.password = "pass123"
        
        await sut.submit()
        
        XCTAssertEqual(sut.errorMessage, "Sin conexión a internet. Inténtalo de nuevo.")
    }
    
    // MARK: - Loading State
    
    func test_submit_sets_isLoading_to_false_after_completion() async {
        let (sut, _, _) = makeSUT()
        sut.email = "user@example.com"
        sut.password = "pass123"
        
        await sut.submit()
        
        XCTAssertFalse(sut.isLoading)
    }
    
    // MARK: - Error Clearing
    
    func test_submit_clears_previous_error_before_new_attempt() async {
        let (sut, _, _) = makeSUT(gatewayResult: .failure(.invalidCredentials))
        sut.email = "user@example.com"
        sut.password = "wrong"
        
        await sut.submit()
        XCTAssertNotNil(sut.errorMessage)
        
        // Second attempt - error should be cleared at the start
        sut.password = "correct"
        // We can't easily test the intermediate state (isLoading=true, errorMessage=nil)
        // but we test that after completion the error reflects the new result
        await sut.submit()
        XCTAssertEqual(sut.errorMessage, "Email o contraseña incorrectos.")
    }
}
```

Fíjate en que los tests del ViewModel son `@MainActor`. Esto es necesario porque el ViewModel es `@MainActor`, así que todas las interacciones con él deben ocurrir en el main actor. Los tests `async` de XCTest soportan esto correctamente.

Los tests verifican:

Que el estado inicial es correcto (campos vacíos, no loading, sin error). Que un login exitoso llama a `navigator.goToCatalog()` exactamente una vez. Que cada tipo de error se traduce al mensaje correcto en español. Que `isLoading` vuelve a `false` después de completar. Que el error anterior se limpia al intentar de nuevo.

---

## La Preview con Stub

Una de las grandes ventajas de nuestra arquitectura es que las previews de SwiftUI funcionan sin servidor, sin red, y de forma instantánea. Esto es posible porque podemos inyectar el `InMemoryAuthRepository` en lugar del gateway real:

```swift
// StackMyArchitecture/Features/Login/Interface/LoginView+Preview.swift

private final class PreviewNavigator: LoginNavigating {
    func goToCatalog() { print("Preview: login exitoso — navegando a Catalog") }
}

#Preview("Login - Happy Path") {
    NavigationStack {
        LoginView(
            viewModel: LoginViewModel(
                useCase: AuthenticateUserUseCase(
                    authRepository: InMemoryAuthRepository(delayNanoseconds: 1_000_000_000)
                ),
                navigator: PreviewNavigator()
            )
        )
    }
}
```

El stub tiene un delay de 1 segundo para que puedas ver el estado de loading en la preview. Si quieres probar el estado de error, puedes crear un stub que siempre falle:

```swift
struct FailingAuthRepository: AuthRepository, Sendable {
    func authenticate(credentials: Credentials) async throws -> UserSession {
        try await Task.sleep(nanoseconds: 500_000_000)
        throw LoginError.invalidCredentials
    }
}

#Preview("Login - Error") {
    NavigationStack {
        LoginView(
            viewModel: LoginViewModel(
                useCase: AuthenticateUserUseCase(repository: FailingAuthRepository()),
                navigator: PreviewNavigator()
            )
        )
    }
}
```

Esto te permite ver cómo se ve la pantalla de login con un mensaje de error sin necesidad de tener un servidor real que rechace credenciales. Las previews son una herramienta de desarrollo, y con nuestra arquitectura, son extremadamente potentes.

---

## El Composition Root: ensamblando todo

Ahora que tenemos todas las piezas, veamos cómo el Composition Root las conecta:

```swift
// StackMyArchitecture/App/CompositionRoot.swift

import SwiftUI

@MainActor
struct CompositionRoot {
    
    func makeLoginView(navigator: any LoginNavigating) -> LoginView {
        let httpClient = URLSessionHTTPClient()
        let baseURL = URL(string: "https://api.example.com")!
        let gateway = AuthHTTPRepository(httpClient: httpClient, baseURL: baseURL)
        let useCase = AuthenticateUserUseCase(repository: gateway)
        let viewModel = LoginViewModel(
            useCase: useCase,
            navigator: navigator
        )
        return LoginView(viewModel: viewModel)
    }
}
```

El Composition Root es el **único lugar** que conoce las implementaciones concretas. Es el único que sabe que `AuthRepository` se implementa con `AuthHTTPRepository`, que `HTTPClient` se implementa con `URLSessionHTTPClient`, y que el navigator es el coordinador de la app.

Si quieres cambiar a un stub para desarrollo local, cambias una línea:

```swift
// Para desarrollo sin servidor:
let gateway = InMemoryAuthRepository()
```

Si quieres apuntar a staging:

```swift
let baseURL = URL(string: "https://staging.example.com")!
```

Ningún otro archivo del proyecto cambia. Eso es inversión de dependencias en acción.

### Cómo se usa en la App principal

```swift
// StackMyArchitecture/App/StackMyArchitectureApp.swift

import SwiftUI

@main
struct StackMyArchitectureApp: App {
    private let compositionRoot = CompositionRoot()
    
    var body: some Scene {
        WindowGroup {
            NavigationStack {
                compositionRoot.makeLoginView(navigator: appCoordinator)
            }
        }
    }
}
```

En la Etapa 2, el `appCoordinator` implementará `LoginNavigating` y decidirá a qué pantalla ir. El ViewModel solo llama a `navigator?.goToCatalog()` — no sabe que el coordinador hace `path.append(.catalog)` por debajo.

---

## El flujo completo de un login exitoso

Para que veas cómo todas las capas trabajan juntas, vamos a trazar el flujo completo de un login exitoso, desde que el usuario pulsa el botón hasta que ve el resultado:

1. El usuario escribe "user@example.com" en el TextField de email y "pass123" en el SecureField de password.

2. El usuario pulsa el botón "Iniciar sesión". El botón crea un `Task` que llama a `viewModel.submit()`.

3. El ViewModel pone `isLoading = true` y `errorMessage = nil`. SwiftUI detecta el cambio y re-renderiza: el botón muestra un `ProgressView` en lugar del texto, y el mensaje de error anterior (si había uno) desaparece.

4. El ViewModel llama a `login.execute(email: "user@example.com", password: "pass123")`.

5. El `AuthenticateUserUseCase` intenta crear un `EmailAddress("user@example.com")`. El Value Object valida el formato: tiene arroba, tiene punto en el dominio. Es válido. Se crea el `EmailAddress`.

6. El `AuthenticateUserUseCase` intenta crear un `Password("pass123")`. El Value Object verifica que no está vacío. No lo está. Se crea el `Password`.

7. El `AuthenticateUserUseCase` crea un `Credentials(email: email, password: password)`.

8. El `AuthenticateUserUseCase` llama a `authRepository.authenticate(credentials: credentials)`. En producción, esto llega al `AuthHTTPRepository`.

9. El `AuthHTTPRepository` construye un `URLRequest` con método POST, URL `https://api.example.com/auth/login`, header `Content-Type: application/json`, y body `{"email":"user@example.com","password":"pass123"}`.

10. El `AuthHTTPRepository` llama a `httpClient.execute(request)`. La petición HTTP viaja al servidor.

11. El servidor verifica las credenciales, genera un token, y responde con status 200 y body `{"token":"abc-123","email":"user@example.com"}`.

12. El `AuthHTTPRepository` recibe la respuesta. Status code 200: OK. Parsea el JSON con `JSONDecoder`. Extrae el token. Crea y devuelve `UserSession(token: "abc-123", email: "user@example.com")`.

13. El `AuthenticateUserUseCase` recibe la `UserSession` del gateway y la devuelve al llamante (el ViewModel).

14. El ViewModel recibe la `UserSession` del UseCase. Llama a `navigator?.goToCatalog()`. El coordinador (que implementa `LoginNavigating`) hace `path.append(.catalog)` y SwiftUI navega a la pantalla del catálogo.

15. El ViewModel pone `isLoading = false`. SwiftUI detecta el cambio y re-renderiza: el botón vuelve a mostrar "Iniciar sesión" en lugar del `ProgressView`.

Trece componentes involucrados (usuario, vista, viewmodel, caso de uso, email VO, password VO, credentials, gateway, http client, request DTO, response DTO, session, navigator/coordinador), pero cada uno con una responsabilidad clara y bien definida. Si cualquiera de ellos falla, sabes exactamente dónde mirar porque cada capa tiene sus propios tests.

---

## Reflexión: la feature completa

Con esta lección hemos completado la implementación de la feature Login de punta a punta. Repasemos lo que tenemos:

**Domain:** Value Objects `EmailAddress` y `Password` con validación en construcción. `Credentials`, `UserSession`, `LoginError`, `LoginEvent`. Tests XCTest para los Value Objects.

**Application:** Protocolo `AuthRepository` (el puerto). `AuthenticateUserUseCase` que orquesta validación local, delegación al gateway, y traducción de errores. Tests XCTest con stub para todos los escenarios BDD.

**Infrastructure:** `AuthHTTPRepository` que implementa el puerto con HTTP/JSON. `InMemoryAuthRepository` para desarrollo sin servidor. DTOs separados. Protocolo `HTTPClient`. Tests de contrato XCTest.

**Interface:** `LoginViewModel` con `@Observable` y `@MainActor`. `LoginView` en SwiftUI. Tests XCTest del ViewModel. Previews funcionales con stub.

**Composition Root:** Ensamblaje de todas las piezas con inyección de dependencias.

Todo conectado, todo testeado, todo desacoplado. La feature es una unidad vertical completa que se puede desarrollar, testear, y mantener de forma independiente.

En la siguiente lección haremos un resumen del ciclo TDD completo que acabamos de vivir, consolidando las lecciones aprendidas.

---

## Error copy orientado al usuario

El `LoginViewModel` ya implementa la traducción correcta: el método `message(for:)` convierte cada caso de `LoginError` a un string legible en español, sin exponer detalles técnicos al usuario.

Esta separación es importante por principio: **nunca pases directamente el mensaje del servidor a la UI**. Si el backend cambia su formato de error, tu app mostraría mensajes extraños o incluso podría exponer información sensible.

Un error copy enterprise sigue estas reglas:

1. **No menciona tecnología** — no digas "database timeout", di "no pudimos conectar con el servidor".
2. **No revela arquitectura** — no digas "JWT verification failed", di "tu sesión ha expirado".
3. **Sugiere acción** — en lugar de "error 500", di "inténtalo de nuevo en unos minutos".
4. **Es amigable** — usa lenguaje natural, no código de error.

Nuestro `message(for:)` ya sigue estas reglas para los cuatro errores de Etapa 1. Cuando en Etapa 2 se añadan casos como `sessionExpired` o `accountLocked`, simplemente se añaden nuevas ramas al `switch` — sin tocar nada más.

---

## Evolución natural: biometría (Face ID / Touch ID)

> **Enterprise (Etapa 2+):** Esta sección describe un patrón que **no se implementa en Etapa 1**. Requiere `SessionRepository` y Keychain, que se abordan más adelante.

Una vez que tienes login con email/contraseña funcionando, la evolución natural en una app enterprise es añadir **biometría** para facilitar el acceso recurrente.

### Patrón de biometría en iOS

El flujo biometrico no reemplaza al login con credenciales — lo complementa:

1. **Primer login** — usuario introduce email/contraseña, sesión se guarda en Keychain.
2. **Login posterior** — app detecta que hay sesión guardada en Keychain.
3. **Prompt biometrico** — app muestra "Iniciar sesión con Face ID?".
4. **Si acepta** — app desbloquea el token de Keychain y usa la sesión directamente.
5. **Si rechaza** — app muestra login con email/contraseña.

Este patrón requiere:

- Guardar un flag en Keychain indicando que el usuario ha activado biometría.
- Usar `LocalAuthentication` framework para el prompt.
- Proteger el token en Keychain con `kSecAttrAccessControl` que requiere biometría.

```swift
import LocalAuthentication

func attemptBiometricLogin() async throws -> UserSession? {
    let context = LAContext()
    var authError: NSError?
    
    guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &authError) else {
        return nil  // Biometría no disponible en este dispositivo
    }
    
    let localizedReason = "Inicia sesión con Face ID para acceder a tu cuenta"
    let success = try await context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics,
                                                  localizedReason: localizedReason)
    guard success else { return nil }
    
    // Biometría exitosa: desbloquear token de Keychain (Etapa 2+)
    return try await sessionRepository.load()
}
```

### Consideraciones UX

- **No forzar biometría** — siempre ofrecer opción de login con contraseña.
- **Fall-back grácil** — si biometría falla (dedo mojado, Face ID no reconoce), mostrar login normal.
- **Explicar valor** — el prompt debe decir claramente "para acceder a tu cuenta", no solo "Face ID".

**En este curso básico** no implementamos biometría porque requiere configuración adicional en Keychain y manejo de permisos. Pero es importante que sepas que esta es la evolución natural del login en apps enterprise.


---

## 🔨 Checkpoint Xcode — Interface en el proyecto real

Abre el scaffold y contrasta lo que acabas de aprender con la implementación de producción.

```bash
open apps/ios/ArchitectureKit/Package.swift
# Navega a: Sources/FeatureLoginUI/LoginViewModel.swift
# Navega a: Sources/FeatureLoginUI/LoginView.swift
```

**Diferencias clave respecto a la lección — léelas con atención:**

| Concepto lección | Implementación real | Por qué importa |
|---|---|---|
| `@StateObject var viewModel` | `@Bindable var viewModel` | Swift 6: `@Observable` reemplaza `ObservableObject`; `@Bindable` habilita bindings sin `@Published` |
| `@ObservedObject` / `@Published` | `@Observable @MainActor` | El compilador garantiza que toda mutación de UI ocurre en el hilo principal |
| `isLoading: Bool` como estado | `Phase` enum (`.idle`, `.loading`, `.authenticated`) | Estado sellado — imposible tener `isLoading: true` + `errorMessage: nil` simultáneamente incoherentes |
| ViewModel con `submit()` síncrono | `submit() async` marcado con `@MainActor` | Swift Concurrency: la tarea se lanza desde `Task { await viewModel.submit() }` en la View |
| Elementos UI sin identificadores | `accessibilityIdentifier` en todos los controles | Los tests de UI localizan nodos por este identificador, no por texto visible |

**Inspecciona `LoginViewModel.swift`:**

```swift
// Esto es lo que ves en el scaffold:
@Observable @MainActor
public final class LoginViewModel {

    public enum Phase { case idle, loading, authenticated }

    public private(set) var phase: Phase = .idle
    public private(set) var errorMessage: String? = nil
    public var email: String = ""
    public var password: String = ""

    // ...
    public func submit() async {
        phase = .loading
        // ...
    }
}
```

Nota: `phase` y `errorMessage` son `private(set)` — la View solo puede leerlos, no escribirlos directamente. Esto es el contrato unidireccional aplicado a nivel de compilador.

**Inspecciona `LoginView.swift`:**

```swift
// @Bindable permite bindings two-way sobre @Observable sin @Published
@Bindable var viewModel: LoginViewModel

// El botón lanza la corrutina correctamente:
Button("Iniciar sesión") {
    Task { await viewModel.submit() }
}
```

**Ejecuta los tests de la capa UI:**

```bash
cd apps/ios/ArchitectureKit
swift test --filter FeatureLoginUITests
```

Resultado esperado: todos los tests en verde. Si alguno falla, es que hay una discrepancia entre la View y el ViewModel — no entre el test y la implementación.

**Preguntas de reflexión antes de continuar:**

1. ¿Por qué `phase` es un enum y no `isLoading: Bool + isAuthenticated: Bool`? ¿Qué estado incoherente imposibilita el enum?
2. `@MainActor` en la clase entera vs en métodos individuales — ¿qué diferencia produce en la experiencia del compilador?
3. Si añadieras un estado `.sessionExpired` al `Phase` enum, ¿cuántos archivos tendrías que tocar? ¿Qué te dice eso sobre el diseño?

**Progreso de la feature Login:**

| Capa | Estado |
|---|---|
| FeatureLoginDomain | ✅ Tests verdes |
| FeatureLoginData | ✅ Tests verdes |
| FeatureLoginUI | ✅ Tests verdes |
| AppComposition | ⏳ Próxima lección |

---

## Qué sigue

La siguiente lección, [TDD: ciclo completo Red-Green-Refactor](05-tdd-ciclo-completo.md), consolida todo lo que hemos construido trazando el ciclo TDD completo de punta a punta sobre la feature Login.

