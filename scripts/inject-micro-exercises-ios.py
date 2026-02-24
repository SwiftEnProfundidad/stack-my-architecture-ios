#!/usr/bin/env python3
"""
Inyecta micro-ejercicios en todas las lecciones del curso iOS que no los tienen.

Uso:
    python3 scripts/inject-micro-exercises-ios.py

El script:
1. Busca todos los archivos .md en 01-fundamentos/ a 05-maestria/
2. Identifica lecciones sin ejercicios (sin marcador <!-- sma:exercise:v1 -->)
3. Genera ejercicios contextualizados según la etapa
4. Inserta antes de "## Continuación" o al final
"""

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

EXCLUDE_PATTERNS = [
    "entregables-",
    "ADR-",
    "README",
    "CHANGELOG",
    "TODO",
    "00-setup",  # Ya tiene ejercicios
]

MARKER = "<!-- sma:exercise:v1 -->"
MARKER_END = "<!-- /sma:exercise:v1 -->"

# Plantillas de ejercicios por etapa
EXERCISE_TEMPLATES = {
    "01-fundamentos": {
        "contexts": [
            "Acabas de aprender este concepto y quieres asegurarte de que lo entiendes antes de seguir.",
            "Estás revisando tu código y te das cuenta de que podrías aplicar esto de forma más limpia.",
            "Un compañero te pregunta cómo funciona esto y necesitas explicárselo con un ejemplo.",
        ],
        "tasks": [
            "Escribe un ejemplo mínimo que demuestre este concepto en 3-5 líneas de código.",
            "Dibuja (en papel o mentalmente) cómo se relacionan estas piezas antes de ver la solución.",
            "Explica con tus propias palabras qué hace este código y por qué es importante.",
            "Identifica el error en este código de ejemplo y propón la corrección.",
        ],
        "hints1": [
            "Piensa en el flujo de datos: ¿qué entra y qué sale?",
            "Revisa la sección 'Concepto principal' de esta lección.",
            "No necesitas escribir código complejo; un ejemplo mínimo es suficiente.",
        ],
        "hints2": [
            "La clave está en la separación de responsabilidades.",
            "Fíjate en cómo se declaran los tipos y sus relaciones.",
            "El error está relacionado con el alcance (scope) de las variables.",
        ],
    },
    "02-integracion": {
        "contexts": [
            "Tienes que conectar dos features y quieres hacerlo siguiendo las mejores prácticas.",
            "Estás refactorizando código legacy para hacerlo más testeable.",
            "Necesitas añadir una nueva dependencia sin romper la arquitectura existente.",
        ],
        "tasks": [
            "Diseña cómo se comunicarían estas dos features usando solo contratos.",
            "Escribe el código del Composition Root que cablearía estas dependencias.",
            "Identifica qué eventos de navegación necesitarías para este flujo.",
            "Propón una mejora al código actual manteniendo los límites de arquitectura.",
        ],
        "hints1": [
            "Recuerda: las features no deben conocerse directamente.",
            "El Composition Root es el único lugar que conoce todo.",
            "Piensa en eventos semánticos, no en destinos concretos.",
        ],
        "hints2": [
            "Necesitas un protocolo que defina el contrato entre ellas.",
            "Usa inyección de dependencias, no creación directa.",
            "El coordinator maneja la navegación, no las views.",
        ],
    },
    "03-evolucion": {
        "contexts": [
            "Tu app necesita funcionar offline y no sabes por dónde empezar.",
            "Hay un bug intermitente en producción relacionado con datos obsoletos.",
            "Necesitas añadir métricas para entender qué está pasando en la app.",
        ],
        "tasks": [
            "Diseña una política de cache para este escenario específico.",
            "Escribe pseudocódigo del flujo de invalidación de datos.",
            "Identifica qué métricas serían útiles para diagnosticar este problema.",
            "Propón un trade-off entre frescura de datos y performance.",
        ],
        "hints1": [
            "Considera qué pasa cuando falla la red.",
            "El TTL no es la única estrategia posible.",
            "Piensa en el usuario: ¿qué prefiere, datos viejos o error?",
        ],
        "hints2": [
            "Una estrategia network-first + fallback a cache es común.",
            "La invalidación debe ser explícita, no implícita.",
            "Las métricas deben responder preguntas específicas.",
        ],
    },
    "04-arquitecto": {
        "contexts": [
            "Tu equipo está creciendo y necesitas establecer límites claros.",
            "Hay dependencias circulares que están dificultando los cambios.",
            "Necesitas justificar una decisión arquitectónica a stakeholders.",
        ],
        "tasks": [
            "Dibuja el mapa de bounded contexts para este sistema.",
            "Propón una regla de dependencia que evite el acoplamiento actual.",
            "Escribe los pros/contras de dos alternativas arquitectónicas.",
            "Diseña un quality gate que valide esta decisión en CI.",
        ],
        "hints1": [
            "Los bounded contexts se definen por el lenguaje ubícuo.",
            "Las reglas de dependencia deben ser verificables.",
            "No hay arquitectura perfecta, solo trade-offs.",
        ],
        "hints2": [
            "Considera extraer un SharedKernel o usar ACL.",
            "Las dependencias deben apuntar hacia el dominio, no al revés.",
            "Un buen quality gate es automático y rápido.",
        ],
    },
    "05-maestria": {
        "contexts": [
            "Hay race conditions en producción que no puedes reproducir localmente.",
            "La app usa mucha memoria y sospechas de leaks.",
            "Necesitas migrar código existente a Swift 6 strict concurrency.",
        ],
        "tasks": [
            "Identifica el actor correcto para esta operación.",
            "Propón una refactorización que elimine el data race.",
            "Escribe un test que verifique la seguridad de concurrencia.",
            "Analiza esta traza de memoria y propón la solución.",
        ],
        "hints1": [
            "Revisa quién posee el estado mutable.",
            "Los actors serializan el acceso, pero no eliminan la complejidad.",
            "Instruments puede mostrarte los ciclos de retención.",
        ],
        "hints2": [
            "Considera si el estado realmente necesita ser mutable.",
            "@Sendable es tu amigo para closures.",
            "Los weak references rompen ciclos de retención.",
        ],
    },
}


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


