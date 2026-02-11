import Foundation

public struct EmailAddress: Equatable, Sendable {
    public let value: String

    public init(_ rawValue: String) throws {
        let normalized = rawValue.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard Self.isValid(normalized) else {
            throw LoginError.invalidEmail
        }
        self.value = normalized
    }

    private static func isValid(_ value: String) -> Bool {
        guard value.contains("@") else { return false }
        let parts = value.split(separator: "@")
        guard parts.count == 2 else { return false }
        guard !parts[0].isEmpty && !parts[1].isEmpty else { return false }
        return parts[1].contains(".")
    }
}
