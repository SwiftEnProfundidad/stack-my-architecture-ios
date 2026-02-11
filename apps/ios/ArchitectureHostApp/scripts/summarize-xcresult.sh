#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Uso: $0 <path-to-xcresult>" >&2
    exit 1
fi

RESULT_BUNDLE_PATH="$1"
if [[ ! -d "$RESULT_BUNDLE_PATH" ]]; then
    echo "## UI Smoke Summary"
    echo ""
    echo "No se encontró bundle de resultados en: $RESULT_BUNDLE_PATH"
    exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
    echo "## UI Smoke Summary"
    echo ""
    echo "`jq` no está instalado; no se pudo generar resumen del xcresult."
    exit 0
fi

SUMMARY_JSON="$(xcrun xcresulttool get test-results summary --path "$RESULT_BUNDLE_PATH" --compact)"
TESTS_JSON="$(xcrun xcresulttool get test-results tests --path "$RESULT_BUNDLE_PATH" --compact)"

result="$(jq -r '.result // "Unknown"' <<<"$SUMMARY_JSON")"
passed="$(jq -r '.passedTests // 0' <<<"$SUMMARY_JSON")"
failed="$(jq -r '.failedTests // 0' <<<"$SUMMARY_JSON")"
skipped="$(jq -r '.skippedTests // 0' <<<"$SUMMARY_JSON")"
expected_failures="$(jq -r '.expectedFailures // 0' <<<"$SUMMARY_JSON")"
total="$(jq -r '.totalTestCount // 0' <<<"$SUMMARY_JSON")"
start_time="$(jq -r '.startTime // 0' <<<"$SUMMARY_JSON")"
finish_time="$(jq -r '.finishTime // 0' <<<"$SUMMARY_JSON")"
duration_seconds="$(awk -v start="$start_time" -v end="$finish_time" 'BEGIN { d=end-start; if (d < 0) d=0; printf "%.2f", d }')"

device="$(jq -r '.devicesAndConfigurations[0].device.deviceName // "N/A"' <<<"$SUMMARY_JSON")"
os_version="$(jq -r '.devicesAndConfigurations[0].device.osVersion // "N/A"' <<<"$SUMMARY_JSON")"
platform="$(jq -r '.devicesAndConfigurations[0].device.platform // "N/A"' <<<"$SUMMARY_JSON")"

failed_details="$(jq -r '
  .testFailures[]?
  | "- " + (.testName // .name // "Unknown") + ": " + (.message // .failureText // "Sin detalle")
' <<<"$SUMMARY_JSON")"

echo "## UI Smoke Summary"
echo ""
echo "- Result: **$result**"
echo "- Total: **$total** (passed: $passed, failed: $failed, skipped: $skipped, expected-failures: $expected_failures)"
echo "- Duration: **${duration_seconds}s**"
echo "- Device: **$device** ($platform $os_version)"
echo "- Bundle: \`$RESULT_BUNDLE_PATH\`"
echo ""
echo "### Test Cases"
echo ""
echo "| Test | Result | Duration (s) |"
echo "|---|---:|---:|"

jq -r '
  [.. | objects | select(.nodeType? == "Test Case")]
  | sort_by(.name)
  | .[]
  | "| " + (.name // "Unknown") + " | " + (.result // "Unknown") + " | " + ((.durationInSeconds // 0) | tostring) + " |"
' <<<"$TESTS_JSON"

if [[ -n "$failed_details" ]]; then
    echo ""
    echo "### Failure Details"
    echo ""
    echo "$failed_details"
fi
