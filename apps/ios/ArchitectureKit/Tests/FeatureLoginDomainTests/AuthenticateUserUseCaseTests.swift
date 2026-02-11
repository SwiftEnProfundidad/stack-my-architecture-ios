import XCTest
@testable import FeatureLoginDomain

private actor AuthRepositoryStub: AuthRepository {
    let result: Result<UserSession, Error>

    init(result: Result<UserSession, Error>) {
        self.result = result
    }

    func authenticate(credentials: Credentials) async throws -> UserSession {
        try result.get()
    }
}

final class AuthenticateUserUseCaseTests: XCTestCase {
    func test_execute_returnsSession_whenCredentialsAreValid() async throws {
        let expected = UserSession(userId: "u-1", token: "token-1")
        let repository = AuthRepositoryStub(result: .success(expected))
        let sut = AuthenticateUserUseCase(repository: repository)

        let session = try await sut.execute(email: "user@site.com", password: "Passw0rd!")

        XCTAssertEqual(session, expected)
    }

    func test_execute_throwsInvalidEmail_whenEmailIsMalformed() async {
        let repository = AuthRepositoryStub(result: .success(.init(userId: "u-1", token: "token-1")))
        let sut = AuthenticateUserUseCase(repository: repository)

        do {
            _ = try await sut.execute(email: "invalid-email", password: "Passw0rd!")
            XCTFail("Expected to throw")
        } catch let error as LoginError {
            XCTAssertEqual(error, .invalidEmail)
        } catch {
            XCTFail("Unexpected error: \(error)")
        }
    }

    func test_execute_throwsInvalidPassword_whenPasswordIsShort() async {
        let repository = AuthRepositoryStub(result: .success(.init(userId: "u-1", token: "token-1")))
        let sut = AuthenticateUserUseCase(repository: repository)

        do {
            _ = try await sut.execute(email: "user@site.com", password: "123")
            XCTFail("Expected to throw")
        } catch let error as LoginError {
            XCTAssertEqual(error, .invalidPassword)
        } catch {
            XCTFail("Unexpected error: \(error)")
        }
    }

    func test_execute_propagatesRepositoryError() async {
        let repository = AuthRepositoryStub(result: .failure(LoginError.invalidCredentials))
        let sut = AuthenticateUserUseCase(repository: repository)

        do {
            _ = try await sut.execute(email: "user@site.com", password: "Passw0rd!")
            XCTFail("Expected to throw")
        } catch let error as LoginError {
            XCTAssertEqual(error, .invalidCredentials)
        } catch {
            XCTFail("Unexpected error: \(error)")
        }
    }
}

