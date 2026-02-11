# Atlas visual de arquitectura

> Este documento es tu **mapa de referencia permanente**. Cuando estés perdido en una lección, vuelve aquí para ver el panorama completo.

---

## 0. Convención de flechas del curso (léela una vez)

Antes de interpretar cualquier diagrama, usa esta clave semántica:

```mermaid
graph LR
    A["A"] -->|"uso directo"| B["B"]
    C["A"] -.->|"wiring / configuración"| D["B"]
    E["A"] -->|"contrato/protocolo"| F["B"]
    G["A"] -.->|"evento / notificación"| H["B"]
```

- `-->` = dependencia o llamada directa en runtime.
- `-.->` = relación de ensamblado/wiring o notificación desacoplada (según etiqueta).
- Etiqueta `"contrato/protocolo"` = dependencia hacia abstracción.
- Etiqueta `"evento/notificación"` = salida de información, no uso fuerte.

Nota de herramienta: en Mermaid `flowchart` no todos los estilos de punta (abierta/cerrada) son igual de expresivos que en herramientas de dibujo manual. Por eso la convención oficial del curso usa **línea + etiqueta textual** como fuente de verdad.

---

## 1. Clean Architecture: las capas y la regla de dependencia

Clean Architecture organiza el código en **anillos concéntricos**. La regla fundamental es una sola: **las dependencias siempre apuntan hacia el centro**. Nunca al revés.

```mermaid
graph TB
    subgraph OUTER["Capa externa: Frameworks y drivers"]
        direction TB
        SW["SwiftUI"]
        URL["URLSession"]
        JSON["JSONDecoder"]
        KCH["Keychain"]
    end

    subgraph ADAPT["Adaptadores: Infrastructure + Interface"]
        direction TB
        VM["ViewModels<br/>LoginViewModel<br/>CatalogViewModel"]
        REPO["Repositories concretos<br/>RemoteAuthGateway<br/>RemoteProductRepository"]
    end

    subgraph APP["Application: Casos de uso y puertos"]
        direction TB
        UC["UseCases<br/>LoginUseCase<br/>LoadProductsUseCase"]
        PORT["Puertos / Protocolos<br/>AuthGateway<br/>ProductRepository"]
    end

    subgraph DOMAIN["Domain: Reglas de negocio puras"]
        direction TB
        ENT["Modelos<br/>Email, Password, Session<br/>Product, Price"]
        ERR["Errores semanticos<br/>LoginError, CatalogError"]
    end

    OUTER --> ADAPT
    ADAPT --> APP
    APP --> DOMAIN

    style DOMAIN fill:#d4edda,stroke:#28a745
    style APP fill:#cce5ff,stroke:#007bff
    style ADAPT fill:#fff3cd,stroke:#ffc107
    style OUTER fill:#f8d7da,stroke:#dc3545
```

**Como leer este diagrama:**

- **Centro (verde) = Domain:** No importa nada externo. No sabe que existe URLSession, SwiftUI ni Firebase. Solo contiene reglas de negocio puras. Si borras toda la app excepto Domain, el Domain sigue compilando.
- **Segundo anillo (azul) = Application:** Conoce Domain. Define los puertos (protocolos) que necesita y los casos de uso que orquestan el flujo. No sabe cómo se implementan los puertos.
- **Tercer anillo (amarillo) = Adaptadores:** Infrastructure implementa los puertos de Application (conecta con el mundo real). Interface consume Application para mostrar datos al usuario.
- **Exterior (rojo) = Frameworks:** Son las herramientas concretas de Apple (SwiftUI, URLSession, etc.). Viven en el borde, nunca en el centro.

**La regla de oro:** Las flechas SOLO van hacia dentro. Domain nunca importa Application. Application nunca importa Infrastructure. Si ves una flecha apuntando hacia fuera, hay un error de arquitectura.

---

## 2. Dependency Inversion: por que existen los protocolos en las fronteras

Sin inversión de dependencias, Application dependería directamente de Infrastructure:

```mermaid
graph LR
    subgraph SIN_INV["SIN inversion: acoplamiento directo"]
        UC1["LoginUseCase"] --> RG1["RemoteAuthGateway"]
        RG1 --> URL1["URLSession"]
    end

    style SIN_INV fill:#f8d7da,stroke:#dc3545
```

