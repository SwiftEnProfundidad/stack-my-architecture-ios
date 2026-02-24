# Anexo: Guía SOLID

> Referencia completa de los 5 principios con ejemplos del curso

---

## S - Single Responsibility Principle (SRP)

### Definición

> "Un módulo debe tener una, y solo una, razón para cambiar."
> — Robert C. Martin

### ¿Por Qué Existe?

Cuando una clase tiene múltiples responsabilidades, los cambios se mezclan:
- El equipo de DB cambia el schema → toca tu clase
- Product quiere nueva validación → toca la misma clase
- Marketing cambia provider → toca la misma clase

**Resultado:** Cambios constantes, riesgo de romper lo que no tocabas.

### Ejemplo en el Curso

```swift
// ❌ ANTES: Una clase, múltiples razones de cambio
class UserManager {
    func saveToDatabase(_ user: User) { ... }        // Cambia: DB team
    func validateEmail(_ email: String) -> Bool { ... } // Cambia: Product
    func sendWelcomeEmail(_ user: User) { ... }      // Cambia: Marketing
}

// ✅ DESPUÉS: Cada clase tiene una razón de cambio
class UserRepository {      // Solo cambia cuando cambia persistencia
    func save(_ user: User) async throws { ... }
}

class UserValidator {         // Solo cambia cuando cambian reglas de negocio
    func validate(_ email: Email) -> ValidationResult { ... }
}

class UserOnboardingService { // Solo cambia cuando cambia estrategia CRM
    func sendWelcome(_ user: User) async { ... }
}
```text

### ¿Dónde Aparece en el Curso?

| Lección | Aplicación |
|---------|-----------|
| `01-principios-ingenieria.md` | Cohesión = SRP práctico |
| `01-fundamentos/04-estructura-feature-first.md` | Cada capa tiene una responsabilidad |
| `05-feature-login/02-application.md` | Un caso de uso = un escenario BDD |
| `05-feature-login/03-infrastructure.md` | Repository solo persiste |

### Señales de Alerta

- Clase >300 líneas
- Dificultad para describir qué hace sin usar "y"
- Múltiples equipos modificando mismo archivo
- Tests difíciles de escribir (demasiados mocks)

### Checklist

- [ ] Puedo describir esta clase en una frase sin "y"
- [ ] Sé quién/es (actor/es) puede pedirme cambios
- [ ] Los cambios son localizados (un lugar, no dispersos)

---

## O - Open/Closed Principle (OCP)

### Definición

> "Las entidades deben estar abiertas para extensión, pero cerradas para modificación."
> — Bertrand Meyer

### ¿Por Qué Existe?

El código que funciona y está testeado es valioso. Modificarlo introduce riesgo de regresión.

### Ejemplo en el Curso

```swift
// ❌ ANTES: Cada nuevo método de pago requiere modificar PaymentProcessor
class PaymentProcessor {
    func process(_ payment: Payment) {
        switch payment.type {
        case .creditCard: processCreditCard(payment)
        case .paypal: processPayPal(payment)
        case .applePay: processApplePay(payment)  // Tocamos clase existente 😱
        }
    }
}

// ✅ DESPUÉS: Extensión sin modificación
protocol PaymentMethod {
    func process(amount: Decimal) async throws -> PaymentResult
}

class PaymentService {
    private let methods: [PaymentType: PaymentMethod]
    
    func execute(_ payment: Payment) async throws -> PaymentResult {
        guard let method = methods[payment.type] else {
            throw PaymentError.unsupportedMethod
        }
        return try await method.process(amount: payment.amount)
    }
}

// Nuevo método: solo añadimos implementación
struct GooglePayPayment: PaymentMethod {
    func process(amount: Decimal) async throws -> PaymentResult { ... }
}
// PaymentService no se entera, no tocamos código existente
```text

### ¿Dónde Aparece en el Curso?

| Lección | Aplicación |
|---------|-----------|
| `02-integracion/04-infra-real-network.md` | Nuevo gateway sin tocar código |
| `03-evolucion/01-caching-offline.md` | Decorator añade caché sin modificar repo |
| `05-maestria/07-composicion-avanzada.md` | Decorators/Composite como OCP |

### Señales de Alerta

- Switch statements que crecen constantemente
- "Tengo que tocar X clases para añadir una feature"
- Miedo a modificar código "antiguo pero funcional"

### Checklist

