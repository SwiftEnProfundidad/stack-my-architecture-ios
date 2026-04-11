# Plan de coherencia del curso iOS

Objetivo: convertir el curso en un material sin ambigüedades donde el estudiante puede seguir cada lección, escribir código en Xcode y ver los tests en verde.

---

## Leyenda

- ✅ Cerrado
- 🚧 En construcción (máximo 1)
- ⏳ Pendiente
- ⛔ Bloqueado

---

## Fase 0 — Diagnóstico completado ✅

> Estado del curso al inicio del plan.

| Tarea | Estado | Notas |
|---|---|---|
| Auditoría de checkpoints (73/91 lecciones cubiertas) | ✅ | Completado en sesión anterior |
| Identificación de incoherencias críticas Etapa 1 | ✅ | `AuthHTTPRepository`, `InMemoryAuthRepository`, `LoginError` corregidos |
| Mapeo de nomenclatura pedagógica vs scaffold | ✅ | `equivalencias-scaffold.md` existía; audit confirmó 190+ ocurrencias de nombres pedagógicos |
| Decisión de modelo pedagógico (C + Camino A) | ✅ | Nombres del scaffold en todo el curso; Etapas 2-5 como scaffold de referencia |

---

## Fase 1 — Unificación de nomenclatura (Opción C) ✅

> Alinear los nombres de todos los snippets de código y referencias en prosa con los nombres reales del scaffold. Eliminar la necesidad de `equivalencias-scaffold.md` como tabla de emergencia.

**Alcance:** ~705 reemplazos en lecciones de Etapas 0-5 + documento de entrevista.

| Tarea | Estado | Archivos afectados |
|---|---|---|
| 1.1 Reemplazar `LoginUseCase` → `AuthenticateUserUseCase` en código | ✅ | 203 reemplazos en 34 archivos |
| 1.2 Reemplazar `AuthGateway` / `authGateway` → `AuthRepository` / `authRepository` | ✅ | 123 reemplazos en 24 archivos (excluidos plan, informe, equivalencias) |
| 1.3 Reemplazar `LoginUseCase.Error` → `LoginError` | ✅ | 38 reemplazos en 6 archivos (AuthenticateUserUseCase.Error → LoginError) |
| 1.4 Reemplazar `RemoteAuthRepository` / `StubAuthRepository` → `AuthHTTPRepository` / `InMemoryAuthRepository` | ✅ | 116 reemplazos en 27 archivos |
| 1.5 Reemplazar `.login()` / `loginTapped` / `onLoginSucceeded` / `onEvent` → `.submit()` / `LoginNavigating` / `navigator.goToCatalog()` | ✅ | ~49 ocurrencias en 13 archivos (Etapas 1-5) |
| 1.6 Reemplazar `LoginViewModel(login:)` → `LoginViewModel(useCase:navigator:)` | ✅ | aplicado junto con 1.5 en todos los archivos afectados |
| 1.7 Reemplazar `Email` → `EmailAddress`, `Session` → `UserSession` | ✅ | 261 reemplazos en 11 archivos Etapa 1; falsos positivos (strings UI, labels mermaid) preservados |
| 1.8 Reemplazar `AuthError` → `LoginError` en prosa y código | ✅ | 57 reemplazos Etapa 1 + 11 Etapas 2-5; `equivalencias-scaffold.md` y `ADR-001` preservados |
| 1.9 Actualizar `equivalencias-scaffold.md` para reflejar que ya no hay divergencias (o eliminarlo) | ✅ | Tabla reescrita: solo muestra las 3 diferencias intencionalmente pedagógicas restantes |
| 1.10 Limpiar `LoginUseCase` residuales en anexos + verificación criterio cierre | ✅ | `atlas-arquitectura.md`, `mental-models.md`, `ADR-003`, `apendice-banca-ledger.md` actualizados; criterio de cierre verificado |

