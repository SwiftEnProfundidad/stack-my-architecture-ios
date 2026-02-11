import FeatureCatalogData
import FeatureCatalogDomain
import Foundation
import XCTest

private enum RemoteError: Error, Sendable {
    case failed
}

private actor CatalogRemoteSpy: CatalogRemoteDataSource {
    private let result: Result<[Product], RemoteError>
    private(set) var calls = 0

    init(result: Result<[Product], RemoteError>) {
        self.result = result
    }

    func fetchProducts() async throws -> [Product] {
        calls += 1
        return try result.get()
    }

    func callCount() -> Int {
        calls
    }
}

final class CachedCatalogRepositoryIntegrationTests: XCTestCase {
    func test_fetchCatalog_online_remoteSuccess_returnsFreshAndSavesCache() async throws {
        let now = Date(timeIntervalSince1970: 1_000)
        let remoteProducts = [Product(id: "1", title: "Bike", price: 199.0)]
        let remote = CatalogRemoteSpy(result: .success(remoteProducts))
        let cache = InMemoryCatalogCacheStore()
        let connectivity = InMemoryConnectivityChecker(online: true)
        let observability = InMemoryCatalogObservability()
        let sut = CachedCatalogRepository(
            remote: remote,
            cache: cache,
            connectivity: connectivity,
            ttlSeconds: 300,
            observability: observability,
            now: { now }
        )

        let result = try await sut.fetchCatalog()
        let cached = try await cache.load()
        let metrics = await observability.snapshot()

        XCTAssertEqual(result, remoteProducts)
        XCTAssertEqual(cached?.products, remoteProducts)
        XCTAssertEqual(cached?.timestamp, now)
        XCTAssertEqual(metrics.last?.path, .remote)
        XCTAssertEqual(metrics.last?.cacheHit, false)
    }

    func test_fetchCatalog_offline_validCache_returnsCache() async throws {
        let now = Date(timeIntervalSince1970: 1_000)
        let cachedProducts = [Product(id: "cache-1", title: "Helmet", price: 49.0)]
        let cached = CachedCatalog(products: cachedProducts, timestamp: Date(timeIntervalSince1970: 900))
        let remote = CatalogRemoteSpy(result: .failure(.failed))
        let cache = InMemoryCatalogCacheStore(cached: cached)
        let connectivity = InMemoryConnectivityChecker(online: false)
        let sut = CachedCatalogRepository(
            remote: remote,
            cache: cache,
            connectivity: connectivity,
            ttlSeconds: 300,
            now: { now }
        )

        let result = try await sut.fetchCatalog()
        let remoteCalls = await remote.callCount()

        XCTAssertEqual(result, cachedProducts)
        XCTAssertEqual(remoteCalls, 0)
    }

    func test_fetchCatalog_online_remoteFails_fallsBackToValidCache() async throws {
        let now = Date(timeIntervalSince1970: 1_000)
        let cachedProducts = [Product(id: "cache-2", title: "Pump", price: 29.0)]
        let cached = CachedCatalog(products: cachedProducts, timestamp: Date(timeIntervalSince1970: 850))
        let remote = CatalogRemoteSpy(result: .failure(.failed))
        let cache = InMemoryCatalogCacheStore(cached: cached)
        let connectivity = InMemoryConnectivityChecker(online: true)
        let observability = InMemoryCatalogObservability()
        let sut = CachedCatalogRepository(
            remote: remote,
            cache: cache,
            connectivity: connectivity,
            ttlSeconds: 300,
            observability: observability,
            now: { now }
        )

        let result = try await sut.fetchCatalog()
        let remoteCalls = await remote.callCount()
        let metrics = await observability.snapshot()

        XCTAssertEqual(result, cachedProducts)
        XCTAssertEqual(remoteCalls, 1)
        XCTAssertEqual(metrics.last?.path, .fallbackCache)
        XCTAssertEqual(metrics.last?.cacheHit, true)
    }

    func test_fetchCatalog_offline_staleCache_throwsStaleError() async throws {
        let now = Date(timeIntervalSince1970: 2_000)
        let cachedProducts = [Product(id: "cache-3", title: "Bottle", price: 12.0)]
        let cached = CachedCatalog(products: cachedProducts, timestamp: Date(timeIntervalSince1970: 1_000))
        let remote = CatalogRemoteSpy(result: .failure(.failed))
        let cache = InMemoryCatalogCacheStore(cached: cached)
        let connectivity = InMemoryConnectivityChecker(online: false)
        let sut = CachedCatalogRepository(
            remote: remote,
            cache: cache,
            connectivity: connectivity,
            ttlSeconds: 300,
            now: { now }
        )

        do {
            _ = try await sut.fetchCatalog()
            XCTFail("Expected stale cache error")
        } catch let error as CatalogError {
            XCTAssertEqual(error, .staleCacheUnavailable)
        } catch {
            XCTFail("Unexpected error: \(error)")
        }
    }
}
