# ETAPA 6: Rúbrica y Entrega — Proyecto Final iOS

## Objetivo de evaluación

Evaluar capacidad de entrega real en contexto enterprise: diseño, implementación, calidad, operación y defensa técnica.

No se evalúa volumen de código; se evalúa criterio más evidencia.

## Paquete obligatorio de entrega

### Código y tests

1. Código fuente de las 2 features nuevas.
2. Tests unitarios y de integración relevantes.
3. Evidencia de ejecución local en verde.

### Artefactos de arquitectura

1. Diagrama de límites y dependencias actualizado.
2. `>= 3` ADRs y `>= 1` RFC con trade-offs explícitos.
3. Contratos de puertos con su justificación.

### Operación y riesgo

1. Minimal observability spec.
2. Release checklist + plan de rollback.
3. Threat model lite + medidas de privacidad.

### Defensa técnica

1. Resumen ejecutivo de 1 página (problema, decisión, resultado).
2. Tabla before/after con métricas.
3. Guion de defensa de 5 minutos.

## Rúbrica de puntuación (100 puntos)

| Categoría | Peso | Criterio de aprobación |
|---|---:|---|
| Arquitectura y límites | 20 | Módulos claros y dependencias defendibles |
| Testing y calidad | 20 | Cobertura significativa en caminos críticos |
| Concurrencia y seguridad técnica | 15 | Aislamiento correcto, cancelación, sin data races obvias |
| Operación y observabilidad | 15 | Señales accionables, runbook útil |
| Release y mitigación | 10 | Rollout + rollback realistas |
| Seguridad y privacidad | 10 | Sin fugas de PII, mitigaciones explícitas |
| Defensa y trazabilidad | 10 | Decisiones defendibles con evidencia |

## Umbrales

1. **Aprobado Hireable**: `>= 70/100` y sin bloqueadores.
2. **Aprobado Architect Ready**: `>= 85/100`, sin bloqueadores y con mínimo `>= 75` en:
- Arquitectura y límites
- Operación y observabilidad
- Seguridad y privacidad

## Bloqueadores automáticos (No apto)

1. Ausencia de tests en caminos críticos.
2. Concurrencia insegura sin mitigación.
3. Sin plan de rollback para cambios de riesgo.
4. PII expuesta en logs/eventos.
5. Sin trazabilidad mínima (`ADRs/RFC/evidencia`).

## Checklist de validación final

- [ ] Alcance funcional mínimo cumplido.
- [ ] Build + tests en verde.
- [ ] Diagrama y contratos actualizados.
- [ ] ADRs/RFC completos.
- [ ] Observabilidad y runbook listos.
- [ ] Release/rollback definidos.
- [ ] Threat model y privacidad validados.
- [ ] Defensa de 5 minutos ensayada.

## Entrega recomendada (formato)

1. Repositorio/branch con código y tests.
2. Carpeta `docs/final-project/` con evidencias.
3. Documento `DEFENSA.md` con:
- problema y contexto,
- decisiones clave,
- trade-offs,
- resultados y métricas,
- riesgos abiertos y próximos pasos.

## Preguntas de defensa (debes poder responder)

1. ¿Qué invariante protegiste y cómo lo demuestras?
2. ¿Qué trade-off principal aceptaste y por qué?
3. ¿Cómo fallaría el sistema y qué harías en los primeros 15 minutos?
4. ¿Qué parte sería más cara de mantener a 12 meses?
5. ¿Qué automatizarías siguiente para reducir riesgo operativo?

## Cierre de etapa

Cuando completes esta rúbrica, actualiza también los entregables de maestría para dejar la trazabilidad completa de salida:

- [`../05-maestria/entregables-etapa-5.md`](../05-maestria/entregables-etapa-5.md)

## 🔨 Checkpoint Xcode — Lista de verificación de entrega

```bash
# Ejecuta todos los gates antes de entregar
cd apps/ios/ArchitectureKit

# Gate 1: Dependencias
grep -rn "^import SwiftUI\|^import UIKit" Sources/FeatureLoginDomain Sources/FeatureCatalogDomain 2>/dev/null || echo "✅ Gate 1: Domain puro"

# Gate 2: Tests unitarios
swift test 2>&1 | tail -5

# Gate 5: Swift 6 strict concurrency
swift build 2>&1 | grep -c "error:" || echo "✅ Gate 5: Sin errores de concurrencia"
```

Ejecuta estos tres comandos y adjunta la salida en tu entrega. Si los tres terminan sin errores, tu proyecto cumple los requisitos técnicos mínimos de la rúbrica.
