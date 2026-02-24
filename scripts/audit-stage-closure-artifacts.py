#!/usr/bin/env python3
"""Revalida artefactos de cierre por etapa y su trazabilidad."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = ROOT / "00-informe" / "AUDITORIA-ARTEFACTOS-CIERRE.json"
OUT_MD = ROOT / "00-informe" / "AUDITORIA-ARTEFACTOS-CIERRE.md"

EXPECTATIONS = {
    "Etapa 1": {
        "intro": "01-fundamentos/00-introduccion.md",
        "must_exist": ["01-fundamentos/entregables-etapa-1.md"],
        "must_reference": ["entregables-etapa-1.md"],
    },
    "Etapa 2": {
        "intro": "02-integracion/00-introduccion.md",
        "must_exist": [
            "02-integracion/entregables-etapa-2.md",
            "anexos/consolidacion-etapa-2-integracion.md",
        ],
        "must_reference": ["entregables-etapa-2.md"],
    },
    "Etapa 3": {
        "intro": "03-evolucion/00-introduccion.md",
        "must_exist": [
            "03-evolucion/entregables-etapa-3.md",
            "anexos/calentamiento-etapa-3-evolucion.md",
        ],
        "must_reference": ["entregables-etapa-3.md"],
    },
    "Etapa 4": {
        "intro": "04-arquitecto/00-introduccion.md",
        "must_exist": [
            "04-arquitecto/entregables-etapa-4.md",
            "anexos/consolidacion-etapa-4-arquitecto.md",
        ],
        "must_reference": ["entregables-etapa-4.md"],
    },
    "Etapa 5": {
        "intro": "05-maestria/00-introduccion.md",
        "must_exist": [
            "05-maestria/entregables-etapa-5.md",
            "05-maestria/10-rubrica-final/01-rubrica-empleabilidad-ios.md",
            "05-maestria/10-rubrica-final/02-evidencias-obligatorias-ios.md",
            "05-maestria/10-rubrica-final/03-checklist-entrega-para-entrevista.md",
            "anexos/calentamiento-etapa-5-maestria.md",
        ],
        "must_reference": ["entregables-etapa-5.md", "10-rubrica-final/01-rubrica-empleabilidad-ios.md"],
    },
}


def main() -> int:
    findings = []

    for stage, cfg in EXPECTATIONS.items():
        intro_path = ROOT / cfg["intro"]
        intro_text = intro_path.read_text(encoding="utf-8") if intro_path.exists() else ""

        if not intro_path.exists():
            findings.append(
                {
                    "severity": "P1",
                    "stage": stage,
                    "path": cfg["intro"],
                    "reason": "Archivo de introduccion de etapa no existe.",
                }
            )
            continue

        for rel in cfg["must_exist"]:
            p = ROOT / rel
            if not p.exists():
                findings.append(
                    {
                        "severity": "P1",
                        "stage": stage,
                        "path": rel,
                        "reason": "Artefacto de cierre requerido no existe.",
                    }
                )

        for token in cfg["must_reference"]:
            if token not in intro_text:
                findings.append(
                    {
                        "severity": "P2",
                        "stage": stage,
                        "path": cfg["intro"],
                        "reason": f"Intro de etapa no referencia `{token}`.",
                    }
                )

    findings.sort(key=lambda x: (x["severity"], x["stage"], x["path"]))
    payload = {"findings_total": len(findings), "findings": findings}
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    p1 = [f for f in findings if f["severity"] == "P1"]
    p2 = [f for f in findings if f["severity"] == "P2"]

    lines = []
    lines.append("# Auditoria de Artefactos de Cierre")
    lines.append("")
    lines.append(f"Hallazgos: total={len(findings)} (P1={len(p1)}, P2={len(p2)})")
    lines.append("")
    lines.append("## P1")
    lines.append("")
    if not p1:
        lines.append("- Sin P1 detectados.")
    else:
        for item in p1:
            lines.append(f"- [{item['stage']}] `{item['path']}`: {item['reason']}")

    lines.append("")
    lines.append("## P2")
    lines.append("")
    if not p2:
        lines.append("- Sin P2 detectados.")
    else:
        for item in p2:
            lines.append(f"- [{item['stage']}] `{item['path']}`: {item['reason']}")

    lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(str(OUT_JSON))
    print(str(OUT_MD))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
