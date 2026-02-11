#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Uso: $0 <path-to-xcresult> <output-dir>" >&2
    exit 1
fi

RESULT_BUNDLE_PATH="$1"
OUTPUT_DIR="$2"
ATTACHMENTS_DIR="$OUTPUT_DIR/attachments"
DIAGNOSTICS_DIR="$OUTPUT_DIR/diagnostics"
SUMMARY_FILE="$OUTPUT_DIR/evidence-summary.md"

mkdir -p "$OUTPUT_DIR"

if [[ ! -d "$RESULT_BUNDLE_PATH" ]]; then
    {
        echo "## UI Smoke Evidence"
        echo ""
        echo "No se encontró bundle en: <code>$RESULT_BUNDLE_PATH</code>"
    } > "$SUMMARY_FILE"
    exit 0
fi

mkdir -p "$ATTACHMENTS_DIR" "$DIAGNOSTICS_DIR"

xcrun xcresulttool export attachments \
    --path "$RESULT_BUNDLE_PATH" \
    --output-path "$ATTACHMENTS_DIR" \
    --only-failures >/dev/null 2>&1 || true

xcrun xcresulttool export diagnostics \
    --path "$RESULT_BUNDLE_PATH" \
    --output-path "$DIAGNOSTICS_DIR" >/dev/null 2>&1 || true

attachments_manifest="$ATTACHMENTS_DIR/manifest.json"
attachments_total=0
if [[ -f "$attachments_manifest" ]] && command -v jq >/dev/null 2>&1; then
    attachments_total="$(jq 'length' "$attachments_manifest" 2>/dev/null || echo 0)"
fi

diagnostics_files="$(find "$DIAGNOSTICS_DIR" -type f | wc -l | tr -d ' ')"
attachments_files="$(find "$ATTACHMENTS_DIR" -type f | wc -l | tr -d ' ')"

{
    echo "## UI Smoke Evidence"
    echo ""
    echo "- Bundle: <code>$RESULT_BUNDLE_PATH</code>"
    echo "- Attachments exports: $attachments_files files"
    echo "- Failure attachments in manifest: $attachments_total"
    echo "- Diagnostics exports: $diagnostics_files files"
    echo "- Output dir: <code>$OUTPUT_DIR</code>"
} > "$SUMMARY_FILE"

cat "$SUMMARY_FILE"
