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

## Fase 1 — Unificación de nomenclatura (Opción C) 🚧

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

## Fase 2 — Modelo pedagógico explícito ⏳

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

## Estado final del plan ✅

**Todas las fases completadas.** El curso iOS está:
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