# Composition Root: donde se ensambla todo


<!-- snippet-mapping-note:auto -->
> **Nota de nomenclatura pedagógica**
> Algunos snippets de esta lección usan `ProductRepository` como nombre conceptual.
> En el scaffold real (`apps/ios/ArchitectureKit`) el equivalente operativo es `CatalogRepository`.
## Objetivo de aprendizaje

Al terminar esta lección vas a entender qué es el Composition Root, por qué es el único lugar que conoce todas las implementaciones concretas, y cómo se cablea una app real con dos features (Login + Catalog) paso a paso.

En palabras simples: el Composition Root es el "director de orquesta" que decide quién toca cada instrumento, pero no toca ninguno él mismo.

---

## Definición simple

El Composition Root es el punto de la aplicación donde se crean todas las dependencias y se conectan entre sí. Es el único lugar que sabe que `AuthGateway` se implementa con `RemoteAuthGateway`, que `ProductRepository` se implementa con `RemoteProductRepository`, y que `HTTPClient` se implementa con `URLSessionHTTPClient`.

Ninguna otra capa sabe estas cosas. Domain no sabe. Application no sabe. Interface no sabe. Solo el Composition Root.

---

## Modelo mental: la fábrica de montaje

Imagina una fábrica de coches:

- **Domain** diseña el motor (reglas de negocio puras).
- **Application** diseña el chasis (casos de uso que conectan piezas).
- **Infrastructure** fabrica las piezas (adaptadores concretos: red, disco).
- **Interface** pinta y decora la carrocería (UI).
- **Composition Root** es la **línea de montaje**: toma todas las piezas y las ensambla en un coche funcional.

Si el Domain supiera cómo se fabrica cada pieza, estaría acoplado al proceso de fabricación. El Composition Root existe para que nadie más tenga que saber cómo se ensambla el todo.

```mermaid
flowchart TD
    CR["Composition Root<br/>Punto de entrada de la app"] -.-> HTTP["Crea URLSessionHTTPClient"]
    CR -.-> AUTH["Crea RemoteAuthGateway<br/>inyecta httpClient"]
    CR -.-> PROD["Crea RemoteProductRepository<br/>inyecta httpClient"]
    CR -.-> LUC["Crea LoginUseCase<br/>inyecta authGateway"]
    CR -.-> PUC["Crea LoadProductsUseCase<br/>inyecta productRepository"]
    CR -.-> LVM["Crea LoginViewModel<br/>inyecta loginUseCase + closure"]
    CR -.-> CVM["Crea CatalogViewModel<br/>inyecta loadProductsUseCase + closure"]
    CR -.-> COORD["Crea AppCoordinator<br/>conecta closures de navegacion"]

    style CR fill:#f8d7da,stroke:#dc3545
```text

---

## Por qué no usar un Service Locator global

Una alternativa común (y problemática) es crear un objeto global accesible desde cualquier parte de la app, donde cualquier componente puede pedir cualquier dependencia cuando quiera. Esto se conoce como **Service Locator** y es un anti-patrón en este curso.

Problemas del Service Locator:

- **Acoplamiento oculto:** No sabes qué dependencias tiene un componente hasta que lo ejecutas y falla. El `init` no te dice nada.
- **Tests difíciles:** Tienes que mutar un estado global para inyectar stubs, lo cual introduce fragilidad y orden de ejecución en los tests.
- **Dependencias invisibles:** Un `LoginUseCase` que accede a un localizador global no declara en su `init` que necesita un `AuthGateway`. Lo descubres leyendo toda la implementación.

Con Composition Root + constructor injection:

```swift
// Dependencias explícitas: ves todo en el init
let useCase = LoginUseCase(gateway: authGateway)
```text

Beneficios:

- **Dependencias visibles:** El `init` te dice exactamente qué necesita.
- **Tests triviales:** Pasas un stub en el `init` y listo.
- **Compilador te ayuda:** Si olvidas una dependencia, no compila.

