# Consistencia e invalidación

> **Nota de nomenclatura:** Esta lección usa nombres genéricos (`ProductRepository`, `ProductStore`) para explicar el patrón. En el scaffold real, los equivalentes son `CatalogRepository` y `CatalogCacheStore`.

## Objetivo de aprendizaje

Al terminar esta lección vas a poder diseñar una política de consistencia para `Catalog` que sea explícita, testeable y operable: sabrás definir qué significa “dato aceptablemente fresco”, cuándo invalidarlo y cómo comunicar ese estado a UI sin engañar al usuario.

En versión simple: cache no es guardar datos, cache es gestionar confianza en esos datos con reglas claras.

---

## Definición simple

- Consistencia: cuánto se parece lo que ve el usuario a la verdad remota dentro de una tolerancia de negocio.
- Invalidación: la regla que decide cuándo un dato local deja de ser aceptable.

No existe “consistencia perfecta” gratis en móvil. Existe consistencia elegida conscientemente según coste/riesgo.

```swift
// ❌ Sin política de consistencia — devuelve cache siempre, aunque tenga 3 días
func fetchCatalog() async throws -> [Product] {
    if let cached = try? await store.load() {
        return cached.products  // ¿Cuándo caducó? Nadie lo sabe
    }
    return try await remote.fetchProducts()
}

// ✅ Con política explícita — la regla es visible y testeable
func fetchCatalog() async throws -> [Product] {
    do {
        let fresh = try await remote.fetchProducts()
        try? await store.save(products: fresh, timestamp: now())
        return fresh
    } catch {
        guard let cached = try? await store.load() else { throw error }
        switch policy.freshness(now: now(), lastUpdatedAt: cached.timestamp) {
        case .fresh:    return cached.products
        case .stale:    throw error  // Cache vieja: honestidad primero
        }
    }
}
```

La diferencia: en el primer caso la “política” es implícita (devolver siempre). En el segundo es explícita, testeable, y documentada.

---

## Modelo mental: fecha de caducidad + contexto

Piensa en leche en la nevera.

- Si está en fecha, probablemente es válida.
- Si caducó, no la usas.
- Si estás en emergencia y no hay alternativa, quizá toleras una ventana extra con aviso.

En software, esa “fecha” suele ser `timestamp + TTL`, pero además importa el contexto de negocio.

```mermaid
flowchart TD
    DATA["Dato en cache"] --> AGE{"Edad < TTL?"}
    AGE -->|"Si"| VALID["Usable"]
    AGE -->|"No"| STALE["Stale"]
    STALE --> NET{"Red disponible?"}
    NET -->|"Si"| REFRESH["Refrescar remoto"]
    NET -->|"No"| POLICY{"Politica negocio"}
    POLICY -->|"Permite stale"| SHOW["Mostrar con aviso"]
    POLICY -->|"No permite"| FAIL["Error + retry"]
```

Lectura del diagrama:

→ **Dato en cache → ¿Edad < TTL?**: la primera pregunta siempre es sobre frescura. Un dato que acaba de guardarse hace 30 segundos y tiene TTL de 5 minutos es "Usable" directamente, sin ir a red.

→ **Stale → ¿Red disponible?**: cuando el dato ha expirado, la decisión se desdobla según conectividad. Con red: refrescar. Sin red: depende de la política de negocio.

→ **Sin red → Política de negocio**: este es el nodo clave del diseño. La pregunta no es técnica — es de producto. "¿Prefiero mostrar un dato viejo con aviso, o bloquear al usuario hasta que haya red?" La respuesta depende del contexto: Catalog puede permitir stale; Payments no.

→ **Mostrar con aviso** vs **Error + retry**: ambas son respuestas válidas. La trampa es la tercera opción implícita: mostrar datos viejos sin avisar. Eso es lo que este diseño explícitamente descarta.

---

## Relación con DDD y bounded contexts

La consistencia no es solo técnica. Depende del bounded context.

Ejemplo:

- `Catalog`: tolera cierto stale breve.
- `Payments`: stale puede ser inaceptable.

Por eso no copiamos la misma política de consistencia a todas las features.

Supuesto de este curso:

- estamos en `Catalog`, donde frescura alta es importante pero no crítica a nivel transaccional inmediato.

---

## Cuándo SÍ y cuándo NO usar TTL como núcleo

### Cuándo SÍ

