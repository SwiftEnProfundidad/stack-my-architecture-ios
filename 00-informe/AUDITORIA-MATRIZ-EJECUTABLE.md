# Auditoria Matriz Ejecutable - Curso iOS

## Resumen

| Etapa | Lecciones | Mermaid | Snippets | Referencias scaffold | Sin practica | Sin validacion | P1+ |
|---|---:|---:|---:|---:|---:|---:|---:|
| Etapa 0 - Core Mobile | 13 | 15 | 15 | 16 | 1 | 1 | 1 |
| Etapa 1 - Junior | 16 | 46 | 162 | 14 | 1 | 0 | 0 |
| Etapa 2 - Mid | 16 | 45 | 179 | 55 | 2 | 0 | 2 |
| Anexos | 35 | 14 | 187 | 6 | 5 | 2 | 2 |
| Etapa 3 - Senior | 9 | 25 | 81 | 30 | 1 | 0 | 0 |
| Etapa 4 - Arquitecto | 8 | 29 | 58 | 47 | 1 | 0 | 0 |
| Etapa 5 - Maestria | 17 | 53 | 203 | 98 | 4 | 0 | 0 |

Severidad global: OK=108, P1=5, P2=1, P0=0, P3=0

## Hallazgos P1

- `00-core-mobile/12-mobile-architect-parity-ios-android.md`: Hay practica pero falta validacion/checklist explicita.
- `02-integracion/01-feature-catalog/00-especificacion-bdd.md`: No se detecta bloque de practica/ejercicio.
- `02-integracion/05-integration-tests.md`: No se detecta bloque de practica/ejercicio.
- `anexos/diagramas/atlas-arquitectura.md`: Hay practica pero falta validacion/checklist explicita.
- `anexos/preguntas-entrevista.md`: Hay practica pero falta validacion/checklist explicita.

## Matriz por leccion

