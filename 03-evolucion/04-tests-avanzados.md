# Tests avanzados

## Ruta scaffold relacionada

- `apps/ios/ArchitectureKit/Sources/` para implementación de código real de esta lección.
- `apps/ios/ArchitectureKit/Tests/` para validación y regresión de contratos.
- `apps/ios/ArchitectureHostApp/` cuando la lección impacta navegación/UI integrada.

## Objetivo de aprendizaje

Al finalizar esta lección vas a poder diseñar y escribir pruebas avanzadas para escenarios donde la mayoría de equipos rompe producción: cancelación, concurrencia, timing y backpressure. El foco es que las pruebas sean deterministas, rápidas y útiles para guiar decisiones de arquitectura.

En versión simple: si solo pruebas caminos felices, el día malo llega en producción. Las pruebas avanzadas entrenan al sistema para días malos.

---

## Definición simple

Un test avanzado valida comportamientos con dimensión temporal o concurrente que no se capturan con assertions lineales de input/output.

Ejemplos de esta etapa:

- cancelación correcta de tareas;
- expiración temporal (TTL) sin reloj real;
- aislamiento concurrente y `Sendable` en dobles/SUT;
- manejo de presión de eventos (backpressure);
- prevención de flakiness.

---

## Modelo mental: túnel de viento

Un coche bonito en parado no dice nada de su estabilidad a 120 km/h. Un test avanzado es túnel de viento para tu arquitectura.

```mermaid
flowchart LR
    SPEC["Escenario BDD"] --> RISK["Riesgo temporal/concurrente"]
    RISK --> TEST["Test determinista"]
    TEST --> FEED["Feedback de diseño"]
    FEED --> HARDEN["Arquitectura mas robusta"]
```

Lectura del diagrama:

→ **Escenario BDD → Riesgo temporal/concurrente**: el punto de partida es siempre un comportamiento de negocio formulado como BDD. "Dado que el usuario navega atrás mientras carga, no se muestra resultado tardío" expresa un riesgo temporal concreto.

→ **Riesgo → Test determinista**: el riesgo se traduce en un test que controla el tiempo (Clock inyectado, no `Date()`) y la concurrencia (dobles con `actor`). Determinista significa que pasa o falla igual cada vez.

→ **Test → Feedback de diseño**: si el test es difícil de escribir, es señal de diseño deficiente — el sistema tiene demasiado acoplamiento temporal o de estado. El test actúa como crítica de arquitectura antes de que el problema llegue a producción.

→ **Feedback → Arquitectura más robusta**: el ciclo cierra. La dificultad de testear lleva a extraer protocolos, inyectar reloj, separar estado. Cada iteración produce código más fácil de testear y, por tanto, más robusto.

Sin este túnel, validas estética de código, no robustez real.

---

## Relación con BDD + TDD

BDD te dice qué comportamientos importan en negocio cuando el sistema está bajo estrés.

Ejemplos BDD reales:

- Given usuario cambia de pantalla durante carga, Then no debo mostrar resultado tardío.
- Given llegan refresh seguidos, Then debo procesar con política estable.
- Given cache expirada y red falla, Then debo fallar de forma explícita.

TDD en tests avanzados:

1. Red: expresas el comportamiento bajo estrés.
2. Green: implementas lo mínimo para cumplirlo.
3. Refactor: limpias diseño (aislamiento, clocks, actores) sin romper contrato.

---

## Bloque 1: cancelación como caso de primera clase

### Qué validar

- la tarea se cancela de verdad;
- no hay side effects posteriores a la cancelación;
- el estado de UI/Application no acaba en resultado inválido.

### Ejemplo mínimo

```swift
import XCTest

final class CancellationTests: XCTestCase {
    func test_useCase_respectsCancellation() async {
        let repository = SlowProductRepositoryStub(delayNanoseconds: 3_000_000_000)
        let sut = LoadProductsUseCase(repository: repository)

        let task = Task { try await sut.execute() }
        try? await Task.sleep(nanoseconds: 100_000_000)
        task.cancel()

        let result = await task.result

        switch result {
        case .failure(let error):
            XCTAssertTrue(error is CancellationError)
        default:
            XCTFail("Expected cancellation")
        }
    }
}
```

### Error típico

