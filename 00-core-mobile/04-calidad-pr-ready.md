# Calidad PR-ready

## Modelo mental

Una PR es una propuesta de cambio al sistema de producción. Trátala como un contrato: el autor propone, la evidencia respalda, el reviewer valida. Si la evidencia no convence a alguien que no escribió el código, la PR no está lista.

## Ejemplo en el scaffold

En `ArchitectureKit`, cada cambio en Domain o Data se valida con `swift test` (26 tests) y `./scripts/quality-gates.sh` (cobertura Domain ≥ 85%, Data ≥ 75%). Antes de mergear, el autor verifica que `./scripts/check-dependencies.sh` pasa (no hay imports prohibidos entre módulos). Este flujo se practica en la Etapa 4 (`04-arquitecto/06-quality-gates.md`).

## Cuándo sí / cuándo no

Aplica esta disciplina a toda PR que toque código de producción o tests. No la apliques a cambios puramente documentales (typos en README) ni a spikes exploratorios que se descartarán.

## Production readiness a nivel Pull Request

Una PR está lista cuando su evidencia supera opinión personal. Eso exige build estable, pruebas relevantes, observabilidad mínima y seguridad básica revisada.

## Checklist de PR-ready

- [ ] Problema y alcance definidos en la PR.
- [ ] Cambios limitados y trazables.
- [ ] Build local y CI en verde.
- [ ] Tests unitarios/integración/contrato según impacto.
- [ ] Casos borde y fallos esperables cubiertos.
- [ ] Logs/métricas para diagnóstico del cambio.
- [ ] Seguridad/privacidad revisadas (PII, secretos, permisos).
- [ ] Plan de rollback o mitigación documentado.

## Definition of Done template

Estado funcional esperado:

Evidencia técnica adjunta:

Riesgos conocidos:

Mitigación en release:

## Matriz de estrategia de testing

| Tipo | Objetivo | Cuándo usar | Evidencia mínima |
|---|---|---|---|
| Unit | Reglas y lógica | Siempre | Suite rápida estable |
| Integration | Wiring real | Cambios entre capas | Tests de colaboración |
| Contract | Acuerdos entre módulos/API | Cambios de contrato | Validación productor/consumidor |
| E2E | Flujos críticos de negocio | Caminos top | Casos críticos automatizados |
| Performance | Regresión de latencia/startup/memoria | Cambios sensibles | Baseline + comparación |
| Accessibility | Uso con ayudas y semántica | UI relevante | Checklist + tests donde aplique |

Regla central: evidence over opinion.

---

<!-- auto-gapfix:layered-mermaid -->
## Diagrama de arquitectura por capas

```mermaid
flowchart LR
  subgraph CORE["Core / Domain"]
    direction TB
    ENT[Entity]
    POL[Policy]
  end

  subgraph APP["Application"]
    direction TB
    BOOT[Composition Root]
    UC[UseCase]
    PORT["FeaturePort (contrato)"]
  end

  subgraph UI["Interface"]
    direction TB
    VM[ViewModel]
    VIEW[View]
  end

  subgraph INFRA["Infrastructure"]
    direction TB
    API[API Client]
    STORE[Persistence Adapter]
  end

  VM --> UC
  UC --> ENT
  UC ==> PORT
  BOOT -.-> PORT
  BOOT -.-> API
  BOOT -.-> STORE
  PORT --o API
  PORT --o STORE
  UC --o VM

  style CORE fill:#0f2338,stroke:#63a4ff,color:#dbeafe,stroke-width:2px
  style APP fill:#2a1f15,stroke:#fb923c,color:#ffedd5,stroke-width:2px
  style UI fill:#14262f,stroke:#93c5fd,color:#e0f2fe,stroke-width:2px
  style INFRA fill:#2a1d34,stroke:#c084fc,color:#f3e8ff,stroke-width:2px

  linkStyle 0 stroke:#f472b6,stroke-width:2.6px
  linkStyle 1 stroke:#f472b6,stroke-width:2.6px
  linkStyle 2 stroke:#60a5fa,stroke-width:2.8px
  linkStyle 3 stroke:#94a3b8,stroke-width:2px,stroke-dasharray:6 4
  linkStyle 4 stroke:#94a3b8,stroke-width:2px,stroke-dasharray:6 4
  linkStyle 5 stroke:#94a3b8,stroke-width:2px,stroke-dasharray:6 4
  linkStyle 6 stroke:#86efac,stroke-width:2.6px
  linkStyle 7 stroke:#86efac,stroke-width:2.6px
  linkStyle 8 stroke:#86efac,stroke-width:2.6px
```

La lectura del diagrama sigue esta semantica:
1. `-->` dependencia directa en runtime.
2. `-.->` wiring o configuracion.
3. `==>` contrato o abstraccion.
4. `--o` salida o propagacion de resultado.