---

## Cuándo SÍ y cuándo NO

### Cuándo SÍ usar Composition Root

- Siempre que tengas inyección de dependencias (es decir, siempre en este curso).
- En el punto de entrada de la app (`@main`).
- Cuando necesites crear features con todas sus capas conectadas.

### Cuándo NO

- No crees múltiples Composition Roots repartidos por la app. Debe haber uno solo (o uno por scope muy claro, como un widget de iOS).
- No metas lógica de negocio en el Composition Root. Su trabajo es solo cablear, no decidir.

---

## Implementación paso a paso

### Paso 1: El HTTPClient compartido

Todas las features que hablan con un servidor necesitan un `HTTPClient`. Lo creamos una sola vez:

```swift
// StackMyArchitecture/App/CompositionRoot.swift

import SwiftUI

@MainActor
struct CompositionRoot {

    // MARK: - Shared dependencies (se crean una sola vez)

    private let httpClient: HTTPClient
    private let baseURL: URL

    init() {
        self.httpClient = URLSessionHTTPClient()
        self.baseURL = URL(string: "https://api.example.com")!
    }
}
```text

**Línea por línea:**

- `@MainActor` — El Composition Root crea ViewModels que son `@MainActor`, así que el propio root debe estar en el hilo principal.
- `private let httpClient` — Creado una vez, compartido por todas las features que necesiten red.
- `private let baseURL` — La URL base del servidor. En producción vendría de una configuración de entorno.

### Paso 2: Factory de Login

Cada feature tiene su propia factory (metodo que crea la cadena completa):

```swift
extension CompositionRoot {

    func makeLoginView(onLoginSucceeded: @MainActor @escaping (Session) -> Void) -> LoginView {
        // 1. Crear el gateway (Infrastructure)
        let authGateway = RemoteAuthGateway(
            httpClient: httpClient,
            baseURL: baseURL
        )

        // 2. Crear el caso de uso (Application)
        let loginUseCase = LoginUseCase(gateway: authGateway)

        // 3. Crear el ViewModel (Interface)
        let viewModel = LoginViewModel(
            loginUseCase: loginUseCase,
            onLoginSucceeded: onLoginSucceeded
        )

        // 4. Crear la vista
        return LoginView(viewModel: viewModel)
    }
}
```text

**Qué pasa aquí:**

1. Creamos `RemoteAuthGateway` inyectando el `httpClient` compartido.
2. Creamos `LoginUseCase` inyectando el gateway. El UseCase no sabe que es un `RemoteAuthGateway`; solo sabe que conforma `AuthGateway`.
3. Creamos `LoginViewModel` inyectando el UseCase y el closure de navegación.
4. Creamos `LoginView` inyectando el ViewModel.

**El closure `onLoginSucceeded`** es lo que conecta Login con el resto de la app. El Composition Root decide qué pasa cuando el login tiene éxito (por ejemplo, navegar al Catálogo). Login no lo sabe ni le importa.

### Paso 3: Factory de Catalog

```swift
extension CompositionRoot {

    func makeCatalogView(onProductSelected: @MainActor @escaping (Product) -> Void) -> CatalogView {
        // 1. Crear el repository (Infrastructure)
        let productRepository = RemoteProductRepository(
            httpClient: httpClient,
            baseURL: baseURL
        )

        // 2. Crear el caso de uso (Application)
        let loadProductsUseCase = LoadProductsUseCase(repository: productRepository)

        // 3. Crear el ViewModel (Interface)
        let viewModel = CatalogViewModel(
            loadProducts: loadProductsUseCase,
            onProductSelected: onProductSelected
        )

        // 4. Crear la vista
        return CatalogView(viewModel: viewModel)
    }
}
```text

Mismo patrón que Login. Misma estructura. Esa consistencia es intencional: cuando un nuevo desarrollador llega al equipo y ve cómo está montado Login, sabe automáticamente cómo está montado Catalog. Y cuando cree una tercera feature, sabe exactamente qué factory escribir.

