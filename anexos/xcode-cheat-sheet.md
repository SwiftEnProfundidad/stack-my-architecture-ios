# Xcode Cheat Sheet: Atajos Esenciales para Productividad

## Los 20 atajos que debes memorizar

> **Consejo:** No intentes aprender todos de golpe. Elige 5 por semana hasta que sean automáticos.

---

## Navegación en código (esenciales)

| Atajo | Acción | Cuándo usarlo |
|-------|--------|---------------|
| `Cmd + Shift + O` | **Abrir rápido** (Open Quickly) | Ir a cualquier archivo/símbolo. El atajo más importante. |
| `Cmd + Click` | Ir a definición | Navegar a la declaración de una función/clase/variable. |
| `Cmd + Ctrl + ↑/↓` | Ir a interfaz/implementación | Cambiar entre `.swift` (implementación) y protocolo. |
| `Cmd + L` | Ir a línea | Saltar a una línea específica (útil para errores de compilación). |
| `Cmd + Shift + J` | Revelar en navegador | Mostrar el archivo actual en el árbol de proyecto. |

---

## Edición de código

| Atajo | Acción | Cuándo usarlo |
|-------|--------|---------------|
| `Cmd + /` | Comentar/descomentar línea | Rápido para desactivar código temporalmente. |
| `Cmd + D` | Duplicar línea | Útil para copiar patrones similares. |
| `Ctrl + Cmd + E` | Editar todas las ocurrencias | Renombrar variable en scope local. |
| `Cmd + Ctrl + M` | Seleccionar bloque de código | Selecciona el bloque entre llaves/actuales. |
| `Cmd + Shift + L` | Insertar snippet | Plantillas de código (funciones, if, for, etc.). |
| `Cmd + ]` / `Cmd + [` | Indentar / Desindentar | Alinear código rápidamente. |
| `Cmd + Shift + M` | Mostrar issues/problems | Ver lista de errores y warnings. |

---

## Build y Run

| Atajo | Acción | Cuándo usarlo |
|-------|--------|---------------|
| `Cmd + B` | **Build** | Compilar sin ejecutar (verifica errores rápido). |
| `Cmd + R` | **Run** | Compilar y ejecutar en simulador/dispositivo. |
| `Cmd + U` | **Test** | Ejecutar todos los tests. |
| `Cmd + .` | Stop | Detener la app en ejecución. |
| `Cmd + Shift + K` | Clean build folder | Limpiar cuando hay errores extraños. |
| `Cmd + Shift + 0` | Seleccionar simulador | Cambiar entre dispositivos de prueba. |

---

## Debug

| Atajo | Acción | Cuándo usarlo |
|-------|--------|---------------|
| `Cmd + \` | Toggle breakpoint | Añadir/quitar punto de interrupción. |
| `Cmd + Y` | Activar/desactivar breakpoints | Habilitar/deshabilitar todos los breakpoints. |
| `F6` | Step Over | Ejecutar línea actual (no entra en funciones). |
| `F7` | Step Into | Entrar en la función de la línea actual. |
| `F8` | Step Out | Salir de la función actual. |
| `Cmd + Shift + C` | Mostrar/ocultar consola | Ver logs y output de debug. |
| `Cmd + Shift + Y` | Mostrar/ocultar debug area | Panel inferior con variables y consola. |

---

## Refactorización

| Atajo | Acción | Cuándo usarlo |
|-------|--------|---------------|
| `Cmd + Shift + A` | Acciones de refactor | Menú contextual con opciones de refactor. |
| `Cmd + Ctrl + E` | Rename en scope | Renombrar variable en toda su función/clase. |
| `Cmd + Option + ↑` | Expand selection | Seleccionar scope creciente (variable → expresión → línea). |
| `Cmd + Option + ↓` | Shrink selection | Reducir selección. |

---

## Canvas y Previews (SwiftUI)

| Atajo | Acción | Cuándo usarlo |
|-------|--------|---------------|
| `Cmd + Option + Enter` | Mostrar/ocultar Canvas | Abrir/cerrar preview de SwiftUI. |
| `Cmd + Option + P` | Resume preview | Actualizar el canvas cuando hay cambios. |
| `Cmd + Option + Return` | Alternar editor/canvas | Cambiar entre código y preview. |

---

## Navegación de ventanas y paneles

| Atajo | Acción | Cuándo usarlo |
|-------|--------|---------------|
| `Cmd + 0` | Mostrar/ocultar Navigator | Panel izquierdo (proyecto, debug, breakpoints). |
| `Cmd + Option + 0` | Mostrar/ocultar Inspector | Panel derecho (propiedades, archivos). |
| `Cmd + Shift + Y` | Mostrar/ocultar Debug area | Panel inferior (consola, variables). |
| `Cmd + J` | Cambiar foco del editor | Mover cursor entre paneles de código. |
| `Cmd + Option + T` | Mostrar/ocultar toolbar | Barra superior con botones de navegación. |
| `Cmd + Enter` | Solo editor | Ocultar todos los paneles, solo código. |

---

## Source Control (Git)

| Atajo | Acción | Cuándo usarlo |
|-------|--------|---------------|
| `Cmd + Shift + C` | Commit | Abrir diálogo de commit (si hay cambios). |
| `Cmd + Ctrl + C` | Mostrar blame | Ver quién escribió cada línea. |
| `Cmd + Shift + G` | Comparar con versión anterior | Ver diff del archivo actual. |
| `Cmd + Option + C` | Crear stash | Guardar cambios temporalmente. |

---

## Trucos avanzados

### Selección múltiple (column mode)

```
Alt/Option + arrastrar selección
→ Selecciona en modo columna para editar múltiples líneas a la vez
```

**Ejemplo:** Quieres añadir `private` a 5 variables:
```swift
// Antes:
var name: String
var email: String
var age: Int

