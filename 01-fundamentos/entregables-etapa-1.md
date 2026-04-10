# Entregables — Etapa 1: Junior

> Checklist verificable de lo que debes tener al completar esta etapa.

---

## Artefactos

- [ ] **Proyecto Xcode** con estructura Feature-First (`Features/Login/` con 4 capas).
- [ ] **Escenarios BDD** del Login documentados (happy path, sad path, edge cases).
- [ ] **Value Objects** `EmailAddress` y `Password` con validación por construcción.
- [ ] **Errores tipados** `LoginError`.
- [ ] **Evento** `LoginEvent` (success/failure).
- [ ] **Puerto** `AuthRepository` como protocolo en Application.
- [ ] **Caso de uso** `AuthenticateUserUseCase` con TDD completo.
- [ ] **Implementación** `AuthHTTPRepository` + `InMemoryAuthRepository`.
- [ ] **ViewModel** `LoginViewModel` con `@Observable` + `@MainActor`.
- [ ] **Vista** `LoginView` en SwiftUI con preview funcional.
- [ ] **ADR-001** documentando decisiones del Login.

---

## Tests

- [ ] Unit tests de `EmailAddress` (formato válido, inválido, vacío, espacios).
- [ ] Unit tests de `Password` (válido, vacío).
- [ ] Unit tests de `AuthenticateUserUseCase` (todos los escenarios BDD).
- [ ] Contract tests de `AuthHTTPRepository` (éxito, 401, error de red).
- [ ] Todos los tests escritos **antes** del código de producción.

---

## Competencias validadas

- [ ] Separación correcta de responsabilidades por capa.
- [ ] Dependencias apuntan hacia Domain (nunca al revés).
- [ ] Test-first real (no test-after).
- [ ] Concurrencia segura: `Sendable` en modelos y dobles de test.
- [ ] Navegación desacoplada (protocolo `LoginNavigating`, no `NavigationLink` directo).

---

## Diagrama de dependencias esperado

```text
LoginView
  └──> LoginViewModel (@Observable, @MainActor)
         └──> AuthenticateUserUseCase (struct, Sendable)
                ├──> EmailAddress, Password (Value Objects)
                ├──> Credentials, UserSession (modelos)
                ├──> LoginError (errores de dominio)
                └──> AuthRepository (protocolo)
                       ├── AuthHTTPRepository (producción)
                       └── InMemoryAuthRepository (desarrollo/tests)
```

---

## Si no cumples todos los entregables

No pasa nada. Esto es normal. Aquí tienes un plan de recuperación:

### Paso 1: Identifica qué te falta
Revisa la checklist de arriba y marca en rojo lo que no tienes.

### Paso 2: Prioriza
No intentes hacer todo a la vez. Orden de prioridad:
1. **Value Objects** (`EmailAddress`, `Password`) - Son la base de todo
2. **AuthenticateUserUseCase con TDD** - El núcleo de la lógica
3. **LoginViewModel** - La conexión con la UI
4. **LoginView** - Lo que el usuario ve
5. **Tests** - La seguridad de que funciona

### Paso 3: Recursos de ayuda
- **Errores de compilación**: Revisa [Guía de Recuperación - Etapa 1](../anexos/guia-recuperacion-ios.md#etapa-1)
- **No entiendes un concepto**: Vuelve a la lección correspondiente, no sigas adelante
- **Tests que no pasan**: Lee el error cuidadosamente; los tests son tu mejor debugger

### Paso 4: Pide ayuda
Si después de 2 intentos sigues atascado:
- Describe qué error ves (copia el mensaje exacto)
- Explica qué has intentado
- Pregunta en el foro/Discord del curso

---

## Lo que ya sabes hacer (celebración)

Aunque no cumplas todos los entregables, seguro que has aprendido algo:

- ✅ Escribir código Swift básico
- ✅ Crear un proyecto Xcode
- ✅ Estructurar carpetas Feature-First
- ✅ Algún concepto de Value Objects o TDD

**Esto ya es más de lo que sabías antes de empezar.** Cada línea de código cuenta.

---

## Qué sigue

Has completado la Etapa 1. Conoces Clean Architecture, Feature-First, BDD, TDD, y tienes una app iOS funcional con separación real de responsabilidades.

La Etapa 2 (Integración) añade una segunda feature, navegación entre features, y un coordinador central. Los mismos principios, más complejidad.
