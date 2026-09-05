"""
BM25-style keyword retrieval using Postgres full-text search
(tsvector + ts_rank), backed by the GIN index from migrations.py.

IMPORTANT: plainto_tsquery() alone joins query terms with AND, meaning a
query must contain every one of its meaningful words in a chunk to match
at all. Real BM25 scores partial term overlap instead of requiring every
term — a query like "how long do we keep employee records" would return
ZERO results against a chunk that says "personnel records" but never says
"long" or "keep." We convert plainto_tsquery's AND (&) into OR (|) to get
that partial-match behavior back, while still keeping its stopword
removal and stemming (so "harasses" still matches "harassment").
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def bm25_search(session: AsyncSession, query: str, top_k: int = 10) -> list[dict]:
    """
    Returns chunks ranked by keyword relevance, most relevant first.
    Each result: {id, chunk_index, text, chunk_type, rank}
    """
    result = await session.execute(
        text(
            "SELECT id, chunk_index, text, chunk_type, "
            "ts_rank(search_vector, to_tsquery('english', replace(plainto_tsquery('english', :q)::text, ' & ', ' | '))) AS rank "
            "FROM chunks "
            "WHERE search_vector @@ to_tsquery('english', replace(plainto_tsquery('english', :q)::text, ' & ', ' | ')) "
            "ORDER BY rank DESC "
            "LIMIT :k"
        ),
        {"q": query, "k": top_k},
    )
    rows = result.mappings().all()
    return [dict(row) for row in rows]