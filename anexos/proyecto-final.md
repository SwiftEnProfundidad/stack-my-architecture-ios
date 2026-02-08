# Proyecto Final: Demuestra lo que has aprendido

Has completado las 5 etapas del curso. Ahora es tu turno. Tienes **dos opciones** para demostrar lo que has aprendido:

**Opción A: Extender tu app del curso (Recomendada)**
Añade nuevas features a la app que has construido (Login + Catalog). Esto demuestra que puedes trabajar en un codebase existente, que es lo más común en el mundo real.

**Opción B: Crear BookShelf desde cero**
Construye una mini-app nueva de catálogo de libros. Esto demuestra que puedes iniciar un proyecto desde zero aplicando todo lo aprendido.

Ambas opciones usan la misma rubrica y requisitos técnicos. Elige la que más te motive.

---

## Opción A: Extender tu app del curso

Añade **una de estas features** a tu app StackMyArchitecture:

### Feature A1: Perfil de usuario
- Pantalla de perfil con datos del usuario (nombre, email)
- Persistencia local con `@AppStorage` o SwiftData
- Navegación desde Catalog (botón de perfil en toolbar)

### Feature A2: Favoritos
- Botón "Añadir a favoritos" en cada producto
- Lista de favoritos persistida (SwiftData)
- Pantalla de "Mis Favoritos" accesible desde Catalog

### Feature A3: Búsqueda de productos
- Barra de búsqueda en Catalog (`.searchable`)
- Filtrado local o remoto de productos
- Resultados en tiempo real

### Feature A4: Carrito de compras
- Botón "Añadir al carrito" en productos
- Badge con cantidad en el icono del carrito
- Pantalla de carrito con resumen y total

---

## Opción B: La app "BookShelf" — Tu estanteria de libros

Vas a construir una app de catalogo de libros desde cero. La app permite al usuario ver una lista de libros y consultar el detalle de cada uno. Es una app sencilla, pero toca TODOS los conceptos del curso.

### Por que esta app

- Tiene un **dominio claro** (libros, autores, precios) — para aplicar Value Objects y modelos.
- Necesita **carga de datos asincrona** — para aplicar async/await, Sendable, repositorios.
- Tiene **dos pantallas** (lista + detalle) — para aplicar navegacion con NavigationPath.
- Requiere **tests** — para aplicar TDD, stubs, spies, Arrange-Act-Assert.
- Es lo suficientemente pequena para hacerla en unas horas, pero lo suficientemente completa para cubrir todo el curso.

---

## Requisitos funcionales (lo que la app tiene que HACER)

Estos son los escenarios BDD que tu app debe cumplir:

### Feature: Ver catalogo de libros

**Escenario 1: Carga exitosa con libros**
- Given el repositorio devuelve una lista de libros
- When la pantalla de catalogo aparece
- Then se muestra la lista de libros con titulo, autor y precio

**Escenario 2: Carga exitosa sin libros**
- Given el repositorio devuelve una lista vacia
- When la pantalla de catalogo aparece
- Then se muestra un mensaje "No hay libros disponibles"

**Escenario 3: Error de conectividad**
- Given el repositorio falla por error de red
- When la pantalla de catalogo aparece
- Then se muestra un mensaje de error con boton de reintentar

### Feature: Ver detalle de un libro

**Escenario 4: Navegacion a detalle**
- Given la lista de libros se ha cargado
- When el usuario pulsa sobre un libro
- Then la app navega a la pantalla de detalle mostrando titulo, autor, precio, y descripcion

---

## Requisitos tecnicos (COMO tiene que estar construida)

### Estructura de carpetas (Feature-First)

