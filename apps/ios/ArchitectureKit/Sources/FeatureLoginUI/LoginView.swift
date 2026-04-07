import SwiftUI

public struct LoginView: View {
  @Bindable var viewModel: LoginViewModel

  public init(viewModel: LoginViewModel) {
    self.viewModel = viewModel
  }

  public var body: some View {
    VStack(alignment: .leading, spacing: 16) {
      Text("Login")
        .font(.largeTitle.bold())
        .accessibilityIdentifier("login_title")

      TextField("Email", text: $viewModel.email)
        #if os(iOS)
          .textInputAutocapitalization(.never)
          .keyboardType(.emailAddress)
        #endif
        .autocorrectionDisabled()
        .textFieldStyle(.roundedBorder)
        .accessibilityIdentifier("login_email")

      SecureField("Password", text: $viewModel.password)
        .textFieldStyle(.roundedBorder)
        .accessibilityIdentifier("login_password")

      Button {
        Task {
          await viewModel.submit()
        }
      } label: {
        if viewModel.phase == .loading {
          ProgressView()
        } else {
          Text("Entrar")
            .fontWeight(.semibold)
        }
      }
      .buttonStyle(.borderedProminent)
      .disabled(viewModel.phase == .loading)
      .accessibilityIdentifier("login_submit")

      if let errorMessage = viewModel.errorMessage {
        Text(errorMessage)
          .foregroundStyle(.red)
          .font(.callout)
          .accessibilityIdentifier("login_error")
      }

      Spacer(minLength: 0)
    }
    .padding(24)
  }
}
