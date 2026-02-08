# Debugging en Xcode: Encuentra y arregla bugs como un profesional

## Por qué esta lección es crítica

Saber escribir código es importante. Pero saber **encontrar y arreglar bugs** es lo que te hace un desarrollador profesional. En esta lección aprenderás las herramientas de Xcode que te permiten diagnosticar problemas rápidamente.

> **Tiempo estimado:** 45 minutos de lectura + 30 minutos de práctica.

---

## El mindset del debugging

Antes de las herramientas, la actitud:

1. **El bug es información.** No te frustres; el bug te está diciendo dónde está el problema.
2. **Reproduce primero.** Si no puedes reproducirlo consistentemente, no puedes arreglarlo.
3. **Divide y vencerás.** Elimina código hasta aislar el problema.
4. **Cambia una cosa a la vez.** Si haces 5 cambios y funciona, no sabes cuál arregló el problema.

---

## Herramienta 1: Breakpoints (Los puntos de interrupción)

Los breakpoints pausan la ejecución en una línea específica. Puedes inspeccionar variables y entender el estado de tu app en ese momento.

### Tipos de breakpoints

**Breakpoint simple:**
```
Click en el margen izquierdo de la línea 42
→ Se añade un punto azul
→ La app se pausa al llegar a esa línea
```

**Breakpoint condicional:**
```
Click derecho en el breakpoint → Edit breakpoint
→ Añade condición: `email.isEmpty`
→ Solo se pausa cuando email está vacío
```

**Breakpoint con acción:**
```
Edit breakpoint → Add Action → Log Message
→ Message: "Email value: @email@"
→ Imprime en consola sin pausar la ejecución
```

### Atajos de teclado esenciales

| Atajo | Acción |
|-------|--------|
| `Cmd + \` | Añadir/quitar breakpoint en línea actual |
| `Cmd + Y` | Activar/desactivar todos los breakpoints |
| `F6` | Step Over (ejecuta línea actual, no entra en funciones) |
| `F7` | Step Into (entra en la función de la línea actual) |
| `F8` | Step Out (sale de la función actual) |
| `Ctrl + Cmd + Y` | Continue (sigue ejecutando hasta el siguiente breakpoint) |

### Ejemplo práctico: Debug de Login

```swift
// En LoginViewModel.swift

func submit() async {
    // Breakpoint 1: ¿Llegamos aquí?
    isLoading = true
    
    do {
        // Breakpoint 2: ¿Qué valor tiene email?
        let emailVO = try Email(value: email)
        
        // Breakpoint 3: ¿Se creó correctamente?
        let credentials = Credentials(email: emailVO, password: passwordVO)
        
        let session = try await loginUseCase.execute(credentials: credentials)
        
        // Breakpoint 4: ¿Login exitoso?
        onLoginSucceeded(session)
        
    } catch {
        // Breakpoint 5: ¿Qué error ocurrió?
        print("Error: \(error)")
    }
}
```

**Flujo de debugging:**
1. Pon breakpoint en línea 2 (isLoading = true)
2. Ejecuta app, escribe email, pulsa botón
3. App se pausa en breakpoint
4. En el panel de variables, verifica: `email`, `password`, `isLoading`
5. Pulsa F6 (Step Over) para avanzar línea por línea
6. Observa cómo cambian las variables

---

## Herramienta 2: La consola y LLDB

La consola de Xcode no solo muestra prints. Es un intérprete de comandos LLDB donde puedes ejecutar código en tiempo real.

### Comandos LLDB útiles

```lldb
// Inspeccionar variable
(lldb) po email
"user@test.com"

// Inspeccionar objeto completo
(lldb) po loginUseCase
<LoginUseCase: 0x600003b180a0>

// Evaluar expresión
(lldb) po email.isEmpty
false

// Llamar a método
(lldb) po Email(value: "test@test.com")
▿ Email
  - value: "test@test.com"

// Castear y explorar
(lldb) po error as? AuthError
▿ Optional(AuthError.invalidEmail)
  - some: AuthError.invalidEmail
