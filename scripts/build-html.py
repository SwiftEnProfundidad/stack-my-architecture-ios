#!/usr/bin/env python3
"""
Convierte todos los .md del curso a un unico HTML autocontenido.
No requiere dependencias externas (solo Python 3 estandar).
Mermaid.js y highlight.js se cargan desde CDN.
"""

import os
import posixpath
import re
import sys
import shutil
import html
import time
from pathlib import Path, PurePosixPath

COURSE_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = COURSE_ROOT / "dist"
OUTPUT_FILE = OUTPUT_DIR / "curso-stack-my-architecture.html"
ASSETS_SRC_DIR = COURSE_ROOT / "assets"
ASSETS_DIST_DIR = OUTPUT_DIR / "assets"

# Directorios a incluir en orden (para autodiscovery)
CONTENT_DIRS = [
    "00-informe",
    "00-core-mobile",
    "01-fundamentos",
    "02-integracion",
    "03-evolucion",
    "04-arquitecto",
    "05-maestria",
    "anexos",
]

def discover_files() -> list[str]:
    """
    Descubre archivos .md automáticamente ordenados por directorio y nombre.
    Fallback si FILE_ORDER no está mantenido.
    """
    discovered = []
    for dir_name in CONTENT_DIRS:
        dir_path = COURSE_ROOT / dir_name
        if not dir_path.exists():
            continue
        # Obtener todos los .md recursivamente, excluyendo ciertos patrones
        md_files = []
        for md_file in dir_path.rglob("*.md"):
            # Excluir archivos que no son contenido principal
            if any(excluded in md_file.name for excluded in ["README", "CHANGELOG", "TODO"]):
                continue
            rel_path = md_file.relative_to(COURSE_ROOT)
            md_files.append(str(rel_path))
        # Ordenar alfabéticamente
        md_files.sort()
        discovered.extend(md_files)
    return discovered

# Orden de los archivos (manual - usa FILE_ORDER)
# O usa discover_files() para autodiscovery
FILE_ORDER = [
    "00-informe/INFORME-CURSO.md",
    "00-informe/DECISIONES-TOMADAS.md",
    "00-informe/TODO.md",
    "00-core-mobile/00-introduccion.md",
    "00-core-mobile/01-marco-de-decisiones.md",
    "00-core-mobile/02-invariantes-y-contratos.md",
    "00-core-mobile/03-variabilidad-y-evolucion.md",
    "00-core-mobile/04-calidad-pr-ready.md",
    "00-core-mobile/05-observabilidad-operacion.md",
    "00-core-mobile/06-release-rollback-flags.md",
    "00-core-mobile/07-apis-contratos-versionado.md",
    "00-core-mobile/08-seguridad-privacidad-threat-modeling.md",
    "00-core-mobile/09-dependency-governance-supply-chain.md",
    "00-core-mobile/10-plantillas.md",
    "00-core-mobile/11-crosswalk-ios-android.md",
    "00-core-mobile/12-mobile-architect-parity-ios-android.md",
    "01-fundamentos/00-introduccion.md",
    "01-fundamentos/00-setup.md",
    "01-fundamentos/01-principios-ingenieria.md",
    "01-fundamentos/02-metodologia-bdd-tdd.md",
    "01-fundamentos/02-metodologia-tdd-practica.md",
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
    "02-integracion/02-navegacion-eventos.md",
    "02-integracion/03-contratos-features.md",
    "02-integracion/04-infra-real-network.md",
    "02-integracion/05-integration-tests.md",
    "02-integracion/06-composition-root.md",
    "02-integracion/07-swiftui-enterprise.md",
    "02-integracion/08-swift-concurrency-enterprise.md",
    "02-integracion/09-app-final-etapa-2.md",
    "02-integracion/01-feature-catalog/ADR-002-catalog.md",
    "02-integracion/entregables-etapa-2.md",
    "anexos/consolidacion-etapa-2-integracion.md",
    "03-evolucion/00-introduccion.md",
    "03-evolucion/01-caching-offline.md",
    "03-evolucion/02-consistencia.md",
    "03-evolucion/03-observabilidad.md",
    "03-evolucion/04-tests-avanzados.md",
    "03-evolucion/05-trade-offs.md",
    "03-evolucion/06-swiftdata-store.md",
    "03-evolucion/07-backend-firebase.md",
    "03-evolucion/entregables-etapa-3.md",
    "anexos/calentamiento-etapa-3-evolucion.md",
    "04-arquitecto/00-introduccion.md",
    "04-arquitecto/01-bounded-contexts.md",
    "04-arquitecto/02-reglas-dependencia-ci.md",
    "04-arquitecto/03-navegacion-deeplinks.md",
    "04-arquitecto/04-versionado-spm.md",
    "04-arquitecto/05-guia-arquitectura.md",
    "04-arquitecto/06-quality-gates.md",
    "04-arquitecto/entregables-etapa-4.md",
    "anexos/consolidacion-etapa-4-arquitecto.md",
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
    "05-maestria/10-rubrica-final/01-rubrica-empleabilidad-ios.md",
    "05-maestria/10-rubrica-final/02-evidencias-obligatorias-ios.md",
    "05-maestria/10-rubrica-final/03-checklist-entrega-para-entrevista.md",
    "anexos/calentamiento-etapa-5-maestria.md",
    "anexos/quizzes-autoevaluacion.md",
    "anexos/guia-recuperacion-ios.md",
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
    "anexos/adrs/ADR-003-composition-root-unico.md",
    "anexos/adrs/ADR-004-navegacion-event-driven.md",
    "anexos/adrs/ADR-005-contratos-features.md",
    "anexos/adrs/ADR-006-infra-network-urlsession.md",
    "anexos/adrs/ADR-007-cache-network-first-ttl.md",
    "anexos/adrs/ADR-008-consistencia-invalidation-policy.md",
    "anexos/adrs/ADR-009-observabilidad-por-decoradores.md",
    "anexos/adrs/ADR-010-firebase-backend-principal.md",
    "anexos/adrs/ADR-011-bounded-contexts-governance.md",
    "anexos/adrs/ADR-012-reglas-dependencia-progresivas.md",
    "anexos/adrs/ADR-013-versionado-spm-progresivo.md",
    "anexos/adrs/ADR-014-quality-gates-conceptuales.md",
    "anexos/adrs/TEMPLATE-ADR.md",
    "anexos/apendice-banca-ledger.md",
    "anexos/glosario.md",
    "anexos/proyecto-final.md",
]


