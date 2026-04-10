# Conectando la App: Tu Primera App Funcional

## El momento de la verdad: ver tu trabajo en el simulador

Has construido la feature Login completa con sus 4 capas: Domain con `Email` y `Password`, Application con `LoginUseCase`, Infrastructure con `RemoteAuthGateway` y `StubAuthGateway`, y Interface con `LoginViewModel` y `LoginView`. Todo testeado, todo desacoplado.

Pero hasta ahora has estado trabajando **en la oscuridad**. Has visto tests pasar en la consola, pero no has visto nada en el simulador de iOS. Esta lección es el puente: vamos a conectar todo para que tu app compile, se ejecute, y veas el formulario de login en pantalla.

> **Objetivo de esta lección:** Al terminar, tendrás una app iOS funcional que muestra el login. Será un **milestone visible** que confirma que todo lo construido hasta ahora realmente funciona.

> **Nota de nomenclatura lección ↔ scaffold:** Esta lección usa los nombres pedagógicos: `LoginUseCase`, `AuthGateway`, `StubAuthGateway`, `Session`. En el scaffold `apps/ios/ArchitectureKit` los equivalentes son `AuthenticateUserUseCase`, `AuthRepository`, `StubAuthRepository`, `UserSession`. Consulta la [tabla de equivalencias completa](../anexos/equivalencias-scaffold.md).

---

## Paso 1: Crear el archivo de entrada de la app

Cada app iOS necesita un punto de entrada. En SwiftUI moderno, esto es un archivo con `@main` que crea la `WindowGroup`.

**Crea el archivo:** `App/StackMyArchitectureApp.swift`

```swift
import SwiftUI

// @main marca el punto de entrada de la aplicación.
// El sistema operativo llama a main() automáticamente cuando el usuario
// abre la app. Sin esto, la app no tiene donde empezar.
@main
struct StackMyArchitectureApp: App {
    
    // El CompositionRoot es el único lugar donde creamos dependencias.
    // Lo hacemos aquí, a nivel de app, para que vivan durante toda
    // la vida de la aplicación. Si lo creáramos dentro de body,
    // se recrearía cada vez que SwiftUI reconstruye la vista.
    private let compositionRoot = CompositionRoot()
    
    // @SceneBuilder es un property wrapper que permite definir
    // la estructura de ventanas de la app. WindowGroup es la escena
    // estándar para apps iOS - maneja la ventana principal.
    var body: some Scene {
        WindowGroup {
            // Aquí conectamos el CompositionRoot con la primera vista.
            // compositionRoot.makeLoginView() devuelve una LoginView
            // completamente configurada con su ViewModel y dependencias.
            compositionRoot.makeLoginView()
        }
    }
}
```

**Paso a paso en Xcode:**
1. Click derecho en la carpeta `App/` en el navegador
2. New File → Swift File
3. Nombre: `StackMyArchitectureApp.swift`
4. Selecciona el target principal (StackMyArchitecture), NO el de tests
5. Pega el código arriba

---

## Paso 2: Crear el CompositionRoot

El `CompositionRoot` es el **único lugar** donde se ensamblan las dependencias. Es el pegamento que conecta las capas sin que ellas se conozcan entre sí.

**Crea el archivo:** `App/CompositionRoot.swift`

```swift
import SwiftUI

// CompositionRoot es el lugar donde ensamblamos el grafo de dependencias.
// Es el único lugar donde una capa "conoce" de otra.
// Por ejemplo: Application conoce de Domain (eso está bien),
// pero Domain NO conoce de Application.
struct CompositionRoot {
    
    // MARK: - Gateways (Infrastructure)
    
    // Creamos el gateway stub para desarrollo local.
    // Usamos 'private' porque nadie fuera de CompositionRoot
    // necesita acceder directamente al gateway.
    private func makeAuthGateway() -> any AuthGateway {
        // StubAuthGateway simula login sin red.
        // Útil para desarrollo: no necesitas servidor backend.
        // El delay de 1 segundo simula latencia real.
        return StubAuthGateway(delayNanoseconds: 1_000_000_000)
    }
    
    // MARK: - Use Cases (Application)
    
    private func makeLoginUseCase() -> LoginUseCase {
        // LoginUseCase depende de AuthGateway (inyectado por constructor).
        // No sabe si es stub o real - eso es desacoplamiento.
        return LoginUseCase(authGateway: makeAuthGateway())
    }
    
    // MARK: - View Models (Interface)
    
    func makeLoginViewModel() -> LoginViewModel {
        // El ViewModel necesita el use case para ejecutar login.
        // También recibe un closure que se llama cuando el login tiene éxito.
        return LoginViewModel(
            login: makeLoginUseCase(),
            onLoginSucceeded: { session in
                // Por ahora, solo imprimimos en consola.
                // En E2 (Integración) conectaremos la navegación real.
                print("Login exitoso! Token: \(session.token)")
            }
        )
    }
    
    // MARK: - Views (Interface)
    
    func makeLoginView() -> some View {
        // LoginView es una struct, así que la creamos directamente.
        // Su ViewModel se crea aquí y se pasa a la vista.
        return LoginView(viewModel: makeLoginViewModel())
    }
}
```

