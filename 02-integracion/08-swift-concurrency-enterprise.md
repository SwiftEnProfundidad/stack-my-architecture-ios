# Swift Concurrency Enterprise: Patrones Imprescindibles

<!-- snippet-mapping-note:auto -->
> **Nota de nomenclatura pedagógica**
> Algunos snippets de esta lección usan `ProductRepository` como nombre conceptual.
> En el scaffold real (`apps/ios/ArchitectureKit`) el equivalente operativo es `CatalogRepository`.
## Mapa de lectura (~35 min)

| # | Sección | Línea | Tiempo |
|---|---------|-------|--------|
| 1 | async/await — La base de todo | ~9 | 3 min |
| 2 | Task — Unidad de trabajo concurrente | ~68 | 3 min |
| 3 | async let — Paralelo (número fijo) | ~148 | 3 min |
| 4 | TaskGroup — Paralelo (número dinámico) | ~210 | 3 min |
| 5 | Actor — Proteger estado compartido | ~260 | 3 min |
| 6 | Sendable — Seguridad al cruzar fronteras | ~340 | 3 min |
| 7 | Cancelación cooperativa | ~397 | 2 min |
| 8 | AsyncSequence y AsyncStream | ~441 | 3 min |
| 9 | Patrones enterprise comunes | ~500 | 3 min |
| 10 | Swift 6 — Lo que cambia | ~585 | 3 min |
| 11 | Anti-patrones — Lo que NUNCA hacer | ~666 | 3 min |
| — | Ejercicio guiado: cancelación segura | ~812 | 3 min |

---

## Por que esta lección

En las lecciones anteriores usamos `async/await`, `Sendable` y `@MainActor` sin profundizar en como funciona la concurrencia por debajo. Un junior que entre en enterprise va a encontrar `Task`, `TaskGroup`, `async let`, `actor`, cancelación, `AsyncSequence`, y errores de Swift 6 como "Sending value of non-Sendable type risks causing data races". Esta lección te prepara para todo eso.

---

## 1. async/await — La base de todo

### Que es

`async/await` permite escribir código asincrono (que tarda en completarse, como una peticion de red) como si fuera sincrono (lineal, de arriba a abajo). Sin `async/await`, usariamos closures anidados (callback hell).

### Comparacion visual

```swift
// SIN async/await (callback hell)
func loadProducts(completion: @escaping ([Product]) -> Void) {
    networkClient.fetch("/products") { data, error in
        if let data = data {
            let products = try? JSONDecoder().decode([Product].self, from: data)
            DispatchQueue.main.async {
                completion(products ?? [])
            }
        }
    }
}

// CON async/await (lineal y claro)
func loadProducts() async throws -> [Product] {
    let (data, _) = try await httpClient.execute(request)
    return try JSONDecoder().decode([Product].self, from: data)
}
```text

**Explicacion:**

`async` — Marca una función como asincrona. Dice: "esta función puede pausarse mientras espera algo". No significa que se ejecute en otro hilo — significa que **puede suspenderse**.

`await` — Marca un **punto de suspension**. Cuando Swift llega a un `await`, la función se pausa. El hilo queda libre para hacer otras cosas. Cuando la operación termina, la función se reanuda donde se quedo.

`throws` — La función puede fallar. `try` acompana a `await` porque la llamada puede tanto suspenderse como fallar.

### El punto de suspension explicado

```mermaid
sequenceDiagram
    participant V as CatalogView
    participant VM as ViewModel.load()
    participant NET as HTTPClient

    V->>VM: .task { await load() }
    VM->>VM: state = .loading
    VM->>NET: try await execute(request)
    Note over VM: SUSPENDIDO<br/>El hilo queda LIBRE<br/>para hacer otras cosas
    Note over NET: Descargando datos...
    NET-->>VM: (data, response)
    Note over VM: REANUDADO<br/>Continua donde se pausó
    VM->>VM: state = .loaded(products)
    VM-->>V: SwiftUI detecta cambio → redibuja
```text

