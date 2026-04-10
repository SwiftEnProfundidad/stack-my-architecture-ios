# Conectando la App: Tu Primera App Funcional

## El momento de la verdad: ver tu trabajo en el simulador

Has construido la feature Login completa con sus 4 capas: Domain con `EmailAddress` y `Password`, Application con `AuthenticateUserUseCase`, Infrastructure con `AuthHTTPRepository` y `InMemoryAuthRepository`, y Interface con `LoginViewModel` y `LoginView`. Todo testeado, todo desacoplado.

Pero hasta ahora has estado trabajando **en la oscuridad**. Has visto tests pasar en la consola, pero no has visto nada en el simulador de iOS. Esta lección es el puente: vamos a conectar todo para que tu app compile, se ejecute, y veas el formulario de login en pantalla.

> **Objetivo de esta lección:** Al terminar, tendrás una app iOS funcional que muestra el login. Será un **milestone visible** que confirma que todo lo construido hasta ahora realmente funciona.

> **Nota de nomenclatura lección ↔ scaffold:** Esta lección usa los nombres pedagógicos: `AuthenticateUserUseCase`, `AuthRepository`, `InMemoryAuthRepository`, `UserSession`. En el scaffold `apps/ios/ArchitectureKit` los equivalentes son `AuthenticateUserUseCase`, `AuthRepository`, `InMemoryAuthRepository`, `UserSession`. Consulta la [tabla de equivalencias completa](../anexos/equivalencias-scaffold.md).

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
    private let navigator = PrintNavigator()
    
    // @SceneBuilder es un property wrapper que permite definir
    // la estructura de ventanas de la app. WindowGroup es la escena
    // estándar para apps iOS - maneja la ventana principal.
    var body: some Scene {
        WindowGroup {
            // Aquí conectamos el CompositionRoot con la primera vista.
            // compositionRoot.makeLoginView(navigator:) devuelve una LoginView
            // completamente configurada con su ViewModel y dependencias.
            compositionRoot.makeLoginView(navigator: navigator)
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
    private func makeAuthRepository() -> any AuthRepository {
        // InMemoryAuthRepository simula login sin red.
        // Útil para desarrollo: no necesitas servidor backend.
        // El delay de 1 segundo simula latencia real.
        return InMemoryAuthRepository(delayNanoseconds: 1_000_000_000)
    }
    
    // MARK: - Use Cases (Application)
    
    private func makeAuthUseCase() -> AuthenticateUserUseCase {
        // AuthenticateUserUseCase depende de AuthRepository (inyectado por constructor).
        // No sabe si es stub o real - eso es desacoplamiento.
        return AuthenticateUserUseCase(repository: makeAuthRepository())
    }
    
    // MARK: - View Models (Interface)
    
    func makeLoginViewModel(navigator: any LoginNavigating) -> LoginViewModel {
        // El ViewModel necesita el use case y un navigator que implemente LoginNavigating.
        // En E2 (Integración) el AppCoordinator implementará LoginNavigating.
        return LoginViewModel(
            useCase: makeAuthUseCase(),
            navigator: navigator
        )
    }
    
    // MARK: - Views (Interface)
    
    func makeLoginView(navigator: any LoginNavigating) -> some View {
        // LoginView es una struct, así que la creamos directamente.
        // Su ViewModel se crea aquí y se pasa a la vista.
        return LoginView(viewModel: makeLoginViewModel(navigator: navigator))
    }
}

// Placeholder para Etapa 1 (sin coordinador real).
// En Etapa 2, AppCoordinator implementará LoginNavigating con NavigationPath.
final class PrintNavigator: LoginNavigating {
    func goToCatalog() { print("Login exitoso — navegando al catálogo (E2)") }
}
```

**Cómo evolucionas a un backend real (sin tocar nada más)**

El poder del desacoplamiento se ve aquí. Cuando tengas un servidor real, el único cambio es en `makeAuthRepository()`. El resto del grafo — use case, view model, vista — no sabe ni que ocurrió:

```swift
// Ahora (desarrollo): stub sin red
private func makeAuthRepository() -> any AuthRepository {
    return InMemoryAuthRepository(delayNanoseconds: 1_000_000_000)
}

// Después (producción): backend real, mismo protocolo
private func makeAuthRepository() -> any AuthRepository {
    let httpClient = URLSessionHTTPClient()
    let baseURL = URL(string: "https://api.tuapp.com")!
    return AuthHTTPRepository(httpClient: httpClient, baseURL: baseURL)
    // AuthenticateUserUseCase, LoginViewModel y LoginView no cambian ni una línea.
    // Solo cambia el ensamblador — CompositionRoot — que es exactamente
    // el único lugar que debería saber qué implementación usar.
}
```

Este es el momento en que la inversión de dependencia se paga: Domain define `AuthRepository`, Infrastructure lo implementa, y CompositionRoot decide cuál usar según el entorno.

---

**¿Por qué struct y no class?**

`CompositionRoot` es un `struct` porque no necesita mantener estado mutable. Cada método crea nuevas instancias. Si fuera `class`, podría tener propiedades que cambian, y eso complicaría el testing.

```swift
// ❌ CompositionRoot como class con estado compartido:
final class CompositionRoot {
    private var cachedGateway: (any AuthRepository)?

    func makeAuthRepository() -> any AuthRepository {
        if let existing = cachedGateway { return existing }
        let new = InMemoryAuthRepository(delayNanoseconds: 1_000_000_000)
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
    func makeAuthRepository() -> any AuthRepository {
        return InMemoryAuthRepository(delayNanoseconds: 1_000_000_000)
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
// AuthRepository, AuthenticateUserUseCase, etc. están en el mismo target,
// así que no necesitas imports adicionales
```

**Si tienes errores de "Cannot find in scope":**

1. Revisa que los archivos estén en el target correcto:
   - Selecciona el archivo en Xcode
   - Abre el Inspector (panel derecho)
   - Verifica que "Target Membership" tenga check en tu app target

2. Verifica que los protocolos y structs tengan visibilidad `internal` o `public`:

```swift
// En AuthRepository.swift
protocol AuthRepository { ... }  // internal por defecto, accesible dentro del target
```

---

## Paso 4: Ajustar el LoginView para navegación (placeholder)

El `LoginViewModel` que construimos en la lección anterior utiliza el protocolo `LoginNavigating`. Asegúrate de que tu `LoginViewModel` tenga este init:

```swift
// En Features/Login/Interface/LoginNavigating.swift
protocol LoginNavigating: AnyObject {
    @MainActor func goToCatalog()
}

// En Features/Login/Interface/LoginViewModel.swift

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

**Nota:** Este es exactamente el mismo `LoginViewModel` que implementamos en la [lección de Interface](05-feature-login/04-interface-swiftui.md). Si ya lo tienes, solo verifica que el init coincide.

**¿Por qué `@MainActor` en la firma del protocolo?**

El método `goToCatalog()` está marcado `@MainActor` en el protocolo. Esto no es decorativo: garantiza que cualquier implementación del protocolo ejecute la navegación en el hilo principal. En Swift 6, esto previene data races en la UI.

```swift
// ✅ El protocolo exige @MainActor — la implementación hereda la restricción:
final class AppCoordinator: LoginNavigating {
    func goToCatalog() {
        // Swift garantiza que este código se ejecuta en el hilo principal.
        // Aquí puedes hacer path.append(.catalog) o isAuthenticated = true
        print("Navegando al catálogo...")
    }
}
```

En la Etapa 2 implementarás `AppCoordinator: LoginNavigating` y harás la navegación real. Por ahora, el `PrintNavigator` es suficiente para verificar el flujo.

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
| "Cannot find 'AuthRepository' in scope" | Revisa que los archivos de Infrastructure estén en el target |
| "Missing argument 'navigator'" | Crea un objeto que implemente `LoginNavigating` y pásale al init |
| "No such module 'SwiftUI'" | Este archivo no está en un target de app |

---

## Paso 6: Probar el flujo manualmente

Una vez que la app corre en el simulador:

1. **Prueba el happy path:**
   - EmailAddress: `user@test.com`
   - Password: `password123`
   - Pulsa "Iniciar sesión"
   - Deberías ver el spinner, y luego en la consola de Xcode: `Login exitoso! Token: ...`

2. **Prueba un error:**
   - EmailAddress: `invalid-email`
   - Pulsa "Iniciar sesión"
   - Deberías ver el mensaje de error en rojo debajo del formulario

3. **Ver la consola:**
   - `Cmd + Shift + C` abre la consola de Xcode
   - Ahí verás los print statements

---

## 🔨 Checkpoint Xcode — La app real en el simulador

Has construido tu propia versión pedagógica. Ahora abre el scaffold y verifica que la misma arquitectura produce una app funcional con tests en verde.

**Paso 1 — Suite completa en verde**

```bash
cd apps/ios/ArchitectureKit
swift test
```

Todos los targets pasan. Este es el punto de llegada de la Etapa 1: una feature completa con 4 capas, cada una testada de forma independiente.

**Paso 2 — Abre el scheme de la app en Xcode**

```bash
open apps/ios/ArchitectureKit/Package.swift
```

En Xcode: selecciona el scheme `AppComposition` (o el scheme de la app si existe) → `Cmd + R`. La pantalla de login aparece en el simulador.

**Paso 3 — Verifica el flujo completo**

- [ ] Formulario de login visible con dos campos y un botón
- [ ] EmailAddress inválido → mensaje de error sin llamar al servidor
- [ ] Credenciales correctas (definidas en `InMemoryAuthRepository`) → pantalla de catálogo
- [ ] `Cmd + U` → todos los tests en verde

**Si algo falla:**
- Revisa que el simulador seleccionado sea iOS 17+ o macOS 14+
- `Product > Clean Build Folder` (`Cmd + Shift + K`) y vuelve a compilar
- Comprueba que `Package.swift` resolvió todas las dependencias (File > Packages > Resolve)
- Mira la consola de errores (`Cmd + Shift + Y`)

**Si todo está ✅, has completado la Etapa 1.** Domain valida, UseCase orquesta, Repository simula la red, ViewModel traduce estado, AppCompositionRoot ensambla todo.

---

## Qué sigue

Ahora tienes una app funcional, pero aislada. Solo muestra login y no navega a ningún lado. Antes de avanzar a la Etapa 2, cierra la Etapa 1 revisando lo que has construido y completando los entregables.

→ [Checkpoint y bitácora — Etapa 1](checkpoint-y-bitacora-etapa-1.md) — Checkpoint y bitácora de la Etapa 1.
