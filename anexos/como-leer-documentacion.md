# Cómo Leer Documentación de Apple Efectivamente

## La habilidad oculta de los desarrolladores senior

Los juniors pierden horas buscando en Stack Overflow. Los seniors van directo a la documentación oficial porque saben cómo leerla. Esta guía te enseña esa habilidad.

> **Tiempo de lectura:** 15 minutos  
> **Tiempo ahorrado:** Horas cada semana, para siempre.

---

## Estructura de la documentación de Apple

Apple tiene 4 fuentes principales de documentación:

| Fuente | Qué encontrarás | Cuándo usarla |
|--------|-----------------|---------------|
| **Apple Developer Documentation** (developer.apple.com) | Referencia de APIs, frameworks, clases | Cuando necesitas saber qué hace una clase/método |
| **Swift.org** | Documentación del lenguaje Swift | Sintaxis, features del lenguaje, evolution proposals |
| **Sample Code** | Proyectos de ejemplo funcionales | Cuando quieres ver cómo se conecta todo |
| **Technical Notes/TN** | Artículos profundos sobre temas específicos | Problemas complejos, edge cases, mejores prácticas |
| **WWDC Videos** | Charlas anuales sobre nuevas features | Entender por qué existen las APIs y cómo Apple las diseñó |

---

## Navegación eficiente en developer.apple.com

### 1. Usa la barra de búsqueda global (Cmd + K)

La búsqueda es tu mejor amiga. No navegues por menús, busca directo:

```
Cmd + K → "Observable" → Enter
```

### 2. Entiende la estructura de una página de API

```
https://developer.apple.com/documentation/swiftui/observable
                    │           │          │
                    │           │          └── Símbolo específico
                    │           └── Framework
                    └── Plataforma
```

### 3. Las 5 secciones clave de toda página de documentación

Cuando abres la doc de cualquier tipo (clase, struct, protocolo), busca en este orden:

```
1. Overview (resumen arriba)
   → ¿Para qué sirve esto? ¿Cuándo lo uso?

2. Topics (secciones del lado izquierdo)
   → Qué métodos/propiedades existen, agrupados por funcionalidad

3. Initializers
   → Cómo crear instancias

4. Instance Methods / Properties
   → Qué puedes hacer con el objeto

5. Relationships (Related Documentation)
   → Protocolos conformados, clases relacionadas
```

---

## Decodificando símbolos y badges

Apple usa iconos para comunicar información rápida:

| Icono | Significado | Importancia |
|-------|-------------|-------------|
| `iOS 17.0+` | Disponible desde iOS 17 | Si tu app soporta iOS 16, no puedes usar esto |
| `macOS 14.0+` | Disponible en macOS | Para apps multiplataforma |
| `Beta` | API en beta | Puede cambiar, no usar en producción |
| `Deprecated` | Obsoleto | Busca la alternativa recomendada |
| `Protocol` | Es un protocolo | Necesitas conformarlo o usar un tipo existente |
| `Struct` / `Class` | Tipo de dato | Afecta cómo se pasa (valor vs referencia) |
| `Actor` | Actor de concurrencia | Seguro para async/await |

---

## Ejemplo práctico: Leer la doc de `@Observable`

**Escenario:** Estás en E1 y no entiendes por qué tu `LoginViewModel` no actualiza la UI.

### Paso 1: Buscar

```
Cmd + K → "@Observable" → Seleccionar "Observable"
```

### Paso 2: Leer Overview

```
"A property wrapper type that supports observing changes to a property."

→ Esto dice: "Esto detecta cambios en propiedades"
```

### Paso 3: Encontrar el ejemplo de código

```swift
@Observable
class Person {
    var name: String
    var age: Int
}
```

**Análisis:**
- La clase debe marcarse con `@Observable`
- Las propiedades var se observan automáticamente
- No necesitas `@Published` como en ObservableObject

### Paso 4: Ver Topics → Instance Properties

```
→ wrappedValue: The underlying observable instance
```

**Conclusión:** Si el ViewModel está marcado con `@Observable` pero la UI no cambia, probablemente:
1. No es `@MainActor`
2. La vista no tiene la dependencia correcta
3. La propiedad es `let` en lugar de `var`

---

## Tip: Lee los "Discussion" en métodos complejos

Los métodos tienen 3 partes:

```swift
func data(for request: URLRequest) async throws -> (Data, URLResponse)
          │              │                    │      │
          │              │                    │      └── Return type
          │              │                    └── Efectos (async throws)
          │              └── Parámetros
          └── Nombre del método
```

**Pero el Discussion es donde está el oro:**

```
Discussion:
"This method returns immediately, but the associated loading ..."

→ Aquí explica el comportamiento real, edge cases, cuándo usarlo vs alternativas
```

---

## Cómo entender un protocolo nuevo

**Ejemplo:** Necesitas implementar `ProductRepository` y ves que debe conformar a `Sendable`.

1. **Busca `Sendable`** en la documentación
2. **Lee Overview:** "A type that can be safely shared across concurrency domains"
3. **Entiende:** Esto es para thread safety en async/await
4. **Ve Conforming Types:** Qué tipos ya son Sendable (String, Int, structs simples)
5. **Implementación:** Tu struct debe ser Sendable si todas sus propiedades lo son