- datos de lectura frecuentes y cambios moderados;
- necesidad de UX rápida offline/intermitente;
- equipo que prioriza simplicidad en etapa de evolución.

### Cuándo NO

- datos con impacto legal/financiero instantáneo;
- cambios remotos muy frecuentes donde TTL fijo rompe expectativas;
- escenarios donde ya dispones de invalidación por eventos en tiempo real y la necesitas.

TTL no es malo. TTL sin contexto sí.

---

## Estrategias A/B/C de consistencia

### Opción A: TTL fijo + network-first + fallback (decisión de etapa)

Ventajas:

- simple de implementar y explicar;
- buen equilibrio inicial entre frescura y resiliencia.

Costes:

- no se adapta dinámicamente;
- puede aumentar latencia en red lenta.

### Opción B: cache-first + refresh background

Ventajas:

- UX inicial muy rápida.

Costes:

- más riesgo de stale percibido;
- requiere gestión visual de frescura más cuidada.

### Opción C: invalidación por eventos (push/websocket)

Ventajas:

- frescura cercana a tiempo real.

Costes:

- complejidad alta de infraestructura/observabilidad.

Trigger para evolucionar A -> B/C:

- métricas de latencia o quejas de stale superan umbral de producto durante varias iteraciones.

---

## Diseño de política explícita

```swift
import Foundation

struct FreshnessPolicy: Sendable {
    let maxAge: TimeInterval

    func freshness(now: Date, lastUpdatedAt: Date) -> Freshness {
        let age = now.timeIntervalSince(lastUpdatedAt)
        if age < maxAge {
            return .fresh
        }
        return .stale(age: age)
    }
}

enum Freshness: Sendable, Equatable {
    case fresh
    case stale(age: TimeInterval)
}
```

La política devuelve estado semántico, no solo booleano. Esto mejora decisiones en Application/UI.

---

## Repositorio cacheado con política

```swift
import Foundation

protocol Clock: Sendable {
    func now() -> Date
}

struct SystemClock: Clock {
    func now() -> Date { Date() }
}

struct CachedProductRepository: ProductRepository, Sendable {
    private let remote: any ProductRepository
    private let store: any ProductStore
    private let policy: FreshnessPolicy
    private let clock: any Clock

    init(
        remote: any ProductRepository,
        store: any ProductStore,
        policy: FreshnessPolicy,
        clock: any Clock = SystemClock()
    ) {
        self.remote = remote
        self.store = store
        self.policy = policy
        self.clock = clock
    }

    func loadAll() async throws -> [Product] {
        do {
            let products = try await remote.loadAll()
            try await store.save(CachedProducts(products: products, timestamp: clock.now()))
            return products
        } catch {
            guard let cached = try await store.load() else {
                throw error
            }

            switch policy.freshness(now: clock.now(), lastUpdatedAt: cached.timestamp) {
            case .fresh:
                return cached.products
            case .stale:
                throw error
            }
        }
    }
}
```

Aquí se ve un principio clave:

- la política decide validez;
- el repositorio aplica la política;
- Application/UI consumen resultado sin conocer detalles internos de cache.

---

## Integración con UI: no ocultar stale data

Si decides devolver cache fresca tras fallo remoto, UI debería reflejarlo de forma legible cuando aporte valor.

Ejemplo de estado:

```swift
enum CatalogScreenState: Sendable, Equatable {
    case loading
    case loaded(products: [Product], freshness: Freshness)
    case error(CatalogError)
}
```

No siempre necesitas mostrar “actualizado hace X minutos”, pero el estado debe poder representarlo para casos de producto exigentes.

---

## BDD -> consistencia

### Happy path

- Given red disponible y payload válido,
- When cargo catálogo,
- Then guardo cache y retorno remoto.

### Sad path

- Given red falla y cache vigente,
- When cargo catálogo,
- Then retorno cache con frescura válida.

### Edge case

- Given red falla y cache expirada,
- When cargo catálogo,
- Then retorno error (sin fingir frescura).

Esta trazabilidad evita decisiones ambiguas cuando aparecen incidencias.

---

## TDD de política de consistencia

El TDD de consistencia tiene tres focos: la política (matemática del TTL), el repositorio (integración del patrón), y los edge cases (exactamente en el límite).

### Paso 1 — Tests de `FreshnessPolicy` (pura, sin IO)

