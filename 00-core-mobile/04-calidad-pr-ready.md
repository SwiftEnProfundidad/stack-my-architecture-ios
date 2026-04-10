# Calidad PR-ready

## Modelo mental

Una PR es una propuesta de cambio al sistema de producción. Trátala como un contrato: el autor propone, la evidencia respalda, el reviewer valida. Si la evidencia no convence a alguien que no escribió el código, la PR no está lista.

## Ejemplo en el scaffold

En `ArchitectureKit`, cada cambio en Domain o Data se valida con `swift test` (26 tests), con umbrales de cobertura de Domain ≥ 85% y Data ≥ 75%. Antes de mergear, el autor verifica que no hay imports prohibidos entre módulos (por ejemplo, Domain no puede importar Infrastructure). Este flujo se practica y formaliza en [Quality Gates — Etapa 4](../04-arquitecto/06-quality-gates.md).

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

Usa esta plantilla como campo de texto en tu PR o ticket. Rellénala antes de marcar la PR como lista para review:

**Estado funcional esperado:**

**Evidencia técnica adjunta:**

**Riesgos conocidos:**

**Mitigación en release:**

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



## 🔭 Explora el scaffold — Los quality gates del scaffold

```bash
# Gate de dependencias: Domain no importa infraestructura
grep -rn "^import" apps/ios/ArchitectureKit/Sources/FeatureLoginDomain/ | grep -v "Foundation\|Testing" || echo "✅ Domain puro"

# Gate de tests: todos los tests en verde
cd apps/ios/ArchitectureKit && swift test 2>&1 | tail -3
```

Estos dos comandos son los gates de PR mínimos del scaffold: dependencias limpias y tests en verde. Si los dos pasan, el código es PR-ready según los criterios de esta lección.

---

## Qué sigue

Con los criterios de PR-ready interiorizados, el siguiente paso es asegurarte de que el sistema en producción es observable: qué pasa cuando algo falla y cómo lo detectas. Eso lo cubre la siguiente lección.
