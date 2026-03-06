# Auditoria de Saltos, Prerrequisitos y Redundancias - Curso iOS

## Resumen por etapa

| Etapa | Lecciones | P1 | P2 |
|---|---:|---:|---:|
| Etapa 0 - Core Mobile | 13 | 0 | 0 |
| Etapa 1 - Junior | 16 | 0 | 1 |
| Etapa 2 - Mid | 16 | 0 | 2 |
| Etapa 3 - Senior | 9 | 0 | 0 |
| Etapa 4 - Arquitecto | 8 | 0 | 0 |
| Etapa 5 - Maestria | 17 | 0 | 0 |
| Anexos | 35 | 0 | 5 |

Hallazgos totales: 9 (P1=0, P2=9)

## Hallazgos P1

- Sin P1 detectados automaticamente.

## Hallazgos P2

- Salto de complejidad en transicion esperada: `anexos/calentamiento-etapa-5-maestria.md` (899) -> `anexos/quizzes-autoevaluacion.md` (2738).
- Salto de complejidad en transicion esperada: `anexos/preguntas-entrevista.md` (2853) -> `anexos/hallazgos-y-correcciones.md` (719).
- Salto de complejidad en transicion esperada: `anexos/adrs/TEMPLATE-ADR.md` (176) -> `anexos/apendice-banca-ledger.md` (1246).
- Salto de complejidad en transicion esperada: `anexos/glosario.md` (727) -> `anexos/proyecto-final.md` (1873).
- Redundancia media entre lecciones consecutivas (Jaccard headings=0.62) en `anexos/adrs/ADR-004-navegacion-event-driven.md`.
- Salto de complejidad en transicion esperada: `01-fundamentos/06-conectando-la-app.md` (1688) -> `01-fundamentos/entregables-etapa-1.md` (681).
- Salto de complejidad en transicion esperada: `02-integracion/06-composition-root.md` (1930) -> `02-integracion/07-swiftui-enterprise.md` (6227).
- Salto de complejidad en transicion esperada: `02-integracion/08-swift-concurrency-enterprise.md` (3986) -> `02-integracion/09-app-final-etapa-2.md` (1723).
- Salto de complejidad en transicion esperada: `03-evolucion/07-backend-firebase.md` (2600) -> `03-evolucion/entregables-etapa-3.md` (1180).

## Accion sugerida

1. Resolver P1 de prerequisitos implicitos con un bloque fijo de entrada por leccion.
2. Añadir notas de transicion en saltos de complejidad para evitar ruptura cognitiva.
3. Podar redundancias moviendo contenido repetido a anexos o referencias cruzadas.