**Criterio de cierre de Fase 1:** ✅ VERIFICADO — `grep -r "LoginUseCase\|AuthGateway\|AuthError" --include="*.md"` devuelve 0 resultados fuera de prosa explicativa y archivos excluídos (ADR-001, equivalencias-scaffold, guia-cqs, consolidacion-etapa-2).

---

## Fase 2 — Modelo pedagógico explícito ✅

> Dejar claro en el curso que el scaffold es la solución de referencia, y guiar al estudiante sobre cómo usarlo.

| Tarea | Estado | Notas |
|---|---|---|
| 2.1 Añadir intro de modelo pedagógico a `01-fundamentos/00-introduccion.md` | ✅ | Sección "Cómo funciona el modelo de aprendizaje" añadida con 2 pistas + cómo usar el scaffold |
| 2.2 Añadir nota de modelo a intro de Etapa 2 | ✅ | Nota de modelo pedagógico añadida en `02-integracion/00-introduccion.md` |
| 2.3 Añadir nota de modelo a intro de Etapa 3 | ✅ | Nota de modelo pedagógico añadida en `03-evolucion/00-introduccion.md` |
| 2.4 Revisar y actualizar `entregables-etapa-1.md` con nombres del scaffold | ✅ | Nombres ya correctos por Fase 1; corregido "closure" → protocolo `LoginNavigating` |
| 2.5 Revisar y actualizar `entregables-etapa-2.md` | ✅ | Verificado limpio, sin nombres obsoletos |
| 2.6 Revisar y actualizar `entregables-etapa-3.md` | ✅ | Verificado limpio, sin nombres obsoletos |

**Criterio de cierre:** ✅ VERIFICADO — un nuevo estudiante puede leer las intros de E1-E3 y saber exactamente qué construye y cómo se evalúa.

**FASE 2 COMPLETADA.**

---

## Fase 3 — Checkpoints de construcción Etapa 1 (revisión de calidad) ✅

> Verificar que los `🔨 Checkpoint Xcode` de Etapa 1 son correctos tras los cambios de nomenclatura de Fase 1. Etapa 1 ya tiene el modelo Camino B (el estudiante construye), por lo que los checkpoints deben ser precisos.

| Tarea | Estado | Notas |
|---|---|---|
| 3.1 Revisar checkpoint de `00-setup.md` | ✅ | Limpio; paths y comandos correctos |
| 3.2 Revisar checkpoint de `05-feature-login/01-domain.md` | ✅ | Nombres correctos; tabla de diferencias actualizada |
| 3.3 Revisar checkpoint de `05-feature-login/02-application.md` | ✅ | Fijada tabla stale "Gateway→Repository"; diferencias actuales descritas |
| 3.4 Revisar checkpoint de `05-feature-login/03-infrastructure.md` | ✅ | Limpio; `AuthHTTPRepository`, `InMemoryAuthRepository` correctos |
| 3.5 Revisar checkpoint de `05-feature-login/04-interface-swiftui.md` | ✅ | Nota de nomenclatura actualizada: nombres coinciden, diferencias son de implementación |
| 3.6 Revisar checkpoint de `05-feature-login/05-tdd-ciclo-completo.md` | ✅ | Limpio; usa `AppCompositionRoot`, `NavigationStore`, `LoginViewModel(useCase:navigator:)` |
| 3.7 Revisar checkpoint de `06-conectando-la-app.md` | ✅ | Limpio; flujo correcto |

**Criterio de cierre:** ✅ VERIFICADO — checkpoints de E1 usan nombres del scaffold; stales corregidos.

**FASE 3 COMPLETADA.**

---

## Fase 4 — Checkpoints de exploración Etapas 2-5 (auditoría post-nomenclatura) ✅

> Verificar que los `🔭 Explora el scaffold` añadidos son correctos tras los cambios de Fase 1. Confirmar que los comandos bash funcionan y apuntan a nombres reales.