- usar `Task.detached` en capa de UI/Application y perder control de cancelación.

### Corrección

- usar `.task`/task estructurada y ownership claro.

---

## Bloque 2: tiempo controlado (TTL y deadlines)

Nunca dependas del reloj de sistema para validar expiración. Inyecta reloj.

```swift
import Foundation

protocol Clock: Sendable {
    func now() -> Date
}

struct FixedClock: Clock {
    let value: Date
    func now() -> Date { value }
}
```

### Test determinista

```swift
func test_policy_marksStale_afterMaxAge() {
    let policy = FreshnessPolicy(maxAge: 300)
    let timestamp = Date(timeIntervalSince1970: 1000)
    let now = Date(timeIntervalSince1970: 1301)

    guard case .stale = policy.freshness(now: now, lastUpdatedAt: timestamp) else {
        return XCTFail("Expected stale")
    }
}
```

Si usas `sleep(300)` en tests, estás construyendo deuda de CI.

---

## Bloque 3: concurrencia y `Sendable` en dobles de prueba

Una gran fuente de falsos verdes son dobles con estado mutable no protegido.

### Anti-ejemplo

```swift
final class UnsafeSpy: ProductRepository, @unchecked Sendable {
    var callCount = 0

    func loadAll() async throws -> [Product] {
        callCount += 1
        return []
    }
}
```

Si hay llamadas concurrentes, este spy introduce carreras.

### Ejemplo correcto con actor

```swift
actor SafeProductRepositorySpy: ProductRepository {
    private(set) var callCount = 0

    func loadAll() async throws -> [Product] {
        callCount += 1
        return []
    }

    func readCallCount() -> Int {
        callCount
    }
}
```

Regla de curso:

- `@unchecked Sendable` solo con invariante escrito y alcance controlado.

---

## Bloque 4: backpressure (presión de eventos)

### Problema real

UI emite muchos eventos de refresh (scroll, pull-to-refresh repetido, navegación rápida).

Si lanzas una tarea por evento sin política, puedes:

- saturar red;
- pisar estado;
- producir resultados fuera de orden.

### Políticas típicas

- última petición gana (cancel previous);
- serializar peticiones en actor;
- debounce/throttle en input.

```mermaid
flowchart TD
    E["Eventos refresh"] --> P{"Politica"}
    P --> C["Cancelar anterior"]
    P --> S["Serializar"]
    P --> D["Debounce"]
    C --> R["Estado estable"]
    S --> R
    D --> R
```

Lectura del diagrama:

→ **Cancelar anterior**: "última petición gana" — se cancela la tarea en curso antes de lanzar la nueva. La UI nunca muestra resultados de una carga que ya no es la más reciente. Coste: el progreso de la carga cancelada se pierde.

→ **Serializar**: las peticiones se encolan en el orden de llegada. La segunda espera a que la primera termine. Garantiza orden pero puede acumular latencia si llegan muchas peticiones seguidas.

→ **Debounce**: espera un tiempo de inactividad antes de lanzar. Un usuario que escribe rápido en búsqueda no lanza 10 peticiones — solo una cuando deja de escribir. Introduce latencia mínima intencional a cambio de no saturar la red.

→ **Estado estable**: las tres políticas convergen en el mismo objetivo — la UI nunca queda con datos de una solicitud obsoleta o en estado inconsistente.

### Test de última petición gana

```swift
func test_viewModel_lastRequestWins_underRapidRefresh() async {
    let repository = ControlledProductRepositoryStub()
    let sut = CatalogViewModel(loadProducts: LoadProductsUseCase(repository: repository))

    await sut.refresh()
    await sut.refresh()

    await repository.completeSecondRequest(with: [makeProduct("2")])
    await repository.completeFirstRequest(with: [makeProduct("1")])

    let state = await sut.state
    XCTAssertEqual(state.products.first?.id, "2")
}
```

Este test protege contra resultados fuera de orden.

---

## Bloque 5: tests de integración avanzada

Además de unit avanzada, necesitas integración avanzada para colaboración real bajo condiciones de timing.

Casos recomendados:

1. remote tarda, cache responde, luego remote completa: verificar política final.
2. cancelación en medio de request: no persistir estado parcial.
3. fallo remoto + cache válida: fallback estable.

