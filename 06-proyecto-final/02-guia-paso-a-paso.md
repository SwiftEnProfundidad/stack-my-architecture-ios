# Guía Paso a Paso — Proyecto Final iOS

> Esta guía desglosa los 7 hitos del proyecto final en tareas concretas y verificables.
> Cada hito tiene entradas, salidas y un comando de verificación.

---

## Hito 1 — Definir escenarios BDD y alcance

**Entrada:** elección de features (ver `00-proyecto-final-ios.md`)
**Salida:** fichero `docs/final-project/SCENARIOS.md` con escenarios completos

### Tareas

1. **Elige tus 2 features** antes de escribir código. Documenta la elección con una línea de justificación.

2. **Por cada feature**, escribe al menos 3 escenarios BDD (happy path, sad path, edge case):

```gherkin
Feature: Checkout

  Scenario: Usuario completa el pago con tarjeta válida
    Given el carrito tiene al menos 1 producto
    When el usuario introduce una tarjeta válida y confirma
    Then se crea una Order con estado "confirmed"
    And se muestra la pantalla de confirmación con el número de pedido

  Scenario: El pago es rechazado por el servidor
    Given el carrito tiene al menos 1 producto
    When el usuario confirma con una tarjeta rechazada
    Then se muestra el error "Pago rechazado. Revisa tus datos."
    And el carrito permanece intacto

  Scenario: El usuario abandona el checkout antes de confirmar
    Given el usuario está en la pantalla de checkout
    When navega hacia atrás sin confirmar
    Then el carrito conserva todos los productos
```

3. **Tabla de trazabilidad** (copia esta plantilla a `SCENARIOS.md`):

| Scenario ID | Feature | Tipo | Capa que lo verifica |
|---|---|---|---|
| CHK-001 | Checkout | Happy | `CheckoutUseCaseTests` |
| CHK-002 | Checkout | Sad | `CheckoutUseCaseTests` |
| CHK-003 | Checkout | Edge | `CheckoutViewModelTests` |

### Verificación del hito 1

- [ ] Cada feature tiene `>= 3` escenarios.
- [ ] Todos los escenarios tienen Given/When/Then.
- [ ] La tabla de trazabilidad relaciona scenario → test target.

---

## Hito 2 — Diseñar contratos y límites de dependencias

**Entrada:** escenarios BDD del Hito 1
**Salida:** diagrama de dependencias actualizado + contratos de puertos definidos como protocolos Swift vacíos

### Tareas

1. **Dibuja el grafo de dependencias** de las features nuevas. Regla: las dependencias apuntan hacia Domain, nunca al revés.

```
CheckoutView
  └──> CheckoutViewModel (@Observable, @MainActor)
         └──> PlaceOrderUseCase (struct, Sendable)
                ├──> CartRepository (protocolo ← Application)
                ├──> PaymentGateway (protocolo ← Application)
                └──> Order, CartItem, PaymentError (Domain)
```

2. **Crea los protocolos vacíos** como contratos. Un protocolo en rojo (`throws`, `async`) es suficiente para empezar TDD:

```swift
// Sources/FeatureCheckoutDomain/CartRepository.swift
protocol CartRepository: Sendable {
    func fetchCart() async throws -> [CartItem]
}

// Sources/FeatureCheckoutDomain/PaymentGateway.swift
protocol PaymentGateway: Sendable {
    func charge(_ cart: [CartItem], with token: String) async throws -> Order
}
```

3. **Documenta el ADR** de la nueva feature (`docs/final-project/ADR-XXX-checkout.md`). Mínimo: contexto, decisión y consecuencias.

### Verificación del hito 2

- [ ] Existe un diagrama (Mermaid o texto) con todas las dependencias nuevas.
- [ ] Los protocolos están en la capa correcta (Domain o Application).
- [ ] Hay al menos 1 ADR por feature nueva.

---

## Hito 3 — Implementar dominio y casos de uso con TDD

**Entrada:** protocolos del Hito 2
**Salida:** Domain + UseCases con cobertura mínima por cada escenario BDD

### Tareas

1. **Crea los Value Objects** del nuevo dominio con validación por construcción:

```swift
// Sources/FeatureCheckoutDomain/CartItem.swift
struct CartItem: Equatable, Sendable {
    let productId: String
    let quantity: Int

    init(productId: String, quantity: Int) throws {
        guard quantity > 0 else { throw CheckoutError.invalidQuantity }
        self.productId = productId
        self.quantity = quantity
    }
}
```

2. **Escribe el test primero** (ciclo Red → Green → Refactor):

```swift
// Tests/FeatureCheckoutDomainTests/PlaceOrderUseCaseTests.swift
final class PlaceOrderUseCaseTests: XCTestCase {

    func test_execute_withEmptyCart_throwsEmptyCartError() async {
        let sut = PlaceOrderUseCase(cart: StubCartRepository(items: []),
                                    gateway: StubPaymentGateway())
        await XCTAssertThrowsError(try await sut.execute(paymentToken: "tok_test")) { error in
            XCTAssertEqual(error as? CheckoutError, .emptyCart)
        }
    }

    func test_execute_withValidCart_returnsOrder() async throws {
        let items = [try CartItem(productId: "P1", quantity: 2)]
        let sut = PlaceOrderUseCase(cart: StubCartRepository(items: items),
                                    gateway: StubPaymentGateway(result: .success(Order.stub)))
        let order = try await sut.execute(paymentToken: "tok_test")
        XCTAssertEqual(order.status, .confirmed)
    }
}
```

