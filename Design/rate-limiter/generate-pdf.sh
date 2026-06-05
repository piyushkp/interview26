#!/usr/bin/env bash
#
# generate-pdf.sh — Generate PDFs from the Markdown design docs in this folder
# (Mermaid diagrams are rendered to real diagrams, not raw text).
#
# Usage:
#   ./generate-pdf.sh                 Convert every .md file in this folder
#   ./generate-pdf.sh file.md ...     Convert only the named files
#
# The converter and its dependencies live in ../node-module (a sibling folder).
# Dependencies are installed automatically on first run (requires Node + npm).

set -euo pipefail

DOCS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NODE_DIR="$DOCS_DIR/../node-module"

if [ ! -d "$NODE_DIR" ]; then
  echo "Error: converter folder not found at $NODE_DIR" >&2
  exit 1
fi

cd "$NODE_DIR"

if ! command -v node >/dev/null 2>&1; then
  echo "Error: Node.js is not installed." >&2
  exit 1
fi

if [ ! -d node_modules ]; then
  echo "Installing dependencies (first run)..."
  npm install
fi

MD2PDF_DOCS_DIR="$DOCS_DIR" node md2pdf.js "$@"

