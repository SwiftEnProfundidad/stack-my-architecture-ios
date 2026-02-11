import FeatureLoginDomain
import Foundation
import InfraHTTP
import InfraPersistence

private struct LoginRequestDTO: Encodable, Sendable {
    let email: String
    let password: String
}

private struct LoginResponseDTO: Decodable, Sendable {
    let userId: String
    let token: String

    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case token
    }
}

public struct AuthHTTPRepository: AuthRepository, Sendable {
    private let httpClient: any HTTPClient
    private let sessionStore: any SessionStore
    private let endpointPath: String

    public init(
        httpClient: any HTTPClient,
        sessionStore: any SessionStore,
        endpointPath: String = "/auth/login"
    ) {
        self.httpClient = httpClient
        self.sessionStore = sessionStore
        self.endpointPath = endpointPath
    }

    public func authenticate(credentials: Credentials) async throws -> UserSession {
        let body = try JSONEncoder().encode(
            LoginRequestDTO(email: credentials.email.value, password: credentials.password.value)
        )
        let request = HTTPRequest(
            path: endpointPath,
            method: "POST",
            headers: ["Content-Type": "application/json"],
            body: body
        )

        let response: HTTPResponse
        do {
            response = try await httpClient.send(request)
        } catch {
            throw LoginError.network
        }

        switch response.statusCode {
        case 200:
            let dto: LoginResponseDTO
            do {
                dto = try JSONDecoder().decode(LoginResponseDTO.self, from: response.body)
            } catch {
                throw LoginError.network
            }

            let session = UserSession(userId: dto.userId, token: dto.token)
            do {
                try await sessionStore.save(session)
            } catch {
                throw LoginError.network
            }
            return session
        case 401:
            throw LoginError.invalidCredentials
        default:
            throw LoginError.network
        }
    }
}