def file_id_for_path(rel_path):
    return rel_path.replace("/", "-").replace(".md", "")


def slugify_heading(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower().strip()).strip("-")


def render_meta_block(yaml_content):
    """Renderiza el bloque de metadata YAML como HTML visual."""
    import html as html_module
    result = '<div class="sma-meta-block">\n'
    result += '  <div class="sma-meta-header">📋 Metadata de la lección</div>\n'
    result += '  <div class="sma-meta-grid">\n'

    # Parse simple YAML key: value
    for line in yaml_content.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # Format key and escape HTML
            key_display = html_module.escape(key.replace('_', ' ').title())
            value_escaped = html_module.escape(value)
            result += f'    <div class="sma-meta-item"><span class="sma-meta-key">{key_display}:</span> <span class="sma-meta-value">{value_escaped}</span></div>\n'

    result += '  </div>\n</div>\n'
    return result


MERMAID_ARROW_LEGEND_KEYWORDS = (
    "module",
    "modulo",
    "feature",
    "context",
    "bounded",
    "boundary",
    "dependency",
    "dependenc",
    "protocol",
    "interface",
    "inherit",
    "extension",
    "router",
    "coordinator",
    "viewmodel",
    "repository",
    "adapter",
    "domain",
    "application",
    "infrastructure",
    "wiring",
    "usecase",
    "actor",
    "aggregate",
    "service",
)


def mermaid_needs_arrow_legend(raw_code_content: str, file_path: str) -> bool:
    source = f"{file_path}\n{raw_code_content}".lower()
    relation_tokens = ("-->", "-.->", "==>", "--o", "<|--", "--|>", "..|>", "..>", "o--", "*--")
    has_relations = any(token in raw_code_content for token in relation_tokens)
    if not has_relations:
        return False
    return any(keyword in source for keyword in MERMAID_ARROW_LEGEND_KEYWORDS)


def normalize_mermaid_source(raw_code_content: str) -> str:
    normalized = raw_code_content
    lines = [line.strip() for line in raw_code_content.splitlines() if line.strip()]
    if not lines:
        return normalized
    is_flowchart = lines[0].startswith("flowchart") or lines[0].startswith("graph")
    if is_flowchart:
        normalized = re.sub(r"\.\.\>\|", "-.->|", normalized)
        normalized = re.sub(r"\.\.\>", "-.->", normalized)
        normalized = normalized.replace("-.o", "-.->")
    return normalized


def render_mermaid_block(raw_code_content: str, file_path: str) -> str:
    normalized_code_content = normalize_mermaid_source(raw_code_content)
    escaped_mermaid_code = html.escape(normalized_code_content)
    legend_html = ""
    if mermaid_needs_arrow_legend(normalized_code_content, file_path):
        legend_html = (
            '<div class="sma-mermaid-legend" role="note" aria-label="Leyenda de flechas para diagramas de arquitectura">'
            '<p class="sma-mermaid-legend-title">Leyenda de flechas</p>'
            '<div class="sma-mermaid-legend-grid">'
            '<span class="sma-mermaid-legend-item"><i class="sma-arrow direct-closed"></i>Dependencia directa (runtime)</span>'
            '<span class="sma-mermaid-legend-item"><i class="sma-arrow dashed-closed"></i>Wiring / configuracion</span>'
            '<span class="sma-mermaid-legend-item"><i class="sma-arrow contract-closed"></i>Contrato / abstraccion</span>'
            '<span class="sma-mermaid-legend-item"><i class="sma-arrow solid-open"></i>Salida / propagacion</span>'
            "</div>"
            "</div>\n"
        )
    return f'<div class="sma-mermaid-block">\n{legend_html}<pre class="mermaid">{escaped_mermaid_code}</pre>\n</div>\n'


