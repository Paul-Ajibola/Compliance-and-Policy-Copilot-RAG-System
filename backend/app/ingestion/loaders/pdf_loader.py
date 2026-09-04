"""
Parses a .pdf into a ParsedDocument.

IMPORTANT CAVEAT, unlike docx_loader.py: PDFs have no semantic heading
metadata at all. This loader APPROXIMATES structure using heuristics:
numbered-heading patterns (e.g. "2.1 "), font-size relative to the
document's most common size, and merging wrapped lines back into
paragraphs based on vertical spacing.

This is inherently less reliable than docx_loader.py. Spot-check its
results on real documents before fully trusting it.
"""
import re
from collections import Counter

import pdfplumber

from app.ingestion.loaders.base import (
    HeadingEl, ParagraphEl, TableEl, ParsedDocument,
    is_metadata_table, extract_metadata_from_grid,
)

_NUMBERED_HEADING_RE = re.compile(r"^(\d+(\.\d+)*)\s+\S")
_PARAGRAPH_GAP_MULTIPLIER = 1.6


def _numbered_heading_level(text: str) -> int | None:
    m = _NUMBERED_HEADING_RE.match(text.strip())
    if not m:
        return None
    return m.group(1).count(".") + 1


def _most_common_font_size(pdf) -> float:
    sizes = [round(char.get("size", 0)) for page in pdf.pages for char in page.chars]
    if not sizes:
        return 10.0
    return Counter(sizes).most_common(1)[0][0]


def _extract_lines(page, table_bboxes) -> list[dict]:
    words = page.extract_words(extra_attrs=["size"])
    lines: dict[int, list[dict]] = {}
    for w in words:
        in_table = any(
            bbox[0] <= w["x0"] <= bbox[2] and bbox[1] <= w["top"] <= bbox[3]
            for bbox in table_bboxes
        )
        if in_table:
            continue
        line_key = round(w["top"])
        lines.setdefault(line_key, []).append(w)

    result = []
    for key in sorted(lines.keys()):
        line_words = sorted(lines[key], key=lambda w: w["x0"])
        text = " ".join(w["text"] for w in line_words).strip()
        if not text:
            continue
        avg_size = sum(w["size"] for w in line_words) / len(line_words)
        top = min(w["top"] for w in line_words)
        bottom = max(w["bottom"] for w in line_words)
        result.append({"text": text, "top": top, "bottom": bottom, "size": avg_size})
    return result


def parse(path: str) -> ParsedDocument:
    title = ""
    metadata = {}
    elements = []
    first_line_seen = False

    with pdfplumber.open(path) as pdf:
        body_font_size = _most_common_font_size(pdf)

        for page in pdf.pages:
            page_tables = page.find_tables()
            table_bboxes = [t.bbox for t in page_tables]

            stream = []
            for t, bbox in zip(page_tables, table_bboxes):
                grid = [[c.strip() if c else "" for c in row] for row in t.extract()]
                grid = [row for row in grid if any(cell for cell in row)]
                if grid:
                    stream.append((bbox[1], "table", grid))

            lines = _extract_lines(page, table_bboxes)
            for line in lines:
                stream.append((line["top"], "line", line))

            stream.sort(key=lambda item: item[0])

            para_buffer = []
            para_last_bottom = None
            para_size = None

            def flush_paragraph():
                nonlocal para_buffer, para_last_bottom, para_size
                if para_buffer:
                    elements.append(ParagraphEl(text=" ".join(para_buffer)))
                para_buffer = []
                para_last_bottom = None
                para_size = None

            for _, kind, payload in stream:
                if kind == "table":
                    flush_paragraph()
                    if is_metadata_table(payload) and not metadata:
                        metadata = extract_metadata_from_grid(payload)
                    else:
                        elements.append(TableEl(rows=payload))
                    continue

                text, top, size = payload["text"], payload["top"], payload["size"]

                if not first_line_seen:
                    title = text
                    first_line_seen = True
                    continue

                numbered_level = _numbered_heading_level(text)
                is_large_font = size > body_font_size + 1.5
                is_heading = (numbered_level is not None and (is_large_font or len(text) < 80)) or \
                             (is_large_font and len(text) < 80)

                if is_heading:
                    flush_paragraph()
                    level = min(numbered_level, 6) if numbered_level else 1
                    elements.append(HeadingEl(level=level, text=text))
                    continue

                gap_ok = (
                    para_last_bottom is None
                    or (top - para_last_bottom) <= _PARAGRAPH_GAP_MULTIPLIER * size
                )
                size_ok = para_size is None or abs(size - para_size) < 0.5

                if not (gap_ok and size_ok):
                    flush_paragraph()

                para_buffer.append(text)
                para_last_bottom = payload["bottom"]
                para_size = size

            flush_paragraph()

    return ParsedDocument(title=title, metadata=metadata, elements=elements)