```
BookShelf/
├── App/
│   ├── BookShelfApp.swift
│   ├── CompositionRoot.swift
│   └── Navigation/
│       ├── AppDestination.swift
│       └── AppCoordinator.swift
├── Features/
│   └── Books/
│       ├── Domain/
│       │   ├── Models/
│       │   │   └── Book.swift
│       │   └── Errors/
│       │       └── BooksError.swift
│       ├── Application/
│       │   ├── Ports/
│       │   │   └── BookRepository.swift
│       │   └── UseCases/
│       │       └── LoadBooksUseCase.swift
│       ├── Infrastructure/
│       │   ├── DTOs/
│       │   │   └── BookDTO.swift
│       │   ├── BookMapper.swift
│       │   ├── RemoteBookRepository.swift
│       │   └── StubBookRepository.swift
│       └── Interface/
│           ├── BooksViewModel.swift
│           ├── BooksView.swift
│           ├── BookRow.swift
│           ├── BookDetailView.swift
│           └── BooksView+Preview.swift
└── SharedKernel/
    └── HTTPClient.swift (reutiliza el del curso)

BookShelfTests/
├── Features/
│   └── Books/
│       ├── Domain/
│       │   └── BookTests.swift
│       ├── Application/
│       │   ├── LoadBooksUseCaseTests.swift
│       │   └── Helpers/
│       │       └── BookRepositoryStub.swift
│       └── Infrastructure/
│           ├── RemoteBookRepositoryTests.swift
│           └── Helpers/
│               └── HTTPClientStub.swift (reutiliza el del curso)
└── App/
    └── Navigation/
        └── AppCoordinatorTests.swift
```

### Modelo de dominio

Tu struct `Book` debe tener:

```
Book
├── id: String
├── title: String
├── author: String
├── price: Price        (reutiliza el Price del curso o crea uno nuevo)
├── coverURL: URL
└── description: String
```

**Pregunta para ti:** Que protocolos necesita conformar `Book`? Piensa en: tests (necesitas `==`), navegacion (necesitas NavigationPath), concurrencia (es async). Escribe los protocolos ANTES de mirar la respuesta.

<details>
<summary>Respuesta</summary>

`struct Book: Equatable, Hashable, Sendable`

- `Equatable` para XCTAssertEqual en tests y para que SwiftUI detecte cambios.
- `Hashable` para AppDestination.bookDetail(Book) y NavigationPath.
- `Sendable` para cruzar fronteras async (red a UI).

</details>

### Errores de dominio

```swift
enum BooksError: Error, Equatable, Sendable {
    case connectivity
    case invalidData
}
```

**Pregunta para ti:** Por que `Error`, `Equatable` y `Sendable`? Escribe tu respuesta antes de mirar.

<details>
<summary>Respuesta</summary>

- `Error` para poder usar `throw BooksError.connectivity`.
- `Equatable` para verificar en tests QUE error se lanzo: `XCTAssertEqual(error, .connectivity)`.
- `Sendable` porque los errores viajan entre hilos (red a UI) en contextos async.

</details>

---

## Reglas obligatorias

Estas reglas son **innegociables**. Si no las cumples, la practica no esta aprobada:

### 1. TDD obligatorio
- Escribe SIEMPRE el test ANTES del codigo de produccion.
- Ciclo Red, Green, Refactor en cada iteracion.
- Minimo **12 tests** en total (ver rubrica).

### 2. Clean Architecture
- **Domain** no importa Foundation (solo tipos Swift puros). Excepcion: `URL` y `Decimal` que requieren Foundation.
- **Application** no importa SwiftUI ni UIKit.
- **Infrastructure** no expone DTOs fuera de su capa.
- **Interface** no accede al repositorio directamente (pasa por el UseCase).

### 3. Concurrencia segura
- Todos los modelos de dominio: `Sendable`.
- Todos los protocolos de puertos: `Sendable`.
- ViewModels: `@Observable @MainActor final class`.
- No usar `@unchecked Sendable` en produccion (solo en test doubles).

### 4. Navegacion por eventos
- Las features NO se conocen entre si.
- El ViewModel NO sabe de navegacion.
- Los closures (`onBookSelected`) conectan features con el coordinador.
- El coordinador gestiona `NavigationPath`.

### 5. Inyeccion de dependencias
- Ningun componente crea sus propias dependencias.
- Todo se ensambla en el `CompositionRoot`.
- Los tests inyectan stubs/spies.

### 6. Sin acceso global a estado
- No usar instancias globales compartidas para nada.
- No usar variables globales.
- Cada dependencia se inyecta por constructor, nunca se accede de forma global.

---

## El DTO del servidor

El servidor devuelve este JSON para el endpoint `GET /books`:

```json
[
    {
        "id": "1",
        "title": "Clean Architecture",
        "author": "Robert C. Martin",
        "price": 35.99,
        "currency": "EUR",
        "cover_url": "https://example.com/clean-arch.jpg",
        "description": "A craftsman's guide to software structure and design."
    },
    {
        "id": "2",
        "title": "Refactoring",
        "author": "Martin Fowler",
        "price": 42.50,
        "currency": "EUR",
        "cover_url": "https://example.com/refactoring.jpg",
        "description": "Improving the design of existing code."
    }
]
```

**Pregunta para ti:** Tu `BookDTO` debe ser `Decodable` o `Codable`? Y necesita `CodingKeys`?

<details>
<summary>Respuesta</summary>

- Solo `Decodable` (no `Codable`) porque solo RECIBIMOS datos del servidor, no los enviamos.
- Si necesita `CodingKeys` porque el campo `cover_url` del JSON usa snake_case, pero en Swift usamos camelCase (`coverURL`).

</details>

---

## Tests minimos que debes escribir

### Domain (2 tests)
1. `test_book_equality_with_same_properties_returns_true`
2. `test_book_equality_with_different_id_returns_false`

### Application (3 tests)
3. `test_execute_returns_books_from_repository`
4. `test_execute_with_empty_repository_returns_empty_array`
5. `test_execute_with_connectivity_error_throws_connectivity`

### Infrastructure (4 tests)
6. `test_loadAll_on_connectivity_error_throws_connectivity`
7. `test_loadAll_on_non_200_status_throws_connectivity`
8. `test_loadAll_on_200_with_valid_json_returns_mapped_books`
9. `test_loadAll_on_200_with_invalid_json_throws_invalidData`

### Interface / ViewModel (3 tests)
10. `test_load_on_success_sets_loaded_state`
11. `test_load_on_empty_sets_empty_state`
12. `test_load_on_error_sets_error_state`

### Navegacion (2 tests)
13. `test_handleBookSelected_pushes_bookDetail`
14. `test_path_starts_empty`

**Total minimo: 14 tests.**

---

## Rubrica de evaluacion

Evalua tu propio trabajo con esta rubrica. Se honesto contigo mismo — el objetivo es aprender, no "aprobar".

### Arquitectura (0-10 puntos)

| Criterio | Puntos | Como verificar |
|---|---|---|
| Estructura Feature-First correcta | 2 | Las carpetas siguen el esquema de arriba |
| Domain no importa SwiftUI | 2 | Abre cada archivo de Domain: solo `import Foundation` |
| Application no importa SwiftUI | 2 | Abre cada archivo de Application: solo `import Foundation` |
| Infrastructure no expone DTOs al Domain | 2 | `BookDTO` no aparece en ningun archivo de Domain ni Application |
| CompositionRoot ensambla todo | 2 | Ningun componente crea sus dependencias internamente |

### TDD (0-10 puntos)

| Criterio | Puntos | Como verificar |
|---|---|---|
| 14+ tests escritos | 3 | Cmd+U, cuenta los tests |
| Todos los tests pasan | 3 | Cmd+U muestra todo verde |
| Tests usan Arrange-Act-Assert | 2 | Cada test tiene 3 bloques claros separados |
| Tests usan stubs (no red real) | 2 | Ningun test hace peticiones HTTP reales |

### Concurrencia (0-10 puntos)

| Criterio | Puntos | Como verificar |
|---|---|---|
| Modelos de dominio son `Sendable` | 2 | `Book` y `BooksError` conforman `Sendable` |
| Protocolos son `Sendable` | 2 | `BookRepository` y `HTTPClient` conforman `Sendable` |
| ViewModel es `@MainActor` | 2 | `BooksViewModel` tiene `@MainActor` |
| No `@unchecked Sendable` en produccion | 2 | Solo en `BookRepositoryStub` (tests) |
| Strict concurrency sin warnings | 2 | Build Settings, Strict Concurrency = Complete, 0 warnings |

### SwiftUI (0-10 puntos)

