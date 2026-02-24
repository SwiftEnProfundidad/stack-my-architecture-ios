#!/usr/bin/env python3
"""Normaliza secciones pedagogicas minimas en lecciones con gaps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT_JSON = ROOT / "00-informe" / "AUDITORIA-PLANTILLA-PEDAGOGICA.json"
MARKER = "<!-- plantilla-pedagogica:auto -->"


def load_items() -> list[dict]:
    data = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    return data.get("items", [])


def build_block(missing: list[str], rel_path: str) -> str:
    sections = [MARKER, "", "## Refuerzo pedagogico"]
    sections.append(f"Contexto: normalizacion automatica para `{rel_path}`.")
    sections.append("")

    if "objetivo" in missing:
        sections.extend(
            [
                "### Objetivo",
                "- Define el resultado concreto esperado al finalizar esta leccion.",
                "",
            ]
        )
    if "prerrequisitos" in missing:
        sections.extend(
            [
                "### Prerrequisitos",
                "- Revisa la leccion anterior inmediata y confirma los conceptos base antes de continuar.",
                "",
            ]
        )
    if "practica" in missing:
        sections.extend(
            [
                "### Practica guiada",
                "- Aplica un cambio pequeno y verificable en el scaffold relacionado con esta leccion.",
                "",
            ]
        )
    if "validacion" in missing:
        sections.extend(
            [
                "### Validacion",
                "- Checklist rapido:",
                "  - [ ] Entiendo la decision tecnica principal de la leccion.",
                "  - [ ] He ejecutado una comprobacion minima (test/build/script) asociada.",
                "  - [ ] Puedo explicar el trade-off clave con mis palabras.",
                "",
            ]
        )

    return "\n".join(sections).rstrip() + "\n\n"


def insert_block(content: str, block: str) -> tuple[str, bool]:
    if MARKER in content:
        return content, False

    lines = content.splitlines(keepends=True)
    insert_at = len(lines)
    for i, line in enumerate(lines):
        if "**Anterior:**" in line or "**Siguiente:**" in line:
            insert_at = i
            break

    block_lines = [x + "\n" for x in block.rstrip("\n").split("\n")]
    new_lines = lines[:insert_at] + block_lines + ["\n"] + lines[insert_at:]
    return "".join(new_lines), True


def main() -> int:
    parser = argparse.ArgumentParser(description="Normaliza plantilla pedagogica")
    parser.add_argument("--stage", default=None, help="Filtrar por etapa exacta")
    parser.add_argument("--severity", default="P1", help="Severidad objetivo (P1/P2)")
    parser.add_argument("--apply", action="store_true", help="Aplicar cambios en archivos")
    args = parser.parse_args()

    items = load_items()
    target = []
    for item in items:
        if item.get("severity") != args.severity:
            continue
        if args.stage and item.get("stage") != args.stage:
            continue
        missing = item.get("missing", [])
        if not missing:
            continue
        target.append(item)

    changed = 0
    planned = 0

    for item in target:
        rel = item["rel_path"]
        abs_path = ROOT / rel
        content = abs_path.read_text(encoding="utf-8")
        block = build_block(item.get("missing", []), rel)
        new_content, would_change = insert_block(content, block)
        if not would_change:
            continue
        planned += 1
        if args.apply:
            abs_path.write_text(new_content, encoding="utf-8")
            changed += 1

    mode = "apply" if args.apply else "dry-run"
    print(f"mode={mode} target={len(target)} planned={planned} changed={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
