"""
Cross-encoder reranking over the RRF shortlist. Unlike dense/BM25 search
(which score query and chunk independently, then compare), a cross-
encoder looks at the query and chunk TOGETHER in one forward pass —
much more precise, but too slow to run over the whole corpus. That's why
this only runs on the small RRF-fused shortlist, not all chunks.
"""
from sentence_transformers import CrossEncoder

_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_model: CrossEncoder | None = None


def get_reranker() -> CrossEncoder:
    global _model
    if _model is None:
        _model = CrossEncoder(_MODEL_NAME)
    return _model


def rerank(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    """
    candidates: output of reciprocal_rank_fusion() — each dict must have
    a "text" key. Returns the same dicts (preserving existing fields like
    rrf_score) with an added "rerank_score", sorted by that score
    descending, truncated to top_k.
    """
    if not candidates:
        return []

    model = get_reranker()
    pairs = [(query, c["text"]) for c in candidates]
    scores = model.predict(pairs)

    reranked = []
    for candidate, score in zip(candidates, scores):
        row = dict(candidate)
        row["rerank_score"] = float(score)
        reranked.append(row)

    reranked.sort(key=lambda r: r["rerank_score"], reverse=True)
    return reranked[:top_k]

