#!/usr/bin/env python3
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORE_DIRS = {
    ".git",
    "dist",
    "00-informe",
    "anexos",
    "docs",
    "output",
    ".runtime",
    ".build",
    "project",
    "node_modules",
    "__pycache__",
    "assistant-bridge",
}

ARROWS = ("-->", "-.->", "==>", "--o")
MERMAID_BLOCK = re.compile(r"```mermaid\s*\n(.*?)\n```", re.IGNORECASE | re.DOTALL)

blocks = []
for path in ROOT.rglob("*.md"):
    rel = path.relative_to(ROOT)
    if any(part in IGNORE_DIRS for part in rel.parts):
        continue
    text = path.read_text(encoding="utf-8")
    for match in MERMAID_BLOCK.finditer(text):
        blocks.append((str(rel), match.group(1)))

if not blocks:
    print("[ERROR] No se encontraron bloques mermaid en ruta de curso")
    sys.exit(1)

present = {key: 0 for key in ARROWS}
for _rel, block in blocks:
    for arrow in ARROWS:
        if arrow in block:
            present[arrow] += 1

missing = [arrow for arrow, count in present.items() if count == 0]
if missing:
    print("[ERROR] Faltan semanticas de flecha en mermaid:")
    for arrow in missing:
        print(f"  - {arrow}")
    sys.exit(1)

print(f"[OK] Mermaid semantica validada en {len(blocks)} bloques")
print("[OK] Cobertura de flechas:")
for arrow, count in present.items():
    print(f"  - {arrow}: {count} bloques")