3. **Estructura de targets SPM** para la nueva feature:

```
Sources/
  FeatureCheckoutDomain/
    CartItem.swift
    Order.swift
    CheckoutError.swift
    CartRepository.swift        ← protocolo
    PaymentGateway.swift        ← protocolo
    PlaceOrderUseCase.swift
Tests/
  FeatureCheckoutDomainTests/
    PlaceOrderUseCaseTests.swift
    CartItemTests.swift
```

### Verificación del hito 3

```bash
# Desde la raíz del Package.swift
swift test --filter FeatureCheckoutDomainTests
```

- [ ] Todos los tests del Domain en verde.
- [ ] Cada escenario BDD tiene al menos 1 test que lo verifica.
- [ ] Sin dependencias de Foundation, UIKit o SwiftUI en Domain.

---

## Hito 4 — Integrar infraestructura y manejo de errores

**Entrada:** protocolos de hito 2, tests de hito 3
**Salida:** adaptadores remotos/locales que implementan los protocolos

### Tareas

1. **Crea el adaptador remoto** implementando el protocolo:

```swift
// Sources/FeatureCheckoutInfra/RemotePaymentGateway.swift
struct RemotePaymentGateway: PaymentGateway {
    private let httpClient: HTTPClient

    func charge(_ cart: [CartItem], with token: String) async throws -> Order {
        let dto = ChargeRequestDTO(items: cart.map(CartItemDTO.init), token: token)
        let response: OrderResponseDTO = try await httpClient.post("/checkout/charge", body: dto)
        return response.toDomain()
    }
}
```

2. **Mapea errores HTTP a errores de dominio** dentro del adaptador. Nunca dejes escapar `URLError` o `DecodingError` sin traducir.

3. **Test de contrato del adaptador** (usa `URLProtocol` stub o `MockHTTPClient`):

```swift
func test_charge_when401_throwsPaymentRejectedError() async {
    let client = MockHTTPClient(status: 401)
    let sut = RemotePaymentGateway(httpClient: client)
    await XCTAssertThrowsError(try await sut.charge([], with: "tok")) { error in
        XCTAssertEqual(error as? CheckoutError, .paymentRejected)
    }
}
```

### Verificación del hito 4

```bash
swift test --filter FeatureCheckoutInfraTests
```

- [ ] Tests de adaptador en verde (éxito + errores HTTP principales).
- [ ] Sin `CheckoutError` leaking desde `URLError` sin traducción.
- [ ] DTOs separados de los modelos de Domain.

---

## Hito 5 — Conectar interfaz y navegación

**Entrada:** casos de uso del Hito 3
**Salida:** ViewModel + View funcionales, integrados en AppCoordinator

### Tareas

1. **ViewModel con @Observable y @MainActor:**

```swift
@Observable
@MainActor
final class CheckoutViewModel {
    var isLoading = false
    var errorMessage: String?
    var confirmedOrder: Order?

    private let placeOrder: PlaceOrderUseCase
    var onOrderConfirmed: ((Order) -> Void)?

    init(placeOrder: PlaceOrderUseCase, onOrderConfirmed: @escaping (Order) -> Void) {
        self.placeOrder = placeOrder
        self.onOrderConfirmed = onOrderConfirmed
    }

    func confirmPurchase(paymentToken: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            let order = try await placeOrder.execute(paymentToken: paymentToken)
            onOrderConfirmed?(order)
        } catch let e as CheckoutError {
            errorMessage = e.localizedDescription
        } catch {
            errorMessage = "Error inesperado"
        }
    }
}
```

2. **Conectar en CompositionRoot:**

```swift
// En CompositionRoot.makeCheckoutViewModel()
func makeCheckoutViewModel(onOrderConfirmed: @escaping (Order) -> Void) -> CheckoutViewModel {
    let gateway = RemotePaymentGateway(httpClient: httpClient)
    let cart = RemoteCartRepository(httpClient: httpClient)
    let useCase = PlaceOrderUseCase(cart: cart, gateway: gateway)
    return CheckoutViewModel(placeOrder: useCase, onOrderConfirmed: onOrderConfirmed)
}
```

3. **Navegar desde AppCoordinator** usando el patrón evento/closure:

```swift
// AppCoordinator: al confirmar el pedido, navega a OrderConfirmation
coordinator.onCheckoutCompleted = { [weak self] order in
    self?.push(.orderConfirmation(order))
}
```

### Verificación del hito 5

- [ ] La app compila y el simulador muestra las pantallas nuevas.
- [ ] La navegación funciona sin `NavigationLink` directo (closure/coordinator).
- [ ] `CheckoutViewModelTests` verifica los estados isLoading/error/success.

