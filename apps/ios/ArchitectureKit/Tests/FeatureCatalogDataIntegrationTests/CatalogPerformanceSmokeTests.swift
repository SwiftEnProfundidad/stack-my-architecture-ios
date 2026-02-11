import FeatureCatalogData
import FeatureCatalogDomain
import Foundation
import XCTest

private actor DelayedCatalogRemoteDataSource: CatalogRemoteDataSource {
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

final class CatalogPerformanceSmokeTests: XCTestCase {
    func test_catalogLoad_warmCacheIsFasterThanColdRemote() async throws {
        let slowRemote = DelayedCatalogRemoteDataSource(
            products: [Product(id: "perf-1", title: "Bike", price: 200)],
            delayNanoseconds: 120_000_000
        )
        let cache = InMemoryCatalogCacheStore()
        let connectivity = InMemoryConnectivityChecker(online: true)
        let observability = InMemoryCatalogObservability()
        let sut = CachedCatalogRepository(
            remote: slowRemote,
            cache: cache,
            connectivity: connectivity,
            ttlSeconds: 300,
            observability: observability
        )

        _ = try await sut.fetchCatalog()
        await connectivity.setOnline(false)
        _ = try await sut.fetchCatalog()

        let metrics = await observability.snapshot()
        XCTAssertEqual(metrics.count, 2)

        let cold = metrics[0]
        let warm = metrics[1]

        XCTAssertEqual(cold.path, .remote)
        XCTAssertEqual(cold.cacheHit, false)
        XCTAssertEqual(warm.path, .offlineCache)
        XCTAssertEqual(warm.cacheHit, true)

        XCTAssertGreaterThan(cold.durationMs, 80)
        XCTAssertLessThan(warm.durationMs, cold.durationMs)
        XCTAssertLessThan(warm.durationMs, 50)
    }
}

