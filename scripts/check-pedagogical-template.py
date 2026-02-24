#!/usr/bin/env python3
"""Comprueba cobertura de plantilla pedagogica minima por leccion."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATRIX_JSON = ROOT / "00-informe" / "AUDITORIA-MATRIZ-EJECUTABLE.json"
OUT_JSON = ROOT / "00-informe" / "AUDITORIA-PLANTILLA-PEDAGOGICA.json"
OUT_MD = ROOT / "00-informe" / "AUDITORIA-PLANTILLA-PEDAGOGICA.md"

PATTERNS = {
    "objetivo": re.compile(r"\bobjetivo\b|que aprenderas|al finalizar", re.IGNORECASE),
    "prerrequisitos": re.compile(r"prerrequisit|requisitos previos|antes de empezar", re.IGNORECASE),
    "practica": re.compile(r"practica|ejercicio|hands-on|reto", re.IGNORECASE),
    "validacion": re.compile(r"validacion|checklist|criterios de exito|verificacion|definition of done", re.IGNORECASE),
}


def load_lessons() -> list[dict]:
    data = json.loads(MATRIX_JSON.read_text(encoding="utf-8"))
    return data.get("lessons", [])


def evaluate(rel_path: str, stage: str) -> dict:
    content = (ROOT / rel_path).read_text(encoding="utf-8")
    hits = {k: bool(p.search(content)) for k, p in PATTERNS.items()}
    missing = [k for k, ok in hits.items() if not ok]

    severity = "OK"
    if len(missing) >= 3:
        severity = "P1"
    elif len(missing) > 0:
        severity = "P2"

    return {
        "rel_path": rel_path,
        "stage": stage,
        "hits": hits,
        "missing": missing,
        "severity": severity,
    }


def to_markdown(items: list[dict]) -> str:
    lines = []
    lines.append("# Auditoria de Plantilla Pedagogica")
    lines.append("")

    total = len(items)
    ok = sum(1 for x in items if x["severity"] == "OK")
    p1 = sum(1 for x in items if x["severity"] == "P1")
    p2 = sum(1 for x in items if x["severity"] == "P2")

    lines.append(f"Cobertura: OK={ok}/{total}, P1={p1}, P2={p2}")
    lines.append("")

    by_stage = {}
    for item in items:
        by_stage.setdefault(item["stage"], []).append(item)

    lines.append("## Resumen por etapa")
    lines.append("")
    lines.append("| Etapa | Lecciones | OK | P1 | P2 |")
    lines.append("|---|---:|---:|---:|---:|")
    for stage, stage_items in by_stage.items():
        s_ok = sum(1 for x in stage_items if x["severity"] == "OK")
        s_p1 = sum(1 for x in stage_items if x["severity"] == "P1")
        s_p2 = sum(1 for x in stage_items if x["severity"] == "P2")
        lines.append(f"| {stage} | {len(stage_items)} | {s_ok} | {s_p1} | {s_p2} |")

    lines.append("")
    lines.append("## P1 (normalizacion prioritaria)")
    lines.append("")
    for item in [x for x in items if x["severity"] == "P1"]:
        lines.append(f"- `{item['rel_path']}`: falta {', '.join(item['missing'])}")

    lines.append("")
    lines.append("## P2 (normalizacion progresiva)")
    lines.append("")
    for item in [x for x in items if x["severity"] == "P2"][:120]:
        lines.append(f"- `{item['rel_path']}`: falta {', '.join(item['missing'])}")

    lines.append("")
    lines.append("## Criterio de cierre")
    lines.append("")
    lines.append("1. P1=0 en etapas 1-5.")
    lines.append("2. P2<=20 en etapas 1-5.")
    lines.append("3. Toda leccion nueva nace con plantilla completa.")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    lessons = load_lessons()
    items = [evaluate(lesson["rel_path"], lesson["stage"]) for lesson in lessons]

    payload = {
        "source": str(MATRIX_JSON),
        "total": len(items),
        "items": items,
    }

    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text(to_markdown(items), encoding="utf-8")
    print(str(OUT_JSON))
    print(str(OUT_MD))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
