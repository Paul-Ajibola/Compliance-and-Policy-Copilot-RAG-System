"""
The Module Docstring
Wraps a local sentence-transformers model for embedding chunk text.
Model: BAAI/bge-small-en-v1.5 (384-dim, runs locally, no API cost).

bge models were trained with an asymmetric convention: passages/documents
are embedded with no prefix, but queries are embedded with an instruction
prefix. Getting this backwards measurably hurts retrieval quality, so
embed_query() and embed_passages() are deliberately separate functions
rather than one generic embed_texts().
"""

from sentence_transformers import SentenceTransformer

_MODEL_NAME = "BAAI/bge-small-en-v1.5"
_QUERY_PREFIX = "Represent this sentence for searching relevant passages:"

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def embed_passages(texts: list[str], show_progress: bool = False) -> list[list[float]]:
    """Embed chunk text for storage/indexing. No prefix."""
    model = get_model()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=show_progress)
    return vectors.tolist()


def embed_query(text: str) -> list[float]:
    """Embed a user's search query. Uses bge's required query prefix."""
    model = get_model()
    vector = model.encode(_QUERY_PREFIX + text, normalize_embeddings=True, show_progress_bar=False)
    return vector.tolist()


