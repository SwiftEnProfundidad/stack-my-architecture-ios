public struct AuthenticateUserUseCase: Sendable {
    private let repository: any AuthRepository

    public init(repository: any AuthRepository) {
        self.repository = repository
    }

    public func execute(email: String, password: String) async throws -> UserSession {
        let credentials = Credentials(
            email: try EmailAddress(email),
            password: try Password(password)
        )
        return try await repository.authenticate(credentials: credentials)
    }
}
