#!/usr/bin/env python3
"""
Expande los ADRs stub del curso iOS con contenido completo siguiendo el template.

Uso:
    python3 scripts/expand-adrs-ios.py

El script lee cada ADR-00{3..14}*.md (excepto ADR-003 y ADR-004 ya expandidos)
y genera contenido completo (~50-70 lineas) manteniendo la decisión original.
"""

import re
from pathlib import Path

COURSE_ROOT = Path(__file__).parent.parent
ADRS_DIR = COURSE_ROOT / "anexos" / "adrs"

# Mapeo de ADR a información contextual
ADR_DATA = {
    "ADR-005": {
        "title": "Contratos entre features por eventos/modelos mínimos",
        "context": "Etapa 2 - Integración / Lección: Contratos entre features",
        "lesson": "../02-integracion/03-contratos-features.md",
        "problem": "Integración entre Login y Catalog sin invadir internals de cada uno.",
        "decision": "Compartir solo contratos públicos mínimos (eventos/tipos), nunca clases internas.",
        "option_a": "Shared Kernel grande con todo compartido",
        "option_b": "Import directo de implementaciones entre features",
        "consequences_pos": "Evolución segura por feature, menor riesgo de cascada de cambios",
        "consequences_neg": "Más archivos de contratos que mantener",
        "risks": "Tentación de compartir demasiado; requiere disciplina en code reviews"
    },
    "ADR-006": {
        "title": "Infraestructura real mínima con URLSessionHTTPClient",
        "context": "Etapa 2 - Integración / Lección: Infra real network",
        "lesson": "../02-integracion/04-infra-real-network.md",
        "problem": "Conectar con red real manteniendo límites de Clean Architecture.",
        "decision": "Introducir HTTPClient como puerto e implementar URLSessionHTTPClient en Infrastructure.",
        "option_a": "Usar Alamofire directamente en Application layer",
        "option_b": "Crear wrapper propio complejo sobre URLSession",
        "consequences_pos": "Tests de contrato en infra, dominio limpio, reemplazo futuro sin tocar core",
        "consequences_neg": "Más código inicial que usar Alamofire directo",
        "risks": "Tentación de exponer detalles HTTP en Domain; requiere mapeo de errores"
    },
    "ADR-007": {
        "title": "Estrategia de cache network-first + TTL + fallback",
        "context": "Etapa 3 - Evolución / Lección: Caching offline",
        "lesson": "../03-evolucion/01-caching-offline.md",
        "problem": "Mejorar resiliencia sin mentir con datos obsoletos.",
        "decision": "Intentar remoto primero; usar cache solo ante fallo y si TTL válido.",
        "option_a": "Cache-first (rápido pero posiblemente obsoleto)",
        "option_b": "Siempre remoto (fresco pero lento y frágil)",
        "consequences_pos": "UX robusta en mala red, control explícito de frescura",
        "consequences_neg": "Primera carga siempre requiere red; implementación más compleja",
        "risks": "TTL mal configurado puede servir datos muy viejos; requiere tuning"
    },
    "ADR-008": {
        "title": "Política explícita de consistencia e invalidación",
        "context": "Etapa 3 - Evolución / Lección: Consistencia",
        "lesson": "../03-evolucion/02-consistencia.md",
        "problem": "Cache sin política produce comportamientos ambiguos y bugs difíciles.",
        "decision": "Definir reglas de frescura/invalidación testeables y documentadas.",
        "option_a": "Invalidación manual por el desarrollador cuando cree conveniente",
        "option_b": "Sin invalidación, siempre confiar en TTL",
        "consequences_pos": "Decisiones previsibles, menor deuda operativa, debugging más rápido",
        "consequences_neg": "Más código de gestión de estado; complejidad adicional",
        "risks": "Política demasiado agresiva puede invalidar innecesariamente; muy laxa puede servir datos obsoletos"
    },
    "ADR-009": {
        "title": "Observabilidad por decoradores y logger de aplicación",
        "context": "Etapa 3 - Evolución / Lección: Observabilidad",
        "lesson": "../03-evolucion/03-observabilidad.md",
        "problem": "Incidentes sin trazas útiles frenan diagnóstico de flujos async.",
        "decision": "Añadir logging/tracing en infraestructura mediante decoradores y puerto de logger.",
        "option_a": "Loggear directamente con print/os_log desde cualquier lugar",
        "option_b": "Usar SDK completo de terceros (Firebase, Datadog) en todo el código",
        "consequences_pos": "Mejor diagnóstico sin contaminar Domain/Application con SDKs concretos",
        "consequences_neg": "Overhead de los decoradores; más código boilerplate",
        "risks": "Logging excesivo puede impactar performance; logging insuficiente no ayuda en debugging"
    },
    "ADR-010": {
        "title": "Firebase como backend principal encapsulado",
        "context": "Etapa 3 - Evolución / Lección: Backend Firebase",
        "lesson": "../03-evolucion/07-backend-firebase.md",
        "problem": "Curso requiere backend gratuito, integrable y didáctico para Auth + datos.",
        "decision": "Adoptar Firebase Auth + Firestore encapsulados en Infrastructure.",
        "option_a": "Crear backend propio (requiere servidor, más complejo para el curso)",
        "option_b": "Usar mock estático sin backend real (no demuestra integración real)",
        "consequences_pos": "Arranque rápido del alumno, separación limpia de capas, tests de integración guiados",
        "consequences_neg": "Vendor lock-in a Firebase; dependencia de servicio externo",
        "risks": "Cambios en APIs de Firebase pueden romper ejemplos; requiere mantenimiento de versiones"
    },
    "ADR-011": {
        "title": "Bounded contexts con ownership y contratos",
        "context": "Etapa 4 - Arquitecto / Lección: Bounded contexts",
        "lesson": "../04-arquitecto/01-bounded-contexts.md",
        "problem": "Escalado por equipos necesita límites semánticos explícitos.",
        "decision": "Definir contextos (Identity, Catalog, etc.) con ownership, contratos y reglas de cambio.",
        "option_a": "Monolito sin límites claros (rápido al inicio, caos al crecer)",
        "option_b": "Microservicios desde día 1 (overkill para el curso, complejidad innecesaria)",
        "consequences_pos": "Menos fricción entre equipos, menor acoplamiento accidental",
        "consequences_neg": "Overhead de definir y mantener contratos entre contextos",
        "risks": "Bounded contexts mal definidos pueden crear más fricción; requiere experiencia en DDD"
    },
    "ADR-012": {
        "title": "Reglas de dependencia progresivas",
        "context": "Etapa 4 - Arquitecto / Lección: Reglas dependencia CI",
        "lesson": "../04-arquitecto/02-reglas-dependencia-ci.md",
        "problem": "Las reglas arquitectónicas solo en texto no evitan regresiones.",
        "decision": "Aplicar enforcement progresivo: convención documentada -> scripts -> modularización estricta.",
        "option_a": "Solo documentación (ignorada fácilmente)",
        "option_b": "Modularización estricta desde día 1 (lento, fricción para el alumno)",
        "consequences_pos": "Control sostenible sin sobrerregular etapas tempranas",
        "consequences_neg": "Período intermedio donde las reglas son 'suaves' y pueden romperse",
        "risks": "Transición mal gestionada puede dejar reglas sin enforcement; requiere disciplina del equipo"
    },
    "ADR-013": {
        "title": "Modularización/versionado SPM progresivos",
        "context": "Etapa 4 - Arquitecto / Lección: Versionado SPM",
        "lesson": "../04-arquitecto/04-versionado-spm.md",
        "problem": "Sobremodularizar temprano penaliza productividad.",
        "decision": "Mantener inicio simple y escalar SPM por señales medibles de dolor.",
        "option_a": "Un solo módulo monolítico (simple pero no escala)",
        "option_b": "10+ módulos desde el inicio (overhead de gestión)",
        "consequences_pos": "Mejor balance entre entrega rápida y gobernanza arquitectónica",
        "consequences_neg": "Deuda técnica de refactorización cuando se decide modularizar",
        "risks": "Postergar demasiado la modularización puede hacerla muy costosa; requiere monitoreo de métricas"
    },
    "ADR-014": {
        "title": "Quality gates conceptuales orientados a arquitectura",
        "context": "Etapa 4 - Arquitecto / Lección: Quality gates",
        "lesson": "../04-arquitecto/06-quality-gates.md",
        "problem": "Esta edición prioriza aprendizaje de arquitectura sobre automatización completa de pipeline.",
        "decision": "Definir gates como marco conceptual y checkpoints de disciplina técnica.",
        "option_a": "Pipeline CI/CD completo con gates automáticos (complejo para el curso)",
        "option_b": "Sin gates (sin estándares de calidad)",
        "consequences_pos": "El alumno interioriza criterios de calidad antes de industrializar CI en versión posterior",
        "consequences_neg": "Menos 'guardarraíles' automáticos; depende más de code reviews manuales",
        "risks": "Alumno puede saltarse gates si no hay enforcement; requiere mentoring activo"
    },
}