---

## Estrategia anti-flaky

Checklist para depurar flakes:

1. ¿usas tiempo real?
2. ¿hay estado compartido entre tests?
3. ¿dependes de red externa?
4. ¿orden de completions no controlado?
5. ¿faltan awaits explícitos?

Si cualquiera da sí, tu test aún no es fiable.

```mermaid
flowchart LR
    F["Flaky"] --> T["Tiempo real"]
    F --> G["Estado global"]
    F --> N["Red real"]
    F --> O["Orden no controlado"]
    T --> FIX1["Clock inyectado"]
    G --> FIX2["SUT aislado por test"]
    N --> FIX3["Dobles de frontera"]
    O --> FIX4["Controladores de completion"]
```

Lectura del diagrama — cada flake tiene causa y cura:

→ **Tiempo real → Clock inyectado**: cualquier test que llama a `Date()` o usa `Task.sleep` para esperar resultados es flaky por diseño. La cura es inyectar un `Clock` que devuelve fechas fijas y controlar completions explícitamente.

→ **Estado global → SUT aislado**: un test que modifica un singleton, una variable `static`, o un actor compartido contamina otros tests. La cura es que cada test crea su propio SUT con `makeSUT()` — sin estado que escape entre tests.

→ **Red real → Dobles de frontera**: cualquier test que llega a la red real es lento, frágil, y depende de infraestructura externa. La cura es un doble en la frontera (`CatalogRemoteDataSource`, no en el repositorio completo) que simula respuestas sin red.

→ **Orden no controlado → Controladores de completion**: los tests de "última petición gana" no pueden depender de `Task.sleep(100ms)` para garantizar orden — si CI es lento, 100ms no es suficiente. La cura es un `ControlledStub` que expone métodos `completeFirstRequest()` / `completeSecondRequest()` para control explícito.

---

## A/B/C de profundidad de pruebas avanzadas

### Opción A: tests básicos solamente

Ventaja:

- rapidez inicial.

Coste:

- riesgo alto en producción bajo estrés.

### Opción B: casos avanzados en rutas críticas (decisión actual)

Ventaja:

- alto retorno con coste razonable.

Coste:

- diseño de dobles y clocks más sofisticado.

### Opción C: cobertura exhaustiva de todos los timings

Ventaja:

- robustez máxima teórica.

Coste:

- coste y complejidad elevados.

Trigger para escalar de B a C:

- incidentes concurrentes repetidos con impacto alto.

---

## Concurrencia Swift 6.2: puntos obligatorios

- identificar boundary de aislamiento por prueba (`@MainActor`, actor propio, no aislado);
- asegurar `Sendable` en fronteras;
- probar cancelación explícitamente;
- justificar cualquier `@unchecked Sendable`.

Anti-patrón:

- poner `@MainActor` global para callar warnings y esconder diseño incorrecto.

---

## Ejemplo de suite combinada (unit + integración)

```swift
final class CatalogAdvancedTestPlan {
    let unitCritical = [
        "FreshnessPolicy marks stale correctly",
        "ViewModel ignores result after cancellation"
    ]

    let integrationCritical = [
        "CachedRepository fallback on connectivity failure",
        "Last request wins under rapid refresh"
    ]
}
```

La idea no es tener 500 tests, sino tests correctos en puntos de máximo riesgo.

---

## ADR corto de la lección

```markdown
## ADR-008: Estrategia de pruebas avanzadas deterministas para concurrencia y tiempo
- Estado: Aprobado
- Contexto: riesgo de regresiones en cancelacion, timing y backpressure
- Decisión: introducir clocks inyectados, dobles seguros y casos avanzados en rutas criticas
- Consecuencias: mayor confianza en evoluciones con coste moderado de diseño de tests
- Fecha: 2026-02-07
```

---

## Matriz de pruebas avanzadas

| Tipo de prueba | Qué valida | Coste | Frecuencia |
| --- | --- | --- | --- |
| Cancelación | no side effects tardíos tras cancelación | Medio | Cada cambio crítico |
| Timing | expiración y deadlines deterministas | Bajo-Medio | Cada cambio de policy |
| Concurrencia | ausencia de carreras en rutas async | Medio | Por PR |
| Backpressure | orden y política bajo ráfagas | Medio-Alto | En features con eventos intensos |
| Integración avanzada | colaboración real en escenarios de estrés | Medio-Alto | Por iteración de feature |

