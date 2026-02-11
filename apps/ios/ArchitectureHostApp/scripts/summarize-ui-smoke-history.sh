#!/usr/bin/env bash
set -euo pipefail

HISTORY_PATH="${1:-artifacts/ui-smoke-history.jsonl}"
MAX_ROWS="${2:-20}"

if [[ ! -f "$HISTORY_PATH" ]]; then
    echo "## UI Smoke History"
    echo ""
    echo "No existe histórico en: <code>$HISTORY_PATH</code>"
    exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
    echo "## UI Smoke History"
    echo ""
    echo "\`jq\` no está instalado; no se puede resumir histórico."
    exit 0
fi

history_json="$(jq -s '.' "$HISTORY_PATH")"
run_count="$(jq 'length' <<<"$history_json")"
passed_runs="$(jq '[.[] | select(.result == "Passed")] | length' <<<"$history_json")"
failed_runs="$(jq '[.[] | select(.result != "Passed")] | length' <<<"$history_json")"
pass_rate="$(awk -v p="$passed_runs" -v t="$run_count" 'BEGIN { if (t == 0) printf "0.00"; else printf "%.2f", (p*100)/t }')"
avg_duration="$(jq '[.[].duration_seconds] | if length==0 then 0 else (add/length) end' <<<"$history_json")"
latest_result="$(jq -r 'last | .result // "Unknown"' <<<"$history_json")"
latest_at="$(jq -r 'last | .at // "N/A"' <<<"$history_json")"

rows="$(jq -r --argjson max "$MAX_ROWS" '
  reverse
  | .[:$max]
  | .[]
  | "| " + (.at // "N/A") + " | " + (.result // "Unknown") + " | " + ((.duration_seconds // 0) | tostring) + " | " + ((.failed // 0) | tostring) + " | " + (.slowest_test // "N/A") + " | "
' <<<"$history_json")"

echo "## UI Smoke History"
echo ""
echo "- Runs: **$run_count** (passed: $passed_runs, failed: $failed_runs, pass-rate: ${pass_rate}%)"
echo "- Avg duration: **$(awk -v d="$avg_duration" 'BEGIN { printf "%.2f", d }')s**"
echo "- Last run: **$latest_result** at $latest_at"
echo "- Source: <code>$HISTORY_PATH</code>"
echo ""
echo "| At (UTC) | Result | Duration (s) | Failed Tests | Slowest Test |"
echo "|---|---:|---:|---:|---|"
echo "$rows"
