#!/usr/bin/env python3
"""
Convierte todos los .md del curso a un unico HTML autocontenido.
No requiere dependencias externas (solo Python 3 estandar).
Mermaid.js y highlight.js se cargan desde CDN.
"""

import os
import re
import sys
import shutil
from pathlib import Path

COURSE_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = COURSE_ROOT / "dist"
OUTPUT_FILE = OUTPUT_DIR / "curso-stack-my-architecture.html"
ASSETS_SRC_DIR = COURSE_ROOT / "assets"
ASSETS_DIST_DIR = OUTPUT_DIR / "assets"

# Orden de los archivos (segun README)
FILE_ORDER = [
    "00-informe/INFORME-CURSO.md",
    "01-fundamentos/00-introduccion.md",
    "01-fundamentos/01-principios-ingenieria.md",
    "01-fundamentos/02-metodologia-bdd-tdd.md",
    "01-fundamentos/03-stack-tecnologico.md",
    "01-fundamentos/04-estructura-feature-first.md",
    "01-fundamentos/05-feature-login/00-especificacion-bdd.md",
    "01-fundamentos/05-feature-login/01-domain.md",
    "01-fundamentos/05-feature-login/02-application.md",
    "01-fundamentos/05-feature-login/03-infrastructure.md",
    "01-fundamentos/05-feature-login/04-interface-swiftui.md",
    "01-fundamentos/05-feature-login/05-tdd-ciclo-completo.md",
    "01-fundamentos/05-feature-login/ADR-001-login.md",
    "01-fundamentos/06-conectando-la-app.md",
    "01-fundamentos/entregables-etapa-1.md",
    "02-integracion/00-introduccion.md",
    "02-integracion/01-feature-catalog/00-especificacion-bdd.md",
    "02-integracion/01-feature-catalog/01-domain.md",
    "02-integracion/01-feature-catalog/02-application.md",
    "02-integracion/01-feature-catalog/03-infrastructure.md",
    "02-integracion/01-feature-catalog/04-interface-swiftui.md",
    "02-integracion/01-feature-catalog/ADR-002-catalog.md",
    "02-integracion/02-navegacion-eventos.md",
    "02-integracion/03-contratos-features.md",
    "02-integracion/04-infra-real-network.md",
    "02-integracion/05-integration-tests.md",
    "02-integracion/06-composition-root.md",
    "02-integracion/07-swiftui-enterprise.md",
    "02-integracion/08-swift-concurrency-enterprise.md",
    "02-integracion/09-app-final-etapa-2.md",
    "02-integracion/entregables-etapa-2.md",
    "03-evolucion/00-introduccion.md",
    "03-evolucion/01-caching-offline.md",
    "03-evolucion/02-consistencia.md",
    "03-evolucion/03-observabilidad.md",
    "03-evolucion/04-tests-avanzados.md",
    "03-evolucion/05-trade-offs.md",
    "03-evolucion/06-swiftdata-store.md",
    "03-evolucion/07-backend-firebase.md",
    "03-evolucion/entregables-etapa-3.md",
    "04-arquitecto/00-introduccion.md",
    "04-arquitecto/01-bounded-contexts.md",
    "04-arquitecto/02-reglas-dependencia-ci.md",
    "04-arquitecto/03-navegacion-deeplinks.md",
    "04-arquitecto/04-versionado-spm.md",
    "04-arquitecto/05-guia-arquitectura.md",
    "04-arquitecto/06-quality-gates.md",
    "04-arquitecto/entregables-etapa-4.md",
    "05-maestria/00-introduccion.md",
    "05-maestria/01-isolation-domains.md",
    "05-maestria/02-actors-en-arquitectura.md",
    "05-maestria/03-structured-concurrency.md",
    "05-maestria/04-testing-concurrente.md",
    "05-maestria/05-swiftui-state-moderno.md",
    "05-maestria/06-swiftui-performance.md",
    "05-maestria/07-composicion-avanzada.md",
    "05-maestria/08-memory-leaks-y-diagnostico.md",
    "05-maestria/09-migracion-swift6.md",
    "05-maestria/10-debugging-xcode.md",
    "05-maestria/11-entrevista-arquitecto.md",
    "05-maestria/12-arquitectura-adaptativa.md",
    "05-maestria/entregables-etapa-5.md",
    "anexos/diagramas/atlas-arquitectura.md",
    "anexos/guia-nueva-feature.md",
    "anexos/git-workflow-curso.md",
    "anexos/xcode-cheat-sheet.md",
    "anexos/como-leer-documentacion.md",
    "anexos/simulator-tips.md",
    "anexos/mental-models.md",
    "anexos/errores-compilacion.md",
    "anexos/guia-solid.md",
    "anexos/guia-cqs-cqrs.md",
    "anexos/preguntas-entrevista.md",
    "anexos/hallazgos-y-correcciones.md",
    "anexos/adrs/INDICE-ADRS.md",
    "anexos/apendice-banca-ledger.md",
    "anexos/glosario.md",
    "anexos/proyecto-final.md",
]


