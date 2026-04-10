# Mental Models: Cómo Pensar en Clean Architecture

## Deja de memorizar, empieza a entender

Los juniors memorizan reglas: "Domain no depende de nada". Los seniors entienden **por qué**. Esta guía te da los modelos mentales para pensar como un arquitecto.

---

## Modelo 1: Las Capas son Fronteras de Cambio

### Analogía: Un Restaurante

```text
┌─────────────────────────────────────────────────────────┐
│                    SALA (Interface)                      │
│  - Meseros toman pedidos                                │
│  - No cocinan, no compran ingredientes                   │
│  - Hablan con clientes y con cocina                    │
├─────────────────────────────────────────────────────────┤
│                    COCINA (Application)                  │
│  - Recibe pedidos de sala                              │
│  - Sigue recetas (reglas de negocio)                   │
│  - Solicita ingredientes al almacén (no gestiona stock) │
├─────────────────────────────────────────────────────────┤
│                    ALMACÉN (Infrastructure)                │
│  - Guarda ingredientes                                  │
│  - No decide qué cocinar                               │
│  - Provee lo que se pide                              │
├─────────────────────────────────────────────────────────┤
│                    RECETAS (Domain)                      │
│  - Define qué es un "buen plato"                       │
│  - No sabe de meseros ni almacén                       │
│  - Reglas universales de la cocina                   │
└─────────────────────────────────────────────────────────┘
```

**Insight:** Cada capa tiene una frontera clara. La sala no entra a la cocina. La cocina no decide qué ingredientes comprar.

### Aplicación a tu código

| Restaurante | Tu App | Responsabilidad |
|-------------|--------|-----------------|
| Sala | Interface (SwiftUI) | Recibir input, mostrar output |
| Cocina | Application | Orquestar casos de uso |
| Almacén | Infrastructure | Proveer datos externos |
| Recetas | Domain | Definir entidades y reglas |

---

## Modelo 2: Las Flechas de Dependencia son Ley

### Analogía: Corriente Eléctrica

```text
Domain        ←─── NO FLUIRÁ
    ↑
Application   ←─── NO FLUIRÁ
    ↑
Infrastructure
    ↑
Interface     ←─── EL BOTÓN FUNCIONA
```

**Principio:** La electricidad fluye hacia arriba (de infraestructura a dominio), pero **nunca** hacia abajo.

### Consecuencias prácticas

**❌ Si Domain depende de Infrastructure:**
```swift
// Domain/Entity/User.swift
import Foundation
import FirebaseAuth  // ← ¡DOMAIN SABE DE FIREBASE!

struct User {
    let firebaseUser: FirebaseAuth.User  // ← Acoplamiento mortal
}
```
→ Tu dominio está "electrocutado" cada vez que Firebase cambia.

**✅ Solución - Inversión de Dependencias:**
```swift
// Domain/Entity/User.swift
struct User {
    let id: String
    let email: String
    // Nada de Firebase aquí
}

// Infrastructure/Auth/FirebaseAuthService.swift
import FirebaseAuth

class FirebaseAuthService: AuthService {  // Implementa protocolo del dominio
    func login() -> User {
        let fbUser = FirebaseAuth.login()  // Traduce de Firebase a Domain
        return User(id: fbUser.uid, email: fbUser.email)
    }
}
```

**Insight:** Domain define el **qué** (protocolo). Infrastructure implementa el **cómo**.

---

## Modelo 3: Los Casos de Uso son Verbos

### Analogía: Ordenes en un Restaurante

Un cliente no dice: "Activa el horno, corta cebolla, sofríe..."

Dice: **"Quiero la paella"** (un verbo/nombre de resultado)

```swift
// ❌ Sin caso de uso - "modo receta"
class LoginViewModel {
    func buttonTapped() {
        let auth = FirebaseAuth.auth()  // Infrastructure directo
        auth.signIn(withEmail: email, password: pass) { result in
            // ... 50 líneas de lógica mezclada
        }
    }
}

// ✅ Con caso de uso - "modo orden"
class LoginViewModel {
    let loginUseCase: AuthenticateUserUseCase  // Application layer
    
    func buttonTapped() {
        Task {
            let result = await loginUseCase.execute(email: email, password: pass)
            // Solo maneja UI, no lógica de negocio
        }
    }
}
```

### Mentalidad: "Quiero que pase X"

| ❌ Imperativo (Cómo) | ✅ Declarativo (Qué) |
|---------------------|---------------------|
| Valida email, hashea password, llama API, guarda token... | Ejecuta `AuthenticateUserUseCase` |
| Muestra loader, fetch products, parse JSON, mapea a modelos... | Ejecuta `GetCatalogUseCase` |
| Verifica conexión, limpia cache, descarga imagen... | Ejecuta `SyncOfflineDataUseCase` |

---

## Modelo 4: Los Protocolos son Contratos

