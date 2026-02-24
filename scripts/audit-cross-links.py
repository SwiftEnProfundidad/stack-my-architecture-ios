#!/usr/bin/env python3
"""Audita enlaces markdown internos entre lecciones."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = ROOT / "00-informe" / "AUDITORIA-ENLACES-CRUZADOS.json"
OUT_MD = ROOT / "00-informe" / "AUDITORIA-ENLACES-CRUZADOS.md"

CONTENT_DIRS = [
    "00-core-mobile",
    "01-fundamentos",
    "02-integracion",
    "03-evolucion",
    "04-arquitecto",
    "05-maestria",
    "anexos",
    "00-informe",
]

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
HEADING_RE = re.compile(r"(?m)^#{1,6}\s+(.+)$")


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\{#([A-Za-z0-9_-]+)\}\s*$", r"\1", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def heading_anchors(md_text: str) -> set[str]:
    anchors = set()
    for raw in HEADING_RE.findall(md_text):
        raw = raw.strip()
        custom = re.search(r"\{#([A-Za-z0-9_-]+)\}\s*$", raw)
        if custom:
            anchors.add(custom.group(1).lower())
            raw = re.sub(r"\s*\{#([A-Za-z0-9_-]+)\}\s*$", "", raw).strip()
        anchors.add(slugify(raw))
    return anchors


def iter_markdown_files() -> list[Path]:
    files = []
    for d in CONTENT_DIRS:
        files.extend((ROOT / d).rglob("*.md"))
    return sorted(set(files))


def audit() -> dict:
    findings = []
    total_links = 0

    cache_md = {}

    for md_file in iter_markdown_files():
        text = md_file.read_text(encoding="utf-8")
        rel_source = str(md_file.relative_to(ROOT))

        for _, href in LINK_RE.findall(text):
            href = href.strip()
            if href.startswith(("http://", "https://", "mailto:", "tel:")):
                continue
            if href.startswith("#"):
                # Anchor local en mismo archivo
                total_links += 1
                anchor = href[1:].strip().lower()
                anchors = heading_anchors(text)
                if anchor and anchor not in anchors:
                    findings.append(
                        {
                            "severity": "P2",
                            "source": rel_source,
                            "href": href,
                            "reason": "Anchor local no encontrado en el mismo archivo.",
                        }
                    )
                continue

            total_links += 1
            path_part, _, anchor_part = href.partition("#")
            target = (md_file.parent / path_part).resolve()
            if not target.exists():
                findings.append(
                    {
                        "severity": "P1",
                        "source": rel_source,
                        "href": href,
                        "reason": "Ruta objetivo no existe.",
                    }
                )
                continue

            if target.suffix.lower() != ".md":
                continue

            if anchor_part:
                key = str(target)
                if key not in cache_md:
                    cache_md[key] = target.read_text(encoding="utf-8")
                anchors = heading_anchors(cache_md[key])
                if anchor_part.lower() not in anchors:
                    findings.append(
                        {
                            "severity": "P2",
                            "source": rel_source,
                            "href": href,
                            "reason": "Anchor en archivo destino no encontrado.",
                        }
                    )

    findings.sort(key=lambda x: (x["severity"], x["source"], x["href"]))
    return {"total_links": total_links, "findings": findings, "findings_total": len(findings)}


def to_markdown(payload: dict) -> str:
    findings = payload["findings"]
    p1 = [f for f in findings if f["severity"] == "P1"]
    p2 = [f for f in findings if f["severity"] == "P2"]

    lines = []
    lines.append("# Auditoria de Enlaces Cruzados")
    lines.append("")
    lines.append(
        f"Links auditados: {payload['total_links']} | Hallazgos: {payload['findings_total']} "
        f"(P1={len(p1)}, P2={len(p2)})"
    )
    lines.append("")

    lines.append("## P1")
    lines.append("")
    if not p1:
        lines.append("- Sin P1 detectados.")
    else:
        for item in p1:
            lines.append(f"- `{item['source']}` -> `{item['href']}`: {item['reason']}")

    lines.append("")
    lines.append("## P2")
    lines.append("")
    if not p2:
        lines.append("- Sin P2 detectados.")
    else:
        for item in p2[:200]:
            lines.append(f"- `{item['source']}` -> `{item['href']}`: {item['reason']}")

    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    payload = audit()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text(to_markdown(payload), encoding="utf-8")
    print(str(OUT_JSON))
    print(str(OUT_MD))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
