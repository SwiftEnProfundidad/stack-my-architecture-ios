# Errores de Compilación: Cómo Leerlos y Solucionarlos

## De "me rompió Xcode" a "sé exactamente qué está pasando"

Los errores del compilador Swift pueden parecer crípticos al principio. Esta guía te enseña a **leer** los mensajes de error como un detective, no a googlearlos ciegamente.

---

## Anatomía de un Error de Swift

### Estructura del mensaje

```
/path/to/file.swift:42:15: error: cannot convert value of type 'String' to expected argument type 'Int'
│                    │  │      │       └─ Descripción del problema
│                    │  │      └─ Tipo de error (error/warning/note)
│                    │  └─ Columna (15)
│                    └─ Línea (42)
└─ Archivo y ruta
```

**Lo que realmente importa:**
1. **Archivo y línea** → Dónde mirar
2. **Descripción** → Qué pasó
3. **Notas adicionales** → Contexto y sugerencias

---

## Errores Comunes y Su Decodificación

### 1. "Cannot convert value of type 'X' to expected argument type 'Y'"

```swift
func calculateAge(birthYear: Int) -> Int {
    return 2024 - birthYear
}

let year = "1990"  // String
calculateAge(birthYear: year)  // ❌ Cannot convert value of type 'String' to expected argument type 'Int'
```

**Diagnóstico:**
- **Qué dice:** Le diste un `String` cuando esperaba un `Int`
- **Por qué pasa:** Swift es type-safe, no convierte automáticamente
- **Cómo arreglar:**

```swift
// Opción 1: Si sabes que es un número válido
if let yearInt = Int(year) {
    calculateAge(birthYear: yearInt)
}

// Opción 2: Forzar (solo si 100% seguro)
calculateAge(birthYear: Int(year)!)  // ⚠️ Cuidado con force unwrap
```

---

### 2. "Value of optional type 'X?' must be unwrapped"

```swift
let optionalName: String? = getUserName()
print(optionalName.uppercased())  // ❌ Value of optional type 'String?' must be unwrapped
```

**Diagnóstico:**
- **Qué dice:** `optionalName` puede ser `nil`, no puedes llamar métodos directamente
- **Las 3 formas de arreglar:**

```swift
// Opción 1: Optional binding (seguro, recomendado)
if let name = optionalName {
    print(name.uppercased())
} else {
    print("No hay nombre")
}

// Opción 2: Guard (para salir temprano)
guard let name = optionalName else {
    print("No hay nombre")
    return
}
print(name.uppercased())

// Opción 3: Nil coalescing (default value)
print((optionalName ?? "Desconocido").uppercased())

// Opción 4: Force unwrap (⚠️ peligroso, evitar)
print(optionalName!.uppercased())  // Crashea si es nil
```

---

### 3. "Type 'X' does not conform to protocol 'Y'"

```swift
protocol Greetable {
    func greet() -> String
}

struct Person: Greetable {  // ❌ Type 'Person' does not conform to protocol 'Greetable'
    let name: String
}
```

**Diagnóstico:**
- **Qué dice:** Dijiste que `Person` conforma `Greetable` pero falta implementar `greet()`
- **Cómo arreglar:**

```swift
struct Person: Greetable {
    let name: String
    
    func greet() -> String {  // ← Implementa el requerimiento
        return "Hola, soy \(name)"
    }
}
```

**Tip:** Presiona `Cmd + .` (Fix-it) en Xcode para que autocomplete el stub del método.

---

### 4. "Reference to property 'X' in closure requires explicit use of 'self'"

```swift
class ViewModel {
    var count = 0
    
    func setup() {
        Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { _ in
            count += 1  // ❌ Reference to property 'count' in closure requires explicit 'self'
        }
    }
}
```

**Diagnóstico:**
- **Qué dice:** En closures, Swift requiere que uses `self` explícitamente para capturar referencias
- **Por qué:** Para que seas consciente de posibles retain cycles
- **Cómo arreglar:**