```swift
// Test: age < TTL → fresh
func test_freshness_isFresh_whenWithinTTL() {
    let policy = FreshnessPolicy(maxAge: 300)
    let now = Date(timeIntervalSince1970: 1000)
    let last = Date(timeIntervalSince1970: 800)  // 200s atrás
    XCTAssertEqual(policy.freshness(now: now, lastUpdatedAt: last), .fresh)
}

// Test: age > TTL → stale
func test_freshness_isStale_whenBeyondTTL() {
    let policy = FreshnessPolicy(maxAge: 300)
    let now = Date(timeIntervalSince1970: 1301)
    let last = Date(timeIntervalSince1970: 1000)  // 301s atrás
    guard case .stale = policy.freshness(now: now, lastUpdatedAt: last) else {
        return XCTFail("Expected .stale")
    }
}
```

Estos tests pasan en milisegundos porque `FreshnessPolicy` es pura — sin IO, sin red, sin store.

### Paso 2 — Implementación mínima

```swift
struct FreshnessPolicy: Sendable {
    let maxAge: TimeInterval
    func freshness(now: Date, lastUpdatedAt: Date) -> Freshness {
        now.timeIntervalSince(lastUpdatedAt) <= maxAge ? .fresh : .stale(age: now.timeIntervalSince(lastUpdatedAt))
    }
}
```

### Paso 3 — Extraer reloj inyectable

El reloj inyectado es lo que hace posible que los tests de repositorio sean deterministas. Sin él, necesitarías `Task.sleep` en los tests (lento y frágil):

```swift
// En vez de: let now = Date()
// Usar: let currentTime = clock.now()
struct FixedClock: Clock, @unchecked Sendable {
    let date: Date
    func now() -> Date { date }
}
```

### Paso 4 — Tests de integración cache + repositorio

```swift
// Fallback válido: cache fresca cuando falla la red
func test_loadsFromCache_whenRemoteFailsAndCacheIsFresh() async throws {
    let policy = FreshnessPolicy(maxAge: 300)
    let clock = FixedClock(date: Date(timeIntervalSince1970: 1000))
    let store = CatalogCacheStoreStub(
        cached: CachedCatalog(
            products: [Product(id: "p1", title: "Widget", price: 9.99)],
            timestamp: Date(timeIntervalSince1970: 800)  // 200s atrás < 300s TTL
        )
    )
    let sut = makeSUT(remoteError: CatalogError.network, store: store, policy: policy, clock: clock)
    let result = try await sut.fetchCatalog()
    XCTAssertEqual(result.map(\.id), ["p1"])
}

// Sin fallback: cache expirada cuando falla la red → propaga error
func test_throwsError_whenRemoteFailsAndCacheIsStale() async {
    let policy = FreshnessPolicy(maxAge: 300)
    let clock = FixedClock(date: Date(timeIntervalSince1970: 2000))
    let store = CatalogCacheStoreStub(
        cached: CachedCatalog(products: [], timestamp: Date(timeIntervalSince1970: 1000))
        // 1000s atrás >> 300s TTL → stale
    )
    let sut = makeSUT(remoteError: CatalogError.network, store: store, policy: policy, clock: clock)
    do {
        _ = try await sut.fetchCatalog()
        XCTFail("Expected error")
    } catch {
        XCTAssertTrue(error is CatalogError)
    }
}
```

---

## Tests deterministas (mínimo y realista)

