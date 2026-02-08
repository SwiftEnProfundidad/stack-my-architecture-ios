# 12. Arquitectura Adaptativa: Más Allá del Patrón

> Cómo pensar como arquitecto senior cuando no hay "una respuesta correcta" en el libro

---

## El Problema del Nivel Master

Has aprendido Clean Architecture, MVVM, TDD, modularización... Pero en el día a día te encontrarás con **problemas que no encajan en ningún patrón conocido**.

- Una app que debe funcionar offline durante 7 días en zonas sin cobertura
- Un sistema que integra 5 SDKs de terceros con APIs incompatibles
- Una arquitectura que debe soportar tanto iOS 15 como visionOS
- Un producto que pivota de B2C a B2B con requirements contradictorios

**No hay un capítulo de libro para esto.**

Esta lección te da el **marco mental** para diseñar arquitecturas custom cuando las recetas estándar no aplican.

---

## 1. El Paradigma del Arquitecto Adaptativo

### De "¿Qué patrón uso?" a "¿Qué problema resuelvo?"

| Pensamiento Junior | Pensamiento Master |
|-------------------|-------------------|
| "Aquí va un Singleton" | "¿Cuál es el lifecycle real de esta dependencia?" |
| "Uso MVVM porque es mejor" | "¿Qué parte cambia más rápido? ¿Dónde necesito testear?" |
| "Añado una capa más" | "¿Estoy simplificando o complicando?" |
| "Busco en Stack Overflow" | "Construyo el modelo mental desde first principles" |

### Los 3 Niveles de Abstracción

Cuando enfrentas un problema arquitectónico nuevo, piensa en tres niveles:

```
NIVEL 1: Principios Universales
├── Separation of Concerns
├── Single Responsibility
├── Dependency Inversion
└── Information Hiding

NIVEL 2: Patrones Arquitectónicos  
├── Clean Architecture
├── Hexagonal / Ports & Adapters
├── Event-Driven
├── Microservices (móvil: modular)
└── CQRS, Event Sourcing...

NIVEL 3: Implementación Específica
├── ¿Value types o reference?
├── ¿Actor o lock?
├── ¿In-memory o persisted?
└── ¿Sync o async?
```

**El error común:** Saltar directo al Nivel 2 ("¿MVP o MVVM?") sin entender el Nivel 1 ("¿Qué cambia independientemente de qué?").

---

## 2. El Framework de Análisis Arquitectónico

### Paso 1: Mapear las Fuerzas

Todo problema arquitectónico tiene fuerzas en conflicto. Identifícalas:

```
Ejemplo: App de ventas offline-first para repartidores

FUERZA A: Disponibilidad (debe funcionar sin red)
FUERZA B: Consistencia (datos actualizados)
FUERZA C: Performance (respuesta inmediata)
FUERZA D: Simplicidad (código mantenible)

Conflicto: A vs B (offline vs fresh)
         A vs D (sync complejo vs simple)
         B vs C (validación vs velocidad)
```

**Herramienta:** Diagrama de fuerzas - dibuja cada fuerza como flecha, identifica tensiones.

### Paso 2: Definir Constraints Duros vs Blandos

| Constraints Duros (no negociables) | Constraints Blandos (preferencias) |
|-----------------------------------|----------------------------------|
| Debe funcionar en iOS 15+ | "Preferimos código declarativo" |
| Máximo 50MB de cache | "Queremos usar SwiftData" |
| Certificación PCI para pagos | "Tests deben ser < 1s" |
| Latencia < 100ms para checkout | "Separación estricta de capas" |

**Los constraints duros definen el espacio de soluciones posibles.**

### Paso 3: Identificar Invariantes

¿Qué NUNCA debe pasar, independientemente de la solución?

```
Ejemplo: App bancaria

INV 1: Nunca perdemos una transacción confirmada al usuario
INV 2: Nunca mostramos saldo inconsistente entre pestañas
INV 3: Nunca procesamos el mismo pago dos veces (idempotencia)
```

Las invariantes son tu brújula: **cualquier solución que las viole está descartada**.

### Paso 4: Diseñar para la Variabilidad

Pregúntate: **¿Qué va a cambiar y cuándo?**

