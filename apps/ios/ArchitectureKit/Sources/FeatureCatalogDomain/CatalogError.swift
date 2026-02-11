public enum CatalogError: Error, Equatable, Sendable {
    case network
    case offlineNoCache
    case staleCacheUnavailable
}

