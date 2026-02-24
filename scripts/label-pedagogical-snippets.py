#!/usr/bin/env python3
"""Inserta nota de mapeo cuando los snippets usan naming pedagogico no literal."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNIPPETS_AUDIT_JSON = ROOT / "00-informe" / "AUDITORIA-SNIPPETS-CALIDAD.json"
MARKER = "<!-- snippet-mapping-note:auto -->"

NOTE_BLOCK = (
    f"{MARKER}\n"
    "> **Nota de nomenclatura pedagógica**\n"
    "> Algunos snippets de esta lección usan `ProductRepository` como nombre conceptual.\n"
    "> En el scaffold real (`apps/ios/ArchitectureKit`) el equivalente operativo es `CatalogRepository`.\n"
    "\n"
)


def target_paths() -> list[str]:
    data = json.loads(SNIPPETS_AUDIT_JSON.read_text(encoding="utf-8"))
    paths = set()
    for item in data.get("findings", []):
        if "ProductRepository" in item.get("message", ""):
            paths.add(item["path"])
    return sorted(paths)


def inject_note(content: str) -> tuple[str, bool]:
    if MARKER in content:
        return content, False

    lines = content.splitlines(keepends=True)
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("# "):
            insert_at = i + 1
            # Skip empty lines after title for cleaner placement
            while insert_at < len(lines) and lines[insert_at].strip() == "":
                insert_at += 1
            break

    note_lines = [x + "\n" for x in NOTE_BLOCK.rstrip("\n").split("\n")]
    new_lines = lines[:insert_at] + ["\n"] + note_lines + lines[insert_at:]
    return "".join(new_lines), True


def main() -> int:
    changed = 0
    paths = target_paths()

    for rel in paths:
        abs_path = ROOT / rel
        content = abs_path.read_text(encoding="utf-8")
        updated, did_change = inject_note(content)
        if did_change:
            abs_path.write_text(updated, encoding="utf-8")
            changed += 1

    print(f"targets={len(paths)} changed={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
