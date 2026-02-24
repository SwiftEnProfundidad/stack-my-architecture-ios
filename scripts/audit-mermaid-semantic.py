#!/usr/bin/env python3
"""Audits semantic coherence between Mermaid diagrams and nearby narrative."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATRIX_JSON = ROOT / "00-informe" / "AUDITORIA-MATRIZ-EJECUTABLE.json"
OUT_JSON = ROOT / "00-informe" / "AUDITORIA-MERMAID-SEMANTICA.json"
OUT_MD = ROOT / "00-informe" / "AUDITORIA-MERMAID-SEMANTICA.md"

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "into",
    "that",
    "this",
    "una",
    "unos",
    "unas",
    "como",
    "para",
    "con",
    "del",
    "las",
    "los",
    "por",
    "que",
    "uno",
    "de",
    "la",
    "el",
    "en",
    "flowchart",
    "graph",
    "subgraph",
    "end",
    "classdef",
    "style",
    "linkstyle",
    "click",
    "direction",
    "left",
    "right",
    "top",
    "bottom",
    "node",
    "edge",
    "title",
    "chart",
    "sequence",
    "state",
}


def normalize_tokens(text: str) -> set[str]:
    words = re.findall(r"[A-Za-z0-9_áéíóúñü]+", text.lower())
    return {w for w in words if len(w) >= 4 and w not in STOPWORDS}


def load_lesson_paths() -> list[str]:
    data = json.loads(MATRIX_JSON.read_text(encoding="utf-8"))
    return [lesson["rel_path"] for lesson in data.get("lessons", [])]


def extract_mermaid_blocks(content: str) -> list[tuple[int, int, str]]:
    blocks: list[tuple[int, int, str]] = []
    pattern = re.compile(r"```mermaid\n(.*?)\n```", re.DOTALL | re.IGNORECASE)
    for m in pattern.finditer(content):
        blocks.append((m.start(), m.end(), m.group(1)))
    return blocks


def classify_severity(rel_path: str, overlap_ratio: float, token_count: int) -> tuple[str, str]:
    if token_count <= 6:
        if overlap_ratio < 0.08:
            return "P2", "Bloque mermaid corto con poco puente narrativo cercano."
        return "OK", "Coherencia aceptable."

    p1_threshold = 0.06
    p2_threshold = 0.14

    # Intro lessons tend to include overview diagrams with broad labels.
    if rel_path.endswith("00-introduccion.md"):
        p1_threshold = 0.04
        p2_threshold = 0.11

    if overlap_ratio < p1_threshold:
        return "P1", "Baja coherencia semantica diagrama<->narrativa cercana."
    if overlap_ratio < p2_threshold:
        return "P2", "Coherencia media-baja; revisar texto puente del diagrama."
    return "OK", "Coherencia aceptable."


def analyze_file(rel_path: str) -> list[dict]:
    content = (ROOT / rel_path).read_text(encoding="utf-8")
    blocks = extract_mermaid_blocks(content)
    findings = []

    for idx, (start, end, mermaid_code) in enumerate(blocks, start=1):
        context_start = max(0, start - 1200)
        context_end = min(len(content), end + 900)
        context = content[context_start:start] + "\n" + content[end:context_end]

        mermaid_tokens = normalize_tokens(mermaid_code)
        context_tokens = normalize_tokens(context)
        if not mermaid_tokens:
            continue

        overlap = mermaid_tokens & context_tokens
        overlap_ratio = len(overlap) / max(len(mermaid_tokens), 1)
        severity, message = classify_severity(rel_path, overlap_ratio, len(mermaid_tokens))

        findings.append(
            {
                "path": rel_path,
                "block_index": idx,
                "severity": severity,
                "overlap_ratio": round(overlap_ratio, 3),
                "mermaid_tokens": len(mermaid_tokens),
                "context_tokens": len(context_tokens),
                "overlap_tokens": sorted(list(overlap))[:25],
                "message": message,
            }
        )

    return findings


def to_markdown(findings: list[dict]) -> str:
    p1 = [f for f in findings if f["severity"] == "P1"]
    p2 = [f for f in findings if f["severity"] == "P2"]
    ok = [f for f in findings if f["severity"] == "OK"]

    lines = []
    lines.append("# Auditoria Semantica Mermaid")
    lines.append("")
    lines.append(f"Bloques auditados: {len(findings)} (OK={len(ok)}, P1={len(p1)}, P2={len(p2)})")
    lines.append("")

    lines.append("## Hallazgos P1")
    lines.append("")
    if not p1:
        lines.append("- Sin P1 detectados.")
    else:
        for item in p1:
            lines.append(
                f"- `{item['path']}` bloque #{item['block_index']} "
                f"(overlap={item['overlap_ratio']}): {item['message']}"
            )

    lines.append("")
    lines.append("## Hallazgos P2")
    lines.append("")
    if not p2:
        lines.append("- Sin P2 detectados.")
    else:
        for item in p2[:200]:
            lines.append(
                f"- `{item['path']}` bloque #{item['block_index']} "
                f"(overlap={item['overlap_ratio']}): {item['message']}"
            )

    lines.append("")
    lines.append("## Recomendacion")
    lines.append("")
    lines.append("1. En cada diagrama P1/P2, añadir 2-3 frases puente justo antes o despues del Mermaid.")
    lines.append("2. Reutilizar nomenclatura del diagrama en el texto (mismos terminos).")
    lines.append("3. Evitar diagramas huerfanos sin introduccion o cierre narrativo inmediato.")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    paths = load_lesson_paths()
    all_findings = []
    for rel in paths:
        all_findings.extend(analyze_file(rel))

    payload = {
        "source": str(MATRIX_JSON),
        "blocks_total": len(all_findings),
        "findings": all_findings,
    }

    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text(to_markdown(all_findings), encoding="utf-8")
    print(str(OUT_JSON))
    print(str(OUT_MD))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
