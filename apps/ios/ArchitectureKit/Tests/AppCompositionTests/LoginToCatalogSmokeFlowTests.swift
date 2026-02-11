import FeatureLoginData
import FeatureLoginDomain
import InfraHTTP
import InfraPersistence
import XCTest
@testable import AppComposition

private actor SmokeHTTPClientStub: HTTPClient {
    let response: HTTPResponse

    init(response: HTTPResponse) {
        self.response = response
    }

    func send(_ request: HTTPRequest) async throws -> HTTPResponse {
        response
    }
}

@MainActor
final class LoginToCatalogSmokeFlowTests: XCTestCase {
    func test_smoke_loginToCatalog_withAuthHTTPRepository() async throws {
        let body = """
        {
          "user_id": "smoke-user",
          "token": "smoke-token"
        }
        """
        let httpClient = SmokeHTTPClientStub(
            response: HTTPResponse(statusCode: 200, body: Data(body.utf8))
        )
        let sessionStore = InMemorySessionStore()
        let authRepository = AuthHTTPRepository(httpClient: httpClient, sessionStore: sessionStore)
        let sut = AppCompositionRoot(authRepository: authRepository)
        sut.loginViewModel.email = "student@course.dev"
        sut.loginViewModel.password = "Passw0rd!"

        await sut.loginViewModel.submit()
        let persistedSession = try await sessionStore.load()

        XCTAssertEqual(sut.navigation.routes, [.login, .catalog])
        XCTAssertEqual(persistedSession, UserSession(userId: "smoke-user", token: "smoke-token"))
    }
}

