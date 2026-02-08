# Anexo: Guía CQS y CQRS

> Separación de comandos y consultas: desde principio simple hasta arquitectura avanzada

---

## CQS - Command Query Separation

### Definición

> "Un método debería ser un comando que ejecuta una acción, o una consulta que devuelve datos, pero no ambas cosas."
> — Bertrand Meyer

### ¿Por Qué Existe?

Métodos que hacen ambas cosas (mutar y devolver) son confusos y peligrosos:

```swift
// ❌ ANTES: Método híbrido
func updateUser(_ user: User) -> User {
    // Muta estado (guarda en DB)
    database.save(user)
    // Devuelve datos (el usuario actualizado)
    return database.fetch(user.id)!  // ¿Y si falla el fetch? Inconsistente
}

// Problemas:
// 1. ¿Qué pasa si save() funciona pero fetch() falla?
// 2. ¿El return es el usuario guardado o uno nuevo?
// 3. Difícil de testear: necesito DB real para verificar
```

### ¿Cómo Aplicarlo?

Separar en dos métodos claros:

```swift
// ✅ DESPUÉS: Separación clara

// COMMAND: Muta estado, no devuelve datos de negocio
func saveUser(_ user: User) async throws {
    try await database.save(user)
    // Éxito o excepción, no hay valor de retorno confuso
}

// QUERY: Solo lee, nunca muta
func fetchUser(id: UserID) async throws -> User {
    return try await database.fetch(id)  // Solo lectura
}

// Uso claro:
// 1. Guardar
try await saveUser(newUser)
// 2. Leer (si necesito confirmar)
let saved = try await fetchUser(id: newUser.id)
```

### Reglas de CQS

| Aspecto | Comando (Command) | Consulta (Query) |
|---------|-------------------|------------------|
| Acción | Muta estado | Solo lee |
| Retorno | `Void` o resultado de operación | Datos solicitados |
| Side effects | Sí (intencionales) | No (puros) |
| Idempotencia | Opcional | Idealmente sí |
| Nombres | `save`, `update`, `delete`, `process` | `get`, `fetch`, `find`, `validate` |

### Ejemplo en el Curso

```swift
// Domain/Application: Use Cases separados

// COMMAND: Login muta estado (crea sesión)
class LoginUseCase {
    func execute(credentials: Credentials) async throws -> Session {
        // Valida, autentica, CREA sesión (muta)
        let session = try await authGateway.authenticate(credentials)
        await analytics.track(.loginSuccess)
        return session  // Devuelve identificador de la mutación, no datos de consulta
    }
}

// QUERY: Solo obtiene datos, nunca muta
class GetCurrentUserUseCase {
    func execute() async throws -> User {
        return try await userRepository.fetchCurrent()
        // Solo lectura, cero side effects
    }
}

// UI sabe qué operación hacer:
// - "Login" → Command (LoginUseCase)
// - "Ver perfil" → Query (GetCurrentUserUseCase)
```

### ¿Dónde Aparece en el Curso?

| Lección | Aplicación |
|---------|-----------|
| `05-feature-login/02-application.md` | Use cases: Command (login) vs Query (getUser) |
| `03-evolucion/01-caching-offline.md` | Cache read (query) vs write (command) |
| `03-evolucion/03-observabilidad.md` | Comando loggea eventos, Query no debe |

### Señales de Alerta

- Métodos que devuelven `Bool` ("¿Funcionó?") mientras mutan
- Métodos tipo `updateAndReturn`
- Dificultad para testear: "¿Mock query o command?"

---

## CQRS - Command Query Responsibility Segregation

### Definición

> "Separar completamente el modelo de escritura (commands) del modelo de lectura (queries)."

### ¿Cuándo Pasar de CQS a CQRS?

| CQS Simple | CQRS Arquitectónico |
|------------|---------------------|
| Mismos modelos para leer y escribir | Modelos diferentes para cada operación |
| Misma base de datos | Bases de datos optimizadas por caso de uso |
| Misma validación | Validaciones específicas por operación |
| Baja complejidad | Alta escala o requisitos conflictivos |

### Escenarios para CQRS

```
Situación 1: Lecturas complejas, escrituras simples
├── Escritura: Solo "añadir producto al carrito"
├── Lectura: Agregaciones complejas (precio total, descuentos, tax, stock)
└── Solución: Modelo de escritura simple, modelo de lectura denormalizado

Situación 2: Escalabilidad asimétrica
├── Escrituras: 100/segundo (carrito, checkout)
├── Lecturas: 10,000/segundo (catálogo, precios)
└── Solución: Scale queries independientemente de writes

Situación 3: Diferentes equipos responsables
├── Equipo A: Gestiona inventario (writes de stock)
├── Equipo B: Gestiona pricing (reads con reglas complejas)
└── Solución: Contextos separados, modelos independientes
```

