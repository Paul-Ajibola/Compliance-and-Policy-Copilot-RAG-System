"""
Turns a ParsedDocument into a list of chunks. Each chunk:
  - carries its full heading path prepended, so it's self-contained
  - never splits a table
  - respects a soft max size, but only breaks at paragraph boundaries
    (never mid-sentence, never mid-table)
"""
from dataclasses import dataclass, field
from app.ingestion.loaders.base import ParsedDocument, HeadingEl, ParagraphEl, TableEl

MAX_CHUNK_CHARS = 1200  # soft target; a chunk may exceed this to keep a table atomic


@dataclass
class Chunk:
    text: str
    heading_path: list
    chunk_type: str  # "text" or "table"
    metadata: dict = field(default_factory=dict)


def _table_to_text(rows: list[list[str]]) -> str:
    header, *body = rows
    lines = [" | ".join(header), " | ".join("---" for _ in header)]
    for row in body:
        lines.append(" | ".join(row))
    return "\n".join(lines)


def chunk_document(parsed: ParsedDocument) -> list[Chunk]:
    chunks = []
    heading_stack = []
    buffer_parts = []
    buffer_chars = 0

    def heading_path_text():
        return " > ".join([parsed.title] + [h[1] for h in heading_stack])

    def flush_buffer():
        nonlocal buffer_parts, buffer_chars
        if buffer_parts:
            prefix = heading_path_text()
            body_text = "\n\n".join(buffer_parts)
            chunks.append(Chunk(
                text=f"[{prefix}]\n{body_text}",
                heading_path=[parsed.title] + [h[1] for h in heading_stack],
                chunk_type="text",
                metadata=dict(parsed.metadata),
            ))
        buffer_parts = []
        buffer_chars = 0

    for el in parsed.elements:
        if isinstance(el, HeadingEl):
            flush_buffer()
            while heading_stack and heading_stack[-1][0] >= el.level:
                heading_stack.pop()
            heading_stack.append((el.level, el.text))

        elif isinstance(el, ParagraphEl):
            if buffer_chars + len(el.text) > MAX_CHUNK_CHARS and buffer_parts:
                flush_buffer()
            buffer_parts.append(el.text)
            buffer_chars += len(el.text)

        elif isinstance(el, TableEl):
            flush_buffer()
            prefix = heading_path_text()
            table_text = _table_to_text(el.rows)
            chunks.append(Chunk(
                text=f"[{prefix}]\n{table_text}",
                heading_path=[parsed.title] + [h[1] for h in heading_stack],
                chunk_type="table",
                metadata=dict(parsed.metadata),
            ))

    flush_buffer()
    return chunks