---

## Checklist de calidad

- [ ] Hay pruebas explícitas de cancelación en flujos críticos.
- [ ] El tiempo está inyectado y controlado en tests de expiración.
- [ ] Dobles concurrentes son seguros (`actor` o invariante documentado).
- [ ] Existe al menos un test de backpressure por feature relevante.
- [ ] La suite evita flakiness por diseño, no por reintentos.

---

## Cierre

Las pruebas avanzadas son el puente entre “funciona hoy” y “seguirá funcionando cuando el sistema evolucione”. Cuando las dominas, puedes refactorizar con seguridad real, que es la moneda principal de la arquitectura enterprise.
---

## Laboratorio guiado de 45 minutos

Objetivo: practicar el ciclo completo en una ruta crítica con concurrencia.

1. escoger flujo `catalog.refresh`;
2. escribir test Red para cancelación al salir de pantalla;
3. escribir test Red para `last request wins`;
4. implementar Green mínimo;
5. refactorizar dobles a `actor` donde haga falta;
6. validar que suite corre estable 10 veces seguidas.

Este laboratorio entrena una skill de producción: robustez repetible bajo presión temporal.

---

## Rubrica de calidad para tests avanzados

Puntúa cada prueba 0-2 en estas dimensiones:

- determinismo;
- relevancia de negocio;
- claridad de contrato;
- aislamiento de dependencias;
- coste de mantenimiento.

Interpretación:

- 8-10: prueba excelente;
- 5-7: útil pero mejorable;
- <5: candidata a rediseño.

Esta rúbrica evita la falsa métrica de “cantidad de tests” y prioriza valor real.

---

## Señales de dominio de la skill

- detectas flakiness por diseño antes de ejecutar CI;
- justificas cuándo usar actor en dobles y cuándo no;
- modelas cancelación como caso funcional, no excepción;
- conviertes bugs de timing en casos reproducibles y protegidos.

Cuando puedes hacer esto de forma sistemática, tus refactors dejan de ser apuestas.

---

## Ejercicio guiado: test de cancelación en caso de uso

**Objetivo:** Verificar que un caso de uso respeta la cancelación de `Task` y no produce efectos secundarios tras ser cancelado.

**Instrucciones:**

1. En `Tests/FeatureCatalogDataIntegrationTests/`, crea un test para `LoadProductsUseCase` (o equivalente).
2. Configura un stub remoto que introduzca un `Task.sleep` de 2 segundos antes de responder.
3. Lanza el caso de uso dentro de un `Task`, y cancélalo tras 100ms.
4. Verifica que el resultado es `CancellationError` (o que el caso de uso no completa con datos).
5. Verifica que el store de cache NO se actualizó (la cancelación interrumpió antes de guardar).

**Criterios de éxito:**

- El test pasa de forma determinista (no flaky).
- El caso de uso usa `try Task.checkCancellation()` o `withTaskCancellationHandler` internamente.
- No se usa `Task.sleep` en el test para esperar resultados (usa `Task.value` con expectativa de error).

<details>
<summary>Solución de referencia</summary>

```swift
// Tests/FeatureCatalogDataIntegrationTests/CancellationTests.swift

final class CachedCatalogRepositoryCancellationTests: XCTestCase {

    func test_fetchCatalog_respectsCancellation_andDoesNotUpdateCache() async throws {
        // Arrange: data source lenta + store espía
        let slowRemote = SlowCatalogRemoteDataSourceStub(
            delay: .seconds(2),
            result: .success([Product(id: "p-1", title: "Slow", price: 9.99)])  // title, no name
        )
        let store = InMemoryCatalogCacheStoreStub()
        let connectivity = AlwaysOnlineConnectivityStub()
        let sut = CachedCatalogRepository(
            remote: slowRemote,
            cache: store,
            connectivity: connectivity,
            ttlSeconds: 300,
            now: Date.init
        )

        // Act: lanzar carga y cancelar rápido
        let task = Task { try await sut.fetchCatalog() }  // fetchCatalog, no loadAll
        try await Task.sleep(for: .milliseconds(100))
        task.cancel()

        // Assert: debe terminar con CancellationError
        do {
            _ = try await task.value
            XCTFail("Debería haber lanzado CancellationError")
        } catch is CancellationError {
            // Correcto: cancelación propagada
        }

        // Assert: el store NO debe haberse actualizado
        let cached = try await store.load()
        XCTAssertNil(cached, "Cache no debe actualizarse tras cancelación")
    }
}

// Stub del data source lento — struct + Sendable automático
struct SlowCatalogRemoteDataSourceStub: CatalogRemoteDataSource {
    let delay: Duration
    let result: Result<[Product], Error>

    func fetchProducts() async throws -> [Product] {
        try await Task.sleep(for: delay)
        try Task.checkCancellation()  // Cooperativo: verifica después del sleep
        return try result.get()
    }
}
```

