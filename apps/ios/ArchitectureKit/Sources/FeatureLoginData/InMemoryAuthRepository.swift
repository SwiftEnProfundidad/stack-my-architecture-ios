import FeatureLoginDomain

public actor InMemoryAuthRepository: AuthRepository {
    private let validEmail: String
    private let validPassword: String
    private let session: UserSession
    private let latencyNanoseconds: UInt64

    public init(
        validEmail: String = "student@course.dev",
        validPassword: String = "Passw0rd!",
        session: UserSession = UserSession(userId: "student-1", token: "token-abc"),
        latencyNanoseconds: UInt64 = 0
    ) {
        self.validEmail = validEmail.lowercased()
        self.validPassword = validPassword
        self.session = session
        self.latencyNanoseconds = latencyNanoseconds
    }

    public func authenticate(credentials: Credentials) async throws -> UserSession {
        if latencyNanoseconds > 0 {
            try? await Task.sleep(nanoseconds: latencyNanoseconds)
        }

        guard credentials.email.value == validEmail else {
            throw LoginError.invalidCredentials
        }
        guard credentials.password.value == validPassword else {
            throw LoginError.invalidCredentials
        }
        return session
    }
}