def md_to_html(md_text, file_id):
    """Convierte markdown a HTML basico con soporte para Mermaid."""
    html = ""
    lines = md_text.split("\n")
    i = 0
    in_code = False
    in_list = False
    in_table = False
    code_lang = ""
    code_buffer = []
    table_buffer = []

    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith("```") and not in_code:
            if in_list:
                html += "</ul>\n"
                in_list = False
            code_lang = line.strip()[3:].strip()
            in_code = True
            code_buffer = []
            i += 1
            continue

        if line.strip().startswith("```") and in_code:
            raw_code_content = "\n".join(code_buffer)
            if code_lang.lower() == "mermaid":
                # Mermaid must be kept raw, otherwise entities like --> and <br/>
                # are escaped and diagrams fail to parse/render.
                html += f'<pre class="mermaid">{raw_code_content}</pre>\n'
            else:
                code_content = (
                    raw_code_content.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                if code_lang:
                    html += f'<pre><code class="language-{code_lang}">{code_content}</code></pre>\n'
                else:
                    html += f"<pre><code>{code_content}</code></pre>\n"
            in_code = False
            code_lang = ""
            i += 1
            continue

        if in_code:
            code_buffer.append(line)
            i += 1
            continue

        # Tables
        if "|" in line and line.strip().startswith("|"):
            if not in_table:
                if in_list:
                    html += "</ul>\n"
                    in_list = False
                in_table = True
                table_buffer = []
            table_buffer.append(line)
            i += 1
            continue
        elif in_table:
            html += render_table(table_buffer)
            in_table = False
            table_buffer = []
            # Don't increment, process current line

        # Headers
        header_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if header_match:
            if in_list:
                html += "</ul>\n"
                in_list = False
            level = len(header_match.group(1))
            text = inline_format(header_match.group(2))
            anchor = re.sub(r"[^a-z0-9]+", "-", text.lower().strip())
            anchor = f"{file_id}-{anchor}"
            html += f'<h{level} id="{anchor}">{text}</h{level}>\n'
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^---+\s*$", line):
            if in_list:
                html += "</ul>\n"
                in_list = False
            html += "<hr>\n"
            i += 1
            continue

        # List items
        if re.match(r"^\s*[-*]\s+", line):
            if not in_list:
                html += "<ul>\n"
                in_list = True
            content = re.sub(r"^\s*[-*]\s+", "", line)
            # Handle checkbox
            content = content.replace("[ ]", "&#9744;").replace("[x]", "&#9745;")
            html += f"  <li>{inline_format(content)}</li>\n"
            i += 1
            continue

        # Numbered list
        if re.match(r"^\s*\d+[.)]\s+", line):
            if not in_list:
                html += "<ol>\n"
                in_list = True
            content = re.sub(r"^\s*\d+[.)]\s+", "", line)
            html += f"  <li>{inline_format(content)}</li>\n"
            i += 1
            continue

        # Close list if we hit non-list content
        if in_list and line.strip():
            if html.rstrip().endswith("</ol>") or "<ol>" in html[-200:]:
                html += "</ol>\n"
            else:
                html += "</ul>\n"
            in_list = False

        # Empty lines
        if not line.strip():
            i += 1
            continue

        # Paragraphs
        html += f"<p>{inline_format(line)}</p>\n"
        i += 1

    if in_list:
        html += "</ul>\n"
    if in_table:
        html += render_table(table_buffer)

    return html


def render_table(rows):
    """Renderiza una tabla markdown a HTML."""
    if len(rows) < 2:
        return ""
    html = '<table>\n<thead>\n<tr>\n'
    headers = [c.strip() for c in rows[0].strip().strip("|").split("|")]
    for h in headers:
        html += f"  <th>{inline_format(h)}</th>\n"
    html += "</tr>\n</thead>\n<tbody>\n"

    for row in rows[2:]:  # Skip header separator
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        html += "<tr>\n"
        for c in cells:
            html += f"  <td>{inline_format(c)}</td>\n"
        html += "</tr>\n"

    html += "</tbody>\n</table>\n"
    return html


def inline_format(text):
    """Aplica formato inline: bold, italic, code, links."""
    # Inline code (before other formatting to avoid conflicts)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # Bold + italic
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Links
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    # Images
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img alt="\1" src="\2">', text)
    return text


def build_nav(files_content):
    """Construye la barra de navegacion con anchors."""
    nav = '<nav id="sidebar">\n<h2>Indice</h2>\n<ul>\n'

    sections = {
        "00-informe": "Informe fundacional",
        "01-fundamentos": "Etapa 1: Junior",
        "02-integracion": "Etapa 2: Mid",
        "03-evolucion": "Etapa 3: Senior",
        "04-arquitecto": "Etapa 4: Arquitecto",
        "05-maestria": "Etapa 5: Maestria",
        "anexos": "Anexos",
    }

    current_section = ""
    for filepath, content in files_content:
        section_key = filepath.split("/")[0]
        section_name = sections.get(section_key, section_key)

        if section_name != current_section:
            if current_section:
                nav += "</ul></li>\n"
            current_section = section_name
            nav += f'<li class="nav-section"><strong>{section_name}</strong>\n<ul>\n'

        # Extract first h1 or filename
        h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = h1_match.group(1) if h1_match else Path(filepath).stem
        file_id = filepath.replace("/", "-").replace(".md", "")
        nav += f'  <li><a class="doc-nav-link" data-lesson-path="{filepath}" href="#{file_id}">{title}</a></li>\n'

    nav += "</ul></li>\n</ul>\n</nav>\n"
    return nav


def build_html():
    """Construye el HTML completo."""
    files_content = []
    for rel_path in FILE_ORDER:
        full_path = COURSE_ROOT / rel_path
        if full_path.exists():
            content = full_path.read_text(encoding="utf-8")
            files_content.append((rel_path, content))
        else:
            print(f"  [SKIP] {rel_path} (no encontrado)")

    print(f"  Procesando {len(files_content)} archivos...")

    nav = build_nav(files_content)

    body_html = ""
    for filepath, content in files_content:
        file_id = filepath.replace("/", "-").replace(".md", "")
        body_html += f'<section id="{file_id}" class="lesson" data-topic-id="{file_id}" data-lesson-path="{filepath}">\n'
        body_html += f'<div class="lesson-path">{filepath}</div>\n'
        body_html += md_to_html(content, file_id)
        body_html += "</section>\n"

    html_template = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="course-id" content="stack-my-architecture-ios">
<title>Stack: My Architecture iOS</title>
<link rel="stylesheet" href="assets/study-ux.css">
<link rel="stylesheet" href="assets/course-switcher.css">
<link rel="stylesheet" href="assets/assistant-panel.css">
<script defer src="assets/study-ux.js"></script>
<script defer src="assets/course-switcher.js"></script>
<script defer src="assets/theme-controls.js"></script>
<script defer src="assets/assistant-panel.js"></script>
<script defer src="assets/assistant-bridge.js"></script>

<!-- Google Fonts - Inter -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;450;500;600;700&display=swap" rel="stylesheet">

<!-- Mermaid.js para diagramas -->
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>

<!-- Highlight.js para syntax highlighting -->
<link id="hljs-theme" rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/monokai.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/swift.min.js"></script>

<style>
/* ============================================
   SISTEMA DE DISEÑO: Stack My Architecture iOS
   ============================================ */

:root {{
    /* ============================================
       VISUAL STYLES: enterprise, bold, paper
       ============================================ */
    --visual-style: 'enterprise';
}}

/* ============================================
   STYLE: ENTERPRISE (Default)
   Profesional, limpio, corporativo
   ============================================ */
[data-style="enterprise"] {{
    /* Paleta de colores */
    --bg: #ffffff;
    --bg-elevated: #fafbfc;
    --bg-surface: #f6f8fa;
    
    --text: #1a1a2e;
    --text-secondary: #4a4a5a;
    --text-muted: #6a6a7a;
    
    --accent: #2563eb;
    --accent-light: #3b82f6;
    --accent-dark: #1d4ed8;
    --accent-soft: rgba(37, 99, 235, 0.1);
    
    --success: #10b981;
    --success-soft: rgba(16, 185, 129, 0.1);
    --warning: #f59e0b;
    --warning-soft: rgba(245, 158, 11, 0.1);
    --danger: #ef4444;
    --danger-soft: rgba(239, 68, 68, 0.1);
    --info: #06b6d4;
    --info-soft: rgba(6, 182, 212, 0.1);
    
    --sidebar-bg: #f8fafc;
    --code-bg: #f1f5f9;
    --border: #e2e8f0;
    --border-light: #f1f5f9;
    
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
    --shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1);
    
    --font-weight-body: 500;
    --font-weight-heading: 700;
    --heading-letter-spacing: -0.02em;
    --border-radius: 8px;
}}