> **Nota scaffold:** El protocolo es `CatalogRemoteDataSource` con `fetchProducts()` (no `ProductRepository.loadAll()`). El repositorio es `CachedCatalogRepository` con `fetchCatalog()`. El `Product` usa `title: String` y `price: Double`. El stub usa `struct` (no `final class @unchecked Sendable`).

La cancelación es cooperativa: el sistema marca el `Task` como cancelado, el stub llama a `Task.checkCancellation()` después del `sleep`, lo que lanza `CancellationError`. El repositorio no llega a guardar en cache. El test verifica dos contratos: (1) la cancelación se propaga, (2) no hay efectos secundarios parciales.

</details>

---

## Implementación en tu proyecto

### Archivos del scaffold relevantes para tests avanzados

| Archivo | Uso en tests |
|---|---|
| `Sources/FeatureCatalogData/InMemoryCatalogStores.swift` | `InMemoryCatalogCacheStore` actor — store para tests de cancelación |
| `Sources/FeatureCatalogData/CatalogDataContracts.swift` | `CatalogRemoteDataSource`, `ConnectivityChecking` — interfaces para stubs |
| `Sources/FeatureCatalogData/CachedCatalogRepository.swift` | El SUT principal para tests de integración avanzada |

### Divergencias respecto a los ejemplos del curso

| Lección | Scaffold real |
|---|---|
| `ProductRepository.loadAll()` | `CatalogRepository.fetchCatalog()` |
| `CatalogRemoteDataSource` (no aparece) | `CatalogRemoteDataSource.fetchProducts()` — la frontera de red real |
| `InMemoryProductStore` | `InMemoryCatalogCacheStoreStub` (en tests) |
| `SlowStubProductRepository: @unchecked Sendable` | `SlowCatalogRemoteDataSourceStub: struct` (Sendable automático) |
| `Product(id:name:price:imageURL:)` | `Product(id:title:price:)` con `Double` |

### El `ConnectivityChecking` como herramienta de test

El scaffold tiene `ConnectivityChecking` como dependencia de `CachedCatalogRepository`. Esto hace los tests de backpressure y cancelación más precisos:

```swift
// ✅ Controlar si el dispositivo "parece online" en tests
struct AlwaysOnlineConnectivityStub: ConnectivityChecking {
    func isOnline() async -> Bool { true }
}

struct AlwaysOfflineConnectivityStub: ConnectivityChecking {
    func isOnline() async -> Bool { false }
}
```

Sin `ConnectivityChecking`, tendrías que simular errores de red para testear el path offline. Con él, el control es explícito y determinista.

---

## 🔭 Explora el scaffold — Tests avanzados en todos los targets

```bash
cd apps/ios/ArchitectureKit
swift test --verbose
```

La salida verbose muestra todos los targets ejecutándose: `FeatureCatalogDomainTests`, `FeatureCatalogDataTests`, `FeatureCatalogPersistenceTests`, `FeatureLoginDataTests`, `AppCompositionTests`. Identifica cuáles son unit tests puros, cuáles integration tests, y cuáles usan `ConnectivityChecking` como herramienta de control de escenarios de red.

---


## Qué sigue

[**Lección 16: Trade-offs de arquitectura →**](./05-trade-offs.md) — Cómo tomar decisiones de arquitectura con criterio: cuándo añadir una capa, cuándo no, y cómo documentar las decisiones para que el equipo no las revierta sin entenderlas.

