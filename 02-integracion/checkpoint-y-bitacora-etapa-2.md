# Checkpoint y bitácora - Etapa 2: Integración

Esta etapa valida que ya sabes ensamblar features, navegación, infraestructura real y composición sin perder la arquitectura.

## Qué debes poder hacer antes de avanzar

- Conectar features desacopladas por contratos o eventos.
- Cablear un `Composition Root` claro y defendible.
- Integrar infraestructura real sin contaminar dominio ni aplicación.
- Añadir tests de integración útiles.
- Explicar cómo se conectan login, catálogo y navegación sin imports prohibidos.

## Checklist de cierre

- [ ] Sé explicar por qué el `Composition Root` es el único sitio que conoce implementaciones concretas.
- [ ] Puedo justificar cómo navegan las features sin acoplarse entre sí.
- [ ] He visto integración real con red o equivalentes sin romper capas.
- [ ] Entiendo qué papel juegan `Sendable`, `@MainActor` y boundaries async en este bloque.
- [ ] Puedo seguir la cadena feature -> contrato -> wiring -> UI final.

## Mini-quiz de autoevaluación

1. ¿Qué pasaría si Login importara directamente Catalog UI?
2. ¿Qué problema resuelve un contrato entre features?
3. ¿Qué cambia entre un test unitario y uno de integración en esta etapa?
4. ¿Por qué el wiring no debe vivir repartido por vistas o casos de uso?
5. ¿Qué riesgo de concurrencia empieza a aparecer aquí y no en la etapa 1?

## Bitácora guiada

### Lo que ya domino

Anota qué parte del ensamblado entre features ya puedes montar con seguridad.

### Lo que aún me cuesta

Escribe dónde aparece más fricción: navegación, wiring, infraestructura o concurrencia.

### Decisión mejor defendida

Resume una decisión de integración que hoy sí sabes justificar.

### Próximo paso

Describe qué debes reforzar para entrar en Evolución pensando ya en cache, consistencia y operación.