def has_exercise_marker(content: str) -> bool:
    """Verifica si el archivo ya tiene ejercicios."""
    return MARKER in content


def get_etapa_from_path(filepath: Path) -> str:
    """Extrae la etapa del path (01-fundamentos, etc.)."""
    parts = filepath.parts
    for part in parts:
        if part.startswith(("01-", "02-", "03-", "04-", "05-")):
            return part
    return "01-fundamentos"


def generate_exercise(filepath: Path) -> str:
    """Genera un ejercicio contextualizado según la etapa."""
    etapa = get_etapa_from_path(filepath)
    templates = EXERCISE_TEMPLATES.get(etapa, EXERCISE_TEMPLATES["01-fundamentos"])
    
    # Seleccionar elementos aleatorios (consistentes por archivo)
    import hashlib
    file_hash = int(hashlib.md5(str(filepath).encode()).hexdigest(), 16)
    
    context = templates["contexts"][file_hash % len(templates["contexts"])]
    task = templates["tasks"][file_hash % len(templates["tasks"])]
    hint1 = templates["hints1"][file_hash % len(templates["hints1"])]
    hint2 = templates["hints2"][file_hash % len(templates["hints2"])]
    
    return f"""## Pausa y practica
{MARKER}

**Contexto:** {context}

**Tarea:** {task}

<details>
<summary>💡 Pista 1: Dónde mirar</summary>

{hint1}

</details>

<details>
<summary>💡 Pista 2: Qué cambiar</summary>

{hint2}

</details>

<details>
<summary>✅ Solución completa</summary>

[La solución específica dependerá de la lección. Consulta el código de ejemplo en la sección anterior o pide ayuda en la comunidad si estás atascado.]

**Por qué funciona:** Esta aproximación respeta los principios de Clean Architecture manteniendo las capas desacopladas y testeables.

</details>
{MARKER_END}
"""


def inject_exercise(filepath: Path) -> bool:
    """Inyecta un ejercicio en un archivo. Retorna True si se modificó."""
    content = filepath.read_text(encoding='utf-8')
    
    if has_exercise_marker(content):
        return False  # Ya tiene ejercicio
    
    # Buscar dónde insertar (antes de ## Continuación o al final)
    lines = content.split('\n')
    insert_idx = len(lines)
    
    for i, line in enumerate(lines):
        if line.strip().startswith("## Continuación"):
            insert_idx = i
            break
    
    # Generar ejercicio
    exercise = generate_exercise(filepath)
    
    # Insertar
    new_lines = lines[:insert_idx] + ['', exercise, ''] + lines[insert_idx:]
    new_content = '\n'.join(new_lines)
    
    filepath.write_text(new_content, encoding='utf-8')
    return True


def main():
    print("🔍 Buscando lecciones sin ejercicios...")
    lessons = get_all_lessons()
    print(f"📚 Encontradas {len(lessons)} lecciones")
    
    modified = 0
    skipped = 0
    errors = 0
    
    for lesson in lessons:
        try:
            rel_path = lesson.relative_to(COURSE_ROOT)
            if inject_exercise(lesson):
                print(f"  ✅ {rel_path}")
                modified += 1
            else:
                print(f"  ⏭️  {rel_path} (ya tiene ejercicio)")
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
