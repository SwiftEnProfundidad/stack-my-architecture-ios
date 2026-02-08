# 11. Cómo Hablar de Arquitectura en una Entrevista

> Guía para expresar tu pensamiento arquitectónico de forma natural y convincente

---

## La Diferencia Entre "Explicar" y "Hablar De"

La diferencia crucial es: **no cuentes qué proyecto hiciste, habla de cómo piensas**. Cuando el entrevistador pregunta sobre tu experiencia con arquitectura, no busca una lista de tecnologías o un timeline de proyectos. Busca entender tu **proceso mental**, cómo enfrentas problemas complejos, cómo tomas decisiones bajo incertidumbre.

Esta sección te da un **hilo narrativo continuo** que puedes seguir, no respuestas memorizadas a memorizar.

---

## Mi Forma de Pensar la Arquitectura

Cuando me enfrento a un problema arquitectónico, siempre empiezo por lo mismo: **¿qué está pasando aquí realmente?** No me refiero a la tecnología, me refiero a las fuerzas en juego. Hay disponibilidad vs consistencia, hay velocidad de desarrollo vs mantenibilidad a largo plazo, hay simplicidad para el equipo actual vs preparación para crecimiento futuro.

La arquitectura, para mí, es el arte de tomar decisiones conscientes sobre estos trade-offs. No hay decisiones correctas o incorrectadas en abstracto, solo decisiones adecuadas o inadecuadas para un contexto específico. Mi trabajo como arquitecto no es aplicar patrones de un libro, es **mapear el espacio de soluciones** y elegir el punto que optimice para las constraints que tenemos ahora, manteniendo puertas abiertas para evolucionar después.

---

## Cómo Abordo Un Nuevo Problema

Mi proceso siempre sigue estas fases, aunque el tiempo dedicado a cada una varía según el problema:

**Primero, mapeo las fuerzas.** Todo problema arquitectónico tiene constraints duros y blandos. Los duros son no negociables: si tenemos que soportar iOS 15, si tenemos que cumplir GDPR, si tenemos que mantener latencia bajo 100ms para checkout. Los blandos son preferencias: preferimos código declarativo, queremos usar SwiftData, nos gustaría que los tests sean rápidos. Saber distinguirlos es crucial porque los constraints duros definen el espacio de soluciones posibles, y los blandos solo guían la elección dentro de ese espacio.

**Segundo, identifico invariantes.** Hay cosas que, independientemente de la solución, nunca deben pasar. En un sistema de pagos, nunca perdemos una transacción confirmada al usuario. En un sistema de reservas, nunca permitimos doble-booking. Estas invariantes son mi brújula: cualquier diseño que las viole está automáticamente descartado, no importa qué ventajas tenga en otros aspectos.

**Tercero, diseño para la variabilidad.** Pregunto: ¿qué va a cambiar y cuándo? Algunas cosas cambian semanalmente (UI, copy), algunas mensualmente (flujos de negocio), algunas anualmente (entidades core), y algunas nunca (principios matemáticos). La arquitectura debe facilitar los cambios rápidos donde son probables, y proteger la estabilidad donde es necesaria. No aplico la misma rigidez en todas partes, porque eso sería over-engineering.

**Cuarto, propongo 3 alternativas mínimo.** Nunca propongo una sola solución. Siempre busco al menos tres aproximaciones diferentes, aunque una parezca obviamente superior. Esto fuerza a pensar profundamente sobre el problema y a entender realmente los trade-offs. A veces la "solución obvia" tiene un defecto oculto que solo se revela cuando la comparas con alternativas.

**Quinto, documento la decisión y reviso métricas.** Una vez elegida la solución, escribo por qué se eligió esta y no las otras. Esto no es burocracia, es dejar una traza para mi yo futuro y para el equipo. Y establezco métricas para revisar: si dijimos que esta solución mejoraría el tiempo de build, medimos el tiempo de build antes y después. Si no mejoró, tenemos datos para aprender, no solo opiniones.

---

## Cómo Hablo de Mis Decisiones

Cuando el entrevistador me pregunta "cuéntame sobre una decisión arquitectónica difícil", no empiezo diciendo "en mi proyecto anterior...". En cambio, describo el **tipo de problema** y mi forma de abordarlo. El proyecto específico es solo el ejemplo que ilustra el patrón de pensamiento.

