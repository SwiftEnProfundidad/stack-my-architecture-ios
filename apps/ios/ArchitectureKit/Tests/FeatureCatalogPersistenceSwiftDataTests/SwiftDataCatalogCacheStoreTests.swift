import FeatureCatalogDomain
@testable import FeatureCatalogPersistenceSwiftData
import Foundation
import XCTest

final class SwiftDataCatalogCacheStoreTests: XCTestCase {
    func test_load_onEmptyStore_returnsNil() async throws {
        let sut = try SwiftDataCatalogCacheStore(inMemory: true)

        let result = try await sut.load()

        XCTAssertNil(result)
    }

    func test_saveThenLoad_returnsStoredProductsAndTimestamp() async throws {
        let sut = try SwiftDataCatalogCacheStore(inMemory: true)
        let timestamp = Date(timeIntervalSince1970: 1_234)
        let products = [
            Product(id: "1", title: "Bike", price: 199.0),
            Product(id: "2", title: "Helmet", price: 49.0)
        ]

        try await sut.save(products: products, timestamp: timestamp)
        let loaded = try await sut.load()

        XCTAssertEqual(loaded?.products, products)
        XCTAssertEqual(loaded?.timestamp, timestamp)
    }

    func test_clear_removesCachedProducts() async throws {
        let sut = try SwiftDataCatalogCacheStore(inMemory: true)
        try await sut.save(
            products: [Product(id: "1", title: "Bike", price: 199.0)],
            timestamp: Date()
        )

        try await sut.clear()

        let result = try await sut.load()
        XCTAssertNil(result)
    }
}