**Clave:** Mientras `ViewModel.load()` espera la respuesta de red, el hilo **no esta bloqueado**. Puede ejecutar otras tareas. Esto es radicalmente diferente a `DispatchQueue.sync` que bloquea el hilo hasta que termina.

---

## 2. Task — La unidad de trabajo concurrente

### Que es

Un `Task` es un **contexto de ejecución asincrono**. Piensalo como un trabajador que puedes contratar para hacer un trabajo en paralelo.

### Task no estructurado (lanzar desde código sincrono)

```swift
// En un Button action (contexto sincrono):
Button("Cargar") {
    Task {
        await viewModel.load()
    }
}
```text

`Task { ... }` — Crea un nuevo contexto async desde código sincrono. Lo necesitas porque el action de un `Button` no es `async`. El `Task` "envuelve" el código async para que pueda ejecutarse.

**Peligro:** Si la vista desaparece, este `Task` sigue ejecutandose. Por eso en SwiftUI preferimos `.task { }` (que se cancela automaticamente).

### .task vs Task { }

| `.task { }` (structured) | `Task { }` (unstructured) |
|---|---|
| Se cancela automaticamente cuando la vista desaparece | Vive independientemente — puede causar memory leaks |
| No necesitas guardarlo ni cancelarlo manualmente | Necesitas guardar la referencia para cancelar |
| Preferido en SwiftUI | Solo cuando no hay alternativa |

```swift
// PREFERIDO: structured
.task {
    await viewModel.load()
}

// SOLO CUANDO NECESARIO: unstructured
Task {
    await viewModel.load()
}
```text

### Cancelación manual de Task

Si usas `Task { }` no estructurado, puedes cancelarlo manualmente:

```swift
@Observable @MainActor
final class SearchViewModel {
    var results: [Product] = []
    private var searchTask: Task<Void, Never>?

    func search(_ query: String) {
        // Cancelar busqueda anterior
        searchTask?.cancel()

        // Lanzar nueva busqueda
        searchTask = Task {
            // Esperar un poco (debounce) antes de buscar
            try? await Task.sleep(for: .milliseconds(300))

            // Verificar que no nos han cancelado
            guard !Task.isCancelled else { return }

            let results = try? await repository.search(query)
            self.results = results ?? []
        }
    }
}
```text

**Explicacion:**

`searchTask?.cancel()` — Cancela la busqueda anterior si aun esta en progreso. Si el usuario escribe rápido "i", "ip", "iph", "ipho", "iphon", "iphone", cancelamos las busquedas intermedias y solo ejecutamos la ultima.

`Task.sleep(for: .milliseconds(300))` — Pausa el Task 300ms (debounce). Si el usuario sigue escribiendo, el Task se cancela antes de que pase ese tiempo.

`Task.isCancelled` — Propiedad booleana que indica si el Task fue cancelado. La cancelación en Swift es **cooperativa**: el sistema NO mata el Task — solo lo marca como cancelado. Tu código debe verificar periodicamente `Task.isCancelled` y salir limpiamente.

---

## 3. async let — Operaciones en paralelo (número fijo)

### Que es

`async let` lanza multiples operaciones en paralelo cuando sabes cuantas son en tiempo de compilacion.

### Ejemplo: cargar datos de perfil

```swift
func loadProfile() async throws -> ProfileData {
    // Sin async let: SECUENCIAL (uno tras otro) — lento
    // let user = try await fetchUser()      // 2 segundos
    // let posts = try await fetchPosts()     // 1 segundo
    // let photos = try await fetchPhotos()   // 1 segundo
    // Total: 4 segundos

    // Con async let: PARALELO (todos a la vez) — rapido
    async let user = fetchUser()      // Empieza inmediatamente
    async let posts = fetchPosts()     // Empieza inmediatamente
    async let photos = fetchPhotos()   // Empieza inmediatamente

    // Esperar a que todos terminen
    return try await ProfileData(
        user: user,
        posts: posts,
        photos: photos
    )
    // Total: ~2 segundos (el mas lento)
}
```text