```swift
Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
    self?.count += 1  // ✅ Usa self explícito y weak para evitar ciclo
}

// O si no hay ciclo de retención:
Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { _ in
    self.count += 1  // ✅ Usa self explícito
}
```

---

### 5. "Escaping closure captures non-escaping parameter 'X'"

```swift
func process(data: String, completion: () -> Void) {
    DispatchQueue.main.async {
        print(data)      // ❌ Escaping closure captures non-escaping parameter 'data'
        completion()     // ❌ Escaping closure captures non-escaping parameter 'completion'
    }
}
```

**Diagnóstico:**
- **Qué dice:** El closure se escapa (se ejecuta después de que la función retorna) pero captura parámetros que no están marcados para escapar
- **Cómo arreglar:**

```swift
func process(data: String, completion: @escaping () -> Void) {
    //                              ↑ @escaping aquí
    DispatchQueue.main.async {
        print(data)
        completion()
    }
}
```

**¿Cuándo usar `@escaping`?**
- El closure se guarda para ejecutar después
- Se usa en async (DispatchQueue, URLSession)
- Se asigna a una propiedad

---

### 6. "Cannot assign to property: 'X' is a 'let' constant"

```swift
struct User {
    let name: String
}

var user = User(name: "Juan")
user.name = "Pedro"  // ❌ Cannot assign to property: 'name' is a 'let' constant
```

**Diagnóstico:**
- **Qué dice:** `name` es constante (`let`), no puede cambiar
- **Opciones:**

```swift
// Opción 1: Si la propiedad debe cambiar, usa var
struct User {
    var name: String  // ← Cambia a var
}

// Opción 2: Si es struct inmutable, crea nueva instancia
user = User(name: "Pedro")  // Structs son value types

// Opción 3: Si debe ser mutable dentro de métodos, mutating
struct Counter {
    var count = 0
    
    mutating func increment() {  // ← mutating para structs
        count += 1
    }
}
```

---

### 7. "Initializer for class 'X' is inaccessible due to 'private' protection level"

```swift
class DatabaseManager {
    private init() {}  // Privado intencionalmente
    static func create() -> DatabaseManager {
        return DatabaseManager()  // Factory method público
    }
}

let db = DatabaseManager()  // ❌ Inaccessible due to 'private' protection level
```

**Diagnóstico:**
- **Qué dice:** El inicializador es `private`, no puedes llamarlo desde fuera
- **Contexto común:** Factory pattern, control de creación
- **Cómo arreglar:**

```swift
// Usa el factory method proporcionado
let db = DatabaseManager.create()

// O si necesitas instanciar directamente, quita 'private'
class DatabaseManager {
    init() {}  // ← Quita private si es necesario
}
```

---

### 8. "Generic parameter 'T' could not be inferred"

```swift
func wrap<T>(value: T) -> [T] {
    return [value]
}

let result = wrap(value: 42)  // ✅ OK, T se infiere como Int

let another = wrap()  // ❌ Generic parameter 'T' could not be inferred
```

**Diagnóstico:**
- **Qué dice:** El compilador no sabe qué tipo es `T`
- **Cómo arreglar:**

```swift
// Opción 1: Especifica explícitamente
let another: [String] = wrap()  // T es String

// Opción 2: Pasa un valor para inferir
let another = wrap(value: "text")  // T se infiere como String
```

---

## Errores de Concurrencia (Swift 6+)

### "Reference to captured var 'X' in concurrently-executing code"

```swift
var counter = 0

Task {
    counter += 1  // ❌ Reference to captured var 'counter' in concurrently-executing code
}
```

**Diagnóstico:**
- **Qué dice:** Estás accediendo a variable mutable desde múltiples hilos (data race)
- **Cómo arreglar:**