| Criterio | Puntos | Como verificar |
|---|---|---|
| ViewModel usa `@Observable` | 2 | No `ObservableObject` ni `@Published` |
| Vista usa `@State` para el ViewModel | 2 | `@State private var viewModel` en la vista |
| Navegacion con `NavigationPath` | 2 | AppCoordinator gestiona un `NavigationPath` |
| `.task` para carga automatica | 2 | La vista usa `.task { await viewModel.load() }` |
| Preview funciona con Stub | 2 | La Preview usa `StubBookRepository` y se ve en Xcode |

### Calidad de codigo (0-10 puntos)

| Criterio | Puntos | Como verificar |
|---|---|---|
| Nombres descriptivos | 2 | Los nombres dicen QUE hace el codigo, no COMO |
| Sin force unwraps innecesarios | 2 | No `!` excepto en URLs hardcodeadas |
| Errores semanticos, no tecnicos | 2 | `BooksError.connectivity`, no `URLError` |
| DTO separado del Domain | 2 | `BookDTO` != `Book`, mapping explicito |
| Sin codigo muerto | 2 | No hay funciones o imports que no se usen |

### Puntuacion total

| Rango | Nivel | Significado |
|---|---|---|
| 45-50 | Excelente | Has interiorizado Clean Architecture y TDD |
| 35-44 | Bien | Entiendes los conceptos, algun detalle por pulir |
| 25-34 | Aceptable | Los fundamentos estan, pero necesitas repasar |
| 0-24 | Necesita repaso | Vuelve a las lecciones y repite los ejercicios |

---

## Consejos para la practica

### El orden importa

Sigue este orden, igual que en el curso:

1. **Primero:** Crea el proyecto Xcode y la estructura de carpetas.
2. **Domain:** Crea `Book`, `BooksError`. Escribe tests de igualdad.
3. **Application:** Crea `BookRepository` (protocolo), `LoadBooksUseCase`. Escribe tests con stub.
4. **Infrastructure:** Crea `BookDTO`, `BookMapper`, `RemoteBookRepository`, `StubBookRepository`. Escribe tests con `HTTPClientStub`.
5. **Interface:** Crea `BooksViewModel`, `BooksView`, `BookRow`, `BookDetailView`. Escribe tests del ViewModel.
6. **Navegacion:** Crea `AppDestination`, `AppCoordinator`. Conecta todo en `CompositionRoot`.
7. **Prueba final:** Cmd+B (compila), Cmd+U (tests), Cmd+R (ejecuta con stub).

### Si te atascas

- **No compila:** Lee el error con atencion. El 90% de los errores en este ejercicio son: falta un protocolo (`Hashable`, `Sendable`), falta un `import`, o un tipo no existe todavia.
- **Test falla:** Verifica el Arrange (configuraste el stub correctamente?), el Act (llamaste al metodo correcto?), y el Assert (comparas lo que crees que comparas?).
- **No sabes como empezar un archivo:** Busca el equivalente en el curso. `Book` es equivalente a `Product`. `BookRepository` es equivalente a `ProductRepository`. `BooksViewModel` es equivalente a `CatalogViewModel`.

### Lo que NO debes hacer

- **No copies y pegues del curso** cambiando nombres. Escribe cada linea tu mismo. El objetivo es que entiendas, no que copies.
- **No te saltes los tests.** Si no escribes tests primero, no estas haciendo TDD y no estas practicando lo que aprendiste.
- **No busques atajos.** Si algo te parece tedioso (crear archivos, escribir stubs), es parte del oficio. La repeticion construye musculo.

---

## Cuando hayas terminado

Si tu puntuacion es 35 o mas, felicidades: has demostrado que puedes construir una app iOS con Clean Architecture, TDD, y SwiftUI moderno. Eso te pone por delante del 90% de los juniors que salen de un bootcamp.

Si tu puntuacion es menor de 35, no te frustres. Vuelve a las lecciones que fallen, repite los ejercicios, y vuelve a intentar esta practica. La repeticion es la madre del aprendizaje.

**El siguiente paso:** Intenta conectar la app a una API real (puedes usar una API publica de libros como Open Library). Eso te obligara a adaptar el DTO al formato real de la API, que es exactamente lo que haras en tu primer trabajo como desarrollador iOS.

Buena suerte. Ya tienes las herramientas. Ahora, a construir.
