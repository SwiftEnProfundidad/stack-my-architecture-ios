public protocol CatalogRepository: Sendable {
    func fetchCatalog() async throws -> [Product]
}

