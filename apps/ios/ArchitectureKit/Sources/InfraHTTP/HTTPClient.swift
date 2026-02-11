import Foundation

public struct HTTPRequest: Sendable, Equatable {
    public let path: String
    public let method: String
    public let headers: [String: String]
    public let body: Data?

    public init(path: String, method: String, headers: [String: String] = [:], body: Data? = nil) {
        self.path = path
        self.method = method
        self.headers = headers
        self.body = body
    }
}

public struct HTTPResponse: Sendable, Equatable {
    public let statusCode: Int
    public let body: Data

    public init(statusCode: Int, body: Data) {
        self.statusCode = statusCode
        self.body = body
    }
}

public enum HTTPClientError: Error, Equatable, Sendable {
    case transport
    case invalidResponse
}

public protocol HTTPClient: Sendable {
    func send(_ request: HTTPRequest) async throws -> HTTPResponse
}

