import FeatureCatalogDomain

public actor DefaultCatalogRemoteDataSource: CatalogRemoteDataSource {
    private let products: [Product]

    public init(
        products: [Product] = [
            Product(id: "p-1", title: "Bike", price: 199.0),
            Product(id: "p-2", title: "Helmet", price: 49.0),
            Product(id: "p-3", title: "Bottle", price: 12.0)
        ]
    ) {
        self.products = products
    }

    public func fetchProducts() async throws -> [Product] {
        products
    }
}

