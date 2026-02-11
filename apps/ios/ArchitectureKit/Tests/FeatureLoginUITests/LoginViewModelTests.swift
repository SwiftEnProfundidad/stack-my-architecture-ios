import AppContracts
import XCTest
@testable import FeatureLoginDomain
@testable import FeatureLoginUI

@MainActor
private final class LoginNavigatorSpy: LoginNavigating {
    private(set) var goToCatalogCalls = 0

    func goToCatalog() {
        goToCatalogCalls += 1
    }
}

private actor AuthRepositoryStub: AuthRepository {
    let result: Result<UserSession, Error>

    init(result: Result<UserSession, Error>) {
        self.result = result
    }

    func authenticate(credentials: Credentials) async throws -> UserSession {
        try result.get()
    }
}

@MainActor
final class LoginViewModelTests: XCTestCase {
    func test_submit_navigatesToCatalog_onSuccessfulLogin() async {
        let repository = AuthRepositoryStub(result: .success(.init(userId: "u-1", token: "token-1")))
        let useCase = AuthenticateUserUseCase(repository: repository)
        let navigator = LoginNavigatorSpy()
        let sut = LoginViewModel(useCase: useCase, navigator: navigator)
        sut.email = "user@site.com"
        sut.password = "Passw0rd!"

        await sut.submit()

        XCTAssertEqual(sut.phase, .authenticated)
        XCTAssertNil(sut.errorMessage)
        XCTAssertEqual(navigator.goToCatalogCalls, 1)
    }

    func test_submit_setsErrorAndDoesNotNavigate_onFailure() async {
        let repository = AuthRepositoryStub(result: .failure(LoginError.invalidCredentials))
        let useCase = AuthenticateUserUseCase(repository: repository)
        let navigator = LoginNavigatorSpy()
        let sut = LoginViewModel(useCase: useCase, navigator: navigator)
        sut.email = "user@site.com"
        sut.password = "Passw0rd!"

        await sut.submit()

        XCTAssertEqual(sut.phase, .idle)
        XCTAssertEqual(sut.errorMessage, "Credenciales inválidas.")
        XCTAssertEqual(navigator.goToCatalogCalls, 0)
    }
}