### Arquitectura CQRS Típica

```
┌─────────────────────────────────────────────────────────┐
│  CAPA DE COMANDOS (Writes)                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Command Bus → Command Handler → Domain Model     │ │
│  │  - Validación de negocio estricta                 │ │
│  │  - Invariantes protegidas                          │ │
│  │  - Eventos de dominio emitidos                     │ │
│  └─────────────────────────────────────────────────────┘ │
│                           │                             │
│                           ▼                             │
│                    ┌─────────────┐                      │
│                    │  Event Bus  │                      │
│                    └──────┬──────┘                      │
└───────────────────────────┼─────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────┐
│  CAPA DE CONSULTAS (Reads)│                             │
│                           ▼                             │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Query Handler → Proyección/Denormalized View        │ │
│  │  - Optimizado para queries específicas              │ │
│  │  - Sin lógica de negocio, solo presentación         │ │
│  │  - Cache agresivo permitido                         │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Ejemplo Práctico: E-commerce

```swift
// ============ MODELO DE ESCRITURA (Commands) ============

// Agregado: Carrito con reglas de negocio estrictas
class ShoppingCart: AggregateRoot {
    private var items: [CartItem] = []
    private var appliedCoupons: [Coupon] = []
    
    // Comando: Añadir item
    func addItem(_ product: Product, quantity: Int) throws {
        guard quantity > 0 else { throw CartError.invalidQuantity }
        guard items.count < 50 else { throw CartError.cartFull }
        
        if let existing = items.firstIndex(where: { $0.productId == product.id }) {
            items[existing].quantity += quantity
        } else {
            items.append(CartItem(productId: product.id, quantity: quantity, unitPrice: product.price))
        }
        
        emit(CartItemAddedEvent(productId: product.id, quantity: quantity))
    }
    
    // Comando: Aplicar cupón
    func applyCoupon(_ coupon: Coupon) throws {
        guard coupon.isValid else { throw CartError.invalidCoupon }
        guard !appliedCoupons.contains(where: { $0.id == coupon.id }) else { throw CartError.couponAlreadyApplied }
        appliedCoupons.append(coupon)
    }
    
    // NO hay método "calculateTotal()" aquí - eso es query
}

// ============ MODELO DE LECTURA (Queries) ============

// Proyección: Vista optimizada para mostrar carrito
struct CartViewModel: Codable {
    let cartId: String
    let items: [CartItemView]
    let subtotal: Money
    let discounts: [DiscountView]
    let tax: Money
    let total: Money
    let itemCount: Int
    let isValidForCheckout: Bool  // Calculado, no editable
}

// Handler: Query optimizada, sin lógica de negocio
class GetCartQueryHandler {
    private let readModel: CartReadModel  // Tabla/caché separada
    
    func handle(query: GetCartQuery) async throws -> CartViewModel {
        // Solo lectura de datos denormalizados
        // Sin validaciones de negocio (eso es en Commands)
        return try await readModel.getCart(query.cartId)
    }
}

// ============ SINCRONIZACIÓN: Eventos ============

// Cuando un comando emite un evento, actualiza el read model
class CartItemAddedEventHandler {
    func handle(_ event: CartItemAddedEvent) async {
        // Actualiza la proyección de lectura
        await cartReadModel.addItem(
            cartId: event.cartId,
            productId: event.productId,
            quantity: event.quantity
        )
    }
}
```

### Consistencia en CQRS

```
Consistencia Inmediata (Síncrona):
├── Aplicar cupón → Actualizar read model → Retornar
├── Pros: UI siempre ve datos actualizados
├── Cons: Más lento, más complejo
└── Cuándo: Operaciones críticas (pagos, stock)

Consistencia Eventual (Asíncrona):
├── Aplicar cupón → Emitir evento → Retornar
├── Event handler actualiza read model después
├── Pros: Rápido, escalable
├── Cons: Read model puede estar desactualizado segundos
└── Cuándo: Analytics, reportes, vistas no críticas
```

### CQRS en Apps Móviles (iOS)

```swift
// Contexto: App iOS con sincronización offline

