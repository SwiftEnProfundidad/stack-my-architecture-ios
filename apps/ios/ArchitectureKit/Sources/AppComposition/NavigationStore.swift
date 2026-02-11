import AppContracts

@MainActor
public final class NavigationStore: LoginNavigating {
    public private(set) var routes: [AppRoute] = [.login]

    public init() {}

    public func goToCatalog() {
        guard routes.last != .catalog else { return }
        routes.append(.catalog)
    }
}

