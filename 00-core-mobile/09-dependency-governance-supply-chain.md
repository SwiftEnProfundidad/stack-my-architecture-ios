# Dependency governance y supply chain

## Modelo mental

Las dependencias son como proveedores externos de tu empresa: cada uno que añades te da capacidad, pero también te expone a su ritmo de cambio, sus bugs y su posible abandono. La gobernanza de dependencias es decidir conscientemente qué proveedores aceptas, bajo qué condiciones y con qué plan de salida.

## Ejemplo en el scaffold

En `ArchitectureKit`, el `Package.swift` define explícitamente qué targets pueden importar qué. `FeatureLoginDomain` solo depende de `CoreDomain`; nunca de `InfraHTTP` ni de `FeatureCatalogDomain`. Si alguien añade un `import InfraHTTP` dentro de `FeatureLoginDomain`, el gate de build falla. Consulta la [estrategia completa de reglas de dependencia en CI](../04-arquitecto/02-reglas-dependencia-ci.md) en la Etapa 4 (Arquitecto). El scaffold de referencia está en `ArchitectureKit/Package.swift` en la raíz del repositorio del curso.

## Cuándo sí / cuándo no

Aplica gobernanza de dependencias desde que tienes más de 3 módulos SPM o más de una dependencia externa: a partir de ese punto, el compilador ya no puede impedirte importar lo que no debes, necesitas reglas explícitas. No la apliques a proyectos de un solo target donde el compilador ya controla todo.

## Reglas de dependencia modular

Define direcciones permitidas y prohibidas entre módulos. Las reglas deben ser ejecutables (lint/build checks) para evitar que la arquitectura dependa de disciplina manual.

Ejemplo en `Package.swift`:
- `FeatureLoginDomain` → puede importar `CoreDomain` ✓
- `FeatureLoginDomain` → no puede importar `InfraHTTP` ✗
- `FeatureLoginDomain` → no puede importar `FeatureCatalogDomain` ✗

Si una regla solo existe en un documento pero no hay un gate que la verifique, no es una regla: es un deseo.

## Política de upgrades

Establece cadencia de actualización según el tipo de dependencia: mensual para dependencias de infraestructura activa (SDKs de red, analítica, auth); trimestral para dependencias estables de bajo riesgo.

Prioriza upgrades por riesgo: (1) vulnerabilidad conocida → inmediato, (2) breaking change en dependencia crítica → siguiente sprint, (3) mejora menor → cadencia normal.

Gates de validación antes de mergear un upgrade: build limpio, tests en verde, sin regresión de performance medible, sin nuevos permisos o capacidades no justificados.

Cada upgrade de dependencia crítica debe incluir plan de rollback explícito: versión anterior pineada en `Package.swift`, con procedimiento documentado de cómo revertir si el upgrade introduce un defecto en producción.

## Supply chain basics

En iOS con SPM, `Package.resolved` actúa como lockfile: fija versiones exactas y checksums de cada dependencia. Commitea siempre `Package.resolved` al repositorio para garantizar builds reproducibles. SPM verifica checksums automáticamente al resolver; no requiere configuración adicional.

Antes de introducir cualquier SDK externo, justifica: qué problema resuelve que no puedes resolver con código propio en menos de una semana, qué riesgo añade (mantenimiento, superficie de ataque, licencia) y cuál es la estrategia de salida si el SDK queda abandonado o introduce una vulnerabilidad.

La [lección anterior sobre threat modeling](08-seguridad-privacidad-threat-modeling.md) incluye "SDK de terceros mal configurado" como actor de amenaza. La gobernanza de supply chain es el control que mitiga ese riesgo.

## Dependency Governance Rules checklist

- [ ] Mapa de módulos y direcciones permitidas actualizado.
- [ ] Imports prohibidos definidos y chequeados.
- [ ] Política de versiones/upgrade publicada.
- [ ] Gates de upgrade definidos (test/perf/security).
- [ ] Plan de rollback por dependencia crítica.
- [ ] Inventario de dependencias con owner.
- [ ] Revisión periódica de dependencias huérfanas.


## 🔭 Explora el scaffold — Dependencias del Package.swift

```bash
# El scaffold tiene cero dependencias externas de terceros
grep "\.package(url:" apps/ios/ArchitectureKit/Package.swift || echo "✅ Sin dependencias de terceros — solo SPM local"

# Todas las dependencias son targets internos del mismo paquete
grep "dependencies:" apps/ios/ArchitectureKit/Package.swift | head -10
```

El scaffold no tiene ninguna dependencia externa de terceros. Esa es una decisión de gobernanza deliberada: minimizar la superficie de supply chain desde el inicio. Cuando se añada una dependencia real, deberá justificarse en un ADR.

---

## Qué sigue

La siguiente lección, [Plantillas operativas](10-plantillas.md), reúne ADR, RFC, PR checklist, DoD y el threat model en un único documento de referencia con ejemplos reales. Es el punto de síntesis de todo lo aprendido en Core Mobile.
