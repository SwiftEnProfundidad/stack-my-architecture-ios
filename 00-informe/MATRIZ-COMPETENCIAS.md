# Matriz de competencias - iOS

## Objetivo
Asegurar progresion verificable desde etapa 0 hasta maestria con evidencia ejecutable y defensa tecnica.

## Niveles y evidencias

| Nivel | Capacidad objetivo | Evidencia minima obligatoria |
| --- | --- | --- |
| Etapa 0 Core Mobile | Entender capas y semantica de dependencias | Diagrama de capas + explicacion de 4 flechas + snippet compilable |
| Etapa 1 Fundamentos | Aplicar feature-first, puertos y TDD base | Test unitario en rojo/verde + implementacion minima + refactor documentado |
| Etapa 2 Integracion | Integrar features sin acoplamiento accidental | Caso de integracion probado + diagrama de wiring + trade-off escrito |
| Etapa 3 Evolucion | Evolucionar persistencia/servicios con contratos estables | Contrato versionado + test de no regresion + metrica de impacto |
| Etapa 4 Arquitecto | Disenar fronteras, navegacion y decisiones complejas | ADR corto + diagrama inter-feature + defensa de decision |
| Etapa 5 Maestria | Operar sistema enterprise con criterios de riesgo | Runbook minimo + gates de calidad + simulacion de incidente |

## Criterio de paso
1. No se aprueba una etapa sin evidencia tecnica y defensa verbal breve.
2. Si falla un gate, la etapa queda en recuperacion y no avanza.
3. Toda evidencia debe ser reproducible en repo.

## Reglas de evaluacion
1. Comprension: explica por que la decision existe.
2. Aplicacion: demuestra con codigo o test.
3. Defensa: justifica trade-offs y riesgos.
4. Operacion: muestra como monitorear, rollback y verificar.
