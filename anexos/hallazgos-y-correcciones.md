# Hallazgos y correcciones pedagógicas

Este documento existe para una cosa: evitar que un alumno junior (o un chaval de 14 años) estudie con huecos y se atasque en silencio.

No es una lista de errores “para juzgar”. Es una guía de depuración del aprendizaje.

---

## Cómo usar este documento

Cuando una lección no te salga a la primera, no saltes de tema. Haz este ciclo:

1. detectar el síntoma;
2. buscar el hallazgo equivalente;
3. aplicar la corrección concreta;
4. re-ejecutar el checkpoint (`Cmd+U`, `Cmd+B`, `Cmd+R` si aplica).

Si después de eso sigue fallando, vuelve a la lección y verifica rutas de archivo y target membership.

---

## Hallazgos frecuentes (globales)

### Hallazgo 1: “Copié el código y no compila”

**Síntoma típico:** errores de símbolos no encontrados o tipos duplicados.

**Causa raíz más frecuente:** archivo creado en la carpeta correcta, pero en el **target equivocado**.

**Corrección:**

1. Selecciona el archivo en Xcode.
2. Abre File Inspector.
3. En `Target Membership`, marca solo el target correcto.
4. `Cmd+B` para validar.

---

### Hallazgo 2: “Mis tests no ejecutan el código que creo”

**Síntoma típico:** test pasa/falla de forma rara aunque cambies implementación.

**Causa raíz:** estás editando un archivo distinto al que usa el target de tests.

**Corrección:**

1. Verifica ruta exacta en el árbol de Xcode.
2. Busca nombre duplicado del archivo (`rg --files | rg NombreArchivo.swift`).
3. Deja una sola fuente de verdad por tipo.

---

### Hallazgo 3: “No veo el ROJO de TDD”

**Síntoma típico:** el test nuevo pasa a la primera.

**Causa raíz:** implementaste antes de escribir test, o el test no está verificando comportamiento real.

**Corrección:**

1. Escribe primero una aserción que debería fallar.
2. Ejecuta solo ese test (`Cmd+U` sobre el test seleccionado).
3. Verifica fallo explícito antes de tocar producción.

---

### Hallazgo 4: “Todo está en verde, pero no entiendo por qué”

**Síntoma típico:** sensación de avanzar sin modelo mental.

**Causa raíz:** ejecutar mecánicamente sin traducir cada paso a responsabilidad de capa.

**Corrección:**

Para cada cambio, responde por escrito:

- ¿Esto es Domain, Application, Interface o Infrastructure?
- ¿Qué invariante protege?
- ¿Qué test protege este comportamiento?

---

## Hallazgos por etapa

## Etapa 1 (Fundamentos)

### Hallazgo: mezclar lógica de negocio en la vista

**Corrección:** la vista solo presenta estado y dispara acciones. Validación e invariantes van en Domain/Application.

### Hallazgo: usar `String` donde debería haber Value Object

**Corrección:** encapsula `Email`, `Password`, `Price` con validación en `init`.

---

## Etapa 2 (Integración)

### Hallazgo: feature A accede a internals de feature B

**Corrección:** cruza límites solo por contratos/eventos públicos.

### Hallazgo: coordinator con lógica de negocio

**Corrección:** el coordinador decide rutas; el negocio vive en UseCases.

---

## Etapa 3 (Resiliencia)

### Hallazgo: cache sin política explícita

**Corrección:** define TTL/invalidez y escribe tests de edge cases temporales.

### Hallazgo: logs sin contexto

**Corrección:** cada evento relevante debe llevar contexto mínimo (`feature`, `caso`, `resultado`, `error`).

---

## Etapa 4 (Arquitecto)

### Hallazgo: reglas en documentos que nadie verifica

**Corrección:** traducir reglas a checklist operable y criterios de PR.

### Hallazgo: modularizar “por moda”

**Corrección:** modulariza por dolor medible (acoplamiento, tiempo de build, coordinación).

---

## Etapa 5 (Maestría)

### Hallazgo: `@MainActor` usado para silenciar errores

**Corrección:** justificar aislamiento real, revisar `Sendable` y ownership.

### Hallazgo: concurrencia probada con tests no deterministas

**Corrección:** controlar reloj, aislar estado mutable y reducir no determinismo.

---

## Protocolo de recuperación rápida (cuando te bloqueas)

1. `Cmd+B` hasta compilar limpio.
2. Ejecuta una sola prueba (la del cambio actual).
3. Si falla, corrige primero el contrato, luego la implementación.
4. Cuando pase, ejecuta suite de la lección.
5. Solo entonces avanza a la siguiente lección.

---

## Señal de progreso real (no ilusión)

Sabes que estás aprendiendo de verdad cuando puedes:

1. explicar una decisión de capa sin mirar apuntes;
2. predecir qué test se romperá antes de ejecutar;
3. corregir un fallo sin “parches mágicos”;
4. defender un trade-off con A/B/C y riesgos.

Ese es el objetivo del curso: convertir criterio técnico en hábito de trabajo diario.
