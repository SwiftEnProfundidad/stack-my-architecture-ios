# Consolidación: Etapa 4 - Arquitecto

<!-- sma:meta:v1 -->
meta_leccion:
  tiempo_lectura: "10 min"
  tiempo_practica: "25 min"
  dificultad: 3
  prerequisitos:
    - "04-arquitecto/entregables-etapa-4.md"
  si_te_atascas: "#ejercicio-de-arquitectura"
<!-- /sma:meta:v1 -->

> 🏛️ **Has completado la Etapa 4.** Esta etapa fue diferente: no construiste features, construiste **la plataforma** sobre la que se construyen features.

---

## ¿Qué deberías saber hacer sin ayuda?

Si te pusieran al frente de un equipo de 5 developers y te dijeran "gobierna esta arquitectura", deberías poder:

### ✅ Checklist de habilidades

- [ ] **Dibujar un mapa de bounded contexts** y explicar por qué los límites están donde están
- [ ] **Definir reglas de dependencia** y explicarlas al equipo
- [ ] **Configurar quality gates** (aunque sean conceptuales/scripted)
- [ ] **Decidir cuándo modularizar** y cuándo no
- [ ] **Justificar trade-offs** a stakeholders no-técnicos

---

## Autoevaluación rápida

### Pregunta 1: Bounded Contexts
> "¿Qué es un bounded context y por qué es mejor que dividir por capas técnicas (UI, Domain, Data)?"

<details>
<summary>Ver respuesta esperada</summary>

Un **bounded context** es un área delimitada del dominio donde un modelo específico aplica. Se define por el **lenguaje ubícuo** (términos que usan los expertos de negocio).

**Por qué es mejor que capas técnicas:**
- **Cohesión**: Todo lo relacionado con "Producto" está junto, no disperso en UI+Domain+Data
- **Equipos**: Un equipo puede ser dueño de un contexto completo
- **Evolución**: Cambiar "Producto" no afecta "Usuario" si están en contextos separados

**Ejemplo:** En una app de comercio:
- Contexto "Catálogo": Producto, Precio, Disponibilidad
- Contexto "Pedidos": Orden, Línea de orden, Pago
- Ambos tienen un concepto "Producto" pero con atributos diferentes

</details>

### Pregunta 2: Reglas de Dependencia
> "¿Qué pasa si permitimos que Domain importe Infrastructure? ¿Por qué es peligroso?"

<details>
<summary>Ver respuesta esperada</summary>

**Qué pasa:**
- Los casos de uso dependen de detalles de implementación
- No puedes testear lógica de negocio sin montar la base de datos
- Un cambio en Firebase puede romper tu lógica de cálculo de precios

**Por qué es peligroso:**
- **Acoplamiento**: Domain (estable) depende de Infrastructure (volátil)
- **Testabilidad**: Tests lentos y frágiles
- **Flexibilidad**: No puedes cambiar de backend sin tocar lógica de negocio

**La regla:** Las dependencias apuntan hacia adentro (Domain). Domain no sabe de Infrastructure; Infrastructure implementa interfaces definidas en Domain.

</details>

### Pregunta 3: Quality Gates
> "¿Por qué no podemos confiar solo en code reviews para mantener la calidad arquitectónica?"

<details>
<summary>Ver respuesta esperada</summary>

**Problemas con solo code reviews:**
- **Humanos fallan**: Es fácil perderse una importación incorrecta en 500 líneas de diff
- **Inconsistencia**: Cada reviewer tiene criterios ligeramente diferentes
- **Escalabilidad**: No escala a 50+ developers

**Quality gates automatizados:**
- Son consistentes (siempre aplican la misma regla)
- Son rápidos (fallan en segundos, no después de 30 min de review)
- Son escalables (funcionan igual con 5 o 500 developers)

**El balance:** Gates automatizados para lo que se puede automatizar + code reviews para lo que requiere juicio humano (diseño, nombres, etc.)

</details>

---

## Ejercicio de arquitectura {#ejercicio-de-arquitectura}

**Contexto:** Eres el arquitecto de una app de gestión de tareas (tipo Todoist). El equipo quiere añadir:

1. **Colaboración en tiempo real** (varios usuarios editando la misma tarea)
2. **Notificaciones push** cuando te asignan una tarea
3. **Modo offline** para crear tareas sin internet

