import FeatureCatalogData
import FeatureCatalogDomain
import Foundation
import XCTest

private actor CountingCatalogRemoteDataSource: CatalogRemoteDataSource {
    private let products: [Product]
    private let delayNanoseconds: UInt64
    private var calls = 0

    init(products: [Product], delayNanoseconds: UInt64) {
        self.products = products
        self.delayNanoseconds = delayNanoseconds
    }

    func fetchProducts() async throws -> [Product] {
        calls += 1
        try? await Task.sleep(nanoseconds: delayNanoseconds)
        return products
    }

    func callCount() async -> Int {
        calls
    }
}

final class CatalogConcurrencyHardeningTests: XCTestCase {
    func test_fetchCatalog_concurrentOnlineLoad_returnsConsistentResults() async throws {
        let expectedProducts = [
            Product(id: "cc-1", title: "Bike", price: 220),
            Product(id: "cc-2", title: "Helmet", price: 60)
        ]
        let remote = CountingCatalogRemoteDataSource(
            products: expectedProducts,
            delayNanoseconds: 30_000_000
        )
        let cache = InMemoryCatalogCacheStore()
        let connectivity = InMemoryConnectivityChecker(online: true)
        let observability = InMemoryCatalogObservability()
        let sut = CachedCatalogRepository(
            remote: remote,
            cache: cache,
            connectivity: connectivity,
            ttlSeconds: 300,
            observability: observability
        )

        let concurrentRequests = 30
        let results = try await withThrowingTaskGroup(of: [Product].self, returning: [[Product]].self) { group in
            for _ in 0..<concurrentRequests {
                group.addTask {
                    try await sut.fetchCatalog()
                }
            }

            var collected: [[Product]] = []
            for try await products in group {
                collected.append(products)
            }
            return collected
        }

        let remoteCalls = await remote.callCount()
        XCTAssertEqual(results.count, concurrentRequests)
        XCTAssertTrue(results.allSatisfy { $0 == expectedProducts })
        XCTAssertEqual(remoteCalls, concurrentRequests)

        let metrics = await observability.snapshot()
        XCTAssertEqual(metrics.count, concurrentRequests)
        XCTAssertTrue(metrics.allSatisfy { $0.path == .remote })
    }

    func test_fetchCatalog_concurrentOfflineLoad_usesCacheWithoutRemoteCalls() async throws {
        let now = Date(timeIntervalSince1970: 2_000)
        let cachedProducts = [
            Product(id: "cc-cache-1", title: "Bottle", price: 12),
            Product(id: "cc-cache-2", title: "Pump", price: 35)
        ]
        let remote = CountingCatalogRemoteDataSource(
            products: [Product(id: "remote", title: "ShouldNotBeUsed", price: 999)],
            delayNanoseconds: 10_000_000
        )
        let cache = InMemoryCatalogCacheStore(
            cached: CachedCatalog(
                products: cachedProducts,
                timestamp: Date(timeIntervalSince1970: 1_900)
            )
        )
        let connectivity = InMemoryConnectivityChecker(online: false)
        let observability = InMemoryCatalogObservability()
        let sut = CachedCatalogRepository(
            remote: remote,
            cache: cache,
            connectivity: connectivity,
            ttlSeconds: 300,
            observability: observability,
            now: { now }
        )

        let concurrentRequests = 40
        let results = try await withThrowingTaskGroup(of: [Product].self, returning: [[Product]].self) { group in
            for _ in 0..<concurrentRequests {
                group.addTask {
                    try await sut.fetchCatalog()
                }
            }

            var collected: [[Product]] = []
            for try await products in group {
                collected.append(products)
            }
            return collected
        }

        let remoteCalls = await remote.callCount()
        XCTAssertEqual(results.count, concurrentRequests)
        XCTAssertTrue(results.allSatisfy { $0 == cachedProducts })
        XCTAssertEqual(remoteCalls, 0)

        let metrics = await observability.snapshot()
        XCTAssertEqual(metrics.count, concurrentRequests)
        XCTAssertTrue(metrics.allSatisfy { $0.path == .offlineCache && $0.cacheHit })
    }
}
