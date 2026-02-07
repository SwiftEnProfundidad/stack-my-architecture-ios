# Caching y offline

## Qué problema resolvemos realmente

Si una app móvil solo funciona con red perfecta, no está lista para producción. El usuario entra al metro, cambia de zona de cobertura, recibe latencia alta o pierde conexión por segundos. En esos momentos, el sistema no debe derrumbarse en "error y reintentar" si tiene datos recientes que todavía aportan valor.

Esta lección define cómo incorporar cache/offline de forma profesional:

- sin contaminar el core de negocio,
- sin esconder inconsistencias,
- sin convertir la arquitectura en un laberinto.

---

## Definición simple

Cache es guardar una copia local de datos para responder rápido o degradar bien cuando falla la fuente principal.

Offline-friendly no significa “funciona todo sin internet”. Significa “las rutas críticas siguen siendo útiles en escenarios de conectividad degradada”.

---

## Modelo mental interno

Piensa en tres niveles de verdad:

1. **Fuente primaria**: backend remoto (verdad canónica).
2. **Fuente secundaria**: caché local (verdad temporal).
3. **UI**: representación con contexto de frescura/error.

La clave no es esconder que el dato puede estar viejo. La clave es decidir cuándo ese dato temporal sigue siendo mejor que no mostrar nada.

```mermaid
flowchart TD
    U["Usuario abre Catalog"] --> R{"Remote disponible?"}
    R -->|"Sí"| REM["Cargar remoto"]
    REM --> SAVE["Guardar cache + timestamp"]
    SAVE --> SHOW_FRESH["Mostrar fresco"]

    R -->|"No"| CACHE{"Cache válido?"}
    CACHE -->|"Sí"| SHOW_CACHE["Mostrar cache"]
    CACHE -->|"No"| SHOW_ERR["Mostrar error"]
```

---

## Cuándo sí / cuándo no usar cache en este contexto

## Cuándo sí

- Catálogo de productos que cambia moderadamente.
- Experiencia donde “algo útil” es mejor que “pantalla vacía”.
- Dominio donde una ventana corta de desactualización es aceptable.

## Cuándo no (o con más cuidado)

- Datos financieros en tiempo real.
- Operaciones críticas con impacto legal/contable inmediato.
- Flujos donde stale data puede inducir decisiones erróneas graves.

---

## Estrategia elegida para Etapa 3

Estrategia base de la etapa:

- **Network-first**.
- Fallback a cache si falla remoto.
- Validez por TTL explícito.

Por qué:

- mantiene frescura cuando hay red,
- mantiene continuidad cuando no la hay,
- y su complejidad es manejable para el nivel actual.

---

## Diseño por capas (Clean + DDD)

## Domain

- `Product`, `Price`, `CatalogError`.
- Sin detalles de archivo, JSON o HTTP.

## Application

- caso de uso `LoadProductsUseCase` depende de `ProductRepository`.
- no sabe si hay cache o remoto.

## Infrastructure

- `RemoteProductRepository`.
- `ProductStore` (persistencia local).
- `CachedProductRepository` como decorador.

## Interface

- estado UI coherente (`loading/loaded/empty/error`).
- mensaje adecuado según política de fallback.

---

## Implementación mínima (mecánica)

```swift
final class CachedProductRepository: ProductRepository, @unchecked Sendable {
    private let remote: any ProductRepository
    private let store: any ProductStore
    private let maxAge: TimeInterval
    private let now: @Sendable () -> Date

    init(
        remote: any ProductRepository,
        store: any ProductStore,
        maxAge: TimeInterval = 300,
        now: @Sendable @escaping () -> Date = { Date() }
    ) {
        self.remote = remote
        self.store = store
        self.maxAge = maxAge
        self.now = now
    }

    func loadAll() async throws -> [Product] {
        do {
            let fresh = try await remote.loadAll()
            try? await store.save(fresh, timestamp: now())
            return fresh
        } catch {
            if let cached = try? await store.load(), isValid(cached.timestamp) {
                return cached.products
            }
            throw error
        }
    }

    private func isValid(_ timestamp: Date) -> Bool {
        now().timeIntervalSince(timestamp) < maxAge
    }
}
```

Este código demuestra el patrón central:
- primero remoto,
- si falla remoto, fallback condicionado por validez de cache.

---

## Implementación realista enterprise (composición)

```mermaid
flowchart LR
    UC["LoadProductsUseCase"] --> CACHED["CachedProductRepository"]
    CACHED --> REMOTE["RemoteProductRepository"]
    CACHED --> STORE["FileProductStore"]
    REMOTE --> HTTP["HTTPClient chain"]
    HTTP --> NET["API"]
```

