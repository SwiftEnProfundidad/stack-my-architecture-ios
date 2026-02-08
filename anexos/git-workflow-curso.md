# Git Workflow para el Curso

## Cómo versionar tu progreso paso a paso

Git es tu herramienta de seguridad. Cada commit es un punto al que puedes volver si algo sale mal. Esta guía te muestra cómo usar Git durante el curso para mantener tu trabajo organizado y recuperable.

> **Nota:** Esta es una guía **opcional** pero recomendada. Si prefieres no usar Git, puedes continuar sin problemas.

---

## Convención de commits

Usa mensajes de commit descriptivos que expliquen qué cambió y por qué:

```
[E1] Domain: Add Email and Password value objects with validation

- Email validates format with regex
- Password enforces minimum length of 8
- Both conform to Equatable, Hashable, Sendable
- Includes unit tests for valid/invalid cases
```

### Estructura del mensaje

```
[ETAPA] Componente: Acción en imperativo

- Detalle de cambios
- Motivación o contexto
```

### Prefijos por etapa

| Prefijo | Significado |
|---------|-------------|
| `[E0]` | Etapa 0 - Introducción |
| `[E1]` | Etapa 1 - Fundamentos (Login) |
| `[E2]` | Etapa 2 - Integración (Catalog) |
| `[E3]` | Etapa 3 - Evolución (SwiftData, Firebase) |
| `[E4]` | Etapa 4 - Arquitecto (Bounded contexts) |
| `[E5]` | Etapa 5 - Maestría (Concurrencia, Performance) |
| `[PF]` | Proyecto Final |

---

## Tags para hitos importantes

Los tags marcan puntos de referencia importantes:

```bash
# Después de completar cada entregable de etapa
git tag -a e1-complete -m "Etapa 1 completa: Login funcional con tests"
git tag -a e2-complete -m "Etapa 2 completa: Login + Catalog navegando"

# Ver todos los tags
git tag -l

# Volver a un tag específico (si rompes algo)
git checkout e1-complete
```

### Tags recomendados

| Tag | Momento de crear |
|-----|------------------|
| `e1-login-domain` | Domain de Login listo |
| `e1-login-app` | Login compila y ejecuta |
| `e1-complete` | Entregables E1 verificados |
| `e2-catalog-domain` | Domain de Catalog listo |
| `e2-navigation` | Navegación Login → Catalog funciona |
| `e2-complete` | Entregables E2 verificados |
| `e3-swiftdata` | Persistencia local funcionando |
| `e3-complete` | Entregables E3 verificados |
| `e4-complete` | Entregables E4 verificados |
| `e5-complete` | Entregables E5 verificados |
| `proyecto-final-v1` | Primera versión del proyecto final |
| `curso-completo` | Curso terminado |

---

## Flujo de trabajo recomendado

### Al inicio del curso

```bash
# Inicializar repositorio
cd /ruta/a/tu/proyecto
git init

# Crear .gitignore para archivos de Xcode que no deben versionarse
cat > .gitignore << 'EOF'
# Xcode
*.xcodeproj/xcuserdata/
*.xcworkspace/xcuserdata/
*.xcworkspace/xcshareddata/IDEWorkspaceChecks.plist
DerivedData/
build/
*.ipa
*.dSYM.zip
*.dSYM

# Swift Package Manager
.build/
Package.resolved

# macOS
.DS_Store
EOF

git add .gitignore
git commit -m "[INIT] Add .gitignore for Xcode project"

# Crear tag inicial
git tag -a inicio-curso -m "Punto de partida del curso"
```

### Durante el desarrollo (después de cada lección)

```bash
# Ver qué cambió
git status

# Añadir archivos nuevos y modificados
git add .

# Commit con mensaje descriptivo
git commit -m "[E1] Domain: Add Email value object with validation

- Validates format with regex
- Unit tests for valid/invalid cases
- Conforms to Equatable, Hashable, Sendable"

# Opcional: crear tag si es un hito
git tag -a e1-email-domain -m "Email VO completo con tests"
```

### Cuando algo se rompe

```bash
# Ver el historial
git log --oneline --graph

# Ver qué cambió en el último commit
git show HEAD

# Deshacer el último commit (mantener los cambios)
git reset --soft HEAD~1

# Deshacer completamente y volver al último tag conocido
git reset --hard e1-login-domain

# O simplemente ver el estado anterior sin cambiar nada
git checkout e1-login-domain
# ...verificar que funcionaba...
git checkout main  # volver a la rama actual
```

