# Marco de decisiones arquitectónicas

## Modelo mental

Piensa en cada decisión arquitectónica como una bifurcación en un camino de montaña. No puedes ver el final desde la bifurcación, pero sí puedes evaluar el terreno visible: pendiente, ancho del sendero, señales de peligro. Las restricciones duras son los precipicios (no negociables). Las restricciones blandas son las preferencias de ruta (negociables si el terreno lo exige). El ADR es el mapa que dejas para quien venga detrás.

```mermaid
flowchart LR
    P["Problema"] --> F["Fuerzas en conflicto"]
    F --> A["Alternativas (mín. 2)"]
    A --> T["Trade-off principal"]
    T --> D["Decisión + evidencia"]
    D --> R["Revisión con datos"]
```

## Flujo de decisión

Una decisión técnica buena no empieza con una solución. Empieza con fuerzas en conflicto.

Primero define restricciones duras. Son las que no puedes negociar, por ejemplo cumplimiento legal, presupuesto de latencia, límites de plataforma o requisitos de seguridad. Luego define restricciones blandas, que sí se pueden negociar, como preferencia de librería, estilo de equipo o velocidad de adopción.

Con esas fuerzas claras, lista alternativas reales. Para cada alternativa, registra beneficios, coste de implementación, coste de operación, riesgo de reversión y coste de oportunidad. Después explicita el trade-off principal, toma decisión y define evidencia de validación.

## Cuándo sí / cuándo no

Usa este marco cuando la decisión afecta a más de un módulo, tiene coste de reversión alto o implica un trade-off que el equipo debe entender. No lo uses para decisiones locales reversibles en minutos (renombrar una variable, elegir un modifier de SwiftUI).

## Ejemplo en el scaffold

En `ArchitectureKit`, la decisión de usar navegación por eventos en lugar de `NavigationLink` directo se documentó en `ADR-001-login.md`. Las fuerzas eran: testabilidad del flujo de navegación (dura) vs simplicidad de `NavigationLink` (blanda). La alternativa descartada fue acoplar Login a Catalog vía import directo. La evidencia de validación fue que `LoginViewModelTests` verifica navegación sin instanciar SwiftUI. Consulta la Etapa 2 (`02-integracion/02-navegacion-eventos.md`) para ver la implementación completa.

## Checklist 1 página: Architecture Decision Loop

- [ ] Problema formulado en una frase verificable.
- [ ] Restricciones duras identificadas y validadas.
- [ ] Restricciones blandas registradas.
- [ ] Mínimo 2 alternativas viables comparadas.
- [ ] Trade-off principal explicado sin ambigüedad.
- [ ] Decisión tomada con alcance y fecha.
- [ ] Consecuencias esperadas (positivas y negativas).
- [ ] Plan de reversión definido.
- [ ] Evidencia de éxito/fallo definida antes de implementar.
- [ ] Fecha de revisión pactada.

## Mini ejemplo opcional (plataforma)

Plataforma iOS/Android: migrar navegación de acoplamiento directo a coordinador/eventos. Restricción dura: no romper deep links existentes. Evidencia: tasa de rutas fallidas, cobertura de navegación y tiempo de onboarding de nueva feature.

---


## Refuerzo pedagogico

### Objetivo
- Comprende el objetivo tecnico de esta leccion y que decision arquitectonica habilita.

### Prerrequisitos
- Revisa la leccion anterior del bloque y confirma que dominas sus conceptos clave.

### Practica guiada
- Aplica un cambio pequeno y verificable en el scaffold o en una plantilla operativa relacionada con esta leccion.

### Verificacion
- ¿Puedes diferenciar restricciones duras y blandas en un ejemplo real de tu proyecto?
- ¿Puedes justificar la alternativa descartada y su trade-off principal?
- ¿Puedes definir una evidencia objetiva que valide tu decisión en producción?

## Semantica de flechas aplicada a esta arquitectura

```mermaid
flowchart LR
    subgraph APP["App / Composition module"]
        CR["CompositionRoot"]
        COORD["AppCoordinator"]
    end

    subgraph FEATURE["Feature module"]
        VM["FeatureViewModel"]
        UC["UseCase"]
        PORT["Repository protocol"]
    end

    subgraph INFRA["Infrastructure module"]
        ADAPTER["RemoteRepository adapter"]
        STORE["LocalStore"]
    end

    CR -.-> COORD
    CR -.-> ADAPTER
    VM --> UC
    UC -.o PORT
    ADAPTER --o PORT
    ADAPTER --> STORE
```

Lectura semantica minima de este diagrama:

1. `-->` dependencia directa en runtime.
2. `-.->` wiring y configuracion de ensamblado.
3. `-.o` dependencia contra contrato/abstraccion.
4. `--o` salida/propagacion desde implementacion concreta.
