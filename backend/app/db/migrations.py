"""
Minimal migration approach for now: create tables directly from the
SQLAlchemy model metadata, plus the HNSW vector index and the full-text
search column/index. Fine while the schema is still moving fast in early
phases. Once it stabilizes, swap this for Alembic so future schema
changes are tracked as versioned, reversible migrations.
"""

import asyncio

from sqlalchemy import text
from app.db.session import engine
from app.db.models import Base


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw_idx "
            "ON chunks USING hnsw (embedding vector_cosine_ops)"
        ))
    
        await conn.execute(text(
            "ALTER TABLE chunks ADD COLUMN IF NOT EXISTS search_vector "
            "tsvector GENERATED ALWAYS AS (to_tsvector('english', text)) STORED"
        ))
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS chunks_search_vector_gin_idx "
            "ON chunks USING GIN (search_vector)"
        ))

    print("Tables, HNSW index, and full-text search index created (or already existed).")


if __name__ == "__main__":
    asyncio.run(create_tables())
