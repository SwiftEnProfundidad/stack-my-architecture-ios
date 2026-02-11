import FeatureCatalogDomain
import Foundation

public struct CachedCatalog: Equatable, Sendable {
    public let products: [Product]
    public let timestamp: Date

    public init(products: [Product], timestamp: Date) {
        self.products = products
        self.timestamp = timestamp
    }
}

