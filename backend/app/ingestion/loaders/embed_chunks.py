"""
Backfills embeddings for any chunk currently missing one.
Run after ingestion, or after changing the embedding model.

Run with: python -m app.ingestion.embed chunks
"""

import asyncio
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.db.models import Chunk
from app.ingestion.embedder import embed_passages


BATCH_SIZE = 32

async def embed_pending_chunks():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Chunk).where(Chunk.embedding.is_(None)))
        chunks = result.scalars().all()

        if not chunks:
            print("No chunks pending embeddings.")
            return

        
        print(f"Embedding {len(chunks)} chunks...")
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i + BATCH_SIZE]
            texts = [c.text for c in batch]
            vectors = embed_passages(texts)
            for chunk, vector in zip(batch, vectors):
                chunk.embedding = vector
            await session.commit()
            print(f"  embedded {min(i + BATCH_SIZE, len(chunks))}/{len(chunks)}")





if __name__ == "__main__":
    asyncio.run(embed_pending_chunks())