/* ============================================
   STYLE: ENTERPRISE - Dark Mode overrides
   Profesional, azul corporativo
   ============================================ */
[data-theme="dark"][data-style="enterprise"] {{
    --bg: #0c1821;
    --bg-elevated: #152a3d;
    --bg-surface: #1e3a5f;
    
    --text: #e8f4ff;
    --text-secondary: #a8c5e0;
    --text-muted: #6b8fb0;
    
    --accent: #60a5fa;
    --accent-light: #93c5fd;
    --accent-dark: #3b82f6;
    --accent-soft: rgba(96, 165, 250, 0.15);
    
    --sidebar-bg: #0f2335;
    --code-bg: #152a3d;
    --border: #2a4a6d;
    --border-light: #1e3a5f;
}}

/* ============================================
   STYLE: BOLD
   Alto contraste, impactante, moderno
   ============================================ */
[data-style="bold"] {{
    --bg: #0a0a0f;
    --bg-elevated: #141419;
    --bg-surface: #1e1e24;
    
    --text: #ffffff;
    --text-secondary: #d0d0e0;
    --text-muted: #a0a0b0;
    
    --accent: #ff6b35;
    --accent-light: #ff8c5a;
    --accent-dark: #e55a2b;
    --accent-soft: rgba(255, 107, 53, 0.15);
    
    --success: #00d9a3;
    --success-soft: rgba(0, 217, 163, 0.15);
    --warning: #ffc107;
    --warning-soft: rgba(255, 193, 7, 0.15);
    --danger: #ff4757;
    --danger-soft: rgba(255, 71, 87, 0.15);
    --info: #00d4ff;
    --info-soft: rgba(0, 212, 255, 0.15);
    
    --sidebar-bg: #0f0f14;
    --code-bg: #1a1a22;
    --border: #3a3a45;
    --border-light: #2a2a35;
    
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
    --shadow: 0 4px 6px -1px rgba(0,0,0,0.4);
    --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.5);
    
    --font-weight-body: 500;
    --font-weight-heading: 800;
    --heading-letter-spacing: -0.03em;
    --border-radius: 12px;
}}