```swift
import XCTest

final class FreshnessPolicyTests: XCTestCase {
    func test_freshness_isFresh_whenAgeLessThanMaxAge() {
        let policy = FreshnessPolicy(maxAge: 300)
        let now = Date(timeIntervalSince1970: 1000)
        let timestamp = Date(timeIntervalSince1970: 800)

        XCTAssertEqual(policy.freshness(now: now, lastUpdatedAt: timestamp), .fresh)
    }

    func test_freshness_isStale_whenAgeExceedsMaxAge() {
        let policy = FreshnessPolicy(maxAge: 300)
        let now = Date(timeIntervalSince1970: 1301)
        let timestamp = Date(timeIntervalSince1970: 1000)

        guard case .stale = policy.freshness(now: now, lastUpdatedAt: timestamp) else {
            return XCTFail("Expected stale")
        }
    }
}

final class CachedProductRepositoryConsistencyTests: XCTestCase {
    func test_loadAll_deliversCacheOnRemoteFailure_whenCacheIsFresh() async throws {
        let clock = FixedClock(now: Date(timeIntervalSince1970: 1000))
        let store = ProductStoreStub(cached: CachedProducts(products: [makeProduct("1")], timestamp: Date(timeIntervalSince1970: 900)))
        let remote = ProductRepositoryFailingStub(error: CatalogError.connectivity)
        let sut = CachedProductRepository(remote: remote, store: store, policy: FreshnessPolicy(maxAge: 300), clock: clock)

        let products = try await sut.loadAll()

        XCTAssertEqual(products.count, 1)
    }

    func test_loadAll_throwsOnRemoteFailure_whenCacheIsStale() async {
        let clock = FixedClock(now: Date(timeIntervalSince1970: 2000))
        let store = ProductStoreStub(cached: CachedProducts(products: [makeProduct("1")], timestamp: Date(timeIntervalSince1970: 1000)))
        let remote = ProductRepositoryFailingStub(error: CatalogError.connectivity)
        let sut = CachedProductRepository(remote: remote, store: store, policy: FreshnessPolicy(maxAge: 300), clock: clock)

        await XCTAssertThrowsErrorAsync(try await sut.loadAll())
    }
}
```

---

## Concurrencia: dónde se rompe de verdad

Riesgo típico:

- dos cargas concurrentes guardan cache con orden no determinista;
- estado final puede quedar desfasado.

Mitigación:

- store serializado en `actor`;
- política clara de resolución (última escritura gana o versión).

```swift
actor InMemoryProductStore: ProductStore {
    private var cached: CachedProducts?

    func save(_ value: CachedProducts) {
        cached = value
    }

    func load() -> CachedProducts? {
        cached
    }
}
```

No metas `@MainActor` en almacenamiento por “silenciar warnings”. Aisla donde corresponde.

---

## Anti-ejemplos y depuración

### Anti-ejemplo 1: TTL hardcoded sin explicación

Problema:

- nadie sabe por qué `maxAge = 173`.

Corrección:

- documentar criterio y trigger de revisión.

### Anti-ejemplo 2: reloj real en tests

Problema:

- tests flaky y lentos.

Corrección:

- inyectar `Clock` fijo.

### Anti-ejemplo 3: devolver stale siempre “para no fallar”

Problema:

- ocultas incidentes reales y engañas UX.

Corrección:

- separar `fresh` vs `stale` con policy explícita.

### Depuración práctica

1. loggear edad del cache y decisión de policy;
2. verificar timestamps guardados;
3. reproducir con reloj fijo;
4. ejecutar tests de concurrencia con cargas solapadas.

---

## ADR corto de la lección

```markdown
## ADR-007: Politica de consistencia de Catalog basada en TTL y fallback controlado
- Estado: Aprobado
- Contexto: necesidad de equilibrio entre disponibilidad y frescura
- Decisión: aplicar network-first con fallback a cache solo cuando politica de frescura lo permita
- Consecuencias: mejor resiliencia sin ocultar stale data expirada
- Fecha: 2026-02-07
```

---

## Matriz de pruebas de consistencia

| Tipo de prueba | Qué valida | Coste | Frecuencia |
| --- | --- | --- | --- |
| Unit policy | cálculo de frescura/expiración | Bajo | Cada cambio |
| Integration cache+repo | fallback real bajo fallos de red | Medio | Por feature |
| UI/E2E | representación de estado fresco/expirado | Alto | Selectivo |

---

## Checklist de calidad

- [ ] Política de consistencia documentada con supuestos.
- [ ] Invalidación centralizada, no repartida por capas.
- [ ] Tests deterministas de TTL con reloj inyectado.
- [ ] Concurrencia de store protegida.
- [ ] UI no disfraza stale expirado como dato fresco.

---

## Cierre

Sin política de consistencia, cache es una lotería. Con política explícita y tests sólidos, cache se convierte en una ventaja competitiva: app rápida y resiliente sin sacrificar honestidad de datos.
---

## Matriz rápida para elegir TTL

| Contexto | Volatilidad | Tolerancia stale | TTL sugerido inicial |
| --- | --- | --- | --- |
| Catalog general | Media | Media | 5 min |
| Pricing sensible | Alta | Baja | <= 1 min |
| Contenido editorial | Baja | Alta | 15-30 min |

