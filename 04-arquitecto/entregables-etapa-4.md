# Entregables — Etapa 4: Arquitecto

## Lo que has construido en esta etapa

La Etapa 4 no añade una feature nueva para el usuario final. Añade algo más importante para escalar: **plataforma, gobernanza y reglas de calidad**.

En palabras simples:

- antes construías pantallas y casos de uso,
- ahora construyes el sistema que evita que esas pantallas se conviertan en caos cuando el equipo crece.

---

## Artefactos documentales de la etapa

```text
04-arquitecto/
  00-introduccion.md            ← objetivo, alcance y riesgos de la etapa
  01-bounded-contexts.md        ← context map, ownership y límites semánticos
  02-reglas-dependencia-ci.md   ← reglas arquitectónicas + enforcement en CI
  03-navegacion-deeplinks.md    ← navegación de plataforma y deep links
  04-versionado-spm.md          ← estrategia de modularización y versionado
  05-guia-arquitectura.md       ← convenciones operativas del repositorio
  06-quality-gates.md           ← gates 0..6, severidad, pipeline y excepciones
  entregables-etapa-4.md        ← cierre verificable de etapa
```

---

## Artefactos técnicos esperados (según decisiones de etapa)

> Nota: algunos artefactos son blueprint conceptual y pueden implementarse en la siguiente iteración técnica.

### 1) Gobernanza de bounded contexts

- Documento de context map con relaciones entre `Identity`, `Catalog` y contextos futuros.
- Ownership explícito por contexto.
- Reglas para cuándo usar Shared Kernel y cuándo usar ACL.

### 2) Reglas de dependencia automatizadas

Artefactos esperados:

```text
scripts/check-domain-imports.sh
scripts/check-feature-imports.sh
scripts/check-architecture-rules.sh
.github/workflows/quality-gates.yml
```

### 3) Navegación y deep links como plataforma

Artefactos esperados:

```text
StackMyArchitecture/App/Navigation/DeepLinkParser.swift
StackMyArchitectureTests/App/Navigation/DeepLinkParserTests.swift
StackMyArchitectureTests/App/Navigation/DeepLinkCoordinatorTests.swift
```

### 4) Versionado y SPM

Artefactos esperados:

```text
docs/versioning/semver-policy.md
docs/versioning/deprecation-policy.md
Packages/ (cuando se active la separación por trigger)
```

### 5) Guía de arquitectura y quality gates

Artefactos esperados:

```text
docs/architecture/context-map.md
docs/architecture/dependency-rules.md
docs/quality-gates.md
anexos/adrs/ADR-EXCEPTION-*.md (si aplica)
```

---

## Criterios de aceptación de la etapa (DoD)

La etapa se considera completada si se cumple todo esto:

- [ ] Existe context map con límites semánticos y ownership definidos.
- [ ] Hay reglas de dependencia explícitas y automatizables.
- [ ] El pipeline contempla gates arquitectónicos antes de tests caros.
- [ ] Hay estrategia de versionado con triggers de migración (no por moda).
- [ ] Existe proceso formal de excepción con ADR temporal.
- [ ] Navegación/deep links están definidos como plataforma (no lógica ad-hoc en vistas).
- [ ] Quality gates documentados: Gate 0..6 con severidad por tipo de PR/release.

---

## Matriz de validación rápida

| Área | Evidencia mínima | Estado esperado |
| --- | --- | --- |
| Contextos | `01-bounded-contexts.md` + ownership | Aprobado |
| Dependencias | `02-reglas-dependencia-ci.md` + scripts/checks | Aprobado |
| Navegación | `03-navegacion-deeplinks.md` + parser/tests | Aprobado |
| Versionado | `04-versionado-spm.md` + política semver | Aprobado |
| Guía repo | `05-guia-arquitectura.md` | Aprobado |
| Gates | `06-quality-gates.md` + flujo CI | Aprobado |

---

## Métricas acumuladas del curso (cierre etapa 4)

### Métricas verificadas en documentos del curso

- Etapas completas: 4 (Fundamentos, Integración, Evolución, Arquitecto).
- Features operativas construidas: 2 (`Login`, `Catalog`).
- Cobertura cualitativa: Domain/Application/Infrastructure/Interface en ambos dominios.

### Métricas exactas numéricas

- Número exacto de tests ejecutables en repo real: **N/D** en este documento.
- Tiempo exacto de pipeline CI real: **N/D** en este documento.

Cómo confirmarlo:

1. Ejecutar suite en entorno real de proyecto.
2. Exportar reporte de test runner/CI.
3. Actualizar tabla con números de la ejecución más reciente.

---

## Competencias demostradas al cerrar la etapa

- Diseñar límites de contexto con lenguaje ubicuo y ownership claro.
- Traducir decisiones arquitectónicas a reglas verificables.
- Definir quality gates proporcionales al riesgo (no burocracia vacía).
- Tomar decisiones de modularización con trade-offs A/B/C y triggers objetivos.
- Gestionar excepciones sin destruir gobernanza (ADR + fecha de retirada).

---

## Riesgos residuales al cierre

### Riesgo 1: arquitectura bien documentada pero sin enforcement técnico completo

Mitigación:

- priorizar implementación de scripts/checks de dependencia en siguiente iteración.

### Riesgo 2: gates definidos pero no calibrados al tiempo real del equipo

Mitigación:

- medir duración de pipeline por gate y ajustar orden/paralelización.

### Riesgo 3: excepción permanente disfrazada de “temporal”

Mitigación:

- no aceptar excepción sin fecha de expiración y ticket de remediación.

---

## Siguiente iteración recomendada

1. Convertir gates conceptuales en scripts/workflows ejecutables.
2. Ejecutar piloto con una feature nueva bajo gobernanza completa.
3. Medir fricción real (tiempo CI, fallos por gate, lead time PR) y recalibrar.

---

**Anterior:** [Quality Gates ←](06-quality-gates.md)
