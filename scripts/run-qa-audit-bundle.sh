#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 scripts/build-html.py
python3 scripts/audit-course-matrix.py
python3 scripts/audit-pedagogical-continuity.py
python3 scripts/audit-complexity-prereq-redundancy.py
python3 scripts/check-pedagogical-template.py
python3 scripts/audit-mermaid-semantic.py
python3 scripts/audit-snippets-quality.py
python3 scripts/audit-scaffold-traceability.py
python3 scripts/audit-cross-links.py
python3 scripts/audit-stage-closure-artifacts.py

if [ ! -f 00-informe/AUDITORIA-GUARDRAILS-BASELINE.json ]; then
  python3 scripts/qa-regression-guardrails.py --write-baseline
fi
python3 scripts/qa-regression-guardrails.py
python3 scripts/generate-qa-summary.py

echo "QA bundle completed"
