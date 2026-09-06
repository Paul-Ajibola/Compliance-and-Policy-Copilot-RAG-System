"""
LLM-as-judge evaluation: for each golden-set question, runs the full
pipeline (retrieve -> rerank -> generate via GEMINI), then asks an
INDEPENDENT model (GROQ/Llama) to score the generated answer. Using a
different model for judging than for generation avoids the well-known
self-bias problem where a model tends to rate its own outputs more
favorably than an independent judge would.

Run with: docker compose exec backend python -m eval.llm_judge
"""
import asyncio
import json
import re
from pathlib import Path

from groq import AsyncGroq

from app.config import settings
from app.db.session import AsyncSessionLocal
from app.retrieval.pipeline import retrieve
from app.generation.generator import generate_answer_full  # still Gemini


EVAL_DIR = Path(__file__).parent
RESULTS_FILE = EVAL_DIR / "judge_results.json"

JUDGE_PROMPT_TEMPLATE = """You are an evaluation judge for a RAG system. Given a question, the passages retrieved to answer it, and the system's generated answer, score three things.

QUESTION: {question}

RETRIEVED PASSAGES:
{passages}

GENERATED ANSWER:
{answer}

Score each on a 1-5 scale:

1. FAITHFULNESS: Does the answer only make claims that are actually supported by the retrieved passages? 5 = fully grounded, no unsupported claims. 1 = contains fabricated or unsupported claims not found in the passages.

2. ANSWER_RELEVANCY: Does the answer actually address the question asked? 5 = directly and completely answers it. 1 = off-topic or evasive.

3. CONTEXT_RELEVANCE: Of the retrieved passages, how many were actually useful for answering this question? 5 = all passages were relevant. 1 = none of the passages were relevant to the question.

Respond with ONLY valid JSON, no other text:
{{"faithfulness": <1-5>, "answer_relevancy": <1-5>, "context_relevance": <1-5>, "reasoning": "<one sentence explaining the scores>"}}
"""

_judge_client: AsyncGroq | None = None


def get_judge_client() -> AsyncGroq:
    global _judge_client
    if _judge_client is None:
        _judge_client = AsyncGroq(api_key=settings.groq_api_key)
    return _judge_client


def load_results():
    if RESULTS_FILE.exists():
        return json.loads(RESULTS_FILE.read_text())
    return {}


def save_results(results):
    RESULTS_FILE.write_text(json.dumps(results, indent=2))


def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in judge response: {text[:200]}")
    return json.loads(match.group(0))


async def judge_one(session, client, item: dict) -> dict:
    question = item["question"]
    context_chunks = await retrieve(session, question, shortlist_k=10, final_k=5)

    if not context_chunks:
        return {"question": question, "error": "no chunks retrieved"}

    answer = await generate_answer_full(question, context_chunks)  # Gemini

    passages_text = "\n\n".join(
        f"[{i+1}] {c['text'][:500]}" for i, c in enumerate(context_chunks)
    )
    prompt = JUDGE_PROMPT_TEMPLATE.format(question=question, passages=passages_text, answer=answer)

    response = await client.chat.completions.create(  # Groq
        model=settings.groq_model,
        messages=[{"role": "user", "content": prompt}],
        stream=False,
    )
    scores = _extract_json(response.choices[0].message.content)

    return {
        "question": question,
        "expected_answer": item.get("expected_answer") or item.get("expected_answer_hint"),
        "generated_answer": answer,
        "faithfulness": scores.get("faithfulness"),
        "answer_relevancy": scores.get("answer_relevancy"),
        "context_relevance": scores.get("context_relevance"),
        "reasoning": scores.get("reasoning"),
    }


async def run():
    golden = json.loads((EVAL_DIR / "golden_dataset.json").read_text())
    results = load_results()
    client = get_judge_client()

    pending = [item for item in golden if item["question"] not in results]

    if not pending:
        print(f"All {len(golden)} questions already judged. See eval/judge_results.json")
    else:
        print(f"Judging {len(pending)} of {len(golden)} questions ({len(results)} already done)...")

        async with AsyncSessionLocal() as session:
            for i, item in enumerate(pending):
                try:
                    result = await judge_one(session, client, item)
                    results[item["question"]] = result
                    save_results(results)
                    print(f"  [{i+1}/{len(pending)}] faithfulness={result.get('faithfulness')} "
                          f"relevancy={result.get('answer_relevancy')} "
                          f"context={result.get('context_relevance')}  {item['question'][:60]}")
                except Exception as e:
                    print(f"  [{i+1}/{len(pending)}] ERROR on {item['question'][:60]}: {e}")
                    continue

                await asyncio.sleep(3)  # stay comfortably under Groq's free-tier RPM limit

    valid = [r for r in results.values() if "faithfulness" in r and r["faithfulness"] is not None]
    if valid:
        avg_faith = sum(r["faithfulness"] for r in valid) / len(valid)
        avg_rel = sum(r["answer_relevancy"] for r in valid) / len(valid)
        avg_ctx = sum(r["context_relevance"] for r in valid) / len(valid)
        low_faith = [r for r in valid if r["faithfulness"] <= 2]

        print(f"\n{'='*70}\nSUMMARY ({len(valid)} questions judged)\n{'='*70}")
        print(f"Avg faithfulness:      {avg_faith:.2f}/5")
        print(f"Avg answer relevancy:  {avg_rel:.2f}/5")
        print(f"Avg context relevance: {avg_ctx:.2f}/5")
        print(f"\nQuestions with LOW faithfulness (<=2), worth reviewing: {len(low_faith)}")
        for r in low_faith:
            print(f"  - {r['question']}")
            print(f"    reasoning: {r.get('reasoning')}")


if __name__ == "__main__":
    asyncio.run(run())