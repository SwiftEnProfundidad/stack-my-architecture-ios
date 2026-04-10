# SwiftUI Enterprise — Parte 1: Navegación, Modales e Interacción

> Parte 1 de 3. Continúa en [Parte 2](./07b-swiftui-enterprise-composicion.md).

## Mapa de lectura (~50 min)

| # | Sección | Línea | Tiempo |
|---|---------|-------|--------|
| 1 | TabView — Navegación por pestañas | ~15 | 3 min |
| 2 | @Environment — Valores del sistema | ~90 | 3 min |
| 3 | .sheet y .fullScreenCover — Modales | ~157 | 3 min |
| 4 | .alert y .confirmationDialog | ~247 | 3 min |
| 5 | .refreshable — Pull to refresh | ~314 | 2 min |
| 6 | .searchable — Búsqueda en listas | ~350 | 3 min |
| 7 | .toolbar — Barra de herramientas | ~417 | 2 min |
| 8 | @Binding — Conexión bidireccional | ~458 | 3 min |
| 9 | Form y Section — Ajustes | ~508 | 3 min |
| — | Ejercicio guiado | ~1313 | 5 min |

---

## Por que está lección

En las lecciones anteriores construimos dos pantallas (Login y Catalog) usando SwiftUI. Pero una app profesional necesita mucho más: modales, alertas, pull-to-refresh, busqueda, tabs, barras de herramientas, persistencia de preferencias... En está lección vamos a enriquecer nuestra app con los patrones SwiftUI que encontraras en **cualquier** app enterprise.

Cada patrón se explica con:
1. **Que es** — Descripción para un junior.
2. **Por que lo necesitas** — Caso de uso real en enterprise.
3. **Como se integra** — Código aplicado a nuestra arquitectura.
4. **Donde vive** — En que capa de Clean Architecture encaja.

---

## 1. TabView — Navegación por pestanas

### Que es

`TabView` organiza la app en pestanas (tabs) en la parte inferior de la pantalla. Piensa en apps como App Store, Spotify, o Instagram: todas tienen una barra de pestanas abajo. Cada pestana es una sección independiente de la app.

### Por que lo necesitas

En enterprise, las apps casi siempre tienen multiples secciones: catálogo, perfil, ajustes, notificaciones. `TabView` es la forma estandar de organizar esto en iOS.

### Como se integra

Modifica `StackMyArchitectureApp.swift` para envolver las secciones en un `TabView`:

```swift
@main
struct StackMyArchitectureApp: App {
    @State private var coordinator: AppCoordinator

    init() {
        let compositionRoot = CompositionRoot()
        _coordinator = State(wrappedValue: AppCoordinator(compositionRoot: compositionRoot))
    }

    var body: some Scene {
        WindowGroup {
            TabView {
                // Tab 1: Catalogo con navegacion
                Tab("Catalogo", systemImage: "book.fill") {
                    NavigationStack(path: $coordinator.catalogPath) {
                        coordinator.makeCatalogView()
                            .navigationDestination(for: AppDestination.self) { destination in
                                switch destination {
                                case .productDetail(let product):
                                    coordinator.makeProductDetailView(product: product)
                                default:
                                    EmptyView()
                                }
                            }
                    }
                }

                // Tab 2: Perfil
                Tab("Perfil", systemImage: "person.fill") {
                    NavigationStack {
                        coordinator.makeProfileView()
                    }
                }

                // Tab 3: Ajustes
                Tab("Ajustes", systemImage: "gear") {
                    NavigationStack {
                        coordinator.makeSettingsView()
                    }
                }
            }
        }
    }
}
```

**Explicacion linea por linea:**

`TabView { ... }` — Crea la barra de pestanas. Cada `Tab` dentro es una pestana.

`Tab("Catalogo", systemImage: "book.fill")` — Crea una pestana con titulo "Catálogo" y un icono de SF Symbols. El icono y texto aparecen en la barra inferior.

Cada tab tiene su propio `NavigationStack` — Esto es **crítico**: cada pestana gestiona su propia pila de navegación. Si navegas a un detalle en Catálogo y cambias a Perfil, al volver a Catálogo sigues en el detalle. Las pilas son independientes.

### Donde vive

En la **capa App** (`StackMyArchitectureApp.swift`). El `TabView` es una decisión de presentación de la app, no de una feature individual.

