# Quizzes de Autoevaluación

> Testea tu comprensión del curso. No son de memorización; son de **entendimiento**.

---

## Cómo usar estos quizzes

1. **Intenta responder sin mirar el material** del curso
2. **No te preocupes por la puntuación**; preocúpate por entender por qué fallaste
3. **Lee las explicaciones** incluso si acertaste (puede haber matices)
4. **Si fallas más de 3 en un bloque**, revisa las lecciones correspondientes antes de continuar

---

## Bloque 1: Fundamentos (Etapa 1)

### Pregunta 1
**¿Por qué usamos Value Objects (como `Email` o `Password`) en lugar de `String` crudos?**

- [ ] a) Porque ocupan menos memoria
- [ ] b) Para encapsular validación e inmutabilidad, evitando estados inválidos
- [ ] c) Porque Swift no permite strings en structs
- [ ] d) Para hacer el código más largo y complejo

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta correcta: b**

Los Value Objects encapsulan:
- **Validación**: Un `Email` no puede existir si no es válido
- **Inmutabilidad**: Una vez creado, no cambia (thread-safe)
- **Semántica**: `Email` comunica más que `String`

La opción a es incorrecta (los VO pueden ocupar más memoria por el overhead). La c es falsa. La d es sarcasmo incorrecto.

</details>

### Pregunta 2
**En Clean Architecture, ¿qué capa NO debe conocer de las demás?**

- [ ] a) Infrastructure
- [ ] b) Application
- [ ] c) Domain
- [ ] d) Interface (UI)

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta correcta: c**

**Domain** es el centro y no debe conocer ninguna otra capa. Las dependencias apuntan hacia Domain:

```text
Interface -> Application -> Domain <- Infrastructure
```

Domain define interfaces (protocolos) que otras capas implementan.

</details>

### Pregunta 3
**¿Cuál es el ciclo TDD correcto?**

- [ ] a) Code → Test → Refactor
- [ ] b) Test → Code → Refactor
- [ ] c) Refactor → Test → Code
- [ ] d) Test → Refactor → Code

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta correcta: b**

**Red → Green → Refactor:**
1. Escribe un test que falle (Red)
2. Escribe el código mínimo para que pase (Green)
3. Refactoriza manteniendo los tests verdes (Refactor)

</details>

### Pregunta 4 (Verdadero/Falso)
**"Un Use Case puede depender de múltiples Repositories si la operación de negocio lo requiere."**

- [ ] Verdadero
- [ ] Falso

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta: Verdadero**

Un Use Case representa una operación de negocio. Si esa operación necesita datos de múltiples fuentes (ej: `PlaceOrderUseCase` necesita `ProductRepository` y `PaymentRepository`), es válido depender de ambos.

Lo que NO debe hacer es depender de implementaciones concretas; debe depender de los protocolos (interfaces).

</details>

### Pregunta 5
**Explica con tus palabras:** ¿Por qué es importante que los errores sean tipados (enum) en lugar de usar `Error` genérico?

<details>
<summary>Ver respuesta esperada (guía)</summary>

Una buena respuesta incluye:

- **Exhaustividad**: Con `switch` el compilador fuerza a manejar todos los casos
- **Semántica**: `LoginError.invalidCredentials` comunica más que `Error(code: 401)`
- **Testabilidad**: Los tests pueden verificar casos específicos
- **UX**: Diferentes errores pueden mostrar diferentes mensajes al usuario

Ejemplo de respuesta:
> "Los errores tipados permiten que el compilador verifique que manejamos todos los casos. Además, hacen el código más legible: sabemos exactamente qué puede fallar leyendo el tipo, sin adivinar códigos numéricos."

</details>

---

## Bloque 2: Integración (Etapa 2)

### Pregunta 6
**¿Cuál es la ventaja principal de la navegación event-driven sobre `NavigationLink` directo?**

- [ ] a) Es más rápida en runtime
- [ ] b) Desacopla las features; la View no conoce el destino
- [ ] c) Usa menos memoria
- [ ] d) Es nativa de SwiftUI

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta correcta: b**

El event-driven desacopla porque:
- La View emite "loginSucceeded", no "ir a Catalog"
- El coordinator decide el destino
- Se pueden interceptar eventos (deep links, analytics)

No es más rápida (a), ni usa menos memoria (c). NavigationLink es nativo de SwiftUI, no event-driven (d).

</details>

### Pregunta 7
**¿Dónde se crean las instancias concretas de Repository y UseCase?**

- [ ] a) En las Views
- [ ] b) En el Composition Root
- [ ] c) En los tests
- [ ] d) En el AppDelegate

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta correcta: b**

El **Composition Root** es el único lugar que conoce implementaciones concretas. Allí se ensambla el grafo de dependencias.