Problema: si cambias la implementación de `RemoteAuthGateway` (por ejemplo, migras de URLSession a Firebase), tienes que **tocar LoginUseCase**. Y si tocas LoginUseCase, tienes que re-testear todo el flujo.

Con inversión de dependencias, Application define un protocolo y no sabe quién lo implementa:

```mermaid
graph LR
    subgraph CON_INV["CON inversion: desacoplamiento por protocolo"]
        UC2["LoginUseCase"] --> PROTO["AuthGateway<br/>(protocolo)"]
        PROTO -.->|"implementa"| RG2["RemoteAuthGateway"]
        PROTO -.->|"implementa"| STUB["AuthGatewayStub<br/>(tests)"]
        RG2 --> URL2["URLSession"]
    end

    style CON_INV fill:#d4edda,stroke:#28a745
```

**La flecha de dependencia se invierte:** ahora `RemoteAuthGateway` depende de `AuthGateway` (el protocolo que vive en Application), no al revés. LoginUseCase solo conoce el protocolo.

Beneficios concretos:

- **Testabilidad:** En tests, inyectas un stub en vez de la implementación real. El UseCase no sabe la diferencia.
- **Intercambiabilidad:** Puedes cambiar de URLSession a Firebase sin tocar Application ni Domain.
- **Compilación independiente:** Application compila sin que exista Infrastructure.

---

## 3. Flujo end-to-end de una peticion (Login)

Este diagrama muestra el viaje completo de los datos cuando el usuario pulsa "Login", desde la UI hasta el servidor y de vuelta:

```mermaid
sequenceDiagram
    participant U as Usuario
    participant V as LoginView
    participant VM as LoginViewModel
    participant UC as LoginUseCase
    participant GW as RemoteAuthGateway
    participant HTTP as URLSession
    participant API as Servidor

    U->>V: Escribe email + password, pulsa Login
    V->>VM: await submit()
    VM->>VM: state = loading

    VM->>UC: try await execute(email, password)
    UC->>UC: Valida Email y Password (Value Objects)
    UC->>GW: try await authenticate(credentials)
    GW->>GW: Construye URLRequest
    GW->>HTTP: try await data(for: request)
    HTTP->>API: POST /auth/login (JSON)

    API-->>HTTP: 200 OK + JSON (token)
    HTTP-->>GW: (Data, HTTPURLResponse)
    GW->>GW: Decodifica JSON a SessionDTO
    GW->>GW: Mapea SessionDTO a Session (Domain)
    GW-->>UC: Session
    UC-->>VM: Session

    VM->>VM: state = success
    VM->>VM: onLoginSucceeded(session)
    V-->>U: Navega al Catalogo
```

**Que datos viajan en cada tramo:**

| Tramo | Datos que viajan | Tipo |
|---|---|---|
| Usuario a View | Strings crudos (email, password) | `String` |
| View a ViewModel | Nada (la View llama `submit()`, el VM ya tiene los strings) | — |
| ViewModel a UseCase | Strings crudos | `String` |
| UseCase (interno) | Value Objects validados | `Email`, `Password` → `Credentials` |
| UseCase a Gateway | Credenciales tipadas | `Credentials` |
| Gateway (interno) | Request HTTP | `URLRequest` con JSON body |
| URLSession a Servidor | Bytes en red | HTTP POST |
| Servidor a URLSession | Bytes en red | HTTP 200 + JSON |
| Gateway (interno) | DTO intermedio | `SessionDTO` → `Session` |
| Gateway a UseCase | Modelo de dominio | `Session` |
| UseCase a ViewModel | Modelo de dominio | `Session` |
| ViewModel a View | Estado de UI | `.loading` / `.idle` |

---

## 4. Flujo end-to-end de una peticion (Catalog)

