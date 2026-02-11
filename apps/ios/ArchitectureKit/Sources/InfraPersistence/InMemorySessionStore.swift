import FeatureLoginDomain

public actor InMemorySessionStore: SessionStore {
    private var session: UserSession?

    public init(initialSession: UserSession? = nil) {
        self.session = initialSession
    }

    public func save(_ session: UserSession) async throws {
        self.session = session
    }

    public func load() async throws -> UserSession? {
        session
    }

    public func clear() async throws {
        session = nil
    }
}