def md_to_html(md_text, file_id, file_path, file_id_by_path):
    """Convierte markdown a HTML basico con soporte para Mermaid y HTML raw (details/summary)."""
    html = ""
    lines = md_text.split("\n")
    i = 0
    in_code = False
    in_list = ""
    in_table = False
    in_raw_html = False
    raw_html_buffer = []
    code_lang = ""
    code_buffer = []
    table_buffer = []

    # Tags HTML que deben pasar como raw (no envueltos en <p>)
    RAW_HTML_TAGS = ('<details', '</details>', '<summary', '</summary>')

    # Meta block handling
    in_meta = False
    meta_buffer = []

    while i < len(lines):
        line = lines[i]

        # Meta block handling (<!-- sma:meta:v1 --> ... <!-- /sma:meta:v1 -->)
        if not in_code and not in_table and not in_list and not in_raw_html:
            stripped = line.strip()
            if stripped == '<!-- sma:meta:v1 -->':
                in_meta = True
                meta_buffer = []
                i += 1
                continue
            elif stripped == '<!-- /sma:meta:v1 -->' and in_meta:
                in_meta = False
                # Parse YAML and render as visual meta block
                meta_html = render_meta_block('\n'.join(meta_buffer))
                html += meta_html
                meta_buffer = []
                i += 1
                continue
            elif in_meta:
                meta_buffer.append(line)
                i += 1
                continue

        # Raw HTML blocks (details, summary, etc.)
        if not in_code and not in_table and not in_list:
            stripped = line.strip()
            # Check if line starts with a raw HTML tag
            if any(stripped.startswith(tag) for tag in RAW_HTML_TAGS):
                if not in_raw_html:
                    in_raw_html = True
                    raw_html_buffer = []
                raw_html_buffer.append(line)
                i += 1
                continue
            elif in_raw_html:
                # We were in raw HTML block but current line doesn't match
                # Flush the buffer and continue processing
                html += "\n".join(raw_html_buffer) + "\n"
                raw_html_buffer = []
                in_raw_html = False
                # Don't increment, process current line normally
        elif in_raw_html:
            # Inside raw HTML block, keep collecting
            raw_html_buffer.append(line)
            i += 1
            continue

        # Code blocks
        if line.strip().startswith("```") and not in_code:
            if in_list:
                html += f"</{in_list}>\n"
                in_list = ""
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
                html += render_mermaid_block(raw_code_content, file_path)
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
                    html += f"</{in_list}>\n"
                    in_list = ""
                in_table = True
                table_buffer = []
            table_buffer.append(line)
            i += 1
            continue
        elif in_table:
            html += render_table(table_buffer, file_path, file_id, file_id_by_path)
            in_table = False
            table_buffer = []
            # Don't increment, process current line

        # Headers
        header_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if header_match:
            if in_list:
                html += f"</{in_list}>\n"
                in_list = ""
            level = len(header_match.group(1))
            raw_heading = header_match.group(2).strip()

            explicit_anchor = None
            explicit_anchor_match = re.match(r"^(.*?)\s*\{#([A-Za-z0-9_-]+)\}\s*$", raw_heading)
            if explicit_anchor_match:
                raw_heading = explicit_anchor_match.group(1).strip()
                explicit_anchor = explicit_anchor_match.group(2).strip().lower()

            text = inline_format(raw_heading, file_path, file_id, file_id_by_path)
            if explicit_anchor:
                anchor = f"{file_id}-{explicit_anchor}"
            else:
                anchor = f"{file_id}-{slugify_heading(raw_heading)}"
            html += f'<h{level} id="{anchor}">{text}</h{level}>\n'
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^---+\s*$", line):
            if in_list:
                html += f"</{in_list}>\n"
                in_list = ""
            html += "<hr>\n"
            i += 1
            continue

        # List items
        if re.match(r"^\s*[-*]\s+", line):
            if in_list != "ul":
                if in_list:
                    html += f"</{in_list}>\n"
                html += "<ul>\n"
                in_list = "ul"
            content = re.sub(r"^\s*[-*]\s+", "", line)
            # Handle checkbox
            content = content.replace("[ ]", "&#9744;").replace("[x]", "&#9745;")
            html += f"  <li>{inline_format(content, file_path, file_id, file_id_by_path)}</li>\n"
            i += 1
            continue

        # Numbered list
        if re.match(r"^\s*\d+[.)]\s+", line):
            if in_list != "ol":
                if in_list:
                    html += f"</{in_list}>\n"
                html += "<ol>\n"
                in_list = "ol"
            content = re.sub(r"^\s*\d+[.)]\s+", "", line)
            html += f"  <li>{inline_format(content, file_path, file_id, file_id_by_path)}</li>\n"
            i += 1
            continue

        # Close list if we hit non-list content
        if in_list and line.strip():
            html += f"</{in_list}>\n"
            in_list = ""

        # Empty lines
        if not line.strip():
            i += 1
            continue

        # Paragraphs
        html += f"<p>{inline_format(line, file_path, file_id, file_id_by_path)}</p>\n"
        i += 1

    if in_list:
        html += f"</{in_list}>\n"
    if in_table:
        html += render_table(table_buffer, file_path, file_id, file_id_by_path)
    if in_raw_html:
        html += "\n".join(raw_html_buffer) + "\n"

    return html


def render_table(rows, current_file_path, current_file_id, file_id_by_path):
    """Renderiza una tabla markdown a HTML."""
    if len(rows) < 2:
        return ""
    html = '<table>\n<thead>\n<tr>\n'
    headers = [c.strip() for c in rows[0].strip().strip("|").split("|")]
    for h in headers:
        html += f"  <th>{inline_format(h, current_file_path, current_file_id, file_id_by_path)}</th>\n"
    html += "</tr>\n</thead>\n<tbody>\n"

    for row in rows[2:]:  # Skip header separator
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        html += "<tr>\n"
        for c in cells:
            html += f"  <td>{inline_format(c, current_file_path, current_file_id, file_id_by_path)}</td>\n"
        html += "</tr>\n"

    html += "</tbody>\n</table>\n"
    return html


def rewrite_md_link_target(href, current_file_path, current_file_id, file_id_by_path):
    if href.startswith(("http://", "https://", "mailto:", "data:")):
        return href

    if href.startswith("#"):
        fragment = href[1:]
        if not fragment:
            return href
        if fragment.startswith(f"{current_file_id}-"):
            return f"#{fragment}"
        return f"#{current_file_id}-{slugify_heading(fragment.replace('-', ' '))}"

    path_part = href
    anchor = ""
    if "#" in href:
        path_part, anchor = href.split("#", 1)

    if not path_part.endswith(".md"):
        return href

    base = PurePosixPath(current_file_path).parent
    normalized = posixpath.normpath((base / path_part).as_posix())
    target_file_id = file_id_by_path.get(normalized)
    if not target_file_id:
        return href

    if anchor:
        if anchor.startswith(f"{target_file_id}-"):
            return f"#{anchor}"
        return f"#{target_file_id}-{slugify_heading(anchor.replace('-', ' '))}"
    return f"#{target_file_id}"