---

## 2. @Environment — Acceso a valores del sistema

### Que es

`@Environment` es un property wrapper que te da acceso a valores proporcionados por SwiftUI o por ti mismo. Piensalo como una **caja de herramientas compartida**: SwiftUI mete herramientas (dismiss, colorScheme, locale...) y tu las sacas cuando las necesitas.

### Los más usados en enterprise

```swift
// Cerrar/volver atras de una vista presentada modalmente
@Environment(\.dismiss) private var dismiss

// Saber si el usuario tiene modo oscuro o claro
@Environment(\.colorScheme) private var colorScheme

// Saber la zona horaria del usuario
@Environment(\.timeZone) private var timeZone

// Saber si la app esta en modo accesibilidad (texto grande)
@Environment(\.dynamicTypeSize) private var dynamicTypeSize

// Contexto de SwiftData (persistencia)
@Environment(\.modelContext) private var modelContext
```

### Ejemplo real: cerrar un modal

```swift
struct FilterView: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            List {
                Text("Filtros aqui...")
            }
            .navigationTitle("Filtrar")
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Aplicar") {
                        // Aplicar filtros...
                        dismiss()
                    }
                }
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancelar") {
                        dismiss()
                    }
                }
            }
        }
    }
}
```

**Explicacion:**

`@Environment(\.dismiss)` — Obtiene la acción de "cerrar está vista". Cuando está vista se presenta como `.sheet`, llamar a `dismiss()` la cierra con animación. Es como un botón de "cerrar" que SwiftUI te da gratis.

`\.dismiss` es un **key path al Environment**. El `\.` apunta a una propiedad del entorno de SwiftUI. Es la misma sintaxis que `\.id` en `List(products, id: \.id)`.

### Donde vive

En la **capa Interface**. `@Environment` es exclusivo de SwiftUI — nunca en Domain, Application, ni Infrastructure.

---

## 3. .sheet y .fullScreenCover — Presentación modal

### Que es

Un **modal** es una pantalla que aparece deslizandose desde abajo, cubriendo parcial (`.sheet`) o totalmente (`.fullScreenCover`) la pantalla actual. Se usa para tareas secundarias: filtros, formularios, confirmaciones, compartir.

### Por que lo necesitas

En enterprise: formularios de edicion, pantallas de filtros, vistas de detalle rápido, flujos de onboarding, pantallas de compartir.

### Como se integra

Anade un botón de filtros al catálogo:

```swift
struct CatalogView: View {
    @State private var viewModel: CatalogViewModel
    @State private var showingFilter = false

    // ... init ...

    var body: some View {
        Group {
            switch viewModel.state {
            case .loaded(let products):
                List(products, id: \.id) { product in
                    ProductRow(product: product)
                        .onTapGesture { viewModel.selectProduct(product) }
                }
            // ... otros casos ...
            }
        }
        .navigationTitle("Catalogo")
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button("Filtrar", systemImage: "line.3.horizontal.decrease") {
                    showingFilter = true
                }
            }
        }
        .sheet(isPresented: $showingFilter) {
            FilterView()
        }
        .task {
            await viewModel.load()
        }
    }
}
```

**Explicacion linea por linea:**

`@State private var showingFilter = false` — Un booleano que controla si el modal está visible. `false` = cerrado, `true` = abierto. Es `@State` porque SwiftUI necesita observar los cambios para animar la apertura/cierre.

`.toolbar { ToolbarItem(placement: .topBarTrailing) { ... } }` — Anade un botón en la barra de navegación, a la derecha (`.topBarTrailing`). Explicaremos `.toolbar` en detalle más abajo.

`showingFilter = true` — Cuando el usuario pulsa "Filtrar", ponemos el booleano en `true`. SwiftUI detecta el cambio y abre el sheet.

`.sheet(isPresented: $showingFilter) { FilterView() }` — Le dice a SwiftUI: "cuando `showingFilter` sea `true`, muestra `FilterView` como modal deslizante desde abajo". El `$` crea un **binding**: SwiftUI puede leer Y escribir el booleano. Cuando el usuario arrastra el sheet hacia abajo para cerrarlo, SwiftUI pone `showingFilter = false` automáticamente.

**`.sheet` vs `.fullScreenCover`:**