```mermaid
sequenceDiagram
    participant U as Usuario
    participant V as CatalogView
    participant VM as CatalogViewModel
    participant UC as LoadProductsUseCase
    participant REPO as RemoteProductRepository
    participant HTTP as URLSession
    participant API as Servidor

    V->>VM: await load() (en .task)
    VM->>VM: state = .loading

    VM->>UC: try await execute()
    UC->>REPO: try await loadAll()
    REPO->>REPO: Construye URLRequest
    REPO->>HTTP: try await data(for: request)
    HTTP->>API: GET /products

    API-->>HTTP: 200 OK + JSON array
    HTTP-->>REPO: (Data, HTTPURLResponse)
    REPO->>REPO: Decodifica [ProductDTO]
    REPO->>REPO: Mapea [ProductDTO] a [Product]
    REPO-->>UC: [Product]
    UC-->>VM: [Product]

    alt Lista con productos
        VM->>VM: state = .loaded(products)
    else Lista vacia
        VM->>VM: state = .empty
    end

    V-->>U: Muestra lista o mensaje
```

---

## 5. Grafo de dependencias entre componentes

Este diagrama muestra TODOS los componentes del proyecto y quién depende de quién:

```mermaid
graph TD
    subgraph DOMAIN_LOGIN["Domain: Login"]
        Email["Email"]
        Password["Password"]
        Session["Session"]
        Credentials["Credentials"]
        LoginError["LoginError"]
    end

    subgraph DOMAIN_CATALOG["Domain: Catalog"]
        Product["Product"]
        Price["Price"]
        CatalogError["CatalogError"]
    end

    subgraph APP_LOGIN["Application: Login"]
        AuthGW["AuthGateway<br/>(protocolo)"]
        LoginUC["LoginUseCase"]
    end

    subgraph APP_CATALOG["Application: Catalog"]
        ProdRepo["ProductRepository<br/>(protocolo)"]
        LoadUC["LoadProductsUseCase"]
    end

    subgraph INFRA["Infrastructure"]
        HTTPClient["HTTPClient<br/>(protocolo)"]
        URLSessionHTTP["URLSessionHTTPClient"]
        RemoteAuth["RemoteAuthGateway"]
        RemoteProd["RemoteProductRepository"]
        SessionDTO["SessionDTO + Mapper"]
        ProductDTO["ProductDTO + Mapper"]
    end

    subgraph INTERFACE["Interface"]
        LoginVM["LoginViewModel"]
        CatalogVM["CatalogViewModel"]
        LoginView["LoginView"]
        CatalogView["CatalogView"]
        AppCoord["AppCoordinator"]
    end

    subgraph COMPOSITION["Composition Root"]
        CR["CompositionRoot<br/>Ensambla todo"]
    end

    LoginUC --> Email
    LoginUC --> Password
    LoginUC --> Credentials
    LoginUC --> AuthGW
    LoadUC --> ProdRepo

    RemoteAuth --> AuthGW
    RemoteAuth --> HTTPClient
    RemoteAuth --> SessionDTO
    RemoteProd --> ProdRepo
    RemoteProd --> HTTPClient
    RemoteProd --> ProductDTO
    URLSessionHTTP --> HTTPClient

    LoginVM --> LoginUC
    CatalogVM --> LoadUC

    LoginView --> LoginVM
    CatalogView --> CatalogVM
    AppCoord --> LoginVM
    AppCoord --> CatalogVM

    CR --> URLSessionHTTP
    CR --> RemoteAuth
    CR --> RemoteProd
    CR --> LoginUC
    CR --> LoadUC
    CR --> LoginVM
    CR --> CatalogVM
    CR --> AppCoord

    style DOMAIN_LOGIN fill:#d4edda,stroke:#28a745
    style DOMAIN_CATALOG fill:#d4edda,stroke:#28a745
    style APP_LOGIN fill:#cce5ff,stroke:#007bff
    style APP_CATALOG fill:#cce5ff,stroke:#007bff
    style INFRA fill:#fff3cd,stroke:#ffc107
    style INTERFACE fill:#e2d5f1,stroke:#6f42c1
    style COMPOSITION fill:#f8d7da,stroke:#dc3545
```

**Como leer este grafo:**

- **Verde (Domain):** No tiene flechas salientes hacia otras capas. Solo depende de sí mismo.
- **Azul (Application):** Depende de Domain. Define protocolos (puertos) que otros implementan.
- **Amarillo (Infrastructure):** Depende de Application (implementa sus protocolos) y de Domain (usa sus tipos).
- **Morado (Interface):** Depende de Application (consume UseCases).
- **Rojo (Composition Root):** Depende de TODO. Es el unico lugar que conoce todas las piezas. Por eso vive fuera del core.

