"""
Manual sanity check: run a handful of hand-picked queries through dense,
BM25, and fused retrieval, and print the results side by side for
eyeballing. Not an automated test — Phase 6 builds the real eval harness.

Run with: python -m app.retrieval.test_queries
"""
import asyncio

from app.db.session import AsyncSessionLocal
from app.retrieval.dense import dense_search
from app.retrieval.bm25 import bm25_search
from app.retrieval.fusion import reciprocal_rank_fusion

QUERIES = [
    "how long do we keep employee personnel records",
    "what happens if someone harasses a coworker",
    "remote work equipment stipend",
    "vendor approval threshold for large contracts",
    "can I get my personal data deleted",
]


async def run():
    async with AsyncSessionLocal() as session:
        for query in QUERIES:
            dense_results = await dense_search(session, query, top_k=5)
            bm25_results = await bm25_search(session, query, top_k=5)
            fused = reciprocal_rank_fusion(dense_results, bm25_results)

            print(f"\n{'='*70}\nQuery: {query!r}\n{'='*70}")
            print(f"Dense top-3: {[r['chunk_index'] for r in dense_results[:3]]}")
            print(f"BM25 top-3:  {[r['chunk_index'] for r in bm25_results[:3]]}")
            print(f"Fused top-3:")
            for r in fused[:3]:
                preview = r["text"][:100].replace("\n", " ")
                print(f"  [{r['chunk_index']}] score={r['rrf_score']:.4f}  {preview}")


if __name__ == "__main__":
    asyncio.run(run())