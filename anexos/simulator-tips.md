# Tips del Simulador: Testing como Profesional

## Más allá de "Cmd + R"

El simulador de iOS no es solo un "dispositivo falso". Es una herramienta de testing poderosa que la mayoría de desarrolladores subutiliza. Esta guía te enseña a sacarle el máximo provecho.

---

## Configuración óptima del simulador

### Crear un simulador para desarrollo

1. **Window → Devices & Simulators** (Cmd + Shift + 2)
2. **Pestaña Simulators**
3. **+ (abajo izquierda)**
4. **Configuración recomendada:**
   - Device Type: iPhone 15 Pro (rendimiento balanceado)
   - iOS Version: Última estable
   - Name: "Dev iPhone 15 Pro" (para identificarlo fácil)

### Device vs Simulador: Cuándo usar cada uno

| Qué probar | Usar | Por qué |
|------------|------|---------|
| Layout UI básico | Simulador | Rápido, múltiples tamaños |
| Gestos (tap, swipe) | Simulador | Funciona igual |
| Cámara | Device real | Simulador tiene cámara "falsa" |
| GPS/Location | Simulador | Puedes simular rutas GPX |
| Notificaciones push | Device real | Requiere certificados reales |
| Rendimiento | Device real | Simulador usa CPU Mac (más rápida) |
| Batería/thermal | Device real | Simulador no simula estos |

**Regla:** 80% simulador, 20% device real. El simulador es más rápido para iterar.

---

## Features ocultas del simulador

### 1. Location/GPS (Cmd + Shift + L)

**Para probar tu app con diferentes ubicaciones:**

```
Features → Location
├── None           (Sin ubicación - prueba errores)
├── Apple          (Cupertino, CA - default)
├── Custom Location (Lat/Lon específicos)
├── City Bicycle Ride (Simula movimiento)
├── City Run       (Movimiento más rápido)
└── Freeway Drive  (Simula conducir)
```

**Ejercicio:** En E2 (Catalog), simula que estás en Tokyo:
```
Features → Location → Custom Location
Latitude: 35.6762
Longitude: 139.6503
```

### 2. Apariencia (Dark Mode, Dynamic Type)

**Cambiar apariencia:**
```
Features → Appearance
├── Light
├── Dark
└── Automatically (sigue el sistema macOS)
```

**Probar Dynamic Type (tamaños de fuente):**
```
Settings app (en simulador) → Display & Brightness → Text Size
→ Arrastra a "Accessibility Sizes" para probar XXXL
```

**Por qué importa:** Tu app debe verse bien en todas las configuraciones de accesibilidad.

### 3. Shake Gesture (Cmd + Ctrl + Z)

**Para probar features que requieren agitar el teléfono:**

```
Device → Shake
→ o atajo: Cmd + Ctrl + Z
```

**Usos comunes:**
- React Native: Abre debugger
- Apps de desarrollo: Mostrar menú debug
- Tu app: Podrías usarlo para "undo"

### 4. Capturas de pantalla y recordings

**Screenshot:**
```
Device → Screenshot (Cmd + S)
→ Se guarda en Desktop por defecto
```

**Screen Recording:**
```
Simulator app → File → Record Screen
├── Start Recording
└── Stop Recording (guarda como .mov)
```

**Para qué usarlo:**
- Documentar bugs con video
- Crear demos para el portfolio
- Verificar animaciones frame a frame

### 5. Touch ID / Face ID

**Aunque el simulador no tiene sensores biométricos, puedes simularlos:**

```
Features → Face ID / Touch ID
├── Enrolled (como si estuviera configurado)
├── Matching Face (autenticación exitosa)
└── Non-matching Face (autenticación fallida)
```

**Escenario de prueba:**
1. En tu app de Login, añade autenticación biométrica
2. Simula "Enrolled" + "Matching Face" → Debe loguear
3. Simula "Enrolled" + "Non-matching" → Debe mostrar error

### 6. Memory Pressure

**Simular dispositivo con poca RAM:**

```
Device → Simulate Memory Warning
```

**Por qué importa:** Tu app debe liberar recursos cuando el sistema está bajo presión. Si no lo hace, el sistema la matará.

### 7. Simular diferentes condiciones de red

```
Window → Devices & Simulators → Simulators → [Tu simulador]
→ Botón con icono de "settings" en el simulador seleccionado
→ Device Conditions
```

**Condiciones disponibles:**
- 100% Loss (sin red - prueba offline)
- 3G (lento - prueba timeouts)
- Edge (muy lento - prueba UX de carga)
- High Latency DNS (DNS lento)

**Ejercicio:** En E3 (Caching), prueba tu app con "100% Loss" → Debe mostrar datos cacheados.

---

## Multi-simulador: Testear múltiples dispositivos

### Ejecutar varios simuladores simultáneamente

```bash
# En Terminal, abrir simuladores adicionales
open -n /Applications/Xcode.app/Contents/Developer/Applications/Simulator.app
```

**Usos:**
- Verificar layout en iPhone SE (pequeño) y iPhone 15 Pro Max (grande) al mismo tiempo
- Probar iPad + iPhone simultáneamente
- Verificar que Universal Links funcionan cross-device

### Atajos de ventana del simulador