**Explicacion:**

`async let user = fetchUser()` — Lanza `fetchUser()` inmediatamente en background, pero NO espera el resultado. Es como pedir tres pizzas a la vez en vez de pedir una, esperar, pedir otra, esperar, pedir otra.

`try await ProfileData(user: user, posts: posts, photos: photos)` — Aquí es donde esperas los tres resultados. Si alguno falla, los demas se **cancelan automaticamente** (structured concurrency).

```mermaid
gantt
    title Carga secuencial vs paralela
    dateFormat X
    axisFormat %s

    section Secuencial
    fetchUser     :0, 2
    fetchPosts    :2, 3
    fetchPhotos   :3, 4

    section Paralelo (async let)
    fetchUser     :0, 2
    fetchPosts    :0, 1
    fetchPhotos   :0, 1
```text

### Cuando usar async let

- Sabes **cuantas** operaciones son en compilacion (2, 3, 5...).
- Las operaciones son **independientes** (no dependen del resultado de otra).
- Quieres que si una falla, las demas se **cancelen automaticamente**.

---

## 4. TaskGroup — Operaciones en paralelo (número dinámico)

### Que es

Cuando el número de operaciones no se conoce en compilacion (ej: descargar N imágenes), usas `TaskGroup`.

### Ejemplo: descargar imágenes de productos

```swift
func loadProductImages(urls: [URL]) async -> [URL: Data] {
    await withTaskGroup(of: (URL, Data?).self) { group in
        // Lanzar una descarga por cada URL
        for url in urls {
            group.addTask {
                let data = try? await httpClient.download(url)
                return (url, data)
            }
        }

        // Recoger resultados a medida que terminan
        var results: [URL: Data] = [:]
        for await (url, data) in group {
            if let data {
                results[url] = data
            }
        }
        return results
    }
}
```text

**Explicacion:**

`withTaskGroup(of: (URL, Data?).self)` — Crea un grupo de tareas. El parámetro `of:` dice que tipo devuelve cada tarea hija.

`group.addTask { ... }` — Anade una tarea al grupo. Cada tarea se ejecuta en paralelo. Si tienes 50 URLs, se lanzan 50 descargas en paralelo (el sistema gestiona cuantas se ejecutan realmente a la vez).

`for await (url, data) in group` — **AsyncSequence**: itera sobre los resultados a medida que van llegando. No espera a que terminen TODAS — procesa cada resultado tan pronto como esta listo. `for await` es como `for in` pero para datos asincronos.

### async let vs TaskGroup

| `async let` | `TaskGroup` |
|---|---|
| Número fijo de operaciones | Número dinámico (array) |
| Conocido en compilacion | Conocido en runtime |
| Más simple de escribir | Más flexible |
| Ej: fetchUser + fetchPosts | Ej: descargar N imágenes |

---

## 5. Actor — Proteger estado compartido

### Que es

Un `actor` es como una `class` con un **candado automático**. Solo una operación puede ejecutarse dentro del actor a la vez. Esto previene **data races** (dos hilos accediendo al mismo dato simultaneamente).

### El problema sin actor

```swift
// PELIGROSO: class normal accedida desde multiples hilos
class ImageCache {
    private var cache: [URL: Data] = [:]

    func get(_ url: URL) -> Data? {
        cache[url]  // Hilo 1 lee...
    }

    func set(_ url: URL, data: Data) {
        cache[url] = data  // Hilo 2 escribe AL MISMO TIEMPO → CRASH
    }
}
```text

### La solución con actor

```swift
actor ImageCache {
    private var cache: [URL: Data] = [:]

    func get(_ url: URL) -> Data? {
        cache[url]  // Solo un hilo a la vez puede entrar aqui
    }

    func set(_ url: URL, data: Data) {
        cache[url] = data  // Seguro: nadie mas esta accediendo
    }
}

// Uso: requiere await porque el actor puede estar ocupado
let data = await imageCache.get(url)
await imageCache.set(url, data: imageData)
```swift

