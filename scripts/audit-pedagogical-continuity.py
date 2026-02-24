#!/usr/bin/env python3
"""Audits pedagogical continuity between lessons by stage."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATRIX_JSON = ROOT / "00-informe" / "AUDITORIA-MATRIZ-EJECUTABLE.json"
OUT_JSON = ROOT / "00-informe" / "AUDITORIA-CONTINUIDAD-PEDAGOGICA.json"
OUT_MD = ROOT / "00-informe" / "AUDITORIA-CONTINUIDAD-PEDAGOGICA.md"

STAGE_ORDER = [
    "Etapa 0 - Core Mobile",
    "Etapa 1 - Junior",
    "Etapa 2 - Mid",
    "Etapa 3 - Senior",
    "Etapa 4 - Arquitecto",
    "Etapa 5 - Maestria",
    "Anexos",
]


def clamp_score(value: int) -> int:
    return max(0, min(100, value))


def load_lessons() -> list[dict]:
    data = json.loads(MATRIX_JSON.read_text(encoding="utf-8"))
    return data.get("lessons", [])


def is_transition_doc(rel_path: str | None) -> bool:
    if not rel_path:
        return False
    name = Path(rel_path).name
    return name.startswith("entregables-etapa-") or "rubrica-final/" in rel_path


def is_expected_complexity_transition(stage: str, current_rel: str | None, next_rel: str | None) -> bool:
    if stage == "Anexos":
        return True
    if is_transition_doc(next_rel):
        return True
    joined = f"{current_rel or ''} {next_rel or ''}"
    return "enterprise" in joined or "app-final-etapa-" in joined


def analyze_stage(stage: str, lessons: list[dict]) -> dict:
    findings = []
    penalties = 0

    no_practice = sum(1 for l in lessons if not l.get("has_practice", False))
    no_validation = sum(1 for l in lessons if not l.get("has_validation", False))

    total = len(lessons) or 1
    no_practice_ratio = no_practice / total
    no_validation_ratio = no_validation / total

    if no_practice_ratio >= 0.45 and stage.startswith("Etapa"):
        findings.append(
            {
                "severity": "P1",
                "type": "stage_density",
                "message": (
                    f"{stage}: {no_practice}/{total} lecciones sin practica explicita "
                    f"({no_practice_ratio:.0%})."
                ),
            }
        )
        penalties += 18

    if no_validation_ratio >= 0.45 and stage.startswith("Etapa"):
        findings.append(
            {
                "severity": "P1",
                "type": "stage_validation",
                "message": (
                    f"{stage}: {no_validation}/{total} lecciones sin validacion/checklist "
                    f"({no_validation_ratio:.0%})."
                ),
            }
        )
        penalties += 15

    for i in range(len(lessons) - 1):
        current = lessons[i]
        nxt = lessons[i + 1]

        current_rel = current.get("rel_path")
        next_rel = nxt.get("rel_path")

        c_words = int(current.get("word_count", 0))
        n_words = int(nxt.get("word_count", 0))
        max_words = max(c_words, n_words, 1)
        min_words = max(min(c_words, n_words), 1)
        ratio = max_words / min_words
        delta = abs(c_words - n_words)

        if ratio >= 2.2 and delta >= 1000:
            if is_expected_complexity_transition(stage, current_rel, next_rel):
                findings.append(
                    {
                        "severity": "P2",
                        "type": "jump_complexity_transition",
                        "from": current_rel,
                        "to": next_rel,
                        "message": (
                            f"Salto de carga en transicion esperada entre `{current_rel}` "
                            f"({c_words} palabras) y `{next_rel}` ({n_words} palabras)."
                        ),
                    }
                )
                penalties += 3
            else:
                findings.append(
                    {
                        "severity": "P1",
                        "type": "jump_complexity",
                        "from": current_rel,
                        "to": next_rel,
                        "message": (
                            f"Salto de carga entre `{current_rel}` ({c_words} palabras) "
                            f"y `{next_rel}` ({n_words} palabras)."
                        ),
                    }
                )
                penalties += 10

        current_practice = bool(current.get("has_practice", False))
        next_practice = bool(nxt.get("has_practice", False))
        if not current_practice and not next_practice and stage.startswith("Etapa"):
            severity = "P2" if is_transition_doc(current_rel) or is_transition_doc(next_rel) else "P1"
            findings.append(
                {
                    "severity": severity,
                    "type": "practice_gap",
                    "from": current_rel,
                    "to": next_rel,
                    "message": (
                        f"Dos lecciones consecutivas sin practica explicita: "
                        f"`{current_rel}` -> `{next_rel}`."
                    ),
                }
            )
            penalties += 3 if severity == "P2" else 8

        current_validation = bool(current.get("has_validation", False))
        next_prereq = bool(nxt.get("has_prerequisites", False))
        if not current_validation and not next_prereq and stage.startswith("Etapa"):
            findings.append(
                {
                    "severity": "P2",
                    "type": "handoff_soft",
                    "from": current_rel,
                    "to": next_rel,
                    "message": (
                        f"Transicion potencialmente debil (sin cierre/validacion previa y sin "
                        f"prerrequisitos explicitos en la siguiente): `{current_rel}` -> `{next_rel}`."
                    ),
                }
            )
            penalties += 3

        current_sev = current.get("severity", "OK")
        next_sev = nxt.get("severity", "OK")
        if current_sev == "P1" and next_sev == "P1":
            findings.append(
                {
                    "severity": "P1",
                    "type": "stacked_risk",
                    "from": current_rel,
                    "to": next_rel,
                    "message": (
                        "Riesgo acumulado: dos lecciones consecutivas marcadas como P1 "
                        f"en matriz base: `{current_rel}` -> `{next_rel}`."
                    ),
                }
            )
            penalties += 6

    score = clamp_score(100 - penalties)
    return {
        "stage": stage,
        "lessons": len(lessons),
        "score": score,
        "no_practice": no_practice,
        "no_validation": no_validation,
        "findings": findings,
    }


def to_markdown(stage_reports: list[dict], global_findings: list[dict]) -> str:
    lines: list[str] = []
    lines.append("# Auditoria de Continuidad Pedagogica - Curso iOS")
    lines.append("")
    lines.append("## Resumen por etapa")
    lines.append("")
    lines.append("| Etapa | Lecciones | Score continuidad | Sin practica | Sin validacion | Hallazgos |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for report in stage_reports:
        lines.append(
            f"| {report['stage']} | {report['lessons']} | {report['score']} | "
            f"{report['no_practice']} | {report['no_validation']} | {len(report['findings'])} |"
        )

    p1 = [f for f in global_findings if f.get("severity") == "P1"]
    p2 = [f for f in global_findings if f.get("severity") == "P2"]

    lines.append("")
    lines.append(f"Hallazgos: P1={len(p1)}, P2={len(p2)}")
    lines.append("")
    lines.append("## Hallazgos P1 (prioridad)")
    lines.append("")
    if not p1:
        lines.append("- Sin hallazgos P1 detectados automaticamente.")
    else:
        for item in p1:
            lines.append(f"- {item['message']}")

    lines.append("")
    lines.append("## Hallazgos P2 (pulido)")
    lines.append("")
    if not p2:
        lines.append("- Sin hallazgos P2 detectados automaticamente.")
    else:
        for item in p2[:120]:
            lines.append(f"- {item['message']}")

    lines.append("")
    lines.append("## Propuesta inmediata")
    lines.append("")
    lines.append("1. Priorizar etapas con score < 70 para cerrar gaps consecutivos de practica.")
    lines.append("2. Añadir bloque fijo por leccion: objetivo, prerequisitos, practica guiada, checklist de validacion.")
    lines.append("3. Revisar transiciones P1 consecutivas con una mini-seccion de puente didactico.")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    lessons = load_lessons()

    by_stage: dict[str, list[dict]] = {}
    for lesson in lessons:
        stage = lesson.get("stage", "Otros")
        by_stage.setdefault(stage, []).append(lesson)

    stage_reports: list[dict] = []
    global_findings: list[dict] = []

    for stage in STAGE_ORDER:
        stage_lessons = by_stage.get(stage, [])
        if not stage_lessons:
            continue
        report = analyze_stage(stage, stage_lessons)
        stage_reports.append(report)
        global_findings.extend(report["findings"])

    payload = {
        "source": str(MATRIX_JSON),
        "stage_reports": stage_reports,
        "findings_total": len(global_findings),
        "findings": global_findings,
    }

    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text(to_markdown(stage_reports, global_findings), encoding="utf-8")

    print(str(OUT_JSON))
    print(str(OUT_MD))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
