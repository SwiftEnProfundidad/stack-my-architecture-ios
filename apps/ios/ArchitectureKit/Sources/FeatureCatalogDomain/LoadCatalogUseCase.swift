public struct LoadCatalogUseCase: Sendable {
    private let repository: any CatalogRepository

    public init(repository: any CatalogRepository) {
        self.repository = repository
    }

    public func execute() async throws -> [Product] {
        try await repository.fetchCatalog()
    }
}
