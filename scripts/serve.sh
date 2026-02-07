#!/bin/bash
# ============================================================
# serve.sh — Construye el HTML del curso y lo abre en localhost
# Uso: bash scripts/serve.sh
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$PROJECT_ROOT/dist"
HTML_FILE="$DIST_DIR/curso-stack-my-architecture.html"
PORT=8042

echo ""
echo "=========================================="
echo "  Stack: My Architecture iOS"
echo "  Generador de HTML + servidor local"
echo "=========================================="
echo ""

# Paso 1: Construir el HTML
echo "[1/3] Construyendo HTML desde Markdown..."
python3 "$SCRIPT_DIR/build-html.py"

if [ ! -f "$HTML_FILE" ]; then
    echo "ERROR: No se genero el HTML. Revisa errores arriba."
    exit 1
fi

# Paso 2: Verificar si el puerto esta ocupado
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo ""
    echo "[!] Puerto $PORT ya en uso. Matando proceso anterior..."
    kill $(lsof -Pi :$PORT -sTCP:LISTEN -t) 2>/dev/null || true
    sleep 1
fi

# Paso 3: Servir y abrir
echo "[2/3] Iniciando servidor en http://localhost:$PORT ..."
echo "[3/3] Abriendo en navegador..."
echo ""
echo "  URL: http://localhost:$PORT/curso-stack-my-architecture.html"
echo ""
echo "  Pulsa Ctrl+C para detener el servidor."
echo ""

# Abrir en navegador (macOS)
open "http://localhost:$PORT/curso-stack-my-architecture.html" 2>/dev/null &

# Servir
cd "$DIST_DIR"
python3 -m http.server $PORT