| `.sheet` | `.fullScreenCover` |
|---|---|
| Cubre parcialmente (se ve la pantalla de atras) | Cubre toda la pantalla |
| El usuario puede cerrar arrastrando hacia abajo | El usuario NO puede cerrar arrastrando |
| Para tareas opcionales (filtros, info) | Para tareas obligatorias (login, onboarding) |

### Variante: sheet con dato

A veces quieres pasar un dato al modal. Usa `.sheet(item:)`:

```swift
@State private var selectedProduct: Product?

// ...

.sheet(item: $selectedProduct) { product in
    ProductQuickView(product: product)
}
```

`item:` recibe un binding a un opcional. Cuando el valor NO es `nil`, el sheet se abre con ese dato. Cuando se cierra, SwiftUI pone el valor a `nil`. El tipo debe conformar `Identifiable` (que requiere una propiedad `id`).

### Donde vive

`.sheet` y `.fullScreenCover` son modifiers de SwiftUI — viven en la **capa Interface**.

---

## 4. .alert y .confirmationDialog — Alertas y confirmaciones

### Que es

`.alert` muestra un popup centrado con un mensaje y botones. `.confirmationDialog` muestra un menu de acciones desde abajo (como un action sheet). Ambos se usan para pedir confirmacion al usuario.

### Caso enterprise: confirmar logout

```swift
struct ProfileView: View {
    @State private var showingLogoutAlert = false
    var onLogout: () -> Void

    var body: some View {
        List {
            Section("Cuenta") {
                Text("usuario@email.com")
            }

            Section {
                Button("Cerrar sesion", role: .destructive) {
                    showingLogoutAlert = true
                }
            }
        }
        .navigationTitle("Perfil")
        .alert("Cerrar sesion", isPresented: $showingLogoutAlert) {
            Button("Cancelar", role: .cancel) { }
            Button("Cerrar sesion", role: .destructive) {
                onLogout()
            }
        } message: {
            Text("Seguro que quieres cerrar sesion? Tendras que volver a iniciar sesion.")
        }
    }
}
```

**Explicacion:**

`.alert("titulo", isPresented: $bool)` — Misma mecanica que `.sheet`: un booleano controla si se muestra. Cuando el usuario pulsa un botón del alert, SwiftUI pone el booleano en `false`.

`Button("Cancelar", role: .cancel)` — `role: .cancel` le dice a SwiftUI que es el botón de cancelar. En iOS, lo estiliza diferente (texto en azul, más prominente). El bloque `{ }` está vacio porque cancelar no hace nada.

`Button("Cerrar sesion", role: .destructive)` — `role: .destructive` pinta el texto en rojo para advertir al usuario que es una acción irreversible.

`message: { Text("...") }` — El cuerpo del alert, debajo del titulo.

### confirmationDialog para multiples opciones

```swift
.confirmationDialog("Ordenar por", isPresented: $showingSortOptions) {
    Button("Nombre") { viewModel.sortBy(.name) }
    Button("Precio: menor a mayor") { viewModel.sortBy(.priceAscending) }
    Button("Precio: mayor a menor") { viewModel.sortBy(.priceDescending) }
    Button("Cancelar", role: .cancel) { }
}
```

Aparece como un menu desde abajo con las opciones. Es el reemplazo moderno del antiguo `ActionSheet`.

### Donde vive

En la **capa Interface**. La lógica de "que pasa cuando el usuario confirma" (ej: `onLogout()`) es un closure que viene del coordinador o del ViewModel.

---

## 5. .refreshable — Pull to refresh

### Que es

El gesto de "arrastrar hacia abajo para refrescar" que ves en casi todas las apps con listas. SwiftUI lo implementa con un solo modifier.

### Como se integra

```swift
case .loaded(let products):
    List(products, id: \.id) { product in
        ProductRow(product: product)
            .onTapGesture { viewModel.selectProduct(product) }
    }
    .refreshable {
        await viewModel.load()
    }
```

**Eso es todo.** Una sola linea. SwiftUI se encarga de:
- Mostrar el spinner de refresh cuando el usuario arrastra hacia abajo.
- Ejecutar el closure async.
- Ocultar el spinner cuando el closure termina.

**Explicacion:**