---

## Rama de trabajo por etapa (opcional avanzado)

Si quieres experimentar sin riesgo, usa ramas:

```bash
# Crear rama para la etapa 2
git checkout -b etapa-2-catalog

# Trabajar en E2, hacer commits...

# Cuando E2 esté estable, fusionar a main
git checkout main
git merge etapa-2-catalog
git tag -a e2-complete -m "Etapa 2 lista"
```

### Estrategia de ramas simple

```
main (estable)
  └─ etapa-2-catalog (desarrollo)
  └─ etapa-3-evolucion (desarrollo)
```

---

## Comandos Git esenciales (cheat sheet)

| Comando | Para qué sirve |
|---------|----------------|
| `git status` | Ver qué archivos cambiaron |
| `git add <archivo>` | Añadir archivo al siguiente commit |
| `git add .` | Añadir todos los cambios |
| `git commit -m "mensaje"` | Crear commit |
| `git log --oneline` | Ver historial resumido |
| `git diff` | Ver cambios no commiteados |
| `git tag -a nombre -m "desc"` | Crear tag anotado |
| `git checkout <tag>` | Cambiar a un tag específico |
| `git reset --soft HEAD~1` | Deshacer último commit, mantener cambios |
| `git reset --hard <tag>` | Volver a un tag, descartar todo |

---

## Escenarios comunes

### "Borré código que funcionaba"

```bash
# Recuperar archivo de un commit anterior
git checkout e1-complete -- Features/Login/Domain/Email.swift
```

### "Hice un desastre y quiero empezar de cero desde el último commit bueno"

```bash
# Ver qué commits hay
git log --oneline

# Volver al commit antes del desastre
git reset --hard abc1234  # hash del commit bueno
```

### "Quiero guardar cambios sin hacer commit (para cambiar de rama/tarea)"

```bash
# Guardar cambios temporalmente
git stash

# ...hacer otra cosa...

# Recuperar cambios
git stash pop
```

### "Commit en el mensaje equivocado"

```bash
# Corregir mensaje del último commit
git commit --amend -m "[E1] Domain: Add Email value object (corregido)"
```

---

## Git en Xcode

Xcode tiene integración visual de Git:

### Source Control Navigator (panel izquierdo)

- Ver historial de commits
- Ver quién cambió qué línea
- Comparar versiones

### Blame (quién escribió esto)

1. Abre cualquier archivo
2. Editor → Show Blame (o click derecho → Show Blame)
3. Cada línea muestra: autor, fecha, mensaje de commit

### Diff (qué cambió)

1. En Source Control Navigator, selecciona un commit
2. El panel derecho muestra qué archivos cambiaron
3. Click en un archivo para ver el diff línea por línea

---

## Mejores prácticas

### ✅ Hacer

- Commits pequeños y frecuentes (cada lección o cada componente)
- Mensajes descriptivos con contexto
- Tags en hitos importantes (fin de etapa, app funcional)
- .gitignore configurado desde el inicio
- Revisar `git status` antes de commit

### ❌ No hacer

- Commits gigantes con "cambios varios"
- Mensajes como "fix" o "update" sin contexto
- Versionar archivos generados (DerivedData, build)
- Commitear código que no compila (a menos que sea temporal)

---

## Resumen visual

```
Inicio curso
    │
    ▼
[E1] Domain ──────► tag: e1-login-domain
    │
    ▼
[E1] Application ─► tag: e1-login-application
    │
    ▼
[E1] Infrastructure ► tag: e1-login-infra
    │
    ▼
[E1] Interface ───► tag: e1-login-interface
    │
    ▼
[E1] App running ──► tag: e1-complete
    │
    ▼
[E2] Catalog ──────► tag: e2-catalog-domain
    │
   ...continúa
```

---

## Recordatorio final

Git es tu **red de seguridad**. No es solo para compartir código, es para:
- Experimentar sin miedo (puedes volver atrás)
- Entender qué cambió y cuándo
- Recuperar trabajo si algo se rompe
- Mantener un historial de tu progreso

**No necesitas ser experto en Git.** Con los comandos de esta guía tienes más que suficiente para todo el curso.

---

**Recursos adicionales:**
- [Git Documentation](https://git-scm.com/doc)
- [Oh Shit, Git!?](https://ohshitgit.com/) - Soluciones rápidas a problemas comunes
