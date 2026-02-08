# Decisiones tomadas durante el desarrollo del curso

## Proposito

Este documento consolida decisiones de alcance, arquitectura y pedagogía de la edición vigente del curso.
Sirve como contrato de coherencia para futuras iteraciones.

---

## Decisiones de alcance (edición actual)

| Tema | Decision vigente | Fuera de alcance ahora | Motivo |
|---|---|---|---|
| **Backend** | Firebase (Auth + Firestore) | Supabase y otros backends alternativos | Mantener foco y reducir carga cognitiva para juniors |
| **State management** | SwiftUI moderno con `@Observable` | TCA | TCA se considera curso separado o extensión futura |
| **CI ejecutable** | Documentación conceptual de quality gates | Pipeline real en este repositorio del curso | El foco actual es arquitectura y proceso técnico |
| **Formato** | Markdown + HTML navegable | Generación de proyecto app preconstruido | El alumno construye la app paso a paso |
| **Target mínimo** | iOS 17+ | iOS 16 y anteriores | Aprovechar APIs modernas (`@Observable`, SwiftData) |

---

## Decisiones arquitectónicas

| Tema | Decision | Referencia |
|---|---|---|
| Patrón base | Clean Architecture + Feature-First | Etapa 1 |
| Dependencias | Flechas hacia adentro, composición fuera del core | Etapa 1-2 |
| Navegación | Event-driven + coordinador | Etapa 2 y 4 |
| Persistencia local | SwiftData para ruta principal de curso | Etapa 3 |
| Concurrencia | Swift 6.2 strict concurrency (`Sendable`, actors, cancelación) | Etapa 3-5 |
| Gobernanza | ADRs + reglas + guías documentadas | Etapa 4 |

---

## Decisiones pedagógicas

| Tema | Decision |
|---|---|
| Audiencia | Junior absoluto a arquitecto |
| Método | BDD -> TDD (Red/Green/Refactor) -> producción -> refactor |
| Enfoque | Hands-on obligatorio con checkpoints visibles en Xcode |
| Profundidad | Explicación extensa: qué, por qué, cómo, cuándo y errores típicos |
| Calidad de aprendizaje | Uniformidad de nivel entre lecciones, evitando huecos y ambigüedad |

---

## Regla de hands-on (obligatoria)

Cada lección debe dar, como mínimo:

1. Qué archivo crear/editar y en qué ruta.
2. Qué test ejecutar primero y por qué debe fallar (RED).
3. Qué implementación mínima escribir (GREEN).
4. Qué refactor hacer sin romper tests (REFACTOR).
5. Qué comandos/acciones de verificación ejecutar (`Cmd+U`, `Cmd+B`, `Cmd+R` cuando aplique).

Si una lección es conceptual (por ejemplo, gobernanza), debe incluir igualmente un checkpoint práctico verificable en documentación, decisiones o pruebas de contrato.

---

## Seguimiento de pendientes (próxima edición)

| Pendiente | Estado |
|---|---|
| CI ejecutable en GitHub Actions para repo demo del alumno | Diferido |
| Ruta backend alternativa completa | Diferido |
| Profundización específica en TCA | Diferido |

