# Core Mobile Architecture

## Qué es este Core y por qué existe

Este Core es la base compartida entre las rutas de iOS y Android. No reemplaza ninguna lección de plataforma. Su función es dar un marco único para tomar decisiones de arquitectura móvil con criterio consistente en ambos ecosistemas.

Existe por una razón práctica: cuando iOS y Android evolucionan con marcos distintos, aparecen incoherencias en seguridad, contratos API, observabilidad, releases y gobernanza. Este Core reduce esa variabilidad y define una forma común de decidir, validar, operar y evolucionar.

## Cómo usar este Core junto a iOS/Android

Usa este bloque como capa de decisión transversal.

Si estás en iOS, estúdialo en paralelo con Fundamentos, Integración, Evolución, Arquitecto y Maestría.

Si estás en Android, estúdialo en paralelo con Nivel 0, Junior, Mid, Senior y Maestría.

Regla operativa: cada vez que en tu track aparezca una decisión crítica (arquitectura, API, release, seguridad, operación), vuelve al Core y aplica las checklists/templates antes de implementar.

## Principios del Core: decidir, validar, operar y evolucionar

### Decide

No se decide por preferencia personal. Se decide por contexto, restricciones y trade-offs explícitos.

### Validate

No basta “suena bien”. Toda decisión debe tener evidencia verificable: tests, métricas, señales operativas.

### Operate

Lo que no se puede observar ni recuperar en incidente no está listo para producción.

### Evolve

La arquitectura no es foto estática. Debe soportar cambios incrementales sin caos ni reescrituras de alto riesgo.

---


## Refuerzo pedagogico

### Objetivo
- Entender para qué existe el Core Mobile y cuándo usarlo como marco de decisión transversal en iOS y Android.

### Prerrequisitos
- No hay prerrequisitos técnicos obligatorios. Basta con conocer la estructura general del curso que vas a seguir (iOS o Android).

### Practica guiada
- Elige una decisión real de tu app (por ejemplo, navegación, contrato API o estrategia de release).
- Escríbela en 4 líneas usando este formato: `decidir -> validar -> operar -> evolucionar`.
- Define una evidencia concreta para validar esa decisión (test, métrica o checklist).

### Verificacion rapida
- ¿Puedes explicar con tus palabras por qué “funcionar en local” no equivale a “estar lista para producción”?
- ¿Puedes nombrar una decisión que deba ser común entre iOS y Android en tu proyecto?
- ¿Puedes indicar qué evidencia usarás para validar esa decisión?

## Diagrama de arquitectura por capas

![Diagrama de arquitectura por capas (Core Mobile)](assets/architecture-ios-core-mobile.png)

La leyenda visual superior define la semántica por tipo de trazo y punta de flecha; el color de cada flecha indica el módulo de origen.

### Convencion de flechas (obligatoria en el curso)
1. `-->` dependencia directa en runtime (linea continua, punta cerrada).
2. `--o` relacion continua con punta abierta.
3. `-.->` wiring/configuracion (linea discontinua, punta cerrada).
4. `-.o` dependencia discontinua contra contrato/abstraccion (punta abierta).

### Zoom de detalle por feature

Para evitar sobrecarga visual en el mapa global, aquí tienes dos vistas de detalle separadas:

#### Login (detalle)

![Diagrama de arquitectura Login (detalle)](assets/architecture-ios-login-detail-v3.png)

#### Catalog (detalle)

![Diagrama de arquitectura Catalog (detalle)](assets/architecture-ios-catalog-detail-v4.png)