```
Estrategia de capas según velocidad de cambio:

CAMBIA RÁPIDO (semanas): UI, copy, analytics events
├── Aísla: ViewModels, UI components
└── Facilita: Hot reload, feature flags, remote config

CAMBIA MEDIO (meses): Flujos de negocio, validaciones  
├── Aísla: Use cases, domain services
└── Facilita: Configuration over code, rule engines

CAMBIA LENTO (años): Entidades core, invariantes
├── Protege: Domain puro, tests exhaustivos
└── Resiste: Refactors mayores, migrations

NO CAMBIA: Principios matemáticos, leyes del negocio
├── Encapsula: En domain, documenta como ADR
└── Asume: Son tu fundamento
```

---

## 3. Catálogo de Problemas Arquitectónicos Reales

### Problema Tipo A: Sistemas Híbridos Legacy-Moderno

**Contexto:** App con 5 años de código Objective-C/C++, debes añadir módulos SwiftUI modernos.

**Fuerzas:**
- No puedes reescribir todo (coste, riesgo)
- Necesitas features nuevos en tecnología moderna
- El equipo quiere adoptar SwiftUI
- El código legacy funciona y está testeado

**Soluciones posibles:**

```
OPCIÓN A: Strangler Fig Pattern
├── Envuelve features legacy en wrappers Swift
├── Crea "fachada" que enruta a old o new
├── Migra feature por feature (no big bang)
└── Ejemplo: Navigation wrapper que decide UIKit vs SwiftUI

OPCIÓN B: Multi-Target Architecture
├── Separa legacy en framework estático
├── Nuevo código en dynamic framework
├── Comunicación mediante protocols (no dependencias directas)
└── Permite build del nuevo sin tocar legacy

OPCIÓN C: Feature Flags + Gradual Migration
├── Cada feature tiene ImplementaciónOld e ImplementaciónNew
├── Configuración en runtime decide cuál usar
├── A/B testing implícito: métricas comparativas
└── Rollback instantáneo si algo falla
```

**Decisión:** Depende de tu invariante. Si es "zero downtime", usa C. Si es "minimizar código duplicado", usa A. Si es "equipos paralelos", usa B.

### Problema Tipo B: Multi-Plataforma con Diferentes Capabilities

**Contexto:** Tu app va a iPhone, iPad, Mac, y ahora visionOS. Cada plataforma tiene constraints diferentes.

**Fuerzas:**
- Máximo code sharing (no 4 apps separadas)
- UX nativa por plataforma (no lowest common denominator)
- Features específicos: Apple Pencil (iPad), hand tracking (visionOS), menu bar (Mac)

**Arquitectura Adaptativa:**

```swift
// Core: Domain + Application (100% compartido)
protocol ProductRepository { ... }
protocol CartUseCase { ... }

// Infrastructure: Implementaciones compartidas donde posible
class NetworkProductRepository: ProductRepository { ... }

// Platform-specific UI (ViewModels compartidos, Views nativas)
#if os(iOS)
struct ProductView_iOS: View {
    @StateObject var viewModel: ProductViewModel // Compartido
    // UIKit-specific cuando necesario
}
#endif

#if os(visionOS)  
struct ProductView_Vision: View {
    @StateObject var viewModel: ProductViewModel // Mismo VM
    // Gestures específicos de visionOS
}
#endif

// Feature detection, no platform detection
if SupportsApplePencil {
    showPencilInterface()
}
```

**Principio:** "Same brain, different face". La lógica de negocio es idéntica; la presentación se adapta.

### Problema Tipo C: Integración Caótica de Terceros

**Contexto:** Debes integrar 5 SDKs diferentes (Analytics, Payment, CRM, Push, Auth), cada uno con su propio modelo de datos, callbacks, y lifecycle.

**El desastre común:**
```swift
// ❌ SDKs regados por toda la app
class ViewController {
    override func viewDidAppear() {
        Analytics.track("screen_view")  // Spaghetti
    }
}

// ❌ Conversión manual de tipos por todas partes
func convertPaymentResult(_ sdkResult: PaySDK.Result) -> MyResult {
    // ... 50 líneas de mapping
}
```