Las Views reciben inyectados los ViewModels (no crean). Los tests crean stubs, no implementaciones reales. AppDelegate es legacy.

</details>

### Pregunta 8 (Verdadero/Falso)
**"Los contratos entre features deben ser lo más grandes posibles para evitar cambios futuros."**

- [ ] Verdadero
- [ ] Falso

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta: Falso**

Los contratos deben ser **mínimos y estables**. Compartir más de lo necesario:
- Aumenta el acoplamiento
- Dificulta la evolución independiente
- Crea "shared kernel" que se convierte en dumping ground

Principio: **Compartir solo lo que es esencial y estable**.

</details>

### Pregunta 9
**¿Cuándo usarías un test de integración en lugar de un test unitario?**

- [ ] a) Cuando quieres que sea más rápido
- [ ] b) Cuando quieres verificar que múltiples componentes funcionan juntos
- [ ] c) Cuando no sabes cómo testear en aislamiento
- [ ] d) Nunca; los tests unitarios son siempre mejores

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta correcta: b**

Los tests de integración verifican **colaboración** entre componentes (ej: Login → Event → Coordinator → Catalog).

No son más rápidos (a). No son excusa por no saber testear (c). Son necesarios además de unitarios (d).

</details>

### Pregunta 10
**Explica:** ¿Por qué es peligroso que dos features se importen mutuamente?

<details>
<summary>Ver respuesta esperada (guía)</summary>

Una buena respuesta incluye:

- **Dependencia circular**: A depende de B, B depende de A
- **Imposibilidad de compilar separadamente**: No puedes trabajar en A sin B, ni en B sin A
- **Dificultad para testear**: No puedes testear A sin montar B
- **Fragilidad**: Cambios en cualquiera pueden romper la otra

Solución: Extraer contratos comunes a un tercer módulo, o usar inversión de dependencias.

Ejemplo de respuesta:
> "Si A importa B y B importa A, tenemos un ciclo. Esto significa que no podemos compilar A sin B ni B sin A. Si queremos cambiar algo en A, podemos romper B sin darnos cuenta. La solución es extraer lo común a un protocolo en un módulo compartido."

</details>

---

## Bloque 3: Evolución (Etapa 3)

### Pregunta 11
**¿Qué estrategia de cache es mejor para datos que cambian frecuentemente?**

- [ ] a) Cache-first (siempre mostrar cache)
- [ ] b) Network-first con fallback a cache
- [ ] c) No usar cache
- [ ] d) Cache infinito sin TTL

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta correcta: b**

**Network-first** intenta obtener datos frescos, y solo si falla usa cache. Esto garantiza frescura sin sacrificar disponibilidad.

Cache-first (a) mostraría datos obsoletos. No cache (c) sería lento y frágil. Cache sin TTL (d) serviría datos potencialmente muy viejos.

</details>

### Pregunta 12
**¿Qué es el TTL (Time To Live) en una estrategia de cache?**

- [ ] a) El tiempo que tarda en cargar la red
- [ ] b) El tiempo máximo que un dato en cache se considera válido
- [ ] c) El tiempo de vida de la app
- [ ] d) Un protocolo de red

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta correcta: b**

**TTL** define cuánto tiempo un dato cacheado es considerado "fresco". Pasado ese tiempo, se invalida o se refresca.

Ejemplo: TTL de 1 hora para lista de productos. Después de 1 hora, el cache se ignora o se refresca.

</details>

### Pregunta 13 (Verdadero/Falso)
**"La observabilidad (logs/métricas) solo es útil en producción, no durante el desarrollo."**

- [ ] Verdadero
- [ ] Falso

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta: Falso**

La observabilidad es útil en **todas las etapas**:
- **Desarrollo**: Entender flujos complejos
- **Testing**: Verificar que se ejecutan los caminos esperados
- **Staging**: Detectar problemas antes de producción
- **Producción**: Diagnosticar incidentes

</details>

### Pregunta 14
**¿Cuándo deberías invalidar el cache manualmente?**

- [ ] a) Nunca; el TTL lo maneja todo
- [ ] b) Cuando el usuario hace pull-to-refresh
- [ ] c) Después de una operación de escritura exitosa
- [ ] d) b y c son correctas

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta correcta: d**

Invalidar manualmente es necesario cuando:
- **Usuario fuerza refresh** (pull-to-refresh): Quiere datos frescos ahora
- **Escritura exitosa**: Si editas un producto, el cache antiguo ya no es válido

El TTL solo maneja el tiempo, no eventos de negocio.

</details>

### Pregunta 15
**Explica:** ¿Por qué es peligroso usar SwiftData (o Core Data) directamente en Domain?

