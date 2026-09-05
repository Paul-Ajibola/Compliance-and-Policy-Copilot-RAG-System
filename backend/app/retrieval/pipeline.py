"""
The full retrieval pipeline: dense + BM25 -> RRF fusion -> rerank.
This is the one function everything downstream (confidence gate, Phase 5
generation) should call, rather than each caller wiring the stages
together separately.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.retrieval.dense import dense_search
from app.retrieval.bm25 import bm25_search
from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.rerank import rerank


async def retrieve(session: AsyncSession, query: str, shortlist_k: int = 10, final_k: int = 5) -> list[dict]:
    dense_results = await dense_search(session, query, top_k=shortlist_k)
    bm25_results = await bm25_search(session, query, top_k=shortlist_k)
    fused = reciprocal_rank_fusion(dense_results, bm25_results)
    return rerank(query, fused, top_k=final_k)