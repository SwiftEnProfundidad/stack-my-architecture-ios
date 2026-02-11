import FeatureCatalogData
import FeatureCatalogDomain
import FeatureCatalogPersistenceSwiftData
import FeatureCatalogUI
import FeatureLoginData
import FeatureLoginDomain
import FeatureLoginUI
import Foundation

@MainActor
public struct AppCompositionRoot {
    public let navigation: NavigationStore
    public let loginViewModel: LoginViewModel
    public let catalogViewModel: CatalogViewModel?

    public init(
        authRepository: any AuthRepository = InMemoryAuthRepository(),
        catalogRepository: (any CatalogRepository)? = nil
    ) {
        let navigation = NavigationStore()
        let loginUseCase = AuthenticateUserUseCase(repository: authRepository)
        let loginViewModel = LoginViewModel(useCase: loginUseCase, navigator: navigation)
        let catalogViewModel = catalogRepository.map {
            CatalogViewModel(useCase: LoadCatalogUseCase(repository: $0))
        }

        self.navigation = navigation
        self.loginViewModel = loginViewModel
        self.catalogViewModel = catalogViewModel
    }

    public static func makeCatalogRepositoryWithSwiftData(
        remote: any CatalogRemoteDataSource = DefaultCatalogRemoteDataSource(),
        connectivity: any ConnectivityChecking = InMemoryConnectivityChecker(online: true),
        ttlSeconds: TimeInterval = 300,
        inMemory: Bool = true,
        observability: any CatalogObservability = NoOpCatalogObservability()
    ) throws -> any CatalogRepository {
        let cacheStore = try SwiftDataCatalogCacheStore(inMemory: inMemory)
        return CachedCatalogRepository(
            remote: remote,
            cache: cacheStore,
            connectivity: connectivity,
            ttlSeconds: ttlSeconds,
            observability: observability
        )
    }
}