/* ============================================
   STYLE: PAPER
   Cálido, orgánico, académico
   ============================================ */
[data-style="paper"] {{
    --bg: #fdfbf7;
    --bg-elevated: #f5f1e8;
    --bg-surface: #f0ebe0;
    
    --text: #2c241b;
    --text-secondary: #5a5045;
    --text-muted: #8a8075;
    
    --accent: #8b4513;
    --accent-light: #a0522d;
    --accent-dark: #654321;
    --accent-soft: rgba(139, 69, 19, 0.08);
    
    --success: #2e7d32;
    --success-soft: rgba(46, 125, 50, 0.1);
    --warning: #ed6c02;
    --warning-soft: rgba(237, 108, 2, 0.1);
    --danger: #c62828;
    --danger-soft: rgba(198, 40, 40, 0.1);
    --info: #1565c0;
    --info-soft: rgba(21, 101, 192, 0.1);
    
    --sidebar-bg: #f7f3ec;
    --code-bg: #f5f0e6;
    --border: #e0d5c5;
    --border-light: #ebe5d8;
    
    --shadow-sm: 0 1px 3px rgba(44, 36, 27, 0.08);
    --shadow: 0 4px 8px rgba(44, 36, 27, 0.12);
    --shadow-lg: 0 8px 16px rgba(44, 36, 27, 0.15);
    
    --font-weight-body: 400;
    --font-weight-heading: 600;
    --heading-letter-spacing: -0.01em;
    --border-radius: 4px;
}}

/* ============================================
   STYLE: PAPER - Dark Mode overrides
   Marrón cálido, estilo parchment
   ============================================ */
[data-theme="dark"][data-style="paper"] {{
    --bg: #2d2419;
    --bg-elevated: #3d3124;
    --bg-surface: #4a3d2e;
    
    --text: #f5e6d3;
    --text-secondary: #d4c4b0;
    --text-muted: #a89080;
    
    --accent: #c4956a;
    --accent-light: #d4a87a;
    --accent-dark: #a87b5a;
    --accent-soft: rgba(196, 149, 106, 0.15);
    
    --sidebar-bg: #3d3124;
    --code-bg: #4a3d2e;
    --border: #5a4d3e;
    --border-light: #4a3d2e;
}}

/* ============================================
   COMMON VARIABLES (No cambian entre estilos)
   ============================================ */
:root {{
    --sidebar-width: 300px;
    
    /* Tipografía */
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --font-mono: 'SF Mono', 'Fira Code', 'JetBrains Mono', Menlo, Consolas, monospace;
    
    /* Espaciado */
    --space-xs: 0.25rem;
    --space-sm: 0.5rem;
    --space-md: 1rem;
    --space-lg: 1.5rem;
    --space-xl: 2rem;
    --space-2xl: 3rem;
    --space-3xl: 4rem;
    
    /* Radios */
    --radius-sm: calc(var(--border-radius) / 2);
    --radius-md: var(--border-radius);
    --radius-lg: calc(var(--border-radius) * 1.5);
    --radius-xl: calc(var(--border-radius) * 2);
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

html {{ scroll-behavior: smooth; }}

body {{
    font-family: var(--font-sans);
    color: var(--text);
    background: var(--bg);
    line-height: 1.75;
    font-size: 16px;
    font-weight: var(--font-weight-body);
    display: flex;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

/* ============================================
   SIDEBAR NAVEGACIÓN
   ============================================ */
#sidebar {{
    position: fixed;
    top: 0;
    left: 0;
    width: var(--sidebar-width);
    height: 100vh;
    overflow-y: auto;
    background: var(--sidebar-bg);
    border-right: 1px solid var(--border);
    padding: var(--space-lg) var(--space-md);
    font-size: 0.875rem;
    z-index: 100;
    scrollbar-width: thin;
}}

#sidebar::-webkit-scrollbar {{
    width: 6px;
}}

#sidebar::-webkit-scrollbar-thumb {{
    background: var(--border);
    border-radius: 3px;
}}

#sidebar h2 {{
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: var(--space-md);
    color: var(--accent);
    letter-spacing: -0.02em;
    text-transform: uppercase;
    font-size: 0.75rem;
}}

#sidebar ul {{ list-style: none; padding-left: 0; }}

#sidebar li {{ margin-bottom: 2px; }}

#sidebar li.nav-section {{
    margin-top: var(--space-lg);
}}

#sidebar li.nav-section:first-child {{
    margin-top: 0;
}}

#sidebar li.nav-section > strong {{
    color: var(--text);
    font-size: 0.8rem;
    font-weight: 600;
    display: block;
    padding: var(--space-xs) var(--space-sm);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
}}

#sidebar a {{
    color: var(--text-secondary);
    text-decoration: none;
    display: block;
    padding: 6px 10px;
    border-radius: var(--radius-sm);
    transition: all 0.2s ease;
    font-weight: 450;
    border-left: 2px solid transparent;
}}

#sidebar a:hover {{
    background: var(--accent-soft);
    color: var(--accent);
    border-left-color: var(--accent);
}}

/* ============================================
   CONTENIDO PRINCIPAL
   ============================================ */
