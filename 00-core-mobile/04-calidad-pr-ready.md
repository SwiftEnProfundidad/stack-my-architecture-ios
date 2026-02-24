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

**Anterior:** [Variabilidad y evolución sin caos ←](03-variabilidad-y-evolucion.md) · **Siguiente:** [Observabilidad y operación →](05-observabilidad-operacion.md)