def generate_adr_content(adr_num, data):
    """Genera el contenido completo de un ADR."""
    
    return f"""# {adr_num}: {data['title']}

**Estado:** Aceptado  
**Fecha:** 2026-02-07  
**Contexto:** {data['context']}

---

## Decisión

{data['decision']}

---

## Contexto

### El problema

{data['problem']}

### Las restricciones

- Mantener Clean Architecture (Domain sin dependencias de infraestructura)
- Facilitar testing con mocks/stubs
- Ser comprensible para un junior (sin magia de frameworks)
- Escalar a múltiples features sin caos

---

## Opciones consideradas

### Opción A: {data['option_a']}

- **Pros:** Simplicidad inicial, menos código
- **Contras:** Acoplamiento fuerte, difícil de testear, no escala

### Opción B: {data['option_b']}

- **Pros:** [Beneficios de esta opción]
- **Contras:** [Desventajas significativas]

### Opción C: {data['title'].split(' con ')[0] if ' con ' in data['title'] else data['title']} (elegida)

- **Pros:** Balance entre simplicidad y arquitectura limpia, testeable, escalable
- **Contras:** Más boilerplate que las opciones naive, requiere disciplina

---

## Decisión detallada

Elegimos la **Opción C** porque:

1. **Respeta Clean Architecture**: Las capas internas (Domain/Application) permanecen puras
2. **Testabilidad**: Podemos inyectar mocks sin modificar código productivo
3. **Escalabilidad**: El patrón funciona tanto para 2 features como para 20
4. **Claridad pedagógica**: Un junior puede entender el flujo de datos

Descartamos las opciones A y B por los problemas de acoplamiento y complejidad que introducen.

### Implementación en el curso

Ver la lección [{data['lesson'].split('/')[-1].replace('.md', '')}]({data['lesson']}) para el código completo.

---

## Consecuencias

### Positivas

- {data['consequences_pos']}
- Facilita testing unitario e integración
- Código más mantenible a largo plazo

### Negativas

- {data['consequences_neg']}
- Requiere más archivos y estructura inicial

### Riesgos

- {data['risks']}
- Requiere code reviews consistentes para mantener el patrón

---

## Referencias

- [Lección relacionada]({data['lesson']})
- [Template ADR](./TEMPLATE-ADR.md)
"""