**Regla: ninguna flecha verde apunta hacia amarillo, morado o rojo. Si lo hiciera, Domain estaría contaminado.**

---

## 6. Fronteras de concurrencia (Swift 6.2)

Este diagrama muestra las zonas de aislamiento y donde se necesita `Sendable`:

```mermaid
graph TD
    subgraph MAIN["MainActor (hilo principal)"]
        direction TB
        VIEW["LoginView / CatalogView<br/>SwiftUI views"]
        VM["ViewModels<br/>@MainActor @Observable"]
    end

    subgraph NONISOLATED["Nonisolated (cualquier hilo)"]
        direction TB
        UC["UseCases<br/>struct Sendable"]
        DOMAIN["Domain models<br/>struct Sendable Equatable"]
    end

    subgraph COOPERATIVE["Cooperative thread pool"]
        direction TB
        GW["Gateways / Repositories<br/>struct Sendable"]
        HTTP["URLSession<br/>async await"]
    end

    VIEW --> VM
    VM -->|"await (cruza frontera)"| UC
    UC -->|"await (cruza frontera)"| GW
    GW --> HTTP

    HTTP -->|"Data cruza de vuelta"| GW
    GW -->|"Product/Session cruza"| UC
    UC -->|"resultado cruza a MainActor"| VM
    VM --> VIEW

    style MAIN fill:#e2d5f1,stroke:#6f42c1
    style NONISOLATED fill:#d4edda,stroke:#28a745
    style COOPERATIVE fill:#cce5ff,stroke:#007bff
```

**Que significa cada zona:**

- **MainActor (morado):** Todo lo que toca la UI. SwiftUI y ViewModels viven aqui. El compilador garantiza que las mutaciones de estado ocurren en el hilo principal.
- **Nonisolated (verde):** UseCases y Domain models son structs `Sendable`. Pueden ejecutarse en cualquier hilo sin riesgo porque son inmutables o value types.
- **Cooperative thread pool (azul):** Las operaciones async (red, disco) se ejecutan aqui. URLSession devuelve datos que cruzan de vuelta hacia MainActor.

**Donde se necesita Sendable:** Cada vez que un dato **cruza** de una zona a otra (las flechas del diagrama), ese dato debe ser `Sendable`. Por eso todos nuestros modelos (Email, Product, Session, etc.) son structs conformando `Sendable`.

**Cancelacion:** Cuando el usuario sale de una pantalla, la `Task` que lanzó el `.task` de SwiftUI se cancela automaticamente. Esa cancelacion se propaga por toda la cadena: ViewModel → UseCase → Gateway → URLSession. Si URLSession recibe la cancelacion, deja de esperar la respuesta del servidor.

---

## 7. Estructura SPM objetivo (Etapa 4)

Este diagrama muestra la estructura de targets SPM hacia la que evoluciona el proyecto:

```mermaid
graph TD
    subgraph SHARED["SharedKernel"]
        SK["Errores base, tipos primitivos<br/>HTTPClient protocolo<br/>helpers puros"]
    end

    subgraph PLATFORM["Platform"]
        PL["URLSessionHTTPClient<br/>Keychain<br/>FileSystem"]
    end

    subgraph BACKEND["BackendFirebase"]
        FB["FirebaseAuthAdapter<br/>FirestoreAdapter<br/>encapsulado"]
    end

    subgraph LOGIN["Feature Login"]
        LD["LoginDomain"]
        LA["LoginApplication"]
        LI["LoginInterface"]
        LINF["LoginInfrastructure"]
    end

    subgraph CATALOG["Feature Catalog"]
        CD["CatalogDomain"]
        CA["CatalogApplication"]
        CI_T["CatalogInterface"]
        CINF["CatalogInfrastructure"]
    end

    subgraph NAV["NavigationPlatform"]
        NP["Event bus<br/>Coordinator<br/>Deep links"]
    end

    subgraph COMP["AppComposition"]
        AC["Composition Root<br/>Factories / Wiring / DI"]
    end

    LD --> SK
    LA --> LD
    LI --> LA
    LI --> NP
    LINF --> LA
    LINF --> PL
    LINF --> BACKEND

    CD --> SK
    CA --> CD
    CI_T --> CA
    CI_T --> NP
    CINF --> CA
    CINF --> PL
    CINF --> BACKEND

    PL --> SK
    BACKEND --> SK

    AC --> LINF
    AC --> CINF
    AC --> LI
    AC --> CI_T
    AC --> NP
    AC --> PL
    AC --> BACKEND

    style SHARED fill:#f8f9fa,stroke:#6c757d
    style PLATFORM fill:#fff3cd,stroke:#ffc107
    style BACKEND fill:#fce4ec,stroke:#e91e63
    style LOGIN fill:#d4edda,stroke:#28a745
    style CATALOG fill:#d4edda,stroke:#28a745
    style NAV fill:#e2d5f1,stroke:#6f42c1
    style COMP fill:#f8d7da,stroke:#dc3545
```

