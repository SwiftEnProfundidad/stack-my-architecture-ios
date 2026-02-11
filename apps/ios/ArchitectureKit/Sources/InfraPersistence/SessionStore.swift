import FeatureLoginDomain

public protocol SessionStore: Sendable {
    func save(_ session: UserSession) async throws
    func load() async throws -> UserSession?
    func clear() async throws
}