<details>
<summary>Ver respuesta esperada (guía)</summary>

Una buena respuesta incluye:

- **Acoplamiento**: Domain dependería de un framework específico
- **Testabilidad**: Los tests de Domain necesitarían montar SwiftData
- **Flexibilidad**: No podrías cambiar de persistencia sin tocar Domain
- **Plataforma**: SwiftData solo funciona en Apple; Domain debería ser portable

La solución es usar el patrón Repository: Domain define un protocolo, Infrastructure implementa con SwiftData.

Ejemplo de respuesta:
> "Si Domain usa SwiftData directamente, estamos acoplando nuestra lógica de negocio a un framework específico de Apple. Los tests se vuelven lentos porque necesitan montar SwiftData. Además, si mañana queremos usar Realm o cambiar a Android, tenemos que reescribir Domain. La solución es que Domain defina un protocolo Repository y la capa de infraestructura lo implemente con SwiftData."

</details>

---

## Bloque 4: Arquitecto (Etapa 4)

### Pregunta 16
**¿Qué es un Bounded Context en DDD?**

- [ ] a) Una capa de la arquitectura (UI, Domain, Data)
- [ ] b) Un área delimitada del dominio donde un modelo específico aplica
- [ ] c) Un tipo de base de datos
- [ ] d) Un patrón de diseño de UI

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta correcta: b**

Un **Bounded Context** es un límite semántico donde un modelo de dominio es consistente. Se define por el **lenguaje ubícuo** (términos del negocio).

Ejemplo: "Producto" en Catálogo vs "Producto" en Inventario pueden tener atributos diferentes; son contextos separados.

</details>

### Pregunta 17
**¿Cuándo deberías modularizar tu app en múltiples módulos SPM?**

- [ ] a) Siempre, desde el día 1
- [ ] b) Nunca; un solo módulo es más simple
- [ ] c) Cuando el dolor de acoplamiento supera el costo de modularizar
- [ ] d) Solo si tienes más de 100 developers

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta correcta: c**

La modularización tiene costos (overhead de gestión, builds más complejos). Se justifica cuando:
- Los tiempos de build son lentos
- Hay acoplamiento no deseado entre equipos
- Se necesita reusar código en otras apps

Ni siempre (a) ni nunca (b). No depende solo del tamaño del equipo (d).

</details>

### Pregunta 18 (Verdadero/Falso)
**"Un quality gate es útil solo si es automático y falla el build."**

- [ ] Verdadero
- [ ] Falso

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta: Falso**

Los quality gates pueden ser:
- **Automáticos**: Scripts que fallan el build
- **Manuales**: Checklists que los developers siguen
- **Híbridos**: Scripts que generan reportes para revisión humana

En etapas tempranas, gates conceptuales (documentados) son válidos y útiles.

</details>

### Pregunta 19
**¿Qué problema resuelve el Anti-Corruption Layer (ACL)?**

- [ ] a) Proteger contra malware
- [ ] b) Aislar nuestro dominio de modelos externos (legacy, terceros)
- [ ] c) Encriptar datos sensibles
- [ ] d) Prevenir inyección SQL

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta correcta: b**

El **ACL** traduce entre nuestro modelo de dominio y modelos externos. Nos protege de:
- APIs de terceros con nombres/estructuras diferentes
- Legacy systems que no podemos cambiar
- Cambios en dependencias externas

El ACL "corrompe" los modelos externos para que no contaminen nuestro dominio.

</details>

### Pregunta 20
**Explica:** ¿Por qué es peligroso tener un "Shared Kernel" muy grande entre equipos?

<details>
<summary>Ver respuesta esperada (guía)</summary>

Una buena respuesta incluye:

- **Acoplamiento**: Todos los equipos dependen del Shared Kernel
- **Coordinación**: Cualquier cambio requiere alinear a todos los equipos
- **Velocidad**: Los equipos se frenan mutuamente
- **Responsabilidad difusa**: Nadie es dueño del Shared Kernel

El Shared Kernel debe ser mínimo y estable. Si crece, considera dividirlo o mover lógica a contextos específicos.

Ejemplo de respuesta:
> "Un Shared Kernel grande crea acoplamiento entre equipos. Si 5 equipos dependen de él, cualquier cambio necesita coordinación. Esto frena la velocidad de desarrollo. Además, tiende a convertirse en 'basurero' donde todo el mundo pone código que no sabe dónde poner. Debe ser mínimo: solo lo que es verdaderamente compartido y estable."

</details>

---

## Bloque 5: Maestría (Etapa 5)

### Pregunta 21
**¿Qué garantiza un actor en Swift?**

- [ ] a) Que el código sea más rápido
- [ ] b) Que solo se ejecute una operación a la vez (serialización)
- [ ] c) Que no haya memory leaks
- [ ] d) Que use menos memoria

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta correcta: b**