**Reglas de dependencia (enforceables por CI):**

| Target | Puede importar | NO puede importar |
|---|---|---|
| `*Domain` | Solo `SharedKernel` | Todo lo demas |
| `*Application` | `*Domain` + `SharedKernel` | Interface, Infrastructure, Platform, Backend |
| `*Interface` | `*Application` + `NavigationPlatform` | Infrastructure, Platform, Backend |
| `*Infrastructure` | `*Application` + `Platform` + `Backend*` | Interface, otros Features directamente |
| `Platform` | `SharedKernel` | Features, Backend |
| `Backend*` | `SharedKernel` | Features, Platform |
| `AppComposition` | Todo | — (es el unico que puede) |

**Entre features:** nunca importar clases internas de otra feature. Solo comunicacion via `NavigationPlatform` (eventos) o `FeatureXContracts` (modelos publicos).

---

## 8. Backend Firebase encapsulado en Infrastructure

```mermaid
graph TD
    subgraph DOMAIN["Domain (no sabe de Firebase)"]
        Session_D["Session"]
        Product_D["Product"]
        AuthGW_D["AuthGateway (protocolo)"]
        ProdRepo_D["ProductRepository (protocolo)"]
    end

    subgraph BACKEND_FB["BackendFirebase (encapsulado)"]
        FBAuth["FirebaseAuthAdapter"]
        FBStore["FirestoreProductAdapter"]
        FBConfig["FirebaseConfig<br/>plist / env"]
    end

    subgraph INFRA["Infrastructure (conecta puertos con backends)"]
        AuthImpl["FirebaseAuthGateway<br/>implementa AuthGateway"]
        ProdImpl["FirestoreProductRepository<br/>implementa ProductRepository"]
    end

    AuthImpl --> AuthGW_D
    AuthImpl --> FBAuth
    ProdImpl --> ProdRepo_D
    ProdImpl --> FBStore

    FBAuth --> FBConfig
    FBStore --> FBConfig

    style DOMAIN fill:#d4edda,stroke:#28a745
    style BACKEND_FB fill:#fce4ec,stroke:#e91e63
    style INFRA fill:#fff3cd,stroke:#ffc107
```

**Principio clave:** Domain y Application no saben que Firebase existe. Solo conocen `AuthGateway` y `ProductRepository` (protocolos). Infrastructure es quien conecta esos protocolos con los adaptadores concretos de Firebase.

Si mañana migras de Firebase a Supabase, solo cambias `BackendFirebase` por `BackendSupabase` y las implementaciones en Infrastructure. **Domain, Application e Interface no se tocan.**

---

## Como usar este atlas

- **Antes de empezar una leccion:** mira el diagrama 1 (capas) para ubicar donde estas trabajando.
- **Si no entiendes por que existe un protocolo:** mira el diagrama 2 (Dependency Inversion).
- **Si no entiendes el flujo de datos:** mira los diagramas 3 o 4 (secuencias end-to-end).
- **Si no sabes quien depende de quien:** mira el diagrama 5 (grafo de dependencias).
- **Si no entiendes `Sendable` o `@MainActor`:** mira el diagrama 6 (concurrencia).
- **Si quieres ver la estructura de modulos futura:** mira el diagrama 7 (SPM).
- **Si quieres saber como encaja Firebase:** mira el diagrama 8 (backend).

**Anterior:** [Glosario](../glosario.md) · **Inicio:** [README](../../README.md)
