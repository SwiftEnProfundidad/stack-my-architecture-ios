# Backlog técnico del repositorio

Actualizado: 2026-02-24.

## Alcance de este documento

Este archivo es un backlog de **mantenimiento del repositorio del curso**. No define objetivos de aprendizaje para el alumno ni es una lección curricular.

## Mejora curricular (estado)

- [x] [Alta] Reducir duplicación entre `01-fundamentos/00-setup.md` y `01-fundamentos/04-estructura-feature-first.md` en la parte de creación del proyecto Xcode y estructura inicial.
- [x] [Media] Añadir referencias cruzadas explícitas desde las lecciones prácticas a `01-fundamentos/01-principios-ingenieria.md` (por ejemplo: "Recuerda el Principio 1" al aplicar TDD/BDD).
- [x] [Media] Dividir `01-fundamentos/02-metodologia-bdd-tdd.md` en dos lecciones: BDD (teoría y escenarios) y TDD (práctica Red-Green-Refactor).

## Mantenimiento interno (no curricular)

- [x] [Media] Añadir validación automática de enlaces/anchors al pipeline de publicación de `dist/` (workflow `course-qa-audit.yml` ejecutando `run-qa-audit-bundle.sh` con `audit-cross-links.py`).
- [ ] [Media] Ejecutar revisión visual trimestral de diagramas Mermaid y assets embebidos en el HTML final.
