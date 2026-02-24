# PHASE TRACKER — Auditoría y Reestructuración Curso iOS

## Leyenda
- ✅ Hecho
- 🚧 En construccion (maximo 1)
- ⏳ Pendiente
- ⛔ Bloqueado

## Fase 0 — Baseline y Marco de Auditoría
- ✅ Inventario de estructura global del curso (`00-core-mobile` a `05-maestria`, `anexos`, `00-informe`)
- ✅ Identificación de punto de generación HTML y navegación (`scripts/build-html.py`)
- ✅ Definir y materializar matriz de auditoría ejecutable (curso + scaffold)

## Fase 1 — Reestructuración de Navegación y Sidebar
- ✅ Implementar sidebar por etapa con formato: `ETAPA X: <ROL>` + `Lección N: <Título>`
- ✅ Garantizar numeración estable por etapa basada en `FILE_ORDER`
- ✅ Verificar navegación `Anterior/Siguiente` y enlaces internos de lecciones
- ✅ Validar comportamiento móvil/desktop del menú lateral en HTML generado

## Fase 2 — Auditoría Pedagógica Profunda (Prioridad Alta)
- ✅ Auditar continuidad didáctica lección a lección por cada etapa
- ✅ Detectar saltos de complejidad, prerequisitos implícitos y redundancias
- ✅ Normalizar plantilla pedagógica mínima por lección (objetivo, prerequisitos, práctica, validación)
- ✅ Registrar hallazgos con severidad (P0/P1/P2/P3) y propuesta de corrección

## Fase 3 — Auditoría Técnica Profunda (Mermaid + Snippets + Scaffold)
- ✅ Auditar coherencia semántica de diagramas Mermaid con la narrativa
- ✅ Auditar snippets (consistencia, validez conceptual, nomenclatura, capas)
- ✅ Trazar snippets/diagramas críticos contra rutas reales del scaffold (`apps/ios/...`)
- ✅ Etiquetar explícitamente snippets pedagógicos no literales

## Fase 4 — Corrección y Reorganización del Contenido
- ✅ Reordenar lecciones/contenido cuando la secuencia pedagógica lo requiera
- ✅ Corregir inconsistencias de mermaid, snippets y explicaciones técnicas
- ✅ Ajustar enlaces cruzados y referencias entre etapas/anexos
- ✅ Revalidar artefactos de cierre por etapa (entregables/rúbricas/checklists)

## Fase 5 — QA Integral y Cierre por Olas
- ✅ Ejecutar QA completo por etapa (100% checklist de cierre)
- ✅ Regenerar HTML y validar navegación/UX final
- ✅ Emitir informe final consolidado (hallazgos, correcciones, backlog residual)
- ✅ Definir guardrails de regresión para futuras ediciones del curso

## Fase 6 — Mantenimiento de Pipeline
- ✅ Primera task: validación automática de enlaces/anchors en pipeline de publicación (`.github/workflows/course-qa-audit.yml` + `scripts/run-qa-audit-bundle.sh` + `scripts/audit-cross-links.py`)
- ✅ Segunda task: revisión visual trimestral de Mermaid/assets en el HTML final (`00-informe/AUDITORIA-REVISION-VISUAL-TRIMESTRAL-2026Q1.md`)

## Nota operativa de cierre
- Bundle QA estable y reproducible: `./scripts/run-qa-audit-bundle.sh`.
- Guardrails activos con baseline: `00-informe/AUDITORIA-GUARDRAILS-BASELINE.json`.
- Estado actual: sin pendientes `P1` en controles priorizados; backlog residual en `P2` para ola de refinamiento.