- [ ] Puedo añadir funcionalidad sin modificar código existente
- [ ] Uso protocols/extensiones en lugar de switches
- [ ] El código "antiguo" está protegido de cambios

---

## L - Liskov Substitution Principle (LSP)

### Definición

> "Los objetos de una clase hija deben poder sustituir objetos de la clase padre sin alterar el funcionamiento."
> — Barbara Liskov

### ¿Por Qué Existe?

Violaciones de LSP crean bugs sutiles que aparecen en runtime.

### Ejemplo en el Curso

```swift
// ❌ VIOLACIÓN: Cuadrado "ES UN" rectángulo matemáticamente, pero...
class Rectangle {
    var width: Double
    var height: Double
}

class Square: Rectangle {
    override var width: Double {
        didSet { height = width }  // Rompe expectativas de Rectangle
    }
}

func resize(_ r: Rectangle, w: Double) {
    r.width = w  // Con Square, height también cambia 😱
}

// ✅ SOLUCIÓN: No heredar, implementar protocolo
protocol Shape {
    func area() -> Double
}

struct Rectangle: Shape { ... }
struct Square: Shape { ... }  // Ambos son Shape, sin herencia forzada
```text

### ¿Dónde Aparece en el Curso?

| Lección | Aplicación |
|---------|-----------|
| Todos los protocols | Cualquier implementación sustituye a otra |
| `05-maestria/03-structured-concurrency.md` | Actors substituibles |

### Señales de Alerta

- `isKindOf` checks dispersos
- Overrides que cambian comportamiento semántico
- "Funciona con X pero no con Y" (subclases)

### Checklist

- [ ] Cualquier implementación del protocolo funciona igual
- [ ] No hay condicionales por tipo específico
- [ ] Las substituciones son transparentes para el cliente

---

## I - Interface Segregation Principle (ISP)

### Definición

> "Ningún cliente debe verse forzado a depender de métodos que no usa."
> — Robert C. Martin

### ¿Por Qué Existe?

Interfaces grandes acoplan innecesariamente. Si tienes 10 métodos y uso 2, estoy acoplado a 8 que no necesito.

### Ejemplo en el Curso

```swift
// ❌ ANTES: Interface "todo-en-uno"
protocol DataStore {
    func read<T>(_ key: String) async -> T?
    func write<T>(_ value: T, for key: String) async
    func delete(_ key: String) async
    func observe<T>(_ key: String) -> AsyncStream<T?>     // No todos necesitan
    func clearAll() async                                  // Peligroso
}

// UI solo lee, pero tiene acceso a clearAll() 😱

// ✅ DESPUÉS: Interfaces segregadas
protocol Readable {
    func read<T>(_ key: String) async -> T?
}

protocol Writable: Readable {
    func write<T>(_ value: T, for key: String) async
    func delete(_ key: String) async
}

protocol AdminStore {
    func clearAll() async  // Solo admins lo ven
}

// Clientes ven solo lo que necesitan
class HistoryViewModel {
    private let store: Readable  // Solo puede leer, seguro
    init(store: Readable) { self.store = store }
}
```text

### ¿Dónde Aparece en el Curso?

| Lección | Aplicación |
|---------|-----------|
| `02-integracion/03-contratos-features.md` | Protocols pequeños y cohesionados |
| `03-evolucion/06-swiftdata-store.md` | Readable vs Writable vs AdminStore |

### Señales de Alerta

- Interfaces con >5 métodos
- Clientes que ignoran parte de la interface
- "Ese método no debería ser público"

### Checklist

- [ ] Cada cliente usa todos los métodos de la interface
- [ ] Interfaces pequeñas y cohesionadas
- [ ] Métodos peligrosos están en interfaces separadas

---

## D - Dependency Inversion Principle (DIP)

### Definición

> "Los módulos de alto nivel no deben depender de módulos de bajo nivel. Ambos deben depender de abstracciones."
> "Las abstracciones no deben depender de detalles. Los detalles deben depender de abstracciones."
> — Robert C. Martin

### ¿Por Qué Existe?

Dependencias directas acoplan y hacen el código imposible de testear sin infraestructura real.

### Ejemplo en el Curso