#content {{
    margin-left: var(--sidebar-width);
    max-width: none;
    padding: var(--space-3xl) var(--space-2xl);
    width: calc(100% - var(--sidebar-width));
    min-height: 100vh;
}}

/* ============================================
   TIPOGRAFÍA - JERARQUÍA VISUAL
   ============================================ */
h1, h2, h3, h4 {{
    font-weight: var(--font-weight-heading);
    line-height: 1.3;
    letter-spacing: var(--heading-letter-spacing);
    color: var(--text);
}}

h1 {{
    font-size: 2.5rem;
    margin: 0 0 var(--space-lg);
    padding-bottom: var(--space-md);
    border-bottom: 3px solid var(--accent);
    color: var(--text);
    position: relative;
}}

h1::after {{
    content: '';
    position: absolute;
    bottom: -3px;
    left: 0;
    width: 120px;
    height: 3px;
    background: linear-gradient(90deg, var(--accent) 0%, var(--accent-light) 100%);
}}

h2 {{
    font-size: 1.75rem;
    margin: var(--space-2xl) 0 var(--space-md);
    color: var(--text);
    display: flex;
    align-items: center;
    gap: var(--space-sm);
}}

h2::before {{
    content: '';
    width: 4px;
    height: 28px;
    background: var(--accent);
    border-radius: 2px;
}}

h3 {{
    font-size: 1.375rem;
    margin: var(--space-xl) 0 var(--space-sm);
    color: var(--text);
    font-weight: 600;
}}

h4 {{
    font-size: 1.125rem;
    margin: var(--space-lg) 0 var(--space-sm);
    color: var(--text-secondary);
    font-weight: 600;
}}

p {{
    margin: var(--space-md) 0;
    color: var(--text-secondary);
    line-height: 1.8;
    font-weight: var(--font-weight-body);
}}

/* ============================================
   SEPARADORES Y SECCIONES
   ============================================ */
hr {{
    border: none;
    border-top: 1px solid var(--border);
    margin: var(--space-2xl) 0;
}}

hr.lesson-separator {{
    border: none;
    height: 4px;
    background: linear-gradient(90deg, var(--accent) 0%, var(--info) 50%, var(--success) 100%);
    margin: var(--space-3xl) 0;
    border-radius: 2px;
}}

/* ============================================
   BLOQUES DE CÓDIGO
   ============================================ */
pre {{
    background: var(--code-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: var(--space-lg);
    overflow-x: auto;
    margin: var(--space-lg) 0;
    font-size: 0.875rem;
    line-height: 1.6;
    box-shadow: var(--shadow-sm);
}}

pre.sma-code-enhanced {{
    position: relative;
    padding-top: calc(var(--space-lg) + 1.2rem);
}}

.sma-code-tools {{
    position: absolute;
    top: 8px;
    right: 10px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    z-index: 2;
}}

.sma-code-lang {{
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--text-muted);
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 2px 8px;
}}

.sma-code-copy-btn {{
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text);
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 3px 10px;
    cursor: pointer;
}}

.sma-code-copy-btn:hover {{
    border-color: var(--accent);
    color: var(--accent);
}}

code {{
    font-family: var(--font-mono);
    font-size: 0.9em;
}}

p code, li code, td code {{
    background: var(--code-bg);
    padding: 3px 8px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-light);
    color: var(--danger);
    font-weight: 500;
    font-size: 0.85em;
}}

/* Mermaid diagrams */
pre.mermaid {{
    background: white;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    text-align: center;
    padding: var(--space-xl);
    box-shadow: var(--shadow);
}}

/* ============================================
   TABLAS MODERNAS
   ============================================ */
table {{
    border-collapse: separate;
    border-spacing: 0;
    width: 100%;
    margin: var(--space-lg) 0;
    font-size: 0.9rem;
    border-radius: var(--radius-md);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}}

th, td {{
    border-bottom: 1px solid var(--border);
    padding: 12px 16px;
    text-align: left;
}}

th {{
    background: linear-gradient(180deg, var(--bg-surface) 0%, var(--sidebar-bg) 100%);
    font-weight: 600;
    color: var(--text);
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
    border-bottom: 2px solid var(--accent);
}}

tr:hover {{
    background: var(--bg-surface);
}}

tr:last-child td {{
    border-bottom: none;
}}

/* ============================================
   LISTAS
   ============================================ */
ul, ol {{
    margin: var(--space-md) 0;
    padding-left: var(--space-xl);
}}

li {{
    margin: var(--space-sm) 0;
    color: var(--text-secondary);
}}

li strong {{
    color: var(--text);
    font-weight: 600;
}}

/* Checkboxes en listas */
li:has(> input[type="checkbox"]) {{
    list-style: none;
    margin-left: -1.5em;
}}

/* ============================================
   LINKS
   ============================================ */
a {{
    color: var(--accent);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.15s ease;
}}

a:hover {{
    color: var(--accent-dark);
    text-decoration: underline;
    text-underline-offset: 2px;
}}

/* ============================================
   BADGE DE RUTA DE LECCIÓN
   ============================================ */
.lesson-path {{
    font-size: 0.75rem;
    color: var(--text-muted);
    background: var(--bg-surface);
    padding: 6px 14px;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-bottom: var(--space-md);
    font-family: var(--font-mono);
    border: 1px solid var(--border-light);
    font-weight: 500;
}}

.lesson-path::before {{
    content: '📁';
    font-size: 0.9em;
}}

