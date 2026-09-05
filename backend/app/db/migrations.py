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
    
    print("Tables created (or already existed).")


if __name__ == "__main__":
    asyncio.run(create_tables())

    