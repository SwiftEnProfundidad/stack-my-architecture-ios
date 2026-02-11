import FeatureCatalogData
import FeatureCatalogDomain
import FeatureLoginData
import InfraHTTP
import InfraPersistence
import XCTest
@testable import AppComposition

private actor EndToEndHTTPClientStub: HTTPClient {
    let response: HTTPResponse

    init(response: HTTPResponse) {
        self.response = response
    }

    func send(_ request: HTTPRequest) async throws -> HTTPResponse {
        response
    }
}

@MainActor
final class AppFlowEndToEndSmokeTests: XCTestCase {
    func test_endToEnd_loginThenLoadCatalog_withRealCompositionWiring() async throws {
        let loginBody = """
        {
          "user_id": "e2e-user",
          "token": "e2e-token"
        }
        """
        let authHTTPClient = EndToEndHTTPClientStub(
            response: HTTPResponse(statusCode: 200, body: Data(loginBody.utf8))
        )
        let sessionStore = InMemorySessionStore()
        let authRepository = AuthHTTPRepository(httpClient: authHTTPClient, sessionStore: sessionStore)

        let catalogRemote = DefaultCatalogRemoteDataSource(
            products: [
                Product(id: "cat-1", title: "Road Bike", price: 1099),
                Product(id: "cat-2", title: "Jersey", price: 79)
            ]
        )
        let catalogRepository = try AppCompositionRoot.makeCatalogRepositoryWithSwiftData(
            remote: catalogRemote,
            inMemory: true
        )

        let sut = AppCompositionRoot(
            authRepository: authRepository,
            catalogRepository: catalogRepository
        )
        sut.loginViewModel.email = "student@course.dev"
        sut.loginViewModel.password = "Passw0rd!"

        await sut.loginViewModel.submit()
        let persistedSession = try await sessionStore.load()
        let catalogViewModel = try XCTUnwrap(sut.catalogViewModel)
        await catalogViewModel.load()

        XCTAssertEqual(sut.navigation.routes, [.login, .catalog])
        XCTAssertEqual(persistedSession?.userId, "e2e-user")
        XCTAssertEqual(catalogViewModel.products.count, 2)
        XCTAssertNil(catalogViewModel.errorMessage)
    }
}

