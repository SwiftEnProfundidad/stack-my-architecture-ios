public struct Product: Equatable, Sendable {
    public let id: String
    public let title: String
    public let price: Double

    public init(id: String, title: String, price: Double) {
        self.id = id
        self.title = title
        self.price = price
    }
}

