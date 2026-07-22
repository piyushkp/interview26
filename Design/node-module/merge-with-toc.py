#!/usr/bin/env python3
"""merge-with-toc.py — Combine the individual design PDFs into a single
``All-Design-Docs.pdf`` with a clickable Table of Contents page and matching
PDF outline bookmarks.

The individual PDFs are produced by ``generate-pdf.sh`` in each doc folder
(via ``node-module/md2pdf.js``). This script only stitches those existing
PDFs together and prepends a generated TOC — it does not re-render Markdown.

Usage:
    python3 merge-with-toc.py            # rebuild Design/All-Design-Docs.pdf

Requires: pypdf and reportlab (``pip install pypdf reportlab``).

The book order below is the canonical order of the combined document. To add,
remove, or reorder chapters, edit the ``DOCS`` list.
"""

import os
import sys

try:
    from reportlab.pdfgen import canvas
    from pypdf import PdfReader, PdfWriter
    from pypdf.annotations import Link
    from pypdf.generic import Fit
except ImportError as exc:  # pragma: no cover - guidance for first run
    sys.stderr.write(
        f"Missing dependency: {exc}.\n"
        "Install with: pip install pypdf reportlab\n"
    )
    sys.exit(1)

# Design/ is the parent of this node-module/ folder.
DESIGN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(DESIGN_DIR, "All-Design-Docs.pdf")

# Page geometry — matches the A4 pages emitted by md2pdf.js / Chromium.
PAGE_W, PAGE_H = 594.96, 841.92

# Canonical chapter order: (display title, path relative to Design/).
DOCS = [
    ("Designing a Multi-Tenant CI/CD Platform (Cloud-Native)",
     "cicd/multi-tenant-cicd-design.pdf"),
    ("Designing a Sandboxed Cloud IDE / Notebook (Colab-like)",
     "cloud-ide/sandboxed-cloud-ide-design.pdf"),
    ("Designing a Cloud DevBox Platform (Remote Dev Environments)",
     "devbox/cloud-devbox-design.pdf"),
    ("Designing an Instagram-like Photo/Video Sharing App (Feed-Focused)",
     "Instagram feed/instagram-feed-design.pdf"),
    ("Designing an In-Memory Key\u2013Value Database (Redis-like)",
     "kvstore/in-memory-kv-store-design.pdf"),
    ("Designing a Distributed Rate Limiter",
     "rate-limiter/distributed-rate-limiter.pdf"),
    ("Distributed Rate Limiter \u2014 One-Page Cheat Sheet",
     "rate-limiter/rate-limiter-cheatsheet.pdf"),
    ("Designing a Slack-like Team Messaging System (Real-Time Focus)",
     "slack/slack-messaging-design.pdf"),
    ("Designing an Online Chess Platform (Real-Time, Timed Games)",
     "chess/online-chess-design.pdf"),
]

# TOC layout constants (points; PDF origin is bottom-left).
LEFT = 54.0
RIGHT = PAGE_W - 54.0
NUM_INDENT = 26.0        # gap between the "1." marker and the title
ROW_H = 30.0             # vertical spacing between chapter rows
FIRST_ROW_Y = PAGE_H - 132.0
BOTTOM_LIMIT = 60.0      # start a new TOC page below this baseline
INK = (0.12, 0.14, 0.16)
GRAY = 0.42


def load_chapters():
    """Return [(title, abs_path, page_count)] for every existing chapter PDF."""
    chapters = []
    for title, rel in DOCS:
        path = os.path.join(DESIGN_DIR, rel)
        if not os.path.exists(path):
            sys.stderr.write(f"  warning: skipping missing PDF {rel}\n")
            continue
        count = len(PdfReader(path).pages)
        chapters.append((title, path, count))
    return chapters


def plan_layout(chapters, toc_page_count):
    """Compute each chapter's 1-based start page in the final combined PDF."""
    rows = []
    cursor = toc_page_count  # 0-based index of the first content page
    for title, path, count in chapters:
        rows.append({"title": title, "start_index": cursor,
                     "start_page": cursor + 1})
        cursor += count
    return rows