**Explicacion:**

`actor ImageCache` — Igual que `class`, pero con serializacion automatica. Cuando el Hilo 1 esta ejecutando `get()`, el Hilo 2 que quiere ejecutar `set()` espera automaticamente hasta que el Hilo 1 termine. No necesitas `DispatchQueue`, `NSLock`, ni `@synchronized`. El compilador lo garantiza.

`await imageCache.get(url)` — **Todo** acceso a un actor desde fuera requiere `await`, porque puede que el actor este ocupado atendiendo otra peticion y tengas que esperar.

### @MainActor — Un actor especial

`@MainActor` es un **actor global** que ejecuta todo en el hilo principal. Ya lo usamos en los ViewModels:

```swift
@Observable @MainActor
final class CatalogViewModel { ... }
```text

**Por que:** Las propiedades del ViewModel son leidas por SwiftUI para renderizar. SwiftUI solo renderiza en el hilo principal. Si cambiaras `state` desde un hilo de background, la app crashearia. `@MainActor` previene eso.

**Regla del skill:** No uses `@MainActor` como solución generica para todo. Solo para código que genuinamente necesita el hilo principal (UI, ViewModels). Infraestructura y Domain NO necesitan `@MainActor`.

### Cuando usar cada herramienta

```mermaid
flowchart TD
    Q1{"Necesitas proteger<br/>estado mutable compartido?"}
    Q1 -->|"Si"| Q2{"Es codigo de UI?"}
    Q1 -->|"No"| SENDABLE["Usa Sendable<br/>(struct inmutable)"]

    Q2 -->|"Si"| MAINACTOR["@MainActor<br/>(ViewModel, coordinador)"]
    Q2 -->|"No"| ACTOR["actor<br/>(cache, store, manager)"]

    style SENDABLE fill:#d4edda,stroke:#28a745
    style MAINACTOR fill:#cce5ff,stroke:#007bff
    style ACTOR fill:#fff3cd,stroke:#ffc107
```text

---

## 6. Sendable — Seguridad al cruzar fronteras

### Que es

`Sendable` es un protocolo que dice: "este tipo es seguro para enviarse entre hilos". Ya lo usamos en todos los modelos de dominio. Aquí profundizamos en POR QUE y CUANDO.

### Que tipos son Sendable automaticamente

| Tipo | Sendable? | Por que |
|---|---|---|
| `struct` con todas las propiedades `Sendable` | Si (automático) | Los structs se copian, no se comparten |
| `enum` con valores asociados `Sendable` | Si (automático) | Los enums se copian |
| `actor` | Si (siempre) | Los actors serializan acceso |
| `class` normal | **No** | Las clases se comparten por referencia → data race |
| `final class` con propiedades `let` `Sendable` | Si (automático) | Inmutable → seguro |
| `@Sendable` closure | Si (marcado) | El closure no captura estado mutable |

### Donde se necesita Sendable

Cada vez que un valor cruza una **frontera de aislamiento** (isolation boundary), necesita ser `Sendable`:

```swift
// Frontera 1: de un actor a otro
await mainActorViewModel.state = .loaded(products)  // products debe ser Sendable

// Frontera 2: de sincrono a Task
Task {
    await process(data)  // data debe ser Sendable
}

// Frontera 3: entre TaskGroup y su padre
group.addTask {
    return processedItem  // processedItem debe ser Sendable
}
```text

### @unchecked Sendable — Deuda tecnica

A veces necesitas marcar un tipo como Sendable cuando el compilador no puede verificarlo:

```swift
// Solo en test doubles y casos excepcionales
final class HTTPClientStub: HTTPClient, @unchecked Sendable {
    var result: Result<(Data, HTTPURLResponse), Error>
    // ...
}
```text

`@unchecked Sendable` — Le dices al compilador: "confio en que esto es thread-safe". Pero si te equivocas, habra data races que el compilador no detectara.

