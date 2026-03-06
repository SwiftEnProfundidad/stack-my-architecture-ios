# ADR-003: Composition Root único para ensamblaje

**Estado:** Aceptado  
**Fecha:** 2026-02-07  
**Contexto:** Etapa 2 - Integración / Lección: [Composition Root](../../02-integración/06-composition-root.md)

---

## Decisión

Centralizar toda la creación y cableado de dependencias en un único **Composition Root** (factorías + wiring), manteniendo el core de la aplicación (Domain y Application) libre de conocimiento sobre implementaciones concretas.

---

## Contexto

### El problema

A medida que el sistema crece de 1 a 2+ features (Login → Catalog), surge una pregunta crítica: **¿quién crea los objetos y quién los conecta?**

Sin una estrategia clara, cada feature tiende a:
1. Crear sus propias dependencias (violando Dependency Inversion)
2. Importar implementaciones concretas de otras features (acoplamiento circular)
3. Mezclar lógica de negocio con lógica de creación (violando Single Responsibility)

### Las restricciones

- Las capas Domain y Application **no deben** conocer implementaciones concretas
- Las features **no deben** depender directamente entre sí
- Los tests unitarios deben poder inyectar stubs/mocks fácilmente
- El código debe ser comprensible para un junior (sin magia de frameworks)

---

## Opciones consideradas

### Opción A: Service Locator (patrón global)

Un registro global donde cualquier clase puede pedir sus dependencias.

```swift
// ❌ Anti-patrón
let repository = ServiceLocator.shared.resolve(AuthRepository.self)
```text

- **Pros:** Fácil de implementar, no cambia la firma de constructores
- **Contras:** 
  - Oculta dependencias (no sabes qué necesita una clase sin leer su implementación)
  - Difícil de testear (estado global compartido)
  - Violación de Dependency Inversion (las clases dependen del locator, no de abstracciónes)

### Opción B: Inyección manual en cada View

Cada View/ViewModel crea sus propias dependencias.

```swift
// ❌ Anti-patrón
struct LoginView: View {
    @StateObject private var viewModel = LoginViewModel(
        useCase: LoginUseCase(repository: RemoteAuthRepository())
    )
}
```text

- **Pros:** Simple en apps pequeñas, no necesitas archivos extra
- **Contras:**
  - Views conocen implementaciones concretas (RemoteAuthRepository)
  - Imposible cambiar implementación sin modificar views
  - Tests requieren modificar el código productivo

### Opción C: Composition Root único (elegida)

Un único lugar (generalmente en la capa de aplicación/main) donde se crean todas las dependencias y se ensambla el grafo de objetos.

```swift
// ✅ Patrón correcto
struct AppCompositionRoot {
    func makeLoginView() -> LoginView {
        let repository = RemoteAuthRepository()
        let useCase = LoginUseCase(repository: repository)
        let viewModel = LoginViewModel(useCase: useCase)
        return LoginView(viewModel: viewModel)
    }
}
```text

- **Pros:**
  - Domain/Application no saben nada de implementaciones
  - Fácil cambiar implementaciones (cambias una línea en el Composition Root)
  - Tests pueden usar el mismo enfoque con stubs
  - Explícito: ves todas las dependencias en un solo lugar
- **Contras:**
  - Archivo adicional que mantener
  - Puede crecer mucho si hay muchas features (se resuelve con factorías por feature)

---

## Decisión detallada

Elegimos **Opción C: Composition Root único** porque:

1. **Respeta Clean Architecture**: Domain y Application permanecen puros, sin imports de infraestructura
2. **Testabilidad**: Podemos crear un `TestCompositionRoot` que inyecte stubs sin tocar código productivo
3. **Escalabilidad**: Aunque crezca a 10 features, el patrón sigue funcionando (usamos factorías internas)
4. **Claridad pedagógica**: Un junior puede ver en un solo archivo cómo se conecta todo

Descartamos Service Locator porque oculta dependencias y crea acoplamiento oculto. Descartamos inyección manual en Views porque viola el principio de inversión de dependencias.

### Implementación en el curso

En `02-integracion/06-composition-root.md` implementamos:

```swift
// AppCompositionRoot.swift
struct AppCompositionRoot {
    private let httpClient: HTTPClient
    private let sessionStore: SessionStore
    
    init(httpClient: HTTPClient, sessionStore: SessionStore) {
        self.httpClient = httpClient
        self.sessionStore = sessionStore
    }
    
    // MARK: - Login Feature
    func makeLoginView(coordinator: AppCoordinator) -> LoginView {
        let repository = RemoteAuthRepository(httpClient: httpClient)
        let useCase = AuthenticateUserUseCase(repository: repository)
        let viewModel = LoginViewModel(useCase: useCase, coordinator: coordinator)
        return LoginView(viewModel: viewModel)
    }
    
    // MARK: - Catalog Feature  
    func makeCatalogView(coordinator: AppCoordinator) -> CatalogView {
        let repository = CachedProductRepository(
            remote: RemoteProductRepository(httpClient: httpClient),
            store: FileProductStore()
        )
        let useCase = LoadProductsUseCase(repository: repository)
        let viewModel = CatalogViewModel(useCase: useCase, coordinator: coordinator)
        return CatalogView(viewModel: viewModel)
    }
}
```

---

## Consecuencias

### Positivas

- **Separación de responsabilidades**: Crear objetos ≠ Usar objetos
- **Flexibilidad**: Cambiar `RemoteAuthRepository` por `MockAuthRepository` requiere cambiar 1 línea
- **Testabilidad**: Tests de integración pueden usar `TestCompositionRoot` con stubs
- **Documentación viva**: El Composition Root muestra el grafo de dependencias completo

### Negativas

- **Boilerplate inicial**: Más código que Service Locator (aceptable por los beneficios)
- **Crecimiento del archivo**: Con 10+ features, el archivo puede ser largo (mitigado con extensiones)

### Riesgos

- **Tentación de "hacer trampas"**: Un desarrollador podría crear dependencias en Views "solo esta vez". Mitigación: code reviews y linting.
- **Ciclos de dependencias**: Si dos features se necesitan mutuamente, el Composition Root no puede resolverlo. Mitigación: diseñar features sin dependencias circulares.

---

## Referencias

- [Lección: Composition Root](../../02-integración/06-composition-root.md)
- [Lección: Feature Login - Infrastructure](../../01-fundamentos/05-feature-login/03-infrastructure.md)
- [Código: AppCompositionRoot en ArchitectureKit](../../apps/ios/ArchitectureKit/Sources/AppComposition/AppCompositionRoot.swift)
- [Patrón: Composition Root (Martin Fowler)](https://martinfowler.com/bliki/CompositionRoot.html)

---

<!-- plantilla-pedagógica:auto -->

## Refuerzo pedagógico
Contexto: normalización automática para `anexos/adrs/ADR-003-composition-root-unico.md`.

### Objetivo
- Define el resultado concreto esperado al finalizar esta lección.

### Prerrequisitos
- Revisa la lección anterior inmediata y confirma los conceptos base antes de continuar.

### Práctica guiada
- Aplica un cambio pequeño y verificable en el scaffold relacionado con esta lección.

### Validación
- Checklist rápido:
  - [ ] Entiendo la decisión técnica principal de la lección.
  - [ ] He ejecutado una comprobación mínima (test/build/script) asociada.
  - [ ] Puedo explicar el trade-off clave con mis palabras.

