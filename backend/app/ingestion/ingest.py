"""
End-to-end ingestion: reads every .docx in a source directory, parses
structure, chunks it, and writes Document + Chunk rows to Postgres.

Run with:  python -m app.ingestion.ingest data/raw
"""
import asyncio
import sys
from pathlib import Path

from dateutil import parser as date_parser

from app.db.session import AsyncSessionLocal
from app.db.models import Document, Chunk
from app.ingestion.parser import parse_docx
from app.ingestion.chunker import chunk_document


def _parse_effective_date(raw: str | None):
    if not raw:
        return None
    try:
        return date_parser.parse(raw).date()
    except (ValueError, TypeError):
        return None


async def ingest_file(path: Path) -> int:
    parsed = parse_docx(str(path))
    chunks = chunk_document(parsed)

    async with AsyncSessionLocal() as session:
        document = Document(
            title=parsed.title or path.stem,
            source_path=str(path),
            department=parsed.metadata.get("department"),
            effective_date=_parse_effective_date(parsed.metadata.get("effective_date")),
            lifecycle_status=parsed.metadata.get("lifecycle_status"),
            document_owner=parsed.metadata.get("document_owner"),
            review_cycle=parsed.metadata.get("review_cycle"),
        )
        session.add(document)
        await session.flush()  # populates document.id before we reference it

        for i, c in enumerate(chunks):
            session.add(Chunk(
                document_id=document.id,
                chunk_index=i,
                text=c.text,
                chunk_type=c.chunk_type,
                heading_path=c.heading_path,
                embedding=None,  # filled in during Phase 3
            ))

        await session.commit()

    return len(chunks)


async def ingest_directory(dir_path: str):
    source_dir = Path(dir_path)
    docx_files = sorted(source_dir.glob("*.docx"))

    if not docx_files:
        print(f"No .docx files found in {source_dir.resolve()}")
        return

    for path in docx_files:
        count = await ingest_file(path)
        print(f"Ingested {path.name}: {count} chunks")


if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "data/raw"
    asyncio.run(ingest_directory(target_dir))


    