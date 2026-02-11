public protocol AuthRepository: Sendable {
    func authenticate(credentials: Credentials) async throws -> UserSession
}

