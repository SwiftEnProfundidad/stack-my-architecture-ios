# Paridad de Mobile Architect iOS ↔ Android

## 1) Contexto y propósito

Este documento define una posición profesional clara y verificable para el rol de Mobile Architect en este programa: profundidad de ejecución en iOS y paridad arquitectónica en Android. Su objetivo es eliminar ambigüedades en evaluación de perfil, contratación y asignación de responsabilidades.

El problema que resuelve es frecuente en equipos y procesos de selección: confundir volumen de código en dos plataformas con capacidad real de arquitectura. Esta guía separa ejecución diaria de autoridad técnica y establece criterios defendibles para alinear expectativas entre ingeniería, management y recruiting.

## 2) Qué significa “Mobile Architect”

Mobile Architect no es “el desarrollador que más código escribe en todas las apps”. Es la responsabilidad de diseñar y sostener decisiones que reducen riesgo, preservan invariantes del sistema y permiten evolución sin degradar calidad operativa.

La función central del rol es decidir con evidencia: qué contratos son no negociables, qué trade-offs se aceptan, qué riesgos se asumen, qué controles de calidad son obligatorios y cómo se gobierna el cambio entre plataformas.

## 3) Profundidad en iOS: plataforma principal de ejecución

iOS es la plataforma de ejecución más profunda en este perfil. Aquí se concentra el mayor nivel hands-on en implementación compleja: flujos críticos, concurrencia segura, rendimiento, estado UI, integración SwiftUI y endurecimiento de calidad técnica en código productivo.

Esta profundidad no es simbólica. Implica responsabilidad directa sobre decisiones de diseño y ejecución en áreas de alta complejidad técnica y alto impacto de negocio dentro del stack iOS.

## 4) Paridad en Android: equivalencia arquitectónica

La paridad en Android se establece en el plano arquitectónico y operativo: arquitectura de capas, contratos entre módulos y servicios, quality gates, operabilidad, estrategia de release/rollback, disciplina de observabilidad y gobernanza técnica.

Paridad no significa mismo volumen diario de código en Android e iOS. Significa equivalencia en estándar de decisión, control de riesgo, coherencia de sistema y capacidad de exigir evidencia técnica en ambas plataformas.

## 5) Qué se comparte entre plataformas (no negociable)

Los siguientes elementos son obligatorios y comunes para iOS y Android. La verificación indicada es el criterio mínimo para considerar cada punto cumplido:

- Invariantes de arquitectura y de dominio. *(verificación: reglas de dependencia ejecutables en CI)*
- Contratos explícitos entre capas, features y APIs. *(verificación: interfaces tipadas con tests de contrato)*
- Estrategia de testing orientada a riesgo y evidencia verificable. *(verificación: cobertura en capas de dominio + gates de CI)*
- Observabilidad mínima operativa. *(verificación: eventos de error y latencia instrumentados sin PII)*
- Disciplina de release, rollback y feature flags. *(verificación: criterios de activación documentados y testados)*
- Postura de seguridad y privacidad consistente. *(verificación: threat model con controles faltantes explícitos)*

Estos puntos no dependen del framework de UI ni del lenguaje; dependen de gobernanza técnica y responsabilidad profesional.

## 6) Qué es específico de plataforma (y por qué)

Lo específico de plataforma incluye lenguaje, frameworks, tooling, pipelines y detalles de runtime. Es normal y saludable que exista especialización: Swift/SwiftUI/Xcode en iOS y Kotlin/Compose/Gradle en Android.

La especialización no contradice la arquitectura común. Al contrario, permite que cada plataforma optimice su ejecución sin romper invariantes compartidos ni degradar la coherencia del sistema móvil.

## 7) Autoridad de decisión vs autoridad de ejecución

**Autoridad de decisión (Mobile Architect)** — se activa cuando una decisión afecta a más de una plataforma, toca un invariante del sistema o implica un trade-off con riesgo sistémico:

- Definir invariantes, contratos y quality gates transversales.
- Aceptar o rechazar trade-offs con impacto en riesgo sistémico.
- Establecer criterios de operabilidad, release y rollback.
- Exigir evidencia PR-ready y trazabilidad de decisiones.

**Autoridad de ejecución (especialistas de plataforma)** — se activa para todo lo que es específico de plataforma y no toca contratos transversales:

- Implementar soluciones dentro de los marcos acordados.
- Seleccionar detalles de implementación plataforma-específicos.
- Optimizar rendimiento y experiencia de desarrollo local sin romper contratos globales.
- Escalar issues técnicos con evidencia cuando un contrato requiera revisión.

## 8) Mapeo a estructuras de equipo

Este rol trabaja como integrador técnico entre iOS, Android, backend, QA y producto. Su función es alinear decisiones de arquitectura y operación, evitando que cada subequipo optimice localmente en contra del sistema global.

Para evitar efectos de la Ley de Conway — que establece que los sistemas tienden a replicar la estructura de comunicación de los equipos que los construyen — las fronteras de equipo deben mapearse a bounded contexts y contratos explícitos, no a silos tecnológicos cerrados. El Mobile Architect sostiene esa coherencia y gestiona la evolución entre dependencias cruzadas.

## 9) Guion de entrevista

Estructura para responder "¿cuál es tu perfil en mobile?" en 5–6 frases. Cada bloque responde a una dimensión que el entrevistador evalúa:

**Profundidad en iOS** *(¿qué haces realmente?)*
Mi ejecución más profunda está en iOS, donde resuelvo flujos complejos y decisiones de alto riesgo técnico en producción.

**Paridad en Android** *(¿no es eso solo iOS?)*
En Android, mi contribución se centra en paridad arquitectónica y operativa: contratos, quality gates, observabilidad, release y gobernanza.

**Qué significa paridad** *(¿paridad = mismo código?)*
No presento paridad como mismo volumen de código diario, sino como misma calidad de decisión y control de riesgo entre plataformas.

**Cómo lo demuestro** *(¿tienes evidencia?)*
Trabajo con evidencia: PR-ready, trazabilidad de decisiones y criterios explícitos de rollback y seguridad.

**Qué aporta al equipo** *(¿para qué sirves en un equipo multiplataforma?)*
Esto me permite coordinar iOS, Android, backend y QA con un lenguaje técnico común y verificable. El resultado es un sistema móvil más estable, evolucionable y menos dependiente de decisiones ad hoc.

## 10) Resumen

La señal profesional de este perfil es clara: profundidad de ejecución en iOS con paridad arquitectónica en Android. Esta combinación no diluye expertise ni exagera alcance; refuerza responsabilidad real sobre coherencia, operabilidad y evolución del sistema móvil.

Bajo este marco, el valor del Mobile Architect no se mide por cantidad de código en dos plataformas, sino por calidad de decisiones, disciplina de evidencia y capacidad de sostener resultados técnicos bajo escrutinio.

---

## Qué sigue

Con esta lección concluye la Etapa 0 — Core Mobile. La siguiente etapa, [Etapa 1: Junior](../01-fundamentos/00-introduccion.md), arranca la construcción práctica: fundamentos de ingeniería, BDD, TDD y el scaffold de referencia.