**Reglas del skill:**
1. **Nunca** en código de producción sin justificacion documentada.
2. Si lo usas, crea un ticket/tarea para eliminarlo en el futuro.
3. En tests es aceptable porque los tests son single-threaded en la practica.

---

## 7. Cancelación cooperativa — Ser buen ciudadano

### Que es

Cuando un Task se cancela (porque la vista desaparecio, el usuario navego atras, o se lanzo una busqueda nueva), Swift NO lo mata inmediatamente. Lo **marca** como cancelado. Tu código debe verificarlo y salir limpiamente.

### Como verificar cancelación

```swift
func processLargeDataset(_ items: [Item]) async throws -> [ProcessedItem] {
    var results: [ProcessedItem] = []

    for item in items {
        // Verificar cancelacion periodicamente
        try Task.checkCancellation()

        let processed = await process(item)
        results.append(processed)
    }

    return results
}
```text

**Explicacion:**

`Task.checkCancellation()` — Si el Task fue cancelado, lanza `CancellationError`. El `try` la propaga hacia arriba y la función termina limpiamente.

Alternativa manual:

```swift
guard !Task.isCancelled else {
    return results  // Devolver lo que tengamos hasta ahora
}
```text

### Por que es importante

Sin verificacion de cancelación, un Task cancelado sigue ejecutandose hasta el final, desperdiciando CPU, memoria, y bateria. En enterprise, esto es inaceptable: si el usuario navega atras, las operaciones de la pantalla anterior deben detenerse.

`.task` de SwiftUI ya maneja esto por ti — cuando la vista desaparece, cancela el Task. Pero tu código **dentro** del Task debe ser cooperativo y verificar `Task.isCancelled` en bucles largos.

---

## 8. AsyncSequence y AsyncStream — Datos que llegan con el tiempo

### Que es

`AsyncSequence` es como un array, pero los elementos llegan **con el tiempo**, no todos de golpe. Piensa en notificaciones push, actualizaciones en tiempo real, o progreso de descarga.

### AsyncSequence nativo (for await)

```swift
// Leer lineas de un archivo una por una (sin cargar todo en memoria)
let url = URL(fileURLWithPath: "/path/to/large-file.txt")
for try await line in url.lines {
    process(line)
}
```text

`for try await line in url.lines` — Igual que `for line in array`, pero cada linea llega de forma asincrona. El bucle se pausa esperando la siguiente linea, sin bloquear el hilo.

### AsyncStream — Crear tu propio stream

Cuando necesitas convertir callbacks o delegados en async:

```swift
func observeLocationUpdates() -> AsyncStream<CLLocation> {
    AsyncStream { continuation in
        let delegate = LocationDelegate { location in
            continuation.yield(location)  // Emitir un valor
        }

        continuation.onTermination = { _ in
            delegate.stop()  // Limpiar cuando el consumidor deja de escuchar
        }

        delegate.start()
    }
}

// Uso:
for await location in observeLocationUpdates() {
    updateMap(with: location)
}
```text

**Explicacion:**

`AsyncStream { continuation in ... }` — Crea un stream asincrono. La `continuation` es el control remoto: llamas a `.yield(valor)` para emitir valores y `.finish()` para terminar el stream.

`continuation.onTermination` — Se ejecuta cuando el consumidor deja de escuchar (cancelación, scope terminado). Aquí limpias recursos.

### Cuando usar AsyncSequence

| Patrón | Herramienta |
|---|---|
| Una peticion, una respuesta | `async/await` |
| N peticiones en paralelo | `async let` / `TaskGroup` |
| Datos que llegan con el tiempo | `AsyncSequence` / `AsyncStream` |

---

## 9. Patrones enterprise comunes

### Patrón: Red + UI update

