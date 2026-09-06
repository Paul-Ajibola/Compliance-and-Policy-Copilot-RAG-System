"""
Reads eval/eval_results.json (produced incrementally by run_eval.py) and
prints the final summary + threshold pass/fail rates.

Run with: docker compose exec backend python -m eval.summarize
"""
import json
from pathlib import Path

from app.confidence.gate import CONFIDENCE_THRESHOLD

EVAL_DIR = Path(__file__).parent
RESULTS_FILE = EVAL_DIR / "eval_results.json"


def main():
    results = json.loads(RESULTS_FILE.read_text())

    golden_scores = [r["score"] for r in results.values() if r["type"] == "golden" and r["score"] is not None]
    trap_scores = [r["score"] for r in results.values() if r["type"] == "trap" and r["score"] is not None]

    print(f"\n{'='*70}\nSUMMARY ({len(results)} total questions processed)\n{'='*70}")
    print(f"Golden set: n={len(golden_scores)}  min={min(golden_scores):.3f}  max={max(golden_scores):.3f}  avg={sum(golden_scores)/len(golden_scores):.3f}")
    print(f"Trap set:   n={len(trap_scores)}  min={min(trap_scores):.3f}  max={max(trap_scores):.3f}  avg={sum(trap_scores)/len(trap_scores):.3f}")

    golden_correct = sum(1 for s in golden_scores if s >= CONFIDENCE_THRESHOLD)
    trap_correct = sum(1 for s in trap_scores if s < CONFIDENCE_THRESHOLD)
    print(f"\nAt threshold={CONFIDENCE_THRESHOLD}:")
    print(f"  Golden set correctly ANSWERED: {golden_correct}/{len(golden_scores)} ({100*golden_correct/len(golden_scores):.0f}%)")
    print(f"  Trap set correctly REFUSED:    {trap_correct}/{len(trap_scores)} ({100*trap_correct/len(trap_scores):.0f}%)")


if __name__ == "__main__":
    main()