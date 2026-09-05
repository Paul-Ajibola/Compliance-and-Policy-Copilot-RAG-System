"""
Wraps the Gemini API for streaming generation, constrained to the
retrieved passages via prompts.py. Kept separate from the confidence
gate and the API route: this module only knows how to talk to the LLM,
nothing about HTTP or retrieval.
"""
from google import genai

from app.config import settings
from app.generation.prompts import build_prompt

_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


async def stream_answer(question: str, context_chunks: list[dict]):
    """
    Yields text chunks as they're generated. context_chunks is the
    confidence gate's already-retrieved, already-reranked result list.
    """
    client = get_client()
    prompt = build_prompt(question, context_chunks)

    stream = await client.aio.models.generate_content_stream(
        model=settings.gemini_model,
        contents=prompt,
    )
    async for chunk in stream:
        if chunk.text:
            yield chunk.text


def build_citations(context_chunks: list[dict]) -> list[dict]:
    """
    Maps citation numbers [1], [2], ... back to their source chunk
    metadata, for the frontend to render as clickable badges (Phase 7).
    """
    citations = []
    for i, chunk in enumerate(context_chunks, start=1):
        citations.append({
            "marker": i,
            "chunk_id": str(chunk.get("id")),
            "chunk_index": chunk.get("chunk_index"),
            "heading_path": chunk.get("heading_path"),
            "chunk_type": chunk.get("chunk_type"),
        })
    return citations

