// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "ArchitectureKit",
    platforms: [
        .iOS(.v17),
        .macOS(.v14)
    ],
    products: [
        .library(name: "CoreDomain", targets: ["CoreDomain"]),
        .library(name: "AppContracts", targets: ["AppContracts"]),
        .library(name: "InfraHTTP", targets: ["InfraHTTP"]),
        .library(name: "InfraPersistence", targets: ["InfraPersistence"]),
        .library(name: "FeatureLoginDomain", targets: ["FeatureLoginDomain"]),
        .library(name: "FeatureLoginData", targets: ["FeatureLoginData"]),
        .library(name: "FeatureLoginUI", targets: ["FeatureLoginUI"]),
        .library(name: "FeatureCatalogDomain", targets: ["FeatureCatalogDomain"]),
        .library(name: "FeatureCatalogData", targets: ["FeatureCatalogData"]),
        .library(name: "FeatureCatalogPersistenceSwiftData", targets: ["FeatureCatalogPersistenceSwiftData"]),
        .library(name: "FeatureCatalogUI", targets: ["FeatureCatalogUI"]),
        .library(name: "AppComposition", targets: ["AppComposition"]),
        .executable(name: "ArchitectureBenchmarks", targets: ["ArchitectureBenchmarks"])
    ],
    targets: [
        .target(
            name: "CoreDomain"
        ),
        .target(
            name: "AppContracts"
        ),
        .target(
            name: "InfraHTTP"
        ),
        .target(
            name: "InfraPersistence",
            dependencies: ["FeatureLoginDomain"]
        ),
        .target(
            name: "FeatureLoginDomain",
            dependencies: ["CoreDomain"]
        ),
        .target(
            name: "FeatureLoginData",
            dependencies: ["FeatureLoginDomain", "InfraHTTP", "InfraPersistence"]
        ),
        .target(
            name: "FeatureLoginUI",
            dependencies: ["FeatureLoginDomain", "AppContracts"]
        ),
        .target(
            name: "FeatureCatalogDomain",
            dependencies: ["CoreDomain"]
        ),
        .target(
            name: "FeatureCatalogData",
            dependencies: ["FeatureCatalogDomain"]
        ),
        .target(
            name: "FeatureCatalogPersistenceSwiftData",
            dependencies: ["FeatureCatalogDomain", "FeatureCatalogData"]
        ),
        .target(
            name: "FeatureCatalogUI",
            dependencies: ["FeatureCatalogDomain", "AppContracts"]
        ),
        .target(
            name: "AppComposition",
            dependencies: [
                "AppContracts",
                "FeatureLoginDomain",
                "FeatureLoginData",
                "FeatureLoginUI",
                "FeatureCatalogDomain",
                "FeatureCatalogData",
                "FeatureCatalogPersistenceSwiftData",
                "FeatureCatalogUI"
            ]
        ),
        .executableTarget(
            name: "ArchitectureBenchmarks",
            dependencies: ["FeatureCatalogData", "FeatureCatalogDomain"]
        ),
        .testTarget(
            name: "FeatureLoginDomainTests",
            dependencies: ["FeatureLoginDomain"]
        ),
        .testTarget(
            name: "FeatureCatalogDomainTests",
            dependencies: ["FeatureCatalogDomain"]
        ),
        .testTarget(
            name: "FeatureLoginUITests",
            dependencies: ["FeatureLoginUI", "FeatureLoginDomain", "AppContracts"]
        ),
        .testTarget(
            name: "FeatureLoginDataIntegrationTests",
            dependencies: ["FeatureLoginData", "FeatureLoginDomain", "InfraHTTP", "InfraPersistence"]
        ),
        .testTarget(
            name: "FeatureCatalogDataIntegrationTests",
            dependencies: ["FeatureCatalogData", "FeatureCatalogDomain"]
        ),
        .testTarget(
            name: "FeatureCatalogPersistenceSwiftDataTests",
            dependencies: ["FeatureCatalogPersistenceSwiftData", "FeatureCatalogDomain"]
        ),
        .testTarget(
            name: "AppCompositionTests",
            dependencies: ["AppComposition", "FeatureLoginData", "AppContracts"]
        )
    ]
)
