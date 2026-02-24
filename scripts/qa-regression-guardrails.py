#!/usr/bin/env python3
"""Regression guardrails for iOS course QA audits."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "00-informe"
BASELINE_PATH = REPORTS_DIR / "AUDITORIA-GUARDRAILS-BASELINE.json"
OUT_JSON = REPORTS_DIR / "AUDITORIA-GUARDRAILS.json"
OUT_MD = REPORTS_DIR / "AUDITORIA-GUARDRAILS.md"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def count_findings(path: Path) -> tuple[int, int]:
    payload = read_json(path)
    findings = payload.get("findings", [])
    p1 = sum(1 for item in findings if item.get("severity") == "P1")
    p2 = sum(1 for item in findings if item.get("severity") == "P2")
    return p1, p2


def count_items(path: Path) -> tuple[int, int, int]:
    payload = read_json(path)
    items = payload.get("items", [])
    ok = sum(1 for item in items if item.get("severity") == "OK")
    p1 = sum(1 for item in items if item.get("severity") == "P1")
    p2 = sum(1 for item in items if item.get("severity") == "P2")
    return ok, p1, p2


def collect_metrics() -> dict[str, int]:
    continuidad_p1, continuidad_p2 = count_findings(REPORTS_DIR / "AUDITORIA-CONTINUIDAD-PEDAGOGICA.json")
    saltos_p1, saltos_p2 = count_findings(REPORTS_DIR / "AUDITORIA-SALTOS-PRERREQUISITOS-REDUNDANCIAS.json")
    mermaid_p1, mermaid_p2 = count_findings(REPORTS_DIR / "AUDITORIA-MERMAID-SEMANTICA.json")
    snippets_p1, snippets_p2 = count_findings(REPORTS_DIR / "AUDITORIA-SNIPPETS-CALIDAD.json")
    scaffold_p1, scaffold_p2 = count_findings(REPORTS_DIR / "AUDITORIA-TRAZABILIDAD-SCAFFOLD.json")
    links_p1, links_p2 = count_findings(REPORTS_DIR / "AUDITORIA-ENLACES-CRUZADOS.json")
    cierre_p1, cierre_p2 = count_findings(REPORTS_DIR / "AUDITORIA-ARTEFACTOS-CIERRE.json")
    _, plantilla_p1, plantilla_p2 = count_items(REPORTS_DIR / "AUDITORIA-PLANTILLA-PEDAGOGICA.json")

    return {
        "continuidad_p1": continuidad_p1,
        "continuidad_p2": continuidad_p2,
        "saltos_p1": saltos_p1,
        "saltos_p2": saltos_p2,
        "mermaid_p1": mermaid_p1,
        "mermaid_p2": mermaid_p2,
        "snippets_p1": snippets_p1,
        "snippets_p2": snippets_p2,
        "scaffold_p1": scaffold_p1,
        "scaffold_p2": scaffold_p2,
        "links_p1": links_p1,
        "links_p2": links_p2,
        "cierre_p1": cierre_p1,
        "cierre_p2": cierre_p2,
        "plantilla_p1": plantilla_p1,
        "plantilla_p2": plantilla_p2,
    }


@dataclass
class RuleResult:
    name: str
    status: str
    message: str


def evaluate(metrics: dict[str, int], baseline: dict[str, int]) -> list[RuleResult]:
    results: list[RuleResult] = []

    hard_zero = ["snippets_p1", "links_p1", "cierre_p1", "plantilla_p1"]
    for metric in hard_zero:
        value = metrics.get(metric, 0)
        status = "PASS" if value == 0 else "FAIL"
        results.append(
            RuleResult(
                name=f"{metric}_must_be_zero",
                status=status,
                message=f"{metric}={value}",
            )
        )

    tracked = ["continuidad_p1", "saltos_p1", "mermaid_p1", "scaffold_p1"]
    for metric in tracked:
        current = metrics.get(metric, 0)
        base = baseline.get(metric, current)
        status = "PASS" if current <= base else "FAIL"
        results.append(
            RuleResult(
                name=f"{metric}_must_not_regress",
                status=status,
                message=f"baseline={base}, current={current}",
            )
        )

    return results


def write_outputs(metrics: dict[str, int], baseline: dict[str, int], rules: list[RuleResult]) -> None:
    payload = {
        "metrics": metrics,
        "baseline": baseline,
        "rules": [r.__dict__ for r in rules],
        "status": "pass" if all(r.status == "PASS" for r in rules) else "fail",
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Auditoria Guardrails",
        "",
        "## Estado",
        "",
        f"- Status: `{payload['status'].upper()}`",
        "",
        "## Reglas",
        "",
        "| Regla | Estado | Detalle |",
        "|---|---|---|",
    ]
    for rule in rules:
        lines.append(f"| `{rule.name}` | `{rule.status}` | {rule.message} |")

    lines.extend(
        [
            "",
            "## Metricas actuales",
            "",
            "```json",
            json.dumps(metrics, indent=2, ensure_ascii=False),
            "```",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QA regression guardrails")
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="Write current metrics as baseline and exit successfully.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    metrics = collect_metrics()

    if args.write_baseline:
        BASELINE_PATH.write_text(
            json.dumps(metrics, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(str(BASELINE_PATH))
        return 0

    baseline = read_json(BASELINE_PATH)
    if not baseline:
        baseline = metrics

    rules = evaluate(metrics, baseline)
    write_outputs(metrics, baseline, rules)
    print(str(OUT_JSON))
    print(str(OUT_MD))
    return 0 if all(r.status == "PASS" for r in rules) else 1


if __name__ == "__main__":
    raise SystemExit(main())
