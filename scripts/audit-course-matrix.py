#!/usr/bin/env python3
"""
Genera una matriz de auditoria ejecutable del curso iOS.

Salidas:
- 00-informe/AUDITORIA-MATRIZ-EJECUTABLE.json
- 00-informe/AUDITORIA-MATRIZ-EJECUTABLE.md
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent.parent
BUILD_HTML_PATH = ROOT / "scripts" / "build-html.py"
OUT_JSON = ROOT / "00-informe" / "AUDITORIA-MATRIZ-EJECUTABLE.json"
OUT_MD = ROOT / "00-informe" / "AUDITORIA-MATRIZ-EJECUTABLE.md"

STAGE_LABELS = {
    "00-core-mobile": "Etapa 0 - Core Mobile",
    "01-fundamentos": "Etapa 1 - Junior",
    "02-integracion": "Etapa 2 - Mid",
    "03-evolucion": "Etapa 3 - Senior",
    "04-arquitecto": "Etapa 4 - Arquitecto",
    "05-maestria": "Etapa 5 - Maestria",
    "anexos": "Anexos",
}

IGNORE_PREFIXES = ("00-informe/",)


@dataclass
class LessonAudit:
    rel_path: str
    stage: str
    title: str
    heading_count: int
    word_count: int
    line_count: int
    mermaid_blocks: int
    code_blocks: int
    scaffold_ref_hits: int
    has_objective: bool
    has_prerequisites: bool
    has_practice: bool
    has_validation: bool
    severity: str
    findings: list[str]


def extract_file_order(py_file: Path) -> list[str]:
    source = py_file.read_text(encoding="utf-8")
    marker = "FILE_ORDER = ["
    start = source.find(marker)
    if start == -1:
        raise RuntimeError("No se encontro FILE_ORDER en scripts/build-html.py")
    start = source.find("[", start)
    depth = 0
    end = -1
    for i in range(start, len(source)):
        c = source[i]
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end == -1:
        raise RuntimeError("No se pudo cerrar FILE_ORDER en scripts/build-html.py")
    raw_list = source[start : end + 1]
    values = ast.literal_eval(raw_list)
    if not isinstance(values, list):
        raise RuntimeError("FILE_ORDER no es una lista valida")
    return [str(v) for v in values]


def classify_stage(rel_path: str) -> str:
    top = rel_path.split("/", 1)[0]
    return STAGE_LABELS.get(top, "Otros")


def parse_title(md: str, fallback: str) -> str:
    for line in md.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def count_words(md: str) -> int:
    return len(re.findall(r"[A-Za-z0-9_]+", md))


def code_block_metrics(md: str) -> tuple[int, int]:
    pattern = re.compile(r"```([^\n]*)\n(.*?)\n```", re.DOTALL)
    code_blocks = 0
    mermaid_blocks = 0
    for match in pattern.finditer(md):
        code_blocks += 1
        lang = (match.group(1) or "").strip().lower()
        if lang == "mermaid":
            mermaid_blocks += 1
    return code_blocks, mermaid_blocks


def scaffold_ref_hits(md: str) -> int:
    checks = [
        r"apps/ios/",
        r"ArchitectureKit",
        r"ArchitectureHostApp",
        r"Package\.swift",
        r"swift test",
        r"quality-gates\.sh",
        r"check-dependencies\.sh",
        r"check-performance-baseline\.sh",
        r"docs/adr/",
    ]
    return sum(len(re.findall(p, md, flags=re.IGNORECASE)) for p in checks)


def has_any(md: str, patterns: Iterable[str]) -> bool:
    return any(re.search(p, md, flags=re.IGNORECASE) for p in patterns)


def evaluate_lesson(rel_path: str) -> LessonAudit:
    abs_path = ROOT / rel_path
    md = abs_path.read_text(encoding="utf-8")
    line_count = len(md.splitlines())
    title = parse_title(md, Path(rel_path).stem.replace("-", " ").title())
    word_count = count_words(md)
    heading_count = len(re.findall(r"(?m)^#{1,6}\s+", md))
    code_blocks, mermaid_blocks = code_block_metrics(md)
    refs = scaffold_ref_hits(md)

    has_objective = has_any(
        md,
        (
            r"\bobjetivo\b",
            r"\bobjetivos\b",
            r"al finalizar",
            r"que aprenderas",
            r"que vas a",
        ),
    )
    has_prereq = has_any(md, (r"prerrequisit", r"requisitos previos", r"antes de empezar"))
    has_practice = has_any(md, (r"ejercicio", r"hands-on", r"practica guiada", r"reto"))
    has_validation = has_any(
        md,
        (
            r"criterios de exito",
            r"checklist",
            r"validacion",
            r"verificacion",
            r"definition of done",
            r"entregable",
            r"rubrica",
        ),
    )

    top = rel_path.split("/", 1)[0]
    is_intro_or_deliverable = bool(
        re.search(r"/00-introduccion\.md$|/entregables-.*\.md$|/10-rubrica-final/", rel_path)
    )

    findings: list[str] = []
    severity = "OK"

    if word_count < 140 and not is_intro_or_deliverable:
        findings.append("Contenido corto (<140 palabras) para una leccion normal.")
        severity = "P2"
    if not has_practice and not is_intro_or_deliverable and top in {
        "01-fundamentos",
        "02-integracion",
        "03-evolucion",
        "04-arquitecto",
        "05-maestria",
    }:
        findings.append("No se detecta bloque de practica/ejercicio.")
        severity = "P1" if severity != "P0" else severity
    if not has_validation and not is_intro_or_deliverable and has_practice:
        findings.append("Hay practica pero falta validacion/checklist explicita.")
        severity = "P1" if severity != "P0" else severity
    if code_blocks == 0 and not is_intro_or_deliverable and top != "anexos":
        findings.append("No se detectan snippets de codigo ni bloques tecnicos.")
        if severity == "OK":
            severity = "P2"
    if refs == 0 and top in {"02-integracion", "03-evolucion", "04-arquitecto", "05-maestria"}:
        findings.append("No se detecta trazabilidad explicita al scaffold/apps iOS.")
        if severity == "OK":
            severity = "P2"

    return LessonAudit(
        rel_path=rel_path,
        stage=classify_stage(rel_path),
        title=title,
        heading_count=heading_count,
        word_count=word_count,
        line_count=line_count,
        mermaid_blocks=mermaid_blocks,
        code_blocks=code_blocks,
        scaffold_ref_hits=refs,
        has_objective=has_objective,
        has_prerequisites=has_prereq,
        has_practice=has_practice,
        has_validation=has_validation,
        severity=severity,
        findings=findings,
    )


def rollup(audits: list[LessonAudit]) -> dict:
    by_stage: dict[str, dict] = {}
    severity_counts = {"OK": 0, "P0": 0, "P1": 0, "P2": 0, "P3": 0}
    for a in audits:
        severity_counts[a.severity] = severity_counts.get(a.severity, 0) + 1
        stage_bucket = by_stage.setdefault(
            a.stage,
            {
                "lessons": 0,
                "words_total": 0,
                "mermaid_total": 0,
                "code_total": 0,
                "refs_total": 0,
                "no_practice": 0,
                "no_validation": 0,
                "p1_or_higher": 0,
            },
        )
        stage_bucket["lessons"] += 1
        stage_bucket["words_total"] += a.word_count
        stage_bucket["mermaid_total"] += a.mermaid_blocks
        stage_bucket["code_total"] += a.code_blocks
        stage_bucket["refs_total"] += a.scaffold_ref_hits
        if not a.has_practice:
            stage_bucket["no_practice"] += 1
        if not a.has_validation:
            stage_bucket["no_validation"] += 1
        if a.severity in {"P0", "P1"}:
            stage_bucket["p1_or_higher"] += 1
    return {"by_stage": by_stage, "severity": severity_counts}


def write_markdown(audits: list[LessonAudit], summary: dict) -> None:
    lines: list[str] = []
    lines.append("# Auditoria Matriz Ejecutable - Curso iOS")
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    lines.append("| Etapa | Lecciones | Mermaid | Snippets | Referencias scaffold | Sin practica | Sin validacion | P1+ |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for stage, s in summary["by_stage"].items():
        lines.append(
            f"| {stage} | {s['lessons']} | {s['mermaid_total']} | {s['code_total']} | "
            f"{s['refs_total']} | {s['no_practice']} | {s['no_validation']} | {s['p1_or_higher']} |"
        )
    lines.append("")
    sev = summary["severity"]
    lines.append(
        f"Severidad global: OK={sev.get('OK', 0)}, P1={sev.get('P1', 0)}, "
        f"P2={sev.get('P2', 0)}, P0={sev.get('P0', 0)}, P3={sev.get('P3', 0)}"
    )
    lines.append("")
    lines.append("## Hallazgos P1")
    lines.append("")
    p1s = [a for a in audits if a.severity == "P1"]
    if not p1s:
        lines.append("- Sin hallazgos P1 detectados automaticamente.")
    else:
        for a in p1s:
            joined = " | ".join(a.findings) if a.findings else "Revisar manualmente."
            lines.append(f"- `{a.rel_path}`: {joined}")
    lines.append("")
    lines.append("## Matriz por leccion")
    lines.append("")
    lines.append(
        "| Path | Etapa | Palabras | Mermaid | Snippets | Obj | Pre | Pract | Valid | Sev |"
    )
    lines.append("|---|---|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|")
    for a in audits:
        lines.append(
            f"| `{a.rel_path}` | {a.stage} | {a.word_count} | {a.mermaid_blocks} | {a.code_blocks} | "
            f"{'Y' if a.has_objective else 'N'} | {'Y' if a.has_prerequisites else 'N'} | "
            f"{'Y' if a.has_practice else 'N'} | {'Y' if a.has_validation else 'N'} | {a.severity} |"
        )
    lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    file_order = extract_file_order(BUILD_HTML_PATH)
    lesson_paths = []
    for rel in file_order:
        if not rel.endswith(".md"):
            continue
        if rel.startswith(IGNORE_PREFIXES):
            continue
        abs_path = ROOT / rel
        if abs_path.exists():
            lesson_paths.append(rel)

    audits = [evaluate_lesson(rel_path) for rel_path in lesson_paths]
    summary = rollup(audits)
    payload = {
        "source": "scripts/build-html.py::FILE_ORDER",
        "lessons_total": len(audits),
        "summary": summary,
        "lessons": [asdict(a) for a in audits],
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(audits, summary)
    print(str(OUT_JSON))
    print(str(OUT_MD))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