```swift
@Observable @MainActor
final class ProductListViewModel {
    var products: [Product] = []
    var isLoading = false

    private let repository: any ProductRepository

    func load() async {
        isLoading = true
        defer { isLoading = false }

        do {
            products = try await repository.loadAll()
        } catch {
            products = []
        }
    }
}
```text

`defer { isLoading = false }` — Se ejecuta **siempre** al salir de la función, sea por exito o por error. Garantiza que `isLoading` se pone en `false` sin importar que pase. Es como un "al salir, apaga la luz".

### Patrón: Retry con backoff exponencial

```swift
func withRetry<T>(
    maxAttempts: Int = 3,
    operation: () async throws -> T
) async throws -> T {
    for attempt in 1...maxAttempts {
        do {
            return try await operation()
        } catch where attempt < maxAttempts {
            // Esperar mas tiempo en cada reintento: 1s, 2s, 4s...
            let delay = UInt64(pow(2.0, Double(attempt - 1))) * 1_000_000_000
            try await Task.sleep(nanoseconds: delay)
        }
    }
    return try await operation()  // Ultimo intento
}

// Uso:
let products = try await withRetry {
    try await repository.loadAll()
}
```text

### Patrón: Timeout

```swift
func withTimeout<T>(
    seconds: TimeInterval,
    operation: @Sendable () async throws -> T
) async throws -> T {
    try await withThrowingTaskGroup(of: T.self) { group in
        group.addTask {
            try await operation()
        }
        group.addTask {
            try await Task.sleep(for: .seconds(seconds))
            throw CancellationError()
        }

        // El primero que termine gana
        let result = try await group.next()!
        group.cancelAll()
        return result
    }
}

// Uso:
let products = try await withTimeout(seconds: 10) {
    try await repository.loadAll()
}
```text

**Explicacion:** Lanza dos tareas en paralelo: la operación real y un timer. Si el timer termina primero (timeout), cancela la operación. Si la operación termina primero, cancela el timer.

---

## 10. Swift 6 — Lo que cambia

### Strict concurrency por defecto

En Swift 6, el compilador **rechaza** código que podria tener data races. Lo que antes eran warnings se convierten en errores.

### Errores más comunes en Swift 6

**Error 1: "Sending value of non-Sendable type"**
```swift
// Esto falla en Swift 6
class MyService {  // class NO es Sendable
    func doWork() { }
}

Task {
    let service = MyService()
    await process(service)  // ERROR: MyService no es Sendable
}

// Solucion: hacer Sendable
final class MyService: Sendable {
    func doWork() { }
}
// O mejor: usar struct
struct MyService: Sendable {
    func doWork() { }
}
```text

**Error 2: "Main actor-isolated property cannot be accessed from nonisolated context"**
```swift
@MainActor
class ViewModel {
    var name = "Hola"
}

// Esto falla en Swift 6
func process(vm: ViewModel) {
    print(vm.name)  // ERROR: accediendo a @MainActor desde contexto no aislado
}

// Solucion: marcar como async o @MainActor
func process(vm: ViewModel) async {
    print(await vm.name)  // OK: await cruza la frontera
}
```text

**Error 3: "Capture of non-Sendable in @Sendable closure"**
```swift
class DataProcessor {
    var data: [String] = []
}

let processor = DataProcessor()
Task {
    processor.data.append("nuevo")  // ERROR: processor no es Sendable
}

// Solucion: usar actor
actor DataProcessor {
    var data: [String] = []
    func add(_ item: String) { data.append(item) }
}

let processor = DataProcessor()
Task {
    await processor.add("nuevo")  // OK: serializado por el actor
}
```text

### Como prepararte

1. En Xcode: Build Settings → **Strict Concurrency Checking** = **Complete**
2. Corrige los warnings uno por uno (son los futuros errores de Swift 6)
3. Convierte `class` a `struct` donde sea posible (los structs son Sendable automaticamente)
4. Usa `actor` para estado mutable compartido
5. Marca `@MainActor` solo lo que genuinamente necesita el hilo principal

---

## 11. Anti-patrones — Lo que NUNCA hacer