/* ============================================
   CALLOUTS / BLOQUES DESTACADOS
   ============================================ */
/* Notas con > blockquote */
blockquote {{
    margin: var(--space-lg) 0;
    padding: var(--space-md) var(--space-lg);
    border-left: 4px solid var(--accent);
    background: var(--accent-soft);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    font-style: italic;
    color: var(--text-secondary);
}}

blockquote p {{
    margin: 0;
}}

/* ============================================
   Responsive - MOBILE FIRST
   ============================================ */
@media (max-width: 1024px) {{
    :root {{ --sidebar-width: 260px; }}
    #content {{ padding: 32px 28px; }}
}}

@media (max-width: 768px) {{
    :root {{ --sidebar-width: 0; }}
    #sidebar {{ display: none; }}
    #content {{ 
        margin-left: 0; 
        padding: 20px 16px;
        width: 100%;
    }}
    h1 {{ font-size: 1.6rem; margin: 32px 0 12px; }}
    h2 {{ font-size: 1.3rem; margin: 28px 0 10px; }}
    h3 {{ font-size: 1.1rem; margin: 20px 0 8px; }}
    h4 {{ font-size: 1rem; margin: 16px 0 6px; }}
    pre {{ padding: 12px; font-size: 0.82rem; }}
    th, td {{ padding: 8px 10px; font-size: 0.85rem; }}
}}

@media (max-width: 480px) {{
    #content {{ padding: 16px 12px; }}
    h1 {{ font-size: 1.4rem; }}
    h2 {{ font-size: 1.2rem; }}
    pre {{ padding: 10px; font-size: 0.78rem; overflow-x: scroll; }}
}}

/* Dark theme */
[data-theme="dark"] {{
    --bg: #0d1117;
    --text: #c9d1d9;
    --sidebar-bg: #161b22;
    --accent: #58a6ff;
    --code-bg: #161b22;
    --border: #30363d;
}}

[data-theme="dark"] h1 {{ color: #f0f6fc; }}
[data-theme="dark"] h2 {{ color: #c9d1d9; }}
[data-theme="dark"] h3 {{ color: #c9d1d9; }}
[data-theme="dark"] th {{ background: #21262d; }}
[data-theme="dark"] tr:nth-child(even) {{ background: #161b22; }}
[data-theme="dark"] li strong {{ color: #f0f6fc; }}
[data-theme="dark"] #sidebar a {{ color: #8b949e; }}
[data-theme="dark"] #sidebar a:hover {{ background: #21262d; color: var(--accent); }}
[data-theme="dark"] #sidebar li.nav-section > strong {{ color: #f0f6fc; }}
[data-theme="dark"] pre.mermaid {{ background: #161b22; }}
[data-theme="dark"] .lesson-path {{ color: #8b949e; }}

/* Back to top */
#back-to-top {{
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: var(--accent);
    color: white;
    border: none;
    border-radius: 50%;
    width: 44px;
    height: 44px;
    font-size: 1.2rem;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    display: none;
    z-index: 200;
}}

/* Theme controls container */
#theme-controls {{
    position: fixed;
    top: 16px;
    right: 16px;
    z-index: 9999;
    display: flex;
    gap: 12px;
    align-items: center;
}}

#theme-controls button {{
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    transition: all 0.2s ease;
    white-space: nowrap;
    border: 2px solid transparent;
}}

#theme-controls button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}}

/* Style cycle button - dynamic colors set by JS */
#style-cycle-btn {{
    background: #2563eb;
    color: white;
    border-color: #3b82f6;
}}

/* Code theme button */
#code-theme-cycle-btn {{
    background: var(--bg-elevated);
    color: var(--text);
    border-color: var(--border);
}}

/* Theme toggle button */
#theme-toggle {{
    background: var(--accent);
    color: white;
    border-color: var(--accent-light);
}}

/* Mobile responsive */
@media (max-width: 768px) {{
    #theme-controls {{
        top: 12px;
        right: 12px;
        gap: 8px;
    }}
    
    #theme-controls button {{
        padding: 8px 12px;
        font-size: 0.75rem;
    }}
}}

@media (max-width: 600px) {{
    #theme-controls {{
        flex-direction: column;
        align-items: flex-end;
        gap: 6px;
    }}
    
    #theme-controls button {{
        width: 120px;
        padding: 6px 10px;
        font-size: 0.7rem;
    }}
}}

/* Style selector dropdowns - ensure they inherit theme colors */
#style-selector select {{
    background-color: var(--bg-elevated) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
}}

#style-selector select option {{
    background-color: var(--bg-elevated);
    color: var(--text);
}}
#menu-toggle {{
    display: none;
    position: fixed;
    top: 12px;
    left: 12px;
    background: var(--sidebar-bg);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 1.1rem;
    cursor: pointer;
    z-index: 250;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}

@media (max-width: 768px) {{
    #menu-toggle {{ display: block; }}
}}
</style>
</head>
<body>

<button id="menu-toggle" onclick="toggleSidebar()" title="Abrir menú">&#9776;</button>

<div id="study-ux-controls" class="study-ux-controls" aria-label="Controles de estudio">
    <button id="study-completion-toggle" type="button">✅ Marcar completado</button>
    <button id="study-zen-toggle" type="button">🧘 Enfoque</button>
    <span id="study-progress" class="study-progress">Progreso: 0/0 (0%)</span>