Por ejemplo: "Me encontré con una situación donde teníamos que elegir entre SwiftData y Core Data para persistencia offline. El contexto era que teníamos un 85% de usuarios en iOS 17+, el modelo de datos era moderado en complejidad, y teníamos presión de tiempo. Las fuerzas eran: modernidad de API vs estabilidad probada, curva de aprendizaje del equipo vs boilerplate conocido.

"Evalué tres opciones: usar Core Data puro para máxima estabilidad, usar SwiftData puro para API moderna, o usar un adapter pattern que nos permitiera cambiar. El invariante que protegí fue que el domain nunca debe conocer detalles de persistencia, así que cualquier solución tenía que pasar por un protocolo.

"Elegí SwiftData con adapter porque el 85% de usuarios en iOS 17+ hacía que el riesgo de usar tecnología nueva fuera manejable, y el adapter nos daba salida de emergencia si algo fallaba. El trade-off que acepté fue escribir más tests de migración, porque SwiftData es más nuevo y teníamos que validar que las migraciones funcionaban correctamente.

"Los resultados fueron: implementación en 3 días vs 2 semanas estimadas con Core Data por el boilerplate que nos ahorramos. Y tres meses después, cuando tuvimos que añadir una nueva entidad, fue literalmente añadir una línea con la macro @Model, vs las 20 líneas de boilerplate que habríamos necesitado en Core Data. La decisión se validó, pero lo importante es que teníamos el adapter como seguro si hubiera fallado."

Nota cómo esta narrativa fluye naturalmente: contexto → fuerzas → alternativas → decisión → trade-offs → resultado. No es un template mecánico, es simplemente contar la historia lógicamente.

## Cómo Explico Trade-offs

Una parte esencial de hablar de arquitectura es ser capaz de explicar por qué **rechazaste** alternativas, no solo por qué elegiste la tuya. Cualquiera puede defender su elección, un buen arquitecto puede explicar por qué las otras opciones no eran adecuadas para este contexto.

Por ejemplo, si uso MVVM en lugar de MVC: "MVC puede funcionar perfectamente bien para apps simples. Lo que me llevó a MVVM fue la necesidad de testear la lógica de presentación sin el overhead de SwiftUI previews. Cada cambio en un ViewModel con MVVM me da feedback en 2 segundos, mientras que con MVC tenía que lanzar el preview de SwiftUI que tarda 30 segundos. Esa diferencia de 28 segundos por cambio, multiplicada por cientos de cambios al día, es una diferencia enorme en velocidad de desarrollo. Pero si la app fuera simple y los cambios pocos, MVC habría sido más que suficiente y menos complejo."

Otro ejemplo, sobre TDD: "No uso TDD para todo. Lo aplico en domain y application layers porque ahí la lógica es compleja, estable, y los bugs son costosos. Para UI y prototipos rápidos, donde hay alto churn visual y los requisitos cambian semanalmente, prefiero tests de snapshot que dan más valor con menos coste. Mi criterio es simple: si el coste potencial de un bug es mayor que el coste de escribir y mantener el test, entonces TDD. Si no, otros tipos de tests o incluso manual QA para flujos críticos."

La clave es que **no defiendo una tecnología o patrón**, defiendo una **decisión contextual** que consideró alternativas y eligió conscientemente.

## Cómo Hablo de Evolución

A los arquitectos nos gusta pensar que diseñamos sistemas perfectos desde el día uno. La realidad es que **toda arquitectura buena evoluciona**. Cuando hablo de esto, no lo presento como un fallo, lo presento como una virtud.

"Empecé con una arquitectura simple que resolvía el problema inmediato. Documenté las decisiones como ADRs porque sabía que algunas serían provisionales. A los tres meses, las métricas de CI mostraban acoplamiento creciente entre dos features que inicialmente parecían independientes. En lugar de hacer un big-bang rewrite que habría sido arriesgado, introduje bounded contexts gradualmente, moviendo código en pequeños PRs que pasaban todos los tests. En seis meses, teníamos una arquitectura modular sin haber tenido downtime ni periodos de inestabilidad."

