"""Generate reproducible Round 1 benchmark artifacts from the local evaluation set."""

import json
from pathlib import Path

from src.core import EVALUATION_SET, benchmark, evaluate, summary


def main() -> None:
    output_dir = Path("artifacts")
    output_dir.mkdir(exist_ok=True)
    questions = [item["question"] for item in EVALUATION_SET]
    expected = {item["question"]: item["expected"] for item in EVALUATION_SET}
    results = evaluate(benchmark(questions), expected)
    payload = {
        "status": "local-demo",
        "note": "Replace EVALUATION_SET with the official 100 public questions before submission.",
        "results": results,
        "summary": summary(results),
    }
    (output_dir / "benchmark_results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))
    print(f"Wrote {len(results)} pipeline results to {output_dir / 'benchmark_results.json'}")


if __name__ == "__main__":
    main()