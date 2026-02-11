## Resumen

<!-- Explica qué cambia y por qué (en 3-6 líneas). -->

## Tipo de cambio

- [ ] Feature
- [ ] Fix
- [ ] Refactor
- [ ] Docs
- [ ] CI/Tooling

## Scope

- [ ] iOS ArchitectureKit (`apps/ios/ArchitectureKit`)
- [ ] Host App UI smoke (`apps/ios/ArchitectureHostApp`)
- [ ] Assistant panel / bridge
- [ ] Docs / ADR / roadmap

## Checklist de arquitectura

- [ ] Se respetan reglas de dependencia por capas/features
- [ ] Navegación desacoplada (contrato) mantenida o extendida con tests
- [ ] Contratos `Repository` no filtran detalles de infraestructura
- [ ] Si cambió una decisión técnica, ADR añadida/actualizada en `docs/adr/`

## Checklist de calidad

- [ ] `./apps/ios/ArchitectureKit/scripts/quality-gates.sh` pasa en local
- [ ] Si aplica, `RUN_UI_SMOKE=1 ./apps/ios/ArchitectureKit/scripts/quality-gates.sh`
- [ ] Cobertura mínima respetada (Domain >= 85%, Data >= 75%)
- [ ] No se añadieron artefactos temporales (`.xcresult`, `artifacts/`, `.build/`)

## Evidencia

<!-- Pega salida corta de gates o links a artifacts del workflow. -->

## Riesgos / rollout

<!-- Riesgos conocidos, mitigaciones y cómo revertir. -->

