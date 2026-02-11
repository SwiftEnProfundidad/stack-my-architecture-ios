#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Uso: $0 <path-to-xcresult> [history-jsonl-path]" >&2
    exit 1
fi

RESULT_BUNDLE_PATH="$1"
HISTORY_PATH="${2:-artifacts/ui-smoke-history.jsonl}"

if [[ ! -d "$RESULT_BUNDLE_PATH" ]]; then
    exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
    exit 0
fi

SUMMARY_JSON="$(xcrun xcresulttool get test-results summary --path "$RESULT_BUNDLE_PATH" --compact)"
TESTS_JSON="$(xcrun xcresulttool get test-results tests --path "$RESULT_BUNDLE_PATH" --compact)"

start_time="$(jq -r '.startTime // 0' <<<"$SUMMARY_JSON")"
start_unix="$(awk -v s="$start_time" 'BEGIN { printf "%d", s }')"
start_iso="$(date -u -r "$start_unix" '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u '+%Y-%m-%dT%H:%M:%SZ')"

slowest_test_name="$(jq -r '
  [.. | objects | select(.nodeType? == "Test Case")]
  | sort_by(.durationInSeconds // 0)
  | last
  | .name // "N/A"
' <<<"$TESTS_JSON")"

slowest_test_duration="$(jq -r '
  [.. | objects | select(.nodeType? == "Test Case")]
  | sort_by(.durationInSeconds // 0)
  | last
  | (.durationInSeconds // 0)
' <<<"$TESTS_JSON")"

entry_json="$(jq -n \
  --arg at "$start_iso" \
  --arg bundle "$RESULT_BUNDLE_PATH" \
  --arg result "$(jq -r '.result // "Unknown"' <<<"$SUMMARY_JSON")" \
  --arg device "$(jq -r '.devicesAndConfigurations[0].device.deviceName // "N/A"' <<<"$SUMMARY_JSON")" \
  --arg platform "$(jq -r '.devicesAndConfigurations[0].device.platform // "N/A"' <<<"$SUMMARY_JSON")" \
  --arg os_version "$(jq -r '.devicesAndConfigurations[0].device.osVersion // "N/A"' <<<"$SUMMARY_JSON")" \
  --arg slowest_test "$slowest_test_name" \
  --argjson total "$(jq '.totalTestCount // 0' <<<"$SUMMARY_JSON")" \
  --argjson passed "$(jq '.passedTests // 0' <<<"$SUMMARY_JSON")" \
  --argjson failed "$(jq '.failedTests // 0' <<<"$SUMMARY_JSON")" \
  --argjson skipped "$(jq '.skippedTests // 0' <<<"$SUMMARY_JSON")" \
  --argjson duration_seconds "$(awk -v start="$(jq -r '.startTime // 0' <<<"$SUMMARY_JSON")" -v end="$(jq -r '.finishTime // 0' <<<"$SUMMARY_JSON")" 'BEGIN { d=end-start; if (d<0) d=0; printf "%.3f", d }')" \
  --argjson slowest_test_duration_seconds "$slowest_test_duration" \
  '{
    at: $at,
    result: $result,
    total: $total,
    passed: $passed,
    failed: $failed,
    skipped: $skipped,
    duration_seconds: $duration_seconds,
    device: $device,
    platform: $platform,
    os_version: $os_version,
    slowest_test: $slowest_test,
    slowest_test_duration_seconds: $slowest_test_duration_seconds,
    bundle: $bundle
  }')"

mkdir -p "$(dirname "$HISTORY_PATH")"
echo "$entry_json" >> "$HISTORY_PATH"