---

## Hito 6 — Añadir observabilidad, release y seguridad

**Entrada:** features integradas del Hito 5
**Salida:** logs estructurados, release checklist y threat model

### Tareas

1. **Logs en flujos críticos** (sin PII):

```swift
// ✅ Correcto
logger.info("checkout.initiated cartItemCount=\(cart.count)")
logger.error("checkout.failed reason=paymentRejected")

// ❌ Incorrecto — nunca loguear PII
logger.info("checkout.initiated user=\(user.email) card=\(card.number)")
```

2. **Release checklist** (`docs/final-project/RELEASE-CHECKLIST.md`):

```markdown
## Release — Checkout v1.0

- [ ] Feature flag `feature_checkout_enabled` activado en staging
- [ ] Tests en verde en CI
- [ ] Rollout al 10% el día 1, 50% día 3, 100% día 7
- [ ] Métricas de conversión monitoradas las primeras 24h
- [ ] Rollback plan: desactivar flag en < 5 min si conversion_rate < umbral
```

3. **Threat model lite** (mínimo 3 amenazas):

| Amenaza | Vector | Mitigación |
|---|---|---|
| Token de pago interceptado | Red insegura | HTTPS obligatorio, token efímero |
| Replay de petición de cobro | Middleware | Idempotency key por request |
| Datos de orden en logs | Logger sin filtro | Sanitización de campos sensibles |

### Verificación del hito 6

- [ ] `grep -r "email\|token\|card" Sources/ --include="*.swift"` no revela PII en logs.
- [ ] El release checklist tiene `>= 5` items con rollback definido.
- [ ] El threat model cubre `>= 3` amenazas con mitigación concreta.

---

## Hito 7 — Preparar la defensa técnica con evidencia

**Entrada:** proyecto completo de hitos 1-6
**Salida:** `docs/final-project/DEFENSA.md` con guion de 5 minutos

### Tareas

1. **Escribe `DEFENSA.md`** con esta estructura:

```markdown
# Defensa Técnica — [Tu nombre] — Proyecto Final iOS

## Contexto y problema
[1 párrafo: qué construiste y por qué]

## Decisión arquitectónica principal
ADR-XXX: [nombre]. Elegí [opción A] sobre [opción B] porque [razón].
Trade-off aceptado: [descripción].

## Evidencia de calidad
- Tests en verde: [N] tests, [N] targets
- Cobertura de caminos críticos: [lista]
- Sin data races detectadas con swift build -sanitize=thread

## Cómo fallaría el sistema
Escenario de fallo principal: [descripción].
Respuesta en los primeros 15 min: [paso 1], [paso 2], [paso 3].

## Qué mejoraría con más tiempo
[2-3 items concretos con justificación]
```

2. **Tabla before/after de métricas:**

| Métrica | Antes | Después |
|---|---|---|
| Número de features con TDD | 1 (Login) | 3 (Login + Catalog + Checkout) |
| Tests totales | N | N+X |
| Tiempo de onboarding de nueva feature | estimado | estimado |

3. **Ensaya las 5 preguntas de defensa** de `01-rubrica-y-entrega.md` en voz alta. Si no puedes responder alguna en < 2 minutos, vuelve al hito correspondiente.

### Verificación del hito 7

```bash
# Build limpio + todos los tests
swift build && swift test
```

- [ ] `DEFENSA.md` completo con todas las secciones.
- [ ] Puedes responder las 5 preguntas de defensa sin leer las notas.
- [ ] La tabla before/after tiene datos reales (no estimados).

---

## Checklist de cierre del proyecto

Antes de entregar, verifica que todo está en orden:

```bash
# 1. Build limpio
swift build

# 2. Suite completa en verde
swift test

# 3. Sin warnings de concurrencia
swift build -strict-concurrency=complete

# 4. Estructura de entrega completa
ls docs/final-project/
# Debe contener: SCENARIOS.md, ADR-*.md, RELEASE-CHECKLIST.md, DEFENSA.md
```

- [ ] Los 7 hitos completados con sus verificaciones.
- [ ] `docs/final-project/` tiene todos los artefactos.
- [ ] La rúbrica de `01-rubrica-y-entrega.md` está autocompletada.
- [ ] La rúbrica de empleabilidad `../05-maestria/rubrica-final/01-rubrica-empleabilidad-ios.md` revisada.

## 🔨 Checkpoint Xcode — Verificación por fase

```bash
# Al final de cada fase, confirma que los tests siguen en verde
cd apps/ios/ArchitectureKit && swift test

# Verifica que no añadiste dependencias ilegales en Domain
grep -rn "^import" Sources/FeatureLoginDomain Sources/FeatureCatalogDomain | grep -v "Foundation\|Testing" || echo "✅ Domain sin dependencias ilegales"
```

Ejecuta estos dos comandos al terminar cada fase de la guía. Si los tests fallan, no avances a la siguiente fase: encuentra el error primero. El progreso rápido con tests rotos es deuda técnica que se paga cara al final.
