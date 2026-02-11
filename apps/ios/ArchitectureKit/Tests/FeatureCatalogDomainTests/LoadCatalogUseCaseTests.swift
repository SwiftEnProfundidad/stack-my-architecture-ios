import XCTest
@testable import FeatureCatalogDomain

private enum StubError: Error, Sendable {
    case failure
}

private actor CatalogRepositoryStub: CatalogRepository {
    let result: Result<[Product], StubError>

    init(result: Result<[Product], StubError>) {
        self.result = result
    }

    func fetchCatalog() async throws -> [Product] {
        try result.get()
    }
}

final class LoadCatalogUseCaseTests: XCTestCase {
    func test_execute_returnsProducts_whenRepositorySucceeds() async throws {
        let expected = [
            Product(id: "1", title: "Bike", price: 199),
            Product(id: "2", title: "Helmet", price: 49)
        ]
        let repository = CatalogRepositoryStub(result: .success(expected))
        let sut = LoadCatalogUseCase(repository: repository)

        let products = try await sut.execute()

        XCTAssertEqual(products, expected)
    }

    func test_execute_propagatesError_whenRepositoryFails() async {
        let repository = CatalogRepositoryStub(result: .failure(.failure))
        let sut = LoadCatalogUseCase(repository: repository)

        do {
            _ = try await sut.execute()
            XCTFail("Expected error")
        } catch let error as StubError {
            XCTAssertEqual(error, .failure)
        } catch {
            XCTFail("Unexpected error: \(error)")
        }
    }
}

