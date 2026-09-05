"""
Dense (semantic/embedding-based) retrieval using the HNSW index.
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.embedder import embed_query


async def dense_search(session: AsyncSession, query: str, top_k: int = 10) -> list[dict]:
    """
    Returns chunks ranked by cosine similarity to the query, closest first.
    Each result: {id, chunk_index, text, chunk_type, distance}
    Lower distance = more similar (0 = identical, 2 = opposite, for
    normalized vectors using cosine distance).
    """
    query_vector = embed_query(query)

    result = await session.execute(
        text(
            "SELECT id, chunk_index, text, chunk_type, heading_path, " 
            "embedding <=> CAST(:qvec AS vector) AS distance "
            "FROM chunks "
            "WHERE embedding IS NOT NULL "
            "ORDER BY embedding <=> CAST(:qvec AS vector) "
            "LIMIT :k"
        ),
        {"qvec": str(query_vector), "k": top_k},
    )
    rows = result.mappings().all()
    return [dict(row) for row in rows]