**Cómo evolucionas a un backend real (sin tocar nada más)**

El poder del desacoplamiento se ve aquí. Cuando tengas un servidor real, el único cambio es en `makeAuthGateway()`. El resto del grafo — use case, view model, vista — no sabe ni que ocurrió:

```swift
// Ahora (desarrollo): stub sin red
private func makeAuthGateway() -> any AuthGateway {
    return StubAuthGateway(delayNanoseconds: 1_000_000_000)
}

// Después (producción): backend real, mismo protocolo
private func makeAuthGateway() -> any AuthGateway {
    let httpClient = URLSessionHTTPClient()
    let baseURL = URL(string: "https://api.tuapp.com")!
    return RemoteAuthGateway(httpClient: httpClient, baseURL: baseURL)
    // LoginUseCase, LoginViewModel y LoginView no cambian ni una línea.
    // Solo cambia el ensamblador — CompositionRoot — que es exactamente
    // el único lugar que debería saber qué implementación usar.
}
```

Este es el momento en que la inversión de dependencia se paga: Domain define `AuthGateway`, Infrastructure lo implementa, y CompositionRoot decide cuál usar según el entorno.

---

**¿Por qué struct y no class?**

`CompositionRoot` es un `struct` porque no necesita mantener estado mutable. Cada método crea nuevas instancias. Si fuera `class`, podría tener propiedades que cambian, y eso complicaría el testing.

```swift
// ❌ CompositionRoot como class con estado compartido:
final class CompositionRoot {
    private var cachedGateway: (any AuthGateway)?

    func makeAuthGateway() -> any AuthGateway {
        if let existing = cachedGateway { return existing }
        let new = StubAuthGateway(delayNanoseconds: 1_000_000_000)
        cachedGateway = new   // mutación compartida entre llamadas
        return new
    }
}
// Problema: si el gateway acumula estado entre tests o llamadas,
// un test puede contaminar al siguiente. Además, en Swift 6,
// pasar `CompositionRoot` a través de contextos de concurrencia
// requiere conformar a `Sendable`, lo que fuerza a proteger
// cada propiedad mutable con locks o actors — complejidad innecesaria.

// ✅ CompositionRoot como struct: sin estado, sin riesgos:
struct CompositionRoot {
    func makeAuthGateway() -> any AuthGateway {
        return StubAuthGateway(delayNanoseconds: 1_000_000_000)
        // Cada llamada crea una instancia fresca.
        // Los tests son deterministas: no hay estado residual entre ellos.
    }
}
// Regla de oro: si un tipo solo ensambla dependencias y no necesita
// recordar nada entre llamadas, hazlo struct.
```

---

## Paso 3: Verificar imports necesarios

Abre cada archivo que creaste y verifica que los imports sean correctos:

**En `StackMyArchitectureApp.swift`:**
```swift
import SwiftUI
// No necesitas importar otros módulos porque
// CompositionRoot está en el mismo target
```

**En `CompositionRoot.swift`:**
```swift
import SwiftUI
// AuthGateway, LoginUseCase, etc. están en el mismo target,
// así que no necesitas imports adicionales
```

**Si tienes errores de "Cannot find in scope":**

1. Revisa que los archivos estén en el target correcto:
   - Selecciona el archivo en Xcode
   - Abre el Inspector (panel derecho)
   - Verifica que "Target Membership" tenga check en tu app target

2. Verifica que los protocolos y structs tengan visibilidad `internal` o `public`:

```swift
// En AuthGateway.swift
protocol AuthGateway { ... }  // internal por defecto, accesible dentro del target
```

---

## Paso 4: Ajustar el LoginView para navegación (placeholder)

El `LoginViewModel` que construimos en la lección anterior espera un closure `onLoginSucceeded`. Asegúrate de que tu `LoginViewModel` tenga este init:

```swift
// En Features/Login/Interface/LoginViewModel.swift

@Observable
@MainActor
final class LoginViewModel {
    var email = ""
    var password = ""
    var isLoading = false
    var errorMessage: String?
    
    private let login: LoginUseCase
    private let onLoginSucceeded: @MainActor (Session) -> Void
    
    init(
        login: LoginUseCase,
        onLoginSucceeded: @MainActor @escaping (Session) -> Void
    ) {
        self.login = login
        self.onLoginSucceeded = onLoginSucceeded
    }
    
    func submit() async {
        isLoading = true
        errorMessage = nil
        
        do {
            let session = try await login.execute(email: email, password: password)
            onLoginSucceeded(session)
        } catch let error as LoginUseCase.Error {
            errorMessage = Self.message(for: error)
        } catch {
            errorMessage = "Error inesperado. Inténtalo de nuevo."
        }
        
        isLoading = false
    }
    
    private static func message(for error: LoginUseCase.Error) -> String {
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

**Nota:** Este es exactamente el mismo `LoginViewModel` que implementamos en la [lección de Interface](05-feature-login/04-interface-swiftui.md). Si ya lo tienes, solo verifica que el init coincide.

**¿Qué pasa si olvidas `@MainActor` en el closure?**

El parámetro `onLoginSucceeded` está marcado `@MainActor @escaping`. Esto no es decorativo: le dice al compilador que ese closure *solo puede ejecutarse en el hilo principal*. En Swift 6, si lo olvidas, el compilador te para en seco:

```swift
// ❌ Closure sin @MainActor — Swift 6 error en compile time:
func makeLoginViewModel() -> LoginViewModel {
    return LoginViewModel(
        login: makeLoginUseCase(),
        onLoginSucceeded: { session in
            // Error: "Converting non-sendable function value to '@MainActor @Sendable (Session) -> Void'"
            // Swift 6 detecta que este closure podría ejecutarse en cualquier hilo,
            // pero el tipo lo exige en main actor. No compila.
            print("Login exitoso!")
        }
    )
}

// ✅ Con @MainActor explícito en el closure — compila y es seguro:
func makeLoginViewModel() -> LoginViewModel {
    return LoginViewModel(
        login: makeLoginUseCase(),
        onLoginSucceeded: { @MainActor session in
            // Ahora Swift garantiza que este código se ejecuta en el hilo principal.
            // Aquí puedes actualizar UI, navegar, o modificar @Observable objects.
            print("Login exitoso! Token: \(session.token)")
        }
    )
}
```

En proyectos reales, este closure es donde lanzas la navegación post-login. Como la navegación toca UI, necesita main actor. Swift 6 te lo exige; si compilas en Swift 5, no ves el error hasta runtime.

---

## Paso 5: Build y Run

**Paso a paso:**

1. Selecciona un simulador:
   - En Xcode, menú superior: `Product → Destination → iPhone 16 Pro`

2. Compila el proyecto:
   - `Cmd + B` (Build)
   - Deberías ver "Build Succeeded" en la barra superior

3. Ejecuta la app:
   - `Cmd + R` (Run)
   - El simulador se abrirá (tarda 10-30 segundos la primera vez)

4. Verifica que ves:
   - El campo de email
   - El campo de password
   - El botón "Iniciar sesión"

**Si hay errores de compilación comunes:**

| Error | Solución |
|-------|----------|
| "Cannot find 'CompositionRoot' in scope" | Verifica que `CompositionRoot.swift` esté en el target correcto |
| "Cannot find 'AuthGateway' in scope" | Revisa que los archivos de Infrastructure estén en el target |
| "Missing argument 'onLoginSucceeded'" | Añade el parámetro al init de LoginViewModel |
| "No such module 'SwiftUI'" | Este archivo no está en un target de app |

---

## Paso 6: Probar el flujo manualmente

Una vez que la app corre en el simulador:

1. **Prueba el happy path:**
   - Email: `user@test.com`
   - Password: `password123`
   - Pulsa "Iniciar sesión"
   - Deberías ver el spinner, y luego en la consola de Xcode: `Login exitoso! Token: ...`

2. **Prueba un error:**
   - Email: `invalid-email`
   - Pulsa "Iniciar sesión"
   - Deberías ver el mensaje de error en rojo debajo del formulario

3. **Ver la consola:**
   - `Cmd + Shift + C` abre la consola de Xcode
   - Ahí verás los print statements

---

## Checkpoint: ¿Funciona?

Antes de continuar, verifica:

- [ ] La app compila sin errores (`Cmd + B`)
- [ ] La app se ejecuta en el simulador (`Cmd + R`)
- [ ] Veo el formulario de login con dos campos y un botón
- [ ] Puedo escribir email y password
- [ ] Al pulsar el botón, aparece un spinner de carga
- [ ] Con datos válidos, veo el mensaje de éxito en consola
- [ ] Con datos inválidos, veo un mensaje de error en la UI

**Si todo está ✅, felicidades.** Tu arquitectura limpia está funcionando. El Domain valida, el Use Case orquesta, el Gateway simula la red, y la Interface muestra todo al usuario.

**Si algo falla:**
- Revisa los imports
- Verifica los targets de cada archivo
- Comprueba que los nombres de archivos coincidan con las referencias
- Mira la consola de errores de Xcode (`Cmd + Shift + Y`)

---

## Qué sigue

Ahora tienes una app funcional, pero aislada. Solo muestra login y no navega a ningún lado. Antes de avanzar a la Etapa 2, cierra la Etapa 1 revisando lo que has construido y completando los entregables.

→ [Checkpoint y bitácora — Etapa 1](checkpoint-y-bitacora-etapa-1.md) — Checkpoint y bitácora de la Etapa 1.
