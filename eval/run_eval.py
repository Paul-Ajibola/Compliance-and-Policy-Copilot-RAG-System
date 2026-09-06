"""
Runs every golden-set and trap-set question through the retrieval
pipeline and prints the top reranked score for each — this is what lets
you pick CONFIDENCE_THRESHOLD in app/confidence/gate.py based on real
numbers, rather than guessing blind.

Processes in small batches with a pause between them to avoid sustained
memory pressure on resource-constrained machines.

Run with: docker compose exec backend python -m eval.run_eval
"""
import asyncio
import json
from pathlib import Path

from app.db.session import AsyncSessionLocal
from app.retrieval.pipeline import retrieve
from app.confidence.gate import CONFIDENCE_THRESHOLD

EVAL_DIR = Path(__file__).parent
BATCH_SIZE = 10
PAUSE_SECONDS = 3


async def score_items(session, items, label):
    scores = []
    for i, item in enumerate(items):
        results = await retrieve(session, item["question"], final_k=1)
        score = results[0]["rerank_score"] if results else None
        scores.append(score)
        print(f"  {score:>8.3f}  {item['question']}")

        if (i + 1) % BATCH_SIZE == 0 and (i + 1) < len(items):
            print(f"  ... pausing {PAUSE_SECONDS}s after {i + 1}/{len(items)} ({label}) ...")
            await asyncio.sleep(PAUSE_SECONDS)

    return scores


async def run():
    golden = json.loads((EVAL_DIR / "golden_dataset.json").read_text())
    trap = json.loads((EVAL_DIR / "trap_set.json").read_text())

    async with AsyncSessionLocal() as session:
        print(f"\n{'='*70}\nGOLDEN SET (should score HIGH) — {len(golden)} questions\n{'='*70}")
        golden_scores = await score_items(session, golden, "golden")

        print(f"\n{'='*70}\nTRAP SET (should score LOW) — {len(trap)} questions\n{'='*70}")
        trap_scores = await score_items(session, trap, "trap")

        valid_golden = [s for s in golden_scores if s is not None]
        valid_trap = [s for s in trap_scores if s is not None]

        print(f"\n{'='*70}\nSUMMARY\n{'='*70}")
        print(f"Golden set: min={min(valid_golden):.3f}  max={max(valid_golden):.3f}  avg={sum(valid_golden)/len(valid_golden):.3f}")
        print(f"Trap set:   min={min(valid_trap):.3f}  max={max(valid_trap):.3f}  avg={sum(valid_trap)/len(valid_trap):.3f}")

        golden_correct = sum(1 for s in valid_golden if s >= CONFIDENCE_THRESHOLD)
        trap_correct = sum(1 for s in valid_trap if s < CONFIDENCE_THRESHOLD)
        print(f"\nAt threshold={CONFIDENCE_THRESHOLD}:")
        print(f"  Golden set correctly ANSWERED: {golden_correct}/{len(valid_golden)} ({100*golden_correct/len(valid_golden):.0f}%)")
        print(f"  Trap set correctly REFUSED:    {trap_correct}/{len(valid_trap)} ({100*trap_correct/len(valid_trap):.0f}%)")


if __name__ == "__main__":
    asyncio.run(run())