`.refreshable { await viewModel.load() }` — El closure es `async`, por eso usamos `await`. SwiftUI sabe que `viewModel.load()` es asincrono y espera a que termine antes de ocultar el spinner. No necesitas gestionar ningun estado de "isRefreshing" — SwiftUI lo hace todo.

**Fijate:** El diagrama de estados de CatalogView ya tenia flechas de "Pull-to-refresh" marcadas como "Etapa 3". Aquí lo activamos.

### Donde vive

Modifier de SwiftUI — **capa Interface**. La lógica de recarga (`viewModel.load()`) ya existe en el ViewModel.

---

## 6. .searchable — Busqueda en listas

### Que es

Anade una barra de busqueda integrada en la navegación. Cuando el usuario escribe, puedes filtrar los resultados.

### Como se integra

Hay dos formas de busqueda: **local** (filtrar datos ya cargados) y **remota** (buscar en servidor). Veamos la local que es la más comun:

```swift
struct CatalogView: View {
    @State private var viewModel: CatalogViewModel
    @State private var searchText = ""

    var body: some View {
        Group {
            switch viewModel.state {
            case .loaded(let products):
                let filtered = products.filter { product in
                    searchText.isEmpty ||
                    product.name.localizedCaseInsensitiveContains(searchText)
                }

                List(filtered, id: \.id) { product in
                    ProductRow(product: product)
                        .onTapGesture { viewModel.selectProduct(product) }
                }
            // ... otros casos
            }
        }
        .searchable(text: $searchText, prompt: "Buscar productos...")
        .navigationTitle("Catalogo")
        .task {
            await viewModel.load()
        }
    }
}
```

**Explicacion:**

`@State private var searchText = ""` — El texto que el usuario escribe en la barra de busqueda. Empieza vacio.

`.searchable(text: $searchText, prompt: "Buscar productos...")` — Anade la barra de busqueda. `text:` es un **binding** al texto de busqueda. SwiftUI actualiza `searchText` automáticamente cuando el usuario escribe. `prompt:` es el texto gris que aparece cuando la barra está vacia.

`products.filter { product in ... }` — Filtra el array en memoria. `.filter` crea un nuevo array con solo los elementos que cumplen la condición. `localizedCaseInsensitiveContains` busca sin importar mayusculas/minusculas ni acentos: "cafe" encuentra "Cafe" y "Cafe".

`searchText.isEmpty || product.name.contains(...)` — Si el texto de busqueda está vacio, muestra todos. Si no, filtra por nombre.

**Nota para enterprise:** En apps reales, el filtrado complejo (por multiples campos, con debounce para busqueda remota) se mueve al ViewModel. Aquí lo ponemos en la vista por simplicidad, pero en producción harias:

```swift
// En CatalogViewModel
func search(_ query: String) {
    guard case .loaded(let allProducts) = state else { return }
    let filtered = allProducts.filter { ... }
    state = .loaded(filtered)
}
```

### Donde vive

El modifier `.searchable` está en la **Interface**. La lógica de filtrado en enterprise se mueve al **ViewModel** (Interface) o incluso a un **UseCase** si la busqueda es remota (Application).

---

## 7. .toolbar — Barra de herramientas

### Que es

`.toolbar` anade botones a la barra de navegación (arriba) o a la barra inferior. Es el lugar para acciones contextuales: filtrar, editar, compartir, anadir.

### Posiciones más usadas

```swift
.toolbar {
    // Arriba a la izquierda (ej: boton "Editar")
    ToolbarItem(placement: .topBarLeading) {
        Button("Editar") { /* ... */ }
    }

    // Arriba a la derecha (ej: boton "Anadir")
    ToolbarItem(placement: .topBarTrailing) {
        Button("Anadir", systemImage: "plus") { /* ... */ }
    }

    // Barra inferior
    ToolbarItem(placement: .bottomBar) {
        Text("\(products.count) productos")
    }
}
```

**Explicacion:**

`ToolbarItem(placement:)` — Cada item tiene una posición. SwiftUI adapta la posición segun la plataforma (iPhone vs iPad vs Mac).

`placement: .topBarTrailing` — Arriba a la derecha. En idiomas RTL (arabe, hebreo), SwiftUI lo mueve automáticamente a la izquierda.

`systemImage: "plus"` — Muestra un icono SF Symbol en vez de (o junto a) texto.

### Donde vive

Modifier de SwiftUI — **capa Interface**.