### Nunca bloquear en async

```swift
// FATAL: bloquear un hilo async con semaforo
func loadData() async -> Data {
    let semaphore = DispatchSemaphore(value: 0)
    var result: Data?

    URLSession(configuration: .default).dataTask(with: url) { data, _, _ in
        result = data
        semaphore.signal()
    }.resume()

    semaphore.wait()  // BLOQUEA el hilo → puede causar deadlock
    return result!
}

// CORRECTO: usar async/await nativo
func loadData() async throws -> Data {
    let session = URLSession(configuration: .default)
    let (data, _) = try await session.data(from: url)
    return data
}
```text

`DispatchSemaphore`, `NSLock`, y `pthread_mutex` **nunca** deben usarse en contextos async. Bloquean el hilo del executor, y como el executor tiene un número limitado de hilos, puedes causar un deadlock donde todas las tareas estan esperando un hilo que esta bloqueado.

### Nunca usar Task.detached sin razón

```swift
// MAL: pierde herencia de contexto (prioridad, actor)
Task.detached {
    await viewModel.load()  // No hereda @MainActor
}

// BIEN: Task normal hereda el contexto
Task {
    await viewModel.load()  // Hereda @MainActor si el padre es @MainActor
}
```swift

`Task.detached` NO hereda el contexto del padre (prioridad, actor isolation). Solo usalo si necesitas **explicitamente** ejecutar fuera del contexto actual (raro).

### Nunca ignorar la cancelación

```swift
// MAL: ignora cancelacion, desperdicia recursos
func processItems(_ items: [Item]) async -> [Result] {
    var results: [Result] = []
    for item in items {
        results.append(await process(item))  // Sigue incluso si fue cancelado
    }
    return results
}

// BIEN: cooperativo con cancelacion
func processItems(_ items: [Item]) async throws -> [Result] {
    var results: [Result] = []
    for item in items {
        try Task.checkCancellation()  // Sale si fue cancelado
        results.append(await process(item))
    }
    return results
}
```text

---

## Resumen: mapa de concurrencia enterprise

```mermaid
flowchart LR
    subgraph BASICO["Basico"]
        B1["async/await<br/>Operacion simple"]
        B2["Task { }<br/>Lanzar async desde sync"]
        B3[".task { }<br/>SwiftUI lifecycle"]
    end

    subgraph PARALELO["Paralelo"]
        P1["async let<br/>2-5 ops fijas"]
        P2["TaskGroup<br/>N ops dinamicas"]
    end

    subgraph PROTECCION["Proteccion"]
        PR1["Sendable<br/>Cruzar fronteras"]
        PR2["actor<br/>Estado mutable"]
        PR3["@MainActor<br/>Hilo principal"]
    end

    subgraph STREAMING["Streaming"]
        S1["AsyncSequence<br/>for await in"]
        S2["AsyncStream<br/>Callbacks a async"]
    end

    subgraph CONTROL["Control"]
        C1["Cancelacion<br/>Task.isCancelled"]
        C2["Retry + Timeout<br/>Patrones enterprise"]
    end
```text

### Checklist de concurrencia para un junior

**Básico (usa a diario):**
- [ ] `async/await` para operaciones asincronas
- [ ] `.task { }` en SwiftUI para carga automatica con cancelación
- [ ] `Task { }` solo cuando no puedas usar `.task`
- [ ] `try/catch` para manejar errores async

**Paralelo (usa cuando necesites rendimiento):**
- [ ] `async let` para 2-5 operaciones independientes
- [ ] `TaskGroup` para N operaciones dinamicas
- [ ] Entender que `async let` cancela hermanos si uno falla

**Protección (usa siempre):**
- [ ] `Sendable` en todos los tipos que cruzan fronteras async
- [ ] `@MainActor` en ViewModels y código de UI
- [ ] `actor` para caches, stores, y estado mutable compartido
- [ ] Evitar `@unchecked Sendable` en producción

