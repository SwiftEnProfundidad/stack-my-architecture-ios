#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
INVOCATION_DIR="$(pwd -P)"

resolve_path_from_invocation() {
  local raw_path="$1"
  if [[ -z "${raw_path}" ]]; then
    echo ""
  elif [[ "${raw_path}" = /* ]]; then
    echo "${raw_path}"
  else
    echo "${INVOCATION_DIR}/${raw_path}"
  fi
}

DOMAIN_MIN_COVERAGE="${DOMAIN_MIN_COVERAGE:-85}"
DATA_MIN_COVERAGE="${DATA_MIN_COVERAGE:-75}"
RUN_UI_SMOKE="${RUN_UI_SMOKE:-0}"

echo "Running architecture dependency checks..."
"${SCRIPT_DIR}/check-dependencies.sh"

echo "Running performance baseline checks..."
"${SCRIPT_DIR}/check-performance-baseline.sh"

echo "Running tests with code coverage..."
cd "${ROOT_DIR}"
swift test --enable-code-coverage

BINARY_PATH="$(find .build -path '*debug/ArchitectureKitPackageTests.xctest/Contents/MacOS/ArchitectureKitPackageTests' | head -n1)"
PROFDATA_PATH="$(find .build -path '*debug/codecov/default.profdata' | head -n1)"

if [[ -z "${BINARY_PATH}" || -z "${PROFDATA_PATH}" ]]; then
  echo "Coverage artifacts not found."
  exit 1
fi

COVERAGE_JSON="$(mktemp)"
xcrun llvm-cov export "${BINARY_PATH}" -instr-profile "${PROFDATA_PATH}" > "${COVERAGE_JSON}"

COVERAGE_RESULT="$(
  jq -r '
    def aggregate($patterns):
      [ .data[0].files[]
        | select(. as $f | any($patterns[]; . as $p | $f.filename | contains($p)))
        | .summary.lines ] as $lines
      | {
          covered: ($lines | map(.covered) | add // 0),
          count: ($lines | map(.count) | add // 0)
        };

    def percent($node):
      if $node.count == 0 then 0 else (($node.covered * 100) / $node.count) end;

    {
      domain: aggregate(["Sources/FeatureLoginDomain/", "Sources/FeatureCatalogDomain/"]),
      data: aggregate([
        "Sources/FeatureLoginData/",
        "Sources/FeatureCatalogData/",
        "Sources/FeatureCatalogPersistenceSwiftData/",
        "Sources/InfraHTTP/",
        "Sources/InfraPersistence/"
      ])
    }
    | [
        (percent(.domain)),
        (percent(.data))
      ]
    | @tsv
  ' "${COVERAGE_JSON}"
)"

rm -f "${COVERAGE_JSON}"

DOMAIN_COVERAGE="$(echo "${COVERAGE_RESULT}" | awk '{print $1}')"
DATA_COVERAGE="$(echo "${COVERAGE_RESULT}" | awk '{print $2}')"

printf 'Domain coverage: %.2f%% (min %.2f%%)\n' "${DOMAIN_COVERAGE}" "${DOMAIN_MIN_COVERAGE}"
printf 'Data coverage: %.2f%% (min %.2f%%)\n' "${DATA_COVERAGE}" "${DATA_MIN_COVERAGE}"

awk -v actual="${DOMAIN_COVERAGE}" -v min="${DOMAIN_MIN_COVERAGE}" 'BEGIN { exit(actual + 0 >= min + 0 ? 0 : 1) }' \
  || { echo "Domain coverage gate failed."; exit 1; }

awk -v actual="${DATA_COVERAGE}" -v min="${DATA_MIN_COVERAGE}" 'BEGIN { exit(actual + 0 >= min + 0 ? 0 : 1) }' \
  || { echo "Data coverage gate failed."; exit 1; }

if [[ "${RUN_UI_SMOKE}" == "1" ]]; then
  UI_SMOKE_SCRIPT="${ROOT_DIR}/../ArchitectureHostApp/scripts/run-ui-smoke.sh"
  if [[ ! -x "${UI_SMOKE_SCRIPT}" ]]; then
    echo "UI smoke script not found at ${UI_SMOKE_SCRIPT}"
    exit 1
  fi

  echo "Running optional iOS UI smoke tests..."
  UI_SMOKE_ENV=()
  if [[ -n "${UI_SMOKE_RESULT_BUNDLE_PATH:-}" ]]; then
    UI_SMOKE_ENV+=("UI_SMOKE_RESULT_BUNDLE_PATH=$(resolve_path_from_invocation "${UI_SMOKE_RESULT_BUNDLE_PATH}")")
  fi
  if [[ -n "${UI_SMOKE_HISTORY_PATH:-}" ]]; then
    UI_SMOKE_ENV+=("UI_SMOKE_HISTORY_PATH=$(resolve_path_from_invocation "${UI_SMOKE_HISTORY_PATH}")")
  fi
  if [[ -n "${UI_SMOKE_ATTEMPTS:-}" ]]; then
    UI_SMOKE_ENV+=("UI_SMOKE_ATTEMPTS=${UI_SMOKE_ATTEMPTS}")
  fi

  env "${UI_SMOKE_ENV[@]}" "${UI_SMOKE_SCRIPT}"
fi

echo "All quality gates passed."
