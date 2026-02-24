#!/usr/bin/env python3
"""Adds scaffold traceability block to lessons flagged as P1."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "00-informe" / "AUDITORIA-TRAZABILIDAD-SCAFFOLD.json"

BLOCK = (
    "\n## Ruta scaffold relacionada\n\n"
    "- `apps/ios/ArchitectureKit/Sources/` para implementacion de codigo real de esta leccion.\n"
    "- `apps/ios/ArchitectureKit/Tests/` para validacion y regresion de contratos.\n"
    "- `apps/ios/ArchitectureHostApp/` cuando la leccion impacta navegacion/UI integrada.\n"
)


def inject_block(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "## Ruta scaffold relacionada" in text:
        return False

    lines = text.splitlines()
    if not lines:
        return False

    insert_at = 1
    while insert_at < len(lines) and lines[insert_at].strip() == "":
        insert_at += 1

    updated = lines[:insert_at] + [""] + BLOCK.strip("\n").split("\n") + [""] + lines[insert_at:]
    path.write_text("\n".join(updated).rstrip() + "\n", encoding="utf-8")
    return True


def main() -> int:
    if not REPORT.exists():
        print(f"Missing report: {REPORT}")
        return 1

    payload = json.loads(REPORT.read_text(encoding="utf-8"))
    findings = payload.get("findings", [])
    targets = [f["path"] for f in findings if f.get("severity") == "P1"]

    changed = 0
    for rel in targets:
        abs_path = ROOT / rel
        if abs_path.exists() and inject_block(abs_path):
            changed += 1

    print(json.dumps({"targets": len(targets), "changed": changed}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
