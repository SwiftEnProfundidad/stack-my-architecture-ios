# Backlog técnico del repositorio

Actualizado: 2026-02-11.

## Alcance de este documento

Este archivo es un backlog de **mantenimiento del repositorio del curso**. No define objetivos de aprendizaje para el alumno ni es una lección curricular.

## Mejora curricular (estado)

- [x] [Alta] Reducir duplicación entre `01-fundamentos/00-setup.md` y `01-fundamentos/04-estructura-feature-first.md` en la parte de creación del proyecto Xcode y estructura inicial.
- [x] [Media] Añadir referencias cruzadas explícitas desde las lecciones prácticas a `01-fundamentos/01-principios-ingenieria.md` (por ejemplo: "Recuerda el Principio 1" al aplicar TDD/BDD).
- [x] [Media] Dividir `01-fundamentos/02-metodologia-bdd-tdd.md` en dos lecciones: BDD (teoría y escenarios) y TDD (práctica Red-Green-Refactor).

## Mantenimiento interno (no curricular)

- [ ] [Alta] Hardenizar la auditoría interna de este repo para ejecutar análisis AST de forma aislada (sin mezclar findings de repos vecinos).

### Nota sobre AST (por qué aparece aquí)

La referencia a AST corresponde a una herramienta interna de auditoría de arquitectura usada por maintainers para detectar violaciones estructurales en CI/local. No es contenido que el alumno deba estudiar para avanzar en las etapas del curso.

### Estado técnico registrado (2026-02-08)

- Orquestador ejecutado: `audit-orchestrator.sh` (modo full audit con `AUDIT_OPTION=1`).
- Resultado en esa ejecución: mezcló findings de `ast-intelligence-hooks` (falsos positivos para este repo).
- Verificación directa AST sobre este repo: `CRITICAL=0`, `HIGH=0`, `MEDIUM=0`, `LOW=0`.