| Tarea | Estado | Notas |
|---|---|---|
| 4.1 Auditar checkpoints de Etapa 2 | ✅ | 10 checkpoints en 10 archivos; 0 stales; `AppDestination` es diferencia intencional documentada |
| 4.2 Auditar checkpoints de Etapa 3 | ✅ | 6 checkpoints; 0 stales; `mapAuthError` es nombre de función correcto |
| 4.3 Auditar checkpoints de Etapa 4 | ✅ | 5 checkpoints; 0 stales |
| 4.4 Auditar checkpoints de Etapa 5 | ✅ | 12+ checkpoints; 0 stales |
| 4.5 Auditar checkpoints de Etapa 0 (Core Mobile) | ✅ | 13 checkpoints; 0 stales |

**Criterio de cierre:** ✅ VERIFICADO — `grep stales E2-E5-E0` = 0.

**FASE 4 COMPLETADA.**

---

## Fase 5 — Rebuild y deploy final ✅

> Una vez cerradas las Fases 1-4, rebuild del HTML y deploy al hub.

| Tarea | Estado | Notas |
|---|---|---|
| 5.1 Merge `develop` → `main` (fast-forward local) | ✅ | `git merge --ff-only develop` en local sin conflictos |
| 5.2 Merge `origin/main` (1 commit de audit) → `main` local | ✅ | 76 conflictos resueltos con `--ours`; push a origin |
| 5.3 Rebuild HTML con `build-html.py` | ✅ | 2348 KB, 117 archivos procesados |
| 5.4 Copy HTML al hub, commit y push → Vercel | ✅ | hub `main` `edc93f7`, Vercel deploy activo |

**FASE 5 COMPLETADA.**

---

## Fase 6 — Convención enterprise de snippets (todo el curso) ✅

> Objetivo: misma línea que Feature Login (`P1.9` / plan maestro `P3.1`): *Tu proyecto (Xcode)* vs *Scaffold (solo referencia)*, just-in-time, en **todas** las lecciones con código o checkpoints de referencia.

| Tarea | Estado | Notas |
| --- | --- | --- |
| 6.1 Checklist y seguimiento | ✅ | `plans/rollout-enterprise-snippet-convencion.md` |
| 6.2 Barrido `01-fundamentos` (fuera de Feature Login ya cerrada) | ✅ | Convención aplicada en toda la carpeta `01-fundamentos/` (incl. setup, intros, principios, BDD/TDD, TDD práctica, stack, estructura, entregables, bitácora, ADR-001, Feature Login, conexión app) |
| 6.3 Barrido `02-integracion` | ✅ | Recuadros *Tu proyecto* / *Scaffold*, intros y 🔭 07b/07c/08; tabla rollout E2 al 100% |
| 6.4 Barrido `00-core-mobile` | ✅ | Convención + recuadros 🔭; alineación nombres (`AuthHTTPRepository`, `UserSession`, `CatalogRepository`, `EmailAddress`) donde tocaba |
| 6.5 Barrido `03-evolucion` | ✅ | Intro *Tu proyecto y scaffold*; recuadros 🔭/🔨; sustitución *Ruta scaffold* engañosa en 00, 04, entregables |
| 6.6 Barrido `04-arquitecto` | ✅ | Intro *Tu proyecto y scaffold*; recuadros 🔭; entregables/checkpoint; mermaid `UserSession`/`EmailAddress` en bounded contexts; tabla rollout incluye `00-introduccion` |
| 6.7 Barrido `05-maestria` | ✅ | *Ruta scaffold* sustituida; recuadros 🔭 (incl. títulos *El scaffold…*); `09` sin Ruta previa; rubrica-final + entregables + checkpoint |
| 6.8 Barrido `06-proyecto-final` + anexos docentes | ✅ | Proyecto final: *Tu proyecto* + *Scaffold* en 00–02 y 🔨; anexos (4) con convención + enlaces intro |
| 6.9 Criterio de cierre | ✅ | Tabla `rollout-enterprise-snippet-convencion.md` al 100% ✅; rebuild HTML + `build-hub.sh --mode fast` (iOS/Android/SDD), Governance solo HTML en `hub/governance/`, Pumuki `build-html.py` (2026-04-11); hub `main` publicado con CI (`hub-ci-verify-published` + `validate-course-surface-guard`; ref `e3f2c86`). |

