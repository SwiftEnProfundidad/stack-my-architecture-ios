#!/usr/bin/env python3
"""Generate consolidated QA report from audit JSON files."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_MD = ROOT / "00-informe" / "AUDITORIA-QA-INTEGRAL.md"
OUT_JSON = ROOT / "00-informe" / "AUDITORIA-QA-INTEGRAL.json"

FILES = {
    "matriz": "00-informe/AUDITORIA-MATRIZ-EJECUTABLE.json",
    "continuidad": "00-informe/AUDITORIA-CONTINUIDAD-PEDAGOGICA.json",
    "saltos": "00-informe/AUDITORIA-SALTOS-PRERREQUISITOS-REDUNDANCIAS.json",
    "plantilla": "00-informe/AUDITORIA-PLANTILLA-PEDAGOGICA.json",
    "mermaid": "00-informe/AUDITORIA-MERMAID-SEMANTICA.json",
    "snippets": "00-informe/AUDITORIA-SNIPPETS-CALIDAD.json",
    "scaffold": "00-informe/AUDITORIA-TRAZABILIDAD-SCAFFOLD.json",
    "links": "00-informe/AUDITORIA-ENLACES-CRUZADOS.json",
    "cierre": "00-informe/AUDITORIA-ARTEFACTOS-CIERRE.json",
    "guardrails": "00-informe/AUDITORIA-GUARDRAILS.json",
}


def read_json(rel: str) -> dict:
    p = ROOT / rel
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def count_severity(items: list[dict], key: str = "severity") -> tuple[int, int]:
    p1 = sum(1 for x in items if x.get(key) == "P1")
    p2 = sum(1 for x in items if x.get(key) == "P2")
    return p1, p2


def main() -> int:
    data = {name: read_json(path) for name, path in FILES.items()}

    lessons_total = data["matriz"].get("lessons_total", 0)

    continuidad_findings = data["continuidad"].get("findings", [])
    c_p1, c_p2 = count_severity(continuidad_findings)

    saltos_findings = data["saltos"].get("findings", [])
    s_p1, s_p2 = count_severity(saltos_findings)

    plantilla_items = data["plantilla"].get("items", [])
    tpl_p1 = sum(1 for x in plantilla_items if x.get("severity") == "P1")
    tpl_p2 = sum(1 for x in plantilla_items if x.get("severity") == "P2")
    tpl_ok = sum(1 for x in plantilla_items if x.get("severity") == "OK")

    mermaid_findings = data["mermaid"].get("findings", [])
    m_p1, m_p2 = count_severity(mermaid_findings)

    snippet_findings = data["snippets"].get("findings", [])
    sn_p1, sn_p2 = count_severity(snippet_findings)

    scaffold_findings = data["scaffold"].get("findings", [])
    sc_p1, sc_p2 = count_severity(scaffold_findings)

    link_findings = data["links"].get("findings", [])
    l_p1, l_p2 = count_severity(link_findings)

    close_findings = data["cierre"].get("findings", [])
    cl_p1, cl_p2 = count_severity(close_findings)

    guardrails_status = data["guardrails"].get("status", "unknown")
    guardrails_rules = data["guardrails"].get("rules", [])
    guardrails_fail = [x for x in guardrails_rules if x.get("status") == "FAIL"]

    controls = [
        {"control": "Continuidad pedagogica", "p1": c_p1, "p2": c_p2, "status": "OK" if c_p1 == 0 else "REVISAR"},
        {"control": "Saltos/prerrequisitos/redundancias", "p1": s_p1, "p2": s_p2, "status": "OK" if s_p1 == 0 else "REVISAR"},
        {"control": "Plantilla pedagogica", "p1": tpl_p1, "p2": tpl_p2, "status": "OK" if tpl_p1 == 0 else "REVISAR"},
        {"control": "Mermaid semantica", "p1": m_p1, "p2": m_p2, "status": "OK" if m_p1 == 0 else "REVISAR"},
        {"control": "Snippets calidad", "p1": sn_p1, "p2": sn_p2, "status": "OK" if sn_p1 == 0 else "REVISAR"},
        {"control": "Trazabilidad scaffold", "p1": sc_p1, "p2": sc_p2, "status": "OK" if sc_p1 == 0 else "REVISAR"},
        {"control": "Enlaces cruzados", "p1": l_p1, "p2": l_p2, "status": "OK" if l_p1 == 0 else "REVISAR"},
        {"control": "Artefactos de cierre", "p1": cl_p1, "p2": cl_p2, "status": "OK" if cl_p1 == 0 else "REVISAR"},
    ]

    lines: list[str] = []
    lines.append("# Auditoria QA Integral - Curso iOS")
    lines.append("")
    lines.append("## Resumen ejecutivo")
    lines.append("")
    lines.append(f"Lecciones auditadas: {lessons_total}")
    lines.append("")
    lines.append("| Control | P1 | P2 | Estado |")
    lines.append("|---|---:|---:|---|")
    for item in controls:
        lines.append(f"| {item['control']} | {item['p1']} | {item['p2']} | {item['status']} |")

    lines.append("")
    lines.append("## Cobertura de plantilla")
    lines.append("")
    lines.append(f"- OK: {tpl_ok}")
    lines.append(f"- P1: {tpl_p1}")
    lines.append(f"- P2: {tpl_p2}")

    lines.append("")
    lines.append("## Guardrails")
    lines.append("")
    lines.append(f"- Estado: `{guardrails_status.upper()}`")
    if guardrails_fail:
        lines.append("- Reglas en fallo:")
        for rule in guardrails_fail:
            lines.append(f"  - `{rule.get('name')}` -> {rule.get('message')}")
    else:
        lines.append("- Sin regresiones frente al baseline.")

    lines.append("")
    lines.append("## Backlog residual (P1)")
    lines.append("")
    residual = [x for x in controls if x["p1"] > 0]
    if residual:
        for item in residual:
            lines.append(f"- {item['control']}: {item['p1']} pendientes")
    else:
        lines.append("- Sin pendientes P1.")

    lines.append("")
    lines.append("## Resultado")
    lines.append("")
    if all(v == 0 for v in [sn_p1, l_p1, cl_p1, tpl_p1]):
        lines.append("- QA tecnico base estable en snippets, enlaces, plantilla y artefactos de cierre.")
    else:
        lines.append("- Existen pendientes P1 en el bloque tecnico base.")

    if c_p1 > 0 or s_p1 > 0 or m_p1 > 0 or sc_p1 > 0:
        lines.append("- Persisten pendientes de contenido/semantica/trazabilidad: mantener ola de correccion por etapas.")
    else:
        lines.append("- No se detectan pendientes P1 en controles priorizados.")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload = {
        "lessons_total": lessons_total,
        "controls": controls,
        "template": {"ok": tpl_ok, "p1": tpl_p1, "p2": tpl_p2},
        "guardrails": {
            "status": guardrails_status,
            "fail_rules": guardrails_fail,
        },
        "residual_p1": {item["control"]: item["p1"] for item in residual},
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(str(OUT_MD))
    print(str(OUT_JSON))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