```

### `po` vs `p`

- `po`: Print object. Muestra la descripción del objeto (usa `debugDescription` o `description`).
- `p`: Print. Muestra la representación cruda, útil para structs simples.

### Ejemplo: Debug de error de red

```lldb
// El catch block se ejecutó, quieres saber qué pasó
(lldb) po error
Error Domain=NSURLErrorDomain Code=-1009 "The Internet connection appears to be offline."

(lldb) po (error as NSError).code
-1009

(lldb) po (error as NSError).userInfo
["NSLocalizedDescription": "The Internet connection appears to be offline."]
```

---

## Herramienta 3: View Debugger (Debug de UI)

Cuando la UI no se ve como esperas, el View Debugger te muestra la jerarquía de vistas en 3D.

### Cómo usarlo

1. Ejecuta la app
2. Cuando la pantalla problemática esté visible, pulsa el botón **Debug View Hierarchy** en la barra de debug (parece un árbol de capas)
3. Xcode captura un snapshot de todas las vistas

### Qué puedes ver

- **Jerarquía:** Lista de todas las vistas, de atrás hacia adelante
- **Constraints:** Todas las constraints de Auto Layout con sus valores actuales
- **Frames:** Posición y tamaño exacto de cada vista
- **3D:** Rotar la escena para ver qué vistas están detrás de otras

### Caso común: Elemento no visible

Problema: Un botón no aparece en pantalla.

1. Debug View Hierarchy
2. Busca el botón en la lista
3. Verifica:
   - ¿Está en la jerarquía? Si no, no se añadió a la vista padre.
   - ¿Frame es (0,0,0,0)? Problema de constraints.
   - ¿Hidden = true? Se ocultó explícitamente.
   - ¿Alpha = 0? Es transparente.

---

## Herramienta 4: Memory Graph Debugger

Detecta memory leaks (objetos que no se liberan) y ciclos de retención.

### Cuándo usarlo

- La app usa cada vez más memoria sin soltarla
- sospechas de ciclo de retención (closures con `self` sin `[weak self]`)
- Crash por Out Of Memory

### Cómo usarlo

1. Ejecuta la app
2. Ve a Debug → Debug Memory Graph (o botón de cámara en la barra de debug)
3. Xcode muestra todos los objetos en memoria y quién los retiene

### Detectar memory leaks

Busca objetos que deberían haberse liberado pero siguen en memoria:

```swift
// Memory leak típico
class LoginViewModel {
    var onLoginSucceeded: (Session) -> Void  // Retiene el closure
    
    init(onLoginSucceeded: @escaping (Session) -> Void) {
        self.onLoginSucceeded = onLoginSucceeded
        // Si el closure captura self del coordinador,
        // y el ViewModel retiene el closure,
        // hay un ciclo: Coordinator ↔ ViewModel
    }
}
```

**Solución:** `[weak self]` en el closure.

---

## Herramienta 5: Instruments

Para problemas de rendimiento: CPU, memoria, red, batería.

### Perfiles útiles

| Instrument | Para qué sirve |
|------------|----------------|
| **Time Profiler** | Ver qué funciones consumen más CPU |
| **Allocations** | Ver cuánta memoria usa cada clase |
| **Leaks** | Detectar memory leaks automáticamente |
| **Network** | Ver todas las peticiones HTTP |
| **Energy Log** | Ver consumo de batería |

### Ejemplo: Time Profiler

1. Product → Profile (Cmd + I)
2. Selecciona Time Profiler
3. La app se ejecuta en el dispositivo/simulador
4. Realiza la acción lenta
5. Detén la grabación
6. Analiza: ¿Qué función toma más tiempo?

### Interpretando resultados

```
┌────────────────────────────────────────┐
│ 95% - LoginViewModel.submit()           │
│   └─ 90% - LoginUseCase.execute()       │
│        └─ 85% - URLSession.data()       │
│             └─ 80% - _CFReadStreamRead │
└────────────────────────────────────────┘
```

**Conclusión:** El 80% del tiempo está esperando red. No es un problema de código, es latencia de red.

---

## Patrones de debugging por tipo de bug

### "No se ejecuta mi código"

1. ¿Está el archivo en el target? (Inspector → Target Membership)
2. ¿Se llamó a la función? (Breakpoint al inicio)
3. ¿La condición if es true? (Breakpoint + inspeccionar)

### "Crash con fatalError / force unwrap"

1. Mira el stack trace en la consola
2. Identifica la línea exacta del crash
3. Pon breakpoint una línea antes
4. Inspecciona la variable que se force-unwrapped

### "Test falla intermitentemente" (Flaky test)

1. Ejecuta el test 10 veces: Product → Test → Run tests repeatedly
2. Si falla a veces, es problema de concurrencia/timing
3. Añade `await Task.yield()` o verifica sincronización

### "La UI no se actualiza"

1. ¿Estás en @MainActor? Verifica que el código que toca UI esté marcado.
2. ¿Es @Observable el ViewModel? Verifica el property wrapper.
3. ¿SwiftUI detectó el cambio? Usa `.onChange` para debug.

---

## Debugging de concurrencia

Los bugs de concurrencia son los más difíciles porque no son deterministas.

### El clásico "data race"

```swift
// ❌ Mal: Acceso concurrente sin sincronización
var counter = 0

