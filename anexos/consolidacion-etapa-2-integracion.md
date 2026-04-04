# Consolidación: Etapa 2 - Integración

<!-- sma:meta:v1 -->
meta_leccion:
  tiempo_lectura: "8 min"
  tiempo_practica: "30 min"
  dificultad: 2
  prerequisitos:
    - "02-integración/entregables-etapa-2.md"
  si_te_atascas: "#checklist-de-verificacion"
<!-- /sma:meta:v1 -->

> 🎯 **Has completado la Etapa 2.** Antes de pasar a la Etapa 3, verifica que realmente dominas lo que deberías.

---

## ¿Qué deberías saber hacer sin ayuda?

Si te dieran una nueva feature (ej: "Perfil de usuario") y te dijeran "intégrala con Login y Catalog", deberías poder:

### ✅ Checklist de habilidades

- [ ] **Crear los contratos** (protocolos/eventos) que definen cómo se comunica la nueva feature
- [ ] **Implementar el Composition Root** que cablea todas las dependencias sin que las features se conozcan
- [ ] **Emitir eventos de navegación** desde la nueva feature hacia el coordinator
- [ ] **Escribir tests de integración** que verifiquen que todo funciona junto
- [ ] **Explicar por qué** Login no importa Catalog directamente

---

## Autoevaluación rápida

Responde estas preguntas mentalmente (o escríbelas):

### Pregunta 1: Contratos
> "¿Por qué usamos un enum `NavigationEvent` en lugar de que Login llame directamente a `CatalogView()`?"

<details>
<summary>Ver respuesta esperada</summary>

Porque:
1. **Desacoplamiento**: Login no sabe que existe Catalog
2. **Testabilidad**: Podemos testear que Login emite el evento correcto sin montar toda la app
3. **Flexibilidad**: Cambiar "después de login ir a Catalog" por "ir a Onboarding" es cambiar 1 línea en el coordinator
4. **Deep links**: El coordinator puede recibir eventos externos

</details>

### Pregunta 2: Composition Root
> "¿Qué problema resuelve el Composition Root y por qué no podemos crear dependencias en las Views?"

<details>
<summary>Ver respuesta esperada</summary>

El Composition Root centraliza la creación de dependencias, permitiendo:
- **Inversión de dependencias**: Domain/Application no conocen implementaciones concretas
- **Testabilidad**: Podemos inyectar mocks cambiando 1 línea
- **Cambio de implementación**: Cambiar `RemoteAuthRepository` por `MockAuthRepository` es trivial

Si creamos dependencias en Views, violamos Dependency Inversion y acoplamos las capas.

</details>

### Pregunta 3: Testing
> "¿Cuál es la diferencia entre un test unitario y un test de integración? ¿Cuándo usarías cada uno?"

<details>
<summary>Ver respuesta esperada</summary>

**Test unitario:**
- Prueba una unidad aislada (ej: `LoginUseCase` con `AuthRepositoryStub`)
- Rápido, determinístico, no toca red ni disco
- Usa cuando quieres verificar lógica de negocio pura

**Test de integración:**
- Prueba que múltiples unidades funcionan juntas (ej: Login -> Evento -> Coordinator -> Catalog)
- Más lento, puede tocar infraestructura real o stubs más complejos
- Usa cuando quieres verificar que el cableado funciona

</details>

---

## Mini-ejercicio de consolidación

**Contexto:** Te piden añadir una feature "Favoritos" que permita guardar productos del catálogo.

**Tarea (30 min):**

1. **Diseña los contratos**: ¿Qué eventos necesitas? ¿Qué protocolos?
2. **Esboza el Composition Root**: ¿Cómo se cablea Favoritos con Catalog?
3. **Escribe 1 test de integración**: Describe con palabras (no código) qué verificarías.

No necesitas escribir código real; basta con un diagrama o pseudocódigo.

<details>
<summary>💡 Pista: Eventos necesarios</summary>

Probablemente necesites:
- `productFavorited(id: String)` (desde Catalog)
- `favoritesTapped()` (para navegar a la lista)
- `backToCatalog()` (para volver)

</details>

<details>
<summary>💡 Pista: Contratos</summary>

```swift
// En AppContracts o similar
enum NavigationEvent {
    // ... eventos existentes ...
    case favoritesTapped
    case productFavorited(id: String)
}

protocol FavoritesRepository {
    func save(productId: String) async throws
    func getAll() async throws -> [String]
}
```

</details>

<details>
<summary>✅ Solución de alto nivel</summary>

**Eventos:**
- `productFavorited(id)` - emitido desde Catalog cuando el usuario da ♥️
- `favoritesTapped` - emitido cuando el usuario quiere ver sus favoritos
- `backToCatalog` - para volver

**Composition Root:**
```swift
func makeFavoritesView() -> FavoritesView {
    let repository = LocalFavoritesRepository(store: userDefaults)
    let useCase = GetFavoritesUseCase(repository: repository)
    let viewModel = FavoritesViewModel(useCase: useCase, coordinator: coordinator)
    return FavoritesView(viewModel: viewModel)
}
```

**Test de integración:**
"Verificar que cuando el usuario da favorito en Catalog, el evento `productFavorited` se emite, el coordinator lo maneja, y el repositorio de favoritos guarda el ID. Luego, al navegar a Favoritos, se muestra el producto guardado."

</details>

---

## Checklist de verificación {#checklist-de-verificacion}

Antes de pasar a la Etapa 3, verifica:

- [ ] Puedes explicar el flujo de navegación event-driven sin mirar código
- [ ] Entiendes por qué el Composition Root es el único lugar que conoce todo
- [ ] Has escrito al menos 1 test de integración que pase
- [ ] Puedes crear una nueva feature siguiendo el patrón establecido
- [ ] Entiendes qué son los contratos y por qué son mínimos

**Si marcaste todas:** 🎉 ¡Adelante a la Etapa 3!

**Si no:** Revisa las lecciones correspondientes antes de continuar. La Etapa 3 asume que dominas estos patrones.

---

## Lo que ya sabes hacer (celebración)

- ✅ Construir features que no se conocen entre sí
- ✅ Navegar entre pantallas sin acoplamiento directo
- ✅ Cablear dependencias de forma testeable
- ✅ Escribir tests que verifiquen colaboración entre componentes
- ✅ Explicar arquitectura a otros developers

**Esto ya es nivel profesional.** Muchos developers con años de experiencia no dominan estos patrones.

---

## Continuación

- 
- **Si necesitas repasar:** [Contratos entre features](../02-integración/03-contratos-features.md)

---

