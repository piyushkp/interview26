#!/usr/bin/env bash
#
# generate-all-docs.sh — Combine every design PDF into a single
# All-Design-Docs.pdf with a clickable Table of Contents and PDF bookmarks.
#
# This stitches together the per-folder PDFs (produced by each folder's
# generate-pdf.sh). Pass --rebuild to regenerate those source PDFs first.
#
# Usage:
#   ./generate-all-docs.sh              Merge existing per-folder PDFs + TOC
#   ./generate-all-docs.sh --rebuild    Rebuild each source PDF, then merge

set -euo pipefail

DESIGN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MERGE_SCRIPT="$DESIGN_DIR/node-module/merge-with-toc.py"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is not installed." >&2
  exit 1
fi

if [ "${1:-}" = "--rebuild" ]; then
  echo "Rebuilding per-folder PDFs..."
  while IFS= read -r script; do
    dir="$(dirname "$script")"
    echo "  -> $(basename "$dir")"
    (cd "$dir" && ./generate-pdf.sh)
  done < <(find "$DESIGN_DIR" -mindepth 2 -name generate-pdf.sh)
fi

# Ensure the Python dependencies are present.
if ! python3 -c "import pypdf, reportlab" >/dev/null 2>&1; then
  echo "Installing Python dependencies (pypdf, reportlab)..."
  python3 -m pip install --quiet pypdf reportlab
fi

python3 "$MERGE_SCRIPT"
