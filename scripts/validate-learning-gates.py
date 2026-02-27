#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "00-informe"

REQUIRED = {
    "MATRIZ-COMPETENCIAS.md": [
        "# Matriz de competencias",
        "## Niveles y evidencias",
        "## Criterio de paso",
    ],
    "RUBRICA-GATES-POR-FASE.md": [
        "# Rubrica de gates por fase",
        "## Gates por fase",
        "## Regla de aprobado",
    ],
    "SCORECARD-EMPLEABILIDAD.md": [
        "# Scorecard de empleabilidad",
        "## Seniority map",
        "## Criterio de empleabilidad",
    ],
}

missing_files = []
missing_headers = []

for filename, headers in REQUIRED.items():
    path = BASE / filename
    if not path.exists():
        missing_files.append(str(path))
        continue

    text = path.read_text(encoding="utf-8")
    for header in headers:
        if header not in text:
            missing_headers.append(f"{filename}: falta '{header}'")

if missing_files or missing_headers:
    if missing_files:
        print("[ERROR] Archivos faltantes:")
        for item in missing_files:
            print(f"  - {item}")
    if missing_headers:
        print("[ERROR] Encabezados faltantes:")
        for item in missing_headers:
            print(f"  - {item}")
    sys.exit(1)

print("[OK] Learning gates baseline validado")