**Cancelación (obligatorio en enterprise):**
- [ ] `Task.checkCancellation()` en bucles largos
- [ ] `Task.isCancelled` para limpiar recursos
- [ ] `defer { }` para garantizar limpieza

**Streaming (cuando los datos llegan con el tiempo):**
- [ ] `for await in` para iterar sobre `AsyncSequence`
- [ ] `AsyncStream` para convertir callbacks a async

**Swift 6 (prepararse ya):**
- [ ] Strict Concurrency = Complete en Build Settings
- [ ] Corregir warnings uno por uno
- [ ] `struct` > `class` donde sea posible
- [ ] `actor` para estado mutable compartido

**Anti-patrones (NUNCA hacer):**
- [ ] No usar `DispatchSemaphore` en contextos async
- [ ] No usar `Task.detached` sin razón documentada
- [ ] No ignorar cancelación en bucles largos
- [ ] No bloquear hilos con `wait()` o `sleep()` (usar `Task.sleep`)

Si dominas estos puntos, puedes manejar cualquier escenario de concurrencia en enterprise iOS.

---

## Ejercicio guiado: cancelación segura en CatalogViewModel

**Objetivo:** Verificar que el ViewModel de Catalog cancela correctamente la carga anterior cuando el usuario dispara una nueva carga.

**Instrucciones:**

1. Abre `apps/ios/ArchitectureKit/Sources/FeatureCatalogUI/` y localiza el ViewModel de Catalog.
2. Verifica (o implementa) que al llamar `load()` por segunda vez, la primera `Task` se cancela.
3. Escribe un test que simule:
   - Primera llamada a `load()` con un repositorio lento (2 segundos).
   - Segunda llamada a `load()` inmediatamente despues.
   - Verifica que solo la segunda carga produce resultado en `products`.

**Criterios de exito:**

- El test pasa de forma determinista.
- El ViewModel almacena la `Task` activa y la cancela antes de crear una nueva.
- No hay data races (el ViewModel usa `@MainActor` o aislamiento equivalente).

**Solución razonada:**

```swift
// En el ViewModel
@MainActor
final class CatalogViewModel: ObservableObject {
    @Published var products: [Product] = []
    private var loadTask: Task<Void, Never>?

    func load() {
        loadTask?.cancel()  // Cancelar carga anterior
        loadTask = Task {
            do {
                let result = try await repository.loadProducts()
                if !Task.isCancelled {
                    products = result
                }
            } catch {
                // Manejar error (no actualizar si cancelado)
            }
        }
    }
}

// Test
func test_load_cancels_previous_load() async {
    let slowRepo = SlowStubRepository(delay: .seconds(2), result: [Product(name: "Old", price: 1)])
    let fastRepo = StubRepository(result: [Product(name: "New", price: 2)])

    let sut = CatalogViewModel(repository: slowRepo)
    sut.load()  // Primera carga (lenta)

    // Cambiar a repo rapido y cargar de nuevo
    sut.repository = fastRepo
    sut.load()  // Segunda carga (cancela la primera)

    // Esperar a que la segunda complete
    try? await Task.sleep(for: .milliseconds(200))
    XCTAssertEqual(sut.products.first?.name, "New")
}
```

La cancelación no es un detalle de implementación: es un requisito de UX. Sin ella, el usuario puede ver datos de una carga que ya no es relevante (por ejemplo, resultados de una busqueda anterior).

---

## Cierre

Swift Concurrency no es una feature opcional que se anade al final. Es el sistema de tipos que garantiza que tu app no tiene data races. En esta lección has visto los patrones fundamentales: `async/await` para flujos lineales, `Task` para trabajo concurrente con cancelación, `@MainActor` para proteger UI, y `Sendable` para fronteras de concurrencia.

La Etapa 5 (Maestria) profundiza en estos conceptos con isolation domains, actors como componentes arquitectonicos y testing concurrente avanzado. Lo que has aprendido aquí es la base operativa; lo que viene es el criterio de diseño.

---

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