La tabla no sustituye métricas reales, pero ayuda a arrancar con criterio explícito.

---

## Ejercicio guiado: invalidación de cache por evento de dominio

**Objetivo:** Implementar y testear la invalidación de cache cuando un evento de dominio indica que los datos han cambiado.

**Instrucciones:**

1. En `FeatureCatalogData`, localiza (o crea) un protocolo `CacheInvalidator` con un método `invalidate() async`.
2. Implementa un `TTLCacheInvalidator` que borre el cache local cuando se invoca.
3. Escribe un test que simule este flujo:
   - Se cargan productos y se guardan en cache.
   - Se dispara un evento de invalidación (simulando que el backend notificó cambio).
   - La siguiente carga debe ir a red, no a cache.

**Criterios de éxito:**

- El test pasa con `swift test --filter CacheInvalidat`.
- El invalidador no conoce SwiftData ni detalles de persistencia.
- La invalidación es explícita (no depende de timing ni de TTL expirado).

<details>
<summary>Solución de referencia</summary>

```swift
// Sources/FeatureCatalogData/CacheInvalidator.swift

protocol CacheInvalidator: Sendable {
    func invalidate() async throws
}

struct StoreCacheInvalidator: CacheInvalidator, Sendable {
    private let store: any CatalogCacheStore  // Scaffold: CatalogCacheStore, no ProductStore

    init(store: any CatalogCacheStore) {
        self.store = store
    }

    func invalidate() async throws {
        try await store.clear()  // Scaffold tiene clear() — más semántico que save([])
    }
}

// Tests/FeatureCatalogDataTests/CacheInvalidatorTests.swift

final class StoreCacheInvalidatorTests: XCTestCase {

    func test_invalidate_clearsStore() async throws {
        let store = InMemoryCatalogCacheStore()
        let products = [Product(id: "p-1", title: "Widget", price: 9.99)]  // title, no name
        try await store.save(products: products, timestamp: Date())

        let invalidator = StoreCacheInvalidator(store: store)
        try await invalidator.invalidate()

        let cached = try await store.load()
        XCTAssertNil(cached, "Tras invalidar, el store debe estar vacío")
    }
}
```

> **Nota scaffold:** El protocolo es `CatalogCacheStore` (no `ProductStore`), tiene `clear()` explícito, y `save` usa etiqueta `products:timestamp:`. El modelo usa `title: String` (no `name`) y `price: Double`.

La razón de separar la invalidación en su propio protocolo: permite componer distintas estrategias sin modificar el repositorio de cache — por TTL expirado, por evento push del backend, o por acción explícita del usuario ("actualizar catálogo").

</details>

---

## Implementación en tu proyecto

### Archivos del scaffold

| Archivo | Qué contiene |
|---|---|
| `Sources/FeatureCatalogData/CatalogDataContracts.swift` | `CatalogCacheStore` con `load()`, `save(products:timestamp:)`, `clear()` |
| `Sources/FeatureCatalogData/CachedCatalogRepository.swift` | La política de consistencia ya implementada |
| `Sources/FeatureCatalogData/InMemoryCatalogStores.swift` | Stubs en memoria para tests de política |

### Divergencias respecto a los ejemplos del curso

| Lección | Scaffold real |
|---|---|
| `ProductStore` | `CatalogCacheStore` |
| `store.save(_:timestamp:)` | `store.save(products:timestamp:)` — etiquetas explícitas |
| `store.save([], timestamp: .distantPast)` para invalidar | `store.clear()` — método semántico explícito |
| `product.name` | `product.title` |
| `Price(amount:currency:)` | `Double` — precio simple |
| `CachedProducts` | `CachedCatalog` |
| `ProductRepository.loadAll()` | `CatalogRepository.fetchCatalog()` |

### La `FreshnessPolicy` como struct independiente

El scaffold integra la política de frescura directamente en `CachedCatalogRepository` como lógica interna (método `isValid`). Extraerla a un `FreshnessPolicy` struct separado (como muestra esta lección) es una refactorización válida que mejora la testeabilidad de la política en aislamiento. Si lo haces, recuerda que el scaffold ya tiene `ttlSeconds` como parámetro del constructor.

---

## Qué sigue

[**Lección 14: Observabilidad →**](./03-observabilidad.md) — Cómo saber qué está pasando en producción: métricas de carga, cache hits, y errores sin afectar la lógica de negocio.