**Arquitectura Adaptativa - Anti-Corruption Layers (ACL):**

```
┌─────────────────────────────────────┐
│  TU APP (Clean Architecture)       │
│  ┌──────────────────────────────┐ │
│  │  Domain: PaymentService      │ │
│  │  (protocolo, modelos propios)│ │
│  └──────────────────────────────┘ │
│              ▲                      │
│  ┌───────────┴──────────────────┐ │
│  │  ACL: PaymentAdapter         │ │  ← Único lugar que conoce PaySDK
│  │  - Mapea errores SDK → Domain│ │
│  │  - Traduce callbacks → async │ │
│  │  - Aísla breaking changes    │ │
│  └──────────────────────────────┘ │
│              ▲                      │
├──────────────┼──────────────────────┤
│  PaySDK.framework (externo)        │
│  - Modelos propietarios            │
│  - Delegates con estado mutable    │
│  - Documentación cambiante         │
└─────────────────────────────────────┘
```

**Beneficios del ACL:**
- Cambiar PaySDK por Stripe solo toca el Adapter
- Tus tests usan mocks de `PaymentService`, no del SDK
- El SDK puede cambiar API: solo adaptas el ACL

### Problema Tipo D: Sistemas Eventuales con Alta Consistencia Requerida

**Contexto:** E-commerce donde el usuario ve stock en tiempo real, pero el backend tiene arquitectura eventualmente consistente (cachés, replicación).

**Fuerzas en conflicto máximo:**
- El usuario no puede comprar algo que ya no hay (consistencia fuerte)
- El sistema debe ser rápido y disponible (disponibilidad)
- El backend no puede garantizar lecturas siempre frescas

**Solución - Optimistic UI con Reconciliación:**

```swift
// 1. Mostramos inmediatamente (optimista)
@Observable class CartViewModel {
    var items: [CartItem]
    var pendingValidation: [CartItem] // Items aún no confirmados
    
    func addToCart(_ product: Product) {
        // UI inmediata: el usuario ve feedback al instante
        items.append(CartItem(product: product, status: .pending))
        
        // Background: validación real
        Task {
            let result = await validateWithServer(product)
            await MainActor.run {
                switch result {
                case .success:
                    updateStatus(product, to: .confirmed)
                case .failure(let error):
                    // Reconciliación: el servidor prevalece
                    showConflict(error)
                    removeFromCart(product)
                }
            }
        }
    }
}

// 2. Estrategias de reconciliación según dominio
enum ConflictStrategy {
    case serverWins        // Stock, precios: el servidor tiene la verdad
    case clientWins        // Preferencias usuario: UX sobre consistencia  
    case merge             // Ambos cambios: resolución manual
    case rejectBoth        // Transacciones críticas: abortar
}
```

**Invariante protegida:** "Nunca cobramos por algo que no tenemos". El servidor es la única fuente de verdad para stock, pero la UI no espera bloqueando.

### Problema Tipo E: Regulación y Compliance Cambiantes

**Contexto:** App fintech que opera en 3 países, cada uno con regulaciones diferentes (GDPR en Europa, LGPD en Brasil, CCPA en California). Las leyes cambian cada año.

**Arquitectura Adaptativa - Compliance as Code:**

```swift
// Domain: Reglas expresadas como código ejecutable, no comentarios
protocol ComplianceRule {
    var jurisdiction: Jurisdiction { get }
    func validate(_ data: UserData) -> ComplianceResult
}

struct GDPRDataRetentionRule: ComplianceRule {
    func validate(_ data: UserData) -> ComplianceResult {
        // Lógica real, testeable
        guard data.retentionDays <= 365 else {
            return .violation(.mustDelete, deadline: 30)
        }
        return .compliant
    }
}

// Application: Motor de compliance que evalúa según contexto
class ComplianceEngine {
    private let rules: [ComplianceRule]
    
    func check(_ operation: UserOperation, for user: User) -> ComplianceDecision {
        let applicable = rules.filter { 
            $0.jurisdiction == user.jurisdiction 
        }
        return evaluate(applicable, against: operation)
    }
}

// Nuevas regulaciones = nuevas implementaciones de ComplianceRule
// Tests garantizan que reglas cumplen la ley
// Documentación vive en ADRs vinculados a cada rule
```