Punto crítico de diseño:
- el UseCase no cambia al introducir cache.
- solo cambia el Composition Root.

Esto es exactamente lo que buscábamos desde Etapa 1: evolución por composición, no por reescritura.

---

## Concurrencia y seguridad

## Aislamiento

- `CachedProductRepository` puede usar actor-store o lock/serialización interna.
- `ProductStore` debe definir claramente si sus operaciones son thread-safe.

## Cancelación

Si la carga se cancela a mitad:
- no se debe publicar estado tardío en UI,
- y no se debe dejar el flujo en estado incoherente.

## Sendable

Los tipos que cruzan tasks deben cumplir sendability o justificar excepciones en test doubles.

---

## El puerto ProductStore

Antes de los tests, necesitamos el protocolo que define la persistencia local:

```swift
protocol ProductStore: Sendable {
    func load() async throws -> CachedProducts?
    func save(_ products: [Product], timestamp: Date) async throws
}

struct CachedProducts: Sendable {
    let products: [Product]
    let timestamp: Date
}
```

**Linea por linea:**

- `load()` — Devuelve los productos guardados con su timestamp, o `nil` si no hay nada en cache.
- `save(_:timestamp:)` — Guarda productos con la fecha en que se obtuvieron. El timestamp es clave para el TTL.
- `CachedProducts` — Agrupa productos + timestamp. El timestamp no es "cuando se guardo", sino "cuando se obtuvo del servidor".

En Etapa 3 implementaremos este protocolo con SwiftData. Por ahora los tests usan un stub.

## Helper makeSUT para tests de cache

```swift
private func makeSUT(
    remoteResult: Result<[Product], CatalogError> = .success([]),
    cached: CachedProducts? = nil,
    maxAge: TimeInterval = 300,
    now: @escaping @Sendable () -> Date = { Date() }
) -> CachedProductRepository {
    let remote = ProductRepositoryStub(result: remoteResult)
    let store = ProductStoreStub(cached: cached)
    return CachedProductRepository(
        remote: remote,
        store: store,
        maxAge: maxAge,
        now: now
    )
}
```

**Por que tantos parametros con valores por defecto:** Cada test solo configura lo que le importa. Si un test verifica el TTL, pasa `maxAge` y `now`. Si verifica el happy path, solo pasa `remoteResult`. Los valores por defecto cubren el caso mas comun (exito, sin cache, 5 minutos de TTL, reloj real).

**`now: @escaping @Sendable () -> Date`** — En vez de usar `Date()` directamente, inyectamos un closure que devuelve la fecha. En tests, pasamos una fecha fija. Esto hace que los tests de tiempo sean **deterministas**: no dependen de cuando ejecutes el test.

## Pruebas que no pueden faltar

### 1) Remoto exito: devuelve fresco + guarda cache

```swift
func test_loadAll_onRemoteSuccess_returnsFreshAndSavesToStore() async throws {
    let products = [makeProduct(id: "1"), makeProduct(id: "2")]
    let store = ProductStoreSpy()
    let remote = ProductRepositoryStub(result: .success(products))
    let fixedDate = Date(timeIntervalSince1970: 1000)
    let sut = CachedProductRepository(
        remote: remote,
        store: store,
        maxAge: 300,
        now: { fixedDate }
    )

    let result = try await sut.loadAll()

    // ASSERT 1: devuelve los productos del remoto
    XCTAssertEqual(result, products)
    // ASSERT 2: los guardo en el store con el timestamp correcto
    XCTAssertEqual(store.savedProducts, products)
    XCTAssertEqual(store.savedTimestamp, fixedDate)
}
```

**Que verifica:** Cuando el remoto responde con exito, el `CachedProductRepository` hace dos cosas: (1) devuelve los productos frescos, y (2) los guarda en el store para uso futuro. Si alguien borrara la linea `try? await store.save(...)`, el segundo assert fallaria.

**ProductStoreSpy:** Es un spy (no un stub) porque ademas de devolver datos, **registra** que se guardo y cuando. Tiene propiedades `savedProducts` y `savedTimestamp` que los tests verifican.

### 2) Remoto fallo + cache valido: devuelve cache

```swift
func test_loadAll_onRemoteFailureWithValidCache_returnsCached() async throws {
    let cachedProducts = [makeProduct(id: "cached-1")]
    let cacheTime = Date(timeIntervalSince1970: 1000)
    let now = Date(timeIntervalSince1970: 1200) // 200s despues (< 300s TTL)

    let sut = makeSUT(
        remoteResult: .failure(.connectivity),
        cached: CachedProducts(products: cachedProducts, timestamp: cacheTime),
        maxAge: 300,
        now: { now }
    )

    let result = try await sut.loadAll()

    XCTAssertEqual(result, cachedProducts)
}
```

