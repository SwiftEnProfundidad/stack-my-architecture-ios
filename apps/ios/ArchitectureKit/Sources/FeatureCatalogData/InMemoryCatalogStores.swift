import FeatureCatalogDomain
import Foundation

public actor InMemoryCatalogCacheStore: CatalogCacheStore {
    private var cached: CachedCatalog?

    public init(cached: CachedCatalog? = nil) {
        self.cached = cached
    }

    public func load() async throws -> CachedCatalog? {
        cached
    }

    public func save(products: [Product], timestamp: Date) async throws {
        cached = CachedCatalog(products: products, timestamp: timestamp)
    }

    public func clear() async throws {
        cached = nil
    }
}

public actor InMemoryConnectivityChecker: ConnectivityChecking {
    private var online: Bool

    public init(online: Bool = true) {
        self.online = online
    }

    public func setOnline(_ newValue: Bool) {
        online = newValue
    }

    public func isOnline() async -> Bool {
        online
    }
}

