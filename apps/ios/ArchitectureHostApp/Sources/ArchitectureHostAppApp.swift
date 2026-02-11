import AppComposition
import AppContracts
import FeatureCatalogDomain
import FeatureLoginData
import SwiftUI

@MainActor
final class AppStore: ObservableObject {
    @Published var route: AppRoute = .login
    @Published var email: String
    @Published var password: String
    @Published var loginError: String?
    @Published var isAuthenticating = false

    @Published var products: [Product] = []
    @Published var isCatalogLoading = false
    @Published var catalogError: String?

    private let composition: AppCompositionRoot

    init() {
        let environment = ProcessInfo.processInfo.environment
        email = environment["UITEST_LOGIN_EMAIL"] ?? "student@course.dev"
        password = environment["UITEST_LOGIN_PASSWORD"] ?? "Passw0rd!"

        let catalogRepository = try? AppCompositionRoot.makeCatalogRepositoryWithSwiftData(inMemory: true)
        composition = AppCompositionRoot(
            authRepository: InMemoryAuthRepository(),
            catalogRepository: catalogRepository
        )
        syncFromComposition()
    }

    func submitLogin() async {
        guard !isAuthenticating else { return }

        isAuthenticating = true
        composition.loginViewModel.email = email
        composition.loginViewModel.password = password
        await composition.loginViewModel.submit()
        syncFromComposition()
        isAuthenticating = false

        if route == .catalog {
            await loadCatalogIfNeeded()
        }
    }

    func loadCatalogIfNeeded() async {
        guard let catalogViewModel = composition.catalogViewModel else {
            return
        }

        guard products.isEmpty else {
            return
        }

        isCatalogLoading = true
        await catalogViewModel.load()
        products = catalogViewModel.products
        catalogError = catalogViewModel.errorMessage
        isCatalogLoading = false
    }

    private func syncFromComposition() {
        route = composition.navigation.routes.last ?? .login
        loginError = composition.loginViewModel.errorMessage
    }
}

struct RootView: View {
    @StateObject private var store = AppStore()

    var body: some View {
        Group {
            switch store.route {
            case .login:
                LoginScreen(store: store)
            case .catalog:
                CatalogScreen(store: store)
            }
        }
        .animation(.easeInOut(duration: 0.2), value: store.route)
    }
}

struct LoginScreen: View {
    @ObservedObject var store: AppStore

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Login")
                .font(.largeTitle.bold())
                .accessibilityIdentifier("login_title")

            TextField("Email", text: $store.email)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
                .keyboardType(.emailAddress)
                .textFieldStyle(.roundedBorder)
                .accessibilityIdentifier("login_email")

            SecureField("Password", text: $store.password)
                .textFieldStyle(.roundedBorder)
                .accessibilityIdentifier("login_password")

            Button {
                Task {
                    await store.submitLogin()
                }
            } label: {
                if store.isAuthenticating {
                    ProgressView()
                } else {
                    Text("Entrar")
                        .fontWeight(.semibold)
                }
            }
            .buttonStyle(.borderedProminent)
            .disabled(store.isAuthenticating)
            .accessibilityIdentifier("login_submit")

            if let loginError = store.loginError {
                Text(loginError)
                    .foregroundStyle(.red)
                    .accessibilityIdentifier("login_error")
            }

            Spacer(minLength: 0)
        }
        .padding(24)
    }
}

struct CatalogScreen: View {
    @ObservedObject var store: AppStore

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Catálogo")
                .font(.largeTitle.bold())
                .accessibilityIdentifier("catalog_title")

            if store.isCatalogLoading {
                ProgressView("Cargando catálogo...")
                    .accessibilityIdentifier("catalog_loading")
            } else if let catalogError = store.catalogError {
                Text(catalogError)
                    .foregroundStyle(.red)
                    .accessibilityIdentifier("catalog_error")
            } else {
                List(store.products, id: \.id) { product in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(product.title)
                            .font(.headline)
                            .accessibilityIdentifier("catalog_item_title_\(product.id)")

                        Text(product.price, format: .currency(code: "EUR"))
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    .padding(.vertical, 6)
                }
                .listStyle(.plain)
                .accessibilityIdentifier("catalog_list")
            }
        }
        .padding(24)
        .task {
            await store.loadCatalogIfNeeded()
        }
    }
}

@main
struct ArchitectureHostAppApp: App {
    var body: some Scene {
        WindowGroup {
            RootView()
        }
    }
}
