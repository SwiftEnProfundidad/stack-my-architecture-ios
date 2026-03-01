# Scorecard de empleabilidad - iOS

## Objetivo
Mapear cada fase a competencias observables en entrevista y en portfolio tecnico.

## Seniority map

| Nivel | Senal en entrevista | Evidencia portfolio | Riesgo si falta |
| --- | --- | --- | --- |
| Junior | Explica capas y flujo basico | Feature pequena con tests base | Respuestas memorizadas sin criterio |
| Mid | Argumenta contratos y boundaries | Integracion de dos features desacopladas | Acoplamiento accidental en cambios |
| Senior | Decide con trade-offs y metricas | ADR + evidencia de evolucion segura | Decisiones por intuicion sin datos |
| Arquitecto | Coordina modulos y roadmap tecnico | Diagrama global + plan de migracion | Arquitectura no defendible ante staff |
| Maestria | Opera bajo riesgo y release real | Runbook + quality gates + rollback | Falta de criterio operativo en produccion |

## Criterio de empleabilidad
1. Cada nivel exige al menos una evidencia ejecutable.
2. Cada evidencia debe incluir defensa de decision.
3. La defensa debe cubrir alternativa descartada y riesgo asumido.

## Checklist de defensa tecnica
- Problema y contexto
- Invariantes
- Opciones evaluadas
- Decision final
- Riesgo y mitigacion
- Como validar en runtime
