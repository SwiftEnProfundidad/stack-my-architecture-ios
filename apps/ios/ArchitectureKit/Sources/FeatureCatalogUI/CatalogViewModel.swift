import FeatureCatalogDomain

@MainActor
public final class CatalogViewModel {
    public private(set) var products: [Product] = []
    public private(set) var isLoading = false
    public private(set) var errorMessage: String?

    private let useCase: LoadCatalogUseCase

    public init(useCase: LoadCatalogUseCase) {
        self.useCase = useCase
    }

    public func load() async {
        isLoading = true
        errorMessage = nil
        do {
            products = try await useCase.execute()
        } catch {
            errorMessage = "No se pudo cargar el catálogo."
        }
        isLoading = false
    }
}

