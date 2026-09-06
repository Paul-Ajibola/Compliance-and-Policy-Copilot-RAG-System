"""
Runs every golden-set and trap-set question through the retrieval
pipeline, prints scores, and saves per-question results to a JSON file
so failures can be inspected individually afterward.

Run with: docker compose exec backend python -m eval.run_eval
"""
import asyncio
import json
from pathlib import Path

from app.db.session import AsyncSessionLocal
from app.retrieval.pipeline import retrieve
from app.confidence.gate import CONFIDENCE_THRESHOLD

EVAL_DIR = Path(__file__).parent


async def run():
    golden = json.loads((EVAL_DIR / "golden_dataset.json").read_text())
    trap = json.loads((EVAL_DIR / "trap_set.json").read_text())

    all_results = []

    async with AsyncSessionLocal() as session:
        print(f"\n{'='*70}\nGOLDEN SET\n{'='*70}")
        for item in golden:
            results = await retrieve(session, item["question"], final_k=1)
            score = results[0]["rerank_score"] if results else None
            correct = score is not None and score >= CONFIDENCE_THRESHOLD
            all_results.append({"type": "golden", "question": item["question"], "score": score, "correct": correct})
            flag = "" if correct else "  <-- MISS"
            print(f"  {score:>8.3f}  {item['question']}{flag}")

        print(f"\n{'='*70}\nTRAP SET\n{'='*70}")
        for item in trap:
            results = await retrieve(session, item["question"], final_k=1)
            score = results[0]["rerank_score"] if results else None
            correct = score is not None and score < CONFIDENCE_THRESHOLD
            all_results.append({"type": "trap", "trap_type": item.get("trap_type"), "question": item["question"], "score": score, "correct": correct})
            flag = "" if correct else "  <-- MISS"
            print(f"  {score:>8.3f}  [{item.get('trap_type')}] {item['question']}{flag}")

    (EVAL_DIR / "eval_details.json").write_text(json.dumps(all_results, indent=2))

    golden_scores = [r["score"] for r in all_results if r["type"] == "golden" and r["score"] is not None]
    trap_scores = [r["score"] for r in all_results if r["type"] == "trap" and r["score"] is not None]
    golden_correct = sum(1 for r in all_results if r["type"] == "golden" and r["correct"])
    trap_correct = sum(1 for r in all_results if r["type"] == "trap" and r["correct"])

    print(f"\n{'='*70}\nSUMMARY\n{'='*70}")
    print(f"Golden set: min={min(golden_scores):.3f}  max={max(golden_scores):.3f}  avg={sum(golden_scores)/len(golden_scores):.3f}")
    print(f"Trap set:   min={min(trap_scores):.3f}  max={max(trap_scores):.3f}  avg={sum(trap_scores)/len(trap_scores):.3f}")
    print(f"\nAt threshold={CONFIDENCE_THRESHOLD}:")
    print(f"  Golden set correctly ANSWERED: {golden_correct}/{len(golden_scores)} ({100*golden_correct/len(golden_scores):.0f}%)")
    print(f"  Trap set correctly REFUSED:    {trap_correct}/{len(trap_scores)} ({100*trap_correct/len(trap_scores):.0f}%)")
    print(f"\nFull per-question details saved to eval/eval_details.json")


if __name__ == "__main__":
    asyncio.run(run())