---

## 4. Cuándo Romper las Reglas (Y Cómo Hacerlo Bien)

### Las Reglas del Rompimiento

**Regla de Oro:** Romper reglas arquitectónicas es válido si:
1. Sabes **exactamente** qué regla rompes y **por qué**
2. El beneficio es **medible** y **significativo**
3. El coste está **acotado** y **documentado**
4. Hay un **plan de contención** si explota

### Anti-Patterns de Rompimiento

❌ **"Todo el mundo acopla domain a UI, así que yo también"**
❌ **"Es más rápido así"** (sin medir)
❌ **"Lo refactorizo después"** (sin ticket/ADR)
❌ **"Es temporal"** (dura 3 años)

### Rompimientos Justificados (Ejemplos Reales)

#### Caso 1: Performance Crítica en Hot Path

**Situación:** Procesamiento de video en tiempo real, cada milisegundo importa.

**Regla rota:** "Nunca uses unsafe code en app de negocio"

**Justificación:**
```swift
// 98% del código: Safe Swift, Clean Architecture
// 2% del código: Performance-critical path

extension ImageProcessor {
    // ACLaramos el rompimiento
    /// - WARNING: Uses unsafe pointers for performance.
    /// - RATIONALE: 50x faster than safe alternative.
    /// - SAFETY: Input size validated upstream, bounds checked.
    /// - REVIEW: Quarterly security audit required.
    func fastPixelAccess(_ buffer: UnsafeMutablePointer<UInt8>) {
        // Implementation...
    }
}
```

**Contención:**
- Aislado en módulo separado
- Tests de fuzzing exhaustivos
- Auditoría de seguridad periódica
- Fallback a implementación safe si detectamos corruption

#### Caso 2: Acoplamiento Temporal en Batch Processing

**Situación:** Sincronización masiva de datos (10k registros). Clean Architecture pura sería 100x más lenta.

**Regla rota:** "Domain nunca conoce infrastructure"

**Solución pragmática:**
```swift
// Rompimiento explícito y documentado
/// ADR-042: Batch Sync Optimization
/// 
/// DECISION: Permitir que BatchSyncUseCase acceda directamente 
/// a Core Data context para sincronización masiva.
/// 
/// CONTEXT: Sync de 10k items con repository pattern 
/// toma 45s. Acceso directo: 2s.
/// 
/// RISK: Lógica de persistencia mezclada con domain.
/// MITIGATION: 
/// - Esta clase es la ÚNICA con permiso de romper la regla.
/// - Tests de integración exhaustivos.
/// - Si cambia modelo de datos, este es el primer archivo a revisar.
/// 
/// REVIEW DATE: Cada cambio de schema de datos.
class BatchSyncUseCase {
    private let coreDataContext: NSManagedObjectContext // ⚠️ Regla rota
    
    // ... implementación optimizada
}
```

---

## 5. Herramientas de Pensamiento Arquitectónico

### 5.1 El Diagrama de Decisión

Cuando dudas entre alternativas, visualiza:

```
                    [PROBLEMA]
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   [OPCIÓN A]     [OPCIÓN B]     [OPCIÓN C]
        │               │               │
   Pros/Cons       Pros/Cons       Pros/Cons
        │               │               │
        └───────────────┼───────────────┘
                        │
                 [DECISIÓN]
                        │
            ┌───────────┴───────────┐
       [TRADE-OFFS                    │
        ACEPTADOS]         [INVARIANTES
                            PROTEGIDOS]
                        │
                 [CRITERIO DE ÉXITO]
```

### 5.2 El "Architecture Journal"

Mantén un registro de decisiones arquitectónicas informales:

```markdown
## 2026-02-08: Decisión de sincronización offline

**Contexto:** Repartidores sin cobertura por 7 días.

**Alternativas consideradas:**
1. Full offline-first con CRDTs (complejo, overkill)
2. Simple queue with retry (no resuelve conflictos)
3. Hybrid: Optimistic writes + conflict detection on reconnect

**Decisión:** Opción 3

**Razonamiento:** CRDTs son overpower para nuestro caso (solo 
un dispositivo por repartidor). Queue simple no detecta cuando 
el repartidor y oficina modificaron mismo pedido.

**Trade-off:** Aceptamos complejidad de resolución de conflictos
manual en casos edge (0.1% estimado).

**Resultado esperado:** 99.9% casos automáticos, 0.1% requieren
intervención del dispatcher.

**Revisar:** Métricas reales en 3 meses.
```

