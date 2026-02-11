import AppContracts
import FeatureLoginDomain

@MainActor
public final class LoginViewModel {
    public enum Phase: Equatable {
        case idle
        case loading
        case authenticated
    }

    public var email: String = ""
    public var password: String = ""
    public private(set) var phase: Phase = .idle
    public private(set) var errorMessage: String?

    private let useCase: AuthenticateUserUseCase
    private weak var navigator: (any LoginNavigating)?

    public init(useCase: AuthenticateUserUseCase, navigator: any LoginNavigating) {
        self.useCase = useCase
        self.navigator = navigator
    }

    public func submit() async {
        guard phase != .loading else { return }
        phase = .loading
        errorMessage = nil

        do {
            _ = try await useCase.execute(email: email, password: password)
            phase = .authenticated
            navigator?.goToCatalog()
        } catch let error as LoginError {
            phase = .idle
            errorMessage = Self.map(error: error)
        } catch {
            phase = .idle
            errorMessage = "Se produjo un error inesperado."
        }
    }

    private static func map(error: LoginError) -> String {
        switch error {
        case .invalidEmail:
            return "Email inválido."
        case .invalidPassword:
            return "Password inválido (mínimo 8 caracteres)."
        case .invalidCredentials:
            return "Credenciales inválidas."
        case .network:
            return "No se pudo conectar. Reintenta."
        }
    }
}