**Tarea (25 min):**

Diseña la arquitectura respondiendo:

1. **Bounded contexts**: ¿Cuántos contextos identificas? ¿Cuáles son?
2. **Dependencias**: ¿Qué contexto depende de cuál? Dibuja el grafo.
3. **Quality gate**: Propón 1 regla que verificarías en CI.
4. **Trade-off**: La colaboración en tiempo real es compleja. ¿La implementas tú o usas un servicio (Firebase, Pusher)? Justifica.

<details>
<summary>💡 Pista 1: Contextos</summary>

Probablemente necesites:
- **Task Management**: Crear, editar, borrar tareas
- **Collaboration**: Quién puede ver/qué, permisos, cambios en tiempo real
- **Notifications**: Push, email, in-app
- **Sync**: Offline, resolución de conflictos

</details>

<details>
<summary>💡 Pista 2: Dependencias</summary>

```
Task Management <-- Collaboration (colaboración necesita saber de tareas)
Task Management <-- Notifications (notificaciones sobre cambios en tareas)
Task Management <-- Sync (sync de tareas)
Collaboration <-- Sync (sync de cambios colaborativos)
```

Task Management es el core; los demás son periféricos.

</details>

<details>
<summary>💡 Pista 3: Quality gate</summary>

Ejemplo: "Ningún archivo en TaskManagement/Domain puede importar de Collaboration/" (evita acoplamiento circular)

</details>

<details>
<summary>✅ Una posible solución</summary>

**Bounded contexts:**
1. **Task Management** (core): CRUD de tareas, estados, prioridades
2. **Collaboration** (support): Permisos, presencia en tiempo real, cursores
3. **Notifications** (support): Push, email digest, preferencias
4. **Sync Engine** (infrastructure): Offline, cola de cambios, resolución de conflictos

**Grafo de dependencias:**
```
Collaboration --> Task Management
Notifications --> Task Management
Sync Engine --> Task Management
Sync Engine --> Collaboration
```

**Quality gate:**
"Si un archivo en TaskManagement/Domain importa de Collaboration/, el build falla."

**Trade-off colaboración:**
**Opción A: Implementar nosotros** (WebSockets, operational transform)
- Pros: Control total, sin costo de terceros
- Contras: 3-6 meses de trabajo, complejidad enorme, bugs garantizados

**Opción B: Usar Firebase Realtime Database**
- Pros: Funciona en días, escalado automático, resolución de conflictos incluida
- Contras: Vendor lock-in, costo a escala, menos control

**Recomendación:** Empezar con Firebase para validar el producto. Si crecemos y el costo es problema, entonces invertimos en solución propia.

</details>

---

## Checklist de verificación

Antes de pasar a la Etapa 5, verifica:

- [ ] Puedes explicar qué es un bounded context con un ejemplo real
- [ ] Entiendes por qué Domain no debe importar Infrastructure
- [ ] Puedes proponer al menos 2 quality gates verificables
- [ ] Sabes cuándo modularizar y cuándo no
- [ ] Puedes justificar un trade-off a un product manager

**Si marcaste todas:** 🎉 ¡Adelante a la Etapa 5!

**Si no:** Revisa las lecciones correspondientes. La Etapa 5 asume que piensas como arquitecto.

---

## Lo que ya sabes hacer (celebración)

- ✅ Diseñar sistemas que escalan por equipos
- ✅ Definir límites semánticos (bounded contexts)
- ✅ Establecer y comunicar reglas arquitectónicas
- ✅ Tomar decisiones con trade-offs explícitos
- ✅ Preparar una arquitectura para crecimiento

**Esto es nivel senior/staff.** Estás pensando no solo en el código de hoy, sino en cómo el equipo trabajará en 6 meses.

---

## Continuación

- 
- **Si necesitas repasar:** [Bounded Contexts](../04-arquitecto/01-bounded-contexts.md)

---

**Anterior:** [Entregables — Etapa 4: Arquitecto ←](../04-arquitecto/entregables-etapa-4.md) · **Siguiente:** [Etapa 5 — Maestría: Concurrency, SwiftUI moderno y patron... →](../05-maestria/00-introduccion.md)
