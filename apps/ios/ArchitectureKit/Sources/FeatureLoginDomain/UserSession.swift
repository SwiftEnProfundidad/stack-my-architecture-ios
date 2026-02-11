public struct UserSession: Equatable, Sendable {
    public let userId: String
    public let token: String

    public init(userId: String, token: String) {
        self.userId = userId
        self.token = token
    }
}

