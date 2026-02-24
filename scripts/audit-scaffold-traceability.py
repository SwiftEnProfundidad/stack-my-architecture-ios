#!/usr/bin/env python3
"""Audita trazabilidad de lecciones tecnicas contra scaffold real iOS."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATRIX_JSON = ROOT / "00-informe" / "AUDITORIA-MATRIZ-EJECUTABLE.json"
OUT_JSON = ROOT / "00-informe" / "AUDITORIA-TRAZABILIDAD-SCAFFOLD.json"
OUT_MD = ROOT / "00-informe" / "AUDITORIA-TRAZABILIDAD-SCAFFOLD.md"

TARGET_STAGES = {
    "Etapa 2 - Mid",
    "Etapa 3 - Senior",
    "Etapa 4 - Arquitecto",
    "Etapa 5 - Maestria",
}


def load_lessons() -> list[dict]:
    data = json.loads(MATRIX_JSON.read_text(encoding="utf-8"))
    return data.get("lessons", [])


def main() -> int:
    lessons = load_lessons()
    findings = []
    by_stage = {}

    for lesson in lessons:
        stage = lesson.get("stage")
        if stage not in TARGET_STAGES:
            continue

        refs = int(lesson.get("scaffold_ref_hits", 0))
        code = int(lesson.get("code_blocks", 0))
        mermaid = int(lesson.get("mermaid_blocks", 0))

        stage_bucket = by_stage.setdefault(stage, {"total": 0, "with_refs": 0, "without_refs": 0})
        stage_bucket["total"] += 1
        if refs > 0:
            stage_bucket["with_refs"] += 1
        else:
            stage_bucket["without_refs"] += 1

            severity = "P2"
            reason = "Sin referencia explicita al scaffold."
            if code > 0:
                severity = "P1"
                reason = "Tiene snippets pero no referencia al scaffold/ruta real."
            elif mermaid > 0:
                severity = "P2"
                reason = "Tiene Mermaid pero no aterriza en ruta real del scaffold."

            findings.append(
                {
                    "severity": severity,
                    "stage": stage,
                    "path": lesson.get("rel_path"),
                    "code_blocks": code,
                    "mermaid_blocks": mermaid,
                    "reason": reason,
                }
            )

    findings.sort(key=lambda x: (x["severity"], x["stage"], x["path"]))

    payload = {
        "source": str(MATRIX_JSON),
        "stage_summary": by_stage,
        "findings_total": len(findings),
        "findings": findings,
    }

    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    p1 = [f for f in findings if f["severity"] == "P1"]
    p2 = [f for f in findings if f["severity"] == "P2"]

    lines = []
    lines.append("# Auditoria de Trazabilidad contra Scaffold iOS")
    lines.append("")
    lines.append("## Resumen por etapa")
    lines.append("")
    lines.append("| Etapa | Total | Con refs scaffold | Sin refs scaffold |")
    lines.append("|---|---:|---:|---:|")
    for stage, summary in by_stage.items():
        lines.append(
            f"| {stage} | {summary['total']} | {summary['with_refs']} | {summary['without_refs']} |"
        )

    lines.append("")
    lines.append(f"Hallazgos: total={len(findings)} (P1={len(p1)}, P2={len(p2)})")
    lines.append("")

    lines.append("## P1")
    lines.append("")
    if not p1:
        lines.append("- Sin P1 detectados.")
    else:
        for item in p1:
            lines.append(f"- `{item['path']}` ({item['stage']}): {item['reason']}")

    lines.append("")
    lines.append("## P2")
    lines.append("")
    if not p2:
        lines.append("- Sin P2 detectados.")
    else:
        for item in p2:
            lines.append(f"- `{item['path']}` ({item['stage']}): {item['reason']}")

    lines.append("")
    lines.append("## Accion sugerida")
    lines.append("")
    lines.append("1. Añadir al menos 1 referencia `apps/ios/...` por leccion tecnica con snippet.")
    lines.append("2. Si el snippet es pedagogico/no literal, añadir nota de mapeo al scaffold real.")
    lines.append("3. Incluir bloque fijo: `Ruta scaffold relacionada:` en lecciones de etapas 2-5.")
    lines.append("")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(str(OUT_JSON))
    print(str(OUT_MD))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