---

## Navegando Sample Code

Los samples de Apple son proyectos completos. Cómo aprovecharlos:

### Estructura de un sample

```
Download → Abre en Xcode → Navega a:
  
README.md        → Qué hace, requisitos, cómo ejecutar
Source Code/     → Código organizado
Configuration/   → Settings, entitlements
```

### Cómo aprender de un sample (ejemplo: Scrumdinger)

1. **Lee el README primero** → Entiende el objetivo
2. **Ejecuta la app** → Vela funcionando
3. **Navega el código en este orden:**
   ```
   App.swift → Views → ViewModels → Use Cases → Domain
   ```
4. **Busca patrones que conozcas:**
   - "¿Cómo hacen navegación?" → Busca `NavigationStack`
   - "¿Cómo guardan datos?" → Busca `@AppStorage` o SwiftData
5. **Copia adapta, no copies directamente:**
   - Entiende por qué lo hicieron así
   - Adapta a tu arquitectura (Clean Architecture)

---

## WWDC Videos: El oro escondido

Las sesiones de WWDC no son solo marketing. Son lecciones de arquitectura de los ingenieros que diseñaron las APIs.

### Cómo ver una sesión eficientemente

**No mires todo de golpe:**

| Tiempo | Acción |
|--------|--------|
| 0:00 - 2:00 | Ver intro (qué problema resuelven) |
| Saltar a demo | Mira el código real funcionando |
| 10:00 - 15:00 | Explicación técnica profunda |
| Final | Recursos y documentación relacionada |

### Sesiones imprescindibles para este curso

| Año | Sesión | Por qué verla |
|-----|--------|---------------|
| WWDC 23 | **Meet SwiftData** | Persistencia moderna |
| WWDC 23 | **Discover Observation** | @Observable en profundidad |
| WWDC 22 | **Meet async/await** | Concurrencia estructurada |
| WWDC 21 | **Meet Swift Concurrency** | Actors, Sendable, Task |
| WWDC 20 | **App essentials** | Ciclo de vida de apps |
| WWDC 19 | **SwiftUI essentials** | Fundamentos de SwiftUI |

**Dónde verlas:** developer.apple.com/wwdc o app Apple Developer

---

## Anti-patrones de lectura (qué NO hacer)

### ❌ Leer de arriba a abajo como un libro

La documentación no es una novela. **Navega por necesidad.**

### ❌ Ignorar los ejemplos de código

```
// No busques solo la API:
func foo(bar: Int) -> String

// Lee el ejemplo:
let result = foo(bar: 42)  // "Hello, 42"
```

### ❌ No revisar version availability

```swift
// No verificar iOS version:
@State var text: String

// Usar sin saber que requiere iOS 17+
// Tu app crashará en iOS 16
```

### ❌ Copiar sin entender

```swift
// Copiado de Stack Overflow:
someAsyncFunction { [weak self] in
    self?.doSomething()
}

// ¿Por qué [weak self]? ¿Cuándo es necesario?
// Si no lo sabes, tendrás bugs de memoria
```

---

## Recursos específicos por tema del curso

### SwiftUI
- **Documentación:** developer.apple.com/documentation/swiftui
- **Sample:** Food Truck, Scrumdinger
- **WWDC:** SwiftUI essentials (2019-2023)

### Concurrencia
- **Documentación:** Concurrency module
- **Sample:** None (usa el curso)
- **WWDC:** Meet async/await (2021), Swift Concurrency (2021-2022)

### SwiftData
- **Documentación:** developer.apple.com/documentation/swiftdata
- **Sample:** Food Truck, Trips
- **WWDC:** Meet SwiftData (2023), Build an app (2023)

### Testing
- **Documentación:** XCTest framework
- **Sample:** None (usa el curso)
- **WWDC:** Testing in Xcode (varios años)

---

## Checklist de lectura efectiva

Cuando consultes documentación, verifica:

- [ ] Busqué directamente con Cmd + K, no navegué menús.
- [ ] Leí el Overview antes de ver código.
- [ ] Revisé version availability (iOS 16+ vs 17+).
- [ ] Encontré al menos un ejemplo de código.
- [ ] Si es un método, leí el Discussion.
- [ ] Busqué Related Documentation para contexto.
- [ ] Si es un protocolo, vi qué tipos lo conforman.
- [ ] Tomé nota de deprecations o warnings.

---

## Ejercicio práctico

**Tarea:** Encuentra la documentación de `NavigationPath` y responde:

1. ¿En qué iOS está disponible?
2. ¿Es struct, class o actor?
3. ¿Conforma a Sendable?
4. ¿Hay un ejemplo de código en la página?
5. ¿Qué método usa para añadir un valor?

**Respuestas esperadas:**
1. iOS 16.0+
2. Struct
3. Sí
4. Sí (el de ejemplo con @State)
5. `append(_:)`

Si encontraste todo en < 2 minutos, estás leyendo documentación efectivamente.

---

> **Regla de oro:** La documentación de Apple es el source of truth. Stack Overflow puede estar desactualizado. La documentación oficial siempre tiene la versión correcta para tu versión de Xcode.

---

**Anexo relacionado:** [Tips del Simulador](simulator-tips.md)
