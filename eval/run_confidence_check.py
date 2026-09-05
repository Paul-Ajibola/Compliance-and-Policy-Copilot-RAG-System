"""
Runs every golden-set and trap-set question through the retrieval
pipeline and prints the top reranked score for each — this is what lets
you actually pick CONFIDENCE_THRESHOLD in gate.py based on real numbers,
rather than guessing blind.

Run with: python -m eval.run_confidence_check
"""
import asyncio
import json
from pathlib import Path

from app.db.session import AsyncSessionLocal
from app.retrieval.pipeline import retrieve

EVAL_DIR = Path(__file__).parent


async def run():
    golden = json.loads((EVAL_DIR / "golden_set.json").read_text())
    trap = json.loads((EVAL_DIR / "trap_set.json").read_text())

    async with AsyncSessionLocal() as session:
        print(f"\n{'='*70}\nGOLDEN SET (should score HIGH)\n{'='*70}")
        golden_scores = []
        for item in golden:
            results = await retrieve(session, item["question"], final_k=1)
            score = results[0]["rerank_score"] if results else None
            golden_scores.append(score)
            print(f"  {score:>8.3f}  {item['question']}")

        print(f"\n{'='*70}\nTRAP SET (should score LOW)\n{'='*70}")
        trap_scores = []
        for item in trap:
            results = await retrieve(session, item["question"], final_k=1)
            score = results[0]["rerank_score"] if results else None
            trap_scores.append(score)
            print(f"  {score:>8.3f}  [{item['trap_type']}] {item['question']}")

        valid_golden = [s for s in golden_scores if s is not None]
        valid_trap = [s for s in trap_scores if s is not None]
        print(f"\n{'='*70}\nSUMMARY\n{'='*70}")
        print(f"Golden set: min={min(valid_golden):.3f}  max={max(valid_golden):.3f}  avg={sum(valid_golden)/len(valid_golden):.3f}")
        print(f"Trap set:   min={min(valid_trap):.3f}  max={max(valid_trap):.3f}  avg={sum(valid_trap)/len(valid_trap):.3f}")
        print(f"\nLook for a threshold value that sits between the two ranges above.")


if __name__ == "__main__":
    asyncio.run(run())