### Paso 4: Conectar con el AppCoordinator

```swift
// StackMyArchitecture/App/StackMyArchitectureApp.swift

import SwiftUI

@main
struct StackMyArchitectureApp: App {
    @State private var coordinator = AppCoordinator()
    private let compositionRoot = CompositionRoot()

    var body: some Scene {
        WindowGroup {
            NavigationStack(path: $coordinator.path) {
                compositionRoot.makeLoginView { session in
                    coordinator.handle(.loginSucceeded(session))
                }
                .navigationDestination(for: AppRoute.self) { route in
                    switch route {
                    case .catalog:
                        compositionRoot.makeCatalogView { product in
                            coordinator.handle(.productSelected(product))
                        }
                    case .productDetail(let product):
                        Text("Detalle de \(product.name)")
                    }
                }
            }
        }
    }
}
```text

**Línea por línea:**

- `@State private var coordinator` — El coordinador gestiona la pila de navegación.
- `private let compositionRoot` — Creado una vez al iniciar la app.
- `compositionRoot.makeLoginView { session in ... }` — La primera pantalla es Login. Cuando el login tiene éxito, le decimos al coordinator.
- `.navigationDestination(for: AppRoute.self)` — SwiftUI moderno: el coordinator empuja rutas, y aquí decidimos qué vista mostrar para cada ruta.
- Cada vista se crea con su factory del CompositionRoot, y el closure de navegación se conecta al coordinator.

---

## Diagrama del flujo de ensamblaje completo

```mermaid
sequenceDiagram
    participant APP as @main App
    participant CR as CompositionRoot
    participant COORD as AppCoordinator

    APP->>CR: init()
    Note over CR: Crea httpClient + baseURL

    APP->>CR: makeLoginView(onLoginSucceeded)
    CR->>CR: RemoteAuthGateway(httpClient)
    CR->>CR: LoginUseCase(gateway)
    CR->>CR: LoginViewModel(useCase, closure)
    CR->>CR: LoginView(viewModel)
    CR-->>APP: LoginView lista

    Note over APP: Usuario hace login exitoso...

    APP->>COORD: handle(.loginSucceeded)
    COORD->>COORD: path.append(.catalog)

    APP->>CR: makeCatalogView(onProductSelected)
    CR->>CR: RemoteProductRepository(httpClient)
    CR->>CR: LoadProductsUseCase(repository)
    CR->>CR: CatalogViewModel(useCase, closure)
    CR->>CR: CatalogView(viewModel)
    CR-->>APP: CatalogView lista
```text

---

## El Composition Root en tests vs producción

En producción, el Composition Root crea implementaciones reales:

```swift
// Producción: red real
let httpClient = URLSessionHTTPClient()
let authGateway = RemoteAuthGateway(httpClient: httpClient, baseURL: prodURL)
```text

En tests, cada test crea su propia cadena con stubs:

```swift
// Tests: sin red, sin servidor
let authGateway = AuthGatewayStub(result: .success(session))
let useCase = LoginUseCase(gateway: authGateway)
let viewModel = LoginViewModel(loginUseCase: useCase, onLoginSucceeded: { _ in })
```text

No hay un "Composition Root de tests". Cada test monta exactamente la cadena que necesita con el helper `makeSUT`. Eso es lo que hemos hecho en todas las lecciones anteriores: el patrón `makeSUT` ES un mini-composition-root local para cada test.

---

## Errores típicos y cómo depurarlos

### Error 1: Crear dependencias dentro de los componentes

Cuando un ViewModel crea internamente su UseCase y su Gateway, no puedes testearlo sin hacer peticiones reales de red. La solución es siempre inyectar por constructor: el ViewModel recibe su UseCase en el `init`.

### Error 2: Pasar el CompositionRoot a los ViewModels

