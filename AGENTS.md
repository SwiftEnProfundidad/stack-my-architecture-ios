# AGENTS.md - stack-my-architecture-ios

## Idioma y comunicación
- MUST: Responder siempre en español.
- MUST: Mantener trazabilidad en cada entrega (`escenario -> tests -> evidencia -> task`).
- MUST: Al cerrar cada iteración, responder siempre con `MD de seguimiento` y `task actual`.

## Project mode
- PROJECT MODE: brownfield

## Método
- REQUIRED SKILL: `enterprise-operating-system`

## Fuente de verdad
- MUST: La autoridad documental local vive en [README.md](/Users/juancarlosmerlosalbarracin/Developer/Projects/stack-my-architecture/stack-my-architecture-ios/README.md), `docs/` y `anexos/`.
- MUST: La cadena de skills del repo se resuelve por `AGENTS.md -> vendor/skills -> skills.sources.json -> skills.lock.json`.

## Skills requeridos
- REQUIRED SKILL: `ios-enterprise-rules`
- REQUIRED SKILL: `swift-concurrency`
- REQUIRED SKILL: `swiftui-expert-skill`

## Reglas del modo
- MUST: No tocar ejemplos iOS, material del curso o `assistant-bridge/` salvo petición explícita.
- MUST: Mantener visible qué parte del legado didáctico se conserva y qué parte solo documenta metodología.

## Reglas locales del repo
- MUST: Mantener organización feature-first por bounded context en cualquier cambio iOS futuro.
- MUST: Para cambios de producto iOS, ejecutar el comando de test/smoke documentado por el módulo afectado antes de cerrar la iteración.
