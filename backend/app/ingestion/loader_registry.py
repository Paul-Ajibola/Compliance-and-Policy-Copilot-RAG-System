"""
Maps a file extension to the loader capable of parsing it. Adding support
for a new format means writing one new loader module and adding one line
here — chunker.py, ingest.py, and everything downstream never change.
"""
from pathlib import Path

from app.ingestion.loaders import docx_loader, pdf_loader, html_loader, plaintext_loader

_REGISTRY = {
    ".docx": docx_loader.parse,
    ".pdf": pdf_loader.parse,
    ".html": html_loader.parse,
    ".htm": html_loader.parse,
    ".txt": plaintext_loader.parse,
}

SUPPORTED_EXTENSIONS = tuple(_REGISTRY.keys())


def get_loader(path: Path):
    loader = _REGISTRY.get(path.suffix.lower())
    if loader is None:
        raise ValueError(
            f"No loader registered for '{path.suffix}' ({path.name}). "
            f"Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
    return loader