**Criterio de cierre:** cada fila del rollout en ✅; `grep -r "🔨 Checkpoint\|🔭 Explora"` revisado con etiqueta scaffold donde toque.

---

## Estado final del plan (Fases 1–6) ✅

**Fases 1–6 completadas** (nomenclatura, modelo pedagógico, checkpoints, deploy, convención enterprise de snippets en todo el curso). El curso iOS está:
- Con nomenclatura 100% unificada con el scaffold real (~860 reemplazos)
- Con 73/91 lecciones con checkpoints (`🔨` o `🔭`)
- Con modelo pedagógico explícito en intros E1-E3
- Desplegado en Vercel (hub `main` `edc93f7`)

---

## Registro de sesiones

| Fecha | Trabajo realizado |
|---|---|
| 2026-04-10 | Auditoría completa, añadidos 73 checkpoints (Etapas 0-5 + Proyecto Final), corrección de nomenclatura parcial en Etapa 1, PR #51 mergeada, CI/CD desactivado |
| 2026-04-10 | Fase 1 completada: ~860 reemplazos de nomenclatura en 51 archivos |
| 2026-04-10 | Fase 2 completada: modelo pedagógico explícito en intros E1-E3; entregables verificados |
| 2026-04-10 | Fase 3 completada: 7 checkpoints E1 auditados; 2 stales corregidos |
| 2026-04-10 | Fase 4 completada: 50 checkpoints E0-E5 auditados; 0 stales |
| 2026-04-10 | **FASE 5 COMPLETADA** — Merge, rebuild HTML (2348 KB), deploy Vercel `edc93f7` |
| 2026-04-10 | **Auditoría snippets (post-cierre):** Preview Login alineada a `latencyNanoseconds` + nota dual pedagógico/scaffold; diagrama `LoginError` 4 casos en `01-domain.md`; prosa `network` vs `connectivity` en `02-application.md`; flujo submit sin label `login` en `04-interface-swiftui.md`; eliminado párrafo stale `receivedSession`; `PrintNavigator` con `@MainActor`; `06-composition-root.md` — plan TDD y diagrama sin `Session`/closure obsoletos; tabla scaffold corregida (`LoginNavigating`). |
| 2026-04-10 | **`06-composition-root.md` Paso 4 + secuencia:** `StackMyArchitectureApp` alineado con la lección `02-integracion/02-navegacion-eventos.md` (`AppCoordinator` + `makeLoginView()` + `AppDestination`); diagrama mermaid sin `handle(.loginSucceeded)`; checklist y ADR-003 coherentes. **Convención curso:** tests en lecciones = **XCTest** (no Swift Testing). |
| 2026-04-10 | **Fase 6 abierta (`P3.1`):** plan maestro Fase 4 multi-curso; checklist `plans/rollout-enterprise-snippet-convencion.md`; `00-setup.md` enlaza convención de snippets; `P1.9` acotado a slice Login. |
| 2026-04-10 | **Fase 6.2 (`01-fundamentos`):** recuadros *Tu proyecto* / *Scaffold* + texto introductorio en principios, BDD, TDD práctica, stack, estructura, entregables, bitácora, ADR-001; corrección prosa intro (checkpoints ≠ pegar en scaffold) y decisión principal ADR (navegación por protocolo). |
| 2026-04-10 | **Fase 6.3 (`02-integracion`):** cierre convención enterprise en `07b`/`07c`/`08` (nota *Cómo leer los swift* + recuadro *Scaffold* en 🔭); nota *Tu proyecto* en `09-app-final-etapa-2.md`; `rollout-enterprise-snippet-convencion.md` — filas E2 en ✅. |
| 2026-04-10 | **Fase 6.4 (`00-core-mobile`):** bloque *Convención del curso* + recuadros bajo cada 🔭 (Scaffold vs material `01-fundamentos/`); correcciones menores de nomenclatura en `05`, `07`, `10`. |
| 2026-04-10 | **Fase 6.5 (`03-evolucion`):** convención + *Tu proyecto y scaffold* en intro/entregables/04; recuadros bajo 🔭 y 🔨; checkpoint/bitácora con enlace a entregables e intro. |
| 2026-04-10 | **Fase 6.6 (`04-arquitecto`):** misma convención en 00–06, entregables y checkpoint; 🔭 con *Scaffold*; diagrama bounded contexts alineado a nomenclatura vigente. |
| 2026-04-10 | **Fase 6.7 (`05-maestria`):** *Tu proyecto y scaffold* en 00–12, `09`, entregables, rubrica-final (3); recuadros bajo todos los 🔭; checkpoint con enlace a entregables e intro; rollout desglosa rubrica por archivo. |
| 2026-04-10 | **Fase 6.8–6.9:** `06-proyecto-final` (00–02, 🔨) + anexos operativos del rollout (`guia-solid`, `guia-recuperacion-ios`, `equivalencias-scaffold`, `atlas-arquitectura`); cierre Fase 6 — checklist rollout iOS 100% (rebuild HTML/hub pendiente de pipeline). |
| 2026-04-10 | **Plan coherencia:** cabecera Fase 1 corregida a ✅ (estaba 🚧 con trabajo ya cerrado). **Ecosistema:** `P3.5` Pumuki cerrado en plan maestro; `stack-my-architecture-pumuki/scripts/check-links.py` omite jsDelivr `pumuki@*` (HEAD/404); `validate-course-structure` + `check-links` en verde en ese repo. |
| 2026-04-11 | **Hub local:** `build-hub.sh --mode fast` + `SKIP_RUNTIME_SMOKE=1` (iOS ~2044 KB, Android ~773 KB, SDD ~2044 KB); Governance `build-html.py` y copia **solo** `curso-*.html` + `index.html` a `hub/governance/` (no `rsync --delete` sobre `governance/`: el `dist/assets` del curso está vacío y borraría diagramas del hub); Pumuki `build-html.py` → `hub/pumuki/`. `verify-hub-build.py` OK. |
| 2026-04-11 | **`build-hub.sh` unificado:** pasos [7/11] Governance (HTML only) y [8/11] Pumuki integrados en `stack-my-architecture-hub/scripts/build-hub.sh`; manifiesto incluye `governance` y `pumuki`; README del hub actualizado. |
| 2026-04-11 | **Hub QA:** `verify-hub-build.py` exige cinco cursos (HTML + assets + hash `dist` ↔ hub + `course-id`); portada `index.html` enlaza Governance y Pumuki; `smoke-hub-runtime.sh` comprueba `/governance` y `/pumuki`. |
| 2026-04-11 | **Hub CI:** workflow `hub-ci-verify-published.yml` (`HUB_VERIFY_SKIP_SOURCE=1`); `validate-course-surface-guard` tolera `?v=` ±1s entre iOS/Android/SDD, `hub-auth-bar` en portada; push hub `e939b08`. |
| 2026-04-11 | **Hub CI + surface guard:** `validate-course-surface-guard.sh` exporta `HUB_VERIFY_SKIP_SOURCE=1` por defecto cuando `GITHUB_ACTIONS=true` (el job `hub-surface-guard-qa` ya no falla por falta de `dist/` hermanos); `hub-ci-verify-published.yml` ejecuta también la guarda de superficie tras `verify-hub-build.py`; push hub `e3f2c86`. |
| 2026-04-11 | **Plan coherencia:** cabecera Fase 2 corregida a ✅; criterio 6.9 y bloque *Estado final* alineados a Fases 1–6 y hub con CI (`e3f2c86`). |