</div>

<div id="course-switcher" class="course-switcher" aria-label="Selector de cursos">
    <div id="course-switcher-menu" class="course-switcher-menu">
        <a id="course-switcher-home" href="#">Cursos</a>
        <a id="course-switcher-ios" href="#">Curso iOS</a>
        <a id="course-switcher-android" href="#">Curso Android</a>
    </div>
</div>

<div id="theme-controls">
    <button id="style-cycle-btn" onclick="cycleStyle()">Estilo: Enterprise</button>
    <button id="code-theme-cycle-btn" onclick="cycleCodeTheme()">Codigo: Monokai</button>
    <button id="theme-toggle" onclick="toggleTheme()" title="Cambiar tema claro/oscuro">Tema: Claro</button>
</div>

{nav}

<main id="content">
<section id="study-ux-index-actions" class="study-ux-index-actions" aria-label="Study UX index actions"></section>
{body_html}
</main>

<button id="back-to-top" onclick="window.scrollTo({{top:0, behavior:'smooth'}})">&#8593;</button>

<script>
// Theme management
function getPreferredTheme() {{
    const saved = localStorage.getItem('course-theme');
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}}

function getPreferredStyle() {{
    return localStorage.getItem('course-style') || 'enterprise';
}}

function getPreferredCodeTheme() {{
    return localStorage.getItem('course-code-theme') || 'monokai';
}}

function applyStyle(style) {{
    document.documentElement.setAttribute('data-style', style);
    localStorage.setItem('course-style', style);
    
    const btn = document.getElementById('style-cycle-btn');
    if (btn) {{
        btn.textContent = 'Estilo: ' + style.charAt(0).toUpperCase() + style.slice(1);
        
        // Set button colors based on style
        const styleColors = {{
            'enterprise': {{ bg: '#2563eb', border: '#3b82f6', text: '#ffffff' }},
            'bold': {{ bg: '#ff6b35', border: '#ff8c5a', text: '#ffffff' }},
            'paper': {{ bg: '#c4956a', border: '#d4a87a', text: '#2d2419' }}
        }};
        
        const colors = styleColors[style] || styleColors['enterprise'];
        btn.style.backgroundColor = colors.bg;
        btn.style.borderColor = colors.border;
        btn.style.color = colors.text;
    }}
}}

function cycleStyle() {{
    const styles = ['enterprise', 'bold', 'paper'];
    const current = document.documentElement.getAttribute('data-style') || 'enterprise';
    const currentIndex = styles.indexOf(current);
    const nextIndex = (currentIndex + 1) % styles.length;
    const nextStyle = styles[nextIndex];
    applyStyle(nextStyle);
    renderMermaid();
}}

function applyCodeTheme(theme) {{
    localStorage.setItem('course-code-theme', theme);
    const btn = document.getElementById('code-theme-cycle-btn');
    if (btn) {{
        btn.textContent = 'Codigo: ' + theme.charAt(0).toUpperCase() + theme.slice(1).replace(/-/g, ' ');
    }}
    
    const hljsLink = document.getElementById('hljs-theme');
    const themeMap = {{
        'monokai': 'monokai.min.css',
        'github': 'github.min.css',
        'github-dark': 'github-dark.min.css',
        'atom-one-dark': 'atom-one-dark.min.css'
    }};
    hljsLink.href = `https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/${{themeMap[theme] || 'monokai.min.css'}}`;
    
    // Re-highlight all code blocks
    document.querySelectorAll('pre code').forEach(block => {{
        hljs.highlightElement(block);
    }});
    enhanceCodeBlocks();
}}

function detectSnippetLang(codeEl) {{
    const className = (codeEl.className || '').toLowerCase();
    if (className.includes('language-swift')) return 'Swift';
    if (className.includes('language-kotlin') || className.includes('language-kt')) return 'KT';
    if (className.includes('language-js') || className.includes('language-javascript')) return 'JS';
    if (className.includes('language-ts') || className.includes('language-typescript')) return 'TS';
    if (className.includes('language-json')) return 'JSON';
    if (className.includes('language-bash') || className.includes('language-shell')) return 'SH';
    if (className.includes('language-yaml') || className.includes('language-yml')) return 'YAML';
    return 'Swift';
}}

function copyCodeToClipboard(text) {{
    if (navigator.clipboard && navigator.clipboard.writeText) {{
        return navigator.clipboard.writeText(text);
    }}
    return new Promise((resolve, reject) => {{
        try {{
            const ta = document.createElement('textarea');
            ta.value = text;
            ta.setAttribute('readonly', 'readonly');
            ta.style.position = 'fixed';
            ta.style.left = '-9999px';
            document.body.appendChild(ta);
            ta.select();
            const ok = document.execCommand('copy');
            document.body.removeChild(ta);
            if (ok) resolve();
            else reject(new Error('copy-failed'));
        }} catch (err) {{
            reject(err);
        }}
    }});
}}

