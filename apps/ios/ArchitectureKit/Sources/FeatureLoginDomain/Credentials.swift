public struct Credentials: Equatable, Sendable {
    public let email: EmailAddress
    public let password: Password

    public init(email: EmailAddress, password: Password) {
        self.email = email
        self.password = password
    }
}

