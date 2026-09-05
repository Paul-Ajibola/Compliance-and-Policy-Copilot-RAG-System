"""
First-pass confidence gate: decides whether the top reranked result is
strong enough to answer from, or whether the system should refuse/escalate.

The threshold below is a placeholder — per the roadmap, this is meant to
be picked by eyeballing real score distributions on the golden vs trap
sets (see eval/run_confidence_check.py), not derived analytically. Phase
6 recalibrates this properly against a much larger dataset.
"""
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.retrieval.pipeline import retrieve

# ms-marco-MiniLM cross-encoder outputs raw logits, not a 0-1 probability —
# roughly negative for irrelevant pairs, positive for relevant ones, but
# the exact useful cutoff can only be determined by looking at real scores.
# Starting placeholder; expect to move this after running the check script.
CONFIDENCE_THRESHOLD = 0.0


@dataclass
class GateResult:
    confident: bool
    top_score: float | None
    top_chunk: dict | None
    all_results: list[dict]


async def evaluate_query(session: AsyncSession, query: str) -> GateResult:
    results = await retrieve(session, query, shortlist_k=10, final_k=5)

    if not results:
        return GateResult(confident=False, top_score=None, top_chunk=None, all_results=[])

    top = results[0]
    confident = top["rerank_score"] >= CONFIDENCE_THRESHOLD

    return GateResult(
        confident=confident,
        top_score=top["rerank_score"],
        top_chunk=top,
        all_results=results,
    )