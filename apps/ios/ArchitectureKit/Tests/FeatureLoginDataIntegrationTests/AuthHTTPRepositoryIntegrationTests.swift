import FeatureLoginData
import FeatureLoginDomain
import Foundation
import InfraHTTP
import InfraPersistence
import XCTest

private actor HTTPClientSpy: HTTPClient {
    private(set) var receivedRequests: [HTTPRequest] = []
    private let result: Result<HTTPResponse, Error>

    init(result: Result<HTTPResponse, Error>) {
        self.result = result
    }

    func send(_ request: HTTPRequest) async throws -> HTTPResponse {
        receivedRequests.append(request)
        return try result.get()
    }

    func lastRequest() -> HTTPRequest? {
        receivedRequests.last
    }
}

private struct AnyError: Error, Sendable {}

final class AuthHTTPRepositoryIntegrationTests: XCTestCase {
    func test_authenticate_returnsSessionAndPersists_whenServerReturns200() async throws {
        let json = """
        {
          "user_id": "u-42",
          "token": "token-42"
        }
        """
        let response = HTTPResponse(statusCode: 200, body: Data(json.utf8))
        let httpClient = HTTPClientSpy(result: .success(response))
        let sessionStore = InMemorySessionStore()
        let sut = AuthHTTPRepository(httpClient: httpClient, sessionStore: sessionStore)
        let credentials = try Credentials(
            email: EmailAddress("student@course.dev"),
            password: Password("Passw0rd!")
        )

        let session = try await sut.authenticate(credentials: credentials)
        let persisted = try await sessionStore.load()
        let request = await httpClient.lastRequest()

        XCTAssertEqual(session, UserSession(userId: "u-42", token: "token-42"))
        XCTAssertEqual(persisted, session)
        XCTAssertEqual(request?.path, "/auth/login")
        XCTAssertEqual(request?.method, "POST")
        XCTAssertEqual(request?.headers["Content-Type"], "application/json")
    }

    func test_authenticate_throwsInvalidCredentials_whenServerReturns401() async throws {
        let response = HTTPResponse(statusCode: 401, body: Data())
        let httpClient = HTTPClientSpy(result: .success(response))
        let sessionStore = InMemorySessionStore()
        let sut = AuthHTTPRepository(httpClient: httpClient, sessionStore: sessionStore)
        let credentials = try Credentials(
            email: EmailAddress("student@course.dev"),
            password: Password("Passw0rd!")
        )

        do {
            _ = try await sut.authenticate(credentials: credentials)
            XCTFail("Expected invalid credentials")
        } catch let error as LoginError {
            XCTAssertEqual(error, .invalidCredentials)
        } catch {
            XCTFail("Unexpected error: \(error)")
        }
    }

    func test_authenticate_throwsNetwork_whenTransportFails() async throws {
        let httpClient = HTTPClientSpy(result: .failure(AnyError()))
        let sessionStore = InMemorySessionStore()
        let sut = AuthHTTPRepository(httpClient: httpClient, sessionStore: sessionStore)
        let credentials = try Credentials(
            email: EmailAddress("student@course.dev"),
            password: Password("Passw0rd!")
        )

        do {
            _ = try await sut.authenticate(credentials: credentials)
            XCTFail("Expected network error")
        } catch let error as LoginError {
            XCTAssertEqual(error, .network)
        } catch {
            XCTFail("Unexpected error: \(error)")
        }
    }
}

