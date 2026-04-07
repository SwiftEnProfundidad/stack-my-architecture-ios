import FeatureCatalogDomain
import SwiftUI

public struct CatalogView: View {
    var viewModel: CatalogViewModel

    public init(viewModel: CatalogViewModel) {
        self.viewModel = viewModel
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Catálogo")
                .font(.largeTitle.bold())
                .accessibilityIdentifier("catalog_title")

            if viewModel.isLoading {
                ProgressView("Cargando catálogo...")
                    .accessibilityIdentifier("catalog_loading")
            } else if let errorMessage = viewModel.errorMessage {
                Text(errorMessage)
                    .foregroundStyle(.red)
                    .accessibilityIdentifier("catalog_error")
            } else {
                List(viewModel.products, id: \.id) { product in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(product.title)
                            .font(.headline)
                            .accessibilityIdentifier("catalog_item_title_\(product.id)")

                        Text(product.price, format: .currency(code: "EUR"))
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    .padding(.vertical, 6)
                }
                .listStyle(.plain)
                .accessibilityIdentifier("catalog_list")
            }
        }
        .padding(24)
        .task {
            await viewModel.load()
        }
    }
}