Si un ViewModel recibe el CompositionRoot entero, puede acceder a cualquier factory y dependencia. Eso rompe la separación de capas. La solución es pasar solo lo que el ViewModel necesita (su UseCase y su closure de navegación).

### Error 3: Olvidar que el Composition Root es @MainActor

Si creas ViewModels (que son `@MainActor`) fuera del hilo principal, el compilador de Swift 6.2 te dará un error. Asegúrate de que el Composition Root y sus factories están marcadas con `@MainActor`.

---

## Evolución futura del Composition Root

Cuando el proyecto crezca, el Composition Root puede evolucionar:

- **Etapa 3:** Añadir `CachedProductRepository` como decorador entre el UseCase y el repository remoto, sin tocar ninguna otra capa.
- **Etapa 4:** Migrar a un `Package.swift` donde `AppComposition` es un target SPM dedicado que importa todos los demás.
- **Firebase:** Cambiar `URLSessionHTTPClient` por `FirebaseAuthAdapter` solo aquí, sin tocar Login ni Catalog.

El Composition Root es el punto de máxima flexibilidad: puedes cambiar toda la infraestructura de la app modificando un solo archivo.

---

## ADR corto de la lección

```markdown
## ADR-003: Composition Root centralizado con factories por feature
- Estado: Aprobado
- Contexto: necesidad de ensamblar Login + Catalog sin acoplar features entre si ni con implementaciones concretas
- Decisión: un único CompositionRoot con factory methods por feature, inyección por constructor, closures de navegación hacia AppCoordinator
- Consecuencias: ensamblaje explícito y testeable; el único punto que conoce todas las implementaciones; fácil de extender con nuevas features o backends
- Fecha: 2026-02-07
```

---

## Checklist de calidad

- [ ] El Composition Root es el único lugar que importa implementaciones concretas.
- [ ] Ningún ViewModel, UseCase ni Gateway crea sus propias dependencias.
- [ ] Cada feature tiene su factory method independiente.
- [ ] Los closures de navegacion conectan features sin que estas se conozcan.
- [ ] En tests, cada test monta su propia cadena con stubs (patron makeSUT).
- [ ] El Composition Root está marcado como `@MainActor`.

---

## Cierre

El Composition Root parece un archivo sencillo: "solo crea objetos y los conecta". Pero su impacto arquitectónico es enorme. Es la razón por la que puedes cambiar de URLSession a Firebase sin tocar Domain. Es la razón por la que puedes testear un ViewModel en milisegundos. Es la razón por la que un nuevo desarrollador puede entender cómo se monta una feature mirando un solo archivo.

Un buen Composition Root no se nota. Un mal Composition Root (o su ausencia) se nota en cada PR, en cada test roto, y en cada refactor que se convierte en pesadilla.

---

**Anterior:** [Integration Tests ←](05-integration-tests.md) · **Siguiente:** [SwiftUI Enterprise: Patrones Imprescindibles →](07-swiftui-enterprise.md)

<!-- semantica-flechas:auto -->
## Semantica de flechas aplicada a esta arquitectura

```mermaid
flowchart LR
    subgraph APP["App / Composition module"]
        CR["CompositionRoot"]
        COORD["AppCoordinator"]
    end

    subgraph FEATURE["Feature module"]
        VM["FeatureViewModel"]
        UC["UseCase"]
        PORT["Repository protocol"]
    end

    subgraph INFRA["Infrastructure module"]
        ADAPTER["RemoteRepository adapter"]
        STORE["LocalStore"]
    end

    CR -.-> COORD
    CR -.-> ADAPTER
    VM --> UC
    UC -.o PORT
    ADAPTER --o PORT
    ADAPTER --> STORE
```text

Lectura semantica minima de este diagrama:

1. `-->` dependencia directa en runtime.
2. `-.->` wiring y configuracion de ensamblado.
3. `-.o` dependencia contra contrato/abstraccion.
4. `--o` salida/propagacion desde implementacion concreta.