---

## 8. @Binding — Conexión bidireccional

### Que es

`@Binding` crea una **conexión de ida y vuelta** entre una vista padre y una vista hija. La hija puede LEER y ESCRIBIR un valor que pertenece al padre. Ya lo usamos con `$` (ej: `$coordinator.path`), pero aquí lo explicamos en profundidad.

### Ejemplo: un toggle de filtro

```swift
// Vista PADRE
struct CatalogView: View {
    @State private var showOnlyExpensive = false

    var body: some View {
        VStack {
            FilterToggle(isOn: $showOnlyExpensive)
            // ... lista filtrada ...
        }
    }
}

// Vista HIJA
struct FilterToggle: View {
    @Binding var isOn: Bool    // <-- Binding, no State

    var body: some View {
        Toggle("Solo productos caros", isOn: $isOn)
            .padding()
    }
}
```

**Explicacion:**

En el padre: `@State private var showOnlyExpensive = false` — El padre **posee** el dato. `@State` significa "yo soy el dueno".

Al pasar: `FilterToggle(isOn: $showOnlyExpensive)` — El `$` crea un binding. Es como dar una **llave de tu casa**: el hijo puede entrar y cambiar cosas.

En el hijo: `@Binding var isOn: Bool` — El hijo **no posee** el dato, solo tiene acceso a el. Cuando el usuario mueve el toggle, `isOn` cambia, y como es un binding, el cambio se propaga al padre automáticamente.

**Regla de oro:**
- `@State` = "Yo soy el dueno de este dato"
- `@Binding` = "Alguien me presto acceso a su dato"

### Donde vive

En la **capa Interface**. `@Binding` es un mecanismo de SwiftUI para comunicar vistas padres con hijas.

---

## 9. Form y Section — Pantallas de ajustes

### Que es

`Form` es un contenedor de SwiftUI disenado para pantallas de configuración, perfil, o ajustes. Agrupa controles en `Section`es con cabeceras y pies. Es lo que ves en la app de Ajustes del iPhone.

### Ejemplo: pantalla de ajustes

```swift
struct SettingsView: View {
    @AppStorage("notifications_enabled") private var notificationsEnabled = true
    @AppStorage("currency_code") private var currencyCode = "EUR"

    var body: some View {
        Form {
            Section("Preferencias") {
                Toggle("Notificaciones", isOn: $notificationsEnabled)

                Picker("Moneda", selection: $currencyCode) {
                    Text("Euro").tag("EUR")
                    Text("Dolar").tag("USD")
                    Text("Libra").tag("GBP")
                }
            }

            Section("Informacion") {
                LabeledContent("Version", value: "1.0.0")
                LabeledContent("Build", value: "42")
            }

            Section {
                NavigationLink("Licencias") {
                    Text("Aqui van las licencias open source...")
                }

                Link("Soporte",
                     destination: URL(string: "https://example.com/soporte")!)
            }
        }
        .navigationTitle("Ajustes")
    }
}
```

**Explicacion linea por linea:**

`Form { ... }` — Crea un formulario con el estilo visual de Ajustes de iOS (fondo gris, secciones con fondo blanco, bordes redondeados).

`Section("Preferencias") { ... }` — Agrupa controles con una cabecera. Visualmente crea un bloque blanco con titulo "PREFERENCIAS" en gris arriba.

`Toggle("Notificaciones", isOn: $notificationsEnabled)` — Un interruptor on/off. `$notificationsEnabled` es un binding: cuando el usuario lo mueve, el valor cambia.

`Picker("Moneda", selection: $currencyCode)` — Un selector. En iOS muestra la opcion actual y al pulsar navega a una lista con las opciones. `.tag("EUR")` asocia cada opcion con un valor.

`LabeledContent("Version", value: "1.0.0")` — Muestra una etiqueta a la izquierda y un valor a la derecha. Solo lectura (no editable).

`NavigationLink("Licencias") { Text("...") }` — Un enlace que navega a otra vista al pulsarlo. Aquí vemos `NavigationLink` en acción: para navegación simple (sin coordinador), es la forma más directa.

`Link("Soporte", destination: URL(...))` — Abre una URL en Safari. No es navegación interna, es una apertura de navegador.

### @AppStorage — persistencia en UserDefaults