### Analogía: Enchufes Universal

```text
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Tu Laptop     │     │   Toma corriente │     │   Generador     │
│   (Interface)   │◄────│   (Protocol)     │◄────│   (Infrastructure)│
│                 │     │                 │     │                 │
│  Necesita:      │     │  Provee:         │     │  Implementa:     │
│  - 220V AC      │     │  - 220V AC      │     │  - Red eléctrica │
│  - 50-60Hz      │     │  - 50-60Hz      │     │  - O generador   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Insight:** Tu laptop (ViewModel) no sabe si la electricidad viene de la red o de un generador. Solo sabe que cumple el contrato.

### Aplicación: Repository Pattern

```swift
// Domain - Define el contrato (enchufe)
protocol ProductRepository {
    func getProducts() async throws -> [Product]
}

// Infrastructure - Implementación A (Red eléctrica)
class RemoteProductRepository: ProductRepository {
    func getProducts() async throws -> [Product] {
        // Llama API remota
    }
}

// Infrastructure - Implementación B (Generador)
class LocalProductRepository: ProductRepository {
    func getProducts() async throws -> [Product] {
        // Lee de base de datos local
    }
}

// Application - Usa el contrato, no le importa la implementación
class GetCatalogUseCase {
    let repository: ProductRepository  // "Enchufe genérico"
    
    func execute() async throws -> [Product] {
        return try await repository.getProducts()
    }
}
```

**Poder:** Puedes cambiar de Remote a Local sin tocar el UseCase. Solo inyectas otra implementación.

---

## Modelo 5: Los ViewModels son Traductores

### Analogía: Intérprete en una Conferencia

```text
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Orador     │◄───────►│  Intérprete  │◄───────►│  Audiencia   │
│  (UseCase)   │  Caso   │  (ViewModel) │   UI    │   (View)     │
│              │  de uso │              │  SwiftUI│              │
│  Habla en:   │         │  Traduce:    │         │  Entiende:   │
│  - Domain    │         │  - Domain →  │         │  - Strings   │
│  - Result    │         │    UI State  │         │  - Booleans  │
│  - Errors    │         │  - Input →   │         │  - Events    │
│              │         │    Commands  │         │              │
└──────────────┘         └──────────────┘         └──────────────┘
```

### Responsabilidad del ViewModel

**Traduce del Domain al UI:**
```swift
// Domain dice: Result<User, LoginError>
// ViewModel traduce a:
enum LoginState {
    case idle
    case loading
    case success(UserViewData)
    case error(String)  // Mensaje traducido para humanos
}
```

**Traduce del UI al Domain:**
```swift
// UI dice: onSubmitButtonTapped()
// ViewModel traduce a:
Task {
    await loginUseCase.execute(email: email, password: password)
}
```

**Nunca hace:**
- ❌ Lógica de negocio (eso es Application/Domain)
- ❌ Llamadas directas a API (eso es Infrastructure)
- ❌ Manejo de base de datos (eso es Infrastructure)

---

## Modelo 6: La Arquitectura es Inversión de Control

### Analogía: Hollywood Principle

> "No nos llames, nosotros te llamamos"

```swift
// ❌ Sin inversión - Tú controlas todo
class LoginViewModel {
    let api = APIClient()  // Tú creas las dependencias
    let auth = AuthManager()  // Tú decides cuándo usarlas
    let db = Database()  // Control total = Fragilidad total
}

// ✅ Con inversión - Te inyectan lo que necesitas
class LoginViewModel {
    let loginUseCase: AuthenticateUserUseCase  // Te dan esto listo
    let validator: InputValidator   // Configurado externamente
    
    init(loginUseCase: AuthenticateUserUseCase, validator: InputValidator) {
        self.loginUseCase = loginUseCase  // "Nosotros te llamamos"
        self.validator = validator
    }
}
```

### CompositionRoot: La Fábrica

```swift
// StackMyArchitectureApp.swift - Aquí se ensambla todo
@main
struct StackMyArchitectureApp: App {
    var body: some Scene {
        WindowGroup {
            CompositionRoot.makeLoginView()  // "Fábrica"
        }
    }
}

