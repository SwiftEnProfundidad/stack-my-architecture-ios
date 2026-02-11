public enum AppRoute: Equatable, Sendable {
    case login
    case catalog
}

@MainActor
public protocol LoginNavigating: AnyObject {
    func goToCatalog()
}