```swift
// ❌ ANTES: Dependencia directa, acoplamiento fuerte
class LoginViewModel {
    private let networkClient: NetworkClient  // Concreto 😱
    
    func login(email: String, password: String) async {
        let result = await networkClient.post("/login", ...)  // Imposible testear sin red
    }
}

// ✅ DESPUÉS: Dependencia de abstracción
protocol AuthGateway {
    func authenticate(credentials: Credentials) async throws -> Session
}

class LoginViewModel {
    private let gateway: AuthGateway  // Abstracción
    
    init(gateway: AuthGateway) {
        self.gateway = gateway  // Inyectado, swappeable
    }
}

// Implementaciones (detalles dependen de abstracción)
class RemoteAuthGateway: AuthGateway { ... }  // Usa URLSession internamente
class StubAuthGateway: AuthGateway { ... }   // Devuelve datos fake para tests
```text

### ¿Dónde Aparece en el Curso?

| Lección | Aplicación |
|---------|-----------|
| `01-fundamentos/04-estructura-feature-first.md` | Composition Root = DIP en acción |
| `05-feature-login/02-application.md` | Puertos (protocolos) en Application |
| `02-integracion/06-composition-root.md` | Wiring de dependencias |

### Señales de Alerta

- Instancias directas de dependencias externas dispersas
- "No puedo testear esto sin servidor"
- Cambios en infraestructura rompen lógica de negocio

### Checklist

- [ ] Alto nivel depende de protocols, no de concretos
- [ ] Las abstracciones están en la capa de alto nivel
- [ ] Los detalles (infraestructura) implementan las abstracciones
- [ ] Composition Root es el único lugar con instanciación

---

## SOLID en Conjunto: Ejemplo Completo

```swift
// ===== SRP: Cada tipo tiene una razón de cambio =====
struct Payment { }           // Cambia: reglas de negocio de pago
struct PaymentValidator { } // Cambia: reglas de validación

// ===== OCP: Extensible sin modificación =====
protocol PaymentMethod {
    func process(amount: Decimal) async throws -> PaymentResult
}

// ===== LSP: Cualquier implementación sustituible =====
struct CreditCardPayment: PaymentMethod { ... }
struct ApplePayPayment: PaymentMethod { ... }

// ===== ISP: Clientes ven solo lo que necesitan =====
protocol PaymentQueryable {
    func history(for user: UserID) async -> [Payment]
}

protocol PaymentProcessable {
    func process(_ payment: Payment) async throws -> PaymentResult
}

// ===== DIP: Alto nivel no depende de bajo nivel =====
class PaymentService {
    private let methods: [PaymentType: PaymentMethod]  // Abstracciones
    
    init(methods: [PaymentType: PaymentMethod]) {       // Inyección
        self.methods = methods
    }
}
```

---

## Anti-Patterns vs SOLID

| Anti-Pattern | Principio Violado | Solución |
|--------------|-------------------|----------|
| God Class (500 líneas) | SRP | Dividir en clases cohesionadas |
| Switch que crece | OCP | Strategy pattern con protocols |
| Herencia forzada | LSP | Composición sobre herencia |
| Interface gigante | ISP | Dividir en interfaces pequeñas |
| Instancias directas | DIP | Inyección de dependencias |

---

## Checklist de Code Review SOLID

### SRP
- [ ] ¿Puedo describir esta clase en una frase sin "y"?
- [ ] ¿Hay un solo actor que puede pedir cambios?

### OCP
- [ ] ¿Puedo añadir funcionalidad sin tocar código existente?
- [ ] ¿Hay switches que podrían ser protocols?

### LSP
- [ ] ¿Cualquier implementación del protocolo funciona igual?
- [ ] ¿No hay `isKindOf` checks?

### ISP
- [ ] ¿Usan todos los clientes todos los métodos?
- [ ] ¿Las interfaces son pequeñas y cohesionadas?

### DIP
- [ ] ¿Dependemos de abstracciones, no de concretos?
- [ ] ¿El Composition Root es el único lugar con instanciación?

---

## Recursos

- ["Clean Code"](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882) - Robert C. Martin
- ["Agile Software Development"](https://www.amazon.com/Agile-Software-Development-Principles-Patterns/dp/0135974445) - Robert C. Martin
- [Swift by Sundell - SOLID](https://www.swiftbysundell.com/articles/solid-swift/)

---

> *"SOLID no es un destino, es un camino. No busques perfección desde el día 1. Busca reconocer violaciones y entender su coste."*

---

**Anterior:** [Errores de Compilación: Cómo Leerlos y Solucionarlos ←](errores-compilacion.md) · **Siguiente:** [Anexo: Guía CQS y CQRS →](guia-cqs-cqrs.md)
