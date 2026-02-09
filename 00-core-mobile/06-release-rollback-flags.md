# Release, rollback y feature flags

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

