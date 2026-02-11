import FeatureCatalogDomain
import Foundation

public struct CachedCatalogRepository: CatalogRepository, Sendable {
    private let remote: any CatalogRemoteDataSource
    private let cache: any CatalogCacheStore
    private let connectivity: any ConnectivityChecking
    private let observability: any CatalogObservability
    private let ttlSeconds: TimeInterval
    private let now: @Sendable () -> Date

    public init(
        remote: any CatalogRemoteDataSource,
        cache: any CatalogCacheStore,
        connectivity: any ConnectivityChecking,
        ttlSeconds: TimeInterval = 300,
        observability: any CatalogObservability = NoOpCatalogObservability(),
        now: @escaping @Sendable () -> Date = Date.init
    ) {
        self.remote = remote
        self.cache = cache
        self.connectivity = connectivity
        self.observability = observability
        self.ttlSeconds = max(1, ttlSeconds)
        self.now = now
    }

    public func fetchCatalog() async throws -> [Product] {
        let startedAt = Date()
        let currentTime = now()
        let durationMs: () -> Double = {
            Date().timeIntervalSince(startedAt) * 1000
        }

        if await connectivity.isOnline() {
            do {
                let freshProducts = try await remote.fetchProducts()
                try? await cache.save(products: freshProducts, timestamp: currentTime)
                await observability.record(
                    CatalogFetchMetric(path: .remote, durationMs: durationMs(), cacheHit: false)
                )
                return freshProducts
            } catch {
                if let fallback = try? await cache.load(), isValid(fallback, currentTime) {
                    await observability.record(
                        CatalogFetchMetric(path: .fallbackCache, durationMs: durationMs(), cacheHit: true)
                    )
                    return fallback.products
                }
                await observability.record(
                    CatalogFetchMetric(path: .networkNoCache, durationMs: durationMs(), cacheHit: false)
                )
                throw CatalogError.network
            }
        }

        guard let cached = try? await cache.load() else {
            await observability.record(
                CatalogFetchMetric(path: .offlineNoCache, durationMs: durationMs(), cacheHit: false)
            )
            throw CatalogError.offlineNoCache
        }
        guard isValid(cached, currentTime) else {
            await observability.record(
                CatalogFetchMetric(path: .offlineStaleCache, durationMs: durationMs(), cacheHit: false)
            )
            throw CatalogError.staleCacheUnavailable
        }
        await observability.record(
            CatalogFetchMetric(path: .offlineCache, durationMs: durationMs(), cacheHit: true)
        )
        return cached.products
    }

    private func isValid(_ cached: CachedCatalog, _ now: Date) -> Bool {
        now.timeIntervalSince(cached.timestamp) <= ttlSeconds
    }
}
