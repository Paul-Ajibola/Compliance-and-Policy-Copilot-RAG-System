"""
Manual check: run the full pipeline (dense+BM25+RRF+rerank) and print
the reranked top result for each query, alongside its RRF-only rank for
comparison.

Run with: python -m app.retrieval.test_rerank
"""
import asyncio

from app.db.session import AsyncSessionLocal
from app.retrieval.pipeline import retrieve

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
            results = await retrieve(session, query, shortlist_k=10, final_k=3)
            print(f"\n{'='*70}\nQuery: {query!r}\n{'='*70}")
            for r in results:
                preview = r["text"][:90].replace("\n", " ")
                print(f"  [{r['chunk_index']}] rerank={r['rerank_score']:.3f}  rrf={r['rrf_score']:.4f}  {preview}")


if __name__ == "__main__":
    asyncio.run(run())