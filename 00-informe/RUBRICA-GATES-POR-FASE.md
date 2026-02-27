# Rubrica de gates por fase - iOS

## Objetivo
Definir criterios de aprobado/rechazado por fase para evitar avance con huecos.

## Gates por fase

| Fase | Gate tecnico | Gate pedagogico | Gate de defensa |
| --- | --- | --- | --- |
| Etapa 0 | Diagrama de capas correcto | Explica significado de las flechas | Justifica una dependencia valida y una invalida |
| Etapa 1 | TDD rojo-verde-refactor completo | Explica por que el test protege el comportamiento | Defiende por que no usar acoplamiento directo |
| Etapa 2 | Integracion de features en verde | Describe contrato entre modulos | Defiende trade-off entre simplicidad y aislamiento |
| Etapa 3 | Persistencia/infra con tests de regresion | Explica impacto en dominio | Defiende costo de cambio y estrategia de migracion |
| Etapa 4 | Arquitectura y navegacion sin ciclos | Describe fronteras y ownership | Defiende ADR con criterios de riesgo |
| Etapa 5 | Hardening/release checklist en verde | Explica criterio de readiness | Defiende plan de rollback y observabilidad |

## Regla de aprobado
1. Se aprueba fase solo con los tres gates en verde.
2. Si un gate falla, se registra recuperacion y evidencia faltante.
3. Todo gate debe poder auditarse en PR o script.

## Evidencia de recuperacion
1. Causa del fallo.
2. Cambio aplicado.
3. Prueba de cierre.
4. Leccion aprendida.
