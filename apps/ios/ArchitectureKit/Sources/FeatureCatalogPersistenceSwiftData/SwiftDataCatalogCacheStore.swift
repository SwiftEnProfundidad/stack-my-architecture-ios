import FeatureCatalogData
import FeatureCatalogDomain
import Foundation
import SwiftData

@Model
final class CatalogProductEntity {
    @Attribute(.unique) var productId: String
    var title: String
    var price: Double
    var cachedAt: Date

    init(productId: String, title: String, price: Double, cachedAt: Date) {
        self.productId = productId
        self.title = title
        self.price = price
        self.cachedAt = cachedAt
    }
}

public final class SwiftDataCatalogCacheStore: CatalogCacheStore, @unchecked Sendable {
    private let container: ModelContainer

    public init(container: ModelContainer) {
        self.container = container
    }

    public convenience init(inMemory: Bool) throws {
        let configuration = ModelConfiguration(isStoredInMemoryOnly: inMemory)
        let container = try ModelContainer(
            for: CatalogProductEntity.self,
            configurations: configuration
        )
        self.init(container: container)
    }

    public func load() async throws -> CachedCatalog? {
        let context = ModelContext(container)
        let descriptor = FetchDescriptor<CatalogProductEntity>(
            sortBy: [SortDescriptor(\.productId)]
        )
        let entities = try context.fetch(descriptor)

        guard !entities.isEmpty else { return nil }

        let timestamp = entities.map(\.cachedAt).min() ?? .distantPast
        let products = entities.map {
            Product(id: $0.productId, title: $0.title, price: $0.price)
        }
        return CachedCatalog(products: products, timestamp: timestamp)
    }

    public func save(products: [Product], timestamp: Date) async throws {
        let context = ModelContext(container)
        try context.delete(model: CatalogProductEntity.self)
        for product in products {
            context.insert(
                CatalogProductEntity(
                    productId: product.id,
                    title: product.title,
                    price: product.price,
                    cachedAt: timestamp
                )
            )
        }
        try context.save()
    }

    public func clear() async throws {
        let context = ModelContext(container)
        try context.delete(model: CatalogProductEntity.self)
        try context.save()
    }
}