Esto muestra que entiendo que la arquitectura es **adaptativa**, no predictiva. No intento adivinar el futuro, construyo para el presente con ganchos de extensión, y adapto cuando el futuro se hace presente.

## Cómo Hablo del Equipo

La arquitectura no es solo código, es **cómo el equipo trabaja con el código**. Cuando hablo de mis decisiones, siempre incluyo la dimensión humana.

"Propuse la arquitectura mediante RFCs internos que explicaban el problema, las alternativas consideradas, la recomendación, y solicitaban feedback explícito. No impuse la decisión, porque una arquitectura que el equipo no entiende o no compra es peor que ninguna arquitectura. Realicé sesiones de pair programming específicamente para transferir el conocimiento de por qué hicimos las cosas así. Definí arquitectura como 'código que otros pueden mantener sin mi', no como mi visión personal que requiere mi presencia para funcionar."

Esto muestra que entiendo que **Conway's Law** es real: la arquitectura del sistema refleja la estructura de comunicación del equipo. Si diseño algo que requiere que 4 equipos se coordinen constantemente, estoy diseñando un problema organizacional, no solo técnico.

---

## Cómo Demuestro Pensamiento en Sistemas

El entrevistador quiere ver que puedo pensar en **efectos de segunda y tercera orden**, no solo en el efecto inmediato de una decisión.

Por ejemplo, sobre agregar caché: "El efecto primario de añadir caché es que las lecturas son más rápidas. El efecto secundario es que introduzco la posibilidad de inconsistencia entre caché y fuente de verdad. El efecto terciario es que mi sistema ahora tiene que manejar invalidación de caché, que es uno de los problemas más difíciles en informática. Por eso no añado caché por defecto. Solo la añado cuando tengo métricas que demuestran que la latencia de lectura es un problema real, y cuando tengo estrategia de invalidación clara: TTL para datos que pueden ser eventualmente consistentes, invalidación inmediata por eventos para datos que deben ser fuertemente consistentes."

Esto demuestra que **mi arquitectura es consciente de sus consecuencias**, no aplico patrones porque suenan bien.

---

## Cómo Cierro Una Respuesta

Las mejores respuestas terminan con **evidencia**, no con opiniones.

"Medí cycle time, defect rate y cognitive load antes y después del cambio arquitectónico. El cycle time bajó de 2 semanas a 4 días. El defect rate se mantuvo estable, lo cual fue una victoria porque normalmente los refactors aumentan bugs a corto plazo. La carga cognitiva, medida por tiempo que nuevos developers tardaban en hacer su primera contribución útil, bajó de 5 días a 2 días. Estas métricas me dijeron que la arquitectura estaba funcionando, no mi intuición."

Si no tengo métricas exactas, al menos doy **indicadores concretos**: "El tiempo de build bajó de 12 minutos a 4 minutos. Los tests flaky que fallaban el 40% de las veces desaparecieron completamente. Cuatro equipos pudieron desarrollar en paralelo sin conflictos de merge que antes eran semanales."

---

## Narrativa Completa de Ejemplo

Aquí va un ejemplo de cómo sonaría una respuesta completa a "cuéntame sobre tu experiencia diseñando arquitectura":

"Para mí, diseñar arquitectura es principalmente sobre entender constraints y trade-offs. Tuve una situación reciente donde necesitábamos permitir que múltiples equipos trabajaran en paralelo en una codebase que estaba creciendo rápidamente. Las fuerzas eran claras: necesitábamos velocidad de desarrollo pero también estabilidad, necesitábamos independencia de equipos pero también consistencia en la experiencia de usuario.

"Identifiqué que el acoplamiento accidental era nuestro mayor problema. Features que deberían ser independientes estaban conectadas mediante estado compartido mutable. Mi invariante fue que ningún feature debe poder romper otro feature simplemente porque cambió su implementación interna.

"Evalué tres aproximaciones: mantener el estado compartido pero añadir tests exhaustivos de integración, eliminar el estado compartido mediante inyección de dependencias pura, o introducir comunicación mediante eventos con contratos claros. La primera opción habría sido la más fácil de implementar pero no escalaba: cada nuevo feature añadía complejidad exponencial a los tests de integración. La segunda era purista pero requería reescribir demasiado código existente de golpe. Elegí la tercera: eventos con contratos.

