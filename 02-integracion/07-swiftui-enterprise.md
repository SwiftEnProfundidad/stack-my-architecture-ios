# SwiftUI Enterprise: Patrones Imprescindibles

> Esta lección se divide en tres partes para facilitar la lectura y el estudio progresivo.

## Partes

- **[Parte 1 — Navegación, Modales e Interacción](./07a-swiftui-enterprise-navegacion.md)** (~17 min)
  TabView, @Environment, .sheet, .alert, .refreshable, .searchable, .toolbar, @Binding, Form/Section

- **[Parte 2 — Composición, Rendimiento y APIs Modernas](./07b-swiftui-enterprise-composicion.md)** (~17 min)
  NavigationLink, ViewModifier, @Bindable, Performance, Animaciones, Accesibilidad, APIs modernas, View Composition

- **[Parte 3 — Liquid Glass, Ejercicio y Cierre](./07c-swiftui-enterprise-moderno.md)** (~10 min)
  Liquid Glass (iOS 26+), resumen completo, ejercicio guiado aplicado al scaffold, cierre

## Por qué está dividida

Esta lección cubre 18 patrones SwiftUI enterprise con código detallado. Dividirla en partes permite:
- Estudiar un bloque temático por sesión sin perder contexto.
- Revisitar patrones específicos sin navegar 1500 líneas.
- Facilitar la búsqueda de código de referencia.

---

Puedes leer las tres partes en orden o saltar directamente a la sección que necesites.

---

## 🔭 Explora el scaffold — SwiftUI enterprise en LoginView y CatalogView

```bash
# Patrones SwiftUI en las vistas del scaffold
cat apps/ios/ArchitectureKit/Sources/FeatureLoginUI/LoginView.swift
cat apps/ios/ArchitectureKit/Sources/FeatureCatalogUI/CatalogView.swift
```

Las vistas del scaffold son las implementaciones de referencia para los patrones enterprise que describe esta lección: composición de vistas pequeñas, `@Bindable` en lugar de `@ObservedObject`, y accesibilidad incorporada con `accessibilityIdentifier`.