`@AppStorage("notifications_enabled")` — Este property wrapper guarda y lee valores de **UserDefaults** automáticamente. Es como `@State` pero **persistente**: si el usuario cierra y abre la app, el valor se mantiene.

- `"notifications_enabled"` es la **clave** en UserDefaults (como un nombre de caja donde guardar el valor).
- `= true` es el valor por defecto si no hay nada guardado.
- Soporta tipos basicos: `Bool`, `Int`, `Double`, `String`, `URL`, `Data`.

**Cuando usar `@AppStorage`:** Solo para preferencias simples (tema, idioma, notificaciones). **Nunca** para datos complejos (productos, sesiones, cache) — para eso usa SwiftData o una capa de Infrastructure.

### Donde vive

`Form` y `@AppStorage` viven en la **capa Interface**. Si las preferencias afectan a la lógica de negocio (ej: la moneda cambia como se muestran los precios), el ViewModel lee de `@AppStorage` y lo pasa al UseCase.

---

## Concurrencia en los patrones SwiftUI

Cada modifier de esta lección que recibe un closure `async` tiene implicaciones de concurrencia que no son obvias.

### `.task` — Cancelación ligada al ciclo de vida

El modifier `.task { await viewModel.load() }` no es solo "ejecutar código async al aparecer la vista". Es un **contrato de ciclo de vida**: SwiftUI crea un `Task` cuando la vista aparece y lo cancela cuando la vista desaparece. Si el usuario navega atrás mientras el catálogo carga, el `Task` recibe `CancellationError` y la respuesta del servidor se descarta antes de actualizar la UI.

Esto resuelve el problema clásico de `onAppear` + `Task { }` manual: si creas el task tú mismo, tienes que cancelarlo tú mismo. Con `.task`, SwiftUI se encarga.

```swift
// ✅ .task cancela automáticamente si la vista desaparece
.task {
    await viewModel.load()
}

// ❌ Task manual — se ejecuta aunque la vista ya no exista
.onAppear {
    Task { await viewModel.load() }
}
```

Para que `.task` funcione correctamente, `viewModel.load()` no debe suprimir `CancellationError`:

```swift
func load() async {
    do {
        let products = try await repository.fetchCatalog()
        self.products = products
    } catch is CancellationError {
        // No actualizar UI — la vista ya no existe
        return
    } catch {
        self.errorMessage = error.localizedDescription
    }
}
```

### `.refreshable` — Backpressure y el doble gesto

`.refreshable` tiene una propiedad útil: serializa los gestos. Si el usuario hace pull-to-refresh mientras ya hay un refresh en curso, SwiftUI espera a que el primero termine. Pero hay un caso delicado: si `viewModel.load()` cancela internamente el `Task` anterior para "empezar de cero", el primer refresh recibe `CancellationError` y SwiftUI oculta el spinner — aunque el segundo todavía no ha terminado.

La solución es que el ViewModel solo cancele la tarea anterior si el gesto viene explícitamente de un "nuevo" pull, no si viene de la serialización de SwiftUI. En la práctica, para apps enterprise con latencias normales (<2s), la serialización de SwiftUI es suficiente sin lógica extra.

### `@MainActor` — Por qué las mutaciones del ViewModel son seguras

Las vistas SwiftUI están anotadas `@MainActor` implícitamente a partir de iOS 16. Los closures de `.task`, `.refreshable`, y `.onAppear` heredan este contexto. Por eso `self.products = products` en el ViewModel se ejecuta en el hilo principal sin que tengas que escribir `await MainActor.run { }` explícitamente — siempre que el ViewModel también esté anotado `@MainActor`.

Si el ViewModel no tiene `@MainActor`, el compilador de Swift 6 lo detecta y da error: "sending main actor-isolated value of type '[Product]' to nonisolated context".

---

## Implementación en tu proyecto

Los patrones de esta lección se implementan sobre las vistas ya existentes en el scaffold. Aquí encontrarás los archivos y las divergencias críticas respecto a los ejemplos del curso.

### Archivos del scaffold

