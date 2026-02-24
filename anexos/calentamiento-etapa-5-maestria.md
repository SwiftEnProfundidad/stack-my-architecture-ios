# Calentamiento: Etapa 5 - Maestría

<!-- sma:meta:v1 -->
meta_leccion:
  tiempo_lectura: "12 min"
  tiempo_practica: "18 min"
  dificultad: 3
  prerequisitos:
    - "04-arquitecto/entregables-etapa-4.md"
  si_te_atascas: "#identificando-race-conditions"
<!-- /sma:meta:v1 -->

> 🎓 **Antes de empezar la Etapa 5**, dedica 30 minutos a este calentamiento. Te preparará para los conceptos avanzados de concurrencia, actores y diagnóstico.

---

## ¿Por qué un calentamiento?

La Etapa 5 es el nivel más alto del curso. Aquí no aprenderás "más cosas", aprenderás a hacer **las mismas cosas de forma correcta bajo presión**:

- Cuando hay millones de usuarios concurrentes
- Cuando un bug solo aparece en producción
- Cuando necesitas explicar tus decisiones en una entrevista técnica

Es el paso de "saber hacerlo" a "saber hacerlo bien y explicar por qué".

---

## Analogía: El chef en hora pico

Imagina un restaurante con un solo chef (single-threaded). Cuando hay pocos clientes, todo bien. Pero en hora pico:

- **Sin concurrencia:** El chef cocina un plato, lo sirve, vuelve a cocinar. Los clientes esperan horas.
- **Con concurrencia mal hecha:** El chef intenta cocinar 5 platos a la vez, se confunde, quema la comida.
- **Con concurrencia bien hecha:** Hay varios chefs (actores), cada uno con su especialidad, coordinados por un jefe de cocina.

En software, los "chefs" son actores y el "jefe de cocina" es tu arquitectura de concurrencia.

---

## Conceptos clave de la Etapa 5 (preview)

### 1. Actors y Aislamiento

**Analogía:** Un cajero de banco.

- El cajero (actor) atiende a una persona a la vez
- Si hay 10 personas, no se atienden a sí mismas; esperan su turno
- El cajero tiene su propio "estado" (caja, dinero) que nadie más toca directamente

**En código:** Los actores en Swift garantizan que solo se ejecute una operación a la vez, eliminando data races.

### 2. Sendable

**Analogía:** Un sobre certificado.

- Puedes enviarlo por correo (pasar entre hilos/actores)
- El destinatario recibe una copia, no el original
- Si contiene algo valioso, el original no se pierde

**En código:** Los tipos `Sendable` pueden cruzar límites de concurrencia de forma segura.

### 3. Structured Concurrency

**Analogía:** Una misión militar.

- Hay una misión principal (task padre)
- Puede tener sub-misiones (tasks hijas)
- Si la principal se cancela, todas las hijas se cancelan
- Todas deben completarse (o fallar) antes de que la principal termine

**En código:** `async let` y `TaskGroup` garantizan que no pierdas tareas por el camino.

---

## Identificando race conditions {#identificando-race-conditions}

**Contexto:** Estás revisando código de un compañero y sospechas que tiene un data race.

**Mira este código y encuentra el problema:**

```swift
class Contador {
    var valor = 0
    
    func incrementar() {
        valor += 1  // ⚠️ ¿Problema?
    }
}

let contador = Contador()

// Dos tareas concurrentes
Task {
    for _ in 0..<1000 {
        contador.incrementar()
    }
}

Task {
    for _ in 0..<1000 {
        contador.incrementar()
    }
}

// ¿Cuál es el valor final esperado? ¿2000?
// En realidad, es impredecible (data race)
```text

**Tarea:** Explica por qué `valor` podría no ser 2000 al final, y propón una solución usando `actor`.

<details>
<summary>💡 Pista 1: Qué es un data race</summary>

Un data race ocurre cuando dos hilos acceden a la misma memoria, al menos uno escribe, y no hay sincronización.

</details>

<details>
<summary>💡 Pista 2: Por qué no es 2000</summary>

`valor += 1` no es atómico. Es: leer (100), sumar (101), escribir (101). Si dos hilos leen 100 al mismo tiempo, ambos escriben 101, perdiendo un incremento.

</details>

<details>
<summary>✅ Solución con actor</summary>

```swift
actor ContadorSeguro {
    var valor = 0
    
    func incrementar() {
        valor += 1  // ✅ El actor serializa el acceso
    }
    
    func getValor() -> Int {
        return valor
    }
}

let contador = ContadorSeguro()

Task {
    for _ in 0..<1000 {
        await contador.incrementar()  // ✅ await porque es actor-isolated
    }
}

Task {
    for _ in 0..<1000 {
        await contador.incrementar()
    }
}

// Ahora valor SIEMPRE será 2000
```swift

**Por qué funciona:** El actor garantiza que solo una operación se ejecute a la vez. El `await` permite que el sistema coordine el acceso.

</details>

---

## Mapa de la Etapa 5

```mermaid
flowchart LR
    A[Isolation Domains] --> B[Actors]
    B --> C[Structured Concurrency]
    C --> D[Testing Concurrente]
    D --> E[SwiftUI Moderno]
    E --> F[Performance]
    F --> G[Memory Leaks]
    G --> H[Migración Swift 6]
    
    style A fill:#f472b6
    style H fill:#a78bfa
```

**Lo que dominarás:**

1. Identificar y eliminar data races en código existente
2. Diseñar con actores desde el inicio
3. Escribir tests que verifiquen seguridad de concurrencia
4. Diagnosticar memory leaks y performance issues
5. Migrar código legacy a Swift 6 strict concurrency

---

## Verificación de preparación

Antes de empezar la Etapa 5, asegúrate de:

- [ ] Haber completado todos los entregables de la Etapa 4
- [ ] Entender qué es un hilo (thread) y por qué la concurrencia es difícil
- [ ] Haber usado `async/await` en múltiples lugares
- [ ] Saber qué es un closure y cómo captura variables
- [ ] Estar cómodo leyendo stack traces de errores

Si falta algo, **vuelve a la Etapa 4**. La Etapa 5 asume que dominas esos conceptos.

---

## Frase para recordar

> "La concurrencia no es difícil porque el código sea complejo. Es difícil porque los errores son no-determinísticos: a veces funciona, a veces falla, y nunca sabes por qué."

Los actores y Swift 6 te dan herramientas para que los errores sean imposibles en tiempo de compilación, no misterios en producción.

---

## Continuación

¿Listo para el nivel más alto? Adelante:

- **Siguiente:** [Introducción a la Etapa 5: Maestría](../05-maestria/00-introduccion.md)

---

**Anterior:** [Checklist de entrega para entrevista (1 página) ←](../05-maestria/10-rubrica-final/03-checklist-entrega-para-entrevista.md) · **Siguiente:** [Quizzes de Autoevaluación →](quizzes-autoevaluacion.md)
