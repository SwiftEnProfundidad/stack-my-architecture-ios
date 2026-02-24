#!/usr/bin/env python3
"""Detects complexity jumps, implicit prerequisites and redundancies."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATRIX_JSON = ROOT / "00-informe" / "AUDITORIA-MATRIZ-EJECUTABLE.json"
OUT_JSON = ROOT / "00-informe" / "AUDITORIA-SALTOS-PRERREQUISITOS-REDUNDANCIAS.json"
OUT_MD = ROOT / "00-informe" / "AUDITORIA-SALTOS-PRERREQUISITOS-REDUNDANCIAS.md"

STAGE_ORDER = [
    "Etapa 0 - Core Mobile",
    "Etapa 1 - Junior",
    "Etapa 2 - Mid",
    "Etapa 3 - Senior",
    "Etapa 4 - Arquitecto",
    "Etapa 5 - Maestria",
    "Anexos",
]

TERM_BANK = [
    "clean architecture",
    "feature-first",
    "ddd",
    "bounded context",
    "composition root",
    "swift concurrency",
    "actor",
    "sendable",
    "taskgroup",
    "asyncsequence",
    "swiftui",
    "swiftdata",
    "firebase",
    "deeplink",
    "quality gates",
    "spm",
    "tdd",
    "bdd",
    "domain event",
    "observabilidad",
    "cache",
    "consistencia",
    "integration test",
]


def heading_set(md: str) -> set[str]:
    headings = re.findall(r"(?m)^#{1,6}\s+(.+)$", md)
    normalized = set()
    for h in headings:
        h = re.sub(r"\{#.*?\}\s*$", "", h).strip().lower()
        if h:
            normalized.add(h)
    return normalized


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def load_lessons() -> list[dict]:
    data = json.loads(MATRIX_JSON.read_text(encoding="utf-8"))
    return data.get("lessons", [])


def lesson_content(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def detect_terms(md: str) -> set[str]:
    lowered = md.lower()
    hits = set()
    for term in TERM_BANK:
        if term in lowered:
            hits.add(term)
    return hits


def is_transition_doc(rel_path: str | None) -> bool:
    if not rel_path:
        return False
    name = Path(rel_path).name
    return name.startswith("entregables-etapa-") or "rubrica-final/" in rel_path


def is_expected_complexity_transition(stage: str, prev_rel: str | None, next_rel: str | None) -> bool:
    if stage == "Anexos":
        return True
    if is_transition_doc(next_rel):
        return True
    joined = f"{prev_rel or ''} {next_rel or ''}"
    return "enterprise" in joined or "app-final-etapa-" in joined


def analyze() -> dict:
    lessons = load_lessons()
    by_stage: dict[str, list[dict]] = defaultdict(list)
    for lesson in lessons:
        by_stage[lesson["stage"]].append(lesson)

    findings: list[dict] = []
    stage_summary: list[dict] = []
    seen_terms_global: set[str] = set()

    for stage in STAGE_ORDER:
        stage_lessons = by_stage.get(stage, [])
        if not stage_lessons:
            continue

        stage_counts = {"P1": 0, "P2": 0}
        previous_headings: set[str] | None = None

        for idx, lesson in enumerate(stage_lessons):
            rel = lesson["rel_path"]
            md = lesson_content(rel)
            words = int(lesson.get("word_count", 0))
            has_prereq = bool(lesson.get("has_prerequisites", False))

            terms = detect_terms(md)
            new_terms = terms - seen_terms_global

            if idx > 0:
                prev = stage_lessons[idx - 1]
                prev_rel = prev.get("rel_path")
                prev_words = int(prev.get("word_count", 0))
                max_words = max(prev_words, words, 1)
                min_words = max(min(prev_words, words), 1)
                ratio = max_words / min_words
                delta = abs(prev_words - words)
                if ratio >= 2.2 and delta >= 1000:
                    if is_expected_complexity_transition(stage, prev_rel, rel):
                        findings.append(
                            {
                                "severity": "P2",
                                "kind": "complexity_jump_transition",
                                "stage": stage,
                                "from": prev_rel,
                                "to": rel,
                                "message": (
                                    f"Salto de complejidad en transicion esperada: `{prev_rel}` "
                                    f"({prev_words}) -> `{rel}` ({words})."
                                ),
                            }
                        )
                        stage_counts["P2"] += 1
                    else:
                        findings.append(
                            {
                                "severity": "P1",
                                "kind": "complexity_jump",
                                "stage": stage,
                                "from": prev_rel,
                                "to": rel,
                                "message": (
                                    f"Salto de complejidad: `{prev_rel}` ({prev_words}) -> `{rel}` ({words})."
                                ),
                            }
                        )
                        stage_counts["P1"] += 1

            if len(new_terms) >= 5 and not has_prereq and not rel.endswith("00-introduccion.md"):
                findings.append(
                    {
                        "severity": "P1",
                        "kind": "implicit_prereq",
                        "stage": stage,
                        "path": rel,
                        "message": (
                            f"Prerrequisitos implicitos: `{rel}` introduce {len(new_terms)} terminos nuevos "
                            "sin bloque explicito de prerequisitos."
                        ),
                        "terms": sorted(new_terms),
                    }
                )
                stage_counts["P1"] += 1
            elif len(new_terms) >= 3 and not has_prereq and not rel.endswith("00-introduccion.md"):
                findings.append(
                    {
                        "severity": "P2",
                        "kind": "implicit_prereq",
                        "stage": stage,
                        "path": rel,
                        "message": (
                            f"Posible prerequisito implicito: `{rel}` introduce {len(new_terms)} terminos nuevos "
                            "sin seccion de prerequisitos."
                        ),
                        "terms": sorted(new_terms),
                    }
                )
                stage_counts["P2"] += 1

            current_headings = heading_set(md)
            if previous_headings is not None:
                overlap = jaccard(previous_headings, current_headings)
                if overlap >= 0.70 and words >= 600:
                    findings.append(
                        {
                            "severity": "P1",
                            "kind": "redundancy_adjacent",
                            "stage": stage,
                            "path": rel,
                            "message": (
                                f"Redundancia alta entre lecciones consecutivas (Jaccard headings={overlap:.2f}) "
                                f"en `{rel}`."
                            ),
                        }
                    )
                    stage_counts["P1"] += 1
                elif overlap >= 0.55 and words >= 600:
                    findings.append(
                        {
                            "severity": "P2",
                            "kind": "redundancy_adjacent",
                            "stage": stage,
                            "path": rel,
                            "message": (
                                f"Redundancia media entre lecciones consecutivas (Jaccard headings={overlap:.2f}) "
                                f"en `{rel}`."
                            ),
                        }
                    )
                    stage_counts["P2"] += 1

            previous_headings = current_headings
            seen_terms_global |= terms

        stage_summary.append(
            {
                "stage": stage,
                "lessons": len(stage_lessons),
                "p1": stage_counts["P1"],
                "p2": stage_counts["P2"],
            }
        )

    findings_sorted = sorted(findings, key=lambda x: (x["severity"], x.get("stage", ""), x.get("path", "")))

    return {
        "source": str(MATRIX_JSON),
        "stage_summary": stage_summary,
        "findings_total": len(findings_sorted),
        "findings": findings_sorted,
    }


def to_markdown(payload: dict) -> str:
    lines = []
    lines.append("# Auditoria de Saltos, Prerrequisitos y Redundancias - Curso iOS")
    lines.append("")
    lines.append("## Resumen por etapa")
    lines.append("")
    lines.append("| Etapa | Lecciones | P1 | P2 |")
    lines.append("|---|---:|---:|---:|")
    for s in payload["stage_summary"]:
        lines.append(f"| {s['stage']} | {s['lessons']} | {s['p1']} | {s['p2']} |")

    p1 = [f for f in payload["findings"] if f["severity"] == "P1"]
    p2 = [f for f in payload["findings"] if f["severity"] == "P2"]

    lines.append("")
    lines.append(f"Hallazgos totales: {payload['findings_total']} (P1={len(p1)}, P2={len(p2)})")
    lines.append("")
    lines.append("## Hallazgos P1")
    lines.append("")
    if not p1:
        lines.append("- Sin P1 detectados automaticamente.")
    else:
        for item in p1:
            lines.append(f"- {item['message']}")

    lines.append("")
    lines.append("## Hallazgos P2")
    lines.append("")
    if not p2:
        lines.append("- Sin P2 detectados automaticamente.")
    else:
        for item in p2:
            lines.append(f"- {item['message']}")

    lines.append("")
    lines.append("## Accion sugerida")
    lines.append("")
    lines.append("1. Resolver P1 de prerequisitos implicitos con un bloque fijo de entrada por leccion.")
    lines.append("2. Añadir notas de transicion en saltos de complejidad para evitar ruptura cognitiva.")
    lines.append("3. Podar redundancias moviendo contenido repetido a anexos o referencias cruzadas.")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    payload = analyze()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text(to_markdown(payload), encoding="utf-8")
    print(str(OUT_JSON))
    print(str(OUT_MD))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