**Que verifica:** Si el remoto falla pero hay cache guardado hace menos de 300 segundos (el TTL), devuelve el cache. El usuario ve productos "un poco viejos" en vez de una pantalla de error. Esto es el **fallback**.

**Los numeros:** `cacheTime = 1000`, `now = 1200`. La diferencia es 200 segundos. El TTL es 300. Como `200 < 300`, el cache es valido.

### 3) Remoto fallo + cache expirado: propaga error

```swift
func test_loadAll_onRemoteFailureWithExpiredCache_throwsError() async {
    let cachedProducts = [makeProduct(id: "old")]
    let cacheTime = Date(timeIntervalSince1970: 1000)
    let now = Date(timeIntervalSince1970: 1401) // 401s despues (> 300s TTL)

    let sut = makeSUT(
        remoteResult: .failure(.connectivity),
        cached: CachedProducts(products: cachedProducts, timestamp: cacheTime),
        maxAge: 300,
        now: { now }
    )

    do {
        _ = try await sut.loadAll()
        XCTFail("Expected error but got success")
    } catch let error as CatalogError {
        XCTAssertEqual(error, .connectivity)
    } catch {
        XCTFail("Unexpected error type: \(error)")
    }
}
```

**Que verifica:** Si el remoto falla Y el cache ha expirado (401 > 300), **no** devuelve datos viejos. Propaga el error. Esto protege al usuario de ver datos que ya no son confiables.

**La diferencia con el test anterior:** Solo cambia `now`. En el test 2, `now = 1200` (cache valido). Aqui, `now = 1401` (cache expirado). Un solo segundo de diferencia en la logica cambia el comportamiento completo.

### 4) Remoto fallo + sin cache: propaga error

```swift
func test_loadAll_onRemoteFailureWithNoCache_throwsError() async {
    let sut = makeSUT(
        remoteResult: .failure(.connectivity),
        cached: nil
    )

    do {
        _ = try await sut.loadAll()
        XCTFail("Expected error but got success")
    } catch let error as CatalogError {
        XCTAssertEqual(error, .connectivity)
    } catch {
        XCTFail("Unexpected error type: \(error)")
    }
}
```

**Que verifica:** Si no hay cache guardado (primera vez que se abre la app, o se borro el cache), y el remoto falla, se propaga el error. No hay magia: si no tienes datos ni remotos ni locales, no puedes mostrar nada.

### 5) TTL determinista: el reloj inyectado decide la validez

```swift
func test_loadAll_cacheExactlyAtTTL_isStillValid() async throws {
    let cacheTime = Date(timeIntervalSince1970: 1000)
    let now = Date(timeIntervalSince1970: 1300) // Exactamente 300s = TTL

    let cachedProducts = [makeProduct(id: "edge")]
    let sut = makeSUT(
        remoteResult: .failure(.connectivity),
        cached: CachedProducts(products: cachedProducts, timestamp: cacheTime),
        maxAge: 300,
        now: { now }
    )

    let result = try await sut.loadAll()
    XCTAssertEqual(result, cachedProducts)
}
```

**Que verifica:** Un edge case critico: el cache tiene exactamente la edad del TTL (300s). La decision de diseño es que `< maxAge` es valido, asi que exactamente 300 esta **en el limite**. Si la condicion fuera `<=`, este test pasaria. Si fuera `<`, fallaria. El test documenta explicitamente que decision tomamos.

**Clave de los tests de cache:**

- **Nunca usar reloj real** (`Date()`) en tests de tiempo. Si lo haces, el test puede pasar o fallar dependiendo de la velocidad del CI.
- **Inyectar `now`** con un closure que devuelve una fecha fija. Asi el test es determinista.
- **Probar los limites** (exactamente en el TTL, un segundo antes, un segundo despues).
- **Usar spy para el store** para verificar que se guarda correctamente, no solo que se lee.

---

## Trade-offs A/B/C de estrategia de cache

## Opción A — network-first + fallback (actual)

Ventaja:
- máxima frescura cuando hay red.

Coste:
- latencia inicial depende de red.

Riesgo:
- UX más lenta en conexiones pobres aunque exista cache válido.

## Opción B — cache-first + refresh en background

Ventaja:
- respuesta inmediata.

Coste:
- más complejidad de estado (mostrar stale + actualizar luego).

Riesgo:
- mayor riesgo de mostrar datos viejos como actuales.

## Opción C — stale-while-revalidate avanzado