enum CompositionRoot {
    static func makeLoginView() -> some View {
        // Infrastructure
        let httpClient = HTTPClient(baseURL: "...")
        let authRepository = AuthHTTPRepository(client: httpClient)
        
        // Application
        let loginUseCase = AuthenticateUserUseCase(repository: authRepository)
        
        // Interface
        let viewModel = LoginViewModel(useCase: loginUseCase)
        return LoginView(viewModel: viewModel)
    }
}
```

**Insight:** La app se "ensambla" en un solo lugar. El resto del código solo usa lo que le dieron.

---

## Modelo 7: Los Tests son Especificaciones Vivas

### Analogía: Seguridad en Aeropuertos

```text
┌────────────────────────────────────────────────────────────┐
│                    CI/CD PIPELINE                           │
├────────────────────────────────────────────────────────────┤
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐ │
│  │ Unit    │───►│ Contract│───►│ Integr. │───►│ UI      │ │
│  │ Tests   │    │ Tests   │    │ Tests   │    │ Tests   │ │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘ │
│       │              │              │              │        │
│   "Código         "Interfaces    "Features      "Usuario   │
│    correcto"      respetadas"    funcionan"   feliz"     │
└────────────────────────────────────────────────────────────┘
```

### Jerarquía de Tests

| Tipo | Velocidad | Confianza | Cuándo falla |
|------|-----------|-----------|--------------|
| **Unit** | ⚡ < 1ms | 🎯 Lógica | Bug en función |
| **Contract** | ⚡ < 10ms | 🔌 Integridad | Cambio rompe API |
| **Integration** | ⚡⚡ < 1s | 🔄 Flujo | Feature no conecta |
| **UI/E2E** | ⚡⚡⚡ < 30s | 👤 Experiencia | Usuario no puede usar |

**Regla:** Si falla un Unit test, no necesitas correr los E2E para saber que algo está roto.

---

## Modelo 8: El Estado es un Snapshot

### Analogía: Fotografías vs. Película

**❌ Programación Imperativa (Película - frame a frame):**
```swift
class OldViewModel: ObservableObject {
    @Published var isLoading = false
    @Published var error: String?
    @Published var data: [Item]?
    
    func load() {
        isLoading = true  // Frame 1
        error = nil       // Frame 2
        
        Task {
            do {
                data = try await fetch()  // Frame 3
                isLoading = false         // Frame 4
            } catch {
                self.error = error.localizedDescription  // Frame 5
                self.isLoading = false                     // Frame 6
            }
        }
    }
}
// ¿Qué pasa si olvidas isLoading = false en algún path? 🐛
```

**✅ Programación Declarativa (Snapshot - una foto):**
```swift
@Observable
class ModernViewModel {
    enum State {
        case idle
        case loading
        case loaded([Item])
        case error(String)
    }
    
    var state: State = .idle  // Una variable = Un estado válido
    
    func load() {
        state = .loading  // Snapshot: "Estamos cargando"
        
        Task {
            do {
                let items = try await fetch()
                state = .loaded(items)  // Snapshot: "Tenemos datos"
            } catch {
                state = .error(error.localizedDescription)  // Snapshot: "Falló"
            }
        }
    }
}
```

**Insight:** Cada estado es **mutuamente excluyente**. No puedes estar simultáneamente en `loading` y `error`.

---

## Checklist de Modelos Mentales

Cuando escribas código, verifica:

- [ ] **¿Qué frontera estoy cruzando?** (Domain/App/Infra/Interface)
- [ ] **¿La flecha de dependencia apunta para arriba?** (hacia Domain)
- [ ] **¿Estoy escribiendo un "Cómo" o un "Qué"?** (Debe ser un caso de uso)
- [ ] **¿Estoy usando un protocolo o una implementación concreta?**
- [ ] **¿El ViewModel traduce o hace lógica de negocio?**
- [ ] **¿Quién controla las dependencias?** (Inyección, no creación)
- [ ] **¿Este test documenta comportamiento o verifica implementación?**
- [ ] **¿El estado es mutuamente excluyente?** (Enum vs. múltiples booleans)

---

## Ejercicio de Reflexión

**Código problemático:**
```swift
class ProductListViewModel: ObservableObject {
    @Published var products: [Product] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    let apiClient = APIClient()  // Creación directa
    let database = Database()      // Dependencia hacia abajo
    
    func load() {
        isLoading = true
        apiClient.fetch { [weak self] result in
            switch result {
            case .success(let data):
                self?.products = data
                self?.database.save(data)  // ViewModel hace persistencia
                self?.isLoading = false
            case .failure(let error):
                self?.errorMessage = error.localizedDescription
                self?.isLoading = false
            }
        }
    }
}
```

**Problemas identificados:**
1. ❌ ViewModel crea dependencias (no inyección)
2. ❌ ViewModel depende de APIClient e Infrastructure
3. ❌ ViewModel llama directamente a base de datos
4. ❌ Lógica de persistencia en Interface layer
5. ❌ Múltiples booleans que pueden estar inconsistentes

**¿Cómo lo arreglarías aplicando los modelos mentales?**

---

> **Regla de oro:** La Clean Architecture no es un conjunto de reglas para memorizar. Es un sistema de fronteras que te fuerza a pensar en responsabilidades. Cada vez que escribes código, pregúntate: "¿En qué capa estoy? ¿Qué frontera estoy cruzando? ¿Es correcto cruzarla?"

---

**Anexo relacionado:** [Guía de Nueva Feature](guia-nueva-feature.md)

---