### 5.3 Análisis de Escenarios

Para decisiones arquitectónicas importantes, analiza:

| Escenario | Probabilidad | Impacto | Mitigación |
|-----------|-------------|---------|------------|
| User base crece 10x en 6 meses | Baja | Alto | Arquitectura modular permite scaling horizontal de equipos |
| API externa depreca endpoint | Media | Medio | Abstract with adapter, swap cost: 2 días |
| Regulación nueva en Brasil | Alta | Alto | Compliance engine extensible |
| Key developer leaves | Media | Medio | ADRs + tests como documentación viva |

---

## 6. Caso de Estudio: Arquitectura Real sin Nombre

### El Problema

App de telemedicina con:
- Video calls (WebRTC)
- Chat persistente
- Records médicos (HIPAA compliance)
- Prescripción electrónica
- Integration con 4 sistemas hospitalarios diferentes
- Debe funcionar en áreas rurales con mala conexión

### Análisis de Fuerzas

```
HIPAA (hard constraint) ────────┐
                              │
Offline availability ───────────┼──► Privacidad + Disponibilidad
                              │    vs Simplicidad
Real-time requirements ─────────┘

Multi-tenancy (hospitales) ───┐
                              ├──► Flexibilidad vs Uniformidad
HIPAA audit trail ────────────┘
```

### La Arquitectura Resultante

```
┌──────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER (SwiftUI + UIKit híbrido)            │
│  - Native UI per platform                                │
│  - Shared ViewModels with @Observable                    │
└──────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────────────────────────────────────┐
│  APPLICATION LAYER                                       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │
│  │ Consultation │ │   Chat       │ │  Records     │     │
│  │   Use Cases  │ │  Use Cases   │ │  Use Cases   │     │
│  └──────────────┘ └──────────────┘ └──────────────┘     │
│  All return: AsyncStream<DomainEvent>                     │
└──────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────────────────────────────────────┐
│  DOMAIN LAYER                                            │
│  - Entities: Patient, Consultation, Prescription         │
│  - HIPAA rules encoded as DomainService validators       │
│  - Event sourcing for audit trail (compliance)           │
└──────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────────────────────────────────────┐
│  INFRASTRUCTURE (Multi-adapter)                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │
│  │ WebRTC ACL   │ │  Chat ACL    │ │ EHR Adapters│     │
│  │ (Twilio)     │ │  (Stream)    │ │ (4 hospitals)│     │
│  └──────────────┘ └──────────────┘ └──────────────┘     │
│  Each maps external API to domain protocols              │
└──────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────────────────────────────────────┐
│  PERSISTENCE (Dual strategy)                             │
│  - Core Data: HIPAA-sensitive data (encrypted)          │
│  - Filesystem: Video recordings (large, external refs) │
│  - Sync: Custom with conflict resolution per entity type │
└──────────────────────────────────────────────────────────┘
```

### Decisiones No Estándar

1. **Event Sourcing para audit trail:** No es "event sourcing tradicional", solo guardamos events para compliance. Usado en 0.1% de casos pero requerido legalmente.

2. **Dual Persistence:** Core Data para datos estructurados, filesystem para blobs. Normalmente no mezclamos, pero los videos son grandes y no queryables.

3. **WebRTC + Chat separados:** Mismo proveedor podría hacer ambos, pero separados nos permiten cambiar uno sin el otro. Chat es más estable que video.

4. **Use Cases retornan AsyncStream:** No usamos completion handlers ni simple async. Necesitamos stream de events porque una consulta tiene múltiples fases (waiting, connected, recording, ended).

---

## 7. Ejercicios de Pensamiento Arquitectónico

### Ejercicio 1: Diseña para el Peor Caso

**Escenario:** Tu app es un dashboard para operadores de central de emergencias. El peor caso posible es: terremoto masivo, red colapsada, pero sistema debe seguir operando para coordinar rescates.