function enhanceCodeBlocks() {{
    document.querySelectorAll('pre code').forEach(code => {{
        const pre = code.closest('pre');
        if (!pre || pre.classList.contains('mermaid')) return;
        if (pre.dataset.codeEnhanced === '1') return;
        pre.dataset.codeEnhanced = '1';
        pre.classList.add('sma-code-enhanced');

        const tools = document.createElement('div');
        tools.className = 'sma-code-tools';

        const lang = document.createElement('span');
        lang.className = 'sma-code-lang';
        lang.textContent = detectSnippetLang(code);

        const copyBtn = document.createElement('button');
        copyBtn.type = 'button';
        copyBtn.className = 'sma-code-copy-btn';
        copyBtn.textContent = 'Copy code';
        copyBtn.addEventListener('click', () => {{
            const originalText = copyBtn.textContent;
            copyCodeToClipboard(code.textContent || '')
                .then(() => {{
                    copyBtn.textContent = 'Copied';
                    setTimeout(() => {{ copyBtn.textContent = originalText; }}, 1200);
                }})
                .catch(() => {{
                    copyBtn.textContent = 'Error';
                    setTimeout(() => {{ copyBtn.textContent = originalText; }}, 1200);
                }});
        }});

        tools.appendChild(lang);
        tools.appendChild(copyBtn);
        pre.appendChild(tools);
    }});
}}

function cycleCodeTheme() {{
    const themes = ['monokai', 'github', 'github-dark', 'atom-one-dark'];
    const current = localStorage.getItem('course-code-theme') || 'monokai';
    const currentIndex = themes.indexOf(current);
    const nextIndex = (currentIndex + 1) % themes.length;
    const nextTheme = themes[nextIndex];
    applyCodeTheme(nextTheme);
}}

function applyTheme(theme) {{
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('course-theme', theme);
    const btn = document.getElementById('theme-toggle');
    btn.textContent = theme === 'dark' ? 'Tema: Oscuro' : 'Tema: Claro';
    btn.title = theme === 'dark' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro';
    // Keep code theme as selected, don't override
}}

function toggleTheme() {{
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    applyTheme(current === 'dark' ? 'light' : 'dark');
    renderMermaid();
}}

// Apply saved preferences immediately
applyStyle(getPreferredStyle());
applyCodeTheme(getPreferredCodeTheme());
applyTheme(getPreferredTheme());

function currentMermaidTheme() {{
    const theme = document.documentElement.getAttribute('data-theme') || 'light';
    return theme === 'dark' ? 'dark' : 'default';
}}

function renderMermaid() {{
    if (typeof mermaid === 'undefined') {{
        console.warn('Mermaid no cargado. Revisa conexión a internet/CDN.');
        return;
    }}

    mermaid.initialize({{
        startOnLoad: false,
        theme: currentMermaidTheme(),
        securityLevel: 'loose'
    }});

    document.querySelectorAll('pre.mermaid').forEach(el => {{
        el.removeAttribute('data-processed');
    }});

    mermaid.run({{ querySelector: 'pre.mermaid' }});
}}

// Init Mermaid
renderMermaid();

// Init Highlight.js
document.querySelectorAll('pre code').forEach(block => {{
    hljs.highlightElement(block);
}});
enhanceCodeBlocks();

// Back to top button
window.addEventListener('scroll', () => {{
    const btn = document.getElementById('back-to-top');
    btn.style.display = window.scrollY > 400 ? 'block' : 'none';
}});

// Active nav highlight
const sections = document.querySelectorAll('section.lesson');
const navLinks = document.querySelectorAll('#sidebar a');

const observer = new IntersectionObserver(entries => {{
    entries.forEach(entry => {{
        if (entry.isIntersecting) {{
            navLinks.forEach(link => link.style.fontWeight = 'normal');
            const active = document.querySelector(`#sidebar a[href="#${{entry.target.id}}"]`);
            if (active) active.style.fontWeight = '700';
        }}
    }});
}}, {{ rootMargin: '-20% 0px -70% 0px' }});

sections.forEach(s => observer.observe(s));

// Mobile sidebar toggle
function toggleSidebar() {{
    const sidebar = document.getElementById('sidebar');
    const current = sidebar.style.display;
    sidebar.style.display = current === 'block' ? 'none' : 'block';
}}

// Close sidebar when clicking a link on mobile
document.querySelectorAll('#sidebar a').forEach(link => {{
    link.addEventListener('click', () => {{
        if (window.innerWidth <= 768) {{
            document.getElementById('sidebar').style.display = 'none';
        }}
    }});
}});
</script>

</body>
</html>"""

    # This template includes lots of CSS/JS braces. We keep the template as a
    # plain string, unescape doubled braces from previous formatting, then inject
    # dynamic sections explicitly.
    html = html_template.replace("{{", "{").replace("}}", "}")
    html = html.replace("{nav}", nav).replace("{body_html}", body_html)

    OUTPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(html, encoding="utf-8")

    ASSETS_DIST_DIR.mkdir(parents=True, exist_ok=True)
    for asset_name in [
        "study-ux.js",
        "study-ux.css",
        "course-switcher.js",
        "course-switcher.css",
        "theme-controls.js",
        "assistant-panel.js",
        "assistant-panel.css",
        "assistant-bridge.js",
    ]:
        src = ASSETS_SRC_DIR / asset_name
        if src.exists():
            shutil.copy2(src, ASSETS_DIST_DIR / asset_name)

    print(f"  HTML generado: {OUTPUT_FILE}")
    print(f"  Tamano: {OUTPUT_FILE.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    print("Construyendo HTML del curso...")
    build_html()
    print("Listo.")
