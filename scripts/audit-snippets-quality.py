#!/usr/bin/env python3
"""Audita snippets de codigo: consistencia, capas y nomenclatura."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATRIX_JSON = ROOT / "00-informe" / "AUDITORIA-MATRIZ-EJECUTABLE.json"
OUT_JSON = ROOT / "00-informe" / "AUDITORIA-SNIPPETS-CALIDAD.json"
OUT_MD = ROOT / "00-informe" / "AUDITORIA-SNIPPETS-CALIDAD.md"


def load_paths() -> list[str]:
    data = json.loads(MATRIX_JSON.read_text(encoding="utf-8"))
    return [x["rel_path"] for x in data.get("lessons", [])]


def extract_code_blocks(md: str) -> list[dict]:
    blocks = []
    pattern = re.compile(r"```([^\n]*)\n(.*?)\n```", re.DOTALL)
    for i, m in enumerate(pattern.finditer(md), start=1):
        lang = (m.group(1) or "").strip().lower()
        code = m.group(2)
        blocks.append({"index": i, "lang": lang, "code": code})
    return blocks


def analyze_path(rel_path: str) -> tuple[list[dict], int]:
    content = (ROOT / rel_path).read_text(encoding="utf-8")
    blocks = extract_code_blocks(content)
    findings = []
    has_mapping_note = ("<!-- snippet-mapping-note:auto -->" in content) or ("Nota de nomenclatura pedagógica" in content)

    for block in blocks:
        lang = block["lang"]
        code = block["code"]
        idx = block["index"]

        if lang == "mermaid":
            continue

        if not lang:
            findings.append(
                {
                    "severity": "P2",
                    "path": rel_path,
                    "block_index": idx,
                    "message": "Snippet sin lenguaje declarado (```lang).",
                }
            )

        if any(len(line) > 220 for line in code.splitlines()):
            findings.append(
                {
                    "severity": "P2",
                    "path": rel_path,
                    "block_index": idx,
                    "message": "Snippet con lineas muy largas (>220 chars).",
                }
            )

        lower = code.lower()

        if "/domain" in rel_path.lower():
            if any(k in lower for k in ["urlsession", "firebase", "swiftdata", "alamofire", "@mainactor"]):
                findings.append(
                    {
                        "severity": "P1",
                        "path": rel_path,
                        "block_index": idx,
                        "message": "Posible contaminacion de infraestructura en leccion Domain.",
                    }
                )

        if "/application" in rel_path.lower():
            if "import swiftui" in lower or "view" in lower:
                findings.append(
                    {
                        "severity": "P2",
                        "path": rel_path,
                        "block_index": idx,
                        "message": "Posible mezcla Application/UI en snippet.",
                    }
                )

        if (
            "productrepository" in lower
            and "catalogrepository" not in lower
            and "02-integracion" in rel_path
            and not has_mapping_note
        ):
            findings.append(
                {
                    "severity": "P2",
                    "path": rel_path,
                    "block_index": idx,
                    "message": "Nomenclatura potencialmente desalineada (ProductRepository vs CatalogRepository).",
                }
            )

    return findings, len([b for b in blocks if b["lang"] != "mermaid"])


def to_markdown(payload: dict) -> str:
    findings = payload["findings"]
    p1 = [f for f in findings if f["severity"] == "P1"]
    p2 = [f for f in findings if f["severity"] == "P2"]

    lines = []
    lines.append("# Auditoria de Calidad de Snippets")
    lines.append("")
    lines.append(
        f"Snippets auditados: {payload['snippets_total']} | Hallazgos: {len(findings)} "
        f"(P1={len(p1)}, P2={len(p2)})"
    )
    lines.append("")

    lines.append("## Hallazgos P1")
    lines.append("")
    if not p1:
        lines.append("- Sin P1 detectados.")
    else:
        for item in p1:
            lines.append(f"- `{item['path']}` bloque #{item['block_index']}: {item['message']}")

    lines.append("")
    lines.append("## Hallazgos P2")
    lines.append("")
    if not p2:
        lines.append("- Sin P2 detectados.")
    else:
        for item in p2[:200]:
            lines.append(f"- `{item['path']}` bloque #{item['block_index']}: {item['message']}")

    lines.append("")
    lines.append("## Recomendacion")
    lines.append("")
    lines.append("1. Forzar lenguaje en todos los bloques de codigo.")
    lines.append("2. Etiquetar snippets pedagogicos cuando no reflejen naming del scaffold literal.")
    lines.append("3. Mantener reglas de capa: Domain sin dependencias de UI/infra.")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    all_findings = []
    snippets_total = 0

    for rel_path in load_paths():
        findings, snippets = analyze_path(rel_path)
        snippets_total += snippets
        all_findings.extend(findings)

    payload = {
        "source": str(MATRIX_JSON),
        "snippets_total": snippets_total,
        "findings": all_findings,
    }

    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text(to_markdown(payload), encoding="utf-8")

    print(str(OUT_JSON))
    print(str(OUT_MD))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
