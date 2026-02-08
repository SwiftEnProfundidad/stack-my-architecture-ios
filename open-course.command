#!/usr/bin/env bash

set -euo pipefail

SCRIPT_SOURCE="${BASH_SOURCE[0]}"
if [[ "${SCRIPT_SOURCE}" == */* ]]; then
  ROOT_DIR="$(cd "${SCRIPT_SOURCE%/*}" && pwd)"
else
  ROOT_DIR="$(pwd)"
fi

exec "${ROOT_DIR}/scripts/open-course.command" "$@"
