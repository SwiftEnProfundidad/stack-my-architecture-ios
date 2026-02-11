import FeatureCatalogDomain
import Foundation

public protocol CatalogRemoteDataSource: Sendable {
    func fetchProducts() async throws -> [Product]
}

public protocol CatalogCacheStore: Sendable {
    func load() async throws -> CachedCatalog?
    func save(products: [Product], timestamp: Date) async throws
    func clear() async throws
}

public protocol ConnectivityChecking: Sendable {
    func isOnline() async -> Bool
}

public enum CatalogLoadPath: Equatable, Sendable {
    case remote
    case fallbackCache
    case offlineCache
    case offlineNoCache
    case offlineStaleCache
    case networkNoCache
}

public struct CatalogFetchMetric: Equatable, Sendable {
    public let path: CatalogLoadPath
    public let durationMs: Double
    public let cacheHit: Bool

    public init(path: CatalogLoadPath, durationMs: Double, cacheHit: Bool) {
        self.path = path
        self.durationMs = durationMs
        self.cacheHit = cacheHit
    }
}

public protocol CatalogObservability: Sendable {
    func record(_ metric: CatalogFetchMetric) async
}

public actor InMemoryCatalogObservability: CatalogObservability {
    private var metrics: [CatalogFetchMetric] = []

    public init() {}

    public func record(_ metric: CatalogFetchMetric) async {
        metrics.append(metric)
    }

    public func snapshot() async -> [CatalogFetchMetric] {
        metrics
    }
}

public struct NoOpCatalogObservability: CatalogObservability {
    public init() {}

    public func record(_ metric: CatalogFetchMetric) async {}
}