// Selecciona los 'var' con Alt+arrastrar
// Escribe 'private var'

// Después:
private var name: String
private var email: String
private var age: Int
```

### Búsqueda global vs local

- `Cmd + F` → Buscar en archivo actual
- `Cmd + Shift + F` → Buscar en TODO el proyecto (Find Navigator)
- `Cmd + Option + F` → Find and replace
- `Cmd + Shift + Option + F` → Find and replace en todo el proyecto

### Autocompletado inteligente

- `Esc` → Mostrar completions disponibles
- `Tab` → Aceptar completion y avanzar al siguiente placeholder
- `Ctrl + Space` → Forzar aparición de completions

---

## Configuración recomendada

### Text Editing

```
Preferences → Text Editing → Editing
✅ Enable type-over completions
✅ Suggest completions while typing
✅ Use escape key to show completions
✅ Automatically trim trailing whitespace
✅ Including whitespace-only lines
```

### Key Bindings personalizados (opcional)

Si quieres añadir atajos custom:
```
Preferences → Key Bindings
Busca el comando → Doble click en atajo → Pulsar combinación deseada
```

---

## Checklist de memorización

**Semana 1: Navegación básica**
- [ ] `Cmd + Shift + O` (Open Quickly) - El más importante
- [ ] `Cmd + Click` (Ir a definición)
- [ ] `Cmd + B` (Build)
- [ ] `Cmd + R` (Run)

**Semana 2: Edición eficiente**
- [ ] `Cmd + /` (Comentar)
- [ ] `Cmd + ]` / `Cmd + [` (Indentar)
- [ ] `Ctrl + Cmd + E` (Editar ocurrencias)
- [ ] `Cmd + D` (Duplicar línea)

**Semana 3: Debug**
- [ ] `Cmd + \` (Toggle breakpoint)
- [ ] `F6` (Step Over)
- [ ] `F7` (Step Into)
- [ ] `Cmd + Shift + C` (Consola)

**Semana 4: Avanzados**
- [ ] `Cmd + Shift + L` (Snippets)
- [ ] `Cmd + Option + ↑` (Expand selection)
- [ ] `Cmd + 0` / `Cmd + Option + 0` (Paneles)
- [ ] `Cmd + Shift + O` (practicar hasta que sea automático)

---

## Recursos adicionales

- **Cheat sheet oficial de Apple:** Help → Keyboard Shortcuts (en Xcode)
- **Custom shortcuts:** Puedes crear los tuyos en Preferences → Key Bindings
- **Practice:** Dedica 5 minutos al día a usar solo atajos, no mouse

---

> **Regla de oro:** Cada vez que usas el mouse/trackpad para algo que tiene atajo, estás perdiendo segundos. Acumulado durante el día, son horas. Acumulado durante un año, son semanas.

---

**Siguiente anexo:** [Tips del Simulador](simulator-tips.md)
