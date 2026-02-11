#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCES_DIR="${ROOT_DIR}/Sources"

violations=0

check_no_import() {
  local target_dir="$1"
  local forbidden_module="$2"
  local matches
  matches="$(rg -n "^[[:space:]]*import[[:space:]]+${forbidden_module}$" "${target_dir}" || true)"
  if [[ -n "${matches}" ]]; then
    echo "Dependency violation: ${target_dir} must not import ${forbidden_module}"
    echo "${matches}"
    echo ""
    violations=$((violations + 1))
  fi
}

# FeatureLoginDomain
check_no_import "${SOURCES_DIR}/FeatureLoginDomain" "AppContracts"
check_no_import "${SOURCES_DIR}/FeatureLoginDomain" "InfraHTTP"
check_no_import "${SOURCES_DIR}/FeatureLoginDomain" "InfraPersistence"
check_no_import "${SOURCES_DIR}/FeatureLoginDomain" "FeatureLoginData"
check_no_import "${SOURCES_DIR}/FeatureLoginDomain" "FeatureLoginUI"
check_no_import "${SOURCES_DIR}/FeatureLoginDomain" "FeatureCatalogDomain"
check_no_import "${SOURCES_DIR}/FeatureLoginDomain" "FeatureCatalogData"
check_no_import "${SOURCES_DIR}/FeatureLoginDomain" "FeatureCatalogUI"

# FeatureLoginData
check_no_import "${SOURCES_DIR}/FeatureLoginData" "FeatureLoginUI"
check_no_import "${SOURCES_DIR}/FeatureLoginData" "FeatureCatalogDomain"
check_no_import "${SOURCES_DIR}/FeatureLoginData" "FeatureCatalogData"
check_no_import "${SOURCES_DIR}/FeatureLoginData" "FeatureCatalogUI"
check_no_import "${SOURCES_DIR}/FeatureLoginData" "AppContracts"

# FeatureLoginUI
check_no_import "${SOURCES_DIR}/FeatureLoginUI" "FeatureLoginData"
check_no_import "${SOURCES_DIR}/FeatureLoginUI" "FeatureCatalogDomain"
check_no_import "${SOURCES_DIR}/FeatureLoginUI" "FeatureCatalogData"
check_no_import "${SOURCES_DIR}/FeatureLoginUI" "FeatureCatalogUI"
check_no_import "${SOURCES_DIR}/FeatureLoginUI" "InfraHTTP"
check_no_import "${SOURCES_DIR}/FeatureLoginUI" "InfraPersistence"

# FeatureCatalogDomain
check_no_import "${SOURCES_DIR}/FeatureCatalogDomain" "AppContracts"
check_no_import "${SOURCES_DIR}/FeatureCatalogDomain" "FeatureCatalogData"
check_no_import "${SOURCES_DIR}/FeatureCatalogDomain" "FeatureCatalogUI"
check_no_import "${SOURCES_DIR}/FeatureCatalogDomain" "FeatureLoginDomain"
check_no_import "${SOURCES_DIR}/FeatureCatalogDomain" "FeatureLoginData"
check_no_import "${SOURCES_DIR}/FeatureCatalogDomain" "FeatureLoginUI"
check_no_import "${SOURCES_DIR}/FeatureCatalogDomain" "InfraHTTP"
check_no_import "${SOURCES_DIR}/FeatureCatalogDomain" "InfraPersistence"

# FeatureCatalogData
check_no_import "${SOURCES_DIR}/FeatureCatalogData" "FeatureCatalogUI"
check_no_import "${SOURCES_DIR}/FeatureCatalogData" "FeatureLoginDomain"
check_no_import "${SOURCES_DIR}/FeatureCatalogData" "FeatureLoginData"
check_no_import "${SOURCES_DIR}/FeatureCatalogData" "FeatureLoginUI"
check_no_import "${SOURCES_DIR}/FeatureCatalogData" "AppContracts"

# FeatureCatalogPersistenceSwiftData
check_no_import "${SOURCES_DIR}/FeatureCatalogPersistenceSwiftData" "FeatureLoginDomain"
check_no_import "${SOURCES_DIR}/FeatureCatalogPersistenceSwiftData" "FeatureLoginData"
check_no_import "${SOURCES_DIR}/FeatureCatalogPersistenceSwiftData" "FeatureLoginUI"
check_no_import "${SOURCES_DIR}/FeatureCatalogPersistenceSwiftData" "FeatureCatalogUI"
check_no_import "${SOURCES_DIR}/FeatureCatalogPersistenceSwiftData" "AppContracts"

# FeatureCatalogUI
check_no_import "${SOURCES_DIR}/FeatureCatalogUI" "FeatureCatalogData"
check_no_import "${SOURCES_DIR}/FeatureCatalogUI" "FeatureCatalogPersistenceSwiftData"
check_no_import "${SOURCES_DIR}/FeatureCatalogUI" "FeatureLoginDomain"
check_no_import "${SOURCES_DIR}/FeatureCatalogUI" "FeatureLoginData"
check_no_import "${SOURCES_DIR}/FeatureCatalogUI" "FeatureLoginUI"
check_no_import "${SOURCES_DIR}/FeatureCatalogUI" "InfraHTTP"
check_no_import "${SOURCES_DIR}/FeatureCatalogUI" "InfraPersistence"

if [[ "${violations}" -gt 0 ]]; then
  echo "Architecture dependency check failed with ${violations} violation(s)."
  exit 1
fi

echo "Architecture dependency check passed."
