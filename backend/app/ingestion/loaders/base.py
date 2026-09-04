"""
Shared structural types every loader produces, regardless of source format.
chunker.py only ever depends on THESE types — never on any specific loader —
which is what lets .docx, .pdf, .html etc. all feed the same chunking logic.
"""
from dataclasses import dataclass, field


@dataclass
class HeadingEl:
    level: int
    text: str


@dataclass
class ParagraphEl:
    text: str


@dataclass
class TableEl:
    rows: list


@dataclass
class ParsedDocument:
    title: str
    metadata: dict
    elements: list = field(default_factory=list)


METADATA_KEYS = {
    "document owner": "document_owner",
    "department": "department",
    "effective date": "effective_date",
    "lifecycle status": "lifecycle_status",
    "review cycle": "review_cycle",
}


def is_metadata_table(grid: list[list[str]]) -> bool:
    if not grid:
        return False
    keys_found = sum(1 for row in grid if row and row[0].strip().lower() in METADATA_KEYS)
    return keys_found >= 2


def extract_metadata_from_grid(grid: list[list[str]]) -> dict:
    metadata = {}
    for row in grid:
        if len(row) >= 2:
            key = METADATA_KEYS.get(row[0].strip().lower())
            if key:
                metadata[key] = row[1].strip()
    return metadata