Los **actors** garantizan **aislamiento de estado**: solo una operación puede acceder al estado mutable del actor a la vez. Esto elimina data races.

No garantizan velocidad (a), ni ausencia de leaks (c), ni menos memoria (d).

</details>

### Pregunta 22
**¿Qué es un data race?**

- [ ] a) Una carrera entre dos developers
- [ ] b) Cuando dos hilos acceden a la misma memoria, al menos uno escribe, sin sincronización
- [ ] c) Un tipo de base de datos
- [ ] d) Un error de compilación

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta correcta: b**

**Data race** = múltiples hilos + misma memoria + al menos una escritura + sin sincronización.

Resultado: comportamiento no determinístico, crashes difíciles de reproducir.

</details>

### Pregunta 23 (Verdadero/Falso)
**"@MainActor garantiza que el código se ejecute en el hilo principal, pero no garantiza que sea thread-safe."**

- [ ] Verdadero
- [ ] Falso

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta: Falso**

`@MainActor` **sí garantiza** thread-safety para el estado que protege, porque serializa el acceso al hilo principal.

Lo que NO garantiza es que el código sea **performante** (puede bloquear el UI si haces operaciones pesadas en MainActor).

</details>

### Pregunta 24
**¿Cuál es la causa más común de memory leaks en Swift?**

- [ ] a) No llamar `deinit`
- [ ] b) Retain cycles en closures que capturan `self` fuertemente
- [ ] c) Usar demasiadas variables
- [ ] d) No usar `weak` en todas las propiedades

<details>
<summary>Ver respuesta y explicación</summary>

**Respuesta correcta: b**

Los **retain cycles** ocurren cuando:
- Objeto A retiene B
- B retiene A (o B tiene un closure que captura A)

Solución: usar `[weak self]` en closures que no necesitan retener `self`.

</details>

### Pregunta 25
**Explica:** ¿Por qué Swift 6 strict concurrency es "strict" y qué problemas detecta en tiempo de compilación?

<details>
<summary>Ver respuesta esperada (guía)</summary>

Una buena respuesta incluye:

- **Strict** = el compilador fuerza seguridad de concurrencia
- **Problemas detectados**:
  - Data races (acceso concurrente no seguro)
  - Captura de valores no-Sendable en closures @Sendable
  - Acceso a estado mutable desde múltiples hilos
  - Falta de aislamiento de actores

**Beneficio:** Los errores de concurrencia se detectan en compile-time, no en producción.

Ejemplo de respuesta:
> "Swift 6 strict concurrency hace que el compilador verifique que no hay data races. Si intentas pasar un valor mutable entre hilos sin sincronización, el compilador da error. Esto es 'strict' porque no te deja 'hacer trampas'. Los problemas que detecta son data races, captura insegura de variables en closures, y acceso no autorizado a estado de actores. El beneficio es que estos errores, que antes aparecían como bugs intermitentes en producción, ahora se detectan al compilar."

</details>

---

## Puntuación y siguientes pasos

### Cómo evaluarte

- **22-25 aciertos:** 🎉 Excelente. Dominas los conceptos clave.
- **18-21 aciertos:** ✅ Bien. Hay algunos huecos; revisa las preguntas falladas.
- **15-17 aciertos:** ⚠️ Regular. Dedica tiempo a repasar las lecciones correspondientes.
- **Menos de 15:** 🚨 Necesitas repasar seriamente antes de continuar.

### Qué hacer según tu bloque

| Bloque | Si fallaste más de 1 |
|--------|---------------------|
| Fundamentos | Revisa [Value Objects](../01-fundamentos/05-feature-login/01-domain.md) y [TDD](../01-fundamentos/02-metodologia-tdd-practica.md) |
| Integración | Revisa [Navegación](../02-integración/02-navegación-eventos.md) y [Composition Root](../02-integración/06-composition-root.md) |
| Evolución | Revisa [Cache](../03-evolucion/01-caching-offline.md) y [Observabilidad](../03-evolucion/03-observabilidad.md) |
| Arquitecto | Revisa [Bounded Contexts](../04-arquitecto/01-bounded-contexts.md) y [Quality Gates](../04-arquitecto/06-quality-gates.md) |
| Maestría | Revisa [Actors](../05-maestria/02-actors-en-arquitectura.md) y [Memory Leaks](../05-maestria/08-memory-leaks-y-diagnostico.md) |

---

## Recordatorio final

> "Estos quizzes no miden cuánto memorizaste, sino cuánto entiendes. Un arquitecto no necesita saberlo todo de memoria; necesita saber dónde buscar y por qué."

¡Sigue adelante!

---