| Archivo | Qué contiene |
|---|---|
| `Sources/FeatureCatalogInterface/CatalogView.swift` | Vista de catálogo — añade `.searchable`, `.refreshable`, `.toolbar` |
| `Sources/FeatureLoginInterface/LoginView.swift` | Vista de login — añade `.fullScreenCover` si necesitas onboarding |
| `Sources/AppComposition/AppCompositionRoot.swift` | Composition Root — TabView se instancia aquí o en `StackMyArchitectureApp` |
| `Sources/AppContracts/NavigationContracts.swift` | `AppRoute` enum y protocolo `LoginNavigating` |

### Divergencias críticas respecto a los ejemplos del curso

**1. `AppDestination` no existe en el scaffold — usa `AppRoute`**

El código de TabView en la lección usa `AppDestination.productDetail` para demostrar el patrón completo. El scaffold solo tiene `AppRoute.login` y `AppRoute.catalog`:

```swift
// ✅ Scaffold real (NavigationContracts.swift)
public enum AppRoute: Equatable, Sendable {
    case login
    case catalog
    // productDetail no existe aún — es el ejercicio de Lección 9
}

// El ejemplo de la lección incluye productDetail como destino futuro
// Puedes añadirlo como ejercicio de extensión del scaffold
```

**2. `CatalogView` usa propiedades separadas, no `enum State`**

Los ejemplos de `.searchable` y `.sheet` del curso usan `switch viewModel.state { case .loaded: }`. El scaffold usa propiedades separadas:

```swift
// ✅ Scaffold real (CatalogViewModel.swift)
public private(set) var products: [Product] = []
public private(set) var isLoading = false
public private(set) var errorMessage: String?

// Adapta el .searchable al scaffold:
.searchable(text: $searchText, prompt: "Buscar productos...")
// Y en el body:
let filtered = viewModel.products.filter {
    searchText.isEmpty || $0.title.localizedCaseInsensitiveContains(searchText)
}
List(filtered, id: \.id) { ... }
```

**3. `product.name` no existe — es `product.title`**

```swift
// ❌ Ejemplo del curso
product.name.localizedCaseInsensitiveContains(searchText)

// ✅ Scaffold real (Product.swift)
product.title.localizedCaseInsensitiveContains(searchText)
```

**4. No hay `coordinator.catalogPath: NavigationPath`**

El scaffold usa `NavigationStore` con `routes: [AppRoute]`, no `NavigationPath`. La integración con TabView es:

```swift
// ✅ Scaffold real
@State private var navigationStore = NavigationStore()

TabView {
    Tab("Catálogo", systemImage: "book.fill") {
        NavigationStack(path: Binding(
            get: { navigationStore.routes.filter { $0 != .login }.map { $0 } },
            set: { _ in }
        )) {
            CatalogView(viewModel: compositionRoot.catalogViewModel!)
        }
    }
}
```

O más sencillo: usa `NavigationStack` sin `path` explícito y delega la navegación programática a `NavigationStore.goToCatalog()` desde el `LoginNavigating` protocol.

### Ejercicio: añadir búsqueda al CatalogView del scaffold

1. Abre `Sources/FeatureCatalogInterface/CatalogView.swift`
2. Añade `@State private var searchText = ""`
3. Añade `.searchable(text: $searchText, prompt: "Buscar...")` al `List`
4. Filtra `viewModel.products` por `title` (no `name`) con `localizedCaseInsensitiveContains`
5. Ejecuta los tests de `CatalogViewTests` — deben seguir en verde (la búsqueda es local, no cambia el ViewModel)

---

## 🔭 Explora el scaffold — Navegación SwiftUI enterprise

```bash
open apps/ios/ArchitectureKit/Package.swift
# Navega a: Sources/FeatureCatalogUI/CatalogView.swift
#           Sources/AppContracts/NavigationContracts.swift
```

El scaffold implementa `NavigationStack` con `AppRoute` como tipo de ruta. Observa cómo `LoginNavigating` desacopla la vista de Login del `NavigationStore` concreto: la vista solo llama `navigator?.goToCatalog()`, sin saber qué hay detrás. El ejercicio de búsqueda al final de esta lección se aplica directamente sobre `CatalogView.swift`.

```bash
cd apps/ios/ArchitectureKit
swift test --filter FeatureCatalogUITests
```

---


## Qué sigue

[**Parte 2: Composición y Rendimiento →**](./07b-swiftui-enterprise-composicion.md) — `@ViewBuilder`, `LazyVStack`, `GeometryReader`, listas grandes con identidad estable, y cómo evitar re-renders innecesarios.
