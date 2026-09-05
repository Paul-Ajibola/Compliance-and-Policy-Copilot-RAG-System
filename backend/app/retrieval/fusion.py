"""
Reciprocal Rank Fusion: combines two independently-ranked result lists
(dense + BM25) into one fused ranking, without needing to compare their
raw scores directly — cosine distance and ts_rank are on completely
different scales and aren't directly comparable, which is exactly the
problem RRF sidesteps by using RANK POSITION instead of raw score.

Formula per list: score(doc) = 1 / (k + rank(doc))
  - rank is 1-indexed (best result = rank 1, not 0)
  - k is a smoothing constant (60 is the standard default from the
    original RRF paper)
Final score = sum of that formula across every list the doc appears in.
"""

RRF_K = 60


def reciprocal_rank_fusion(*ranked_lists: list[dict], id_key: str = "id", k: int = RRF_K) -> list[dict]:
    """
    Each ranked_list is a list of dicts already sorted best-first. Returns
    a single fused list, sorted by fused score descending, each with an
    added "rrf_score" field.
    """
    scores: dict = {}
    merged_rows: dict = {}

    for ranked_list in ranked_lists:
        for rank, row in enumerate(ranked_list, start=1):
            doc_id = row[id_key]
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
            if doc_id not in merged_rows:
                merged_rows[doc_id] = dict(row)

    fused = []
    for doc_id, score in scores.items():
        row = dict(merged_rows[doc_id])
        row["rrf_score"] = score
        fused.append(row)

    fused.sort(key=lambda r: r["rrf_score"], reverse=True)
    return fused