Ventaja:
- UX muy fluida + consistencia progresiva.

Coste:
- complejidad alta (versionado, invalidaciones finas, conflictos).

Riesgo:
- sobreingeniería temprana.

Decisión de etapa:
- A, con trigger claro para pasar a B/C cuando métricas de latencia/UX lo exijan.

---

## Anti-patrones (y corrección)

## Anti-patrón 1: cache global sin ownership

Corrección:
- encapsular en repositorio/store con contrato claro.

## Anti-patrón 2: TTL hardcoded en múltiples sitios

Corrección:
- centralizar política en configuración/constructor.

## Anti-patrón 3: cache usado como sustituto de dominio

Corrección:
- mantener mapeo y validación en infraestructura/domain adecuados.

## Anti-patrón 4: fallback silencioso sin observabilidad

Corrección:
- loggear transición “remote fail -> cached response”.

---

## Skills aplicadas en esta lección

- `swift-concurrency`: cancelación, aislamiento y sendability en ruta de carga.
- `swiftui-expert-skill`: estado de UI coherente ante fallback.
- `windsurf-rules-ios` (si aplica): composición limpia y separación de responsabilidades.

---

## Checklist de cierre

- [ ] Existe `CachedProductRepository` por composición, no acoplamiento.
- [ ] Política TTL explícita y testeada.
- [ ] Fallback offline cubierto por tests.
- [ ] Core (Domain/Application) sin contaminación de detalles de cache.
- [ ] Decisión de estrategia documentada con trade-offs.

---

## Siguiente paso

Con cache funcional, toca resolver una pregunta crítica: **cuánta desactualización es aceptable y cuándo invalidar datos**.

**Siguiente:** [Consistencia e invalidación →](02-consistencia.md)

---

## Máquina de estados de UI para cache/offline

Cuando introduces cache, UI necesita modelar claramente qué está ocurriendo. Si no, aparecen estados ambiguos.

```mermaid
stateDiagram-v2
    [*] --> Loading
    Loading --> LoadedFresh: remoto OK
    Loading --> LoadedCached: remoto falla + cache valida
    Loading --> Error: remoto falla + cache invalida
    LoadedFresh --> Loading: refresh manual
    LoadedCached --> Loading: refresh manual
    Error --> Loading: retry
```

Esta máquina evita frases ambiguas como “está cargando pero también mostrando error”.

---

## Wiring en Composition Root

Para mantener arquitectura limpia, el wiring de cache vive fuera del core.

```swift
import Foundation

struct CatalogComposer {
    let baseURL: URL
    let httpClient: any HTTPClient
    let store: any ProductStore

    func makeUseCase() -> LoadProductsUseCase {
        let remote = RemoteProductRepository(httpClient: httpClient, baseURL: baseURL)
        let cached = CachedProductRepository(
            remote: remote,
            store: store,
            maxAge: 300
        )
        return LoadProductsUseCase(repository: cached)
    }
}
```

Con este patrón puedes reemplazar estrategia de cache sin tocar Domain/Application.

---

## Runbook de depuración para fallos de cache

Si en producción reportan “a veces veo productos viejos”:

1. verificar política TTL vigente y valor configurado;
2. revisar logs de decisión (`remote`, `fallback`, `cache age`);
3. comprobar timestamps reales guardados;
4. reproducir con clock fijo en tests;
5. validar si UI comunica frescura o no.

Si reportan “nunca uso cache aunque no haya red”:

1. revisar condición de validez;
2. comprobar lectura/escritura del store;
3. validar traducción de error remoto;
4. verificar que cancelación no interrumpe guardado.

---

## Métricas básicas para decidir evolución de estrategia

Métricas sugeridas:

- `fallback_rate`: porcentaje de cargas servidas desde cache;
- `stale_error_rate`: porcentaje de fallos por cache inválida + remoto fallido;
- `catalog_load_p95`: latencia p95 percibida por usuario.

Con estas métricas puedes decidir cuándo mantener `network-first` o pasar a `cache-first`.

---

## Cierre extendido

Caching/offline bien diseñado no trata de esconder problemas de red; trata de diseñar una experiencia honesta y resistente. Esa diferencia marca el paso de “app que funciona en demo” a “app confiable en la vida real”.

---

## Modelo de coste de estrategia de cache

Evalúa cada estrategia en tres costes:

- coste de implementación;
- coste de mantenimiento;
- coste de incidente por dato stale.

Con esta visión, eliges políticas de cache por impacto total, no por preferencia técnica.

---

## Criterio de UX mínimo

Si se sirve cache, la interfaz nunca debe dar impresión de “dato en tiempo real” sin indicador o semántica de frescura adecuada.
