import AppContracts
import XCTest
@testable import AppComposition

@MainActor
final class AppCompositionRootTests: XCTestCase {
    func test_loginFlow_wiresNavigation_fromLoginToCatalog() async {
        let sut = AppCompositionRoot()
        sut.loginViewModel.email = "student@course.dev"
        sut.loginViewModel.password = "Passw0rd!"

        await sut.loginViewModel.submit()

        XCTAssertEqual(sut.navigation.routes, [.login, .catalog])
    }

    func test_loginFlow_keepsLoginRoute_whenCredentialsAreInvalid() async {
        let sut = AppCompositionRoot()
        sut.loginViewModel.email = "student@course.dev"
        sut.loginViewModel.password = "wrong"

        await sut.loginViewModel.submit()

        XCTAssertEqual(sut.navigation.routes, [.login])
    }
}

