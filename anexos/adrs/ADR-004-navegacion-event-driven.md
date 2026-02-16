# ADR-004: Navegación event-driven desacoplada

**Estado:** Aceptado  
**Fecha:** 2026-02-07  
**Contexto:** Etapa 2 - Integración / Lección: [Navegación por eventos](../02-integracion/02-navegacion-eventos.md)

---

## Decisión

Las features emiten **eventos de navegación** (intenciones) en lugar de navegar directamente; un **coordinador central** escucha estos eventos y decide las rutas, manteniendo las features completamente desacopladas.

---

## Contexto

### El problema

En apps con múltiples features (Login → Catalog → Detail), surge el dilema: **¿quién decide a dónde ir?**

El enfoque naive es que cada View tenga un `NavigationLink` directo:

```swift
// ❌ Anti-patrón: LoginView conoce CatalogView
NavigationLink(destination: CatalogView()) {
    Text("Ir al catálogo")
}
```

Esto crea:
1. **Acoplamiento directo**: Login importa Catalog
2. **Imposibilidad de deep links**: No hay un lugar central donde interceptar navegaciones
3. **Dificultad para testing**: Para testear Login necesitas el Catalog completo
4. **Código spaghetti**: La lógica de navegación está dispersa en cientos de Views

### Las restricciones

- Features deben poder existir independientemente (compilarse solas)
- Deep links deben ser posibles sin modificar Views
- El flujo de navegación debe ser observable/testeable
- Un junior debe entender dónde mirar para cambiar una transición

---

## Opciones consideradas

### Opción A: NavigationLinks directos entre Views

Cada View conoce y navega directamente a la siguiente.

```swift
// ❌ Anti-patrón
struct LoginView: View {
    var body: some View {
        NavigationLink("Entrar", destination: CatalogView())
    }
}
```

- **Pros:** Simple, nativo de SwiftUI, poco código
- **Contras:**
  - Acoplamiento fuerte entre features
  - Imposible testear navegación en aislamiento
  - No hay lugar central para lógica de navegación (ej: "solo navegar si está autenticado")

### Opción B: Router/Coordinator por feature

Cada feature tiene su propio router que conoce las rutas internas.

```swift
// ⚠️ Parcialmente válido pero complejo
LoginRouter.shared.navigate(to: .catalog)
```

- **Pros:** Desacopla Views de destinos específicos
- **Contras:**
  - Múltiples routers crean confusión (¿cuál uso?)
  - Navegación cross-feature sigue siendo problemática
  - Lógica de navegación dispersa

### Opción C: Event-driven con Coordinator único (elegida)

Las Views emiten eventos semánticos (`loginSucceeded`, `productSelected`); un coordinador único los escucha y decide la navegación.

```swift
// ✅ Patrón correcto
class AppCoordinator {
    func handle(_ event: NavigationEvent) {
        switch event {
        case .loginSucceeded:
            currentRoute = .catalog
        case .productSelected(let id):
            currentRoute = .productDetail(id: id)
        }
    }
}
```

- **Pros:**
  - Features no conocen otras features
  - Lógica de navegación centralizada y testeable
  - Deep links fáciles (el coordinator puede recibir rutas externas)
  - Observable: puedes loggear todas las navegaciones
- **Contras:**
  - Más boilerplate que NavigationLink directo
  - Requiere disciplina (no "hacer trampas" con NavigationLink oculto)

---

## Decisión detallada

Elegimos **Opción C: Event-driven con Coordinator único** porque:

1. **Desacoplamiento total**: Login no sabe que existe Catalog; solo emite "loginSucceeded"
2. **Testabilidad**: Podemos testear que Login emite el evento correcto sin montar toda la app
3. **Deep links**: El coordinator puede recibir `handle(.deepLink("/product/123"))` sin modificar Views
4. **Flexibilidad**: Cambiar "después de login ir a Catalog" por "después de login ir a Onboarding" es cambiar 1 línea en el coordinator

Descartamos NavigationLinks directos por el acoplamiento que crean. Descartamos routers por feature por la complejidad innecesaria y la falta de un lugar único de verdad.

### Implementación en el curso

Definimos un enum de eventos semánticos:

```swift
enum NavigationEvent {
    case loginSucceeded
    case logoutRequested
    case productSelected(ProductID)
    case backToCatalog
    case deepLink(path: String)
}
```

El coordinator implementa la política de navegación:

```swift
@Observable
class AppCoordinator {
    enum Route: Hashable {
        case login
        case catalog
        case productDetail(id: String)
    }
    
    var currentRoute: Route = .login
    var navigationPath = NavigationPath()
    
    func handle(_ event: NavigationEvent) {
        switch event {
        case .loginSucceeded:
            currentRoute = .catalog
            navigationPath.removeLast(navigationPath.count)
        case .productSelected(let id):
            navigationPath.append(Route.productDetail(id: id))
        case .deepLink(let path):
            handleDeepLink(path)
        }
    }
}
```

---

## Consecuencias

### Positivas

- **Features desacopladas**: Login puede existir sin saber que existe Catalog
- **Navegación testeable**: Podemos testear el coordinator con eventos sin montar Views
- **Deep links nativos**: El coordinator es el único lugar que necesita modificación
- **Trazabilidad**: Podemos loggear todos los eventos de navegación para analytics

### Negativas

- **Curva de aprendizaje**: Un junior necesita entender el patrón antes de ser productivo
- **Boilerplate**: Más código que NavigationLink directo
- **Riesgo de inconsistencia**: Si alguien usa NavigationLink directo "solo esta vez", rompe el patrón

### Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| Developer usa NavigationLink directo | Code reviews + linting |
| Coordinator crece demasiado | Dividir en extensiones por feature |
| Eventos se descontrolan | Mantener `NavigationEvent` pequeño (máx 10-15 casos) |

---

## Referencias

- [Lección: Navegación por eventos](../02-integracion/02-navegacion-eventos.md)
- [Lección: Contratos entre features](../02-integracion/03-contratos-features.md)
- [Patrón: Coordinator (Soroush Khanlou)](http://khanlou.com/2015/10/coordinators-redux/)

---

**Anterior:** [ADR-003: Composition Root único para ensamblaje ←](ADR-003-composition-root-unico.md) · **Siguiente:** [ADR-005: Contratos entre features por eventos/modelos mín... →](ADR-005-contratos-features.md)
