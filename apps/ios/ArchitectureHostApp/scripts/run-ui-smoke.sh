#!/usr/bin/env bash
set -euo pipefail

CALLER_DIR="$(pwd -P)"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

resolve_path_from_caller() {
    local raw_path="$1"
    if [[ -z "$raw_path" ]]; then
        echo ""
    elif [[ "$raw_path" = /* ]]; then
        echo "$raw_path"
    else
        echo "$CALLER_DIR/$raw_path"
    fi
}

RESULT_BUNDLE_PATH="$(resolve_path_from_caller "${UI_SMOKE_RESULT_BUNDLE_PATH:-}")"
ATTEMPTS_RAW="${UI_SMOKE_ATTEMPTS:-1}"
ATTEMPTS="$ATTEMPTS_RAW"
if [[ -n "${UI_SMOKE_HISTORY_PATH:-}" ]]; then
    HISTORY_PATH="$(resolve_path_from_caller "$UI_SMOKE_HISTORY_PATH")"
else
    HISTORY_PATH="$ROOT_DIR/artifacts/ui-smoke-history.jsonl"
fi

if ! [[ "$ATTEMPTS" =~ ^[0-9]+$ ]] || [[ "$ATTEMPTS" -lt 1 ]]; then
    ATTEMPTS=1
fi

if ! command -v xcodegen >/dev/null 2>&1; then
    echo "xcodegen no está instalado."
    exit 1
fi

echo "[ui-smoke] Generating project with xcodegen"
xcodegen generate >/dev/null

SIMULATOR_ID="$(xcrun simctl list devices available | awk -F'[()]' '/iPhone/ { print $2; exit }')"
if [[ -z "${SIMULATOR_ID:-}" ]]; then
    echo "No hay simuladores iPhone disponibles"
    exit 1
fi

echo "[ui-smoke] Running test on simulator id=$SIMULATOR_ID"
xcrun simctl boot "$SIMULATOR_ID" >/dev/null 2>&1 || true
xcrun simctl bootstatus "$SIMULATOR_ID" -b >/dev/null 2>&1 || true

XCODEBUILD_ARGS=(
    -project ArchitectureHostApp.xcodeproj
    -scheme ArchitectureHostApp
    -destination "id=$SIMULATOR_ID"
    -only-testing:ArchitectureHostAppUITests
    test
)

if [[ -n "$RESULT_BUNDLE_PATH" ]]; then
    mkdir -p "$(dirname "$RESULT_BUNDLE_PATH")"
    XCODEBUILD_ARGS+=(-resultBundlePath "$RESULT_BUNDLE_PATH")
fi

attempt=1
while true; do
    if [[ -n "$RESULT_BUNDLE_PATH" ]]; then
        rm -rf "$RESULT_BUNDLE_PATH"
        echo "[ui-smoke] Result bundle: $RESULT_BUNDLE_PATH"
    fi

    echo "[ui-smoke] Attempt $attempt/$ATTEMPTS"
    if xcodebuild "${XCODEBUILD_ARGS[@]}"; then
        break
    fi

    if [[ "$attempt" -ge "$ATTEMPTS" ]]; then
        echo "[ui-smoke] Failed after $ATTEMPTS attempt(s)."
        exit 1
    fi

    echo "[ui-smoke] Attempt $attempt failed, retrying..."
    xcrun simctl shutdown "$SIMULATOR_ID" >/dev/null 2>&1 || true
    xcrun simctl boot "$SIMULATOR_ID" >/dev/null 2>&1 || true
    xcrun simctl bootstatus "$SIMULATOR_ID" -b >/dev/null 2>&1 || true
    attempt=$((attempt + 1))
done

if [[ -n "$RESULT_BUNDLE_PATH" ]]; then
    HISTORY_SCRIPT="$ROOT_DIR/scripts/record-ui-smoke-history.sh"
    if [[ -x "$HISTORY_SCRIPT" ]]; then
        "$HISTORY_SCRIPT" "$RESULT_BUNDLE_PATH" "$HISTORY_PATH" || true
        echo "[ui-smoke] History: $HISTORY_PATH"
    fi
fi