```swift
// Opción 1: Actor (recomendado para estado compartido)
actor Counter {
    var value = 0
    func increment() { value += 1 }
}

let counter = Counter()
await counter.increment()

// Opción 2: MainActor para UI
@MainActor
class ViewModel {
    var count = 0  // Seguro acceder desde MainActor
}

// Opción 3: Sendable y valor inmutable
let counter = 0  // let es thread-safe
Task {
    print(counter)  // ✅ OK, no se modifica
}
```

---

### "Expression is 'async' but is not marked with 'await'"

```swift
func fetchData() async -> String { "data" }

func load() {
    let data = fetchData()  // ❌ Expression is 'async' but not marked with 'await'
}
```

**Diagnóstico:**
- **Qué dice:** La función es `async`, debes usar `await` para llamarla
- **Cómo arreglar:**

```swift
func load() async {  // ← La función contenedora debe ser async
    let data = await fetchData()  // ← await aquí
}

// O en Task:
func load() {
    Task {
        let data = await fetchData()  // ← await en contexto async
    }
}
```

---

## Cómo Leer Stack Traces

### Cuando la app crashea en runtime

```
Thread 1: Fatal error: Unexpectedly found nil while unwrapping an Optional value

0  libswiftCore.dylib  specialized _fatalErrorMessage
1  MyApp               LoginViewController.viewDidLoad() at LoginViewController.swift:25
2  MyApp               @objc LoginViewController.viewDidLoad()
3  UIKitCore           -[UIViewController loadViewIfRequired]
```

**Lectura:**
1. **El error:** Force unwrap de nil (`!` en optional nil)
2. **Dónde:** `LoginViewController.swift` línea 25
3. **En qué método:** `viewDidLoad()`

**Acción:** Ve a esa línea y busca el `!`. Reemplaza con `?` o optional binding.

---

## Estrategia de Debugging

### Paso 1: Lee el primer error primero

Los errores de compilación se muestran en orden. El primero suele causar el resto.

```
❌ error 1: Type 'LoginViewModel' does not conform to protocol 'ObservableObject'
❌ error 2: Cannot assign to property: 'state' is immutable  
❌ error 3: Reference to invalid member
```

Arregla el **error 1** primero. Los otros dos probablemente desaparecerán.

### Paso 2: Usa "Fix-it" de Xcode

Presiona `Cmd + .` (punto) sobre el error rojo. Xcode sugiere arreglos automáticos.

**⚠️ Cuidado:** No siempre es lo que quieres, pero es un buen punto de partida.

### Paso 3: Busca en documentación, no solo Stack Overflow

```
error: 'some' return types are only available in iOS 13.0.0 or newer
```

Busca en Apple Developer Docs: `some keyword Swift` o `opaque types`.

---

## Checklist Antes de Pedir Ayuda

Cuando te atasques con un error:

- [ ] ¿Leí el mensaje de error completo (no solo la primera línea)?
- [ ] ¿Verifiqué el número de línea que indica el error?
- [ ] ¿Intenté el Fix-it de Xcode (`Cmd + .`)?
- [ ] ¿Busqué en la documentación oficial de Apple?
- [ ] ¿Revisé si hay un error anterior que causa este?
- [ ] ¿Intenté aislar el problema en un playground?
- [ ] ¿Verifiqué los tipos de todas las variables involucradas?

---

## Errores "Fantasma": Clean Build

A veces Xcode muestra errores que no existen.

**Síntomas:**
- Error en línea que ya borraste
- Error que no tiene sentido
- Error que "debería" estar arreglado

**Solución:**
```
Product → Clean Build Folder (Cmd + Shift + K)
Product → Build (Cmd + B)
```

**Nuclear option (si todo falla):**
```bash
# En Terminal
rm -rf ~/Library/Developer/Xcode/DerivedData
```

---

> **Regla de oro:** Los errores del compilador no son enemigos. Son mensajes del compilador tratando de ayudarte a escribir código seguro. Aprende a leerlos como leerías un email de un colega que revisa tu código.

---

**Anexo relacionado:** [Debugging en Xcode](../05-maestria/10-debugging-xcode.md)
