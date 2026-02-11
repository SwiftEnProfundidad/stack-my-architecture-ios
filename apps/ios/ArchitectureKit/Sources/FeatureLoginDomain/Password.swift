import Foundation

public struct Password: Equatable, Sendable {
    public let value: String

    public init(_ rawValue: String) throws {
        let normalized = rawValue.trimmingCharacters(in: .whitespacesAndNewlines)
        guard normalized.count >= 8 else {
            throw LoginError.invalidPassword
        }
        self.value = normalized
    }
}
