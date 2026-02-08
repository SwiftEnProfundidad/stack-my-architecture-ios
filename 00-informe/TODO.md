# TODO del curso

Actualizado: 2026-02-08 (tarde).

## Pendientes de mejora

- [x] [Alta] Reducir duplicación entre `01-fundamentos/00-setup.md` y `01-fundamentos/04-estructura-feature-first.md` en la parte de creación del proyecto Xcode y estructura inicial.
- [x] [Media] Añadir referencias cruzadas explícitas desde las lecciones prácticas a `01-fundamentos/01-principios-ingenieria.md` (por ejemplo: "Recuerda el Principio 1" al aplicar TDD/BDD).
- [x] [Media] Dividir `01-fundamentos/02-metodologia-bdd-tdd.md` (637 líneas) en dos lecciones: BDD (teoría y escenarios) y TDD (práctica Red-Green-Refactor).
- [ ] [Alta] Hardenizar la auditoría interna para este repo: documentar y automatizar una ejecución que analice `stack-my-architecture-ios` (evitar falsos positivos cuando el orquestador se lanza desde `ast-intelligence-hooks`).

## Estado de auditoría interna (2026-02-08)

- Orquestador ejecutado: `audit-orchestrator.sh` (modo full audit con `AUDIT_OPTION=1`).
- Resultado del orquestador en esta máquina: mezcló findings de `ast-intelligence-hooks` (falsos positivos para este repo).
- Verificación directa AST sobre este repo: `CRITICAL=0`, `HIGH=0`, `MEDIUM=0`, `LOW=0`.
