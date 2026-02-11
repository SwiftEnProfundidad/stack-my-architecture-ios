import FeatureCatalogData
import FeatureCatalogDomain
import Foundation

private actor DelayedRemoteDataSource: CatalogRemoteDataSource {
    private let products: [Product]
    private let delayNanoseconds: UInt64

    init(products: [Product], delayNanoseconds: UInt64) {
        self.products = products
        self.delayNanoseconds = delayNanoseconds
    }

    func fetchProducts() async throws -> [Product] {
        try? await Task.sleep(nanoseconds: delayNanoseconds)
        return products
    }
}

@main
enum ArchitectureBenchmarks {
    static func main() async throws {
        let environment = ProcessInfo.processInfo.environment
        let remoteDelayNanoseconds = UInt64(environment["BENCH_REMOTE_DELAY_NS"] ?? "120000000") ?? 120_000_000
        let ttlSeconds = Double(environment["BENCH_TTL_SECONDS"] ?? "300") ?? 300

        let remote = DelayedRemoteDataSource(
            products: [Product(id: "bench-1", title: "Road Bike", price: 1500)],
            delayNanoseconds: remoteDelayNanoseconds
        )
        let cache = InMemoryCatalogCacheStore()
        let connectivity = InMemoryConnectivityChecker(online: true)
        let observability = InMemoryCatalogObservability()
        let repository = CachedCatalogRepository(
            remote: remote,
            cache: cache,
            connectivity: connectivity,
            ttlSeconds: ttlSeconds,
            observability: observability
        )

        _ = try await repository.fetchCatalog()
        await connectivity.setOnline(false)
        _ = try await repository.fetchCatalog()

        let metrics = await observability.snapshot()
        let cold = metrics.first(where: { $0.path == .remote })
        let warm = metrics.first(where: { $0.path == .offlineCache || $0.path == .fallbackCache })

        let coldMs = cold?.durationMs ?? 0
        let warmMs = warm?.durationMs ?? 0
        let ratio = coldMs > 0 ? (warmMs / coldMs) : 0

        let output: [String: Any] = [
            "cold_ms": round(coldMs * 100) / 100,
            "warm_ms": round(warmMs * 100) / 100,
            "warm_to_cold_ratio": round(ratio * 10000) / 10000,
            "remote_delay_ns": remoteDelayNanoseconds
        ]

        let jsonData = try JSONSerialization.data(withJSONObject: output, options: [.sortedKeys])
        if let jsonString = String(data: jsonData, encoding: .utf8) {
            print(jsonString)
        }
    }
}

