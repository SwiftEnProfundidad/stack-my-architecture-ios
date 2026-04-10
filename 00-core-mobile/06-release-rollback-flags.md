# Release, rollback y feature flags

## Modelo mental

Un release es como abrir una compuerta: una vez que el agua fluye, no puedes recogerla fácilmente. En mobile, el rollback es especialmente difícil porque dependes de que los usuarios actualicen. Por eso necesitas dos mecanismos: staged rollout (abrir la compuerta poco a poco) y feature flags (poder cerrar una tubería específica sin cerrar toda la compuerta).

## Ejemplo en el scaffold

En `ArchitectureKit`, la Etapa 4 define gates que deben pasar antes de release: `swift test`, validación de dependencias y baseline de performance. Si algún gate falla, el release se bloquea. Los feature flags no están implementados en el scaffold actual, pero la arquitectura los soporta: el `AppComposition` puede inyectar implementaciones distintas según configuración remota sin tocar Domain. El flujo completo de quality gates se detalla en [Quality Gates — Etapa 4](../04-arquitecto/06-quality-gates.md).

## Cuándo sí / cuándo no

Usa staged rollout siempre que el cambio afecte a flujos críticos de usuario. Usa feature flags cuando necesites activar/desactivar funcionalidad sin deploy. No uses flags para todo: cada flag es deuda temporal que necesita owner y fecha de retiro.

## Estrategias de release

Prioriza despliegues graduales: staged rollout, canary o phased rollout según plataforma/canal. El objetivo es reducir blast radius y aprender pronto.

## Rollback en mobile

El rollback de app tiene limitaciones por adopción de versiones y stores. Por eso debes diseñar mitigaciones server-side y flags para desactivar rutas de riesgo sin esperar a que toda la base actualice.

## Feature flags

Un flag es deuda temporal con fecha de caducidad. Cada flag debe tener owner, propósito, criterio de retiro y kill-switch asociado para incidentes graves.

Evita flags permanentes sin gobierno, porque añaden complejidad oculta.

## Kill-switch

Diseña kill-switch para desactivar funciones críticas con seguridad, auditabilidad y latencia de propagación conocida.

## Release readiness checklist

- [ ] Scope de release cerrado y trazable.
- [ ] Riesgos críticos identificados.
- [ ] Plan de rollback y mitigación server-side.
- [ ] Flags nuevas con owner y fecha de expiración.
- [ ] Kill-switch validado en entorno controlado.
- [ ] Monitoreo reforzado para ventana de lanzamiento.
- [ ] Comunicación de release preparada.


## 🔭 Explora el scaffold — Feature flags en Infrastructure

```bash
# Busca cualquier feature flag o toggle en el scaffold
grep -rn "featureFlag\|FeatureFlag\|isEnabled\|toggle" apps/ios/ArchitectureKit/Sources/ 2>/dev/null || echo "No hay feature flags aún — son una extensión natural del scaffold"
```

El scaffold actual no implementa feature flags — eso es deliberado para el nivel Junior/Mid. Cuando llegues a Etapa 3 (Senior), añadirás un mecanismo de flags sobre `InfraPersistence` sin tocar Domain ni Application.

---

## Qué sigue

Con release, rollback y feature flags en tu toolkit, el siguiente paso es gestionar los contratos que definen cómo se comunican los componentes de tu sistema: APIs, versionado y estabilidad de interfaces.