def render_toc(rows, tmp_path, total_pages):
    """Draw the Table of Contents to ``tmp_path``.

    Returns (toc_page_count, links) where ``links`` is a list of dicts:
    {toc_page, rect, target_index} used to attach clickable annotations
    after the documents are merged.
    """
    c = canvas.Canvas(tmp_path, pagesize=(PAGE_W, PAGE_H))
    links = []
    toc_page = 0

    def draw_header():
        c.setFillColorRGB(*INK)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(LEFT, PAGE_H - 76, "System Design Documents")
        c.setFillGray(GRAY)
        c.setFont("Helvetica", 11)
        c.drawString(
            LEFT, PAGE_H - 96,
            f"Table of Contents   \u00b7   {len(rows)} documents"
            f"   \u00b7   {total_pages} pages",
        )
        c.setStrokeGray(0.8)
        c.setLineWidth(1)
        c.line(LEFT, PAGE_H - 106, RIGHT, PAGE_H - 106)

    draw_header()
    y = FIRST_ROW_Y
    for i, row in enumerate(rows):
        if y < BOTTOM_LIMIT:
            c.showPage()
            toc_page += 1
            draw_header()
            y = FIRST_ROW_Y

        marker = f"{i + 1}."
        title = row["title"]
        page_str = str(row["start_page"])

        # Chapter number marker.
        c.setFillGray(GRAY)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(LEFT, y, marker)

        # Chapter title.
        c.setFillColorRGB(*INK)
        c.setFont("Helvetica", 12)
        title_x = LEFT + NUM_INDENT
        c.drawString(title_x, y, title)
        title_end = title_x + c.stringWidth(title, "Helvetica", 12)

        # Right-aligned page number.
        c.setFont("Helvetica", 12)
        c.drawRightString(RIGHT, y, page_str)
        page_start = RIGHT - c.stringWidth(page_str, "Helvetica", 12)

        # Dotted leader between title and page number.
        if page_start - title_end > 12:
            c.setStrokeGray(0.72)
            c.setLineWidth(0.75)
            c.setDash(1, 3)
            c.line(title_end + 6, y + 3, page_start - 6, y + 3)
            c.setDash()

        # Invisible clickable area spanning the whole row.
        links.append({
            "toc_page": toc_page,
            "rect": (LEFT - 6, y - 8, RIGHT + 6, y + 16),
            "target_index": row["start_index"],
        })
        y -= ROW_H

    c.setFillGray(0.6)
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(LEFT, 40, "Click any entry to jump to that document.")
    c.showPage()
    c.save()
    return toc_page + 1, links


def build():
    chapters = load_chapters()
    if not chapters:
        sys.stderr.write("No chapter PDFs found; nothing to build.\n")
        sys.exit(1)

    tmp_toc = os.path.join(DESIGN_DIR, ".toc.tmp.pdf")
    content_pages = sum(count for _title, _path, count in chapters)

    # Pass 1: lay out assuming a single TOC page to learn the real page count.
    rows = plan_layout(chapters, toc_page_count=1)
    toc_count, _ = render_toc(rows, tmp_toc, 1 + content_pages)
    # Pass 2: re-plan with the true TOC page count and render final numbers.
    rows = plan_layout(chapters, toc_page_count=toc_count)
    toc_count, links = render_toc(rows, tmp_toc, toc_count + content_pages)

    writer = PdfWriter()
    for page in PdfReader(tmp_toc).pages:
        writer.add_page(page)
    for (title, path, _count), row in zip(chapters, rows):
        for page in PdfReader(path).pages:
            writer.add_page(page)

    # Clickable TOC entries -> the first page of each document.
    for link in links:
        target = writer.pages[link["target_index"]]
        top = float(target.mediabox.top)
        added = writer.add_annotation(
            page_number=link["toc_page"],
            annotation=Link(
                rect=link["rect"],
                border=[0, 0, 0],
                target_page_index=link["target_index"],
                fit=Fit.xyz(left=0, top=top),
            ),
        )
        # pypdf stores /Dest as [<page-index int>, /XYZ ...], which is an
        # invalid local destination. Replace the leading integer with a real
        # indirect reference to the target page so viewers actually navigate.
        dest = added.get_object().get("/Dest")
        if dest is not None:
            dest[0] = target.indirect_reference

    # Outline bookmarks (reader sidebar / navigation panel).
    writer.add_outline_item("Table of Contents", 0)
    for row in rows:
        writer.add_outline_item(row["title"], row["start_index"])
    writer.page_mode = "/UseOutlines"  # show the bookmarks panel on open

    with open(OUTPUT, "wb") as fh:
        writer.write(fh)
    os.remove(tmp_toc)

    print(f"Wrote {os.path.relpath(OUTPUT, DESIGN_DIR)} "
          f"({len(writer.pages)} pages, {toc_count} TOC page(s))")
    for i, row in enumerate(rows, 1):
        print(f"  {row['start_page']:>4}  {i}. {row['title']}")


if __name__ == "__main__":
    build()