def inline_format(text, current_file_path, current_file_id, file_id_by_path):
    """Aplica formato inline: bold, italic, code, links."""
    # Inline code (before other formatting to avoid conflicts)
    text = re.sub(r"`([^`]+)`", lambda m: "<code>" + m.group(1).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + "</code>", text)
    # Color chips: render `fill:#xxxxxx` or `stroke:#xxxxxx` as visual swatches
    text = re.sub(
        r"<code>\s*(fill|stroke)\s*:\s*(#[0-9a-fA-F]{3,8})\s*</code>",
        lambda m: (
            f'<span class="color-chip" title="{m.group(1).lower()}:{m.group(2).lower()}">'
            f'<span class="color-chip-swatch" style="background:{m.group(2).lower()};"></span>'
            "</span>"
        ),
        text,
    )
    # Bold + italic
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Images
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img alt="\1" src="\2">', text)
    # Normalize markdown-relative asset paths to dist-local asset paths.
    text = re.sub(r'src="(?:\.\./)+assets/', 'src="assets/', text)
    # Links
    def _link_repl(match):
        label = match.group(1)
        href = match.group(2).strip()
        rewritten = rewrite_md_link_target(href, current_file_path, current_file_id, file_id_by_path)
        return f'<a href="{rewritten}">{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _link_repl, text)
    return text


