#!/usr/bin/env python3
"""
Inyecta bloques de metadata YAML en todas las lecciones del curso iOS.
Usa solo stdlib (sin PyYAML) para evitar dependencias externas.

Uso:
    python3 scripts/inject-meta-leccion-ios.py

El script:
1. Busca todos los archivos .md en 01-fundamentos/ a 05-maestria/
2. Calcula tiempo_lectura (~200 palabras/min)
3. Asigna dificultad según etapa (1-5)
4. Define prerequisitos por secuencia
5. Inserta metadata si no existe el marcador <!-- sma:meta:v1 -->
"""

import os
import re
from pathlib import Path

COURSE_ROOT = Path(__file__).parent.parent
LESSON_DIRS = [
    COURSE_ROOT / "01-fundamentos",
    COURSE_ROOT / "02-integracion", 
    COURSE_ROOT / "03-evolucion",
    COURSE_ROOT / "04-arquitecto",
    COURSE_ROOT / "05-maestria",
]

# Mapeo de directorio a dificultad base
DIFFICULTY_MAP = {
    "01-fundamentos": 1,
    "02-integracion": 2,
    "03-evolucion": 3,
    "04-arquitecto": 4,
    "05-maestria": 5,
}

# Archivos a excluir (entregables, ADRs, etc.)
EXCLUDE_PATTERNS = [
    "entregables-",
    "ADR-",
    "README",
    "CHANGELOG",
    "TODO",
]

MARKER = "<!-- sma:meta:v1 -->"
MARKER_END = "<!-- /sma:meta:v1 -->"


def should_process_file(filepath: Path) -> bool:
    """Determina si un archivo debe procesarse."""
    if not filepath.suffix == ".md":
        return False
    
    name = filepath.name
    for pattern in EXCLUDE_PATTERNS:
        if pattern in name:
            return False
    
    return True


def get_all_lessons() -> list[Path]:
    """Obtiene todos los archivos de lección ordenados."""
    lessons = []
    for dir_path in LESSON_DIRS:
        if not dir_path.exists():
            continue
        for md_file in sorted(dir_path.rglob("*.md")):
            if should_process_file(md_file):
                lessons.append(md_file)
    return lessons


def calculate_reading_time(content: str) -> str:
    """Calcula tiempo de lectura (~200 palabras/min)."""
    # Eliminar código y bloques técnicos para contar solo texto legible
    cleaned = re.sub(r'```[\s\S]*?```', '', content)  # Code blocks
    cleaned = re.sub(r'`[^`]+`', '', cleaned)  # Inline code
    cleaned = re.sub(r'\[.*?\]\(.*?\)', '', cleaned)  # Links
    
    words = len(cleaned.split())
    minutes = max(5, round(words / 200))  # Mínimo 5 min
    return f"{minutes} min"


def calculate_practice_time(difficulty: int) -> str:
    """Calcula tiempo de práctica según dificultad."""
    times = {
        1: "10 min",
        2: "15 min",
        3: "20 min",
        4: "25 min",
        5: "30 min",
    }
    return times.get(difficulty, "15 min")


def get_difficulty(filepath: Path) -> int:
    """Obtiene dificultad según directorio."""
    dir_name = filepath.parent.name
    return DIFFICULTY_MAP.get(dir_name, 2)


def find_prerequisite(lessons: list[Path], current: Path) -> str | None:
    """Encuentra la lección anterior como prerequisito."""
    try:
        idx = lessons.index(current)
        if idx > 0:
            prev = lessons[idx - 1]
            # Convertir a path relativo
            rel_path = prev.relative_to(COURSE_ROOT)
            return str(rel_path)
    except ValueError:
        pass
    return None


def generate_meta_block(filepath: Path, lessons: list[Path]) -> str:
    """Genera el bloque de metadata YAML."""
    content = filepath.read_text(encoding='utf-8')
    difficulty = get_difficulty(filepath)
    
    reading_time = calculate_reading_time(content)
    practice_time = calculate_practice_time(difficulty)
    prereq = find_prerequisite(lessons, filepath)
    
    # Determinar sección de recuperación según etapa
    etapa = filepath.parent.name.split('-')[0]  # "01", "02", etc.
    recovery_section = f"anexos/guia-recuperacion-ios.md#etapa-{etapa}"
    
    lines = [
        MARKER,
        "meta_leccion:",
        f'  tiempo_lectura: "{reading_time}"',
        f'  tiempo_practica: "{practice_time}"',
        f"  dificultad: {difficulty}",
    ]
    
    if prereq:
        lines.append("  prerequisitos:")
        lines.append(f'    - "{prereq}"')
    else:
        lines.append("  prerequisitos: []")
    
    lines.append(f'  si_te_atascas: "{recovery_section}"')
    lines.append(MARKER_END)
    
    return "\n".join(lines)


def has_meta_marker(content: str) -> bool:
    """Verifica si el archivo ya tiene metadata usando regex para evitar falsos positivos."""
    import re
    # Busca el marcador al inicio de línea (con posible whitespace)
    return bool(re.search(r'^\s*<!--\s*sma:meta:v1\s*-->', content, re.MULTILINE))


def inject_meta(filepath: Path, lessons: list[Path]) -> bool:
    """Inyecta metadata en un archivo. Retorna True si se modificó."""
    content = filepath.read_text(encoding='utf-8')
    
    if has_meta_marker(content):
        return False  # Ya tiene metadata
    
    # Encontrar la primera línea que no sea el título (# Título)
    lines = content.split('\n')
    insert_idx = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('# ') and i == 0:
            insert_idx = i + 1
            break
        elif stripped and not stripped.startswith('#'):
            insert_idx = i
            break
    
    # Generar bloque de metadata
    meta_block = generate_meta_block(filepath, lessons)
    
    # Insertar después del título
    new_lines = lines[:insert_idx] + ['', meta_block, ''] + lines[insert_idx:]
    new_content = '\n'.join(new_lines)
    
    filepath.write_text(new_content, encoding='utf-8')
    return True


def main():
    print("🔍 Buscando lecciones...")
    lessons = get_all_lessons()
    print(f"📚 Encontradas {len(lessons)} lecciones")
    
    modified = 0
    skipped = 0
    errors = 0
    
    for lesson in lessons:
        try:
            rel_path = lesson.relative_to(COURSE_ROOT)
            if inject_meta(lesson, lessons):
                print(f"  ✅ {rel_path}")
                modified += 1
            else:
                print(f"  ⏭️  {rel_path} (ya tiene metadata)")
                skipped += 1
        except Exception as e:
            print(f"  ❌ Error en {lesson}: {e}")
            errors += 1
    
    print()
    print("=" * 50)
    print(f"✅ Modificados: {modified}")
    print(f"⏭️  Saltados: {skipped}")
    print(f"❌ Errores: {errors}")
    print("=" * 50)


if __name__ == "__main__":
    main()
