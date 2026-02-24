#!/usr/bin/env python3
"""Normaliza fences Markdown sin lenguaje declarado."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIRS = [
    "00-core-mobile",
    "01-fundamentos",
    "02-integracion",
    "03-evolucion",
    "04-arquitecto",
    "05-maestria",
    "anexos",
]

FENCE_RE = re.compile(r"```[ \t]*\n(.*?)\n```", re.DOTALL)


def detect_lang(code: str) -> str:
    lines = [ln.rstrip() for ln in code.splitlines()]
    non_empty = [ln for ln in lines if ln.strip()]
    head = non_empty[0].strip() if non_empty else ""
    lowered = head.lower()
    joined = "\n".join(non_empty[:6]).lower()

    bash_starts = (
        "$", "git ", "swift ", "xcodebuild ", "cd ", "mkdir ", "ls", "cat ", "./", "make ",
        "curl ", "python ", "python3 ", "npm ", "pnpm ", "yarn ", "brew ", "pod ", "spm ",
    )
    if lowered.startswith(bash_starts):
        return "bash"

    if any(tok in joined for tok in ["import swiftui", "import foundation", "struct ", "class ", "actor ", "protocol ", "func ", "enum "]):
        return "swift"

    if lowered.startswith("{") or lowered.startswith("["):
        return "json"

    if lowered.startswith("graph ") or lowered.startswith("flowchart ") or lowered.startswith("sequencediagram"):
        return "mermaid"

    if lowered.startswith("<") and ">" in lowered:
        return "xml"

    return "text"


def normalize_file(path: Path) -> int:
    original = path.read_text(encoding="utf-8")

    def repl(match: re.Match[str]) -> str:
        code = match.group(1)
        lang = detect_lang(code)
        return f"```{lang}\n{code}\n```"

    updated, count = FENCE_RE.subn(repl, original)
    if count > 0 and updated != original:
        path.write_text(updated, encoding="utf-8")
    return count


def main() -> int:
    total_files = 0
    changed_files = 0
    replaced_fences = 0

    for d in CONTENT_DIRS:
        for path in (ROOT / d).rglob("*.md"):
            total_files += 1
            count = normalize_file(path)
            if count > 0:
                changed_files += 1
                replaced_fences += count

    print(f"files_scanned={total_files} files_changed={changed_files} fences_labeled={replaced_fences}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