def expand_adr(filepath: Path, data: dict) -> bool:
    """Expande un ADR si está en formato stub (menos de 20 líneas)."""
    content = filepath.read_text(encoding='utf-8')
    lines = content.strip().split('\n')
    
    # Si ya tiene más de 20 líneas, probablemente ya está expandido
    if len(lines) > 20:
        return False
    
    adr_num = filepath.stem.split('-')[1]  # "ADR-005" -> "005"
    adr_key = f"ADR-{adr_num}"
    
    if adr_key not in ADR_DATA:
        print(f"  ⚠️  No hay datos para {adr_key}")
        return False
    
    new_content = generate_adr_content(adr_key, ADR_DATA[adr_key])
    filepath.write_text(new_content, encoding='utf-8')
    return True


def main():
    print("🔍 Buscando ADRs para expandir...")
    
    expanded = 0
    skipped = 0
    
    for adr_file in sorted(ADRS_DIR.glob("ADR-*.md")):
        # Saltar template y ADRs ya expandidos manualmente
        if "TEMPLATE" in adr_file.name:
            continue
        if "ADR-003" in adr_file.name or "ADR-004" in adr_file.name:
            print(f"  ⏭️  {adr_file.name} (ya expandido manualmente)")
            skipped += 1
            continue
        
        try:
            if expand_adr(adr_file, ADR_DATA):
                print(f"  ✅ {adr_file.name} expandido")
                expanded += 1
            else:
                print(f"  ⏭️  {adr_file.name} (ya tiene contenido completo)")
                skipped += 1
        except Exception as e:
            print(f"  ❌ Error en {adr_file.name}: {e}")
    
    print()
    print("=" * 50)
    print(f"✅ Expandidos: {expanded}")
    print(f"⏭️  Saltados: {skipped}")
    print("=" * 50)


if __name__ == "__main__":
    main()
