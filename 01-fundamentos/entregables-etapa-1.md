# Entregables — Etapa 1: Junior

> Checklist verificable de lo que debes tener al completar esta etapa.

---

## Artefactos

- [ ] **Proyecto Xcode** con estructura Feature-First (`Features/Login/` con 4 capas).
- [ ] **Escenarios BDD** del Login documentados (happy path, sad path, edge cases).
- [ ] **Value Objects** `Email` y `Password` con validación por construcción.
- [ ] **Errores tipados** `AuthError` y `LoginUseCase.Error`.
- [ ] **Evento** `LoginEvent` (succeeded/failed).
- [ ] **Puerto** `AuthGateway` como protocolo en Application.
- [ ] **Caso de uso** `LoginUseCase` con TDD completo.
- [ ] **Implementación** `RemoteAuthGateway` + `StubAuthGateway`.
- [ ] **ViewModel** `LoginViewModel` con `@Observable` + `@MainActor`.
- [ ] **Vista** `LoginView` en SwiftUI con preview funcional.
- [ ] **ADR-001** documentando decisiones del Login.

---

## Tests

- [ ] Unit tests de `Email` (formato válido, inválido, vacío, espacios).
- [ ] Unit tests de `Password` (válido, vacío).
- [ ] Unit tests de `LoginUseCase` (todos los escenarios BDD).
- [ ] Contract tests de `RemoteAuthGateway` (éxito, 401, error de red).
- [ ] Todos los tests escritos **antes** del código de producción.

---

## Competencias validadas

- [ ] Separación correcta de responsabilidades por capa.
- [ ] Dependencias apuntan hacia Domain (nunca al revés).
- [ ] Test-first real (no test-after).
- [ ] Concurrencia segura: `Sendable` en modelos y dobles de test.
- [ ] Navegación desacoplada (closure, no `NavigationLink` directo).

---

## Diagrama de dependencias esperado

```
LoginView
  └──> LoginViewModel (@Observable, @MainActor)
         └──> LoginUseCase (struct, Sendable)
                ├──> Email, Password (Value Objects)
                ├──> Credentials, Session (modelos)
                ├──> AuthError (errores de dominio)
                └──> AuthGateway (protocolo)
                       ├── RemoteAuthGateway (producción)
                       └── StubAuthGateway (desarrollo/tests)
```

---

**Siguiente etapa:** [Etapa 2 — Integración y disciplina →](../02-integracion/00-introduccion.md)