Task {
    for _ in 0..<1000 {
        counter += 1  // Race condition!
    }
}

Task {
    for _ in 0..<1000 {
        counter += 1  // Race condition!
    }
}
// Resultado: counter es probablemente < 2000
```

**Debug:**
1. Ejecuta con Thread Sanitizer: Edit Scheme → Run → Diagnostics → Thread Sanitizer
2. Xcode detectará el data race y te mostrará exactamente qué líneas compiten

### Deadlock

```swift
// ❌ Mal: Dos actors esperándose mutuamente
actor A {
    func callB(_ b: B) async {
        await b.doSomething()  // Espera a B
    }
}

actor B {
    func callA(_ a: A) async {
        await a.callB(self)  // Espera a A → Deadlock!
    }
}
```

**Debug:** La app se congela. Pause execution y mira el stack trace: verás `await` en ambos hilos.

---

## Debugging de SwiftUI Previews

Cuando el preview no compila o crashea:

### Preview crashea

```swift
#Preview("Login") {
    // Si esto crashea, el preview se queda gris
    LoginView(viewModel: makeViewModel())
}

// Solución: Añade manejo de errores
#Preview("Login") {
    do {
        return try LoginView(viewModel: makeViewModel())
    } catch {
        return Text("Preview error: \(error)")
    }
}
```

### Preview no actualiza

1. Verifica que el canvas esté activo (Cmd + Option + Enter)
2. Resume automático puede fallar → pulsa el botón Resume manualmente
3. Si hay error de compilación, el preview no se actualiza hasta que arregles el error

---

## Checklist de debugging efectivo

- [ ] Puedo reproducir el bug consistentemente.
- [ ] He añadido breakpoints para entender el flujo.
- [ ] Inspeccioné variables en el momento del bug.
- [ ] Usé `po` en consola para entender el estado.
- [ ] Si es UI, usé Debug View Hierarchy.
- [ ] Si es memoria, usé Memory Graph Debugger.
- [ ] Si es rendimiento, usé Instruments.
- [ ] Arreglé UNA cosa, verifiqué si funcionó.
- [ ] Escribí un test que capture este bug (regression test).

---

## Ejercicio práctico

**Bug simulado:** El login siempre falla con "Email inválido" aunque el email es correcto.

**Tarea:** Usa breakpoints y la consola para encontrar el bug.

**Pista:** El problema está en `Email.swift`. El regex es correcto, pero...

**Solución:** (no la abras hasta intentarlo)
<details>
<summary>Spoiler: Ver solución</summary>

El bug está en que `Email` valida con `value.lowercased()` pero almacena el original. Si el usuario escribe "User@Test.COM", la validación pasa (porque lowercased es "user@test.com"), pero el valor almacenado es "User@Test.COM". Luego, cuando se compara, hay inconsistencia.

Fix: Normalizar el email en el init.
</details>

---

**Recuerda:** El debugging es una habilidad que mejora con la práctica. Cada bug que arreglas te hace mejor para el siguiente.

---

**Siguiente lección:** [Testing Concurrente](04-testing-concurrente.md)