| Path | Etapa | Palabras | Mermaid | Snippets | Obj | Pre | Pract | Valid | Sev |
|---|---|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| `00-core-mobile/00-introduccion.md` | Etapa 0 - Core Mobile | 409 | 0 | 0 | Y | Y | Y | Y | OK |
| `00-core-mobile/01-marco-de-decisiones.md` | Etapa 0 - Core Mobile | 611 | 2 | 2 | Y | Y | Y | Y | OK |
| `00-core-mobile/02-invariantes-y-contratos.md` | Etapa 0 - Core Mobile | 585 | 2 | 2 | Y | Y | Y | Y | OK |
| `00-core-mobile/03-variabilidad-y-evolucion.md` | Etapa 0 - Core Mobile | 562 | 2 | 2 | Y | Y | Y | Y | OK |
| `00-core-mobile/04-calidad-pr-ready.md` | Etapa 0 - Core Mobile | 574 | 1 | 1 | Y | N | Y | Y | OK |
| `00-core-mobile/05-observabilidad-operacion.md` | Etapa 0 - Core Mobile | 718 | 1 | 1 | Y | Y | Y | Y | OK |
| `00-core-mobile/06-release-rollback-flags.md` | Etapa 0 - Core Mobile | 587 | 1 | 1 | Y | N | N | Y | OK |
| `00-core-mobile/07-apis-contratos-versionado.md` | Etapa 0 - Core Mobile | 651 | 1 | 1 | N | N | Y | Y | OK |
| `00-core-mobile/08-seguridad-privacidad-threat-modeling.md` | Etapa 0 - Core Mobile | 906 | 1 | 1 | N | N | Y | Y | OK |
| `00-core-mobile/09-dependency-governance-supply-chain.md` | Etapa 0 - Core Mobile | 601 | 1 | 1 | Y | Y | Y | Y | OK |
| `00-core-mobile/10-plantillas.md` | Etapa 0 - Core Mobile | 1065 | 1 | 1 | Y | N | Y | Y | OK |
| `00-core-mobile/11-crosswalk-ios-android.md` | Etapa 0 - Core Mobile | 462 | 1 | 1 | Y | Y | Y | Y | OK |
| `00-core-mobile/12-mobile-architect-parity-ios-android.md` | Etapa 0 - Core Mobile | 1118 | 1 | 1 | Y | N | Y | N | P1 |
| `01-fundamentos/00-introduccion.md` | Etapa 1 - Junior | 3888 | 7 | 7 | Y | Y | Y | Y | OK |
| `01-fundamentos/00-setup.md` | Etapa 1 - Junior | 2028 | 1 | 15 | N | N | Y | Y | OK |
| `01-fundamentos/01-principios-ingenieria.md` | Etapa 1 - Junior | 3651 | 3 | 3 | Y | Y | Y | Y | OK |
| `01-fundamentos/02-metodologia-bdd-tdd.md` | Etapa 1 - Junior | 2214 | 2 | 8 | Y | Y | Y | Y | OK |
| `01-fundamentos/02-metodologia-tdd-practica.md` | Etapa 1 - Junior | 4075 | 6 | 16 | Y | Y | Y | Y | OK |
| `01-fundamentos/03-stack-tecnologico.md` | Etapa 1 - Junior | 4254 | 2 | 7 | Y | Y | Y | Y | OK |
| `01-fundamentos/04-estructura-feature-first.md` | Etapa 1 - Junior | 2267 | 2 | 4 | Y | Y | Y | Y | OK |
| `01-fundamentos/05-feature-login/00-especificacion-bdd.md` | Etapa 1 - Junior | 2810 | 2 | 9 | N | N | Y | Y | OK |
| `01-fundamentos/05-feature-login/01-domain.md` | Etapa 1 - Junior | 4489 | 3 | 22 | Y | Y | Y | Y | OK |
| `01-fundamentos/05-feature-login/02-application.md` | Etapa 1 - Junior | 5055 | 5 | 19 | Y | Y | Y | Y | OK |
| `01-fundamentos/05-feature-login/03-infrastructure.md` | Etapa 1 - Junior | 4002 | 4 | 14 | Y | Y | Y | Y | OK |
| `01-fundamentos/05-feature-login/04-interface-swiftui.md` | Etapa 1 - Junior | 5102 | 5 | 18 | Y | Y | Y | Y | OK |
| `01-fundamentos/05-feature-login/05-tdd-ciclo-completo.md` | Etapa 1 - Junior | 3095 | 3 | 12 | Y | Y | Y | Y | OK |
| `01-fundamentos/05-feature-login/ADR-001-login.md` | Etapa 1 - Junior | 1864 | 0 | 0 | Y | Y | Y | Y | P2 |
| `01-fundamentos/06-conectando-la-app.md` | Etapa 1 - Junior | 1688 | 0 | 6 | Y | Y | Y | Y | OK |
| `01-fundamentos/entregables-etapa-1.md` | Etapa 1 - Junior | 681 | 1 | 2 | N | Y | N | Y | OK |
| `02-integracion/00-introduccion.md` | Etapa 2 - Mid | 1686 | 3 | 3 | Y | N | Y | Y | OK |
| `02-integracion/01-feature-catalog/00-especificacion-bdd.md` | Etapa 2 - Mid | 1605 | 2 | 12 | Y | N | N | Y | P1 |
| `02-integracion/01-feature-catalog/01-domain.md` | Etapa 2 - Mid | 1640 | 2 | 7 | Y | N | Y | Y | OK |
| `02-integracion/01-feature-catalog/02-application.md` | Etapa 2 - Mid | 2054 | 3 | 9 | Y | N | Y | Y | OK |
| `02-integracion/01-feature-catalog/03-infrastructure.md` | Etapa 2 - Mid | 1891 | 2 | 10 | Y | N | Y | Y | OK |
| `02-integracion/01-feature-catalog/04-interface-swiftui.md` | Etapa 2 - Mid | 2682 | 4 | 12 | Y | Y | Y | Y | OK |
| `02-integracion/02-navegacion-eventos.md` | Etapa 2 - Mid | 1708 | 3 | 9 | Y | Y | Y | Y | OK |
| `02-integracion/03-contratos-features.md` | Etapa 2 - Mid | 1599 | 3 | 8 | Y | N | Y | Y | OK |
| `02-integracion/04-infra-real-network.md` | Etapa 2 - Mid | 1547 | 3 | 9 | Y | N | Y | Y | OK |
| `02-integracion/05-integration-tests.md` | Etapa 2 - Mid | 1724 | 3 | 7 | Y | N | N | Y | P1 |
| `02-integracion/06-composition-root.md` | Etapa 2 - Mid | 1930 | 3 | 11 | Y | N | Y | Y | OK |
| `02-integracion/07-swiftui-enterprise.md` | Etapa 2 - Mid | 6227 | 3 | 40 | Y | Y | Y | Y | OK |
| `02-integracion/08-swift-concurrency-enterprise.md` | Etapa 2 - Mid | 3986 | 5 | 30 | Y | N | Y | Y | OK |
| `02-integracion/09-app-final-etapa-2.md` | Etapa 2 - Mid | 1723 | 2 | 8 | Y | Y | Y | Y | OK |
| `02-integracion/01-feature-catalog/ADR-002-catalog.md` | Etapa 2 - Mid | 1172 | 2 | 2 | Y | Y | Y | Y | OK |
| `02-integracion/entregables-etapa-2.md` | Etapa 2 - Mid | 1501 | 2 | 2 | Y | Y | Y | Y | OK |
| `anexos/consolidacion-etapa-2-integracion.md` | Anexos | 804 | 0 | 2 | N | N | Y | Y | OK |
| `03-evolucion/00-introduccion.md` | Etapa 3 - Senior | 1692 | 4 | 4 | Y | N | N | Y | OK |
| `03-evolucion/01-caching-offline.md` | Etapa 3 - Senior | 2783 | 4 | 14 | Y | N | Y | Y | OK |
| `03-evolucion/02-consistencia.md` | Etapa 3 - Senior | 1782 | 2 | 9 | Y | N | Y | Y | OK |
| `03-evolucion/03-observabilidad.md` | Etapa 3 - Senior | 1886 | 3 | 11 | Y | N | Y | Y | OK |
| `03-evolucion/04-tests-avanzados.md` | Etapa 3 - Senior | 1880 | 4 | 13 | Y | N | Y | Y | OK |
| `03-evolucion/05-trade-offs.md` | Etapa 3 - Senior | 1863 | 2 | 3 | Y | N | Y | Y | OK |
| `03-evolucion/06-swiftdata-store.md` | Etapa 3 - Senior | 2356 | 2 | 9 | Y | N | Y | Y | OK |
| `03-evolucion/07-backend-firebase.md` | Etapa 3 - Senior | 2600 | 2 | 16 | Y | N | Y | Y | OK |
| `03-evolucion/entregables-etapa-3.md` | Etapa 3 - Senior | 1180 | 2 | 2 | Y | Y | Y | Y | OK |
| `anexos/calentamiento-etapa-3-evolucion.md` | Anexos | 718 | 1 | 1 | Y | Y | Y | Y | OK |
| `04-arquitecto/00-introduccion.md` | Etapa 4 - Arquitecto | 1665 | 4 | 4 | Y | N | Y | Y | OK |
| `04-arquitecto/01-bounded-contexts.md` | Etapa 4 - Arquitecto | 1842 | 5 | 8 | Y | N | Y | Y | OK |
| `04-arquitecto/02-reglas-dependencia-ci.md` | Etapa 4 - Arquitecto | 1783 | 4 | 7 | Y | N | Y | Y | OK |
| `04-arquitecto/03-navegacion-deeplinks.md` | Etapa 4 - Arquitecto | 1837 | 4 | 13 | Y | N | Y | Y | OK |
| `04-arquitecto/04-versionado-spm.md` | Etapa 4 - Arquitecto | 1770 | 4 | 10 | Y | N | Y | Y | OK |
| `04-arquitecto/05-guia-arquitectura.md` | Etapa 4 - Arquitecto | 1867 | 4 | 6 | Y | N | Y | Y | OK |
| `04-arquitecto/06-quality-gates.md` | Etapa 4 - Arquitecto | 1850 | 3 | 4 | Y | N | Y | Y | OK |
| `04-arquitecto/entregables-etapa-4.md` | Etapa 4 - Arquitecto | 1324 | 1 | 6 | Y | N | N | Y | OK |
| `anexos/consolidacion-etapa-4-arquitecto.md` | Anexos | 1035 | 0 | 2 | N | N | Y | Y | OK |
| `05-maestria/00-introduccion.md` | Etapa 5 - Maestria | 2030 | 5 | 6 | Y | N | N | Y | OK |
| `05-maestria/01-isolation-domains.md` | Etapa 5 - Maestria | 3312 | 4 | 29 | Y | Y | Y | Y | OK |
| `05-maestria/02-actors-en-arquitectura.md` | Etapa 5 - Maestria | 2720 | 6 | 16 | Y | Y | Y | Y | OK |
| `05-maestria/03-structured-concurrency.md` | Etapa 5 - Maestria | 2572 | 7 | 22 | Y | Y | Y | Y | OK |
| `05-maestria/04-testing-concurrente.md` | Etapa 5 - Maestria | 2283 | 4 | 15 | N | N | Y | Y | OK |
| `05-maestria/05-swiftui-state-moderno.md` | Etapa 5 - Maestria | 2135 | 3 | 17 | Y | Y | Y | Y | OK |
| `05-maestria/06-swiftui-performance.md` | Etapa 5 - Maestria | 2175 | 4 | 17 | Y | Y | Y | Y | OK |
| `05-maestria/07-composicion-avanzada.md` | Etapa 5 - Maestria | 2214 | 4 | 14 | Y | Y | Y | Y | OK |
| `05-maestria/08-memory-leaks-y-diagnostico.md` | Etapa 5 - Maestria | 2251 | 5 | 15 | N | N | Y | Y | OK |
| `05-maestria/09-migracion-swift6.md` | Etapa 5 - Maestria | 2011 | 3 | 16 | Y | Y | Y | Y | OK |
| `05-maestria/10-debugging-xcode.md` | Etapa 5 - Maestria | 1914 | 1 | 12 | N | N | Y | Y | OK |
| `05-maestria/11-entrevista-arquitecto.md` | Etapa 5 - Maestria | 2965 | 1 | 1 | N | N | Y | Y | OK |
| `05-maestria/12-arquitectura-adaptativa.md` | Etapa 5 - Maestria | 3125 | 1 | 18 | N | N | Y | Y | OK |
| `05-maestria/entregables-etapa-5.md` | Etapa 5 - Maestria | 1917 | 2 | 2 | Y | N | N | Y | OK |
| `05-maestria/10-rubrica-final/01-rubrica-empleabilidad-ios.md` | Etapa 5 - Maestria | 2044 | 1 | 1 | Y | N | N | Y | OK |
| `05-maestria/10-rubrica-final/02-evidencias-obligatorias-ios.md` | Etapa 5 - Maestria | 1069 | 1 | 1 | Y | Y | Y | Y | OK |
| `05-maestria/10-rubrica-final/03-checklist-entrega-para-entrevista.md` | Etapa 5 - Maestria | 578 | 1 | 1 | Y | N | N | Y | OK |
| `anexos/calentamiento-etapa-5-maestria.md` | Anexos | 899 | 1 | 3 | N | Y | N | Y | OK |
| `anexos/quizzes-autoevaluacion.md` | Anexos | 2738 | 0 | 1 | N | N | N | Y | OK |
| `anexos/guia-recuperacion-ios.md` | Anexos | 1810 | 1 | 34 | Y | Y | Y | Y | OK |
| `anexos/diagramas/atlas-arquitectura.md` | Anexos | 2282 | 9 | 9 | Y | Y | Y | N | P1 |
| `anexos/guia-nueva-feature.md` | Anexos | 1374 | 1 | 8 | N | Y | N | Y | OK |
| `anexos/git-workflow-curso.md` | Anexos | 1192 | 0 | 13 | Y | Y | Y | Y | OK |
| `anexos/xcode-cheat-sheet.md` | Anexos | 948 | 0 | 4 | N | N | N | Y | OK |
| `anexos/como-leer-documentacion.md` | Anexos | 1321 | 0 | 13 | Y | N | Y | Y | OK |
| `anexos/simulator-tips.md` | Anexos | 1278 | 0 | 17 | N | N | Y | Y | OK |
| `anexos/mental-models.md` | Anexos | 1427 | 0 | 16 | N | N | Y | Y | OK |
| `anexos/errores-compilacion.md` | Anexos | 1526 | 0 | 26 | N | N | Y | Y | OK |
| `anexos/guia-solid.md` | Anexos | 1538 | 0 | 6 | N | N | Y | Y | OK |
| `anexos/guia-cqs-cqrs.md` | Anexos | 1480 | 0 | 11 | N | N | Y | Y | OK |
| `anexos/preguntas-entrevista.md` | Anexos | 2853 | 0 | 0 | Y | N | Y | N | P1 |
| `anexos/hallazgos-y-correcciones.md` | Anexos | 719 | 0 | 0 | Y | N | N | Y | OK |
| `anexos/adrs/INDICE-ADRS.md` | Anexos | 627 | 0 | 0 | Y | Y | Y | Y | OK |
| `anexos/adrs/ADR-003-composition-root-unico.md` | Anexos | 876 | 0 | 4 | Y | Y | Y | Y | OK |
| `anexos/adrs/ADR-004-navegacion-event-driven.md` | Anexos | 859 | 0 | 6 | Y | Y | Y | Y | OK |
| `anexos/adrs/ADR-005-contratos-features.md` | Anexos | 415 | 0 | 0 | Y | Y | Y | Y | OK |
| `anexos/adrs/ADR-006-infra-network-urlsession.md` | Anexos | 413 | 0 | 0 | Y | Y | Y | Y | OK |
| `anexos/adrs/ADR-007-cache-network-first-ttl.md` | Anexos | 415 | 0 | 0 | Y | Y | Y | Y | OK |
| `anexos/adrs/ADR-008-consistencia-invalidation-policy.md` | Anexos | 419 | 0 | 0 | Y | Y | Y | Y | OK |
| `anexos/adrs/ADR-009-observabilidad-por-decoradores.md` | Anexos | 404 | 0 | 0 | Y | Y | Y | Y | OK |
| `anexos/adrs/ADR-010-firebase-backend-principal.md` | Anexos | 422 | 0 | 0 | Y | Y | Y | Y | OK |
| `anexos/adrs/ADR-011-bounded-contexts-governance.md` | Anexos | 417 | 0 | 0 | Y | Y | Y | Y | OK |
| `anexos/adrs/ADR-012-reglas-dependencia-progresivas.md` | Anexos | 415 | 0 | 0 | Y | Y | Y | Y | OK |
| `anexos/adrs/ADR-013-versionado-spm-progresivo.md` | Anexos | 414 | 0 | 0 | Y | Y | Y | Y | OK |
| `anexos/adrs/ADR-014-quality-gates-conceptuales.md` | Anexos | 426 | 0 | 0 | Y | Y | Y | Y | OK |
| `anexos/adrs/TEMPLATE-ADR.md` | Anexos | 176 | 0 | 0 | Y | Y | Y | Y | OK |
| `anexos/apendice-banca-ledger.md` | Anexos | 1246 | 1 | 7 | Y | Y | Y | Y | OK |
| `anexos/glosario.md` | Anexos | 727 | 0 | 0 | Y | Y | Y | Y | OK |
| `anexos/proyecto-final.md` | Anexos | 1873 | 0 | 4 | Y | N | Y | Y | OK |

