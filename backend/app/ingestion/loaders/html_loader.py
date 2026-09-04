"""
Parses an .html file into a ParsedDocument using the DOM's real <h1>-<h6>
and <table> tags — reliable in the same way docx_loader.py is.

Caveat: assumes well-formed HTML with real heading tags. Scraped HTML using
<div class="heading"> instead of real <h1>-<h6> won't be detected — that's
closer to what plaintext_loader.py is meant for.
"""
from bs4 import BeautifulSoup, Tag

from app.ingestion.loaders.base import (
    HeadingEl, ParagraphEl, TableEl, ParsedDocument,
    is_metadata_table, extract_metadata_from_grid,
)

_HEADING_TAGS = {f"h{i}": i for i in range(1, 7)}


def _table_to_grid(table_tag: Tag) -> list[list[str]]:
    grid = []
    for row in table_tag.find_all("tr"):
        cells = row.find_all(["td", "th"])
        grid.append([c.get_text(strip=True) for c in cells])
    return [row for row in grid if any(cell for cell in row)]


def parse(path: str) -> ParsedDocument:
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    title = ""
    metadata = {}
    elements = []

    title_tag = soup.find("title")
    if title_tag and title_tag.get_text(strip=True):
        title = title_tag.get_text(strip=True)

    body = soup.body or soup

    for tag in body.find_all(list(_HEADING_TAGS.keys()) + ["p", "table"], recursive=True):
        if tag.find_parent("table") is not None:
            continue

        if tag.name in _HEADING_TAGS:
            text = tag.get_text(strip=True)
            if not text:
                continue
            if not title:
                title = text
                continue
            elements.append(HeadingEl(level=_HEADING_TAGS[tag.name], text=text))

        elif tag.name == "p":
            text = tag.get_text(strip=True)
            if text:
                elements.append(ParagraphEl(text=text))

        elif tag.name == "table":
            grid = _table_to_grid(tag)
            if not grid:
                continue
            if is_metadata_table(grid) and not metadata:
                metadata = extract_metadata_from_grid(grid)
            else:
                elements.append(TableEl(rows=grid))

    return ParsedDocument(title=title, metadata=metadata, elements=elements)