// ==== LADO LOCAL (Command + Query locales) ====
class LocalCartRepository {
    // Commands locales (mutan Core Data/SwiftData)
    func saveItem(_ item: CartItem) async throws
    func removeItem(_ id: ProductID) async throws
    
    // Queries locales (leen Core Data)
    func getCartItems() async -> [CartItem]
    func getCartTotal() async -> Money
}

// ==== SINCRONIZACIÓN (Command remoto) ====
class CartSyncService {
    // Command: Sincroniza con servidor
    func syncCartToServer() async throws {
        let pendingChanges = await localRepo.getUnsyncedChanges()
        try await remoteCartApi.submitChanges(pendingChanges)
        await localRepo.markAsSynced()
    }
}

// ==== CONSULTAS REMOTAS (Query remoto) ====
class CartPricingService {
    // Query: Obtiene precios calculados (podría ser CQRS server-side)
    func getCalculatedCart(cartId: String) async throws -> CartCalculation {
        // Este endpoint podría apuntar a la "query store" del servidor
        return try await pricingApi.getCartCalculation(cartId: cartId)
    }
}
```

### ¿Cuándo Usar CQS vs CQRS?

| Situación | Recomendación |
|-----------|---------------|
| App simple, poca escala | CQS (métodos separados) |
| Validaciones complejas en writes | CQS |
| Lecturas muy diferentes de escrituras | CQRS (modelos separados) |
| Escala masiva (millones de usuarios) | CQRS con bases separadas |
| Equipos grandes, bounded contexts | CQRS por contexto |
| Event sourcing | CQRS natural (events → projections) |

### ¿Dónde Aparece en el Curso?

| Lección | Concepto | Nivel |
|---------|----------|-------|
| `05-feature-login/02-application.md` | CQS básico | Use cases como C o Q |
| `03-evolucion/01-caching-offline.md` | CQS práctico | Separar read/write cache |
| `03-evolucion/02-consistencia.md` | Consistencia eventual | Sync strategies |
| `04-arquitecto/01-bounded-contexts.md` | CQRS arquitectónico | Contextos con modelos separados |

---

## Anti-Patterns de CQS/CQRS

### 1. Leer dentro de un Command

```swift
// ❌ MAL: Query dentro de Command
func updateUser(_ user: User) -> User {
    let existing = repository.fetch(user.id)  // Query!
    existing.name = user.name  // Mutación
    return repository.save(existing)  // Command
}

// ✅ BIEN: Separar completamente
// Command Handler recibe datos ya preparados
func updateUser(command: UpdateUserCommand) async throws {
    // Asume que los datos están validados
    try await repository.update(command.userData)
}
```

### 2. Muttear en un Query

```swift
// ❌ MAL: Side effect en Query
func getUser(id: UserID) -> User {
    analytics.track("user_viewed")  // Side effect!
    return repository.fetch(id)
}

// ✅ BIEN: Query puro, tracking separado
func getUser(id: UserID) -> User {
    return repository.fetch(id)  // Solo lectura
}

// Tracking se hace en capa externa (decorator/interceptor)
```

### 3. Sobre-ingeniería CQRS

```swift
// ❌ MAL: CQRS para todo
class UserNameQuery { }      // Overkill
class UserNameCommand { }    // Overkill

// ✅ BIEN: CQS es suficiente
func getUserName() -> String  // Query
func updateUserName(_ name: String)  // Command

// CQRS solo cuando hay modelos realmente diferentes
```

---

## Checklist CQS/CQRS

### CQS Básico
- [ ] ¿Este método muta o consulta? (no ambos)
- [ ] ¿Los comandos devuelven Void o resultado de operación?
- [ ] ¿Las queries son puras (sin side effects)?
- [ ] ¿Los nombres reflejan la intención (save/get)?

### CQRS Arquitectónico
- [ ] ¿Los modelos de lectura y escritura son diferentes?
- [ ] ¿Hay un mecanismo de sincronización (eventos)?
- [ ] ¿La consistencia es adecuada para el caso de uso?
- [ ] ¿El equipo entiende la arquitectura?

---

## Recursos

- ["CQRS Journey" - Microsoft](https://msdn.microsoft.com/en-us/library/jj554200.aspx)
- ["Exploring CQRS and Event Sourcing"](https://www.amazon.com/Exploring-CQRS-Event-Sourcing-Microsoft-Patterns/dp/1621140252)
- [Greg Young on CQRS](https://cqrs.wordpress.com/)

---

> *"CQS separa métodos. CQRS separa modelos. Ambos buscan claridad: haz una cosa y hazla bien."*
