import XCTest

final class ArchitectureHostAppUITests: XCTestCase {
    @MainActor
    func testLoginToCatalogSmokeFlow() {
        let app = XCUIApplication()
        app.launch()

        let loginButton = app.buttons["login_submit"]
        XCTAssertTrue(loginButton.waitForExistence(timeout: 5))
        loginButton.tap()

        let catalogTitle = app.staticTexts["Catálogo"]
        XCTAssertTrue(catalogTitle.waitForExistence(timeout: 8))

        let firstItem = app.staticTexts["Bike"]
        XCTAssertTrue(firstItem.waitForExistence(timeout: 5))
    }

    @MainActor
    func testInvalidLogin_staysOnLoginAndShowsError() {
        let app = XCUIApplication()
        app.launchEnvironment["UITEST_LOGIN_PASSWORD"] = "WrongPass123!"
        app.launch()

        let loginButton = app.buttons["login_submit"]
        XCTAssertTrue(loginButton.waitForExistence(timeout: 5))
        loginButton.tap()

        let loginError = app.staticTexts["login_error"]
        XCTAssertTrue(loginError.waitForExistence(timeout: 5))
        XCTAssertEqual(loginError.label, "Credenciales inválidas.")

        let catalogTitle = app.staticTexts["Catálogo"]
        XCTAssertFalse(catalogTitle.exists)
    }
}
