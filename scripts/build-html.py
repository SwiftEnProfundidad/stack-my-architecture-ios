#!/usr/bin/env python3
"""
Convierte todos los .md del curso a un unico HTML autocontenido.
No requiere dependencias externas (solo Python 3 estandar).
Mermaid.js y highlight.js se cargan desde CDN.
"""

import os
import re
import sys
from pathlib import Path

COURSE_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = COURSE_ROOT / "dist"
OUTPUT_FILE = OUTPUT_DIR / "curso-stack-my-architecture.html"

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
    "02-integracion/entregables-etapa-2.md",
    "03-evolucion/00-introduccion.md",
    "03-evolucion/01-caching-offline.md",
    "03-evolucion/02-consistencia.md",
    "03-evolucion/03-observabilidad.md",
    "03-evolucion/04-tests-avanzados.md",
    "03-evolucion/05-trade-offs.md",
    "03-evolucion/06-swiftdata-store.md",
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
    "05-maestria/entregables-etapa-5.md",
    "anexos/diagramas/atlas-arquitectura.md",
    "anexos/glosario.md",
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
            code_content = "\n".join(code_buffer)
            code_content = (
                code_content.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            if code_lang == "mermaid":
                html += f'<pre class="mermaid">{code_content}</pre>\n'
            elif code_lang:
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
        nav += f'  <li><a href="#{file_id}">{title}</a></li>\n'

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
        body_html += f'<section id="{file_id}" class="lesson">\n'
        body_html += f'<div class="lesson-path">{filepath}</div>\n'
        body_html += md_to_html(content, file_id)
        body_html += "</section>\n<hr class='lesson-separator'>\n"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stack: My Architecture iOS</title>

<!-- Mermaid.js para diagramas -->
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>

<!-- Highlight.js para syntax highlighting -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/swift.min.js"></script>

<style>
:root {{
    --bg: #ffffff;
    --text: #1a1a2e;
    --sidebar-bg: #f8f9fa;
    --sidebar-width: 300px;
    --accent: #007bff;
    --code-bg: #f6f8fa;
    --border: #e1e4e8;
    --success: #28a745;
    --warning: #ffc107;
    --danger: #dc3545;
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: var(--text);
    background: var(--bg);
    line-height: 1.7;
    display: flex;
}}

/* Sidebar */
#sidebar {{
    position: fixed;
    top: 0;
    left: 0;
    width: var(--sidebar-width);
    height: 100vh;
    overflow-y: auto;
    background: var(--sidebar-bg);
    border-right: 1px solid var(--border);
    padding: 20px 16px;
    font-size: 0.85rem;
    z-index: 100;
}}

#sidebar h2 {{
    font-size: 1.1rem;
    margin-bottom: 16px;
    color: var(--accent);
}}

#sidebar ul {{
    list-style: none;
    padding-left: 0;
}}

#sidebar li {{
    margin-bottom: 4px;
}}

#sidebar li.nav-section {{
    margin-top: 16px;
}}

#sidebar li.nav-section > strong {{
    color: var(--text);
    font-size: 0.9rem;
}}

#sidebar a {{
    color: #586069;
    text-decoration: none;
    display: block;
    padding: 2px 8px;
    border-radius: 4px;
    transition: background 0.15s;
}}

#sidebar a:hover {{
    background: #e2e6ea;
    color: var(--accent);
}}

/* Main content */
#content {{
    margin-left: var(--sidebar-width);
    max-width: 860px;
    padding: 40px 48px;
    width: calc(100% - var(--sidebar-width));
}}

/* Typography */
h1 {{ font-size: 2rem; margin: 48px 0 16px; padding-bottom: 8px; border-bottom: 2px solid var(--accent); }}
h2 {{ font-size: 1.5rem; margin: 36px 0 12px; color: #24292e; }}
h3 {{ font-size: 1.25rem; margin: 28px 0 10px; }}
h4 {{ font-size: 1.1rem; margin: 20px 0 8px; }}
p {{ margin: 12px 0; }}
hr {{ border: none; border-top: 1px solid var(--border); margin: 32px 0; }}
hr.lesson-separator {{ border-top: 3px solid var(--accent); margin: 64px 0; }}

/* Code */
pre {{
    background: var(--code-bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 16px;
    overflow-x: auto;
    margin: 16px 0;
    font-size: 0.88rem;
    line-height: 1.5;
}}

code {{
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', Menlo, monospace;
    font-size: 0.88em;
}}

p code, li code, td code {{
    background: var(--code-bg);
    padding: 2px 6px;
    border-radius: 3px;
    border: 1px solid var(--border);
}}

/* Mermaid */
pre.mermaid {{
    background: white;
    border: 1px solid var(--border);
    text-align: center;
    padding: 20px;
}}

/* Tables */
table {{
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
    font-size: 0.9rem;
}}
th, td {{
    border: 1px solid var(--border);
    padding: 10px 14px;
    text-align: left;
}}
th {{
    background: var(--sidebar-bg);
    font-weight: 600;
}}
tr:nth-child(even) {{ background: #fafbfc; }}

/* Lists */
ul, ol {{
    margin: 12px 0;
    padding-left: 28px;
}}
li {{ margin: 6px 0; }}

/* Links */
a {{ color: var(--accent); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

/* Lesson path badge */
.lesson-path {{
    font-size: 0.75rem;
    color: #6a737d;
    background: var(--sidebar-bg);
    padding: 4px 10px;
    border-radius: 4px;
    display: inline-block;
    margin-bottom: 8px;
    font-family: monospace;
}}

/* Strong in lists */
li strong {{ color: #24292e; }}

/* Responsive */
@media (max-width: 900px) {{
    #sidebar {{ display: none; }}
    #content {{ margin-left: 0; padding: 20px; }}
}}

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
</style>
</head>
<body>

{nav}

<main id="content">
{body_html}
</main>

<button id="back-to-top" onclick="window.scrollTo({{top:0, behavior:'smooth'}})">&#8593;</button>

<script>
// Init Mermaid
mermaid.initialize({{ startOnLoad: true, theme: 'default' }});

// Init Highlight.js
document.querySelectorAll('pre code').forEach(block => {{
    hljs.highlightElement(block);
}});

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
</script>

</body>
</html>"""

    OUTPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"  HTML generado: {OUTPUT_FILE}")
    print(f"  Tamano: {OUTPUT_FILE.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    print("Construyendo HTML del curso...")
    build_html()
    print("Listo.")