| Atajo | Acción |
|-------|--------|
| `Cmd + 1` | Escalar al 100% |
| `Cmd + 2` | Escalar al 75% |
| `Cmd + 3` | Escalar al 50% |
| `Cmd + →/←` | Rotar derecha/izquierda |
| `Cmd + Shift + H` | Ir a Home screen |
| `Cmd + L` | Lock screen (bloquear) |
| `Cmd + Shift + M` | Enviar notificación test |
| `Cmd + K` | Toggle teclado virtual |

---

## Testing específico por etapa del curso

### E1: Feature Login

**Qué probar en simulador:**
- [ ] Keyboard aparece al tocar text field (`Cmd + K` para toggle)
- [ ] Keyboard se oculta al pulsar Return o tocar fuera
- [ ] Layout en iPhone SE (pantalla pequeña, sin notch)
- [ ] Layout en iPhone 15 Pro Max (pantalla grande, Dynamic Island)
- [ ] Dark mode (`Features → Appearance → Dark`)
- [ ] Rotación landscape (login debería funcionar igual)

### E2: Login + Catalog

**Qué probar:**
- [ ] Navegación entre pantallas (`Cmd + Shift + H` para ir a home)
- [ ] List scrolling performance (debe ser smooth a 60fps)
- [ ] Pull to refresh (si implementaste `.refreshable`)
- [ ] Accessibility: VoiceOver (ver abajo)
- [ ] Dynamic Type: Texto XXL en listas

### E3: Offline/Caching

**Qué probar:**
- [ ] Modo avión (`Features → Network Condition → 100% Loss`)
- [ ] Cache persistence (cerrar app, abrir, verificar datos)
- [ ] Location-based features (si aplica)
- [ ] Memory warning (`Device → Simulate Memory Warning`)

### E4/E5: Arquitectura avanzada

**Qué probar:**
- [ ] Deep links (abrir URL en Safari simulador, verificar app se abre)
- [ ] Background fetch (simular background refresh)
- [ ] App lifecycle (background, foreground, terminate)
- [ ] Performance: Animaciones smooth con Instruments

---

## Accessibility Testing (Importante)

Muchos desarrolladores ignoran accesibilidad. Apple sí la revisa en App Store.

### Activar VoiceOver

```
Settings app → Accessibility → VoiceOver → ON
→ O atajo triple-click en side button (configurar primero)
```

**Navegación con VoiceOver activado:**
- Deslizar derecha: Siguiente elemento
- Deslizar izquierda: Anterior elemento
- Doble tap: Activar elemento seleccionado
- Tres dedos deslizar: Scroll

### Verificar que tu app es accesible

**Con VoiceOver activado:**
- [ ] ¿Cada elemento interactivo tiene label descriptivo?
- [ ] ¿Los labels son concisos? ("Enviar", no "Botón para enviar el formulario")
- [ ] ¿El orden de navegación tiene sentido lógico?
- [ ] ¿Los elementos decorativos están ocultos? (`accessibilityHidden`)

**Herramienta adicional:**
```
Xcode → Open Developer Tool → Accessibility Inspector
→ Te muestra el árbol de accesibilidad en tiempo real
```

---

## Debugging en el simulador

### Ver logs en tiempo real

```bash
# En Terminal, ver logs del simulador
xcrun simctl spawn booted log stream --level debug
```

### Instalar certificados/rutas para testing

```bash
# Simular ruta GPX (para apps de fitness/maps)
xcrun simctl location booted start --gpx /path/to/route.gpx

# Cambiar fotos del simulador
# Arrastrar imágenes a Photos app en simulador
```

### Resetear simulador (si se comporta raro)

```
Device → Erase All Content and Settings
→ O: xcrun simctl erase <device_id>
```

**Cuándo usarlo:**
- Datos corruptos en la app
- Simulador muy lento
- Cambios de sistema que no se aplican

---

## Checklist de testing en simulador

Antes de decir "está listo", verifica:

- [ ] Funciona en iPhone SE (pantalla pequeña, no notch)
- [ ] Funciona en iPhone 15 Pro Max (pantalla grande, Dynamic Island)
- [ ] Dark mode se ve bien (no hay textos blancos sobre blanco)
- [ ] Dynamic Type XXXL no rompe el layout
- [ ] Landscape (rotación) funciona correctamente
- [ ] Sin conexión a internet muestra UI apropiada
- [ ] Keyboard no oculta elementos importantes
- [ ] VoiceOver puede navegar toda la app
- [ ] Animaciones son smooth (60fps)
- [ ] App no crashea con memory warning

---

## Comandos xcrun útiles (Terminal)

```bash
# Listar simuladores disponibles
xcrun simctl list devices

# Instalar app en simulador específico
xcrun simctl install "iPhone 15 Pro" /path/to/YourApp.app

# Lanzar app específica
xcrun simctl launch "iPhone 15 Pro" com.yourcompany.yourapp

# Tomar screenshot
xcrun simctl io "iPhone 15 Pro" screenshot screenshot.png

# Grabar video
xcrun simctl io "iPhone 15 Pro" recordVideo video.mov
# Ctrl+C para parar

# Simular ubicación
xcrun simctl location "iPhone 15 Pro" set 37.7749,-122.4194
```

---

> **Consejo final:** Dedica 10% de tu tiempo de desarrollo a probar en el simulador con configuraciones "edge case" (Dark mode, Dynamic Type XL, landscape, sin red). Ese 10% evitará el 90% de bugs reportados por usuarios.

---

**Anexo relacionado:** [Xcode Cheat Sheet](xcode-cheat-sheet.md)