"El trade-off fue que añadíamos complejidad de indirección. Cada comunicación entre features ahora pasaba por un bus de eventos en lugar de llamadas directas. Pero esto nos permitió desacoplar el tiempo de deployment: un equipo podía cambiar su feature sin que otros equipos tuvieran que saberlo, siempre que respetaran el contrato de eventos.

"Lo validé primero con una feature piloto. Medí tiempo de build, frecuencia de conflictos de merge, y tiempo que nuevos developers tardaban en entender las dependencias. Después de tres meses con la nueva arquitectura, el tiempo de build había bajado un 60% porque podíamos compilar features independientemente, los conflictos de merge pasaron de semanales a mensuales, y los nuevos developers entendían el sistema en días en lugar de semanas porque las fronteras eran claras.

"Lo más importante que aprendí fue que la arquitectura no es estática. Tres meses después descubrimos que algunos eventos se estaban usando de formas que no anticipamos, así que tuvimos que redefinir algunos contratos. Pero porque teníamos contratos explícitos, detectamos el problema rápidamente mediante los tests de contrato, no mediante bugs en producción. La arquitectura nos permitió evolucionar, no nos encorsetó."

---

## Red Flags Que Debo Evitar

En mi forma de hablar, evito:

- **"Siempre uso X"**: La respuesta correcta es "elijo según el contexto"
- **"La arquitectura perfecta es..."**: No existe, hay arquitecturas adecuadas para contextos específicos
- **"Yo decidí sin consultar"**: La arquitectura es un esfuerzo de equipo, no un diktat
- **"No tengo métricas pero funcionó mejor"**: Si no puedo medirlo, no sé si funcionó
- **"Refactoricé todo de golpe"**: Los big-bang rewrites son riesgosos; evolución gradual es la norma

---

## Checklist Pre-Entrevista

Antes de la entrevista, me aseguro de poder:

- [ ] Explicar mi proceso de toma de decisiones arquitectónicas en secuencia lógica
- [ ] Contar al menos una historia donde rechazé alternativas por buenas razones
- [ ] Articular trade-offs en términos de constraints, no de preferencias personales
- [ ] Demostrar pensamiento en sistemas (efectos de segunda orden)
- [ ] Hablar de la dimensión humana (equipo, comunicación, Conway's Law)
- [ ] Citar métricas o indicadores concretos, no solo "mejoró"
- [ ] Dibujar la arquitectura en papel en menos de 2 minutos si me lo piden

---

## Recursos Para Prepararme

- [System Design Primer](https://github.com/donnemartin/system-design-primer) - Para ejercicios de diseño
- [Architecture Katas](https://archkatas.org/) - Práctica de decisiones bajo presión
- [The Software Architect Elevator](https://architectelevator.com/) - Pensamiento estratégico

---

## Mi "Architecture Elevator Pitch"

Si solo tengo 30 segundos para describir cómo pienso la arquitectura:

"Mi arquitectura es adaptativa, no predictiva. No intento diseñar el sistema perfecto para hipotéticos futuros. Diseño para el problema actual con ganchos de extensión, mido resultados, y adapto cuando el contexto cambia. Todo trade-off es consciente y documentado. La arquitectura es código que el equipo puede mantener, no mi visión personal."

---

## Entregable de esta Lección

Tu ejercicio es escribir tu propia "narrativa natural" respondiendo estas preguntas en voz alta, grabándote o escribiendo:

1. Describe tu proceso mental cuando enfrentas un problema arquitectónico nuevo
2. Cuenta una decisión específica: contexto, alternativas, por qué elegiste una, trade-offs aceptados, resultado
3. Explica por qué rechazaste una alternativa específica (no solo por qué elegiste la tuya)
4. Articula cómo tu arquitectura evolucionó, no cómo la diseñaste perfecta desde el día uno
5. Cierra con métricas o indicadores concretos de éxito

Practica estas narrativas hasta que fluyan naturalmente, sin sonar memorizadas. La autenticidad es más convincente que la perfección.
