"""
Fallback loader for formats with no extractable structure: raw .txt
files, or text where headings/tables were already lost upstream.
No heading detection is attempted — there's no structure to find.
"""
from pathlib import Path

from app.ingestion.loaders.base import ParagraphEl, ParsedDocument


def parse(path: str) -> ParsedDocument:
    text = Path(path).read_text(encoding="utf-8")
    raw_paragraphs = [p.strip() for p in text.split("\n\n")]
    elements = [ParagraphEl(text=p) for p in raw_paragraphs if p]
    title = Path(path).stem.replace("_", " ").replace("-", " ").title()
    return ParsedDocument(title=title, metadata={}, elements=elements)