**Preguntas:**
1. ¿Qué invariantes son absolutos? ("Nunca perdemos un mensaje de emergencia")
2. ¿Qué puedes sacrificar? (UI puede ser fea, offline puede ser read-only)
3. ¿Qué arquitectura emerge de esas constraints?

**Spoiler:** Probablemente no sea Clean Architecture pura. Probablemente involucre: queue persistente, replication local, y modo "degradado" explícito.

### Ejercicio 2: El Sistema que Nadie Diseñó

**Escenario:** Dos empresas se fusionan. App A usa MVVM + Combine. App B usa VIPER + RxSwift. Deben convertirse en una sola app en 6 meses.

**Preguntas:**
1. ¿Migras todo a un patrón? ¿Cuál?
2. ¿Mantienes ambos en coexistencia perpetua?
3. ¿Cómo defines "hecho" para esta migración?

**Spoiler:** La respuesta correcta probablemente es "depende del equipo y el código". No hay solución universal.

### Ejercicio 3: La Feature Imposible

**Escenario:** Product Manager pide "tiempo real colaborativo" (como Google Docs) en tu app de notas. Tu stack actual es offline-first con sync eventual.

**Preguntas:**
1. ¿Es esto realmente necesario o es "nice to have"?
2. ¿Puedes hacer versión simplificada que satisfaga el 80% del valor?
3. ¿Cuál es el coste real de cambiar toda la arquitectura?

**Spoiler:** A veces "no" es la respuesta arquitectónica correcta. O "sí, pero en versión 2.0 el año que viene".

---

## 8. El Mindset del Arquitecto Adaptativo

### Principios Fundamentales

1. **"No existe la arquitectura perfecta, solo la adecuada para este contexto"**

2. **"Cada decisión es un trade-off documentado"** - Si no sabes qué sacrificaste, no tomaste una decisión, tomaste un default.

3. **"El código es el diagrama, el diagrama es una aproximación"** - El sistema real es lo que corre, no lo que dibujaste.

4. **"Las mejores arquitecturas evolucionan, no se diseñan perfectas"** - Planifica la evolución, no el estado final.

5. **"La arquitectura es sobre personas tanto como sobre código"** - Conway's Law es real. Diseña para el equipo que tienes, no el que quieres.

### El Ciclo de Aprendizaje

```
    ┌─────────────────┐
    │  ENFRENTA      │
    │  problema real │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  ANALIZA        │
    │  fuerzas        │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  DISEÑA         │
    │  3 alternativas │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  IMPLEMENTA     │
    │  la mejor       │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  MIDE           │
    │  resultados     │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  DOCUMENTA      │
    │  y comparte     │
    └────────┬────────┘
             │
             └────────────► (vuelve al inicio)
```

---

## Entregable de esta Lección

Tu **"Architecture Decision Portfolio"** personal:

1. **3 problemas reales** que hayas enfrentado (o simulado)
2. **Análisis de fuerzas** para cada uno
3. **Alternativas consideradas** (mínimo 2 por problema)
4. **Decisión tomada** con justificación
5. **Trade-offs aceptados** explícitamente
6. **Resultado medido** (o cómo lo medirías)
7. **Lección aprendida** para próxima vez

Este portfolio demuestra que no solo aplicas patrones, **piensas como arquitecto**.

---

## Recursos de Profundización

- ["Software Architecture: The Hard Parts"](https://www.amazon.com/Software-Architecture-Handbooks-Neal-Ford/dp/1492086894) - Análisis de trade-offs reales
- ["Building Evolutionary Architectures"](https://www.amazon.com/Building-Evolutionary-Architectures-Support-Constant/dp/1491986360) - Arquitecturas que cambian
- [Architecture Katas](https://archkatas.org/) - Práctica de decisiones bajo incertidumbre
- [The Macroscope](https://mikefisher.substack.com/) - Pensamiento sistémico aplicado a software

---

> *"La arquitectura no es seguir recetas. Es entender qué estás cocinando, por qué, para quién, y bajo qué constraints. Las recetas son útiles, pero el chef adaptativo sabe cuándo improvisar."*