def build_nav(files_content):
    """Construye la barra de navegacion con anchors y numeracion estable por etapa."""
    nav = (
        '<nav id="sidebar">\n'
        '<div class="sidebar-top">\n'
        '<h2>Indice</h2>\n'
        '<div class="sidebar-search-wrap">\n'
        '  <input id="sidebar-search" type="search" placeholder="Buscar leccion..." '
        'aria-label="Buscar leccion en el curso" autocomplete="off">\n'
        '  <div id="sidebar-search-count" aria-live="polite"></div>\n'
        '</div>\n'
        '</div>\n'
        '<ul>\n'
    )

    section_meta = {
        "00-informe": {"title": "Informe fundacional", "lesson_label": "Documento", "numbered": False},
        "00-core-mobile": {"title": "ETAPA 0: CORE MOBILE", "lesson_label": "Leccion", "numbered": True},
        "01-fundamentos": {"title": "ETAPA 1: JUNIOR", "lesson_label": "Leccion", "numbered": True},
        "02-integracion": {"title": "ETAPA 2: MID", "lesson_label": "Leccion", "numbered": True},
        "03-evolucion": {"title": "ETAPA 3: SENIOR", "lesson_label": "Leccion", "numbered": True},
        "04-arquitecto": {"title": "ETAPA 4: ARQUITECTO", "lesson_label": "Leccion", "numbered": True},
        "05-maestria": {"title": "ETAPA 5: MAESTRIA", "lesson_label": "Leccion", "numbered": True},
        "anexos": {"title": "Anexos", "lesson_label": "Anexo", "numbered": False},
    }

    current_section_key = ""
    section_lesson_counter = 0

    for filepath, content in files_content:
        section_key = filepath.split("/")[0]
        meta = section_meta.get(
            section_key,
            {"title": section_key, "lesson_label": "Leccion", "numbered": False},
        )

        if section_key != current_section_key:
            if current_section_key:
                nav += "</ul></li>\n"
            current_section_key = section_key
            section_lesson_counter = 0
            nav += f'<li class="nav-section"><strong>{meta["title"]}</strong>\n<ul>\n'

        h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = h1_match.group(1).strip() if h1_match else Path(filepath).stem.replace("-", " ").strip()

        section_lesson_counter += 1
        if meta["numbered"]:
            nav_title = f"{meta['lesson_label']} {section_lesson_counter}: {title}"
        else:
            label_prefix = f"{meta['lesson_label']}: "
            if title.lower().startswith(label_prefix.lower()):
                nav_title = title
            else:
                nav_title = f"{meta['lesson_label']}: {title}"

        file_id = file_id_for_path(filepath)
        nav += (
            f'  <li><a class="doc-nav-link" data-lesson-path="{filepath}" '
            f'href="#{file_id}">{nav_title}</a></li>\n'
        )

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

    file_id_by_path = {path: file_id_for_path(path) for path, _ in files_content}

    nav = build_nav(files_content)

    version_sources = [
        "study-ux.js",
        "study-ux.css",
        "course-switcher.js",
        "course-switcher.css",
        "theme-controls.js",
        "assistant-panel.js",
        "assistant-panel.css",
        "assistant-bridge.js",
    ]
    version_marks = [
        int((ASSETS_SRC_DIR / name).stat().st_mtime)
        for name in version_sources
        if (ASSETS_SRC_DIR / name).exists()
    ]
    asset_version = str(max(version_marks + [int(time.time())]))

    body_html = ""
    for filepath, content in files_content:
        file_id = file_id_for_path(filepath)
        body_html += f'<section id="{file_id}" class="lesson" data-topic-id="{file_id}" data-lesson-path="{filepath}">\n'
        body_html += f'<div class="lesson-path">{filepath}</div>\n'
        body_html += md_to_html(content, file_id, filepath, file_id_by_path)
        body_html += "</section>\n"

    html_template = """<!DOCTYPE html>
<html lang="es" data-code-theme="monokai">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="darkreader-lock">
<meta name="course-id" content="stack-my-architecture-ios">
<title>Stack: My Architecture iOS</title>
<link rel="stylesheet" href="assets/study-ux.css?v=__ASSET_VERSION__">
<link rel="stylesheet" href="assets/course-switcher.css?v=__ASSET_VERSION__">
<link rel="stylesheet" href="assets/assistant-panel.css?v=__ASSET_VERSION__">
<script defer src="assets/study-ux.js?v=__ASSET_VERSION__"></script>
<script defer src="assets/course-switcher.js?v=__ASSET_VERSION__"></script>
<script defer src="assets/theme-controls.js?v=__ASSET_VERSION__"></script>
<script defer src="assets/assistant-panel.js?v=__ASSET_VERSION__"></script>
<script defer src="assets/assistant-bridge.js?v=__ASSET_VERSION__"></script>

<!-- Google Fonts - Inter -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;450;500;600;700&display=swap" rel="stylesheet">

<!-- Mermaid.js para diagramas -->
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>

<!-- Highlight.js para syntax highlighting -->
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
   STYLE: BOLD - Dark Mode overrides
   Alto contraste, manteniendo la identidad naranja
   ============================================ */
[data-theme="dark"][data-style="bold"] {{
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
    
    --sidebar-bg: #0f0f14;
    --code-bg: #1a1a22;
    --border: #3a3a45;
    --border-light: #2a2a35;
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
    padding: calc(var(--space-lg) + 8px) var(--space-md) var(--space-lg);
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

#sidebar .sidebar-top {{
    position: sticky;
    top: 0;
    z-index: 5;
    background: var(--sidebar-bg);
    padding-top: var(--space-xs);
}}

#sidebar h2 {{
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: var(--space-sm);
    color: var(--accent);
    letter-spacing: -0.02em;
    text-transform: uppercase;
    font-size: 0.75rem;
    line-height: 1.25;
}}

#sidebar .sidebar-search-wrap {{
    margin-bottom: var(--space-sm);
    padding-bottom: var(--space-sm);
    border-bottom: 1px solid color-mix(in srgb, var(--border) 80%, transparent);
}}

#sidebar #sidebar-search {{
    width: 100%;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    background: var(--bg-surface);
    color: var(--text);
    padding: 8px 10px;
    font-size: 0.82rem;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}}

#sidebar #sidebar-search::placeholder {{
    color: var(--text-muted);
}}

#sidebar #sidebar-search:focus {{
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 20%, transparent);
}}

#sidebar #sidebar-search-count {{
    margin-top: 6px;
    min-height: 1em;
    font-size: 0.72rem;
    color: var(--text-muted);
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
    overflow-x: hidden;
    box-sizing: border-box;
}}

section.lesson {{
    overflow-x: hidden;
    max-width: 100%;
    box-sizing: border-box;
    word-wrap: break-word;
    overflow-wrap: break-word;
}}

section.lesson > * {{
    max-width: 100%;
    box-sizing: border-box;
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
    font-size: 2.5em;
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
    font-size: 1.75em;
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
    font-size: 1.375em;
    margin: var(--space-xl) 0 var(--space-sm);
    color: var(--text);
    font-weight: 600;
}}

h4 {{
    font-size: 1.125em;
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
    background: transparent;
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 0;
    overflow-x: auto;
    margin: var(--space-lg) 0;
    font-size: 0.875em;
    line-height: 1.6;
    box-shadow: var(--shadow-sm);
}}

pre > code {{
    display: block;
    padding: var(--space-lg);
    border-radius: var(--radius-md);
}}

pre > code:not(.hljs) {{
    background: var(--code-bg);
}}

pre.sma-code-enhanced {{
    position: relative;
}}

pre.sma-code-enhanced > code {{
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

/* Meta block styles */
.sma-meta-block {{
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: var(--space-md);
    margin: var(--space-lg) 0;
    box-shadow: var(--shadow-sm);
}}

.sma-meta-header {{
    font-weight: 600;
    font-size: 0.9em;
    color: var(--accent);
    margin-bottom: var(--space-sm);
    padding-bottom: var(--space-xs);
    border-bottom: 1px solid var(--border-light);
}}

.sma-meta-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--space-sm);
}}

.sma-meta-item {{
    font-size: 0.85em;
}}

.sma-meta-key {{
    color: var(--text-secondary);
    font-weight: 500;
}}

.sma-meta-value {{
    color: var(--text);
    font-weight: 600;
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

.color-chip {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 3px 10px;
    border-radius: 999px;
    border: 1px solid var(--border-light);
    background: var(--bg-surface);
    vertical-align: middle;
}}

.color-chip-swatch {{
    width: 12px;
    height: 12px;
    border-radius: 999px;
    border: 1px solid rgba(0, 0, 0, 0.25);
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.4);
}}

.color-chip-label {{
    font-family: var(--font-mono);
    font-size: 0.82em;
    color: var(--text);
    letter-spacing: 0.01em;
}}

/* Mermaid diagrams */
:root {{
    --mermaid-bg: #ffffff;
    --mermaid-text: #0f172a;
    --mermaid-node-bg: #f8fafc;
    --mermaid-node-border: #1d4ed8;
    --mermaid-line: #1e40af;
    --mermaid-label-bg: #eef2ff;
    --mermaid-legend-direct: #d946ef;
    --mermaid-legend-dashed-closed: #64748b;
    --mermaid-legend-contract: #2563eb;
    --mermaid-legend-solid-open: #059669;
}}

.sma-mermaid-block {{
    margin: var(--space-lg) 0;
}}

.sma-mermaid-legend {{
    border: 1px solid var(--border);
    background: var(--bg-surface);
    border-radius: var(--radius-md);
    padding: 10px 12px;
    margin: 0 0 var(--space-sm);
}}

.sma-mermaid-legend-title {{
    margin: 0 0 8px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    color: var(--text-secondary);
}}

.sma-mermaid-legend-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 6px 12px;
}}

.sma-mermaid-legend-item {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 0.78rem;
    color: var(--text);
}}

.sma-arrow {{
    position: relative;
    display: inline-block;
    width: 36px;
    height: 12px;
    flex: 0 0 36px;
    line-height: 0;
}}

.sma-arrow::before {{
    content: '';
    position: absolute;
    left: 0;
    right: 8px;
    top: 50%;
    border-top: 2px solid currentColor;
    transform: translateY(-50%);
}}

.sma-arrow::after {{
    content: '';
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    border-left: 8px solid currentColor;
    border-top: 5px solid transparent;
    border-bottom: 5px solid transparent;
}}

.sma-arrow.direct-closed {{ color: var(--mermaid-legend-direct); }}

.sma-arrow.dashed-closed {{
    color: var(--mermaid-legend-dashed-closed);
}}

.sma-arrow.dashed-closed::before {{
    border-top-style: dashed;
}}

.sma-arrow.contract-closed {{
    color: var(--mermaid-legend-contract);
}}

.sma-arrow.contract-closed::before {{
    border-top-width: 3px;
}}

.sma-arrow.solid-open::after {{
    width: 8px;
    height: 8px;
    border: 0;
    border-top: 2px solid currentColor;
    border-right: 2px solid currentColor;
    transform: translateY(-50%) rotate(45deg);
    right: 1px;
    background: transparent;
}}

.sma-arrow.solid-open {{ color: var(--mermaid-legend-solid-open); }}

pre.mermaid {{
    background: var(--mermaid-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    text-align: center;
    padding: var(--space-xl);
    box-shadow: var(--shadow);
    overflow-x: auto;
    overflow-y: hidden;
}}

pre.mermaid svg {{
    max-width: 100%;
    height: auto;
}}

html[data-theme][data-style] pre.mermaid .label,
html[data-theme][data-style] pre.mermaid .nodeLabel,
html[data-theme][data-style] pre.mermaid .edgeLabel,
html[data-theme][data-style] pre.mermaid .cluster-label,
html[data-theme][data-style] pre.mermaid text,
html[data-theme][data-style] pre.mermaid tspan {{
    fill: var(--mermaid-text) !important;
    color: var(--mermaid-text) !important;
}}

html[data-theme][data-style] pre.mermaid .node rect,
html[data-theme][data-style] pre.mermaid .node polygon,
html[data-theme][data-style] pre.mermaid .node circle,
html[data-theme][data-style] pre.mermaid .node ellipse,
html[data-theme][data-style] pre.mermaid .cluster rect,
html[data-theme][data-style] pre.mermaid .actor,
html[data-theme][data-style] pre.mermaid .labelBox {{
    fill: var(--mermaid-node-bg) !important;
    stroke: var(--mermaid-node-border) !important;
}}

html[data-theme][data-style] pre.mermaid .edgePath .path,
html[data-theme][data-style] pre.mermaid path.relation,
html[data-theme][data-style] pre.mermaid line {{
    stroke: var(--mermaid-line) !important;
}}

html[data-theme][data-style] pre.mermaid .messageLine0,
html[data-theme][data-style] pre.mermaid .messageLine1,
html[data-theme][data-style] pre.mermaid .messageLine2 {{
    stroke: var(--mermaid-line) !important;
    stroke-width: 2px !important;
    opacity: 1 !important;
}}

html[data-theme][data-style] pre.mermaid .arrowheadPath,
html[data-theme][data-style] pre.mermaid marker path,
html[data-theme][data-style] pre.mermaid marker polygon,
html[data-theme][data-style] pre.mermaid marker polyline {{
    fill: var(--mermaid-line) !important;
    stroke: var(--mermaid-line) !important;
    opacity: 1 !important;
}}

html[data-theme][data-style] pre.mermaid .edgeLabel rect,
html[data-theme][data-style] pre.mermaid .labelBkg {{
    fill: var(--mermaid-label-bg) !important;
    opacity: 1 !important;
}}

img {{
    max-width: 100%;
    height: auto;
}}

p > img {{
    display: block;
    margin: var(--space-md) auto;
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
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
    h1 {{ font-size: 1.6em; margin: 32px 0 12px; }}
    h2 {{ font-size: 1.3em; margin: 28px 0 10px; }}
    h3 {{ font-size: 1.1em; margin: 20px 0 8px; }}
    h4 {{ font-size: 1em; margin: 16px 0 6px; }}
    pre {{ padding: 0; font-size: 0.82em; }}
    th, td {{ padding: 8px 10px; font-size: 0.85rem; }}
}}

@media (max-width: 480px) {{
    #content {{ padding: 16px 12px; }}
    h1 {{ font-size: 1.4em; }}
    h2 {{ font-size: 1.2em; }}
    pre {{ padding: 0; font-size: 0.78em; overflow-x: scroll; }}
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

/* ============================================
   HLJS CODE THEMES (embedded - no CDN dependency)
   ============================================ */
[data-code-theme="monokai"] pre > code.hljs {{ background: #272822; color: #ddd; }}
[data-code-theme="monokai"] .hljs-keyword,[data-code-theme="monokai"] .hljs-literal,[data-code-theme="monokai"] .hljs-selector-tag,[data-code-theme="monokai"] .hljs-tag {{ color: #f92672; }}
[data-code-theme="monokai"] .hljs-string,[data-code-theme="monokai"] .hljs-title,[data-code-theme="monokai"] .hljs-type,[data-code-theme="monokai"] .hljs-built_in,[data-code-theme="monokai"] .hljs-variable {{ color: #a6e22e; }}
[data-code-theme="monokai"] .hljs-comment,[data-code-theme="monokai"] .hljs-meta {{ color: #75715e; }}
[data-code-theme="monokai"] .hljs-number,[data-code-theme="monokai"] .hljs-symbol {{ color: #ae81ff; }}
[data-code-theme="monokai"] .hljs-attr {{ color: #a6e22e; }}
[data-code-theme="monokai"] .hljs-params {{ color: #fd971f; }}

[data-code-theme="github"] pre > code.hljs {{ background: #ffffff; color: #24292e; }}
[data-code-theme="github"] .hljs-keyword,[data-code-theme="github"] .hljs-type {{ color: #d73a49; }}
[data-code-theme="github"] .hljs-title,[data-code-theme="github"] .hljs-title.function_ {{ color: #6f42c1; }}
[data-code-theme="github"] .hljs-string {{ color: #032f62; }}
[data-code-theme="github"] .hljs-number,[data-code-theme="github"] .hljs-literal {{ color: #005cc5; }}
[data-code-theme="github"] .hljs-comment {{ color: #6a737d; }}
[data-code-theme="github"] .hljs-built_in,[data-code-theme="github"] .hljs-symbol {{ color: #e36209; }}
[data-code-theme="github"] .hljs-attr {{ color: #005cc5; }}
[data-code-theme="github"] .hljs-params {{ color: #24292e; }}

[data-code-theme="github-dark"] pre > code.hljs {{ background: #0d1117; color: #c9d1d9; }}
[data-code-theme="github-dark"] .hljs-keyword,[data-code-theme="github-dark"] .hljs-type {{ color: #ff7b72; }}
[data-code-theme="github-dark"] .hljs-title,[data-code-theme="github-dark"] .hljs-title.function_ {{ color: #d2a8ff; }}
[data-code-theme="github-dark"] .hljs-string {{ color: #a5d6ff; }}
[data-code-theme="github-dark"] .hljs-number,[data-code-theme="github-dark"] .hljs-literal {{ color: #79c0ff; }}
[data-code-theme="github-dark"] .hljs-comment {{ color: #8b949e; }}
[data-code-theme="github-dark"] .hljs-built_in,[data-code-theme="github-dark"] .hljs-symbol {{ color: #ffa657; }}
[data-code-theme="github-dark"] .hljs-attr {{ color: #79c0ff; }}
[data-code-theme="github-dark"] .hljs-params {{ color: #c9d1d9; }}

[data-code-theme="atom-one-dark"] pre > code.hljs {{ background: #282c34; color: #abb2bf; }}
[data-code-theme="atom-one-dark"] .hljs-keyword {{ color: #c678dd; }}
[data-code-theme="atom-one-dark"] .hljs-title,[data-code-theme="atom-one-dark"] .hljs-title.function_ {{ color: #61afef; }}
[data-code-theme="atom-one-dark"] .hljs-string {{ color: #98c379; }}
[data-code-theme="atom-one-dark"] .hljs-number,[data-code-theme="atom-one-dark"] .hljs-literal {{ color: #d19a66; }}
[data-code-theme="atom-one-dark"] .hljs-comment {{ color: #5c6370; font-style: italic; }}
[data-code-theme="atom-one-dark"] .hljs-built_in {{ color: #e6c07b; }}
[data-code-theme="atom-one-dark"] .hljs-type {{ color: #e5c07b; }}
[data-code-theme="atom-one-dark"] .hljs-attr {{ color: #d19a66; }}
[data-code-theme="atom-one-dark"] .hljs-params {{ color: #abb2bf; }}
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
    <button id="course-switcher-toggle" type="button">&#9776; Cursos</button>
    <div id="course-switcher-menu" class="course-switcher-menu">
        <a id="course-switcher-home" href="#">Cursos</a>
        <a id="course-switcher-ios" href="#">Curso iOS</a>
        <a id="course-switcher-android" href="#">Curso Android</a>
        <a id="course-switcher-sdd" href="#">Curso IA + SDD</a>
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
// Fix browser HTML5 parser nesting: move non-li children out of ol/ul
(function fixListNesting() {{
    document.querySelectorAll('ol, ul').forEach(function(list) {{
        var children = Array.from(list.children);
        for (var i = children.length - 1; i >= 0; i--) {{
            var child = children[i];
            if (child.tagName !== 'LI' && child.tagName !== 'SCRIPT' && child.tagName !== 'TEMPLATE') {{
                list.parentNode.insertBefore(child, list.nextSibling);
            }}
        }}
    }});
}})();
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
    document.documentElement.setAttribute('data-code-theme', theme);
    const btn = document.getElementById('code-theme-cycle-btn');
    if (btn) {{
        btn.textContent = 'Codigo: ' + theme.charAt(0).toUpperCase() + theme.slice(1).replace(/-/g, ' ');
    }}
    
    document.querySelectorAll('pre code[data-highlighted]').forEach(block => {{
        block.removeAttribute('data-highlighted');
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
    if (className.includes('language-python') || className.includes('language-py')) return 'PY';
    if (className.includes('language-mermaid')) return 'Mermaid';
    if (className.includes('language-xml') || className.includes('language-html')) return 'XML';
    if (className.includes('language-sql')) return 'SQL';
    if (className.includes('language-markdown') || className.includes('language-md')) return 'MD';
    if (className.includes('language-gherkin') || className.includes('language-feature')) return 'Gherkin';

    const content = (codeEl.textContent || '').trim();
    if (!content) return 'TXT';

    if (
        content.startsWith('flowchart') ||
        content.startsWith('sequenceDiagram') ||
        content.startsWith('classDiagram') ||
        content.startsWith('stateDiagram') ||
        content.startsWith('erDiagram')
    ) return 'Mermaid';

    if (/^(\\$\\s*)?(swift|xcodebuild|npm|yarn|pnpm|git|python3|node|bash|sh)\\b/m.test(content)) return 'SH';
    if (/^\\s*(import\\s+SwiftUI|import\\s+Foundation|struct\\s+\\w+\\s*[:\\{{]|enum\\s+\\w+\\s*[:\\{{]|actor\\s+\\w+\\s*[:\\{{]|protocol\\s+\\w+\\s*[:\\{{])/m.test(content)) return 'Swift';
    if (/^\\s*(\\{{|\\[\\s*\\{{|\"[^\"]+\"\\s*:)/m.test(content)) return 'JSON';
    if (/^\\s*[a-zA-Z0-9_-]+\\s*:\\s*.+$/m.test(content) && !/;\\s*$/m.test(content)) return 'YAML';
    if (/^\\s*SELECT\\b|^\\s*INSERT\\b|^\\s*UPDATE\\b|^\\s*DELETE\\b|^\\s*CREATE\\s+TABLE\\b/im.test(content)) return 'SQL';
    if (/^\\s*<[^>]+>/m.test(content)) return 'XML';

    return 'TXT';
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
        copyBtn.textContent = 'Copiar';
        copyBtn.setAttribute('aria-label', `Copiar snippet ${lang.textContent}`);
        copyBtn.addEventListener('click', () => {{
            const originalText = copyBtn.textContent;
            copyCodeToClipboard(code.textContent || '')
                .then(() => {{
                    copyBtn.textContent = 'Copiado';
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

    document.querySelectorAll('pre.mermaid').forEach(function(el) {{
        if (!el.dataset.originalMermaid) {{
            el.dataset.originalMermaid = (el.textContent || '').trimEnd();
        }}
        if (el.dataset.originalMermaid) {{
            el.innerHTML = '';
            el.textContent = el.dataset.originalMermaid;
        }}
        el.removeAttribute('data-processed');
    }});

    mermaid.initialize({{
        startOnLoad: false,
        theme: currentMermaidTheme(),
        securityLevel: 'loose'
    }});

    mermaid.run({{ querySelector: 'pre.mermaid' }}).catch(function() {{}});
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

// Sidebar search/filter
const sidebarSearchInput = document.getElementById('sidebar-search');
const sidebarSearchCount = document.getElementById('sidebar-search-count');

function normalizeSearchText(value) {{
    return (value || '')
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '');
}}

function applySidebarSearch() {{
    if (!sidebarSearchInput) return;
    const query = normalizeSearchText(sidebarSearchInput.value.trim());
    const sections = document.querySelectorAll('#sidebar li.nav-section');
    let visibleLessons = 0;

    sections.forEach(section => {{
        const sectionTitle = section.querySelector(':scope > strong');
        const sectionLabel = normalizeSearchText(sectionTitle ? sectionTitle.textContent : '');
        const links = section.querySelectorAll('a.doc-nav-link');
        let sectionHasVisible = false;

        links.forEach(link => {{
            const item = link.closest('li');
            if (!item) return;
            const lessonPath = normalizeSearchText(link.dataset.lessonPath || '');
            const lessonTitle = normalizeSearchText(link.textContent || '');
            const match = !query || lessonTitle.includes(query) || lessonPath.includes(query) || sectionLabel.includes(query);
            item.style.display = match ? '' : 'none';
            if (match) {{
                sectionHasVisible = true;
                visibleLessons += 1;
            }}
        }});

        section.style.display = sectionHasVisible ? '' : 'none';
    }});

    if (sidebarSearchCount) {{
        if (!query) {{
            sidebarSearchCount.textContent = '';
        }} else if (visibleLessons === 1) {{
            sidebarSearchCount.textContent = '1 resultado';
        }} else {{
            sidebarSearchCount.textContent = `${{visibleLessons}} resultados`;
        }}
    }}
}}

if (sidebarSearchInput) {{
    sidebarSearchInput.addEventListener('input', applySidebarSearch);
    sidebarSearchInput.addEventListener('keydown', event => {{
        if (event.key === 'Escape') {{
            sidebarSearchInput.value = '';
            applySidebarSearch();
            sidebarSearchInput.blur();
        }}
    }});
    applySidebarSearch();
}}
</script>

</body>
</html>"""

    # This template includes lots of CSS/JS braces. We keep the template as a
    # plain string, unescape doubled braces from previous formatting, then inject
    # dynamic sections explicitly.
    html = html_template.replace("{{", "{").replace("}}", "}")
    html = html.replace("__ASSET_VERSION__", asset_version)
    html = html.replace("{nav}", nav).replace("{body_html}", body_html)

    OUTPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(html, encoding="utf-8")

    ASSETS_DIST_DIR.mkdir(parents=True, exist_ok=True)
    for src in ASSETS_SRC_DIR.iterdir():
        if src.is_file():
            shutil.copy2(src, ASSETS_DIST_DIR / src.name)

    print(f"  HTML generado: {OUTPUT_FILE}")
    print(f"  Tamano: {OUTPUT_FILE.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    print("Construyendo HTML del curso...")
    build_html()
    print("Listo.")
