import FeatureCatalogData
import FeatureCatalogDomain
import XCTest
@testable import AppComposition

@MainActor
final class CatalogCompositionSwiftDataTests: XCTestCase {
    func test_makeCatalogRepositoryWithSwiftData_wiresCatalogViewModelAndLoadsProducts() async throws {
        let remote = DefaultCatalogRemoteDataSource(
            products: [
                Product(id: "p-100", title: "Road Bike", price: 1299),
                Product(id: "p-101", title: "Gloves", price: 35)
            ]
        )
        let observability = InMemoryCatalogObservability()
        let repository = try AppCompositionRoot.makeCatalogRepositoryWithSwiftData(
            remote: remote,
            inMemory: true,
            observability: observability
        )
        let sut = AppCompositionRoot(catalogRepository: repository)

        let catalogViewModel = try XCTUnwrap(sut.catalogViewModel)
        await catalogViewModel.load()
        let metrics = await observability.snapshot()

        XCTAssertEqual(catalogViewModel.products.count, 2)
        XCTAssertEqual(catalogViewModel.products.first?.id, "p-100")
        XCTAssertEqual(metrics.last?.path, .remote)
    }
}

