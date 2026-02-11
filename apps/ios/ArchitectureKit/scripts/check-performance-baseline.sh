#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BASELINE_FILE="${ROOT_DIR}/benchmarks/performance-baseline.json"
LAST_RUN_FILE="${ROOT_DIR}/benchmarks/performance-last-run.json"

if [[ ! -f "${BASELINE_FILE}" ]]; then
  echo "Performance baseline file not found: ${BASELINE_FILE}"
  exit 1
fi

cd "${ROOT_DIR}"

REMOTE_DELAY_NS="$(jq -r '.remote_delay_ns' "${BASELINE_FILE}")"
COLD_MS_MAX="$(jq -r '.cold_ms_max' "${BASELINE_FILE}")"
WARM_MS_MAX="$(jq -r '.warm_ms_max' "${BASELINE_FILE}")"
RATIO_MAX="$(jq -r '.warm_to_cold_ratio_max' "${BASELINE_FILE}")"

echo "Running performance benchmark..."
BENCH_OUTPUT="$(BENCH_REMOTE_DELAY_NS="${REMOTE_DELAY_NS}" swift run -q ArchitectureBenchmarks)"
echo "${BENCH_OUTPUT}" > "${LAST_RUN_FILE}"

COLD_MS="$(echo "${BENCH_OUTPUT}" | jq -r '.cold_ms')"
WARM_MS="$(echo "${BENCH_OUTPUT}" | jq -r '.warm_ms')"
RATIO="$(echo "${BENCH_OUTPUT}" | jq -r '.warm_to_cold_ratio')"

printf 'Cold load: %.2fms (max %.2fms)\n' "${COLD_MS}" "${COLD_MS_MAX}"
printf 'Warm load: %.2fms (max %.2fms)\n' "${WARM_MS}" "${WARM_MS_MAX}"
printf 'Warm/Cold ratio: %.4f (max %.4f)\n' "${RATIO}" "${RATIO_MAX}"

awk -v actual="${COLD_MS}" -v max="${COLD_MS_MAX}" 'BEGIN { exit(actual + 0 <= max + 0 ? 0 : 1) }' \
  || { echo "Performance gate failed: cold_ms over baseline."; exit 1; }

awk -v actual="${WARM_MS}" -v max="${WARM_MS_MAX}" 'BEGIN { exit(actual + 0 <= max + 0 ? 0 : 1) }' \
  || { echo "Performance gate failed: warm_ms over baseline."; exit 1; }

awk -v actual="${RATIO}" -v max="${RATIO_MAX}" 'BEGIN { exit(actual + 0 <= max + 0 ? 0 : 1) }' \
  || { echo "Performance gate failed: warm_to_cold_ratio over baseline."; exit 1; }

awk -v cold="${COLD_MS}" -v warm="${WARM_MS}" 'BEGIN { exit(warm + 0 < cold + 0 ? 0 : 1) }' \
  || { echo "Performance gate failed: warm load is not faster than cold load."; exit 1; }

echo "Performance baseline gate passed."

